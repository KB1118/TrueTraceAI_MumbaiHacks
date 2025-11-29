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
    
    # Database - MySQL Configuration
    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DB_USER: str = "root"
    DB_PASSWORD: str = "AryanPRao_04"
    DB_NAME: str = "truetrace"
    DB_DRIVER: str = "pymysql"  # Options: pymysql, mysqlconnector
    
    def get_database_url(self) -> str:
        """Construct MySQL database URL from components."""
        driver = self.DB_DRIVER
        if driver == "mysqlconnector":
            driver_prefix = "mysql+mysqlconnector"
        else:
            driver_prefix = "mysql+pymysql"
        
        # URL encode password in case it contains special characters
        from urllib.parse import quote_plus
        encoded_password = quote_plus(self.DB_PASSWORD)
        
        return f"{driver_prefix}://{self.DB_USER}:{encoded_password}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}?charset=utf8mb4"
    
    @property
    def DATABASE_URL(self) -> str:
        """Property accessor for database URL."""
        return self.get_database_url()
    
    # Gemini API
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.0-flash-exp"

    # Ollama Cloud API (used for mock social data generation)
    OLLAMA_API_KEY: str = ""
    OLLAMA_API_BASE_URL: str = "https://api.ollama.com"
    OLLAMA_MODEL: str = "gpt-oss-120b"
    
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

