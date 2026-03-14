"""
Churn Prediction Model
==========================================
Train a churn prediction model on the Gold-layer feature set.

Input:   warehouse/gold/features.csv   ← from ETL pipeline
Output:  models/saved/churn_model.pkl  → for API & Dashboard

Usage (from project root):
    python models/churn_model.py
"""

import os
import sys
import warnings
import numpy as np
import pandas as pd

# Fix Windows console encoding for Unicode characters
if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if sys.stderr.encoding != "utf-8":
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
import pickle

from sklearn.model_selection import train_test_split, StratifiedKFold
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, roc_auc_score, classification_report,
    confusion_matrix,
)
from sklearn.ensemble import VotingClassifier

warnings.filterwarnings("ignore")

# ── Paths ─────────────────────────────────────────────────────────────────────
GOLD_PATH  = "warehouse/gold/features.csv"
MODEL_DIR  = "models/saved"
MODEL_PATH = os.path.join(MODEL_DIR, "churn_model.pkl")
REPORT_PATH = os.path.join(MODEL_DIR, "training_report.txt")

# Columns to DROP before training (non-features)
DROP_COLS = [
    "CustomerID", "CustomerSegment",
    # Drop raw (un-normalised) columns — they duplicate info
    "Tenure_raw", "WarehouseToHome_raw", "HourSpendOnApp_raw",
    "NumberOfDeviceRegistered_raw", "SatisfactionScore_raw",
    "NumberOfAddress_raw", "Complain_raw",
    "OrderAmountHikeFromlastYear_raw", "CouponUsed_raw",
    "OrderCount_raw", "DaySinceLastOrder_raw", "CashbackAmount_raw",
]
TARGET_COL = "Churn"


# ══════════════════════════════════════════════════════════════════════════════
#  MODEL TRAINING
# ══════════════════════════════════════════════════════════════════════════════

