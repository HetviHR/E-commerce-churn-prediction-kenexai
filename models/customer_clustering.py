"""
models/customer_clustering.py
================================
Customer Segmentation & Persona Generation Module.

Performs KMeans clustering on behavioural features, assigns meaningful
persona labels to each cluster, saves the cluster model, and writes a
per-customer persona file to personas/persona_data.csv.

Usage:
    python models/customer_clustering.py
"""

import os
import sys
import pickle
import json
import numpy as np


def _numpy_safe(obj):
    """JSON default handler: converts any numpy scalar to a native Python type."""
    if isinstance(obj, np.integer):
        return int(obj)
    if isinstance(obj, np.floating):
        return float(obj)
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")
import pandas as pd

from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from pipeline.feature_engineering import preprocess_data

# ===========================================================================
# CONFIGURATION
# ===========================================================================
OUTPUT_DIR        = "models_output"
PERSONAS_DIR      = "personas"
CLUSTER_FILE      = os.path.join(OUTPUT_DIR, "customer_clusters.pkl")
PERSONA_CSV       = os.path.join(PERSONAS_DIR, "persona_data.csv")
PERSONA_META_FILE = os.path.join(PERSONAS_DIR, "persona_descriptions.json")

N_CLUSTERS    = 4
RANDOM_STATE  = 42

# Behavioural features used for clustering (subset of all features)
CLUSTER_FEATURES = [
    "Tenure",
    "SatisfactionScore",
    "OrderCount",
    "CouponUsed",
    "CashbackAmount",
    "DaySinceLastOrder",
    "HourSpendOnApp",
    "Complain",
    "OrderAmountHikeFromlastYear",
]

# Human-readable persona labels (mapped after cluster profiling)
# Order corresponds to KMeans cluster label 0-3.
# The actual best-fit assignment is computed dynamically in persona_label().
PERSONA_DEFINITIONS = {
    "Loyal Customers": {
        "description": "High tenure, high satisfaction, frequent orders, low churn risk.",
        "retention_tip": "Reward with exclusive loyalty perks and early-access deals.",
    },
    "Discount Seekers": {
        "description": "High coupon usage, price-driven, moderate satisfaction.",
        "retention_tip": "Offer personalised discount bundles before they migrate to competitors.",
    },
    "High Churn Risk": {
        "description": "Low engagement, many days since last order, complaints present.",
        "retention_tip": "Trigger urgent win-back campaign with strong incentive (20%+ coupon + free shipping).",
    },
    "Premium Customers": {
        "description": "High order value, high cashback, premium category preference.",
        "retention_tip": "Upsell premium memberships and curated product recommendations.",
    },
}


# ===========================================================================
# HELPERS
# ===========================================================================

def _assign_persona_labels(df_cluster: pd.DataFrame, cluster_col: str = "Cluster") -> dict:
    """
    Dynamically assign persona labels to cluster IDs based on cluster centroids.

    Strategy:
        - Cluster with highest mean Tenure + SatisfactionScore  → Loyal Customers
        - Cluster with highest mean CouponUsed                  → Discount Seekers
        - Cluster with highest mean DaySinceLastOrder + Complain → High Churn Risk
        - Remaining cluster                                      → Premium Customers
    """
    summary = df_cluster.groupby(cluster_col)[CLUSTER_FEATURES].mean()

    assigned: dict[int, str] = {}
    used_labels: set[str] = set()

    def _pick(cluster_id: int, label: str) -> None:
        assigned[cluster_id] = label
        used_labels.add(label)

    # Loyal → highest Tenure + SatisfactionScore
    loyal_id = (summary["Tenure"] + summary["SatisfactionScore"]).idxmax()
    _pick(loyal_id, "Loyal Customers")

    # Discount Seekers → highest CouponUsed
    remaining = summary.index.difference(list(assigned.keys()))
    discount_id = summary.loc[remaining, "CouponUsed"].idxmax()
    _pick(discount_id, "Discount Seekers")

    # High Churn Risk → highest DaySinceLastOrder + Complain
    remaining = summary.index.difference(list(assigned.keys()))
    churn_score = summary.loc[remaining, "DaySinceLastOrder"] + summary.loc[remaining, "Complain"]
    churn_id = churn_score.idxmax()
    _pick(churn_id, "High Churn Risk")

    # Premium Customers → whatever is left
    remaining = summary.index.difference(list(assigned.keys()))
    for cluster_id in remaining:
        _pick(cluster_id, "Premium Customers")

    return assigned


