"""
URL analysis Pydantic schemas.
"""
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, HttpUrl

from schemas.common import RiskLevel, RiskIndicator


class URLAnalyzeRequest(BaseModel):
    url: str = Field(..., min_length=1, max_length=2048, description="URL to analyze")


class URLFeatures(BaseModel):
    url_length: int
    hostname_length: int
    num_subdomains: int
    has_https: bool
    has_ip_host: bool
    num_dots: int
    num_hyphens: int
    num_at: int
    num_question_marks: int
    num_ampersands: int
    num_percent_encoded: int
    path_length: int
    query_length: int
    is_shortened_url: bool
    has_suspicious_tld: bool
    has_punycode: bool
    has_double_slash: bool
    special_char_ratio: float
    digit_ratio: float


class URLAnalyzeResponse(BaseModel):
    success: bool = True
    url: str
    risk_level: RiskLevel
    risk_score: float = Field(..., ge=0.0, le=1.0)
    ml_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    features: URLFeatures
    indicators: List[RiskIndicator] = Field(default_factory=list)
    explanation: str = ""
