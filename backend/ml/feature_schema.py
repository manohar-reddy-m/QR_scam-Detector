"""
Feature schema definitions — single source of truth for ML feature names and types.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List

FEATURE_NAMES: List[str] = [
    "url_length",
    "hostname_length",
    "num_subdomains",
    "has_https",
    "has_ip_host",
    "num_dots",
    "num_hyphens",
    "num_at",
    "num_question_marks",
    "num_ampersands",
    "num_percent_encoded",
    "path_length",
    "query_length",
    "is_shortened_url",
    "has_suspicious_tld",
    "has_punycode",
    "has_double_slash",
    "special_char_ratio",
    "digit_ratio",
]

NUM_FEATURES = len(FEATURE_NAMES)

FEATURE_TYPES = {
    "url_length": "int",
    "hostname_length": "int",
    "num_subdomains": "int",
    "has_https": "bool",
    "has_ip_host": "bool",
    "num_dots": "int",
    "num_hyphens": "int",
    "num_at": "int",
    "num_question_marks": "int",
    "num_ampersands": "int",
    "num_percent_encoded": "int",
    "path_length": "int",
    "query_length": "int",
    "is_shortened_url": "bool",
    "has_suspicious_tld": "bool",
    "has_punycode": "bool",
    "has_double_slash": "bool",
    "special_char_ratio": "float",
    "digit_ratio": "float",
}
