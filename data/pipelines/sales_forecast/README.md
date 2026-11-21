# Nexova sales forecasting backtest

This is a historical feasibility experiment, not a production forecast or dashboard. It uses the supplied `data/raw/nexova_sales.csv` unchanged. The one forecast origin is December 2023: the model is trained on 96 monthly observations from 2016-2023 and evaluated on the 24 months in 2024-2025. Finance has not specified an acceptable error threshold, so the results do not establish acceptance.

## Run

From the repository root, install [uv](https://docs.astral.sh/uv/getting-started/installation/) if necessary, then run:

```bash
uv sync
uv run pytest tests/pipelines/test_sales_forecast.py -q
uv run python scripts/sales_forecast.py
```

The focused test path is required because the root pytest configuration defaults to another service. The command produces `data/process/sales_forecast/frozen_forecast.csv`, `predictions.csv`, `metrics.json`, `forecast.png`, and `model.joblib`. The frozen forecast is written before test actuals are joined. Outputs are currently untracked and reproducible from the raw CSV and `uv.lock`; `model.joblib` is a Python pickle and must only be loaded from a trusted source. The raw dataset is never rewritten.

## Data and model

The loader requires the five columns specified in `sales-forecast-CONTEXT-nexova.md`, one consolidated row per month, the exact 2016-2025 calendar, and positive finite revenue. Blank fields become missing values; missing or invalid dates and revenue, duplicate months, and missing months fail explicitly. Contract counts and average values are checked when present, but are not features: their future values are unknown at the forecast origin. Missing optional contract fields therefore need no imputation.

The scikit-learn pipeline uses `RandomForestRegressor(n_estimators=200, min_samples_leaf=2, random_state=42, n_jobs=1)` without hyperparameter tuning. With only 96 training months, a forest is a practical starting point that needs less tuning and is easier to explain to Finance than sequential boosted trees, though an ensemble is not fully transparent. XGBoost is not assumed to be worse. A forest cannot extrapolate beyond its training target values, so it may understate growth. Trees do not need feature scaling; the pipeline's median imputer is fitted only on its training features and the target remains in USD.

The model uses month number and cyclical sine/cosine values, plus previous-month revenue, revenue 12 months earlier, and the mean of the three immediately preceding months. Twelve months are dropped as training warm-up, leaving 84 fitted rows. For the test horizon, each prediction is appended to the history for the next month's features; no test actuals or test-period contract values enter the model. Forecast and calibration fits only use data available at each respective origin.

The empirical range adds the 10th and 90th percentiles of signed errors from three separate 24-month recursive backtests, with origins at December 2019, 2020, and 2021, to each forecast horizon. It is an 80% nominal empirical range, not a guaranteed prediction interval. Only three overlapping historical errors are available per horizon. Test coverage is evaluated after the range is frozen and must not be used to recalibrate it. The comparison baseline repeats the matching 2023 monthly actuals for both test years.

## Metrics

All prediction metrics use only the 24 held-out months. PSI compares test revenue with the training revenue distribution; it is not an accuracy metric.

- **MSE (USD²):** mean squared difference between actual and forecast; it penalizes large misses. RMSE is its square root in USD. Normalized RMSE is `100 * RMSE / mean(test actual revenue)`, an interpretable percentage; MSE itself cannot be expressed as a percentage of dollar revenue by direct division.
- **MAE (USD):** average absolute monthly forecast error.
- **PSI:** training revenue quantile bins compare train and test shares with `(test_share - train_share) * ln(test_share / train_share)`. Shares receive `1e-6` smoothing and are renormalized. Growth or seasonality may shift this distribution. Business-line mix is unavailable and cannot be inferred from this PSI.
- **Normalized rank Gini:** with average ranks for ties, `G = 2 * sum(rank_i * actual_i) / (n * sum(actual_i)) - (n + 1) / n`; divide prediction-ranked G by actual-ranked G. One means perfect ordering, zero indicates no rank discrimination, negative values mean reversed ordering, and a constant actual series is undefined. It does not measure dollar accuracy or independently detect anomalous drops.
- **R²:** `1 - sum((actual - forecast)^2) / sum((actual - mean(actual))^2)`. One is perfect, zero matches the test-mean reference, and negative is worse; constant actuals make it undefined. R² was explicitly approved as a replacement for the unspecified K2 criterion and is not K2.

A low MSE alone does not demonstrate ranking quality, stable distributions, calibrated variability, robustness, or Finance acceptance. `metrics.json` contains the exact values, PSI bins and counts, seasonality and annual-growth summaries, interval coverage, source checksum, and library versions. The briefing's seasonal and growth percentages are approximate; observed yearly values can differ without changing the dataset. One holdout and three calibration windows do not guarantee future performance, and data ending in 2025 cannot establish a current forecast without newer approved observations.
