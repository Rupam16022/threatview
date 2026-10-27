from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routes import health_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager for startup and shutdown procedures.
    """
    # Startup tasks (e.g. database connection check, scheduler init in Day 5)
    print(f"[*] Starting {settings.APP_NAME} API in {settings.APP_ENV} mode...")
    yield
    # Shutdown tasks
    print(f"[*] Shutting down {settings.APP_NAME} API...")


app = FastAPI(
    title=settings.APP_NAME,
    description="Cybersecurity Threat Intelligence Platform API",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Configure Cross-Origin Resource Sharing (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routers
app.include_router(health_router, prefix=settings.API_PREFIX)


@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint returning service identity and quick links to documentation.
    """
    return {
        "name": settings.APP_NAME,
        "description": "Cybersecurity Threat Intelligence API",
        "documentation": "/docs",
        "health": f"{settings.API_PREFIX}/health",
        "version": "0.1.0",
    }
