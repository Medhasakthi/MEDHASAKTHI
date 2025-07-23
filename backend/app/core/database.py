"""
Database configuration and session management
"""
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
import redis
from typing import Generator

from app.core.config import settings

# SQLAlchemy setup
engine = create_engine(
    settings.DATABASE_URL,
    pool_size=settings.DATABASE_POOL_SIZE,
    max_overflow=settings.DATABASE_MAX_OVERFLOW,
    pool_pre_ping=True,
    echo=settings.DEBUG  # Log SQL queries in debug mode
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all models
Base = declarative_base()

# Naming convention for constraints
convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

Base.metadata = MetaData(naming_convention=convention)

# Redis setup
redis_client = redis.Redis.from_url(
    settings.REDIS_URL,
    password=settings.REDIS_PASSWORD,
    decode_responses=True
)


def get_db() -> Generator[Session, None, None]:
    """
    Database dependency for FastAPI
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_redis() -> redis.Redis:
    """
    Redis dependency for FastAPI
    """
    return redis_client


def create_tables():
    """
    Create all database tables
    """
    Base.metadata.create_all(bind=engine)


def drop_tables():
    """
    Drop all database tables (use with caution!)
    """
    Base.metadata.drop_all(bind=engine)


# Database utilities
class DatabaseManager:
    """Database management utilities"""
    
    @staticmethod
    def check_connection() -> bool:
        """Check if database connection is working"""
        try:
            with engine.connect() as conn:
                conn.execute("SELECT 1")
            return True
        except Exception:
            return False
    
    @staticmethod
    def check_redis_connection() -> bool:
        """Check if Redis connection is working"""
        try:
            redis_client.ping()
            return True
        except Exception:
            return False
    
    @staticmethod
    def get_db_info() -> dict:
        """Get database information"""
        try:
            with engine.connect() as conn:
                result = conn.execute("SELECT version()")
                version = result.fetchone()[0]
                return {
                    "status": "connected",
                    "version": version,
                    "url": settings.DATABASE_URL.split("@")[1] if "@" in settings.DATABASE_URL else "hidden"
                }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    @staticmethod
    def get_redis_info() -> dict:
        """Get Redis information"""
        try:
            info = redis_client.info()
            return {
                "status": "connected",
                "version": info.get("redis_version"),
                "memory_usage": info.get("used_memory_human"),
                "connected_clients": info.get("connected_clients")
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }


# Session management for authentication
class SessionManager:
    """Manage user sessions in Redis"""
    
    def __init__(self):
        self.redis = redis_client
        self.session_prefix = "session:"
        self.user_sessions_prefix = "user_sessions:"
    
    def create_session(self, user_id: str, session_token: str, device_info: dict = None) -> bool:
        """Create a new user session"""
        try:
            session_key = f"{self.session_prefix}{session_token}"
            user_sessions_key = f"{self.user_sessions_prefix}{user_id}"
            
            session_data = {
                "user_id": user_id,
                "created_at": str(datetime.utcnow()),
                "device_info": str(device_info) if device_info else "",
                "is_active": "true"
            }
            
            # Store session data
            self.redis.hset(session_key, mapping=session_data)
            self.redis.expire(session_key, settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600)
            
            # Add to user's session list
            self.redis.sadd(user_sessions_key, session_token)
            self.redis.expire(user_sessions_key, settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600)
            
            return True
        except Exception:
            return False
    
    def get_session(self, session_token: str) -> dict:
        """Get session data"""
        try:
            session_key = f"{self.session_prefix}{session_token}"
            return self.redis.hgetall(session_key)
        except Exception:
            return {}
    
    def invalidate_session(self, session_token: str) -> bool:
        """Invalidate a specific session"""
        try:
            session_key = f"{self.session_prefix}{session_token}"
            session_data = self.redis.hgetall(session_key)
            
            if session_data:
                user_id = session_data.get("user_id")
                if user_id:
                    user_sessions_key = f"{self.user_sessions_prefix}{user_id}"
                    self.redis.srem(user_sessions_key, session_token)
                
                self.redis.delete(session_key)
            
            return True
        except Exception:
            return False
    
    def invalidate_all_user_sessions(self, user_id: str) -> bool:
        """Invalidate all sessions for a user"""
        try:
            user_sessions_key = f"{self.user_sessions_prefix}{user_id}"
            session_tokens = self.redis.smembers(user_sessions_key)
            
            for token in session_tokens:
                session_key = f"{self.session_prefix}{token}"
                self.redis.delete(session_key)
            
            self.redis.delete(user_sessions_key)
            return True
        except Exception:
            return False
    
    def get_user_sessions(self, user_id: str) -> list:
        """Get all active sessions for a user"""
        try:
            user_sessions_key = f"{self.user_sessions_prefix}{user_id}"
            session_tokens = self.redis.smembers(user_sessions_key)
            
            sessions = []
            for token in session_tokens:
                session_data = self.get_session(token)
                if session_data:
                    sessions.append({
                        "token": token,
                        **session_data
                    })
            
            return sessions
        except Exception:
            return []


# Rate limiting
class RateLimiter:
    """Rate limiting using Redis"""
    
    def __init__(self):
        self.redis = redis_client
    
    def is_allowed(self, key: str, limit: int, window: int = 60) -> bool:
        """
        Check if request is allowed based on rate limit
        
        Args:
            key: Unique identifier (e.g., user_id, ip_address)
            limit: Maximum number of requests
            window: Time window in seconds
        """
        try:
            current = self.redis.get(key)
            if current is None:
                self.redis.setex(key, window, 1)
                return True
            
            if int(current) < limit:
                self.redis.incr(key)
                return True
            
            return False
        except Exception:
            # If Redis is down, allow the request
            return True
    
    def get_remaining(self, key: str, limit: int) -> int:
        """Get remaining requests for a key"""
        try:
            current = self.redis.get(key)
            if current is None:
                return limit
            return max(0, limit - int(current))
        except Exception:
            return limit
    
    def reset_limit(self, key: str) -> bool:
        """Reset rate limit for a key"""
        try:
            self.redis.delete(key)
            return True
        except Exception:
            return False


# Global instances
db_manager = DatabaseManager()
session_manager = SessionManager()
rate_limiter = RateLimiter()


# Import datetime for session manager
from datetime import datetime
