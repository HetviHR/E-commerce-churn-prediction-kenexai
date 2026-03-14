/**
 * api/client.js
 * =============
 * Centralised API client for the KenexAI FastAPI backend.
 *
 * All requests go through Vite's dev proxy (/api → http://localhost:8000).
 * In production, set VITE_API_BASE to the full backend URL.
 *
 * Exports:
 *   getHealth()            GET  /health
 *   getFeatureImportance() GET  /feature-importance
 *   predictChurn(features) POST /predict
 *   predictFull(features)  POST /predict/full
 */

const BASE = import.meta.env.VITE_API_BASE ?? '/api';

/** Shared fetch wrapper — throws a human-readable Error on non-2xx. */
async function apiFetch(path, options = {}) {
    const url = `${BASE}${path}`;
    const res = await fetch(url, {
        headers: { 'Content-Type': 'application/json' },
        ...options,
    });
    if (!res.ok) {
        const text = await res.text().catch(() => res.statusText);
        throw new Error(`[${res.status}] ${text}`);
    }
    return res.json();
}

// ── Endpoint functions ────────────────────────────────────────────────────

/** Check if the backend is running. */
export const getHealth = () => apiFetch('/health');

/**
 * Fetch global feature importance from the trained Random Forest.
 * Returns: { model_name, feature_importance: { [feature]: weight }, top_features: [] }
 */
export const getFeatureImportance = () => apiFetch('/feature-importance');

/**
 * Basic churn prediction.
 * @param {Object} features  Customer feature object matching CustomerFeatures schema
 * Returns: { churn_probability, churn_prediction, top_factors }
 */
export const predictChurn = (features) =>
    apiFetch('/predict', { method: 'POST', body: JSON.stringify(features) });

/**
 * Full pipeline prediction: churn + cluster + persona + retention strategy.
 * @param {Object} features  Customer feature object matching CustomerFeatures schema
 * Returns: { churn_probability, churn_prediction, top_factors, cluster, persona, retention_strategy }
 */
export const predictFull = (features) =>
    apiFetch('/predict/full', { method: 'POST', body: JSON.stringify(features) });

// ── Demo customer (used when no specific customer is selected) ─────────────

/**
 * A representative demo customer vector matching the API schema.
 * Replace / extend with real customer data from Hetvi's Gold dataset later.
 */
export const DEMO_CUSTOMER = {
    Tenure: 5,
    PreferredLoginDevice: 'Mobile Phone',
    CityTier: 1,
    WarehouseToHome: 18,
    PreferredPaymentMode: 'Debit Card',
    Gender: 'Male',
    HourSpendOnApp: 1.5,
    NumberOfDeviceRegistered: 3,
    PreferedOrderCat: 'Mobile',
    SatisfactionScore: 2,
    MaritalStatus: 'Single',
    NumberOfAddress: 2,
    Complain: 1,
    OrderAmountHikeFromlastYear: 15,
    CouponUsed: 4,
    OrderCount: 3,
    DaySinceLastOrder: 40,
    CashbackAmount: 60,
};
