"""
Brand model for database
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base


class Brand(Base):
    """Brand model for storing brand information"""
    
    __tablename__ = "brands"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    
    # Brand configuration
    keywords = Column(JSON, default=[])  # Keywords to monitor
    platforms = Column(JSON, default=[])  # Platforms to monitor
    
    # Monitoring settings
    monitoring_enabled = Column(Boolean, default=True)
    monitoring_interval = Column(Integer, default=15)  # Minutes
    
    # Alert settings
    alert_settings = Column(JSON, default={})
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(String(255))
    
    # Relationships
    mentions = relationship("Mention", back_populates="brand")
    alerts = relationship("Alert", back_populates="brand")
    
    def __repr__(self):
        return f"<Brand(id={self.id}, name='{self.name}')>"
