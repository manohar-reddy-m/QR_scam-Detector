"""
Unit tests for FeatureExtractor service and vector schema compliance.
"""
import pytest
import numpy as np

from services.url_analyzer import URLAnalyzer
from services.feature_extractor import FeatureExtractor
from ml.feature_schema import FEATURE_NAMES, NUM_FEATURES


def test_feature_vector_shape_and_names():
    analyzer = URLAnalyzer()
    extractor = FeatureExtractor()
    features = analyzer.extract_features("https://secure.example.com/login?token=abc")
    vector = extractor.to_vector(features)
    
    assert isinstance(vector, np.ndarray)
    assert vector.shape == (1, NUM_FEATURES)
    assert len(FEATURE_NAMES) == NUM_FEATURES


def test_feature_vector_values_finite():
    analyzer = URLAnalyzer()
    extractor = FeatureExtractor()
    features = analyzer.extract_features("http://10.0.0.1/auth?x=1&y=2#frag")
    vector = extractor.to_vector(features)
    
    assert not np.isnan(vector).any()
    assert not np.isinf(vector).any()

