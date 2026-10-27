from fastapi import APIRouter
from datetime import datetime, timezone
from app.config import settings
from app.database import check_db_connection

router = APIRouter(tags=["Health"])


@router.get("/health")
async def health_check():
    """
    Health check endpoint returning system status, API version, and database connectivity.
    """
    db_connected = check_db_connection()
    return {
        "status": "healthy" if db_connected else "degraded",
        "service": settings.APP_NAME,
        "version": "0.1.0",
        "environment": settings.APP_ENV,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "database": "connected" if db_connected else "disconnected",
    }
