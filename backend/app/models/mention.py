"""
Mention model for storing social media mentions
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, JSON, ForeignKey, Float
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base


class Mention(Base):
    """Mention model for storing brand mentions from various platforms"""
    
    __tablename__ = "mentions"
    
    id = Column(Integer, primary_key=True, index=True)
    brand_id = Column(Integer, ForeignKey("brands.id"), nullable=False, index=True)
    
    # Content information
    platform = Column(String(100), nullable=False, index=True)
    platform_id = Column(String(255), unique=True, index=True)  # Original platform ID
    text = Column(Text, nullable=False)
    processed_text = Column(Text)
    
    # Author information
    author = Column(String(255))
    author_id = Column(String(255))
    
    # Metadata
    url = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    platform_created_at = Column(DateTime(timezone=True))
    
    # Metrics from platform
    metrics = Column(JSON, default={})  # likes, shares, comments, etc.
    
    # Analysis flags
    is_analyzed = Column(Boolean, default=False)
    analysis_version = Column(String(50))
    
    # Source information
    source = Column(String(100))  # api, scraper, etc.
    collection_method = Column(String(100))
    
    # Relationships
    brand = relationship("Brand", back_populates="mentions")
    sentiment_analysis = relationship("SentimentAnalysis", back_populates="mention", uselist=False)
    
    def __repr__(self):
        return f"<Mention(id={self.id}, platform='{self.platform}', brand_id={self.brand_id})>"
