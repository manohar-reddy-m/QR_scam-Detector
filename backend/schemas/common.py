"""
Shared/common Pydantic schemas.
"""
from enum import Enum
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    INCONCLUSIVE = "INCONCLUSIVE"


class SuccessResponse(BaseModel):
    success: bool = True
    data: Any = None


class ErrorDetail(BaseModel):
    code: str
    message: str


class ErrorResponse(BaseModel):
    success: bool = False
    error: ErrorDetail


class RiskIndicator(BaseModel):
    name: str = Field(..., description="Short name of the indicator")
    description: str = Field(..., description="Human-readable description")
    severity: str = Field(..., description="LOW | MEDIUM | HIGH")
    triggered: bool = Field(..., description="Whether this indicator was triggered")
