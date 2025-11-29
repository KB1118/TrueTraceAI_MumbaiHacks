"""
SQLAlchemy database models.
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, Boolean, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class User(Base):
    """User model for authentication."""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True)


class Crisis(Base):
    """Crisis model for tracking global events."""
    __tablename__ = "crises"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False)
    description = Column(Text)
    keywords = Column(JSON)  # List of keywords
    detected_at = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(String(50), default="active")  # active, resolved, archived
    crisis_metadata = Column(JSON)  # Additional crisis metadata
    
    # Relationships
    clusters = relationship("RumorCluster", back_populates="crisis", cascade="all, delete-orphan")


class RumorCluster(Base):
    """Rumor cluster model for grouping similar posts."""
    __tablename__ = "rumor_clusters"
    
    id = Column(Integer, primary_key=True, index=True)
    crisis_id = Column(Integer, ForeignKey("crises.id"), nullable=False)
    topic_label = Column(String(500))
    post_ids = Column(JSON)  # List of post IDs in this cluster
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    crisis = relationship("Crisis", back_populates="clusters")
    claims = relationship("Claim", back_populates="cluster", cascade="all, delete-orphan")


class Claim(Base):
    """Canonical claim model for fact-checking."""
    __tablename__ = "claims"
    
    id = Column(Integer, primary_key=True, index=True)
    cluster_id = Column(Integer, ForeignKey("rumor_clusters.id"), nullable=False)
    text = Column(Text, nullable=False)
    verdict = Column(String(50))  # True, False, Misleading, Uncertain
    confidence_score = Column(Float)  # 0.0 to 1.0
    volatility_score = Column(Float)  # 0.0 to 1.0
    reasoning = Column(Text)
    evidence_citations = Column(JSON)  # List of evidence URLs/sources
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    cluster = relationship("RumorCluster", back_populates="claims")
    cards = relationship("ResultCard", back_populates="claim", cascade="all, delete-orphan")


class ResultCard(Base):
    """Formatted result card for different audience types."""
    __tablename__ = "result_cards"
    
    id = Column(Integer, primary_key=True, index=True)
    claim_id = Column(Integer, ForeignKey("claims.id"), nullable=False)
    audience_type = Column(String(50))  # general, journalist, researcher
    title = Column(String(500))
    content = Column(Text)
    formatted_data = Column(JSON)  # Structured card data
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    claim = relationship("Claim", back_populates="cards")

