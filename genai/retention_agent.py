"""
GenAI Retention Agent
======================
Generates personalised retention strategies for customers predicted to churn.

Works in two modes:
  1. **Rule-based** (always available): Returns per-persona retention strategy,
     urgency level, and offer type — no API key needed.
  2. **Gemini-enhanced** (optional): If GEMINI_API_KEY is set in the .env file,
     uses Google Gemini to craft a more detailed, personalised retention message.

Called from:  api/model_api.py  → /predict/full endpoint
Returns:      dict  (retention_message, urgency_level, offer_type, actions)
"""

from __future__ import annotations

import os
from typing import Optional

# ── Optional: load .env so GEMINI_API_KEY is available ──────────────────────
try:
    from dotenv import load_dotenv  # type: ignore[import-untyped]
    load_dotenv()
except ImportError:
    pass  # python-dotenv not installed; rely on env var set at system level

# ── Optional: Google Gemini SDK ──────────────────────────────────────────────
try:
    import google.generativeai as _genai  # type: ignore[import-untyped]
    _GEMINI_AVAILABLE = True
except Exception:
    _genai = None
    _GEMINI_AVAILABLE = False


# ── Persona-to-strategy mapping ──────────────────────────────────────────────

_PERSONA_STRATEGIES: dict[str, dict] = {
    "High Churn Risk": {
        "urgency_level":    "CRITICAL",
        "offer_type":       "Discount Coupon",
        "actions": [
            "Send immediate win-back email with 20% discount code",
            "Assign dedicated support agent for next interaction",
            "Offer free priority shipping on next 3 orders",
        ],
        "message_template": (
            "Hi there,\n\n"
            "We noticed you haven't been around lately, and we genuinely miss you! "
            "Your satisfaction means everything to us, so we've put together a "
            "special offer just for you.\n\n"
            "🎁 Use code COMEBACK20 for 20% off your next order — no minimum spend.\n\n"
            "We'd love to hear your feedback too. Reply to this email and a dedicated "
            "support agent will reach out personally.\n\n"
            "— The KenexAI Team"
        ),
    },
    "Premium Customers": {
        "urgency_level":    "HIGH",
        "offer_type":       "Loyalty Reward",
        "actions": [
            "Enrol in exclusive loyalty rewards programme",
            "Grant early access to new product launches",
            "Offer complimentary annual subscription upgrade",
        ],
        "message_template": (
            "Hi there,\n\n"
            "As one of our most valued customers, we want to make sure your "
            "experience with us is always exceptional.\n\n"
            "🏆 You've been selected for our exclusive Loyalty Rewards programme: "
            "earn double points on every purchase, get early access to new "
            "arrivals, and enjoy complimentary upgrades.\n\n"
            "Thank you for being part of our premium community.\n\n"
            "— The KenexAI Team"
        ),
    },
    "Loyal Customers": {
        "urgency_level":    "MEDIUM",
        "offer_type":       "VIP Benefits",
        "actions": [
            "Upgrade to VIP tier with enhanced benefits",
            "Offer birthday / anniversary surprise gift",
            "Invite to exclusive community events",
        ],
        "message_template": (
            "Hi there,\n\n"
            "Your loyalty means the world to us! 🌟 As a long-standing member "
            "of our community, we'd like to upgrade you to our VIP tier.\n\n"
            "Enjoy priority customer support, exclusive VIP-only deals, and a "
            "special gift on your next anniversary with us.\n\n"
            "Thank you for being with us — we look forward to serving you for "
            "many more years.\n\n"
            "— The KenexAI Team"
        ),
    },
    "Discount Seekers": {
        "urgency_level":    "HIGH",
        "offer_type":       "Targeted Promotions",
        "actions": [
            "Send personalised coupon bundle based on order history",
            "Offer flash sale access for favourite categories",
            "Provide cashback on next 2 purchases",
        ],
        "message_template": (
            "Hi there,\n\n"
            "We know you love a great deal — so we've got something special!\n\n"
            "🛍️ Enjoy an exclusive bundle of personalised coupons selected just "
            "for the categories you love most. Plus, get 10% cashback on your "
            "next two orders.\n\n"
            "Hurry — these offers expire in 48 hours!\n\n"
            "— The KenexAI Team"
        ),
    },
}

