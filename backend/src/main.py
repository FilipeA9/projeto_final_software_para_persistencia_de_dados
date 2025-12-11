"""
FastAPI main application module.

Entry point for the Tourism Platform API with lifecycle management.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config.settings import settings
from src.config.postgres import init_db, close_db
from src.config.mongodb import init_mongo, close_mongo
from src.config.redis import init_redis, close_redis
from src.middleware.error_handler import setup_error_handlers
from src.middleware.rate_limit import rate_limit_middleware
from src.utils.logging_config import setup_logging
import logging

# Setup logging
setup_logging(
    log_level=getattr(settings, "LOG_LEVEL", "INFO"),
    log_to_file=True,
    log_to_console=True,
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager - handles startup and shutdown.
    
    Initializes database connections on startup and closes them on shutdown.
    """
    # Startup
    logger.info("🚀 Starting Tourism Platform API...")
    try:
        await init_db()
        logger.info("✅ PostgreSQL initialized")
    except Exception as e:
        logger.error(f"⚠️  PostgreSQL initialization failed: {e}")
    
    try:
        await init_mongo()
        logger.info("✅ MongoDB initialized")
    except Exception as e:
        logger.error(f"⚠️  MongoDB initialization failed: {e}")
    
    try:
        await init_redis()
        logger.info("✅ Redis initialized")
    except Exception as e:
        logger.error(f"⚠️  Redis initialization failed: {e}")
    
    logger.info("✅ All services initialized successfully!")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down Tourism Platform API...")
    await close_db()
    await close_mongo()
    await close_redis()
    logger.info("✅ All connections closed")


# Create FastAPI application
app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    description="Tourism Platform Management System - REST API for managing tourist spots, reviews, and accommodations",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting middleware
app.middleware("http")(rate_limit_middleware)

# Setup error handlers
setup_error_handlers(app)


@app.get("/")
async def root():
    """Root endpoint - API health check."""
    return {
        "message": "Tourism Platform API",
        "version": settings.API_VERSION,
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "api_version": settings.API_VERSION,
    }


# Register API routers
from src.api import spots, photos, ratings, auth, comments, accommodations, favorites, health

app.include_router(health.router, tags=["health"])
app.include_router(auth.router, prefix=settings.API_V1_PREFIX, tags=["auth"])
app.include_router(spots.router, prefix=settings.API_V1_PREFIX, tags=["spots"])
app.include_router(photos.router, prefix=settings.API_V1_PREFIX, tags=["photos"])
app.include_router(ratings.router, prefix=settings.API_V1_PREFIX, tags=["ratings"])
app.include_router(comments.router, prefix=settings.API_V1_PREFIX, tags=["comments"])
app.include_router(accommodations.router, prefix=settings.API_V1_PREFIX, tags=["accommodations"])
app.include_router(favorites.router, prefix=settings.API_V1_PREFIX, tags=["favorites"])
