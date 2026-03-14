"""
ETL Pipeline  –  Medallion Architecture
=========================================
  Bronze  →  raw combined CSV
  Silver  →  cleaned & encoded data       → warehouse/silver/clean_data.csv
  Gold    →  feature-engineered dataset   → warehouse/gold/features.csv

This is the FINAL dataset your ML teammate uses for model training.

Usage (from project root):
    python pipeline/etl.py
"""

import os
import sys
import warnings
import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# ── Paths ─────────────────────────────────────────────────────────────────────
BRONZE_PATH = "warehouse/bronze/raw_data.csv"
SILVER_PATH = "warehouse/silver/clean_data.csv"
GOLD_PATH   = "warehouse/gold/features.csv"

# These are the exact known columns from the E Comm sheet
NUMERIC_COLS = [
    "Tenure", "WarehouseToHome", "HourSpendOnApp",
    "NumberOfDeviceRegistered", "SatisfactionScore",
    "NumberOfAddress", "Complain",
    "OrderAmountHikeFromlastYear", "CouponUsed",
    "OrderCount", "DaySinceLastOrder", "CashbackAmount",
]
CATEGORICAL_COLS = [
    "PreferredLoginDevice", "CityTier", "PreferredPaymentMode",
    "Gender", "PreferedOrderCat", "MaritalStatus",
]
TARGET_COL  = "Churn"
ID_COL      = "CustomerID"


# ══════════════════════════════════════════════════════════════════════════════
#  SILVER LAYER STEPS
# ══════════════════════════════════════════════════════════════════════════════

def step1_profile(df: pd.DataFrame) -> None:
    """Print a concise data quality report."""
    print("\n" + "─" * 60)
    print("  STEP 1 │ DATA PROFILING")
    print("─" * 60)
    print(f"  Rows             : {len(df):,}")
    print(f"  Columns          : {len(df.columns)}")
    print(f"  Duplicate rows   : {df.duplicated().sum():,}")

    missing = df.isnull().sum()
    missing = missing[missing > 0]
    if missing.empty:
        print("  Missing values   : None ✅")
    else:
        print("  Missing values   :")
        for col, cnt in missing.items():
            print(f"    • {col:<40} {cnt:>5}  ({cnt/len(df)*100:.1f}%)")

    print(f"\n  Churn distribution:")
    vc = df[TARGET_COL].value_counts()
    for val, cnt in vc.items():
        print(f"    • Churn={val}  →  {cnt:,} rows  ({cnt/len(df)*100:.1f}%)")


def step2_remove_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    """Drop exact duplicate rows."""
    print("\n" + "─" * 60)
    print("  STEP 2 │ REMOVE DUPLICATES")
    print("─" * 60)
    before = len(df)
    df = df.drop_duplicates()
    removed = before - len(df)
    print(f"  Removed: {removed:,}  |  Remaining: {len(df):,}")
    return df


def step3_fix_missing(df: pd.DataFrame) -> pd.DataFrame:
    """Fill missing values: median for numeric, mode for categorical."""
    print("\n" + "─" * 60)
    print("  STEP 3 │ HANDLE MISSING VALUES")
    print("─" * 60)

    filled = 0
    for col in NUMERIC_COLS:
        if col in df.columns and df[col].isnull().sum() > 0:
            val = df[col].median()
            df[col] = df[col].fillna(val)
            print(f"  {col:<40}  filled with median = {val:.2f}")
            filled += 1

    for col in CATEGORICAL_COLS:
        if col in df.columns and df[col].isnull().sum() > 0:
            val = df[col].mode()[0]
            df[col] = df[col].fillna(val)
            print(f"  {col:<40}  filled with mode  = '{val}'")
            filled += 1

    if filled == 0:
        print("  No missing values found ✅")

    return df


