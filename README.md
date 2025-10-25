# Brand Reputation Management System

A comprehensive Multi-Agent AI system for real-time brand reputation monitoring and analysis across social media platforms and web sources.

## 🚀 Features

### Core Capabilities
- **Real-time Social Media Monitoring** - Track mentions across Twitter, Facebook, Instagram, Reddit, and news sources
- **AI-Powered Sentiment Analysis** - Advanced NLP models for accurate sentiment detection and emotion analysis
- **Intelligent Alert System** - Crisis detection with automated notifications and escalation workflows
- **Multi-Agent Architecture** - Scalable, distributed system with specialized AI agents
- **Competitive Intelligence** - Monitor competitors and industry trends
- **Actionable Insights** - AI-generated recommendations and strategic analysis

### Technical Architecture
- **Backend**: Python 3.11+ with FastAPI
- **Frontend**: React.js with TypeScript (planned)
- **Database**: PostgreSQL with SQLAlchemy ORM
- **AI/ML**: Transformers, scikit-learn, NLTK, spaCy
- **Multi-Agent System**: Custom asynchronous agent framework
- **Deployment**: Docker containers with cloud deployment ready

## 🏗️ Multi-Agent System

### Agent Types
1. **Data Collection Agent** - Monitors and collects data from various platforms
2. **Sentiment Analysis Agent** - Processes content for sentiment and emotion analysis
3. **Alert Management Agent** - Detects crises and manages notifications
4. **Insight Generation Agent** - Creates actionable insights and recommendations
5. **Agent Orchestrator** - Coordinates all agent activities

### Agent Communication
- Asynchronous message passing between agents
- Event-driven architecture with correlation tracking
- Fault-tolerant with automatic recovery
- Real-time monitoring and health checks

## 🛠️ Setup & Installation

### Prerequisites
- Python 3.11 or higher
- PostgreSQL 13+ (or SQLite for development)
- Redis (for caching and agent coordination)
- Node.js 18+ (for frontend)

### Backend Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd "MAS for Brand Reputation Management"
   ```

2. **Create virtual environment**
   ```bash
   cd backend
   python -m venv venv
   # Windows
   venv\\Scripts\\activate
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Configuration**
   Create a `.env` file in the backend directory:
   ```env
   # Database
   DATABASE_URL=postgresql://user:password@localhost/brand_reputation
   
   # Redis
   REDIS_URL=redis://localhost:6379/0
   
   # Social Media APIs (optional for development)
   TWITTER_BEARER_TOKEN=your_twitter_bearer_token
   FACEBOOK_ACCESS_TOKEN=your_facebook_token
   
   # Security
   SECRET_KEY=your-secret-key-here
   
   # Development
   DEBUG=True
   ```

5. **Initialize Database**
   ```bash
   # For development, SQLite is used by default
   python main.py
   ```

6. **Start the application**
   ```bash
   python main.py
   ```

The API will be available at `http://localhost:8000`
- API Documentation: `http://localhost:8000/docs`
- Alternative docs: `http://localhost:8000/redoc`

## 📊 API Endpoints

### System Status
- `GET /` - System overview and status
- `GET /health` - Health check endpoint

### Monitoring
- `POST /api/v1/monitoring/start` - Start brand monitoring
- `GET /api/v1/monitoring/status` - Get monitoring status
- `GET /api/v1/monitoring/agents` - Agent status information
- `GET /api/v1/monitoring/metrics` - System metrics

### Brands (Planned)
- `GET /api/v1/brands/` - List all brands
- `POST /api/v1/brands/` - Create new brand
- `GET /api/v1/brands/{id}` - Get brand details

### Alerts (Planned)
- `GET /api/v1/alerts/` - List active alerts
- `POST /api/v1/alerts/{id}/acknowledge` - Acknowledge alert
- `POST /api/v1/alerts/{id}/resolve` - Resolve alert

## 🤖 Agent System Usage

### Starting Monitoring
```python
# Example API call to start monitoring
curl -X POST "http://localhost:8000/api/v1/monitoring/start" \\
-H "Content-Type: application/json" \\
-d '{
  "brand_id": "my_brand",
  "platforms": ["twitter", "facebook", "instagram"],
  "keywords": ["my brand", "brand name", "product name"],
  "timeframe": "1h"
}'
```

### System Status
```python
# Check system health
curl "http://localhost:8000/api/v1/monitoring/health"
```

## 🔧 Development

### Project Structure
```
backend/
├── main.py                    # FastAPI application entry point
├── requirements.txt           # Python dependencies
├── app/
│   ├── __init__.py
│   ├── agents/               # Multi-Agent System
│   │   ├── base_agent.py    # Base agent class
│   │   ├── data_collection_agent.py
│   │   ├── sentiment_analysis_agent.py
│   │   ├── alert_management_agent.py
│   │   └── orchestrator.py  # Agent coordinator
│   ├── api/                 # FastAPI routes
│   │   ├── v1.py           # API version 1 router
│   │   └── endpoints/       # API endpoints
│   ├── core/               # Core configuration
│   │   ├── config.py       # Settings
│   │   └── database.py     # Database setup
│   ├── models/             # Database models
│   │   ├── brand.py
│   │   ├── mention.py
│   │   ├── sentiment.py
│   │   ├── alert.py
│   │   └── user.py
│   └── services/           # Business logic services
├── tests/                   # Test files
├── docs/                   # Documentation
└── config/                 # Configuration files
```

### Running Tests
```bash
cd backend
pytest tests/ -v
```

### Code Quality
```bash
# Format code
black app/

# Lint code
flake8 app/

# Type checking
mypy app/
```

## 🚀 Deployment

### Docker Deployment (Planned)
```bash
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

## 📞 Support

For questions and support, please open an issue in the GitHub repository.

---

**Built with ❤️ using Multi-Agent AI Architecture**
