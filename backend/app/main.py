from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routes import (
    health_router,
    scheduler_router,
    dashboard_router,
    indicators_router,
    monitoring_router,
    reports_router,
)
from app.scheduler.jobs import threat_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan – start/stop the background scheduler."""
    print(f"[*] Starting {settings.APP_NAME} API in {settings.APP_ENV} mode...")
    if settings.ENABLE_SCHEDULER:
        try:
            threat_scheduler.start()
            print(f"[*] Scheduler started (interval: {settings.INGESTION_INTERVAL_MINUTES}m).")
        except Exception as exc:
            print(f"[!] Scheduler start warning: {exc}")
    yield
    print(f"[*] Shutting down {settings.APP_NAME} API...")
    if threat_scheduler.is_running():
        threat_scheduler.shutdown()
        print("[*] Scheduler stopped.")


app = FastAPI(
    title=settings.APP_NAME,
    description="Cybersecurity Threat Intelligence Platform API",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register all routers
app.include_router(health_router,     prefix=settings.API_PREFIX)
app.include_router(scheduler_router,  prefix=settings.API_PREFIX)
app.include_router(dashboard_router,  prefix=settings.API_PREFIX)
app.include_router(indicators_router, prefix=settings.API_PREFIX)
app.include_router(monitoring_router, prefix=settings.API_PREFIX)
app.include_router(reports_router,    prefix=settings.API_PREFIX)


@app.get("/", tags=["Root"])
async def root():
    return {
        "name": settings.APP_NAME,
        "version": "0.1.0",
        "docs": "/docs",
        "endpoints": {
            "health":     f"{settings.API_PREFIX}/health",
            "dashboard":  f"{settings.API_PREFIX}/dashboard/stats",
            "indicators": f"{settings.API_PREFIX}/indicators",
            "scheduler":  f"{settings.API_PREFIX}/scheduler/status",
            "monitoring": f"{settings.API_PREFIX}/monitoring/domains",
            "reports":    f"{settings.API_PREFIX}/reports/weekly",
        },
    }
