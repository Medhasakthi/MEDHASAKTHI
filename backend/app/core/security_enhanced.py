"""
Enhanced Security Module for MEDHASAKTHI
Enterprise-grade security features including advanced authentication,
encryption, monitoring, and threat detection
"""
import hashlib
import hmac
import secrets
import ipaddress
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any, Tuple
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import json
import geoip2.database
from sqlalchemy.orm import Session
from fastapi import Request, HTTPException, status
import redis
import logging

from app.core.config import settings
from app.models.user import User, SecurityLog, DeviceSession

# Configure security logger
security_logger = logging.getLogger("security")
security_logger.setLevel(logging.INFO)

# Redis client for security caching
redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_SECURITY_DB,
    decode_responses=True
)


class AdvancedSecurityManager:
    """Advanced security manager with enterprise-grade features"""
    
    def __init__(self):
        self.encryption_key = self._get_or_create_encryption_key()
        self.cipher_suite = Fernet(self.encryption_key)
        self.geoip_reader = self._initialize_geoip()
        
    def _get_or_create_encryption_key(self) -> bytes:
        """Get or create encryption key for data encryption"""
        key_file = "encryption.key"
        try:
            with open(key_file, "rb") as f:
                return f.read()
        except FileNotFoundError:
            key = Fernet.generate_key()
            with open(key_file, "wb") as f:
                f.write(key)
            return key
    
    def _initialize_geoip(self):
        """Initialize GeoIP database for location tracking"""
        try:
            return geoip2.database.Reader('GeoLite2-City.mmdb')
        except:
            return None
    
    def encrypt_sensitive_data(self, data: str) -> str:
        """Encrypt sensitive data"""
        return self.cipher_suite.encrypt(data.encode()).decode()
    
    def decrypt_sensitive_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data"""
        return self.cipher_suite.decrypt(encrypted_data.encode()).decode()
    
    def generate_secure_token(self, length: int = 32) -> str:
        """Generate cryptographically secure token"""
        return secrets.token_urlsafe(length)
    
    def hash_password_advanced(self, password: str, salt: Optional[str] = None) -> Tuple[str, str]:
        """Advanced password hashing with PBKDF2"""
        if not salt:
            salt = secrets.token_hex(32)
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt.encode(),
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key.decode(), salt
    
    def verify_password_advanced(self, password: str, hashed_password: str, salt: str) -> bool:
        """Verify password with advanced hashing"""
        key, _ = self.hash_password_advanced(password, salt)
        return hmac.compare_digest(key, hashed_password)


class ThreatDetectionSystem:
    """Real-time threat detection and prevention system"""
    
    def __init__(self):
        self.suspicious_patterns = [
            r'(?i)(union|select|insert|delete|drop|create|alter)',  # SQL injection
            r'(?i)(<script|javascript:|vbscript:|onload=|onerror=)',  # XSS
            r'(?i)(\.\.\/|\.\.\\)',  # Path traversal
            r'(?i)(eval\(|exec\(|system\()',  # Code injection
        ]
        self.max_requests_per_minute = 60
        self.max_failed_logins = 5
        self.lockout_duration = 900  # 15 minutes
    
    def detect_sql_injection(self, input_data: str) -> bool:
        """Detect potential SQL injection attempts"""
        import re
        for pattern in self.suspicious_patterns:
            if re.search(pattern, input_data):
                return True
        return False
    
    def check_rate_limiting(self, client_ip: str, endpoint: str) -> bool:
        """Check if client is within rate limits"""
        key = f"rate_limit:{client_ip}:{endpoint}"
        current_requests = redis_client.get(key)
        
        if current_requests is None:
            redis_client.setex(key, 60, 1)
            return True
        
        if int(current_requests) >= self.max_requests_per_minute:
            return False
        
        redis_client.incr(key)
        return True
    
    def track_failed_login(self, identifier: str) -> bool:
        """Track failed login attempts and implement lockout"""
        key = f"failed_login:{identifier}"
        failed_attempts = redis_client.get(key)
        
        if failed_attempts is None:
            redis_client.setex(key, self.lockout_duration, 1)
            return True
        
        failed_count = int(failed_attempts)
        if failed_count >= self.max_failed_logins:
            return False
        
        redis_client.incr(key)
        redis_client.expire(key, self.lockout_duration)
        return True
    
    def clear_failed_logins(self, identifier: str):
        """Clear failed login attempts after successful login"""
        redis_client.delete(f"failed_login:{identifier}")
    
    def detect_anomalous_behavior(self, user_id: str, request_data: Dict[str, Any]) -> List[str]:
        """Detect anomalous user behavior"""
        anomalies = []
        
        # Check for unusual login times
        current_hour = datetime.now().hour
        if current_hour < 6 or current_hour > 22:
            anomalies.append("unusual_login_time")
        
        # Check for multiple device logins
        active_sessions = redis_client.get(f"active_sessions:{user_id}")
        if active_sessions and int(active_sessions) > 3:
            anomalies.append("multiple_device_logins")
        
        # Check for rapid API calls
        api_calls = redis_client.get(f"api_calls:{user_id}")
        if api_calls and int(api_calls) > 100:
            anomalies.append("rapid_api_calls")
        
        return anomalies


class DeviceTrackingSystem:
    """Advanced device tracking and session management"""
    
    def __init__(self):
        self.security_manager = AdvancedSecurityManager()
    
    def generate_device_fingerprint(self, request: Request) -> str:
        """Generate unique device fingerprint"""
        user_agent = request.headers.get("user-agent", "")
        accept_language = request.headers.get("accept-language", "")
        accept_encoding = request.headers.get("accept-encoding", "")
        
        fingerprint_data = f"{user_agent}:{accept_language}:{accept_encoding}"
        return hashlib.sha256(fingerprint_data.encode()).hexdigest()
    
    def get_location_from_ip(self, ip_address: str) -> Dict[str, Any]:
        """Get location information from IP address"""
        if not self.security_manager.geoip_reader:
            return {"country": "Unknown", "city": "Unknown"}
        
        try:
            response = self.security_manager.geoip_reader.city(ip_address)
            return {
                "country": response.country.name,
                "city": response.city.name,
                "latitude": float(response.location.latitude) if response.location.latitude else None,
                "longitude": float(response.location.longitude) if response.location.longitude else None
            }
        except:
            return {"country": "Unknown", "city": "Unknown"}
    
    def create_device_session(
        self, 
        user_id: str, 
        request: Request, 
        db: Session
    ) -> DeviceSession:
        """Create new device session with tracking"""
        client_ip = request.client.host
        device_fingerprint = self.generate_device_fingerprint(request)
        location = self.get_location_from_ip(client_ip)
        
        session = DeviceSession(
            user_id=user_id,
            device_fingerprint=device_fingerprint,
            ip_address=client_ip,
            user_agent=request.headers.get("user-agent", ""),
            location_data=location,
            is_active=True,
            created_at=datetime.now()
        )
        
        db.add(session)
        db.commit()
        
        # Track active sessions in Redis
        redis_client.incr(f"active_sessions:{user_id}")
        redis_client.expire(f"active_sessions:{user_id}", 86400)  # 24 hours
        
        return session
    
    def validate_device_session(
        self, 
        user_id: str, 
        device_fingerprint: str, 
        db: Session
    ) -> bool:
        """Validate if device session is legitimate"""
        session = db.query(DeviceSession).filter(
            DeviceSession.user_id == user_id,
            DeviceSession.device_fingerprint == device_fingerprint,
            DeviceSession.is_active == True
        ).first()
        
        return session is not None


class SecurityAuditLogger:
    """Comprehensive security audit logging system"""
    
    def __init__(self):
        self.security_manager = AdvancedSecurityManager()
    
    def log_security_event(
        self,
        event_type: str,
        user_id: Optional[str],
        ip_address: str,
        details: Dict[str, Any],
        severity: str = "INFO",
        db: Session = None
    ):
        """Log security events for audit trail"""
        
        # Encrypt sensitive details
        encrypted_details = self.security_manager.encrypt_sensitive_data(
            json.dumps(details)
        )
        
        # Create security log entry
        if db:
            log_entry = SecurityLog(
                event_type=event_type,
                user_id=user_id,
                ip_address=ip_address,
                details=encrypted_details,
                severity=severity,
                timestamp=datetime.now()
            )
            db.add(log_entry)
            db.commit()
        
        # Log to security logger
        security_logger.info(
            f"Security Event: {event_type} | User: {user_id} | IP: {ip_address} | Severity: {severity}"
        )
        
        # Store in Redis for real-time monitoring
        redis_client.lpush(
            "security_events",
            json.dumps({
                "event_type": event_type,
                "user_id": user_id,
                "ip_address": ip_address,
                "severity": severity,
                "timestamp": datetime.now().isoformat()
            })
        )
        redis_client.ltrim("security_events", 0, 1000)  # Keep last 1000 events
    
    def get_security_events(
        self,
        user_id: Optional[str] = None,
        event_type: Optional[str] = None,
        hours: int = 24
    ) -> List[Dict[str, Any]]:
        """Get security events for monitoring"""
        events = redis_client.lrange("security_events", 0, -1)
        filtered_events = []
        
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        for event_json in events:
            event = json.loads(event_json)
            event_time = datetime.fromisoformat(event["timestamp"])
            
            if event_time < cutoff_time:
                continue
            
            if user_id and event.get("user_id") != user_id:
                continue
            
            if event_type and event.get("event_type") != event_type:
                continue
            
            filtered_events.append(event)
        
        return filtered_events


class IPWhitelistManager:
    """IP whitelisting and geolocation restrictions"""
    
    def __init__(self):
        self.whitelisted_ips = set()
        self.blocked_countries = set()
        self.load_whitelist()
    
    def load_whitelist(self):
        """Load IP whitelist from configuration"""
        # This would typically load from database or config file
        self.whitelisted_ips = set(getattr(settings, 'WHITELISTED_IPS', []))
        self.blocked_countries = set(getattr(settings, 'BLOCKED_COUNTRIES', []))
    
    def is_ip_whitelisted(self, ip_address: str) -> bool:
        """Check if IP is whitelisted"""
        if not self.whitelisted_ips:
            return True  # No whitelist configured
        
        try:
            ip = ipaddress.ip_address(ip_address)
            for whitelisted in self.whitelisted_ips:
                if ip in ipaddress.ip_network(whitelisted, strict=False):
                    return True
        except:
            pass
        
        return False
    
    def is_country_blocked(self, country: str) -> bool:
        """Check if country is blocked"""
        return country in self.blocked_countries


# Initialize global security components
security_manager = AdvancedSecurityManager()
threat_detector = ThreatDetectionSystem()
device_tracker = DeviceTrackingSystem()
audit_logger = SecurityAuditLogger()
ip_manager = IPWhitelistManager()


# Security middleware functions
async def security_middleware(request: Request, call_next):
    """Enhanced security middleware"""
    client_ip = request.client.host
    
    # Check IP whitelist
    if not ip_manager.is_ip_whitelisted(client_ip):
        audit_logger.log_security_event(
            "ip_not_whitelisted",
            None,
            client_ip,
            {"endpoint": str(request.url)},
            "WARNING"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied from this IP address"
        )
    
    # Check rate limiting
    endpoint = str(request.url.path)
    if not threat_detector.check_rate_limiting(client_ip, endpoint):
        audit_logger.log_security_event(
            "rate_limit_exceeded",
            None,
            client_ip,
            {"endpoint": endpoint},
            "WARNING"
        )
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded"
        )
    
    # Check for suspicious patterns in request
    if request.method in ["POST", "PUT", "PATCH"]:
        body = await request.body()
        if body and threat_detector.detect_sql_injection(body.decode()):
            audit_logger.log_security_event(
                "sql_injection_attempt",
                None,
                client_ip,
                {"endpoint": endpoint, "body_length": len(body)},
                "CRITICAL"
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Malicious request detected"
            )
    
    response = await call_next(request)
    return response
