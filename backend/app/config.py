"""
Configuration management for TrueTrace AI backend.
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # API Configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "TrueTrace AI"
    VERSION: str = "1.0.0"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Database
    DATABASE_URL: str = "sqlite:///./truetrace.db"
    
    # Gemini API
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.0-flash-exp"
    
    # Vector Store (using ChromaDB for simplicity)
    VECTOR_STORE_PATH: str = "./chroma_db"
    
    # Social Media APIs (placeholder keys)
    TWITTER_BEARER_TOKEN: Optional[str] = None
    REDDIT_CLIENT_ID: Optional[str] = None
    REDDIT_CLIENT_SECRET: Optional[str] = None
    REDDIT_USER_AGENT: str = "TrueTraceAI/1.0"
    
    # News API
    NEWS_API_KEY: Optional[str] = None
    
    # Pipeline Configuration
    CRISIS_DETECTION_INTERVAL_MINUTES: int = 60
    MAX_POSTS_PER_KEYWORD: int = 100
    CLUSTERING_MIN_SIZE: int = 3
    EVIDENCE_RETRIEVAL_LIMIT: int = 10
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

