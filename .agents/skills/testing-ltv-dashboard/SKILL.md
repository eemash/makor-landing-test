# Testing the LTV Dashboard

## Overview
Full-stack dashboard with a FastAPI backend (Python) and React + Vite + Recharts frontend.

## Local Setup

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
npx vite --port 5173
```

The Vite dev server proxies `/api` requests to `localhost:8000` (configured in `vite.config.js`).

Note: If port 5173 is taken, Vite auto-increments. Check terminal output for actual port.

## API Endpoints

| Endpoint | Returns |
|---|---|
| `GET /api/summary` | KPI metrics: total_customers, total_orders, total_revenue, avg_order_value, avg_orders_per_customer, estimated_ltv, repeat_customer_rate |
| `GET /api/orders` | Array of monthly {month, orders, revenue} |
| `GET /api/retention` | Array of cohort {cohort, customers, month_0..month_3} |
| `GET /api/ltv-distribution` | Array of {bucket, customers} |
| `GET /api/health` | {status: "ok"} |

## Data
Simulated data in `backend/app/data.py` with `random.seed(42)` and 200 customers. Data is deterministic but date-relative (uses `date.today()`), so exact values will shift over time.

## Testing Approach

1. **Verify API first**: `curl http://localhost:8000/api/summary` to confirm backend is serving data
2. **Verify proxy**: `curl http://localhost:<vite-port>/api/health` to confirm Vite proxy works
3. **UI testing**: Open dashboard in browser and verify:
   - 6 KPI metric cards render with non-zero values
   - 3 charts render (Orders bar chart, Revenue area chart, LTV histogram)
   - Cohort retention table renders with multiple rows, all Month 0 = 100%
   - Color coding on retention cells (green=high %, red/orange=low %)

## Key Files
- `backend/app/main.py` — FastAPI app with route definitions
- `backend/app/data.py` — Simulated data generation
- `frontend/src/App.jsx` — Main dashboard component, fetches all 4 API endpoints
- `frontend/src/components/` — MetricCard, OrdersChart, RevenueChart, LTVChart, RetentionTable
- `frontend/vite.config.js` — Dev server config with API proxy

## Devin Secrets Needed
None — uses simulated data. If Shopify integration is added, will need `SHOPIFY_API_KEY` and `SHOPIFY_STORE_URL`.

## Common Issues
- If Vite port conflicts, check terminal output for the actual port being used
- Backend must be running before frontend for API proxy to work
- `npm run dev` might silently exit in background mode; use `npx vite --port 5173` as a foreground process instead
