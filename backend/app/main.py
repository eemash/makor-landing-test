"""FastAPI backend for CPG Idea Generator."""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import get_latest_ideas, get_todays_ideas, init_db
from app.email_sender import send_daily_email
from app.generator import generate_daily_batch, generate_idea

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()


def scheduled_generation() -> None:
    """Run by the scheduler — generates 1 coffee + 3 general CPG ideas, then emails."""
    try:
        logger.info("Running scheduled idea generation...")
        ideas = generate_daily_batch()
        logger.info("Scheduled generation complete — %d ideas created.", len(ideas))
        send_daily_email(ideas)
    except Exception as e:
        logger.error("Scheduled generation failed: %s", e)


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    scheduler.add_job(
        scheduled_generation, "cron", hour="8,20", minute=0, id="daily_generation"
    )
    scheduler.start()
    logger.info("Scheduler started — ideas generate at 8:00 and 20:00 UTC")
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
    """Manually trigger a new batch of ideas (1 coffee + 3 general CPG)."""
    ideas = generate_daily_batch()
    return {"status": "ok", "ideas": ideas}


@app.post("/api/ideas/generate/email")
def trigger_generation_with_email():
    """Generate ideas and send email summary."""
    ideas = generate_daily_batch()
    send_daily_email(ideas)
    return {"status": "ok", "ideas": ideas, "email_sent": True}


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
