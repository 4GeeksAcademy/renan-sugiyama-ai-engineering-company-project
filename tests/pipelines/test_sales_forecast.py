from pathlib import Path
import sys

import joblib
import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[2]
DATA_PATH = ROOT / "data/raw/nexova_sales.csv"
sys.path.insert(0, str(ROOT))

from data.pipelines.sales_forecast.core import (
    forecast_with_intervals,
    load_sales,
    recursive_forecast,
    split_sales,
    training_features,
    validate_sales,
)
from data.pipelines.sales_forecast.metrics import normalized_rank_gini, regression_metrics, revenue_psi
from data.pipelines.sales_forecast.experiment import run_experiment
from data.pipelines.sales_forecast import core


def test_split_uses_first_eight_and_last_two_years_without_overlap() -> None:
    data = load_sales(DATA_PATH).sample(frac=1, random_state=42)
    train, test = split_sales(data)
    assert len(train) == 96
    assert len(test) == 24
    assert train["month"].min() == pd.Timestamp("2016-01-01")
    assert train["month"].max() == pd.Timestamp("2023-12-01")
    assert test["month"].min() == pd.Timestamp("2024-01-01")
    assert test["month"].max() == pd.Timestamp("2025-12-01")
    assert set(train["month"]).isdisjoint(test["month"])


@pytest.mark.parametrize("problem", ["missing", "duplicate", "invalid", "null", "nonpositive"])
def test_invalid_calendar_and_targets_are_rejected(problem: str) -> None:
    data = pd.read_csv(DATA_PATH)
    if problem == "missing":
        data = data.iloc[1:]
    elif problem == "duplicate":
        data.loc[1, "month"] = data.loc[0, "month"]
    elif problem == "invalid":
        data.loc[0, "month"] = "2016-13-01"
    elif problem == "null":
        data.loc[0, "revenue_usd"] = None
    else:
        data.loc[0, "revenue_usd"] = 0
    with pytest.raises(ValueError):
        validate_sales(data)


def test_training_features_use_only_prior_revenue() -> None:
    train, _ = split_sales(load_sales(DATA_PATH))
    features, target = training_features(train)
    assert len(features) == 84
    assert features.iloc[0]["lag_1"] == train.iloc[11]["revenue_usd"]
    assert features.iloc[0]["lag_12"] == train.iloc[0]["revenue_usd"]
    assert features.iloc[0]["rolling_3"] == pytest.approx(train.iloc[9:12]["revenue_usd"].mean())
    assert target.iloc[0] == train.iloc[12]["revenue_usd"]


def test_recursive_forecast_uses_predicted_values_for_lags() -> None:
    train, _ = split_sales(load_sales(DATA_PATH))

    class IncrementModel:
        def predict(self, features: pd.DataFrame) -> list[float]:
            return [features.iloc[0]["lag_1"] + 1]

    result = recursive_forecast(IncrementModel(), train, periods=3)
    assert result["prediction"].tolist() == pytest.approx(
        [train.iloc[-1]["revenue_usd"] + step for step in (1, 2, 3)]
    )


def test_forecast_and_band_ignore_all_test_period_values() -> None:
    data = load_sales(DATA_PATH)
    train, _ = split_sales(data)
    original = forecast_with_intervals(train)
    changed = data.copy()
    changed.loc[changed["month"] >= pd.Timestamp("2024-01-01"), "revenue_usd"] *= 3
    changed.loc[changed["month"] >= pd.Timestamp("2024-01-01"), "active_contracts"] *= 10
    changed.loc[changed["month"] >= pd.Timestamp("2024-01-01"), "avg_contract_value_usd"] *= 10
    changed_train, _ = split_sales(changed)
    repeated = forecast_with_intervals(changed_train)
    pd.testing.assert_frame_equal(original, repeated)
    assert len(original) == 24
    assert (original["lower"] <= original["upper"]).all()


def test_regression_metrics_and_undefined_r2() -> None:
    metrics = regression_metrics(np.array([1.0, 2.0, 3.0]), np.array([2.0, 2.0, 2.0]))
    assert metrics["mse_usd2"] == pytest.approx(2 / 3)
    assert metrics["rmse_usd"] == pytest.approx(np.sqrt(2 / 3))
    assert metrics["mae_usd"] == pytest.approx(2 / 3)
    assert metrics["normalized_rmse_percent"] == pytest.approx(50 * np.sqrt(2 / 3))
    assert metrics["r2"] == pytest.approx(0)
    assert regression_metrics(np.array([2.0, 2.0]), np.array([1.0, 1.0]))["r2"] is None


