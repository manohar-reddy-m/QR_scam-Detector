"""
URL analysis endpoint.
"""
from fastapi import APIRouter, Request

from schemas.url import URLAnalyzeRequest, URLAnalyzeResponse
from services.url_analyzer import URLAnalyzer
from services.feature_extractor import FeatureExtractor
from services.risk_engine import RiskEngine

router = APIRouter()


@router.post("/analyze", response_model=URLAnalyzeResponse, summary="Analyze a URL for threats")
async def analyze_url(request: Request, body: URLAnalyzeRequest):
    """
    Extract features from a URL and assess its threat level using
    ML classification + rule-based indicators.
    """
    classifier = getattr(request.app.state, "classifier", None)

    analyzer = URLAnalyzer()
    features = analyzer.extract_features(body.url)

    extractor = FeatureExtractor()
    feature_vector = extractor.to_vector(features)

    ml_score = None
    if classifier and classifier.is_loaded:
        ml_score = classifier.predict_proba(feature_vector)

    engine = RiskEngine()
    risk_level, risk_score, indicators, explanation = engine.assess(
        features=features,
        ml_score=ml_score,
        raw_payload=body.url,
    )

    return URLAnalyzeResponse(
        url=body.url,
        risk_level=risk_level,
        risk_score=risk_score,
        ml_score=ml_score,
        features=features,
        indicators=indicators,
        explanation=explanation,
    )
