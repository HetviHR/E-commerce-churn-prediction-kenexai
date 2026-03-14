/**
 * api/usePrediction.js
 * ====================
 * Custom React hook — wraps predictFull() and getFeatureImportance() with
 * loading / error state so pages don't repeat boilerplate.
 *
 * Usage:
 *   const { prediction, featureImportance, loading, error } = usePrediction(customerFeatures);
 *
 * prediction  → full /predict/full response object (or null while loading)
 * featureImportance → feature_importance map from /feature-importance (or {})
 * loading     → true while any request is in flight
 * error       → string error message, or null
 */

import { useState, useEffect, useCallback } from 'react';
import { predictFull, getFeatureImportance, DEMO_CUSTOMER } from './client';

export function usePrediction(features = DEMO_CUSTOMER) {
    const [prediction, setPrediction] = useState(null);
    const [featureImportance, setFeatureImportance] = useState({});
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const fetchAll = useCallback(async () => {
        setLoading(true);
        setError(null);
        try {
            const [pred, imp] = await Promise.all([
                predictFull(features),
                getFeatureImportance(),
            ]);
            setPrediction(pred);
            setFeatureImportance(imp.feature_importance ?? {});
        } catch (err) {
            setError(err.message ?? 'Failed to connect to ML backend.');
        } finally {
            setLoading(false);
        }
    }, [JSON.stringify(features)]); // re-fetch when customer changes

    useEffect(() => { fetchAll(); }, [fetchAll]);

    return { prediction, featureImportance, loading, error, refetch: fetchAll };
}

/**
 * Lightweight hook — only fetches /feature-importance.
 * Used by DataQuality and Marketing pages.
 */
export function useFeatureImportance() {
    const [data, setData] = useState({});
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        getFeatureImportance()
            .then(res => setData(res.feature_importance ?? {}))
            .catch(err => setError(err.message ?? 'Could not load feature importance.'))
            .finally(() => setLoading(false));
    }, []);

    return { data, loading, error };
}
