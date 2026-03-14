"""
models/train_churn_model.py
============================
Churn Prediction Model Training Module.

Trains Logistic Regression, Random Forest, and XGBoost classifiers,
compares their performance, selects the best model, computes feature
importance (XAI), and saves the artefacts to models_output/.

Usage:
    python models/train_churn_model.py
"""

import os
import sys
import pickle
import json
import warnings
import numpy as np
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    roc_auc_score,
)
from xgboost import XGBClassifier

# Allow imports from the project root regardless of cwd
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from pipeline.feature_engineering import preprocess_data

warnings.filterwarnings("ignore")


# ===========================================================================
# CONFIGURATION
# ===========================================================================
OUTPUT_DIR = "models_output"
MODEL_FILE = os.path.join(OUTPUT_DIR, "churn_model.pkl")
IMPORTANCE_FILE = os.path.join(OUTPUT_DIR, "feature_importance.json")
TEST_SIZE = 0.2
RANDOM_STATE = 42
TOP_N_FEATURES = 10   # number of top features saved for XAI


# ===========================================================================
# HELPERS
# ===========================================================================

def _build_candidates() -> dict:
    """Return the candidate classifiers with sensible defaults."""
    return {
        "Logistic Regression": LogisticRegression(
            max_iter=1000,
            random_state=RANDOM_STATE,
            class_weight="balanced",
        ),
        "Random Forest": RandomForestClassifier(
            n_estimators=200,
            max_depth=10,
            random_state=RANDOM_STATE,
            class_weight="balanced",
            n_jobs=-1,
        ),
        "XGBoost": XGBClassifier(
            n_estimators=200,
            max_depth=6,
            learning_rate=0.05,
            use_label_encoder=False,
            eval_metric="logloss",
            random_state=RANDOM_STATE,
            n_jobs=-1,
        ),
    }


def _evaluate(model, X_test: pd.DataFrame, y_test: pd.Series, name: str) -> dict:
    """Compute and print evaluation metrics for a fitted model."""
    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]

    acc = accuracy_score(y_test, y_pred)
    auc = roc_auc_score(y_test, y_prob)

    print(f"\n{'='*55}")
    print(f"  {name}")
    print(f"{'='*55}")
    print(f"  Accuracy : {acc:.4f}")
    print(f"  ROC-AUC  : {auc:.4f}")
    print("\n  Classification Report:")
    print(classification_report(y_test, y_pred, target_names=["Retained", "Churned"]))

    return {"name": name, "model": model, "accuracy": acc, "roc_auc": auc}


def _compute_feature_importance(
    model, feature_names: list[str], top_n: int = TOP_N_FEATURES
) -> dict:
    """
    Extract feature importances from a tree-based model.
    Falls back to absolute coefficient weights for linear models.
    """
    if hasattr(model, "feature_importances_"):
        importances = model.feature_importances_
    elif hasattr(model, "coef_"):
        importances = np.abs(model.coef_[0])
    else:
        print("[XAI] Model does not expose feature importances — skipping.")
        return {}

    importance_map = dict(zip(feature_names, importances.tolist()))
    # Sort descending and keep top N
    sorted_imp = dict(
        sorted(importance_map.items(), key=lambda x: x[1], reverse=True)[:top_n]
    )
    return sorted_imp


# ===========================================================================
# MAIN TRAINING PIPELINE
# ===========================================================================

def train_and_save_best_model() -> None:
    """
    End-to-end training pipeline:
        1. Load & preprocess data
        2. Train/evaluate all candidate models
        3. Select best by ROC-AUC
        4. Save model + feature importance artefacts
    """
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # ── 1. Preprocess ──────────────────────────────────────────────────────
    print("\n[train] Loading and preprocessing data...")
    X, y, _ = preprocess_data()

    # ── 2. Train / Test split ──────────────────────────────────────────────
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE, stratify=y
    )
    print(f"[train] Train: {X_train.shape[0]} rows | Test: {X_test.shape[0]} rows")

    # ── 3. Train & evaluate candidates ─────────────────────────────────────
    candidates = _build_candidates()
    results = []

    for name, model in candidates.items():
        print(f"\n[train] Training '{name}'...")
        model.fit(X_train, y_train)
        result = _evaluate(model, X_test, y_test, name)
        results.append(result)

    # ── 4. Select best ─────────────────────────────────────────────────────
    best = max(results, key=lambda r: r["roc_auc"])
    print(f"\n[train] ✅ Best model: '{best['name']}'")
    print(f"         ROC-AUC = {best['roc_auc']:.4f} | Accuracy = {best['accuracy']:.4f}")

    best_model = best["model"]

    # ── 5. Feature importance (XAI) ────────────────────────────────────────
    # Always derive importances from the Random Forest for consistency
    print("\n[XAI] Computing feature importance from Random Forest...")
    rf_model = next(r["model"] for r in results if r["name"] == "Random Forest")
    importance_map = _compute_feature_importance(rf_model, list(X.columns))

    print("[XAI] Top features:")
    for feat, val in importance_map.items():
        print(f"  {feat:<35} {val:.4f}")

    # ── 6. Persist artefacts ───────────────────────────────────────────────
    with open(MODEL_FILE, "wb") as f:
        pickle.dump(best_model, f)
    print(f"\n[train] Model saved → {MODEL_FILE}")

    importance_payload = {
        "model_name": best["name"],
        "feature_importance": importance_map,
        "top_features": list(importance_map.keys()),
    }
    with open(IMPORTANCE_FILE, "w") as f:
        json.dump(importance_payload, f, indent=2)
    print(f"[train] Feature importance saved → {IMPORTANCE_FILE}")

    # Also save full column order so the API can align inputs
    col_order_file = os.path.join(OUTPUT_DIR, "feature_columns.json")
    with open(col_order_file, "w") as f:
        json.dump(list(X.columns), f, indent=2)
    print(f"[train] Column order saved → {col_order_file}")

    print("\n[train] 🎉 Training complete.")


# ===========================================================================
# ENTRY POINT
# ===========================================================================
if __name__ == "__main__":
    train_and_save_best_model()
