"""
KenexAI Dashboard  (Tarishi's Module)
=======================================
Interactive dashboard for exploring churn predictions,
customer segments, and GenAI retention strategies.

Input:   warehouse/gold/features.csv    ← from Hetvi's pipeline
         models/saved/churn_model.pkl   ← from Jaini's model
Output:  Web dashboard

Usage:
    streamlit run dashboard/app.py
    OR
    Build as React app (Tarishi's choice)
"""

# TODO (Tarishi): Implement the dashboard
#
# Option A: Streamlit (quick prototype)
#   - pip install streamlit plotly
#   - streamlit run dashboard/app.py
#
# Option B: React + FastAPI (production)
#   - React frontend with charts (Recharts / Plotly.js)
#   - FastAPI backend serving model predictions
#   - GenAI chat widget for retention strategies
#
# Suggested pages/features:
#   1. Overview — KPI cards (total customers, churn rate, at-risk count)
#   2. Customer Explorer — filterable table with churn probabilities
#   3. Model Performance — accuracy, F1, ROC AUC gauges
#   4. Retention Strategies — GenAI-powered strategy cards
#   5. Feature Analysis — correlation heatmap, distributions