def test_normalized_gini_ranking_and_ties() -> None:
    actual = np.array([1.0, 2.0, 3.0])
    assert normalized_rank_gini(actual, actual) == pytest.approx(1)
    assert normalized_rank_gini(actual, actual[::-1]) == pytest.approx(-1)
    assert normalized_rank_gini(actual, np.array([1.0, 1.0, 1.0])) == pytest.approx(0)
    assert normalized_rank_gini(np.array([2.0, 2.0]), np.array([1.0, 2.0])) is None


def test_psi_uses_training_bins_and_smooths_empty_bins() -> None:
    train = np.arange(1, 101, dtype=float)
    same = revenue_psi(train, train)
    shifted = revenue_psi(train, np.full(24, 200.0))
    assert same["psi"] == pytest.approx(0)
    assert shifted["psi"] > 0
    assert np.isfinite(shifted["psi"])
    assert shifted["bin_edges_usd"] == same["bin_edges_usd"]
    assert sum(shifted["test_counts"]) == 24
    with pytest.raises(ValueError, match="at least two"):
        revenue_psi(np.ones(10), np.ones(3))


def test_calibration_fits_only_through_each_forecast_origin(monkeypatch: pytest.MonkeyPatch) -> None:
    train, _ = split_sales(load_sales(DATA_PATH))
    original_fit = core.fit_model
    observed_origins = []

    def record_fit(history: pd.DataFrame):
        observed_origins.append(history["month"].max())
        return original_fit(history)

    monkeypatch.setattr(core, "fit_model", record_fit)
    core.forecast_with_intervals(train)
    assert observed_origins == [pd.Timestamp(date) for date in ("2019-12-01", "2020-12-01", "2021-12-01", "2023-12-01")]


def test_empty_target_rejected_and_optional_missing_values_not_used() -> None:
    data = pd.read_csv(DATA_PATH)
    data.loc[0, "revenue_usd"] = np.nan
    with pytest.raises(ValueError, match="Missing month or revenue"):
        validate_sales(data)
    data = pd.read_csv(DATA_PATH)
    data.loc[0, "active_contracts"] = np.nan
    data.loc[0, "avg_contract_value_usd"] = np.nan
    train, _ = split_sales(validate_sales(data))
    features, _ = training_features(train)
    assert features.notna().all().all()
    assert "active_contracts" not in features.columns


def test_imputer_statistics_are_fitted_only_on_training_features() -> None:
    train, _ = split_sales(load_sales(DATA_PATH))
    features, _ = training_features(train)
    model = core.fit_model(train)
    np.testing.assert_allclose(model.named_steps["imputer"].statistics_, features.median().to_numpy())


def test_experiment_writes_reproducible_artifacts(tmp_path: Path) -> None:
    report = run_experiment(DATA_PATH, tmp_path)
    predictions = pd.read_csv(tmp_path / "predictions.csv")
    frozen = pd.read_csv(tmp_path / "frozen_forecast.csv")
    assert len(predictions) == 24
    assert predictions["month"].tolist() == pd.date_range("2024-01-01", "2025-12-01", freq="MS").strftime("%Y-%m-%d").tolist()
    assert list(frozen.columns) == ["month", "prediction", "lower", "upper"]
    assert (predictions["lower"] <= predictions["upper"]).all()
    assert (tmp_path / "forecast.png").read_bytes().startswith(b"\x89PNG\r\n\x1a\n")
    assert joblib.load(tmp_path / "model.joblib").named_steps["forest"].random_state == 42
    assert {"mse_usd2", "r2", "normalized_rank_gini"} <= report["test_metrics"].keys()
    assert "psi" in report["revenue_psi"]
    assert "Undecided" in report["finance_acceptance"]
    repeated_report = run_experiment(DATA_PATH, tmp_path)
    pd.testing.assert_frame_equal(predictions, pd.read_csv(tmp_path / "predictions.csv"))
    assert report["test_metrics"] == repeated_report["test_metrics"]
    assert report["revenue_psi"] == repeated_report["revenue_psi"]