def run_training() -> dict:
    """
    Full training pipeline:
      1. Load Gold features
      2. Prepare X, y
      3. Handle class imbalance with SMOTE
      4. Train XGBoost + LightGBM ensemble
      5. Evaluate on test set
      6. Save model + report
    Returns a dict of evaluation metrics.
    """
    print("\n" + "═" * 60)
    print("  CHURN MODEL TRAINING")
    print("  XGBoost + LightGBM Ensemble with SMOTE")
    print("═" * 60)

    # ── 1. Load Gold layer ────────────────────────────────────────────────
    if not os.path.exists(GOLD_PATH):
        print(f"\n❌  Gold file not found: {GOLD_PATH}")
        print("    Run the ETL pipeline first.")
        sys.exit(1)

    df = pd.read_csv(GOLD_PATH)
    print(f"\n  📂  Loaded: {GOLD_PATH}")
    print(f"      Rows: {len(df):,}  │  Columns: {len(df.columns)}")

    # ── 2. Prepare features and target ────────────────────────────────────
    print("\n" + "─" * 60)
    print("  STEP 1 │ FEATURE PREPARATION")
    print("─" * 60)

    # Drop non-feature columns
    drop_existing = [c for c in DROP_COLS if c in df.columns]
    X = df.drop(columns=drop_existing + [TARGET_COL], errors="ignore")
    y = df[TARGET_COL]

    print(f"  Features used     : {len(X.columns)}")
    print(f"  Target            : {TARGET_COL}")
    print(f"  Class distribution:")
    print(f"    • Stay  (0) : {(y == 0).sum():,}  ({(y == 0).mean() * 100:.1f}%)")
    print(f"    • Churn (1) : {(y == 1).sum():,}  ({(y == 1).mean() * 100:.1f}%)")

    feature_names = list(X.columns)
    print(f"\n  Feature list:")
    for i, col in enumerate(feature_names, 1):
        print(f"    {i:2d}. {col}")

    # ── 3. Train/Test Split ───────────────────────────────────────────────
    print("\n" + "─" * 60)
    print("  STEP 2 │ TRAIN/TEST SPLIT (80/20, stratified)")
    print("─" * 60)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    print(f"  Training set : {len(X_train):,} rows")
    print(f"  Test set     : {len(X_test):,} rows")

    # ── 4. SMOTE for class imbalance ──────────────────────────────────────
    print("\n" + "─" * 60)
    print("  STEP 3 │ SMOTE OVERSAMPLING")
    print("─" * 60)

    try:
        from imblearn.over_sampling import SMOTE

        smote = SMOTE(random_state=42)
        X_train_sm, y_train_sm = smote.fit_resample(X_train, y_train)
        print(f"  Before SMOTE : {len(X_train):,} rows")
        print(f"  After SMOTE  : {len(X_train_sm):,} rows")
        print(f"    • Stay  (0) : {(y_train_sm == 0).sum():,}")
        print(f"    • Churn (1) : {(y_train_sm == 1).sum():,}")
    except ImportError:
        print("  ⚠  imbalanced-learn not installed — skipping SMOTE")
        print("     Install with: pip install imbalanced-learn")
        X_train_sm, y_train_sm = X_train, y_train

    # ── 5. Train Models ──────────────────────────────────────────────────
    print("\n" + "─" * 60)
    print("  STEP 4 │ MODEL TRAINING")
    print("─" * 60)

    # --- XGBoost ---
    print("\n  🌲 Training XGBoost...")
    try:
        from xgboost import XGBClassifier

        xgb_model = XGBClassifier(
            n_estimators=200,
            max_depth=6,
            learning_rate=0.1,
            subsample=0.8,
            colsample_bytree=0.8,
            scale_pos_weight=(y_train == 0).sum() / max((y_train == 1).sum(), 1),
            use_label_encoder=False,
            eval_metric="logloss",
            random_state=42,
            verbosity=0,
        )
        xgb_model.fit(X_train_sm, y_train_sm)
        xgb_acc = accuracy_score(y_test, xgb_model.predict(X_test))
        print(f"     XGBoost test accuracy: {xgb_acc:.4f}")
        xgb_available = True
    except ImportError:
        print("  ⚠  xgboost not installed — skipping")
        xgb_available = False

    # --- LightGBM ---
    print("  🌿 Training LightGBM...")
    try:
        from lightgbm import LGBMClassifier

        lgb_model = LGBMClassifier(
            n_estimators=200,
            max_depth=6,
            learning_rate=0.1,
            subsample=0.8,
            colsample_bytree=0.8,
            scale_pos_weight=(y_train == 0).sum() / max((y_train == 1).sum(), 1),
            random_state=42,
            verbose=-1,
        )
        lgb_model.fit(X_train_sm, y_train_sm)
        lgb_acc = accuracy_score(y_test, lgb_model.predict(X_test))
        print(f"     LightGBM test accuracy: {lgb_acc:.4f}")
        lgb_available = True
    except ImportError:
        print("  ⚠  lightgbm not installed — skipping")
        lgb_available = False

    # --- Ensemble (Voting Classifier) ---
    print("\n  🏆 Building Ensemble...")
    if xgb_available and lgb_available:
        ensemble = VotingClassifier(
            estimators=[("xgb", xgb_model), ("lgb", lgb_model)],
            voting="soft",
        )
        ensemble.fit(X_train_sm, y_train_sm)
        final_model = ensemble
        model_name = "XGBoost + LightGBM Ensemble (soft vote)"
    elif xgb_available:
        final_model = xgb_model
        model_name = "XGBoost (standalone)"
    elif lgb_available:
        final_model = lgb_model
        model_name = "LightGBM (standalone)"
    else:
        # Fallback to RandomForest
        from sklearn.ensemble import RandomForestClassifier
        print("  ⚠  Neither XGBoost nor LightGBM available. Using Random Forest.")
        final_model = RandomForestClassifier(
            n_estimators=200, max_depth=10, random_state=42, n_jobs=-1
        )
        final_model.fit(X_train_sm, y_train_sm)
        model_name = "Random Forest (fallback)"

    print(f"     Model: {model_name}")

    # ── 6. Evaluation ────────────────────────────────────────────────────
    print("\n" + "─" * 60)
    print("  STEP 5 │ MODEL EVALUATION")
    print("─" * 60)

    y_pred = final_model.predict(X_test)
    y_proba = final_model.predict_proba(X_test)[:, 1]

    metrics = {
        "accuracy":  accuracy_score(y_test, y_pred),
        "precision": precision_score(y_test, y_pred),
        "recall":    recall_score(y_test, y_pred),
        "f1_score":  f1_score(y_test, y_pred),
        "roc_auc":   roc_auc_score(y_test, y_proba),
    }

    print(f"\n  📊  {model_name}")
    print(f"  {'─' * 40}")
    print(f"  Accuracy   : {metrics['accuracy']:.4f}")
    print(f"  Precision  : {metrics['precision']:.4f}")
    print(f"  Recall     : {metrics['recall']:.4f}")
    print(f"  F1 Score   : {metrics['f1_score']:.4f}")
    print(f"  ROC AUC    : {metrics['roc_auc']:.4f}")

    # Confusion Matrix
    cm = confusion_matrix(y_test, y_pred)
    print(f"\n  Confusion Matrix:")
    print(f"                  Predicted Stay  Predicted Churn")
    print(f"    Actual Stay   {cm[0][0]:>10,}    {cm[0][1]:>10,}")
    print(f"    Actual Churn  {cm[1][0]:>10,}    {cm[1][1]:>10,}")

    # Classification Report
    report = classification_report(y_test, y_pred, target_names=["Stay", "Churn"])
    print(f"\n  Classification Report:\n{report}")

    # Feature Importance (from XGBoost if available)
    print("  📈  Top 10 Feature Importances:")
    try:
        if xgb_available:
            importances = xgb_model.feature_importances_
        elif lgb_available:
            importances = lgb_model.feature_importances_
        else:
            importances = final_model.feature_importances_

        feat_imp = sorted(
            zip(feature_names, importances), key=lambda x: x[1], reverse=True
        )
        for i, (feat, imp) in enumerate(feat_imp[:10], 1):
            bar = "█" * int(imp / max(importances) * 20)
            print(f"    {i:2d}. {feat:<30s}  {imp:.4f}  {bar}")
    except AttributeError:
        print("    (Not available for this model type)")

    # ── 7. Save Model ────────────────────────────────────────────────────
    print("\n" + "─" * 60)
    print("  STEP 6 │ SAVE MODEL")
    print("─" * 60)

    os.makedirs(MODEL_DIR, exist_ok=True)

    model_artifact = {
        "model": final_model,
        "model_name": model_name,
        "feature_names": feature_names,
        "metrics": metrics,
        "target_col": TARGET_COL,
    }

    with open(MODEL_PATH, "wb") as f:
        pickle.dump(model_artifact, f)

    model_size = os.path.getsize(MODEL_PATH) / (1024 * 1024)
    print(f"  ✅  Model saved → {MODEL_PATH}  ({model_size:.2f} MB)")

    # Save training report
    report_lines = [
        "=" * 60,
        "  CHURN MODEL TRAINING REPORT",
        "=" * 60,
        f"  Model     : {model_name}",
        f"  Features  : {len(feature_names)}",
        f"  Train set : {len(X_train_sm):,} rows (after SMOTE)",
        f"  Test set  : {len(X_test):,} rows",
        "",
        "  METRICS",
        "  " + "─" * 40,
        f"  Accuracy  : {metrics['accuracy']:.4f}",
        f"  Precision : {metrics['precision']:.4f}",
        f"  Recall    : {metrics['recall']:.4f}",
        f"  F1 Score  : {metrics['f1_score']:.4f}",
        f"  ROC AUC   : {metrics['roc_auc']:.4f}",
        "",
        "  FEATURES USED",
        "  " + "─" * 40,
    ]
    for i, col in enumerate(feature_names, 1):
        report_lines.append(f"    {i:2d}. {col}")
    report_lines.append("\n" + "=" * 60)

    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))
    print(f"  📄  Report saved → {REPORT_PATH}")

    print("\n" + "═" * 60)
    print("  ✅  MODEL TRAINING COMPLETE")
    print("═" * 60 + "\n")

    return metrics


# ══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    run_training()
