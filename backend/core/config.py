"""
Application Configuration via Pydantic Settings.
"""
from pathlib import Path
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict

# Absolute path to backend/ directory (config.py lives in backend/core/)
_BACKEND_DIR = Path(__file__).parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # App metadata
    APP_NAME: str = "QR Sentinel"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    PORT: int = 8000

    # API
    API_V1_PREFIX: str = "/api/v1"

    # CORS
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173", "http://localhost:8080"]

    # Security
    MAX_FILE_SIZE_MB: int = 10
    ALLOWED_IMAGE_TYPES: List[str] = ["image/png", "image/jpeg", "image/webp"]

    # ML Model — absolute path so it works regardless of CWD
    MODEL_DIR: Path = _BACKEND_DIR / "models"
    MODEL_FILE: str = "threat_classifier.joblib"
    PIPELINE_FILE: str = "preprocessing_pipeline.joblib"
    FEATURE_SCHEMA_FILE: str = "feature_schema.json"
    TRAINING_METRICS_FILE: str = "training_metrics.json"

    # Risk thresholds
    RISK_LOW_THRESHOLD: float = 0.3
    RISK_HIGH_THRESHOLD: float = 0.6

    # Logging
    LOG_LEVEL: str = "INFO"

    # URL analysis
    URL_SHORTENERS: List[str] = [
        "bit.ly", "tinyurl.com", "t.co", "goo.gl", "ow.ly", "buff.ly",
        "is.gd", "cli.gs", "pic.gd", "dlvr.it", "short.to", "rb.gy",
        "cutt.ly", "shorturl.at", "tiny.cc", "short.link", "v.gd",
    ]
    SUSPICIOUS_TLDS: List[str] = [
        ".xyz", ".top", ".club", ".work", ".gq", ".ml", ".cf", ".tk",
        ".ga", ".pw", ".cc", ".su", ".biz", ".link", ".click",
        ".download", ".win", ".loan", ".racing", ".review",
        # Country TLDs heavily abused in phishing
        ".ru", ".cn", ".bd", ".kz", ".ua", ".by",
        # Additional free/abused TLDs
        ".info", ".online", ".site", ".website", ".space", ".fun",
        ".icu", ".vip", ".monster", ".cyou", ".buzz",
    ]

    # High-value brand names whose presence as a SUBDOMAIN of a foreign domain is suspicious
    BRAND_NAMES_IN_SUBDOMAIN: List[str] = [
        "paypal", "amazon", "google", "apple", "microsoft", "netflix",
        "facebook", "instagram", "whatsapp", "twitter", "linkedin",
        "bank", "secure", "login", "account", "verify", "support",
        "update", "confirm", "billing", "payment", "wallet",
    ]


settings = Settings()
