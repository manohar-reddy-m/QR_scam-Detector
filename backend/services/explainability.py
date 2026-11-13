"""
Explainability service — generates human-readable feature importance explanations.
"""
from __future__ import annotations

from typing import Dict, List, Any, Optional
import numpy as np

from core.logging_config import get_logger

logger = get_logger(__name__)

FEATURE_DESCRIPTIONS = {
    "url_length": "Total URL length",
    "hostname_length": "Hostname length",
    "num_subdomains": "Number of subdomains",
    "has_https": "Uses HTTPS",
    "has_ip_host": "IP-based hostname",
    "num_dots": "Number of dots",
    "num_hyphens": "Number of hyphens",
    "num_at": "@ symbols present",
    "num_question_marks": "Query string count",
    "num_ampersands": "Ampersand count",
    "num_percent_encoded": "Percent-encoded characters",
    "path_length": "URL path length",
    "query_length": "Query string length",
    "is_shortened_url": "Known URL shortener",
    "has_suspicious_tld": "Suspicious TLD",
    "has_punycode": "Punycode / IDN domain",
    "has_double_slash": "Double-slash in path",
    "special_char_ratio": "Special character ratio",
    "digit_ratio": "Digit ratio",
}


class ExplainabilityService:
    """Generate feature importance explanations from ML model."""

    def explain(
        self,
        model: Any,
        feature_vector: np.ndarray,
        feature_names: List[str],
    ) -> List[Dict[str, Any]]:
        """
        Return top features contributing to the prediction.
        Uses feature_importances_ for RandomForest; falls back to coef_ for LogReg.
        """
        importances = None

        # Try inner estimator (CalibratedClassifierCV wraps the base)
        base = getattr(model, "estimator", model)
        if hasattr(base, "feature_importances_"):
            importances = base.feature_importances_
        elif hasattr(base, "coef_"):
            importances = np.abs(base.coef_[0])

        if importances is None:
            return []

        result = []
        for i, (name, imp) in enumerate(zip(feature_names, importances)):
            value = float(feature_vector[0][i]) if feature_vector is not None else None
            result.append({
                "feature": name,
                "description": FEATURE_DESCRIPTIONS.get(name, name),
                "importance": round(float(imp), 4),
                "value": value,
            })

        return sorted(result, key=lambda x: x["importance"], reverse=True)[:10]
