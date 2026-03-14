"""
run_pipeline.py
================
One-command orchestrator for the entire ML Intelligence Layer.

Run order:
    1. Feature Engineering (smoke-test / verify data loads)
    2. Churn Model Training  →  models_output/churn_model.pkl
    3. Customer Clustering   →  models_output/customer_clusters.pkl
                                personas/persona_data.csv

Usage:
    python run_pipeline.py
    python run_pipeline.py --skip-train     # skip churn model if already saved
    python run_pipeline.py --skip-cluster   # skip clustering if already saved
"""

import argparse
import sys
import os

# ── ensure project root on path ───────────────────────────────────────────
sys.path.insert(0, os.path.dirname(__file__))


def _banner(text: str) -> None:
    width = 60
    print()
    print("=" * width)
    print(f"  {text}")
    print("=" * width)


def run_feature_check() -> None:
    _banner("STEP 1 / 3 — Feature Engineering (data check)")
    from pipeline.feature_engineering import preprocess_data
    X, y, _ = preprocess_data()
    print(f"✅  Data OK  |  X={X.shape}  |  Churn rate={y.mean()*100:.1f}%")


def run_churn_training() -> None:
    _banner("STEP 2 / 3 — Churn Model Training")
    from models.train_churn_model import train_and_save_best_model
    train_and_save_best_model()
    print("✅  Churn model saved.")


def run_clustering() -> None:
    _banner("STEP 3 / 3 — Customer Segmentation & Persona Generation")
    from models.customer_clustering import cluster_and_save
    cluster_and_save()
    print("✅  Clusters + personas saved.")


def main() -> None:
    parser = argparse.ArgumentParser(description="KenexAI ML Pipeline Orchestrator")
    parser.add_argument("--skip-train",   action="store_true", help="Skip churn model training")
    parser.add_argument("--skip-cluster", action="store_true", help="Skip customer clustering")
    args = parser.parse_args()

    run_feature_check()

    if not args.skip_train:
        run_churn_training()
    else:
        print("\n[skip] Churn model training skipped.")

    if not args.skip_cluster:
        run_clustering()
    else:
        print("\n[skip] Customer clustering skipped.")

    print()
    print("=" * 60)
    print("  🎉  ML Pipeline complete!")
    print("  👉  Start the API with:")
    print("      uvicorn api.model_api:app --reload --port 8000")
    print("=" * 60)


if __name__ == "__main__":
    main()
