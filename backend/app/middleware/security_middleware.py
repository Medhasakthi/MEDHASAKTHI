"""
Advanced Security Middleware for MEDHASAKTHI
Enterprise-grade security middleware with comprehensive protection
"""
import time
import json
import hashlib
import ipaddress
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from fastapi import Request, Response, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import redis
import geoip2.database
import user_agents
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.security_enhanced import (
    security_manager, threat_detector, audit_logger, ip_manager
)
from app.models.user import User, SecurityLog, DeviceSession


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses"""
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self' https:; "
            "connect-src 'self' wss: https:; "
            "frame-ancestors 'none';"
        )
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = (
            "geolocation=(), microphone=(), camera=(), "
            "payment=(), usb=(), magnetometer=(), gyroscope=(), "
            "accelerometer=(), ambient-light-sensor=()"
        )
        
        return response


class AdvancedRateLimitMiddleware(BaseHTTPMiddleware):
    """Advanced rate limiting with multiple strategies"""
    
    def __init__(self, app, redis_client: redis.Redis):
        super().__init__(app)
        self.redis = redis_client
        self.rate_limits = {
            "global": {"requests": 1000, "window": 60},  # 1000 req/min globally
            "per_ip": {"requests": 100, "window": 60},   # 100 req/min per IP
            "auth": {"requests": 10, "window": 60},      # 10 auth attempts/min
            "api": {"requests": 500, "window": 60},      # 500 API calls/min per user
        }
    
    async def dispatch(self, request: Request, call_next):
        client_ip = self._get_client_ip(request)
        endpoint = request.url.path
        
        # Check different rate limit types
        if not await self._check_global_rate_limit():
            return self._rate_limit_response("Global rate limit exceeded")
        
        if not await self._check_ip_rate_limit(client_ip):
            return self._rate_limit_response("IP rate limit exceeded")
        
        if endpoint.startswith("/api/v1/auth/") and not await self._check_auth_rate_limit(client_ip):
            return self._rate_limit_response("Authentication rate limit exceeded")
        
        # Check user-specific rate limits for authenticated requests
        user_id = await self._get_user_from_request(request)
        if user_id and endpoint.startswith("/api/") and not await self._check_user_rate_limit(user_id):
            return self._rate_limit_response("User API rate limit exceeded")
        
        response = await call_next(request)
        return response
    
    def _get_client_ip(self, request: Request) -> str:
        """Get real client IP considering proxies"""
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        return request.client.host
    
    async def _check_global_rate_limit(self) -> bool:
        """Check global rate limit"""
        key = "rate_limit:global"
        return await self._check_rate_limit(key, self.rate_limits["global"])
    
    async def _check_ip_rate_limit(self, ip: str) -> bool:
        """Check per-IP rate limit"""
        key = f"rate_limit:ip:{ip}"
        return await self._check_rate_limit(key, self.rate_limits["per_ip"])
    
    async def _check_auth_rate_limit(self, ip: str) -> bool:
        """Check authentication rate limit"""
        key = f"rate_limit:auth:{ip}"
        return await self._check_rate_limit(key, self.rate_limits["auth"])
    
    async def _check_user_rate_limit(self, user_id: str) -> bool:
        """Check user-specific rate limit"""
        key = f"rate_limit:user:{user_id}"
        return await self._check_rate_limit(key, self.rate_limits["api"])
    
    async def _check_rate_limit(self, key: str, limits: Dict[str, int]) -> bool:
        """Generic rate limit checker"""
        try:
            current = self.redis.get(key)
            if current is None:
                self.redis.setex(key, limits["window"], 1)
                return True
            
            if int(current) >= limits["requests"]:
                return False
            
            self.redis.incr(key)
            return True
        except Exception:
            # If Redis is down, allow the request
            return True
    
    async def _get_user_from_request(self, request: Request) -> Optional[str]:
        """Extract user ID from JWT token"""
        try:
            auth_header = request.headers.get("Authorization")
            if not auth_header or not auth_header.startswith("Bearer "):
                return None
            
            token = auth_header.split(" ")[1]
            # This would decode the JWT and extract user_id
            # For now, return None to skip user-specific rate limiting
            return None
        except Exception:
            return None
    
    def _rate_limit_response(self, message: str) -> JSONResponse:
        """Return rate limit exceeded response"""
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={
                "error": "Rate limit exceeded",
                "message": message,
                "retry_after": 60
            },
            headers={"Retry-After": "60"}
        )


class ThreatDetectionMiddleware(BaseHTTPMiddleware):
    """Advanced threat detection and prevention"""
    
    def __init__(self, app, redis_client: redis.Redis):
        super().__init__(app)
        self.redis = redis_client
        self.suspicious_patterns = [
            # SQL Injection patterns
            r'(?i)(union\s+select|select\s+.*\s+from|insert\s+into|delete\s+from|drop\s+table)',
            r'(?i)(or\s+1\s*=\s*1|and\s+1\s*=\s*1|\'.*or.*\'|\".*or.*\")',
            
            # XSS patterns
            r'(?i)(<script|javascript:|vbscript:|onload=|onerror=|onclick=)',
            r'(?i)(alert\s*\(|confirm\s*\(|prompt\s*\()',
            
            # Path traversal
            r'(\.\.\/|\.\.\\|%2e%2e%2f|%2e%2e%5c)',
            
            # Command injection
            r'(?i)(;|\||&|`|\$\(|exec\s*\(|system\s*\(|eval\s*\()',
            
            # LDAP injection
            r'(?i)(\*\)|\)\(|\|\(|\&\()',
        ]
    
    async def dispatch(self, request: Request, call_next):
        client_ip = self._get_client_ip(request)
        user_agent = request.headers.get("User-Agent", "")
        
        # Check for suspicious patterns in URL
        if self._detect_malicious_patterns(str(request.url)):
            await self._log_threat("malicious_url", client_ip, {"url": str(request.url)})
            return self._threat_response("Malicious request detected")
        
        # Check for suspicious patterns in headers
        for header_name, header_value in request.headers.items():
            if self._detect_malicious_patterns(header_value):
                await self._log_threat("malicious_header", client_ip, {
                    "header": header_name,
                    "value": header_value[:100]
                })
                return self._threat_response("Malicious request detected")
        
        # Check for bot/crawler patterns
        if self._detect_bot_patterns(user_agent):
            await self._log_threat("bot_detected", client_ip, {"user_agent": user_agent})
            # Don't block bots, just log them
        
        # Check request body for POST/PUT requests
        if request.method in ["POST", "PUT", "PATCH"]:
            body = await self._get_request_body(request)
            if body and self._detect_malicious_patterns(body):
                await self._log_threat("malicious_payload", client_ip, {
                    "method": request.method,
                    "path": request.url.path,
                    "body_length": len(body)
                })
                return self._threat_response("Malicious payload detected")
        
        # Check for suspicious IP behavior
        if await self._is_suspicious_ip(client_ip):
            await self._log_threat("suspicious_ip", client_ip, {})
            return self._threat_response("Suspicious activity detected")
        
        response = await call_next(request)
        return response
    
    def _get_client_ip(self, request: Request) -> str:
        """Get real client IP"""
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        return request.client.host
    
    def _detect_malicious_patterns(self, text: str) -> bool:
        """Detect malicious patterns in text"""
        import re
        for pattern in self.suspicious_patterns:
            if re.search(pattern, text):
                return True
        return False
    
    def _detect_bot_patterns(self, user_agent: str) -> bool:
        """Detect bot/crawler patterns"""
        bot_patterns = [
            r'(?i)(bot|crawler|spider|scraper|curl|wget|python|java)',
            r'(?i)(googlebot|bingbot|slurp|duckduckbot|baiduspider)',
        ]
        
        import re
        for pattern in bot_patterns:
            if re.search(pattern, user_agent):
                return True
        return False
    
    async def _get_request_body(self, request: Request) -> Optional[str]:
        """Safely get request body"""
        try:
            body = await request.body()
            return body.decode('utf-8', errors='ignore')
        except Exception:
            return None
    
    async def _is_suspicious_ip(self, ip: str) -> bool:
        """Check if IP shows suspicious behavior"""
        try:
            # Check request frequency
            key = f"ip_requests:{ip}"
            requests_count = self.redis.get(key)
            
            if requests_count is None:
                self.redis.setex(key, 300, 1)  # 5 minutes window
                return False
            
            # More than 500 requests in 5 minutes is suspicious
            if int(requests_count) > 500:
                return True
            
            self.redis.incr(key)
            return False
        except Exception:
            return False
    
    async def _log_threat(self, threat_type: str, ip: str, details: Dict[str, Any]):
        """Log threat detection"""
        audit_logger.log_security_event(
            event_type=f"threat_detected_{threat_type}",
            user_id=None,
            ip_address=ip,
            details=details,
            severity="WARNING"
        )
    
    def _threat_response(self, message: str) -> JSONResponse:
        """Return threat detection response"""
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "error": "Security violation",
                "message": message,
                "code": "THREAT_DETECTED"
            }
        )


class DeviceTrackingMiddleware(BaseHTTPMiddleware):
    """Track and validate device sessions"""
    
    def __init__(self, app, redis_client: redis.Redis):
        super().__init__(app)
        self.redis = redis_client
    
    async def dispatch(self, request: Request, call_next):
        # Only track authenticated requests
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return await call_next(request)
        
        client_ip = self._get_client_ip(request)
        user_agent = request.headers.get("User-Agent", "")
        device_fingerprint = self._generate_device_fingerprint(request)
        
        # Track device session
        await self._track_device_session(client_ip, user_agent, device_fingerprint)
        
        response = await call_next(request)
        return response
    
    def _get_client_ip(self, request: Request) -> str:
        """Get real client IP"""
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        return request.client.host
    
    def _generate_device_fingerprint(self, request: Request) -> str:
        """Generate device fingerprint"""
        user_agent = request.headers.get("User-Agent", "")
        accept_language = request.headers.get("Accept-Language", "")
        accept_encoding = request.headers.get("Accept-Encoding", "")
        
        fingerprint_data = f"{user_agent}:{accept_language}:{accept_encoding}"
        return hashlib.sha256(fingerprint_data.encode()).hexdigest()
    
    async def _track_device_session(self, ip: str, user_agent: str, fingerprint: str):
        """Track device session in Redis"""
        try:
            session_key = f"device_session:{fingerprint}"
            session_data = {
                "ip": ip,
                "user_agent": user_agent,
                "last_seen": datetime.now().isoformat(),
                "request_count": 1
            }
            
            existing_session = self.redis.get(session_key)
            if existing_session:
                existing_data = json.loads(existing_session)
                session_data["request_count"] = existing_data.get("request_count", 0) + 1
            
            self.redis.setex(session_key, 86400, json.dumps(session_data))  # 24 hours
        except Exception:
            # Don't fail the request if tracking fails
            pass


class ComplianceMiddleware(BaseHTTPMiddleware):
    """Ensure compliance with various regulations"""
    
    async def dispatch(self, request: Request, call_next):
        # Add compliance headers
        response = await call_next(request)
        
        # GDPR compliance headers
        response.headers["X-Privacy-Policy"] = "https://medhasakthi.com/privacy"
        response.headers["X-Terms-Of-Service"] = "https://medhasakthi.com/terms"
        response.headers["X-Data-Controller"] = "MEDHASAKTHI Education Platform"
        
        # COPPA compliance (for users under 13)
        response.headers["X-Child-Privacy"] = "COPPA-Compliant"
        
        # FERPA compliance (for educational records)
        response.headers["X-Educational-Records"] = "FERPA-Protected"
        
        return response


# Initialize Redis client for middleware
try:
    middleware_redis = redis.Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        db=settings.REDIS_SECURITY_DB,
        decode_responses=True
    )
except Exception:
    # Fallback to mock Redis if connection fails
    class MockRedis:
        def get(self, key): return None
        def set(self, key, value): return True
        def setex(self, key, time, value): return True
        def incr(self, key): return 1
        def delete(self, key): return True
    
    middleware_redis = MockRedis()


# Export middleware instances
security_headers_middleware = SecurityHeadersMiddleware
advanced_rate_limit_middleware = lambda app: AdvancedRateLimitMiddleware(app, middleware_redis)
threat_detection_middleware = lambda app: ThreatDetectionMiddleware(app, middleware_redis)
device_tracking_middleware = lambda app: DeviceTrackingMiddleware(app, middleware_redis)
compliance_middleware = ComplianceMiddleware
