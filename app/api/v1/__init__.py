from fastapi import APIRouter
from .health import router as health_router
from .auth import router as auth_router
__all__ = ("health_router", "auth_router")

router = APIRouter(prefix="/api/v1", tags=["API"])

router.include_router(auth_router)
router.include_router(health_router)
