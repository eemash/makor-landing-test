"""FastAPI backend for CPG Idea Generator."""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import get_latest_ideas, get_todays_ideas, init_db
from app.generator import generate_daily_pair, generate_idea

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()


def scheduled_generation() -> None:
    """Run by the scheduler twice daily."""
    try:
        logger.info("Running scheduled idea generation...")
        generate_daily_pair()
        logger.info("Scheduled generation complete.")
    except Exception as e:
        logger.error("Scheduled generation failed: %s", e)


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    scheduler.add_job(scheduled_generation, "cron", hour="8,20", minute=0, id="morning")
    scheduler.start()
    logger.info("Scheduler started — ideas will generate at 8:00 and 20:00 UTC")
    yield
    scheduler.shutdown()


app = FastAPI(title="CPG Idea Generator", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/ideas/today")
def today_ideas():
    """Get today's generated ideas."""
    return get_todays_ideas()


@app.get("/api/ideas/history")
def idea_history():
    """Get the most recent 20 ideas."""
    return get_latest_ideas(20)


@app.post("/api/ideas/generate")
def trigger_generation():
    """Manually trigger a new pair of ideas (coffee + general)."""
    ideas = generate_daily_pair()
    return {"status": "ok", "ideas": ideas}


@app.post("/api/ideas/generate/{category}")
def trigger_single(category: str):
    """Manually trigger a single idea generation.

    category: 'coffee' or 'general_cpg'
    """
    if category not in ("coffee", "general_cpg"):
        return {"error": "Category must be 'coffee' or 'general_cpg'"}
    idea = generate_idea(category)
    return {"status": "ok", "idea": idea}


@app.get("/api/health")
def health():
    return {"status": "ok"}
