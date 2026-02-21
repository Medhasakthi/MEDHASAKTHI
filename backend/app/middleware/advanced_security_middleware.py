"""
Advanced Security Middleware for MEDHASAKTHI
Implements intrusion detection, advanced rate limiting, and threat monitoring
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set
from collections import defaultdict, deque
import re
import hashlib
import ipaddress

from fastapi import Request, Response, HTTPException
from fastapi.responses import JSONResponse
import redis
from sqlalchemy.orm import Session

from app.core.database import get_db, get_redis
from app.core.config import settings

logger = logging.getLogger(__name__)

class ThreatDetector:
    """Advanced threat detection system"""
    
    def __init__(self):
        self.redis_client = get_redis()
        self.suspicious_patterns = [
            r'(?i)(union|select|insert|delete|drop|create|alter|exec|script)',  # SQL injection
            r'(?i)(<script|javascript:|vbscript:|onload|onerror)',  # XSS
            r'(?i)(\.\.\/|\.\.\\|\/etc\/|\/proc\/|\/sys\/)',  # Path traversal
            r'(?i)(cmd|powershell|bash|sh|exec|eval)',  # Command injection
            r'(?i)(base64|hex|url|html)encode',  # Encoding attacks
        ]
        self.compiled_patterns = [re.compile(pattern) for pattern in self.suspicious_patterns]
        
        # Threat scoring thresholds
        self.threat_levels = {
            'low': 10,
            'medium': 25,
            'high': 50,
            'critical': 100
        }
        
        # Rate limiting configurations
        self.rate_limits = {
            'login': {'requests': 5, 'window': 300},  # 5 attempts per 5 minutes
            'register': {'requests': 3, 'window': 3600},  # 3 registrations per hour
            'api': {'requests': 100, 'window': 60},  # 100 API calls per minute
            'payment': {'requests': 10, 'window': 3600},  # 10 payments per hour
        }

    async def detect_threats(self, request: Request) -> Dict:
        """Comprehensive threat detection"""
        threats = []
        threat_score = 0
        
        # Get request data
        ip_address = self.get_client_ip(request)
        user_agent = request.headers.get('user-agent', '')
        url_path = str(request.url.path)
        
        # Check for suspicious patterns in URL
        for pattern in self.compiled_patterns:
            if pattern.search(url_path):
                threats.append(f"Suspicious pattern in URL: {pattern.pattern}")
                threat_score += 15
        
        # Check for suspicious patterns in headers
        for header_name, header_value in request.headers.items():
            for pattern in self.compiled_patterns:
                if pattern.search(header_value):
                    threats.append(f"Suspicious pattern in header {header_name}")
                    threat_score += 10
        
        # Check for suspicious user agents
        if self.is_suspicious_user_agent(user_agent):
            threats.append("Suspicious user agent detected")
            threat_score += 20
        
        # Check for rapid requests (potential DDoS)
        if await self.check_rapid_requests(ip_address):
            threats.append("Rapid request pattern detected")
            threat_score += 30
        
        # Check for geographic anomalies
        if await self.check_geographic_anomaly(ip_address):
            threats.append("Geographic anomaly detected")
            threat_score += 25
        
        # Check for known malicious IPs
        if await self.check_malicious_ip(ip_address):
            threats.append("Known malicious IP address")
            threat_score += 50
        
        return {
            'threats': threats,
            'threat_score': threat_score,
            'threat_level': self.get_threat_level(threat_score),
            'ip_address': ip_address,
            'timestamp': datetime.utcnow().isoformat()
        }

    def get_client_ip(self, request: Request) -> str:
        """Get real client IP address"""
        # Check for forwarded headers
        forwarded_for = request.headers.get('x-forwarded-for')
        if forwarded_for:
            return forwarded_for.split(',')[0].strip()
        
        real_ip = request.headers.get('x-real-ip')
        if real_ip:
            return real_ip
        
        return request.client.host if request.client else 'unknown'

    def is_suspicious_user_agent(self, user_agent: str) -> bool:
        """Check for suspicious user agents"""
        suspicious_agents = [
            'sqlmap', 'nikto', 'nmap', 'masscan', 'zap', 'burp',
            'python-requests', 'curl', 'wget', 'bot', 'crawler',
            'scanner', 'exploit', 'hack'
        ]
        
        user_agent_lower = user_agent.lower()
        return any(agent in user_agent_lower for agent in suspicious_agents)

    async def check_rapid_requests(self, ip_address: str) -> bool:
        """Check for rapid request patterns"""
        key = f"requests:{ip_address}"
        current_time = int(time.time())
        
        # Add current request
        await self.redis_client.zadd(key, {current_time: current_time})
        
        # Remove old entries (older than 1 minute)
        await self.redis_client.zremrangebyscore(key, 0, current_time - 60)
        
        # Count requests in last minute
        request_count = await self.redis_client.zcard(key)
        
        # Set expiry
        await self.redis_client.expire(key, 60)
        
        return request_count > 50  # More than 50 requests per minute

    async def check_geographic_anomaly(self, ip_address: str) -> bool:
        """Check for geographic anomalies (simplified)"""
        # This would integrate with a GeoIP service in production
        # For now, we'll check for private/local IPs
        try:
            ip = ipaddress.ip_address(ip_address)
            return ip.is_private or ip.is_loopback
        except ValueError:
            return True  # Invalid IP is suspicious

    async def check_malicious_ip(self, ip_address: str) -> bool:
        """Check against known malicious IP lists"""
        # Check our internal blacklist
        blacklist_key = "blacklisted_ips"
        is_blacklisted = await self.redis_client.sismember(blacklist_key, ip_address)
        
        return bool(is_blacklisted)

    def get_threat_level(self, threat_score: int) -> str:
        """Determine threat level based on score"""
        if threat_score >= self.threat_levels['critical']:
            return 'critical'
        elif threat_score >= self.threat_levels['high']:
            return 'high'
        elif threat_score >= self.threat_levels['medium']:
            return 'medium'
        elif threat_score >= self.threat_levels['low']:
            return 'low'
        else:
            return 'none'

    async def log_threat(self, threat_data: Dict):
        """Log threat to Redis and potentially alert"""
        threat_key = f"threats:{threat_data['ip_address']}:{int(time.time())}"
        await self.redis_client.setex(threat_key, 86400, json.dumps(threat_data))  # 24 hours
        
        # If critical threat, add to blacklist temporarily
        if threat_data['threat_level'] == 'critical':
            await self.redis_client.sadd("blacklisted_ips", threat_data['ip_address'])
            await self.redis_client.expire("blacklisted_ips", 3600)  # 1 hour blacklist
            
            # Log critical threat
            logger.critical(f"Critical threat detected: {threat_data}")

class AdvancedRateLimiter:
    """Advanced rate limiting with multiple strategies"""
    
    def __init__(self):
        self.redis_client = get_redis()
    
    async def check_rate_limit(self, identifier: str, limit_type: str) -> Dict:
        """Check if request exceeds rate limit"""
        if limit_type not in ThreatDetector().rate_limits:
            return {'allowed': True, 'remaining': float('inf')}
        
        config = ThreatDetector().rate_limits[limit_type]
        key = f"rate_limit:{limit_type}:{identifier}"
        current_time = int(time.time())
        window_start = current_time - config['window']
        
        # Remove old entries
        await self.redis_client.zremrangebyscore(key, 0, window_start)
        
        # Count current requests
        current_count = await self.redis_client.zcard(key)
        
        if current_count >= config['requests']:
            return {
                'allowed': False,
                'remaining': 0,
                'reset_time': window_start + config['window']
            }
        
        # Add current request
        await self.redis_client.zadd(key, {current_time: current_time})
        await self.redis_client.expire(key, config['window'])
        
        return {
            'allowed': True,
            'remaining': config['requests'] - current_count - 1
        }

# Middleware instances
threat_detector = ThreatDetector()
rate_limiter = AdvancedRateLimiter()

async def advanced_security_middleware(request: Request, call_next):
    """Advanced security middleware"""
    start_time = time.time()
    
    try:
        # Get client IP
        client_ip = threat_detector.get_client_ip(request)
        
        # Detect threats
        threat_analysis = await threat_detector.detect_threats(request)
        
        # Block critical threats immediately
        if threat_analysis['threat_level'] == 'critical':
            await threat_detector.log_threat(threat_analysis)
            return JSONResponse(
                status_code=403,
                content={
                    "error": "Access Denied",
                    "message": "Suspicious activity detected",
                    "threat_id": hashlib.md5(f"{client_ip}{time.time()}".encode()).hexdigest()
                }
            )
        
        # Check rate limits
        endpoint_type = 'api'  # Default
        if 'login' in str(request.url.path):
            endpoint_type = 'login'
        elif 'register' in str(request.url.path):
            endpoint_type = 'register'
        elif 'payment' in str(request.url.path):
            endpoint_type = 'payment'
        
        rate_limit_result = await rate_limiter.check_rate_limit(client_ip, endpoint_type)
        
        if not rate_limit_result['allowed']:
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Rate Limit Exceeded",
                    "message": f"Too many {endpoint_type} requests",
                    "reset_time": rate_limit_result.get('reset_time')
                },
                headers={
                    "X-RateLimit-Limit": str(ThreatDetector().rate_limits[endpoint_type]['requests']),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(rate_limit_result.get('reset_time', 0))
                }
            )
        
        # Process request
        response = await call_next(request)
        
        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        
        # Add rate limit headers
        response.headers["X-RateLimit-Limit"] = str(ThreatDetector().rate_limits[endpoint_type]['requests'])
        response.headers["X-RateLimit-Remaining"] = str(rate_limit_result['remaining'])
        
        # Log high-level threats
        if threat_analysis['threat_level'] in ['high', 'medium']:
            await threat_detector.log_threat(threat_analysis)
        
        # Add processing time
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        
        return response
        
    except Exception as e:
        logger.error(f"Security middleware error: {e}")
        # Don't block requests due to security middleware errors
        return await call_next(request)
