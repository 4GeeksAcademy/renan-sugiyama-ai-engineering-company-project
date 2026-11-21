from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error


def regression_metrics(actual: np.ndarray, predicted: np.ndarray) -> dict:
    actual = np.asarray(actual, dtype=float)
    predicted = np.asarray(predicted, dtype=float)
    mse = float(mean_squared_error(actual, predicted))
    rmse = float(np.sqrt(mse))
    denominator = float(np.sum((actual - np.mean(actual)) ** 2))
    return {
        "mse_usd2": mse,
        "rmse_usd": rmse,
        "normalized_rmse_percent": 100 * rmse / float(np.mean(actual)),
        "mae_usd": float(mean_absolute_error(actual, predicted)),
        "r2": None if denominator == 0 else 1 - float(np.sum((actual - predicted) ** 2)) / denominator,
        "normalized_rank_gini": normalized_rank_gini(actual, predicted),
    }


def normalized_rank_gini(actual: np.ndarray, predicted: np.ndarray) -> float | None:
    actual = np.asarray(actual, dtype=float)
    predicted = np.asarray(predicted, dtype=float)
    if len(actual) == 0 or len(actual) != len(predicted) or not np.isfinite(actual).all() or not np.isfinite(predicted).all():
        raise ValueError("Gini requires equally sized finite arrays")
    if np.any(actual < 0) or actual.sum() <= 0:
        raise ValueError("Gini requires nonnegative actual values with a positive sum")
    count = len(actual)

    def ranked_gini(values: np.ndarray) -> float:
        ranks = pd.Series(values).rank(method="average").to_numpy()
        return float(2 * np.dot(ranks, actual) / (count * actual.sum()) - (count + 1) / count)

    perfect = ranked_gini(actual)
    return None if abs(perfect) < 1e-12 else ranked_gini(predicted) / perfect


def revenue_psi(reference: np.ndarray, comparison: np.ndarray) -> dict:
    reference = np.asarray(reference, dtype=float)
    comparison = np.asarray(comparison, dtype=float)
    if not len(reference) or not len(comparison) or not np.isfinite(reference).all() or not np.isfinite(comparison).all():
        raise ValueError("PSI requires nonempty finite distributions")
    edges = np.unique(np.quantile(reference, np.linspace(0, 1, 11)))
    if len(edges) < 3:
        raise ValueError("PSI requires at least two training-derived bins")
    edges[0], edges[-1] = -np.inf, np.inf
    train_counts = np.histogram(reference, bins=edges)[0]
    test_counts = np.histogram(comparison, bins=edges)[0]
    train_shares = train_counts / len(reference) + 1e-6
    test_shares = test_counts / len(comparison) + 1e-6
    train_shares /= train_shares.sum()
    test_shares /= test_shares.sum()
    value = float(np.sum((test_shares - train_shares) * np.log(test_shares / train_shares)))
    return {
        "psi": value,
        "bin_edges_usd": ["-inf" if np.isneginf(edge) else "+inf" if np.isposinf(edge) else float(edge) for edge in edges],
        "train_counts": train_counts.tolist(),
        "test_counts": test_counts.tolist(),
    }