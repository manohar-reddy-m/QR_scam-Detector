"""
QR analysis request/response Pydantic schemas.
"""
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from schemas.common import RiskLevel, RiskIndicator


class QRPayloadType(str, Enum):
    URL_HTTP = "URL_HTTP"
    URL_HTTPS = "URL_HTTPS"
    UPI_PAYMENT = "UPI_PAYMENT"
    TEXT = "TEXT"
    EMAIL = "EMAIL"
    PHONE = "PHONE"
    WIFI = "WIFI"
    VCARD = "VCARD"
    UNKNOWN = "UNKNOWN"


class QRDecodeResult(BaseModel):
    decoded: bool = Field(..., description="Whether a QR code was successfully decoded")
    payload: Optional[str] = Field(None, description="Raw decoded payload string")
    payload_type: QRPayloadType = Field(QRPayloadType.UNKNOWN, description="Classified payload type")
    confidence: float = Field(0.0, ge=0.0, le=1.0, description="Decode confidence (0–1)")
    decoder_used: str = Field("none", description="Which decoder succeeded: pyzbar | opencv | none")


class ThreatAnalysisResult(BaseModel):
    risk_level: RiskLevel
    risk_score: float = Field(..., ge=0.0, le=1.0, description="Composite risk score (0–1)")
    ml_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="ML model probability")
    indicators: List[RiskIndicator] = Field(default_factory=list)
    explanation: str = Field("", description="Human-readable explanation of the risk assessment")


class QRAnalyzeResponse(BaseModel):
    success: bool = True
    request_id: Optional[str] = None
    decode: QRDecodeResult
    threat: ThreatAnalysisResult
    metadata: Dict[str, Any] = Field(default_factory=dict)


class QRDecodeOnlyResponse(BaseModel):
    success: bool = True
    decode: QRDecodeResult


class QRDistortRequest(BaseModel):
    distortion_types: List[str] = Field(
        default=["blur", "noise", "rotate", "compress"],
        description="Distortion types to apply"
    )
    severity: float = Field(0.5, ge=0.0, le=1.0, description="Distortion severity")


class QRDistortResult(BaseModel):
    distortion_type: str
    severity: float
    still_decodable: bool
    decoded_payload: Optional[str] = None


class QRDistortResponse(BaseModel):
    success: bool = True
    original_payload: Optional[str] = None
    distortion_results: List[QRDistortResult] = Field(default_factory=list)
    robustness_score: float = Field(0.0, ge=0.0, le=1.0)
