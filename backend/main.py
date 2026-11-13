"""
QR Sentinel — FastAPI Application Entry Point
"""
import time
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from core.config import settings
from core.logging_config import get_logger, setup_logging
from core.exceptions import register_exception_handlers
from api.v1.router import api_router

logger = get_logger(__name__)

START_TIME = time.time()



@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: startup and shutdown events."""
    setup_logging()
    logger.info("QR Sentinel backend starting up", version=settings.APP_VERSION)
    # Pre-load ML model at startup if not already loaded
    try:
        from services.threat_classifier import classifier_service
        if not classifier_service.is_loaded:
            classifier_service.load_model()
        app.state.classifier = classifier_service
        if classifier_service.is_loaded:
            logger.info("ML model loaded successfully")
        else:
            logger.warning("ML model not available — running without ML classification")
    except Exception as exc:
        logger.warning("ML model not loaded at startup", error=str(exc))
        app.state.classifier = None
    yield
    logger.info("QR Sentinel backend shutting down")


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        description="AI-Powered QR Code Threat Detection Platform",
        version=settings.APP_VERSION,
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Request ID + timing middleware
    @app.middleware("http")
    async def request_middleware(request: Request, call_next):
        request_id = str(uuid.uuid4())[:8]
        request.state.request_id = request_id
        start = time.perf_counter()
        response = await call_next(request)
        duration_ms = round((time.perf_counter() - start) * 1000, 2)
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Response-Time"] = f"{duration_ms}ms"
        return response

    # Exception handlers
    register_exception_handlers(app)

    # Routers
    app.include_router(api_router, prefix=settings.API_V1_PREFIX)

    @app.get("/", include_in_schema=False)
    async def root():
        return {
            "service": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "status": "running",
            "docs": "/api/docs",
            "uptime_seconds": round(time.time() - START_TIME, 1),
        }

    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=settings.PORT, reload=settings.DEBUG, log_level="info")