def step4_remove_outliers(df: pd.DataFrame) -> pd.DataFrame:
    """
    Conservative outlier removal using IQR (cap, not drop).
    We CAP instead of dropping to keep dataset size stable for ML.
    """
    print("\n" + "─" * 60)
    print("  STEP 4 │ OUTLIER TREATMENT  (IQR capping)")
    print("─" * 60)

    sensitive_cols = [
        "WarehouseToHome", "HourSpendOnApp", "NumberOfAddress",
        "OrderAmountHikeFromlastYear", "CouponUsed",
        "OrderCount", "DaySinceLastOrder", "CashbackAmount",
    ]

    for col in sensitive_cols:
        if col not in df.columns:
            continue
        Q1  = df[col].quantile(0.25)
        Q3  = df[col].quantile(0.75)
        IQR = Q3 - Q1
        lower = Q1 - 1.5 * IQR
        upper = Q3 + 1.5 * IQR
        out_count = ((df[col] < lower) | (df[col] > upper)).sum()
        df[col] = df[col].clip(lower=lower, upper=upper)
        if out_count:
            print(f"  {col:<40}  capped {out_count:>4} outliers  "
                  f"[{lower:.1f} – {upper:.1f}]")

    print(f"\n  Rows after outlier treatment: {len(df):,}")
    return df


def step5_encode(df: pd.DataFrame) -> pd.DataFrame:
    """
    Encode categorical columns with consistent ordinal mappings.
    (Readable by business users + ML-ready)
    """
    print("\n" + "─" * 60)
    print("  STEP 5 │ CATEGORICAL ENCODING")
    print("─" * 60)

    encodings = {
        "PreferredLoginDevice": {"Mobile": 0, "Computer": 1, "Phone": 0},
        "CityTier":             {"Tier1": 1, "Tier2": 2, "Tier3": 3,
                                 1: 1, 2: 2, 3: 3},
        "PreferredPaymentMode": {
            "Debit Card": 0, "Credit Card": 1, "UPI": 2,
            "Cash on Delivery": 3, "COD": 3, "E wallet": 4, "CC": 1,
        },
        "Gender":               {"Male": 0, "Female": 1},
        "MaritalStatus":        {"Single": 0, "Married": 1, "Divorced": 2},
        "PreferedOrderCat":     {
            "Laptop & Accessory": 0, "Mobile": 1, "Mobile Phone": 1,
            "Fashion": 2, "Electronics": 3, "Grocery": 4, "Others": 5,
        },
    }

    for col, mapping in encodings.items():
        if col in df.columns:
            df[col] = df[col].map(mapping)
            # Fill any unmapped with -1 so we can spot them
            df[col] = df[col].fillna(-1).astype(int)
            print(f"  ✅  {col}")

    return df


def step6_normalise(df: pd.DataFrame) -> pd.DataFrame:
    """
    Min-Max normalise numeric columns (except ID and Churn target).
    Stores originals as _raw columns for interpretability.
    """
    print("\n" + "─" * 60)
    print("  STEP 6 │ MIN-MAX NORMALISATION")
    print("─" * 60)

    skip = {TARGET_COL, ID_COL}
    for col in NUMERIC_COLS:
        if col not in df.columns or col in skip:
            continue
        col_min = df[col].min()
        col_max = df[col].max()
        if col_max - col_min > 0:
            # Keep a human-readable raw copy
            df[f"{col}_raw"] = df[col]
            df[col] = (df[col] - col_min) / (col_max - col_min)

    print("  All numeric columns normalised to [0, 1]")
    print("  Original values preserved in  *_raw  columns")
    return df


# ══════════════════════════════════════════════════════════════════════════════
#  GOLD LAYER  –  FEATURE ENGINEERING
# ══════════════════════════════════════════════════════════════════════════════

