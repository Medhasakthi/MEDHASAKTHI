"""
CSRF Protection Middleware for MEDHASAKTHI
Implements Cross-Site Request Forgery protection
"""

import secrets
import hmac
import hashlib
import time
from typing import Optional
from fastapi import Request, Response, HTTPException
from fastapi.responses import JSONResponse
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)

class CSRFProtection:
    """CSRF Protection Implementation"""
    
    def __init__(self):
        self.secret_key = getattr(settings, 'CSRF_SECRET_KEY', secrets.token_urlsafe(32))
        self.token_name = 'csrf_token'
        self.header_name = 'X-CSRF-Token'
        self.cookie_name = 'csrf_token'
        self.token_lifetime = 3600  # 1 hour
        
        # Methods that require CSRF protection
        self.protected_methods = {'POST', 'PUT', 'PATCH', 'DELETE'}
        
        # Paths that don't require CSRF protection
        self.exempt_paths = {
            '/api/v1/auth/login',
            '/api/v1/auth/register', 
            '/api/v1/payments/upi/webhook',  # Payment webhooks
            '/health',
            '/metrics'
        }
    
    def generate_token(self, session_id: str = None) -> str:
        """Generate CSRF token"""
        if not session_id:
            session_id = secrets.token_urlsafe(16)
        
        timestamp = str(int(time.time()))
        message = f"{session_id}:{timestamp}"
        
        # Create HMAC signature
        signature = hmac.new(
            self.secret_key.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()
        
        token = f"{message}:{signature}"
        return token
    
    def validate_token(self, token: str, session_id: str = None) -> bool:
        """Validate CSRF token"""
        try:
            if not token:
                return False
            
            parts = token.split(':')
            if len(parts) != 3:
                return False
            
            token_session_id, timestamp, signature = parts
            
            # Check if session matches (if provided)
            if session_id and token_session_id != session_id:
                return False
            
            # Check token age
            token_time = int(timestamp)
            current_time = int(time.time())
            if current_time - token_time > self.token_lifetime:
                return False
            
            # Verify signature
            message = f"{token_session_id}:{timestamp}"
            expected_signature = hmac.new(
                self.secret_key.encode(),
                message.encode(),
                hashlib.sha256
            ).hexdigest()
            
            return hmac.compare_digest(signature, expected_signature)
            
        except (ValueError, TypeError) as e:
            logger.warning(f"CSRF token validation error: {e}")
            return False
    
    def is_exempt(self, path: str) -> bool:
        """Check if path is exempt from CSRF protection"""
        return path in self.exempt_paths or path.startswith('/static/')
    
    def get_token_from_request(self, request: Request) -> Optional[str]:
        """Extract CSRF token from request"""
        # Try header first
        token = request.headers.get(self.header_name)
        if token:
            return token
        
        # Try form data
        if hasattr(request, 'form'):
            try:
                form_data = request.form()
                token = form_data.get(self.token_name)
                if token:
                    return token
            except:
                pass
        
        # Try cookies as fallback
        token = request.cookies.get(self.cookie_name)
        return token

# Global CSRF protection instance
csrf_protection = CSRFProtection()

async def csrf_middleware(request: Request, call_next):
    """CSRF protection middleware"""
    
    # Skip CSRF protection for safe methods
    if request.method not in csrf_protection.protected_methods:
        response = await call_next(request)
        
        # Add CSRF token to safe responses for future use
        if request.method == 'GET':
            token = csrf_protection.generate_token()
            response.headers[csrf_protection.header_name] = token
            response.set_cookie(
                csrf_protection.cookie_name,
                token,
                max_age=csrf_protection.token_lifetime,
                httponly=True,
                secure=not settings.DEBUG,
                samesite='strict'
            )
        
        return response
    
    # Skip CSRF protection for exempt paths
    if csrf_protection.is_exempt(request.url.path):
        return await call_next(request)
    
    # Get CSRF token from request
    csrf_token = csrf_protection.get_token_from_request(request)
    
    if not csrf_token:
        logger.warning(f"CSRF token missing for {request.method} {request.url.path}")
        return JSONResponse(
            status_code=403,
            content={
                "error": "CSRF Protection",
                "message": "CSRF token missing",
                "code": "CSRF_TOKEN_MISSING"
            }
        )
    
    # Validate CSRF token
    if not csrf_protection.validate_token(csrf_token):
        logger.warning(f"Invalid CSRF token for {request.method} {request.url.path}")
        return JSONResponse(
            status_code=403,
            content={
                "error": "CSRF Protection", 
                "message": "Invalid CSRF token",
                "code": "CSRF_TOKEN_INVALID"
            }
        )
    
    # Process request
    response = await call_next(request)
    
    # Add new CSRF token to response
    new_token = csrf_protection.generate_token()
    response.headers[csrf_protection.header_name] = new_token
    response.set_cookie(
        csrf_protection.cookie_name,
        new_token,
        max_age=csrf_protection.token_lifetime,
        httponly=True,
        secure=not settings.DEBUG,
        samesite='strict'
    )
    
    return response

# CSRF token generation endpoint
async def get_csrf_token(request: Request) -> dict:
    """Generate and return CSRF token"""
    token = csrf_protection.generate_token()
    return {
        "csrf_token": token,
        "expires_in": csrf_protection.token_lifetime
    }
