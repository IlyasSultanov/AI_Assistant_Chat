from fastapi import APIRouter
from .health import router as health_router
__all__ = ("health_router",)

router = APIRouter(prefix="/api/v1", tags=["API"])
