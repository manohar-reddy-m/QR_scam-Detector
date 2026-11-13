"""
API v1 router — aggregates all endpoint routers.
"""
from fastapi import APIRouter

from api.v1.endpoints import qr, url, model, system

api_router = APIRouter()

api_router.include_router(system.router, prefix="/system", tags=["System"])
api_router.include_router(qr.router, prefix="/qr", tags=["QR Analysis"])
api_router.include_router(url.router, prefix="/url", tags=["URL Analysis"])
api_router.include_router(model.router, prefix="/model", tags=["Model"])
