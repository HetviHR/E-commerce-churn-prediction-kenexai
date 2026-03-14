"""
api/model_api.py
=================
FastAPI Prediction Service for E-commerce Customer Churn Prediction.

Endpoints:
    POST /predict            → churn probability, prediction, top factors
    POST /predict/full       → churn + cluster + persona + retention strategy
    GET  /health             → service health check
    GET  /feature-importance → global feature importance (XAI)

Usage:
    uvicorn api.model_api:app --reload --host 0.0.0.0 --port 8000

Or from project root:
    python -m uvicorn api.model_api:app --reload
"""

from __future__ import annotations

import json
import os
import pickle
import sys
from typing import Optional

import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Resolve project root so sibling packages can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from genai.retention_agent import get_retention_message

# ===========================================================================
# PATHS
# ===========================================================================
MODEL_DIR          = "models_output"
CHURN_MODEL_PATH   = os.path.join(MODEL_DIR, "churn_model.pkl")
CLUSTER_MODEL_PATH = os.path.join(MODEL_DIR, "customer_clusters.pkl")
IMPORTANCE_PATH    = os.path.join(MODEL_DIR, "feature_importance.json")
COLUMNS_PATH       = os.path.join(MODEL_DIR, "feature_columns.json")
PERSONA_META_PATH  = os.path.join("personas", "persona_descriptions.json")
TOP_N_FACTORS      = 3   # features returned in /predict response


