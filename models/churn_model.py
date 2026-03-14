"""
Churn Prediction Model  (Jaini's Module)
==========================================
Train a churn prediction model on the Gold-layer feature set.

Input:   warehouse/gold/features.csv   ← from Hetvi's ETL pipeline
Output:  models/saved/churn_model.pkl  → for Tarishi's API & Dashboard

Usage (from project root):
    pip install -r requirements.txt
    python models/churn_model.py
"""

# TODO (Jaini): Implement model training
#
# Suggested steps:
#   1. Load  warehouse/gold/features.csv
#   2. Drop non-feature columns: CustomerID, CustomerSegment, *_raw columns
#   3. Target column: "Churn" (0 = stay, 1 = churn)
#   4. Handle class imbalance (72% Stay vs 28% Churn) — try SMOTE
#   5. Train/test split (stratified)
#   6. Train model (XGBoost / LightGBM / Random Forest)
#   7. Evaluate: accuracy, precision, recall, F1, ROC AUC
#   8. Save to  models/saved/churn_model.pkl
#
# Key features available in Gold layer:
#   - Recency, Frequency, EngagementScore, DiscountDependency
#   - ChurnRiskScore, Tenure, SatisfactionScore, Complain
#   - CashbackAmount, OrderCount, CouponUsed, etc.
#   - All normalised to [0, 1] range
