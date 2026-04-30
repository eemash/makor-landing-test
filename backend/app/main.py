"""FastAPI backend for Makor Coffee LTV Dashboard."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.data import (
    get_ltv_distribution,
    get_orders_over_time,
    get_retention_cohorts,
    get_summary_metrics,
)

app = FastAPI(title="Makor LTV Dashboard API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/summary")
def summary():
    """Top-level KPI metrics."""
    return get_summary_metrics()


@app.get("/api/orders")
def orders():
    """Monthly order counts and revenue."""
    return get_orders_over_time()


@app.get("/api/retention")
def retention():
    """Cohort retention data."""
    return get_retention_cohorts()


@app.get("/api/ltv-distribution")
def ltv_distribution():
    """LTV bucket distribution."""
    return get_ltv_distribution()


@app.get("/api/health")
def health():
    return {"status": "ok"}
