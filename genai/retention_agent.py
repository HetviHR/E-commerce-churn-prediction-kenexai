"""
GenAI Retention Agent
==========================================
Generates personalised retention strategies for customers predicted to churn.

Uses Google Gemini if API key available, otherwise falls back to
a rule-based strategy engine.

Input:   models/saved/churn_model.pkl   ← trained model
         warehouse/gold/features.csv    ← from ETL pipeline
Output:  genai/outputs/retention_strategies.csv
"""

import os
import sys
import pickle
import warnings
import numpy as np
import pandas as pd

# Fix Windows console encoding for Unicode characters
if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if sys.stderr.encoding != "utf-8":
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

warnings.filterwarnings("ignore")

# ── Paths ─────────────────────────────────────────────────────────────────────
GOLD_PATH       = "warehouse/gold/features.csv"
MODEL_PATH      = "models/saved/churn_model.pkl"
OUTPUT_DIR      = "genai/outputs"
OUTPUT_CSV      = os.path.join(OUTPUT_DIR, "retention_strategies.csv")


# ══════════════════════════════════════════════════════════════════════════════
#  RULE-BASED RETENTION ENGINE  (fallback when no API key)
# ══════════════════════════════════════════════════════════════════════════════

def _segment_strategy(row: pd.Series) -> dict:
    """Generate a retention strategy based on customer features."""

    strategies = []
    urgency = "Medium"
    channel = "Email"

    # --- High Churn Risk ---
    churn_prob = row.get("churn_probability", 0)
    if churn_prob > 0.7:
        urgency = "Critical"
        strategies.append("Immediate personal outreach by account manager")
        strategies.append("Offer exclusive loyalty discount (15-20% off next 3 orders)")
        channel = "Phone + Email"
    elif churn_prob > 0.5:
        urgency = "High"
        strategies.append("Send personalised re-engagement email within 24 hours")
        strategies.append("Offer targeted coupon (10-15% off preferred category)")
        channel = "Email + Push Notification"

    # --- Complaint-Based ---
    if row.get("Complain_raw", 0) == 1:
        strategies.append("Escalate to customer success team for complaint resolution")
        strategies.append("Send apology with compensation (free shipping on next order)")
        if urgency != "Critical":
            urgency = "High"

    # --- Low Satisfaction ---
    sat_score = row.get("SatisfactionScore_raw", 3)
    if sat_score <= 2:
        strategies.append("Schedule satisfaction survey with incentive")
        strategies.append("Assign dedicated support representative")
    elif sat_score == 3:
        strategies.append("Send feedback request with small reward")

    # --- Tenure-Based ---
    tenure = row.get("Tenure_raw", 12)
    if tenure <= 3:
        strategies.append("Activate new customer nurture campaign")
        strategies.append("Offer first-time loyalty program enrollment bonus")
    elif tenure >= 12:
        strategies.append("Recognise loyalty with VIP tier upgrade or milestone reward")

    # --- Order Category Specific ---
    order_cat = row.get("PreferedOrderCat", -1)
    cat_names = {0: "Laptop & Accessory", 1: "Mobile", 2: "Fashion",
                 3: "Electronics", 4: "Grocery", 5: "Others"}
    cat_name = cat_names.get(order_cat, "General")
    strategies.append(f"Curate personalised {cat_name} deals based on browsing history")

    # --- Low Engagement ---
    if row.get("HourSpendOnApp_raw", 5) <= 1:
        strategies.append("Send app engagement push: 'New arrivals in your favourite category'")
    if row.get("DaySinceLastOrder_raw", 0) >= 15:
        strategies.append("Trigger win-back campaign: 'We miss you!' with free delivery")

    # --- Cashback Strategy ---
    if row.get("CashbackAmount_raw", 0) < 100:
        strategies.append("Boost cashback rewards temporarily (2x cashback for 7 days)")

    # Ensure at least 3 strategies
    if len(strategies) < 3:
        strategies.append("Include in weekly newsletter with personalised recommendations")
        strategies.append("Offer free express delivery for next purchase")

    return {
        "urgency": urgency,
        "channel": channel,
        "strategies": " | ".join(strategies[:5]),  # Top 5 strategies
        "num_strategies": min(len(strategies), 5),
    }


# ══════════════════════════════════════════════════════════════════════════════
#  MAIN FUNCTION
# ══════════════════════════════════════════════════════════════════════════════

