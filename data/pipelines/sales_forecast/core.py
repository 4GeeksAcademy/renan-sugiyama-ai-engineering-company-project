from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline


EXPECTED_COLUMNS = (
    "month",
    "revenue_usd",
    "active_contracts",
    "avg_contract_value_usd",
    "business_line",
)
EXPECTED_MONTHS = pd.date_range("2016-01-01", "2025-12-01", freq="MS")
TEST_START = pd.Timestamp("2024-01-01")
FEATURES = ("month", "month_sin", "month_cos", "lag_1", "lag_12", "rolling_3")
CALIBRATION_ORIGINS = ("2019-12-01", "2020-12-01", "2021-12-01")


def load_sales(path: Path) -> pd.DataFrame:
    raw = pd.read_csv(path, dtype={"month": "string", "business_line": "string"})
    return validate_sales(raw)


def validate_sales(raw: pd.DataFrame) -> pd.DataFrame:
    if set(raw.columns) != set(EXPECTED_COLUMNS) or len(raw.columns) != len(EXPECTED_COLUMNS):
        raise ValueError(f"Expected columns: {', '.join(EXPECTED_COLUMNS)}")
    data = raw.copy().replace(r"^\s*$", np.nan, regex=True)
    if data["business_line"].isna().any():
        raise ValueError("Missing business_line")
    data = data.loc[data["business_line"] == "consolidated"].copy()
    if data["month"].isna().any() or data["revenue_usd"].isna().any():
        raise ValueError("Missing month or revenue")
    month_strings = data["month"].astype("string")
    if not month_strings.str.fullmatch(r"\d{4}-\d{2}-01").all():
        raise ValueError("Invalid month: expected YYYY-MM-01")
    data["month"] = pd.to_datetime(month_strings, format="%Y-%m-%d", errors="coerce")
    if data["month"].isna().any():
        raise ValueError("Invalid month")
    for column in ("revenue_usd", "active_contracts", "avg_contract_value_usd"):
        numeric = pd.to_numeric(data[column], errors="coerce")
        if (data[column].notna() & numeric.isna()).any():
            raise ValueError(f"Invalid {column}")
        if not np.isfinite(numeric.dropna()).all():
            raise ValueError(f"Non-finite {column}")
        data[column] = numeric
    if (data["revenue_usd"] <= 0).any():
        raise ValueError("Revenue must be positive")
    contracts = data["active_contracts"].dropna()
    if (contracts % 1 != 0).any():
        raise ValueError("active_contracts must be an integer")
    data = data.sort_values("month").reset_index(drop=True)
    if data["month"].duplicated().any():
        raise ValueError("Duplicate consolidated month")
    if not pd.DatetimeIndex(data["month"]).equals(EXPECTED_MONTHS):
        raise ValueError("Missing or unexpected consolidated months")
    return data


def split_sales(data: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    data = validate_sales(data.assign(month=data["month"].astype(str)))
    train = data.loc[data["month"] < TEST_START].copy()
    test = data.loc[data["month"] >= TEST_START].copy()
    if len(train) != 96 or len(test) != 24 or train["month"].max() >= test["month"].min():
        raise ValueError("Expected an ordered 96/24 month split")
    return train.reset_index(drop=True), test.reset_index(drop=True)


def training_features(history: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    ordered = history.sort_values("month").reset_index(drop=True)
    revenue = ordered["revenue_usd"]
    month = ordered["month"].dt.month
    features = pd.DataFrame(
        {
            "month": month,
            "month_sin": np.sin(2 * np.pi * month / 12),
            "month_cos": np.cos(2 * np.pi * month / 12),
            "lag_1": revenue.shift(1),
            "lag_12": revenue.shift(12),
            "rolling_3": revenue.shift(1).rolling(3).mean(),
        }
    )
    eligible = features.notna().all(axis=1)
    return features.loc[eligible], revenue.loc[eligible]


def fit_model(history: pd.DataFrame) -> Pipeline:
    features, target = training_features(history)
    if features.empty:
        raise ValueError("At least 13 months of history are required")
    model = Pipeline(
        [
            ("imputer", SimpleImputer(strategy="median")),
            ("forest", RandomForestRegressor(n_estimators=200, min_samples_leaf=2, random_state=42, n_jobs=1)),
        ]
    )
    return model.fit(features, target)


def recursive_forecast(model: Pipeline, history: pd.DataFrame, periods: int = 24) -> pd.DataFrame:
    ordered = history.sort_values("month")
    revenue = ordered["revenue_usd"].astype(float).tolist()
    if len(revenue) < 12:
        raise ValueError("At least 12 months of history are required")
    months = pd.date_range(ordered["month"].max() + pd.offsets.MonthBegin(), periods=periods, freq="MS")
    predictions = []
    for month in months:
        calendar_month = month.month
        row = pd.DataFrame(
            [[calendar_month, np.sin(2 * np.pi * calendar_month / 12),
              np.cos(2 * np.pi * calendar_month / 12), revenue[-1], revenue[-12], np.mean(revenue[-3:])]],
            columns=FEATURES,
        )
        prediction = float(model.predict(row)[0])
        predictions.append(prediction)
        revenue.append(prediction)
    return pd.DataFrame({"month": months, "prediction": predictions})


def forecast_with_intervals(train: pd.DataFrame, model: Pipeline | None = None) -> pd.DataFrame:
    errors = []
    for origin in CALIBRATION_ORIGINS:
        origin_date = pd.Timestamp(origin)
        history = train.loc[train["month"] <= origin_date]
        actual = train.loc[train["month"] > origin_date].sort_values("month").head(24)
        if len(actual) != 24:
            raise ValueError(f"Insufficient calibration data after {origin}")
        forecast = recursive_forecast(fit_model(history), history)
        if not forecast["month"].reset_index(drop=True).equals(actual["month"].reset_index(drop=True)):
            raise ValueError("Calibration months do not match forecast months")
        errors.append(actual["revenue_usd"].to_numpy() - forecast["prediction"].to_numpy())
    result = recursive_forecast(model if model is not None else fit_model(train), train)
    residuals = np.asarray(errors)
    result["lower"] = result["prediction"] + np.quantile(residuals, 0.1, axis=0)
    result["upper"] = result["prediction"] + np.quantile(residuals, 0.9, axis=0)
    return result