# ===========================================================================
# MAIN CLUSTERING PIPELINE
# ===========================================================================

def cluster_and_save() -> pd.DataFrame:
    """
    Full segmentation pipeline:
        1. Load & preprocess features
        2. Scale clustering features
        3. Fit KMeans (N_CLUSTERS)
        4. Assign persona labels
        5. Save model + persona CSV + metadata
    Returns
    -------
    df_result : pd.DataFrame
        Original features + Cluster ID + Persona columns.
    """
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(PERSONAS_DIR, exist_ok=True)

    # ── 1. Load features ───────────────────────────────────────────────────
    print("[clustering] Loading and preprocessing data...")
    X, y, _ = preprocess_data()
    print(f"[clustering] Feature matrix: {X.shape}")

    # ── 2. Select & scale clustering features ─────────────────────────────
    available = [f for f in CLUSTER_FEATURES if f in X.columns]
    missing   = set(CLUSTER_FEATURES) - set(available)
    if missing:
        print(f"[clustering] ⚠ Missing cluster features (will skip): {missing}")

    X_clust = X[available].copy()

    scaler  = StandardScaler()
    X_scaled = scaler.fit_transform(X_clust)

    # ── 3. Fit KMeans ──────────────────────────────────────────────────────
    print(f"[clustering] Fitting KMeans with {N_CLUSTERS} clusters...")
    kmeans = KMeans(
        n_clusters=N_CLUSTERS,
        init="k-means++",
        n_init=20,
        random_state=RANDOM_STATE,
    )
    cluster_labels = kmeans.fit_predict(X_scaled)

    sil_score = silhouette_score(X_scaled, cluster_labels)
    print(f"[clustering] Silhouette Score: {sil_score:.4f}")

    # ── 4. Build result dataframe ──────────────────────────────────────────
    df_result        = X.copy()
    df_result["Churn"]   = y.values
    df_result["Cluster"] = cluster_labels

    # ── 5. Assign persona labels ───────────────────────────────────────────
    persona_map  = _assign_persona_labels(df_result, cluster_col="Cluster")
    df_result["Persona"] = df_result["Cluster"].map(persona_map)

    print("[clustering] Cluster → Persona mapping:")
    for cid, pname in sorted(persona_map.items()):
        count = (df_result["Cluster"] == cid).sum()
        churn_rate = df_result.loc[df_result["Cluster"] == cid, "Churn"].mean() * 100
        print(f"  Cluster {cid} → {pname:<22} | n={count:4d} | churn_rate={churn_rate:.1f}%")

    # ── 6. Save model artefacts ────────────────────────────────────────────
    model_bundle = {
        "kmeans": kmeans,
        "scaler": scaler,
        "cluster_features": available,
        "persona_map": persona_map,
    }
    with open(CLUSTER_FILE, "wb") as f:
        pickle.dump(model_bundle, f)
    print(f"[clustering] Cluster model saved → {CLUSTER_FILE}")

    # ── 7. Save persona CSV ────────────────────────────────────────────────
    persona_cols = ["Cluster", "Persona", "Churn"] + available
    persona_cols = [c for c in persona_cols if c in df_result.columns]
    df_result[persona_cols].to_csv(PERSONA_CSV, index=False)
    print(f"[clustering] Persona data saved → {PERSONA_CSV}")

    # ── 8. Save persona metadata JSON ─────────────────────────────────────
    meta = {}
    for cid, pname in persona_map.items():
        meta[str(int(cid))] = {
            "cluster_id": int(cid),   # cast numpy int32/int64 → native Python int
            "persona": pname,
            **PERSONA_DEFINITIONS.get(pname, {}),
        }
    with open(PERSONA_META_FILE, "w") as f:
        json.dump(meta, f, indent=2, default=_numpy_safe)
    print(f"[clustering] Persona metadata saved → {PERSONA_META_FILE}")

    print("\n[clustering] 🎉 Segmentation complete.")
    return df_result


# ===========================================================================
# ENTRY POINT
# ===========================================================================
if __name__ == "__main__":
    cluster_and_save()