def run_retention_agent() -> None:
    """
    Generate retention strategies for at-risk customers.
    Uses Gemini if API key found, else rule-based fallback.
    """
    print("\n" + "═" * 60)
    print("  GENAI RETENTION AGENT")
    print("  Personalised Churn Prevention Strategies")
    print("═" * 60)

    # ── Load Model ────────────────────────────────────────────────────────
    if not os.path.exists(MODEL_PATH):
        print(f"\n❌  Model not found: {MODEL_PATH}")
        print("    Run model training first.")
        sys.exit(1)

    with open(MODEL_PATH, "rb") as f:
        artifact = pickle.load(f)

    model = artifact["model"]
    feature_names = artifact["feature_names"]
    print(f"  📦  Loaded model: {artifact['model_name']}")

    # ── Load Gold Data ────────────────────────────────────────────────────
    df = pd.read_csv(GOLD_PATH)
    print(f"  📂  Loaded: {GOLD_PATH}  ({len(df):,} rows)")

    # ── Get Churn Predictions ─────────────────────────────────────────────
    print("\n" + "─" * 60)
    print("  STEP 1 │ PREDICT CHURN PROBABILITIES")
    print("─" * 60)

    X = df[feature_names]
    churn_proba = model.predict_proba(X)[:, 1]
    df["churn_probability"] = churn_proba
    df["churn_prediction"] = (churn_proba >= 0.5).astype(int)

    at_risk = df[df["churn_prediction"] == 1].copy()
    print(f"  Total customers         : {len(df):,}")
    print(f"  Predicted to churn      : {len(at_risk):,}  ({len(at_risk)/len(df)*100:.1f}%)")
    print(f"  Average churn probability: {churn_proba.mean():.4f}")

    # ── Generate Strategies ───────────────────────────────────────────────
    print("\n" + "─" * 60)
    print("  STEP 2 │ GENERATE RETENTION STRATEGIES")
    print("─" * 60)

    # Check for Gemini API key
    use_gemini = False
    try:
        from dotenv import load_dotenv
        load_dotenv()
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key:
            use_gemini = True
            print("  🤖  Gemini API key found — using AI-powered strategies")
        else:
            print("  📋  No GEMINI_API_KEY — using rule-based strategies")
            print("       (Set GEMINI_API_KEY in .env for AI-powered strategies)")
    except ImportError:
        print("  📋  python-dotenv not installed — using rule-based strategies")

    if use_gemini:
        # Use Gemini for top 50 highest-risk customers
        top_risk = at_risk.nlargest(50, "churn_probability")
        print(f"  Generating AI strategies for top {len(top_risk)} highest-risk customers...")

        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            gemini = genai.GenerativeModel("gemini-1.5-flash")

            results = []
            for idx, row in top_risk.iterrows():
                prompt = f"""You are a customer retention specialist for an e-commerce company.
A customer with the following profile is likely to churn (probability: {row['churn_probability']:.2f}):
- Satisfaction Score: {row.get('SatisfactionScore_raw', 'N/A')}/5
- Has Complained: {'Yes' if row.get('Complain_raw', 0) == 1 else 'No'}
- Tenure: {row.get('Tenure_raw', 'N/A')} months
- Days Since Last Order: {row.get('DaySinceLastOrder_raw', 'N/A')}
- Order Count: {row.get('OrderCount_raw', 'N/A')}
- Cashback Amount: ${row.get('CashbackAmount_raw', 'N/A')}

Provide exactly 3 specific, actionable retention strategies. Be concise (1 line each)."""

                response = gemini.generate_content(prompt)
                strategies_text = response.text.strip()

                results.append({
                    "CustomerID": row.get("CustomerID"),
                    "churn_probability": row["churn_probability"],
                    "urgency": "Critical" if row["churn_probability"] > 0.7 else "High",
                    "channel": "Phone + Email" if row["churn_probability"] > 0.7 else "Email",
                    "strategies": strategies_text,
                    "source": "Gemini AI",
                })

            # For remaining at-risk customers, use rule-based
            remaining = at_risk[~at_risk.index.isin(top_risk.index)]
            for idx, row in remaining.iterrows():
                strat = _segment_strategy(row)
                results.append({
                    "CustomerID": row.get("CustomerID"),
                    "churn_probability": row["churn_probability"],
                    "urgency": strat["urgency"],
                    "channel": strat["channel"],
                    "strategies": strat["strategies"],
                    "source": "Rule Engine",
                })

            strategies_df = pd.DataFrame(results)

        except Exception as e:
            print(f"  ⚠  Gemini API error: {e}")
            print("  Falling back to rule-based strategies...")
            use_gemini = False

    if not use_gemini:
        # Rule-based strategies for all at-risk customers
        results = []
        for idx, row in at_risk.iterrows():
            strat = _segment_strategy(row)
            results.append({
                "CustomerID": row.get("CustomerID"),
                "churn_probability": row["churn_probability"],
                "urgency": strat["urgency"],
                "channel": strat["channel"],
                "strategies": strat["strategies"],
                "num_strategies": strat["num_strategies"],
                "source": "Rule Engine",
            })

        strategies_df = pd.DataFrame(results)

    # ── Sort by risk ──────────────────────────────────────────────────────
    strategies_df = strategies_df.sort_values("churn_probability", ascending=False)

    # ── Save Output ───────────────────────────────────────────────────────
    print("\n" + "─" * 60)
    print("  STEP 3 │ SAVE STRATEGIES")
    print("─" * 60)

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    strategies_df.to_csv(OUTPUT_CSV, index=False)
    print(f"  ✅  Saved → {OUTPUT_CSV}  ({len(strategies_df):,} customers)")

    # ── Summary ───────────────────────────────────────────────────────────
    print("\n" + "─" * 60)
    print("  SUMMARY")
    print("─" * 60)

    urgency_counts = strategies_df["urgency"].value_counts()
    for urg, cnt in urgency_counts.items():
        print(f"    {urg:<12s}  :  {cnt:,} customers")

    # Show sample strategies
    print(f"\n  📋  Sample Strategies (Top 3 highest risk):")
    for i, (_, row) in enumerate(strategies_df.head(3).iterrows(), 1):
        print(f"\n  ── Customer {row.get('CustomerID', 'N/A')} "
              f"(Churn Prob: {row['churn_probability']:.2f}) ──")
        print(f"     Urgency : {row['urgency']}")
        print(f"     Channel : {row['channel']}")
        for s in str(row['strategies']).split(" | "):
            print(f"     → {s.strip()}")

    print("\n" + "═" * 60)
    print("  ✅  RETENTION AGENT COMPLETE")
    print("═" * 60 + "\n")


# ══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    run_retention_agent()
