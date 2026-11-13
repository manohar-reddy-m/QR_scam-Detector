"""
Unit tests for Image Robustness & Distortion Analysis.
"""
import pytest
from services.image_robustness import ImageRobustnessTester


def test_robustness_test_all(valid_qr_url_png):
    tester = ImageRobustnessTester()
    results = tester.test_all(valid_qr_url_png, severity=0.3)
    
    assert len(results) > 0
    distortion_types = [r.distortion_type for r in results]
    assert "blur" in distortion_types
    assert "noise" in distortion_types
    assert "rotate" in distortion_types
    assert "compress" in distortion_types
    assert "brightness" in distortion_types
    assert "crop" in distortion_types
    
    # Mild distortions (e.g. slight compression or brightness) should generally remain decodable
    at_least_one_decodable = any(r.still_decodable for r in results)
    assert at_least_one_decodable


def test_robustness_extreme_severity(valid_qr_url_png):
    tester = ImageRobustnessTester()
    results = tester.test_all(valid_qr_url_png, severity=1.0)
    assert len(results) > 0
    # At extreme severity 1.0 (heavy crop/noise/blur), decodability is typically impaired
    assert isinstance(results[0].still_decodable, bool)

