"""
FastAPI Application - Sports Coach AI

Performance features:
- Model preload + warmup at startup -- Fix #5
- Cache-Control headers on /results -- Fix #7
- Periodic file cleanup scheduler -- Fix #10
"""

import asyncio
import time
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .config import settings
from .routers.analyze import router as analyze_router
from .routers.sports import router as sports_router

# Import sports to trigger registration
from . import sports as _sports  # noqa: F401


# ---------------------------------------------------------------------------
# Fix #10: Periodic cleanup of old uploads, results, and task store files
# ---------------------------------------------------------------------------

def _cleanup_old_files(directory: Path, max_age_hours: int) -> int:
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
    from .tasks.analysis_tasks import task_store

    while True:
        await asyncio.sleep(3600)
        max_age = settings.cleanup_max_age_hours
        u = _cleanup_old_files(settings.upload_dir, max_age)
        r = _cleanup_old_files(settings.results_dir, max_age)
        t = task_store.cleanup(max_age)
        if u or r or t:
            print(f"Cleanup: removed {u} uploads, {r} results, {t} task records")


# ---------------------------------------------------------------------------
# Lifespan
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    from .tasks.analysis_tasks import preload_models, set_event_loop

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

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)


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
app.include_router(sports_router)


@app.get("/api/health")
async def health_check():
    from .sports.registry import SportRegistry

    return {
        "status": "ok",
        "sports": [s["sport_id"] for s in SportRegistry.list_sports()],
    }
