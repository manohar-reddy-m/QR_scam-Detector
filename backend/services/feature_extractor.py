"""
Feature extractor: converts URLFeatures model → numpy vector for ML inference.
"""
from __future__ import annotations

import numpy as np
from schemas.url import URLFeatures

FEATURE_NAMES = [
    "url_length", "hostname_length", "num_subdomains", "has_https", "has_ip_host",
    "num_dots", "num_hyphens", "num_at", "num_question_marks", "num_ampersands",
    "num_percent_encoded", "path_length", "query_length", "is_shortened_url",
    "has_suspicious_tld", "has_punycode", "has_double_slash", "special_char_ratio",
    "digit_ratio",
]


class FeatureExtractor:
    """Converts a URLFeatures Pydantic model to a numpy feature vector."""

    def to_vector(self, features: URLFeatures) -> np.ndarray:
        vec = [
            features.url_length,
            features.hostname_length,
            features.num_subdomains,
            int(features.has_https),
            int(features.has_ip_host),
            features.num_dots,
            features.num_hyphens,
            features.num_at,
            features.num_question_marks,
            features.num_ampersands,
            features.num_percent_encoded,
            features.path_length,
            features.query_length,
            int(features.is_shortened_url),
            int(features.has_suspicious_tld),
            int(features.has_punycode),
            int(features.has_double_slash),
            features.special_char_ratio,
            features.digit_ratio,
        ]
        return np.array(vec, dtype=float).reshape(1, -1)
