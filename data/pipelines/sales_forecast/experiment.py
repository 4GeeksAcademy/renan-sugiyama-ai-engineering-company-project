from __future__ import annotations

import hashlib
import json
import platform
from pathlib import Path

import joblib
import matplotlib
import numpy as np
import pandas as pd
import sklearn

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from data.pipelines.sales_forecast.core import CALIBRATION_ORIGINS, fit_model, forecast_with_intervals, load_sales, split_sales
from data.pipelines.sales_forecast.metrics import regression_metrics, revenue_psi


def input_summary(data: pd.DataFrame, raw: pd.DataFrame) -> dict:
    annual = data.groupby(data["month"].dt.year)["revenue_usd"].sum()
    relative = data["revenue_usd"] / data.groupby(data["month"].dt.year)["revenue_usd"].transform("mean")
    monthly = pd.DataFrame({"month": data["month"].dt.month, "ratio": relative})
    patterns = monthly.groupby("month")["ratio"].agg(["min", "max", "mean"])
    return {
        "rows": len(data),
        "columns": list(raw.columns),
        "raw_dtypes": {column: str(dtype) for column, dtype in raw.dtypes.items()},
        "missing_or_empty_by_column": raw.replace(r"^\s*$", np.nan, regex=True).isna().sum().to_dict(),
        "business_line_counts": raw["business_line"].value_counts(dropna=False).to_dict(),
        "duplicate_months": int(data["month"].duplicated().sum()),
        "nonpositive_revenue_count": int((data["revenue_usd"] <= 0).sum()),
        "annual_growth_percent": {str(year): float(value) for year, value in (annual.pct_change() * 100).dropna().items()},
        "monthly_to_annual_mean_ratio": {str(month): {name: float(value) for name, value in row.items()} for month, row in patterns.iterrows()},
        "pattern_note": "Observed annual growth and individual monthly ratios can differ from the approximate briefing ranges; source data was not altered.",
        "missing_value_policy": "Missing dates and targets are rejected. Optional contract fields are not model features; no optional-field imputation is required.",
    }


def run_experiment(input_path: Path, output_dir: Path) -> dict:
    data = load_sales(input_path)
    train, test = split_sales(data)
    output_dir.mkdir(parents=True, exist_ok=True)
    model = fit_model(train)
    frozen = forecast_with_intervals(train, model)
    frozen.to_csv(output_dir / "frozen_forecast.csv", index=False, date_format="%Y-%m-%d", float_format="%.10f")
    joblib.dump(model, output_dir / "model.joblib")

    predictions = frozen.merge(test[["month", "revenue_usd"]], on="month", validate="one_to_one")
    if len(predictions) != 24:
        raise ValueError("Expected all 24 test months")
    baseline_by_month = train.loc[train["month"].dt.year == 2023].set_index(train.loc[train["month"].dt.year == 2023, "month"].dt.month)["revenue_usd"]
    predictions["baseline"] = predictions["month"].dt.month.map(baseline_by_month)
    predictions = predictions.rename(columns={"revenue_usd": "actual"})
    predictions = predictions[["month", "actual", "prediction", "lower", "upper", "baseline"]]
    predictions.to_csv(output_dir / "predictions.csv", index=False, date_format="%Y-%m-%d", float_format="%.10f")

    actual = predictions["actual"].to_numpy()
    prediction = predictions["prediction"].to_numpy()
    metrics = regression_metrics(actual, prediction)
    baseline = regression_metrics(actual, predictions["baseline"].to_numpy())
    psi = revenue_psi(train["revenue_usd"].to_numpy(), actual)
    coverage = float(((predictions["lower"] <= predictions["actual"]) & (predictions["actual"] <= predictions["upper"])).mean())

    figure, axis = plt.subplots(figsize=(12, 5.5), layout="constrained")
    axis.fill_between(predictions["month"], predictions["lower"], predictions["upper"], color="#c5e7d0", alpha=0.8, label="Empirical 80% nominal range")
    axis.plot(predictions["month"], predictions["actual"], color="#17211b", linewidth=2, marker=".", label="Actual revenue")
    axis.plot(predictions["month"], predictions["prediction"], color="#a94d24", linewidth=2, marker=".", label="Forecast")
    axis.set(title="Nexova monthly revenue: 24-month holdout", xlabel="Month", ylabel="Revenue (USD)")
    axis.grid(axis="y", alpha=0.25)
    axis.legend(loc="best")
    figure.savefig(output_dir / "forecast.png", dpi=160)
    plt.close(figure)

    report = {
        "input": {"path": str(input_path), "sha256": hashlib.sha256(input_path.read_bytes()).hexdigest(), **input_summary(data, pd.read_csv(input_path))},
        "train_period": ["2016-01", "2023-12"],
        "test_period": ["2024-01", "2025-12"],
        "train_months": len(train),
        "test_months": len(test),
        "model": {"algorithm": "RandomForestRegressor", "parameters": model.named_steps["forest"].get_params(), "training_rows_after_warmup": 84},
        "versions": {"python": platform.python_version(), "numpy": np.__version__, "pandas": pd.__version__, "scikit-learn": sklearn.__version__, "matplotlib": matplotlib.__version__, "joblib": joblib.__version__},
        "test_metrics": metrics,
        "revenue_psi": psi,
        "seasonal_naive_test_mse_usd2": baseline["mse_usd2"],
        "seasonal_naive_test_rmse_usd": baseline["rmse_usd"],
        "interval": {"method": "Per-horizon 10th/90th percentile of three signed recursive backtest errors", "nominal_percent": 80, "calibration_origins": list(CALIBRATION_ORIGINS), "test_coverage_percent": 100 * coverage, "caveat": "Three overlapping historical calibration windows do not guarantee coverage."},
        "finance_acceptance": "Undecided: Finance has not specified an acceptable error threshold.",
        "limitations": ["PSI compares consolidated revenue distributions, not unavailable business-line mix.", "A low MSE alone cannot establish robustness, ranking, distribution stability, interval calibration, or business acceptance.", "Random Forest predictions cannot extrapolate beyond training target ranges.", "This single historical holdout does not guarantee future performance or provide a forecast beyond 2025 without newer approved data."],
    }
    (output_dir / "metrics.json").write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
    return report