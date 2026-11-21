from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from data.pipelines.sales_forecast.experiment import run_experiment


if __name__ == "__main__":
    report = run_experiment(ROOT / "data/raw/nexova_sales.csv", ROOT / "data/process/sales_forecast")
    print(f"MSE: {report['test_metrics']['mse_usd2']:.2f} USD²")
    print(f"RMSE: {report['test_metrics']['rmse_usd']:.2f} USD ({report['test_metrics']['normalized_rmse_percent']:.2f}% of average test revenue)")
    print(f"Revenue PSI: {report['revenue_psi']['psi']:.4f}")
    print(f"Normalized rank Gini: {report['test_metrics']['normalized_rank_gini']}")
    print(f"R²: {report['test_metrics']['r2']}")
    print(report["finance_acceptance"])