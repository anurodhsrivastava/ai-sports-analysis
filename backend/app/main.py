"""
FastAPI Application - Sports Coach AI

Performance features:
- Model preload + warmup at startup -- Fix #5
- Cache-Control headers on /results -- Fix #7
- Periodic file cleanup scheduler -- Fix #10
- GZip compression for JSON responses
- Database initialization at startup
"""

import asyncio
import logging
import os
import time
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.staticfiles import StaticFiles

from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from .config import settings
from .routers.analyze import limiter, router as analyze_router
from .routers.auth import router as auth_router
from .routers.sports import router as sports_router
from .routers.payments import router as payments_router
from .routers.admin import router as admin_router
from .routers.videos import router as videos_router
from .routers.progress import router as progress_router

# Import sports to trigger registration
from . import sports as _sports  # noqa: F401

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Fix #10: Periodic cleanup of old uploads, results, and task store files
# ---------------------------------------------------------------------------

def _cleanup_old_files(directory: Path, max_age_hours: int) -> int:
    """Delete files older than max_age_hours. Returns count removed."""
    if not directory.exists():
        return 0
    now = time.time()
    removed = 0
    for f in directory.iterdir():
        if f.is_file():
            try:
                if now - f.stat().st_mtime > max_age_hours * 3600:
                    f.unlink(missing_ok=True)
                    removed += 1
            except Exception:
                pass
    return removed


async def _periodic_cleanup() -> None:
    """Background loop that cleans up old files every hour."""
    from .tasks.analysis_tasks import task_store

    while True:
        await asyncio.sleep(3600)
        max_age = settings.cleanup_max_age_hours
        u = _cleanup_old_files(settings.upload_dir, max_age)
        r = _cleanup_old_files(settings.results_dir, max_age)
        t = task_store.cleanup(max_age)
        if u or r or t:
            logger.info("Cleanup: removed %d uploads, %d results, %d task records", u, r, t)


# ---------------------------------------------------------------------------
# Lifespan -- startup/shutdown
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    from .tasks.analysis_tasks import preload_models, set_event_loop
    from .database import init_db

    # Validate secrets in production
    if settings.environment == "production" and settings.jwt_secret == "change-me-in-production":
        raise RuntimeError("JWT_SECRET must be changed from default value in production")

    # Initialize database tables
    init_db()
    logger.info("Database initialized")

    set_event_loop(asyncio.get_event_loop())
    preload_models()

    cleanup_task = asyncio.create_task(_periodic_cleanup())

    yield

    cleanup_task.cancel()
    try:
        await cleanup_task
    except asyncio.CancelledError:
        pass


app = FastAPI(
    title="Sports Coach AI",
    description="Multi-sport pose estimation and biomechanical analysis",
    version="1.0.0",
    lifespan=lifespan,
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# GZip compression for JSON responses
app.add_middleware(GZipMiddleware, minimum_size=1000)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)


# ---------------------------------------------------------------------------
# Request logging middleware
# ---------------------------------------------------------------------------

@app.middleware("http")
async def request_logging_middleware(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    duration_ms = (time.time() - start) * 1000
    if not request.url.path.startswith("/results/"):
        logger.info(
            "%s %s %d %.0fms",
            request.method, request.url.path, response.status_code, duration_ms,
        )
    return response


# ---------------------------------------------------------------------------
# Security headers middleware
# ---------------------------------------------------------------------------

@app.middleware("http")
async def security_headers_middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    if os.environ.get("ENVIRONMENT", "development") == "production":
        response.headers["Strict-Transport-Security"] = (
            "max-age=63072000; includeSubDomains"
        )
    return response


# ---------------------------------------------------------------------------
# Fix #7: Cache-Control headers for static result videos
# ---------------------------------------------------------------------------

@app.middleware("http")
async def cache_control_middleware(request: Request, call_next):
    response = await call_next(request)
    if request.url.path.startswith("/results/"):
        response.headers["Cache-Control"] = "public, max-age=86400, immutable"
    return response


# Static file serving for annotated result videos
results_dir = settings.results_dir
results_dir.mkdir(parents=True, exist_ok=True)
app.mount("/results", StaticFiles(directory=str(results_dir)), name="results")

# Routers
app.include_router(analyze_router)
app.include_router(auth_router)
app.include_router(sports_router)
app.include_router(payments_router)
app.include_router(admin_router)
app.include_router(videos_router)
app.include_router(progress_router)


@app.get("/api/health")
async def health_check():
    from .sports.registry import SportRegistry

    return {
        "status": "ok",
        "environment": settings.environment,
        "sports": [s["sport_id"] for s in SportRegistry.list_sports()],
        "upload_dir_writable": os.access(str(settings.upload_dir), os.W_OK),
        "results_dir_writable": os.access(str(settings.results_dir), os.W_OK),
    }