_DEFAULT_STRATEGY: dict = {
    "urgency_level":    "MEDIUM",
    "offer_type":       "Personalised Outreach",
    "actions": [
        "Send personalised re-engagement email",
        "Offer a satisfaction survey with reward on completion",
    ],
    "message_template": (
        "Hi there,\n\n"
        "We'd love to have you back! We've put together a personalised offer "
        "just for you. Use code RETURN15 for 15% off your next order.\n\n"
        "If there's anything we can do to improve your experience, please "
        "don't hesitate to reach out.\n\n"
        "— The KenexAI Team"
    ),
}


# ── Urgency score based on churn probability ─────────────────────────────────

def _urgency_from_prob(churn_probability: float, base_urgency: str) -> str:
    """Override urgency level when churn probability is very high or very low."""
    if churn_probability >= 0.85:
        return "CRITICAL"
    if churn_probability >= 0.65:
        return "HIGH"
    if churn_probability <= 0.25:
        return "LOW"
    return base_urgency


# ── Optional: Gemini-enhanced message ────────────────────────────────────────

def _gemini_message(
    persona: str,
    churn_probability: float,
    satisfaction_score: float,
    days_since_last_order: float,
    complain: int,
    offer_type: str,
) -> Optional[str]:
    """
    Generate a personalised retention message via Google Gemini.
    Returns None if the API key is missing or the call fails.
    """
    api_key = os.getenv("GEMINI_API_KEY", "")
    if not api_key or not _GEMINI_AVAILABLE or _genai is None:
        return None

    try:
        _genai.configure(api_key=api_key)  # type: ignore[union-attr]
        model = _genai.GenerativeModel("gemini-1.5-flash")  # type: ignore[union-attr]

        prompt = (
            f"You are a customer retention specialist. Write a short, empathetic, "
            f"personalised retention email (≤120 words) for an e-commerce customer "
            f"with the following profile:\n"
            f"- Persona: {persona}\n"
            f"- Churn Probability: {round(churn_probability * 100)}%\n"
            f"- Satisfaction Score: {satisfaction_score}/5\n"
            f"- Days Since Last Order: {int(days_since_last_order)}\n"
            f"- Recent Complaint: {'Yes' if complain else 'No'}\n"
            f"- Recommended Offer: {offer_type}\n\n"
            f"Start with 'Hi there,' and sign off as '— The KenexAI Team'. "
            f"Do not use markdown. Keep tone warm and genuine."
        )

        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception:
        return None  # fall back to rule-based template


# ── Public API ────────────────────────────────────────────────────────────────

def get_retention_message(
    churn_probability: float,
    persona: str,
    cluster_id: int,
    satisfaction_score: float,
    coupon_used: float,
    days_since_last_order: float,
    order_count: float,
    complain: int,
    cashback_amount: float,
    hour_spend_on_app: float,
) -> dict:
    """
    Build and return a retention strategy dictionary for the given customer.

    Returns
    -------
    dict with keys:
        retention_message : str   — Human-readable retention message
        urgency_level     : str   — "CRITICAL" | "HIGH" | "MEDIUM" | "LOW"
        offer_type        : str   — Short label for the recommended incentive
        actions           : list  — Ordered list of recommended retention actions
    """
    strategy = _PERSONA_STRATEGIES.get(persona, _DEFAULT_STRATEGY)

    urgency = _urgency_from_prob(churn_probability, strategy["urgency_level"])

    # Try Gemini first, fall back to rule-based template
    ai_message = _gemini_message(
        persona=persona,
        churn_probability=churn_probability,
        satisfaction_score=satisfaction_score,
        days_since_last_order=days_since_last_order,
        complain=complain,
        offer_type=strategy["offer_type"],
    )

    return {
        "retention_message": ai_message or strategy["message_template"],
        "urgency_level":     urgency,
        "offer_type":        strategy["offer_type"],
        "actions":           strategy["actions"],
    }
