"""
pipeline/feature_engineering.py
================================
Feature Engineering Module for E-commerce Customer Churn Prediction.

Supports two input modes:
  1. Excel (temporary): data/raw/E Commerce Dataset.xlsx  (sheet: "E Comm")
  2. CSV  (production): warehouse/gold/features.csv

To switch datasets, change DATA_SOURCE_CONFIG at the top of this file.
"""

import os
import pandas as pd
from sklearn.preprocessing import LabelEncoder

# ===========================================================================
# DATASET CONFIGURATION — change only this block when the Gold dataset arrives
# ===========================================================================
DATA_SOURCE_CONFIG = {
    # "mode" can be "excel" or "csv"
    "mode": "excel",

    # Excel settings (temporary dataset)
    "excel_path": "data/raw/E Commerce Dataset.xlsx",
    "excel_sheet": "E Comm",

    # CSV settings (future Gold dataset from warehouse)
    "csv_path": "warehouse/gold/features.csv",
}

# Column that holds the churn label
TARGET_COLUMN = "Churn"

# CustomerID is an identifier — exclude from features
ID_COLUMN = "CustomerID"


# ===========================================================================
# HELPERS
# ===========================================================================

def _load_raw_data(config: dict) -> pd.DataFrame:
    """Load raw data from Excel or CSV depending on DATA_SOURCE_CONFIG."""
    mode = config.get("mode", "excel")

    if mode == "excel":
        path = config["excel_path"]
        sheet = config["excel_sheet"]
        print(f"[feature_engineering] Loading Excel: {path}  (sheet='{sheet}')")
        df = pd.read_excel(path, sheet_name=sheet)

    elif mode == "csv":
        path = config["csv_path"]
        print(f"[feature_engineering] Loading CSV: {path}")
        df = pd.read_csv(path)

    else:
        raise ValueError(f"Unknown data source mode: '{mode}'. Use 'excel' or 'csv'.")

    print(f"[feature_engineering] Raw shape: {df.shape}")
    return df


def _handle_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """Fill numeric NaNs with column median; categorical NaNs with mode."""
    numeric_cols = df.select_dtypes(include=["float64", "int64"]).columns.tolist()
    cat_cols = df.select_dtypes(include=["object"]).columns.tolist()

    for col in numeric_cols:
        median_val = df[col].median()
        missing = df[col].isna().sum()
        if missing:
            print(f"  [impute] '{col}': {missing} nulls → median={median_val:.2f}")
        df[col] = df[col].fillna(median_val)

    for col in cat_cols:
        mode_val = df[col].mode()[0] if not df[col].mode().empty else "Unknown"
        missing = df[col].isna().sum()
        if missing:
            print(f"  [impute] '{col}': {missing} nulls → mode='{mode_val}'")
        df[col] = df[col].fillna(mode_val)

    return df


def _encode_categorical(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Label-encode all object columns. Returns encoded df and encoder map."""
    cat_cols = df.select_dtypes(include=["object"]).columns.tolist()
    encoders: dict[str, LabelEncoder] = {}

    for col in cat_cols:
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col].astype(str))
        encoders[col] = le
        print(f"  [encode] '{col}': {list(le.classes_)}")

    return df, encoders


# ===========================================================================
# PUBLIC API
# ===========================================================================

def preprocess_data(
    config: dict | None = None,
) -> tuple[pd.DataFrame, pd.Series, dict]:
    """
    Full preprocessing pipeline: load → impute → encode → split X/y.

    Parameters
    ----------
    config : dict, optional
        Override DATA_SOURCE_CONFIG. Useful for testing with ad-hoc paths.

    Returns
    -------
    X : pd.DataFrame
        Feature matrix (CustomerID dropped, all columns numeric).
    y : pd.Series
        Binary churn target (0 = retained, 1 = churned).
    encoders : dict
        Mapping {column_name: fitted LabelEncoder} for inverse-transforming.
    """
    if config is None:
        config = DATA_SOURCE_CONFIG

    # 1. Load
    df = _load_raw_data(config)

    # 2. Drop identifier column if present
    if ID_COLUMN in df.columns:
        df = df.drop(columns=[ID_COLUMN])
        print(f"[feature_engineering] Dropped identifier column: '{ID_COLUMN}'")

    # 3. Impute missing values
    print("[feature_engineering] Imputing missing values...")
    df = _handle_missing_values(df)

    # 4. Encode categoricals
    print("[feature_engineering] Encoding categorical features...")
    df, encoders = _encode_categorical(df)

    # 5. Separate features and target
    if TARGET_COLUMN not in df.columns:
        raise ValueError(
            f"Target column '{TARGET_COLUMN}' not found. "
            f"Available columns: {list(df.columns)}"
        )

    X = df.drop(columns=[TARGET_COLUMN])
    y = df[TARGET_COLUMN]

    print(f"[feature_engineering] Final  X shape: {X.shape}")
    print(f"[feature_engineering] Target distribution:\n{y.value_counts().to_dict()}")
    return X, y, encoders


def load_features_for_clustering(config: dict | None = None) -> pd.DataFrame:
    """
    Return the fully processed feature matrix (no target) for clustering use.
    Convenient wrapper around preprocess_data().
    """
    X, _, _ = preprocess_data(config)
    return X


# ===========================================================================
# QUICK SMOKE TEST
# ===========================================================================
if __name__ == "__main__":
    X, y, encoders = preprocess_data()
    print("\n--- SAMPLE ---")
    print(X.head(3))
    print(y.head(3))