def step7_feature_engineering(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create business-meaningful features:
      • Recency              – how recently the customer ordered
      • Frequency            – how often they order
      • EngagementScore      – composite activity + satisfaction signal
      • DiscountDependency   – reliance on coupons
      • ChurnRiskScore       – composite risk signal (used for GenAI messages)
    """
    print("\n" + "─" * 60)
    print("  STEP 7 │ FEATURE ENGINEERING  (Gold Layer)")
    print("─" * 60)

    # Recency: 1 = very recent, 0 = hasn't ordered in a while
    if "DaySinceLastOrder" in df.columns:
        df["Recency"] = 1.0 - df["DaySinceLastOrder"]
        df["Recency"] = df["Recency"].clip(0, 1)
        print("  ✅  Recency             = 1 - DaySinceLastOrder (normalised)")

    # Frequency: normalised OrderCount (already normalised in step 6)
    if "OrderCount" in df.columns:
        df["Frequency"] = df["OrderCount"]
        print("  ✅  Frequency           = OrderCount (normalised)")

    # EngagementScore: average of app hours + satisfaction + device diversity
    eng_parts = []
    for c in ["HourSpendOnApp", "SatisfactionScore", "NumberOfDeviceRegistered"]:
        if c in df.columns:
            eng_parts.append(df[c])
    if eng_parts:
        df["EngagementScore"] = sum(eng_parts) / len(eng_parts)
        print(f"  ✅  EngagementScore     = mean({[c for c in ['HourSpendOnApp','SatisfactionScore','NumberOfDeviceRegistered'] if c in df.columns]})")

    # DiscountDependency: coupons used relative to orders placed
    if "CouponUsed" in df.columns and "OrderCount" in df.columns:
        denom = df["OrderCount"].replace(0, np.nan)
        df["DiscountDependency"] = (df["CouponUsed"] / denom).fillna(0).clip(0, 1)
        print("  ✅  DiscountDependency  = CouponUsed / OrderCount")

    # ChurnRiskScore: higher = more likely to churn
    #  Uses: complaints + low recency + low satisfaction + high discount dependency
    risk_parts = []
    if "Complain" in df.columns:
        risk_parts.append(df["Complain"])               # 0 or 1
    if "Recency" in df.columns:
        risk_parts.append(1.0 - df["Recency"])           # low recency = risky
    if "SatisfactionScore" in df.columns:
        risk_parts.append(1.0 - df["SatisfactionScore"]) # low score = risky
    if "DiscountDependency" in df.columns:
        risk_parts.append(df["DiscountDependency"])       # high = risky

    if risk_parts:
        df["ChurnRiskScore"] = sum(risk_parts) / len(risk_parts)
        df["ChurnRiskScore"] = df["ChurnRiskScore"].clip(0, 1)
        print("  ✅  ChurnRiskScore      = composite of Complain + Recency + Satisfaction + DiscountDependency")

    # RFM Category label (business-readable, useful for GenAI messages)
    if all(c in df.columns for c in ["Recency", "Frequency", "EngagementScore"]):
        conditions = [
            (df["Recency"] > 0.6) & (df["Frequency"] > 0.6) & (df["EngagementScore"] > 0.6),
            (df["Recency"] > 0.4) | (df["Frequency"] > 0.4),
        ]
        choices = ["Champion", "At Risk"]
        df["CustomerSegment"] = np.select(conditions, choices, default="Lost")
        print("  ✅  CustomerSegment     = Champion / At Risk / Lost")

    return df


# ══════════════════════════════════════════════════════════════════════════════
#  POSTGRESQL LOAD  (non-blocking)
# ══════════════════════════════════════════════════════════════════════════════

def load_to_postgres(df: pd.DataFrame) -> None:
    print("\n" + "─" * 60)
    print("  STEP 8 │ POSTGRESQL LOAD  (optional)")
    print("─" * 60)
    try:
        from database.db_connection import get_connection

        conn   = get_connection()
        cursor = conn.cursor()

        # Build DDL
        col_defs = []
        for col in df.columns:
            dtype = str(df[col].dtype)
            pg_type = ("INTEGER" if "int" in dtype
                       else "FLOAT" if "float" in dtype
                       else "TEXT")
            col_defs.append(f'"{col}" {pg_type}')

        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS customer_features ({", ".join(col_defs)});
        """)
        cursor.execute("TRUNCATE TABLE customer_features;")

        placeholders = ", ".join(["%s"] * len(df.columns))
        records = [
            tuple(None if (isinstance(v, float) and np.isnan(v)) else v
                  for v in row)
            for _, row in df.iterrows()
        ]
        cursor.executemany(
            f'INSERT INTO customer_features VALUES ({placeholders})', records
        )
        conn.commit()
        cursor.close()
        conn.close()
        print(f"  ✅  {len(records):,} rows → PostgreSQL 'customer_features'")

    except Exception as exc:
        print(f"  ⚠  Skipped (Docker container not running): {exc}")
        print("     Start with:  docker compose up -d  (in database/ folder)")


