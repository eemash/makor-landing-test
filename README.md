# Makor Coffee - LTV Dashboard

A simple dashboard tracking estimated Customer Lifetime Value (LTV), orders, and retention for Makor Coffee.

## Architecture

- **Backend**: FastAPI (Python) — serves REST API with simulated e-commerce data
- **Frontend**: React + Vite + Recharts — clean dashboard UI with charts

## Quick Start

### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173 to view the dashboard.

## API Endpoints

| Endpoint | Description |
|---|---|
| `GET /api/summary` | Top-level KPI metrics (LTV, total orders, revenue, etc.) |
| `GET /api/orders` | Monthly order counts and revenue over time |
| `GET /api/retention` | Cohort retention percentages |
| `GET /api/ltv-distribution` | Customer LTV bucket distribution |
| `GET /api/health` | Health check |

## Dashboard Features

- **KPI Cards**: Estimated LTV, Total Orders, Total Revenue, Avg Order Value, Repeat Customer Rate, Total Customers
- **Orders Over Time**: Monthly bar chart
- **Monthly Revenue**: Area chart showing revenue trend
- **LTV Distribution**: Histogram of customer lifetime values
- **Cohort Retention**: Color-coded table showing retention rates by cohort month

## Data

Currently uses simulated data (200 customers with realistic order patterns). Can be extended to pull real data from Shopify API.
