from pydantic_settings import BaseSettings
from typing import Optional, List
import os


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "AI Chatbot API"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Database
    DATABASE_URL: str = "sqlite:///./chatbot.db"  # SQLite for local development
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 30
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    REDIS_DB: int = 0
    
    # AI - Free alternatives
    AI_PROVIDER: str = "local"  # local, openai, huggingface
    OPENAI_API_KEY: str = ""  # Optional - only if using OpenAI
    HUGGINGFACE_API_KEY: str = ""  # Optional - for free models
    LOCAL_MODEL_PATH: str = "models/"  # Local model directory
    
    # Local AI Models (Free)
    LOCAL_EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    LOCAL_CHAT_MODEL: str = "microsoft/DialoGPT-medium"  # Free alternative
    
    # Translation - Free alternatives
    TRANSLATION_PROVIDER: str = "local"  # local, google, libre
    GOOGLE_TRANSLATE_API_KEY: str = ""  # Optional
    
    # File Storage - Local only
    STORAGE_TYPE: str = "local"  # local only for free setup
    LOCAL_STORAGE_PATH: str = "uploads/"
    
    # Email - Free alternatives
    EMAIL_PROVIDER: str = "local"  # local, sendgrid, smtp
    SMTP_HOST: str = "localhost"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    FROM_EMAIL: str = "noreply@chatbot.local"
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_PER_HOUR: int = 1000
    
    # CORS
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8080"]
    
    # Monitoring - Free alternatives
    LOG_LEVEL: str = "INFO"
    ENABLE_METRICS: bool = True
    
    # GDPR
    DATA_RETENTION_DAYS: int = 730  # 2 years
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings() 