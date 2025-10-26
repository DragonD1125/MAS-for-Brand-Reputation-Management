# Brand Reputation Management System

A streamlined NewsAPI-powered workflow for assessing brand reputation within minutes. The system collects recent
articles for any brand, performs lightweight sentiment scoring, and presents actionable insights in a focused React
dashboard. Social data connectors (Twitter/Reddit/Instagram) remain part of the codebase but are disabled by default so
you can run the project end-to-end without additional credentials.

## 🌟 Highlights

- **On-demand NewsAPI ingestion** – Provide a brand name, fetch up to 25 recent articles, and analyze coverage trends.
- **Lightweight sentiment heuristics** – Classify each article as positive, neutral, or negative without heavyweight ML
   dependencies.
- **Concise insight engine** – Summaries include sentiment counts, trending keywords, and recommended follow-up steps.
- **Modern React dashboard** – Single-page UI with a guided form, sentiment visualization, insights panels, and a clean
   article list.
- **Extensible multi-agent backend** – LangChain-based agents and social connectors are ready for future expansion but
   safely toggled off in this configuration.

## ⚙️ Prerequisites

- Python 3.11+
- Node.js 18+
- A NewsAPI key (free tier works great): https://newsapi.org/

All other integrations are optional. By default the backend runs against SQLite and only the NewsAPI-powered pipeline is
active.

## 🚀 Quick Start

### 1. Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate  # or `source venv/bin/activate` on macOS/Linux
pip install -r requirements.txt

# copy environment template and set keys
cp .env.example .env
# edit .env -> set NEWSAPI_KEY and GEMINI_API_KEY (if LLM orchestration needed)

uvicorn main:app --reload
```

The API runs at `http://localhost:8000`.

### 2. Frontend

```bash
cd frontend
npm install
npm start
```

The React app is available at `http://localhost:3000` and communicates with the backend’s `/api/v1` routes.

## 🔐 Configuration Notes

- `backend/.env.example` documents all available environment variables. For the News-only flow you only need:
   - `NEWSAPI_KEY` – required to fetch live articles.
   - `GEMINI_API_KEY` – optional unless you re-enable LangChain planning.
- Social platform connectors are disabled by default using the new feature flags:
   - `ENABLE_TWITTER=false`
   - `ENABLE_REDDIT=false`
   - `ENABLE_INSTAGRAM=false`
   When you are ready to supply credentials, flip the flag to `true` and install the relevant Python packages.

## 🧠 How the News Workflow Operates

1. The frontend collects a brand name, article count (3–25), and timeframe (1–30 days).
2. `POST /api/v1/analytics/brand-analysis` triggers the backend service to:
    - Query NewsAPI through `MultiPlatformDataCollector` (news tool only).
    - Run keyword-based sentiment heuristics for each article.
    - Aggregate counts, trending keywords, and recommendations.
3. The response powers the dashboard’s sentiment chart, insights, and article cards.

The sentiment engine intentionally avoids heavy dependencies so the workflow stays fast on modest hardware. When you
need deeper NLP, plug in the advanced models under `app/tools/analysis_tools.py`.

## 📡 API Reference (Active Routes)

| Method | Endpoint                              | Description                                   |
|--------|----------------------------------------|-----------------------------------------------|
| GET    | `/`                                    | Backend status and agent metadata.            |
| GET    | `/health`                              | Basic health probe.                           |
| GET    | `/api/v1/analytics/`                   | Simple status for the analytics module.       |
| POST   | `/api/v1/analytics/brand-analysis`     | Run NewsAPI-driven sentiment analysis.        |

Other routers (brands, monitoring, alerts) remain in place for future agent work but currently return placeholder
responses.

### Sample Request

```bash
curl -X POST http://localhost:8000/api/v1/analytics/brand-analysis \
   -H "Content-Type: application/json" \
   -d '{
            "brand_name": "OpenAI",
            "max_articles": 10,
            "days_back": 7
         }'
```

### Sample Response (abridged)

```json
{
   "brand_name": "OpenAI",
   "timeframe_days": 7,
   "fetched_at": "2024-06-01T14:22:05.123456",
   "summary": {
      "total_articles": 10,
      "positive": 6,
      "neutral": 3,
      "negative": 1,
      "average_sentiment_score": 0.28,
      "top_keywords": ["ai", "chatbot", "launch", "startup"],
      "insights": ["Positive coverage outweighs negative mentions for OpenAI."],
      "recommendations": ["Continue monitoring – sentiment distribution remains balanced."]
   },
   "articles": [
      {
         "title": "OpenAI announces new product",
         "source": "Example News",
         "sentiment": "positive",
         "sentiment_score": 0.5,
         "keywords": ["launch", "ai", "product"],
         "url": "https://news.example.com/openai-launch"
      }
   ]
}
```

## 🖥️ Frontend Experience

- Launch the site and enter the brand you wish to monitor.
- Choose how many articles to fetch (default 10) and the timeframe in days.
- Review the sentiment pie chart, insight/recommendation panes, and the article list with quick actions.
- Keywords appear as chips for easy scanning; click “Read article” to open the source in a new tab.

Legacy navigation items (Mentions, Analytics, HITL, System Health) now display short informational stubs explaining that
social integrations are offline in this mode.

## 🔧 Extending the Platform

- **Re-enable social connectors** by installing `tweepy`, `praw`, or other platform SDKs and turning on the corresponding
   `ENABLE_*` flags.
- **Swap in advanced sentiment** by invoking the transformer-based pipelines in `app/tools/analysis_tools.py`.
- **Expand API surface** by wiring additional FastAPI endpoints under `app/api/endpoints/` and exposing them through the
   React client.

## 🧪 Testing & Quality

```bash
# Backend tests
cd backend
pytest -q

# Formatting & linting suggestions
black app/
flake8 app/
```

## 🐞 Troubleshooting

- **NewsAPI returns 401** – verify `NEWSAPI_KEY` and make sure it is not rate-limited.
- **No articles found** – increase `days_back` or add alternate spellings for the brand name.
- **Frontend cannot reach backend** – confirm the backend runs on `http://localhost:8000` and CORS settings include your
   frontend origin.
- **Optional agents crash during import** – ensure the related packages are installed or keep the `ENABLE_*` flags set to
   `false`.

Enjoy exploring your brand coverage! 🎯
docker-compose up -d
```

### Production Environment Variables
See `.env.example` for all required environment variables for production deployment.

## 📈 Monitoring & Observability

- **Agent Health Monitoring** - Real-time agent status and performance
- **System Metrics** - Message processing, error rates, response times
- **Alert Management** - Crisis detection and notification tracking
- **Performance Analytics** - System throughput and efficiency metrics

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔮 Roadmap

- [ ] Enhanced AI models for sentiment analysis
- [ ] Real-time dashboard with React frontend
- [ ] Advanced analytics and reporting
- [ ] Integration with more social platforms
- [ ] Mobile application
- [ ] Enterprise features and SSO
---

