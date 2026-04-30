# CPG Idea Generator

AI-powered CPG (Consumer Packaged Goods) brand idea generator that analyzes Google Trends to suggest new brand opportunities — one coffee-related, one general CPG — delivered twice daily.

## Architecture

- **Backend**: FastAPI + pytrends + OpenAI (gpt-4o-mini)
- **Frontend**: React + Vite
- **Database**: SQLite (stores generated ideas)
- **Scheduler**: APScheduler (generates ideas at 8:00 and 20:00 UTC)

## Setup

### Backend

```bash
cd backend
pip install -r requirements.txt
export OPENAI_API_KEY=your_key_here
uvicorn app.main:app --reload --port 8001
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5180 to view the dashboard.

## How It Works

1. **Trend Analysis**: Samples random keywords from curated CPG category lists and queries Google Trends for interest data, rising queries, and related topics
2. **AI Generation**: Feeds trend data to GPT-4o-mini with a specialized prompt to generate a brand concept including name, tagline, target audience, and detailed reasoning
3. **Scheduling**: Runs automatically at 8:00 AM and 8:00 PM UTC
4. **Manual Trigger**: Click "Generate New Ideas Now" on the dashboard for on-demand ideas

## API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/api/ideas/today` | GET | Get today's generated ideas |
| `/api/ideas/history` | GET | Get the most recent 20 ideas |
| `/api/ideas/generate` | POST | Manually trigger a new pair (coffee + general) |
| `/api/ideas/generate/{category}` | POST | Generate a single idea (coffee or general_cpg) |
| `/api/health` | GET | Health check |
