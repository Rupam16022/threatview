from fastapi import APIRouter
from datetime import datetime, timezone
from app.config import settings

router = APIRouter(tags=["Health"])


@router.get("/health")
async def health_check():
    """
    Health check endpoint returning system status, API version, and timestamp.
    Used by frontend, orchestrators, and monitoring services.
    """
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": "0.1.0",
        "environment": settings.APP_ENV,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "database": "pending_setup",  # Day 3 milestone
    }
