"""
Configuration settings for MEDHASAKTHI backend
"""
import os
from typing import Optional, List
from pydantic import BaseSettings, validator


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "MEDHASAKTHI API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Security
    SECRET_KEY: str = "your-super-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Database
    DATABASE_URL: str = "postgresql://admin:password@localhost:5432/medhasakthi"
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    REDIS_PASSWORD: Optional[str] = None
    
    # Email
    SENDGRID_API_KEY: Optional[str] = None
    FROM_EMAIL: str = "noreply@medhasakthi.com"
    FROM_NAME: str = "MEDHASAKTHI"

    # Frontend URLs
    FRONTEND_URL: str = "http://localhost:3000"
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:3002",
        "https://medhasakthi.vercel.app"
    ]

    # Auto-scaling Configuration
    AUTO_SCALING_ENABLED: bool = False
    MIN_SERVERS: int = 1
    MAX_SERVERS: int = 10
    SCALE_UP_CPU_THRESHOLD: int = 70
    SCALE_DOWN_CPU_THRESHOLD: int = 30
    SCALE_UP_DURATION_MINUTES: int = 5
    SCALE_DOWN_DURATION_MINUTES: int = 15
    SCALING_COOLDOWN_MINUTES: int = 10

    # Health Check Configuration
    HEALTH_CHECK_INTERVAL_SECONDS: int = 30
    METRICS_COLLECTION_INTERVAL_SECONDS: int = 60
    SCALING_CHECK_INTERVAL_SECONDS: int = 300
    CLEANUP_INTERVAL_SECONDS: int = 3600

    # Service Discovery
    CONSUL_ENABLED: bool = False
    CONSUL_URL: str = "http://consul:8500"

    # Cloud Provider Configuration
    AWS_AUTO_SCALING_ENABLED: bool = False
    DO_AUTO_SCALING_ENABLED: bool = False
    
    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v):
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    # File Upload
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    UPLOAD_DIR: str = "uploads"
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # AI Services
    OPENAI_API_KEY: Optional[str] = None
    HUGGINGFACE_API_KEY: Optional[str] = None
    
    # Exam Security
    EXAM_SESSION_TIMEOUT_MINUTES: int = 180  # 3 hours
    MAX_CONCURRENT_SESSIONS: int = 1
    
    # Monitoring
    SENTRY_DSN: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Create global settings instance
settings = Settings()


# Database configuration
def get_database_url() -> str:
    """Get database URL for SQLAlchemy"""
    return settings.DATABASE_URL


def get_redis_url() -> str:
    """Get Redis URL"""
    return settings.REDIS_URL


# Security configuration
def get_secret_key() -> str:
    """Get secret key for JWT"""
    return settings.SECRET_KEY


# Email configuration
def get_email_config() -> dict:
    """Get email configuration"""
    return {
        "api_key": settings.SENDGRID_API_KEY,
        "from_email": settings.FROM_EMAIL,
        "from_name": settings.FROM_NAME
    }


# CORS configuration
def get_cors_origins() -> List[str]:
    """Get CORS origins"""
    return settings.BACKEND_CORS_ORIGINS


# Development helpers
def is_development() -> bool:
    """Check if running in development mode"""
    return settings.DEBUG


def is_production() -> bool:
    """Check if running in production mode"""
    return not settings.DEBUG