# ══════════════════════════════════════════════════════════════════════════════
#  MASTER ORCHESTRATOR
# ══════════════════════════════════════════════════════════════════════════════

def run_etl() -> None:
    print("\n" + "═" * 60)
    print("  E-COMMERCE CHURN  –  ETL PIPELINE")
    print("  Medallion: Bronze → Silver → Gold")
    print("═" * 60)

    if not os.path.exists(BRONZE_PATH):
        print(f"\n❌  Bronze file not found: {BRONZE_PATH}")
        print("    Run  python ingestion/data_ingestion.py  first.")
        sys.exit(1)

    # ── Load Bronze ───────────────────────────────────────────────────────
    print(f"\nLoading Bronze layer from {BRONZE_PATH} ...")
    df = pd.read_csv(BRONZE_PATH)
    print(f"  Rows: {len(df):,}  │  Columns: {len(df.columns)}")

    # ── Silver Steps ──────────────────────────────────────────────────────
    step1_profile(df)
    df = step2_remove_duplicates(df)
    df = step3_fix_missing(df)
    df = step4_remove_outliers(df)
    df = step5_encode(df)
    df = step6_normalise(df)

    os.makedirs(os.path.dirname(SILVER_PATH), exist_ok=True)
    df.to_csv(SILVER_PATH, index=False)
    print(f"\n✅  SILVER saved → {SILVER_PATH}  ({len(df):,} rows, {len(df.columns)} cols)")

    # ── Gold Steps ────────────────────────────────────────────────────────
    df_gold = step7_feature_engineering(df.copy())

    os.makedirs(os.path.dirname(GOLD_PATH), exist_ok=True)
    df_gold.to_csv(GOLD_PATH, index=False)
    print(f"✅  GOLD  saved → {GOLD_PATH}  ({len(df_gold):,} rows, {len(df_gold.columns)} cols)")

    # ── PostgreSQL (non-blocking) ─────────────────────────────────────────
    load_to_postgres(df_gold)

    # ── Final Summary ─────────────────────────────────────────────────────
    print("\n" + "═" * 60)
    print("  PIPELINE COMPLETE — SUMMARY")
    print("═" * 60)
    print(f"  Bronze  : {BRONZE_PATH}")
    print(f"  Silver  : {SILVER_PATH}")
    print(f"  Gold    : {GOLD_PATH}")
    print(f"\n  Final rows      : {len(df_gold):,}")
    print(f"  Final columns   : {len(df_gold.columns)}")
    print(f"\n  New features created:")
    for f in ["Recency", "Frequency", "EngagementScore",
              "DiscountDependency", "ChurnRiskScore", "CustomerSegment"]:
        if f in df_gold.columns:
            print(f"    ✅  {f}")
    print(f"\n  🎯  Share  warehouse/gold/features.csv  with your ML teammate!")
    print("═" * 60 + "\n")


if __name__ == "__main__":
    run_etl()
