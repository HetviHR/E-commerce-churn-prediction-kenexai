"""
Master Pipeline Runner
========================
Runs the full KenexAI pipeline end-to-end:

  1.  Synthetic data generation   (if not already done)
  2.  Data Ingestion → Bronze
  3.  ETL → Silver → Gold
  4.  Churn Model Training        (XGBoost + LightGBM ensemble)
  5.  GenAI Retention Agent       (Gemini or rule-based fallback)
  6.  PostgreSQL load             (optional, skips if Docker not running)

Usage (from project root):
    python run_pipeline.py              # full pipeline
    python run_pipeline.py --skip-model # skip model + GenAI (data only)

After completion, launch the dashboard:
    streamlit run dashboard/app.py
"""

import os
import sys
import time
import argparse


def section(title: str) -> None:
    print("\n" + "█" * 60)
    print(f"  {title}")
    print("█" * 60)


def main():
    parser = argparse.ArgumentParser(description="KenexAI Master Pipeline")
    parser.add_argument("--skip-model", action="store_true",
                        help="Skip model training and GenAI steps")
    args = parser.parse_args()

    start = time.time()
    print("\n" + "═" * 60)
    print("  KenexAI  │  E-Commerce Churn Data Pipeline")
    print("  Full End-to-End Run  🚀")
    print("═" * 60)

    # ── STEP 1: Synthetic Data (skip if already generated) ────────────────
    synth_csv = "data/synthetic/synthetic_data.csv"
    section("STEP 1 │ Synthetic Data Generation")

    if os.path.exists(synth_csv):
        import pandas as pd
        n = len(pd.read_csv(synth_csv))
        print(f"  ✅  Already generated ({n:,} rows) — skipping.")
    else:
        print("  Generating synthetic data...")
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "generator", "data/synthetic/generator.py"
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        mod.generate_synthetic_data()

    # ── STEP 2: Ingestion → Bronze ────────────────────────────────────────
    section("STEP 2 │ Data Ingestion  →  Bronze Layer")
    from ingestion.data_ingestion import run_ingestion
    run_ingestion()

    # ── STEP 3: ETL → Silver → Gold ───────────────────────────────────────
    section("STEP 3 │ ETL Pipeline  →  Silver & Gold Layers")
    from pipeline.etl import run_etl
    run_etl()

    if not args.skip_model:
        # ── STEP 4: Model Training ────────────────────────────────────────
        section("STEP 4 │ Churn Model Training")
        from models.churn_model import run_training
        run_training()

        # ── STEP 5: GenAI Retention Agent ─────────────────────────────────
        section("STEP 5 │ GenAI Retention Strategies")
        from genai.retention_agent import run_retention_agent
        run_retention_agent()
    else:
        print("\n  ⏭  Skipping model training and GenAI steps (--skip-model)")

    # ── Done ──────────────────────────────────────────────────────────────
    elapsed = time.time() - start
    print("\n" + "═" * 60)
    print("  🏁  PIPELINE COMPLETE")
    print("═" * 60)
    print(f"  Total time : {elapsed:.1f}s")
    print(f"\n  Outputs:")
    print(f"    📁  warehouse/bronze/raw_data.csv")
    print(f"    📁  warehouse/silver/clean_data.csv")
    print(f"    📁  warehouse/gold/features.csv")
    if not args.skip_model:
        print(f"    🤖  models/saved/   (trained ensemble)")
        print(f"    💡  genai/outputs/  (retention strategies)")
    print(f"\n  🚀  Launch dashboard:")
    print(f"      streamlit run dashboard/app.py")
    print("═" * 60 + "\n")


if __name__ == "__main__":
    main()
