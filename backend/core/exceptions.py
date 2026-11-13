"""
Custom exceptions and FastAPI exception handlers.
No stack traces are ever leaked in API responses.
"""
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from core.logging_config import get_logger

logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# Domain exceptions
# ---------------------------------------------------------------------------

class QRSentinelError(Exception):
    """Base error for QR Sentinel domain errors."""
    status_code: int = 500
    error_code: str = "INTERNAL_ERROR"
    message: str = "An unexpected error occurred."

    def __init__(self, message: str | None = None, **kwargs):
        self.message = message or self.__class__.message
        self.detail = kwargs
        super().__init__(self.message)


class FileTooLargeError(QRSentinelError):
    status_code = 413
    error_code = "FILE_TOO_LARGE"
    message = "Uploaded file exceeds the maximum allowed size."


class InvalidFileTypeError(QRSentinelError):
    status_code = 415
    error_code = "INVALID_FILE_TYPE"
    message = "Unsupported file type. Allowed: PNG, JPEG, WEBP."


class QRDecodeError(QRSentinelError):
    status_code = 422
    error_code = "QR_DECODE_FAILED"
    message = "Could not decode a QR code from the provided image."


class ModelNotLoadedError(QRSentinelError):
    status_code = 503
    error_code = "MODEL_NOT_LOADED"
    message = "The ML model is not loaded. Please try again later."


class FeatureExtractionError(QRSentinelError):
    status_code = 422
    error_code = "FEATURE_EXTRACTION_FAILED"
    message = "Failed to extract features from the input."


# ---------------------------------------------------------------------------
# Error response helper
# ---------------------------------------------------------------------------

def _error_response(status_code: int, error_code: str, message: str) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={"success": False, "error": {"code": error_code, "message": message}},
    )


# ---------------------------------------------------------------------------
# Register handlers on the FastAPI app
# ---------------------------------------------------------------------------

def register_exception_handlers(app: FastAPI) -> None:

    @app.exception_handler(QRSentinelError)
    async def handle_domain_error(request: Request, exc: QRSentinelError):
        logger.warning("Domain error", error_code=exc.error_code, message=exc.message, path=request.url.path)
        return _error_response(exc.status_code, exc.error_code, exc.message)

    @app.exception_handler(StarletteHTTPException)
    async def handle_http_error(request: Request, exc: StarletteHTTPException):
        logger.warning("HTTP error", status=exc.status_code, path=request.url.path)
        return _error_response(exc.status_code, "HTTP_ERROR", str(exc.detail))

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(request: Request, exc: RequestValidationError):
        logger.warning("Validation error", errors=exc.errors(), path=request.url.path)
        return _error_response(422, "VALIDATION_ERROR", "Request validation failed. Check your input.")

    @app.exception_handler(Exception)
    async def handle_unexpected_error(request: Request, exc: Exception):
        logger.error("Unexpected error", exc_info=exc, path=request.url.path)
        return _error_response(500, "INTERNAL_ERROR", "An unexpected internal error occurred.")
