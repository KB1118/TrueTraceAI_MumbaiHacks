"""
Configuration management for TrueTrace AI backend.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
from urllib.parse import quote_plus

class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # --- Pydantic V2 Configuration ---
    # extra='ignore' prevents crashes if .env has variables we don't use
    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding='utf-8',
        case_sensitive=False,
        extra='ignore' 
    )

    # API Configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "TrueTrace AI"
    VERSION: str = "1.0.0"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Database - MySQL Configuration
    DB_HOST: str = "127.0.0.1"
    DB_PORT: int = 3306
    DB_USER: str = "root"
    DB_PASSWORD: str = "ashbhairockz69"
    DB_NAME: str = "truetrace"
    DB_DRIVER: str = "pymysql"
    
    def get_database_url(self) -> str:
        """Construct MySQL database URL from components."""
        driver_prefix = "mysql+mysqlconnector" if self.DB_DRIVER == "mysqlconnector" else "mysql+pymysql"
        encoded_password = quote_plus(self.DB_PASSWORD)
        return f"{driver_prefix}://{self.DB_USER}:{encoded_password}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}?charset=utf8mb4"
    
    @property
    def DATABASE_URL(self) -> str:
        """Property accessor for database URL."""
        return self.get_database_url()
    
    # Gemini + data extraction
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.0-flash-exp"
    SENTENCE_TRANSFORMER_MODEL: str = "all-MiniLM-L6-v2"
    MAX_PIPELINE_CLUSTERS: int = 10
    CRISIS_KEYWORD_QUERY: str = "What major crises are happening right now worldwide?"
    SCRAPE_KEYWORD_LIMIT: int = 5
    REDDIT_SUBREDDIT_LIMIT: int = 12
    REDDIT_POST_LIMIT: int = 5
    TELEGRAM_CHANNEL_LIMIT: int = 20
    TELEGRAM_POST_LIMIT: int = 50
    CLAIMS_PER_CLUSTER: int = 5

    # Ollama Cloud API
    OLLAMA_API_KEY: str = ""
    OLLAMA_API_BASE_URL: str = "https://api.ollama.com"
    OLLAMA_MODEL: str = "gpt-oss-20b-cloud"
    
    # Vector Store
    VECTOR_STORE_PATH: str = "./chroma_db"
    
    # Social Media APIs
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

settings = Settings()