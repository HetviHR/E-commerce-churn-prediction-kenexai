"""
Data Ingestion  –  Bronze Layer
=================================
Loads raw Excel + pre-generated synthetic CSV,
merges them, and saves to warehouse/bronze/raw_data.csv.

PostgreSQL insert is OPTIONAL — the script skips it gracefully
so the rest of the pipeline is never blocked.

Usage (from project root):
    python ingestion/data_ingestion.py
"""

import os
import sys
import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# ── Paths ────────────────────────────────────────────────────────────────────
RAW_EXCEL   = "data/raw/ecommerce_churn.xlsx"
SYNTH_CSV   = "data/synthetic/synthetic_data.csv"
BRONZE_PATH = "warehouse/bronze/raw_data.csv"


# ── Step 1 : Load original Excel ─────────────────────────────────────────────
def load_excel() -> pd.DataFrame:
    print("[1/4] Loading Excel dataset (sheet: E Comm)...")
    df = pd.read_excel(RAW_EXCEL, sheet_name="E Comm")
    print(f"      Original rows : {len(df):,}  |  Columns: {len(df.columns)}")
    print(f"      Columns       : {list(df.columns)}")
    return df


# ── Step 2 : Merge with synthetic data ───────────────────────────────────────
def merge_synthetic(df_original: pd.DataFrame) -> pd.DataFrame:
    print("[2/4] Merging with synthetic data...")

    if not os.path.exists(SYNTH_CSV):
        print(f"      ⚠  Synthetic CSV not found at {SYNTH_CSV}")
        print("      Run  python data/synthetic/generator.py  first.")
        return df_original

    df_synth = pd.read_csv(SYNTH_CSV)

    # Keep only columns that exist in original
    shared_cols = [c for c in df_original.columns if c in df_synth.columns]
    df_synth    = df_synth[shared_cols]

    df_combined = pd.concat([df_original, df_synth], ignore_index=True)
    print(f"      Combined rows : {len(df_combined):,}")
    return df_combined


# ── Step 3 : Save Bronze CSV ──────────────────────────────────────────────────
def save_bronze(df: pd.DataFrame) -> None:
    print("[3/4] Saving Bronze layer...")
    os.makedirs(os.path.dirname(BRONZE_PATH), exist_ok=True)
    df.to_csv(BRONZE_PATH, index=False)
    print(f"      ✅  Saved → {BRONZE_PATH}  ({len(df):,} rows)")


# ── Step 4 : Optional PostgreSQL load (raw_customers) ────────────────────────
def load_postgres_optional(df: pd.DataFrame) -> None:
    print("[4/4] PostgreSQL load (optional, port 5433)...")
    try:
        from database.db_connection import get_connection
        import numpy as np

        conn   = get_connection()
        cursor = conn.cursor()

        # Build DDL dynamically
        col_defs = []
        for col in df.columns:
            dtype = str(df[col].dtype)
            pg_type = "INTEGER" if "int" in dtype else ("FLOAT" if "float" in dtype else "TEXT")
            col_defs.append(f'"{col}" {pg_type}')

        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS raw_customers ({", ".join(col_defs)});
        """)
        cursor.execute("TRUNCATE TABLE raw_customers;")

        placeholders = ", ".join(["%s"] * len(df.columns))
        records = [
            tuple(None if (v != v) else v for v in row)   # NaN → None
            for _, row in df.iterrows()
        ]
        cursor.executemany(f"INSERT INTO raw_customers VALUES ({placeholders})", records)
        conn.commit()
        cursor.close()
        conn.close()
        print(f"      ✅  {len(records):,} rows → PostgreSQL table 'raw_customers'")

    except Exception as exc:
        print(f"      ⚠  Skipped (Docker not running?): {exc}")


# ── Orchestrator ──────────────────────────────────────────────────────────────
def run_ingestion() -> pd.DataFrame:
    print("\n" + "═" * 60)
    print("  DATA INGESTION  –  BRONZE LAYER")
    print("═" * 60)

    df = load_excel()
    df = merge_synthetic(df)
    save_bronze(df)
    load_postgres_optional(df)

    print("\n✅  Ingestion complete.\n")
    return df


if __name__ == "__main__":
    run_ingestion()