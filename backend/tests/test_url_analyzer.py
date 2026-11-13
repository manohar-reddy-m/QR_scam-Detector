"""
Unit tests for URL Analyzer & Security Feature Extraction.
"""
import pytest
from services.url_analyzer import URLAnalyzer


def test_benign_https_url():
    analyzer = URLAnalyzer()
    features = analyzer.extract_features("https://www.google.com/search?q=cybersecurity")
    assert features.has_https is True
    assert features.has_ip_host is False
    assert features.is_shortened_url is False
    assert features.has_suspicious_tld is False
    assert features.has_punycode is False
    assert features.num_dots >= 2


def test_ip_based_malicious_url():
    analyzer = URLAnalyzer()
    features = analyzer.extract_features("http://192.168.1.100:8080/admin/login.php")
    assert features.has_https is False
    assert features.has_ip_host is True
    assert features.num_dots == 4


def test_url_shortener_detection():
    analyzer = URLAnalyzer()
    features = analyzer.extract_features("https://bit.ly/3xY9ZzQ")
    assert features.is_shortened_url is True


def test_suspicious_tld_detection():
    analyzer = URLAnalyzer()
    features = analyzer.extract_features("http://bank-security-verify.tk/update")
    assert features.has_suspicious_tld is True


def test_punycode_detection():
    analyzer = URLAnalyzer()
    features = analyzer.extract_features("https://xn--pple-43d.com/login")
    assert features.has_punycode is True


def test_url_with_double_slash_redirect():
    analyzer = URLAnalyzer()
    features = analyzer.extract_features("https://example.com/redirect//evil.com")
    assert features.has_double_slash is True


def test_malformed_url_graceful_handling():
    analyzer = URLAnalyzer()
    features = analyzer.extract_features("not-a-valid-url-at-all!@@##$$")
    assert isinstance(features.url_length, int)
    assert features.url_length > 0
    assert features.has_https is False
