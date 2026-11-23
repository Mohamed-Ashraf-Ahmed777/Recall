from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import FileResponse

from app.api.routes.items import router as items_router
from app.api.routes.stats import router as stats_router
from app.api.routes.tags import router as tags_router
from app.core.config import settings
from app.database.init_db import init_db

UI_FILE = Path(__file__).resolve().parent / "static" / "index.html"


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title=settings.app_name, lifespan=lifespan)
app.include_router(items_router)
app.include_router(tags_router)
app.include_router(stats_router)


@app.get("/", include_in_schema=False)
def serve_ui():
    return FileResponse(UI_FILE)


@app.get("/health")
def health_check():
    return {"status": "ok", "app": settings.app_name}
