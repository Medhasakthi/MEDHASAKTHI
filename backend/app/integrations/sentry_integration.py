"""
Sentry Integration for MEDHASAKTHI
Advanced error tracking, performance monitoring, and alerting
"""

import logging
import os
import time
from typing import Dict, Any, Optional
from functools import wraps

import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from sentry_sdk.integrations.redis import RedisIntegration
from sentry_sdk.integrations.logging import LoggingIntegration
from sentry_sdk.integrations.asyncio import AsyncioIntegration
from fastapi import Request, HTTPException

from app.core.config import settings

logger = logging.getLogger(__name__)

class SentryManager:
    """Advanced Sentry integration manager"""
    
    def __init__(self):
        self.initialized = False
        self.sentry_dsn = settings.SENTRY_DSN if hasattr(settings, 'SENTRY_DSN') else None
        
    def initialize(self):
        """Initialize Sentry with comprehensive configuration"""
        if not self.sentry_dsn or self.initialized:
            logger.warning("Sentry DSN not configured or already initialized")
            return
        
        try:
            # Configure logging integration
            logging_integration = LoggingIntegration(
                level=logging.INFO,        # Capture info and above as breadcrumbs
                event_level=logging.ERROR  # Send errors as events
            )
            
            sentry_sdk.init(
                dsn=self.sentry_dsn,
                environment=settings.ENVIRONMENT if hasattr(settings, 'ENVIRONMENT') else 'development',
                release=f"medhasakthi@{settings.APP_VERSION}",
                
                # Integrations
                integrations=[
                    FastApiIntegration(auto_enable=True),
                    SqlalchemyIntegration(),
                    RedisIntegration(),
                    logging_integration,
                    AsyncioIntegration(),
                ],
                
                # Performance monitoring
                traces_sample_rate=0.1,  # 10% of transactions
                profiles_sample_rate=0.1,  # 10% of transactions for profiling
                
                # Error filtering
                before_send=self.before_send_filter,
                before_send_transaction=self.before_send_transaction_filter,
                
                # Additional configuration
                attach_stacktrace=True,
                send_default_pii=False,  # Don't send personally identifiable information
                max_breadcrumbs=50,
                
                # Custom tags
                default_integrations=True,
            )
            
            # Set global tags
            sentry_sdk.set_tag("service", "medhasakthi-api")
            sentry_sdk.set_tag("version", settings.APP_VERSION)
            
            self.initialized = True
            logger.info("Sentry integration initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Sentry: {e}")
    
    def before_send_filter(self, event: Dict[str, Any], hint: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Filter events before sending to Sentry"""
        
        # Don't send health check errors
        if 'request' in event and event['request'].get('url', '').endswith('/health'):
            return None
        
        # Filter out common non-critical errors
        if 'exception' in event:
            exception_type = event['exception']['values'][0]['type']
            if exception_type in ['HTTPException', 'ValidationError']:
                # Only send 5xx HTTP errors
                if hasattr(hint.get('exc_info', [None, None, None])[1], 'status_code'):
                    status_code = hint['exc_info'][1].status_code
                    if status_code < 500:
                        return None
        
        # Add custom context
        self.add_custom_context(event)
        
        return event
    
    def before_send_transaction_filter(self, event: Dict[str, Any], hint: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Filter transaction events"""
        
        # Don't track health check transactions
        if event.get('transaction', '').endswith('/health'):
            return None
        
        # Only track slow transactions (>1 second)
        if event.get('start_timestamp') and event.get('timestamp'):
            duration = event['timestamp'] - event['start_timestamp']
            if duration < 1.0:  # Less than 1 second
                return None
        
        return event
    
    def add_custom_context(self, event: Dict[str, Any]):
        """Add custom context to Sentry events"""
        
        # Add system information
        sentry_sdk.set_context("system", {
            "environment": settings.ENVIRONMENT if hasattr(settings, 'ENVIRONMENT') else 'unknown',
            "debug_mode": settings.DEBUG,
            "app_version": settings.APP_VERSION,
        })
        
        # Add database context if available
        try:
            from app.core.database import db_manager
            db_info = db_manager.get_db_info()
            sentry_sdk.set_context("database", {
                "status": db_info.get("status", "unknown"),
                "pool_size": db_info.get("pool_size", 0),
                "checked_out": db_info.get("checked_out", 0),
            })
        except Exception:
            pass
    
    def capture_exception(self, exception: Exception, **kwargs):
        """Capture exception with additional context"""
        if not self.initialized:
            return
        
        with sentry_sdk.push_scope() as scope:
            # Add additional context
            for key, value in kwargs.items():
                scope.set_extra(key, value)
            
            sentry_sdk.capture_exception(exception)
    
    def capture_message(self, message: str, level: str = "info", **kwargs):
        """Capture custom message"""
        if not self.initialized:
            return
        
        with sentry_sdk.push_scope() as scope:
            for key, value in kwargs.items():
                scope.set_extra(key, value)
            
            sentry_sdk.capture_message(message, level=level)
    
    def set_user_context(self, user_id: str, email: str = None, username: str = None):
        """Set user context for error tracking"""
        if not self.initialized:
            return
        
        sentry_sdk.set_user({
            "id": user_id,
            "email": email,
            "username": username,
        })
    
    def add_breadcrumb(self, message: str, category: str = "custom", level: str = "info", data: Dict = None):
        """Add breadcrumb for debugging"""
        if not self.initialized:
            return
        
        sentry_sdk.add_breadcrumb(
            message=message,
            category=category,
            level=level,
            data=data or {}
        )

# Global Sentry manager instance
sentry_manager = SentryManager()

def sentry_trace(operation_name: str = None):
    """Decorator to trace function performance"""
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            if not sentry_manager.initialized:
                return await func(*args, **kwargs)
            
            op_name = operation_name or f"{func.__module__}.{func.__name__}"
            
            with sentry_sdk.start_transaction(op=op_name, name=func.__name__):
                try:
                    result = await func(*args, **kwargs)
                    return result
                except Exception as e:
                    sentry_manager.capture_exception(e, function=func.__name__)
                    raise
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            if not sentry_manager.initialized:
                return func(*args, **kwargs)
            
            op_name = operation_name or f"{func.__module__}.{func.__name__}"
            
            with sentry_sdk.start_transaction(op=op_name, name=func.__name__):
                try:
                    result = func(*args, **kwargs)
                    return result
                except Exception as e:
                    sentry_manager.capture_exception(e, function=func.__name__)
                    raise
        
        # Return appropriate wrapper based on function type
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator

async def sentry_middleware(request: Request, call_next):
    """Sentry middleware for FastAPI"""
    
    if not sentry_manager.initialized:
        return await call_next(request)
    
    # Set request context
    with sentry_sdk.push_scope() as scope:
        scope.set_context("request", {
            "url": str(request.url),
            "method": request.method,
            "headers": dict(request.headers),
            "query_params": dict(request.query_params),
        })
        
        # Add breadcrumb
        sentry_manager.add_breadcrumb(
            message=f"{request.method} {request.url.path}",
            category="request",
            level="info",
            data={
                "method": request.method,
                "url": str(request.url),
                "user_agent": request.headers.get("user-agent"),
            }
        )
        
        start_time = time.time()
        
        try:
            response = await call_next(request)
            
            # Track response time
            response_time = time.time() - start_time
            
            # Add response breadcrumb
            sentry_manager.add_breadcrumb(
                message=f"Response {response.status_code}",
                category="response",
                level="info",
                data={
                    "status_code": response.status_code,
                    "response_time": response_time,
                }
            )
            
            # Track slow requests
            if response_time > 2.0:  # Slower than 2 seconds
                sentry_manager.capture_message(
                    f"Slow request: {request.method} {request.url.path}",
                    level="warning",
                    response_time=response_time,
                    endpoint=str(request.url.path)
                )
            
            return response
            
        except Exception as e:
            # Capture the exception with request context
            sentry_manager.capture_exception(
                e,
                request_method=request.method,
                request_url=str(request.url),
                request_headers=dict(request.headers)
            )
            raise

# Performance monitoring decorators
def monitor_database_query(query_name: str = None):
    """Monitor database query performance"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            if not sentry_manager.initialized:
                return await func(*args, **kwargs)
            
            with sentry_sdk.start_span(op="db.query", description=query_name or func.__name__):
                return await func(*args, **kwargs)
        
        return wrapper
    return decorator

def monitor_external_api(api_name: str = None):
    """Monitor external API calls"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            if not sentry_manager.initialized:
                return await func(*args, **kwargs)
            
            with sentry_sdk.start_span(op="http.client", description=api_name or func.__name__):
                return await func(*args, **kwargs)
        
        return wrapper
    return decorator

# Initialize Sentry on module import
sentry_manager.initialize()
