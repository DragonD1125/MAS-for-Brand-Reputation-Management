"""
Core configuration settings for the Brand Reputation Management System
"""

from pydantic_settings import BaseSettings
from typing import List, Optional
import os
from datetime import datetime


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "Brand Reputation Management System"
    VERSION: str = "1.0.0"
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost/brand_reputation"
    DATABASE_URL_ASYNC: str = "postgresql+asyncpg://user:password@localhost/brand_reputation"
    
    # Redis (for Celery and caching)
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # CORS
    ALLOWED_HOSTS: List[str] = ["*"]
    
    # LLM Configuration
    GEMINI_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    LLM_MODEL_NAME: str = "gemini-2.0-flash"  # Updated to available model
    LLM_TEMPERATURE: float = 0.1
    LLM_MAX_TOKENS: int = 2048
    
    # Autonomous System Configuration
    AUTONOMOUS_CHECK_INTERVAL: int = 300  # 5 minutes between autonomous cycles
    AUTONOMOUS_ENABLED: bool = True
    AUTO_RESPONSE_RISK_THRESHOLD: float = 0.3  # Below this, auto-approve responses
    HUMAN_REVIEW_RISK_THRESHOLD: float = 0.7  # Above this, require human approval
    
    # Social Media APIs
    TWITTER_API_KEY: Optional[str] = None
    TWITTER_API_SECRET: Optional[str] = None
    TWITTER_ACCESS_TOKEN: Optional[str] = None
    TWITTER_ACCESS_TOKEN_SECRET: Optional[str] = None
    TWITTER_BEARER_TOKEN: Optional[str] = None
    
    FACEBOOK_APP_ID: Optional[str] = None
    FACEBOOK_ACCESS_TOKEN: Optional[str] = None
    
    # Reddit API
    REDDIT_CLIENT_ID: Optional[str] = None
    REDDIT_CLIENT_SECRET: Optional[str] = None
    REDDIT_USER_AGENT: str = "BrandReputationBot/1.0 by YourUsername"
    
    # Instagram API
    INSTAGRAM_ACCESS_TOKEN: Optional[str] = None
    INSTAGRAM_APP_SECRET: Optional[str] = None
    
    # News API
    NEWS_API_KEY: Optional[str] = None
    
    # Additional API Keys
    NEWSAPI_KEY: Optional[str] = None
    
    # Application Settings
    RISK_THRESHOLD_HIGH: float = 0.7
    RISK_THRESHOLD_MEDIUM: float = 0.3
    
    # Security
    JWT_SECRET_KEY: str = "your-jwt-secret-key-change-in-production"
    
    # Data Collection Settings
    DEFAULT_COLLECTION_INTERVAL: int = 3600  # 1 hour in seconds
    MAX_MENTIONS_PER_COLLECTION: int = 100
    MENTION_RETENTION_DAYS: int = 90
    FACEBOOK_APP_SECRET: Optional[str] = None
    FACEBOOK_ACCESS_TOKEN: Optional[str] = None
    
    INSTAGRAM_USERNAME: Optional[str] = None
    INSTAGRAM_PASSWORD: Optional[str] = None
    
    GOOGLE_API_KEY: Optional[str] = None
    
    # Monitoring intervals (in minutes)
    MONITORING_INTERVAL: int = 15
    CRISIS_CHECK_INTERVAL: int = 5
    INSIGHT_GENERATION_INTERVAL: int = 60
    
    # Alert thresholds
    NEGATIVE_SENTIMENT_THRESHOLD: float = 0.7
    CRISIS_MENTION_THRESHOLD: int = 10
    VOLUME_SPIKE_MULTIPLIER: float = 3.0
    
    # AI/ML Model settings
    SENTIMENT_MODEL: str = "cardiffnlp/twitter-roberta-base-sentiment-latest"
    EMOTION_MODEL: str = "j-hartmann/emotion-english-distilroberta-base"
    ENABLE_GPU: bool = False
    
    # Notification settings
    EMAIL_ENABLED: bool = False
    SMTP_SERVER: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USERNAME: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    
    SLACK_WEBHOOK_URL: Optional[str] = None
    DISCORD_WEBHOOK_URL: Optional[str] = None
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} - {message}"
    
    class Config:
        # Look for .env in multiple locations
        env_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env")
        env_file_encoding = 'utf-8'
        case_sensitive = True
    
    @staticmethod
    def get_current_timestamp() -> str:
        """Get current timestamp as ISO string"""
        return datetime.utcnow().isoformat() + "Z"


# Global settings instance
settings = Settings()


# Development settings override
if settings.DEBUG:
    settings.DATABASE_URL = "sqlite:///./brand_reputation.db"
    settings.DATABASE_URL_ASYNC = "sqlite+aiosqlite:///./brand_reputation.db"