# ===========================================================================
# APP INIT
# ===========================================================================
app = FastAPI(
    title="KenexAI – Churn Prediction API",
    description=(
        "End-to-end ML inference service: churn probability, customer persona, "
        "XAI feature factors, and personalised retention strategies."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # tighten in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ===========================================================================
# MODEL LOADING (lazy, on first request)
# ===========================================================================
_churn_model   = None
_cluster_bundle = None
_feature_importance: dict = {}
_feature_columns: list[str] = []
_persona_meta: dict = {}


def _load_artifacts() -> None:
    global _churn_model, _cluster_bundle, _feature_importance
    global _feature_columns, _persona_meta

    # Churn model
    if not os.path.exists(CHURN_MODEL_PATH):
        raise RuntimeError(
            f"Churn model not found at '{CHURN_MODEL_PATH}'. "
            "Run `python models/train_churn_model.py` first."
        )
    with open(CHURN_MODEL_PATH, "rb") as f:
        _churn_model = pickle.load(f)

    # Cluster model
    if not os.path.exists(CLUSTER_MODEL_PATH):
        raise RuntimeError(
            f"Cluster model not found at '{CLUSTER_MODEL_PATH}'. "
            "Run `python models/customer_clustering.py` first."
        )
    with open(CLUSTER_MODEL_PATH, "rb") as f:
        _cluster_bundle = pickle.load(f)

    # Feature importance
    if os.path.exists(IMPORTANCE_PATH):
        with open(IMPORTANCE_PATH) as f:
            _feature_importance = json.load(f)

    # Column order
    if os.path.exists(COLUMNS_PATH):
        with open(COLUMNS_PATH) as f:
            _feature_columns = json.load(f)

    # Persona metadata
    if os.path.exists(PERSONA_META_PATH):
        with open(PERSONA_META_PATH) as f:
            _persona_meta = json.load(f)


@app.on_event("startup")
def load_on_startup() -> None:
    try:
        _load_artifacts()
        print("[API] ✅ All models loaded successfully.")
    except RuntimeError as exc:
        print(f"[API] ⚠  {exc}")
        print("[API]    The service will start but /predict will fail until models are trained.")


# ===========================================================================
# SCHEMAS
# ===========================================================================

class CustomerFeatures(BaseModel):
    """Input schema — mirrors the dataset feature set."""
    Tenure:                     float = Field(..., example=12)
    PreferredLoginDevice:       str   = Field(..., example="Mobile Phone")
    CityTier:                   int   = Field(..., ge=1, le=3, example=1)
    WarehouseToHome:            float = Field(..., example=15)
    PreferredPaymentMode:       str   = Field(..., example="Debit Card")
    Gender:                     str   = Field(..., example="Male")
    HourSpendOnApp:             float = Field(..., example=3.0)
    NumberOfDeviceRegistered:   int   = Field(..., example=4)
    PreferedOrderCat:           str   = Field(..., example="Laptop & Accessory")
    SatisfactionScore:          int   = Field(..., ge=1, le=5, example=3)
    MaritalStatus:              str   = Field(..., example="Married")
    NumberOfAddress:            int   = Field(..., example=2)
    Complain:                   int   = Field(..., ge=0, le=1, example=0)
    OrderAmountHikeFromlastYear: Optional[float] = Field(None, example=15.0)
    CouponUsed:                 Optional[float] = Field(None, example=2.0)
    OrderCount:                 Optional[float] = Field(None, example=8.0)
    DaySinceLastOrder:          Optional[float] = Field(None, example=5.0)
    CashbackAmount:             Optional[float] = Field(None, example=180.0)


class ChurnResponse(BaseModel):
    churn_probability: float
    churn_prediction: int
    top_factors: list[str]


class FullPredictionResponse(BaseModel):
    churn_probability: float
    churn_prediction: int
    top_factors: list[str]
    cluster: int
    persona: str
    retention_strategy: dict


# ===========================================================================
# FEATURE PREPARATION
# ===========================================================================

_LABEL_MAPS: dict[str, list[str]] = {
    "PreferredLoginDevice": ["Computer", "Mobile Phone", "Phone"],
    "PreferredPaymentMode": [
        "Cash on Delivery", "CC", "COD", "Credit Card",
        "Debit Card", "E wallet", "UPI",
    ],
    "Gender":              ["Female", "Male"],
    "PreferedOrderCat":   [
        "Fashion", "Grocery", "Laptop & Accessory",
        "Mobile", "Mobile Phone", "Others",
    ],
    "MaritalStatus":       ["Divorced", "Married", "Single"],
}


def _encode_column(value: str, classes: list[str]) -> int:
    """Simple label encoding aligned to sorted classes (mirrors LabelEncoder)."""
    sorted_classes = sorted(classes)
    if value in sorted_classes:
        return sorted_classes.index(value)
    # unknown category — map to 0
    return 0


def _prepare_features(data: CustomerFeatures) -> pd.DataFrame:
    """Convert Pydantic model to a numeric DataFrame aligned to training columns."""
    raw = data.dict()

    # Encode categorical columns
    for col, classes in _LABEL_MAPS.items():
        if col in raw:
            raw[col] = _encode_column(str(raw[col]), classes)

    # Replace None with 0 for optional fields
    for k, v in raw.items():
        if v is None:
            raw[k] = 0.0

    df = pd.DataFrame([raw])

    # Align to training column order
    if _feature_columns:
        for col in _feature_columns:
            if col not in df.columns:
                df[col] = 0.0
        df = df[_feature_columns]

    return df


def _get_top_factors(n: int = TOP_N_FACTORS) -> list[str]:
    """Return the top-N most important features from the saved XAI artefact."""
    top_features = _feature_importance.get("top_features", [])
    return top_features[:n]


def _resolve_persona(cluster_id: int) -> str:
    """Look up the persona name for a given cluster ID."""
    if _cluster_bundle:
        persona_map: dict[int, str] = _cluster_bundle.get("persona_map", {})
        return persona_map.get(cluster_id, "Unknown")
    return "Unknown"


def _predict_cluster(df: pd.DataFrame) -> int:
    """Return the cluster ID for a customer feature vector."""
    if _cluster_bundle is None:
        return -1
    kmeans  = _cluster_bundle["kmeans"]
    scaler  = _cluster_bundle["scaler"]
    c_feats = _cluster_bundle["cluster_features"]

    # Only keep cluster features that exist in the input
    available = [f for f in c_feats if f in df.columns]
    X_c = df[available].copy()

    # Pad missing cluster features with zeros
    for f in c_feats:
        if f not in X_c:
            X_c[f] = 0.0
    X_c = X_c[c_feats]

    X_scaled = scaler.transform(X_c)
    return int(kmeans.predict(X_scaled)[0])


# ===========================================================================
# ENDPOINTS
# ===========================================================================

@app.get("/health", tags=["Utility"])
def health_check():
    """Service liveness check."""
    return {
        "status": "ok",
        "churn_model_loaded":   _churn_model is not None,
        "cluster_model_loaded": _cluster_bundle is not None,
    }


@app.get("/feature-importance", tags=["XAI"])
def feature_importance():
    """Return global feature importance computed from the training run."""
    if not _feature_importance:
        raise HTTPException(
            status_code=404,
            detail="Feature importance not found. Train the model first.",
        )
    return _feature_importance


@app.post("/predict", response_model=ChurnResponse, tags=["Prediction"])
def predict_churn(data: CustomerFeatures) -> ChurnResponse:
    """
    Predict churn probability and return the top influencing features.

    Returns
    -------
    churn_probability : float  — Model probability score [0, 1]
    churn_prediction  : int    — Binary label (1 = likely to churn)
    top_factors       : list   — Top N feature names driving the prediction
    """
    if _churn_model is None:
        raise HTTPException(
            status_code=503,
            detail="Churn model not loaded. Run `python models/train_churn_model.py`.",
        )

    df = _prepare_features(data)
    prob = float(_churn_model.predict_proba(df)[0][1])
    pred = int(_churn_model.predict(df)[0])
    factors = _get_top_factors(TOP_N_FACTORS)

    return ChurnResponse(
        churn_probability=round(prob, 4),
        churn_prediction=pred,
        top_factors=factors,
    )


@app.post("/predict/full", response_model=FullPredictionResponse, tags=["Prediction"])
def predict_full(data: CustomerFeatures) -> FullPredictionResponse:
    """
    Full-pipeline prediction: churn + cluster + persona + retention strategy.

    Returns
    -------
    churn_probability  : float  — Churn probability [0, 1]
    churn_prediction   : int    — Binary churn label
    top_factors        : list   — Top influencing features (XAI)
    cluster            : int    — KMeans cluster ID
    persona            : str    — Human-readable persona label
    retention_strategy : dict   — AI-generated retention message and incentives
    """
    if _churn_model is None or _cluster_bundle is None:
        raise HTTPException(
            status_code=503,
            detail="Models not loaded. Train churn and cluster models first.",
        )

    df = _prepare_features(data)

    # Churn prediction
    prob    = float(_churn_model.predict_proba(df)[0][1])
    pred    = int(_churn_model.predict(df)[0])
    factors = _get_top_factors(TOP_N_FACTORS)

    # Cluster & persona
    cluster_id = _predict_cluster(df)
    persona    = _resolve_persona(cluster_id)

    # Retention strategy from GenAI agent
    retention = get_retention_message(
        churn_probability       = prob,
        persona                 = persona,
        cluster_id              = cluster_id,
        satisfaction_score      = float(data.SatisfactionScore),
        coupon_used             = float(data.CouponUsed or 0),
        days_since_last_order   = float(data.DaySinceLastOrder or 0),
        order_count             = float(data.OrderCount or 0),
        complain                = int(data.Complain),
        cashback_amount         = float(data.CashbackAmount or 0),
        hour_spend_on_app       = float(data.HourSpendOnApp),
    )

    return FullPredictionResponse(
        churn_probability  = round(prob, 4),
        churn_prediction   = pred,
        top_factors        = factors,
        cluster            = cluster_id,
        persona            = persona,
        retention_strategy = retention,
    )
