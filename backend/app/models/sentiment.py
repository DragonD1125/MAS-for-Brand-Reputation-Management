"""
Sentiment Analysis model for storing AI analysis results
"""

from sqlalchemy import Column, Integer, String, DateTime, Float, JSON, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base


class SentimentAnalysis(Base):
    """Sentiment analysis results for mentions"""
    
    __tablename__ = "sentiment_analyses"
    
    id = Column(Integer, primary_key=True, index=True)
    mention_id = Column(Integer, ForeignKey("mentions.id"), nullable=False, unique=True, index=True)
    
    # Sentiment scores
    overall_sentiment = Column(String(50), nullable=False, index=True)  # positive, negative, neutral
    positive_score = Column(Float, default=0.0)
    negative_score = Column(Float, default=0.0)
    neutral_score = Column(Float, default=0.0)
    confidence = Column(Float, default=0.0)
    
    # Emotion analysis
    dominant_emotion = Column(String(50))
    emotion_scores = Column(JSON, default={})
    
    # Crisis indicators
    has_crisis_indicators = Column(String(10), default="false")  # true/false as string
    crisis_keywords = Column(JSON, default=[])
    crisis_severity = Column(String(50))  # low, medium, high, critical
    risk_level = Column(String(50))
    
    # Analysis metadata
    model_version = Column(String(100))
    analysis_method = Column(String(100))
    processing_time = Column(Float)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    mention = relationship("Mention", back_populates="sentiment_analysis")
    
    def __repr__(self):
        return f"<SentimentAnalysis(id={self.id}, mention_id={self.mention_id}, sentiment='{self.overall_sentiment}')>"
