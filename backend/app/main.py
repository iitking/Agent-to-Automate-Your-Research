from contextlib import asynccontextmanager
import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.core.config import settings
from app.core.logging import setup_logging, logger
from app.database.connection import init_db
from app.api.routes import health, research, config


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    logger.info("Initializing ResearchAgent backend application...")
    await init_db()
    logger.info("Database initialized successfully.")
    yield
    logger.info("Shutting down ResearchAgent backend application.")


app = FastAPI(
    title="Agent to Automate Your Research - API",
    description="Autonomous Multi-Agent AI Research Platform API",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(health.router)
app.include_router(config.router)
app.include_router(research.router)

# Mount exports directory for downloads
os.makedirs(settings.EXPORTS_DIR, exist_ok=True)
app.mount("/exports", StaticFiles(directory=settings.EXPORTS_DIR), name="exports")

# If frontend is built, serve index and static assets
frontend_dist = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"
if frontend_dist.exists():
    app.mount("/", StaticFiles(directory=str(frontend_dist), html=True), name="frontend")
