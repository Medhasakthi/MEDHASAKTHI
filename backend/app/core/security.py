"""
Security utilities for authentication and authorization
"""
import bcrypt
import jwt
import secrets
import pyotp
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from passlib.context import CryptContext
from jose import JWTError

from app.core.config import settings


class SecurityManager:
    """Handles all security-related operations"""
    
    def __init__(self):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.secret_key = settings.SECRET_KEY
        self.algorithm = settings.ALGORITHM
        self.access_token_expire_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES
        self.refresh_token_expire_days = settings.REFRESH_TOKEN_EXPIRE_DAYS
    
    # Password operations
    def hash_password(self, password: str) -> str:
        """Hash a password using bcrypt"""
        return self.pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return self.pwd_context.verify(plain_password, hashed_password)
    
    # JWT token operations
    def create_access_token(self, data: Dict[str, Any]) -> str:
        """Create JWT access token"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        to_encode.update({
            "exp": expire,
            "type": "access",
            "iat": datetime.utcnow()
        })
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
    
    def create_refresh_token(self, data: Dict[str, Any]) -> str:
        """Create JWT refresh token"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=self.refresh_token_expire_days)
        to_encode.update({
            "exp": expire,
            "type": "refresh",
            "iat": datetime.utcnow()
        })
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except JWTError:
            return None
    
    def decode_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Decode JWT token without verification (for debugging)"""
        try:
            return jwt.decode(token, options={"verify_signature": False})
        except JWTError:
            return None
    
    # Random token generation
    def generate_verification_token(self) -> str:
        """Generate secure random token for email verification"""
        return secrets.token_urlsafe(32)
    
    def generate_reset_token(self) -> str:
        """Generate secure random token for password reset"""
        return secrets.token_urlsafe(32)
    
    def generate_session_token(self) -> str:
        """Generate secure session token"""
        return secrets.token_urlsafe(64)
    
    # Two-Factor Authentication
    def generate_totp_secret(self) -> str:
        """Generate TOTP secret for 2FA"""
        return pyotp.random_base32()
    
    def generate_totp_qr_url(self, email: str, secret: str) -> str:
        """Generate TOTP QR code URL"""
        totp = pyotp.TOTP(secret)
        return totp.provisioning_uri(
            name=email,
            issuer_name="MEDHASAKTHI"
        )
    
    def verify_totp(self, token: str, secret: str) -> bool:
        """Verify TOTP token"""
        totp = pyotp.TOTP(secret)
        return totp.verify(token, valid_window=1)
    
    # Password validation
    def validate_password_strength(self, password: str) -> Dict[str, Any]:
        """Validate password strength"""
        errors = []
        
        if len(password) < 8:
            errors.append("Password must be at least 8 characters long")
        
        if not any(c.isupper() for c in password):
            errors.append("Password must contain at least one uppercase letter")
        
        if not any(c.islower() for c in password):
            errors.append("Password must contain at least one lowercase letter")
        
        if not any(c.isdigit() for c in password):
            errors.append("Password must contain at least one digit")
        
        if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            errors.append("Password must contain at least one special character")
        
        return {
            "is_valid": len(errors) == 0,
            "errors": errors,
            "strength": self._calculate_password_strength(password)
        }
    
    def _calculate_password_strength(self, password: str) -> str:
        """Calculate password strength score"""
        score = 0
        
        # Length
        if len(password) >= 8:
            score += 1
        if len(password) >= 12:
            score += 1
        
        # Character types
        if any(c.isupper() for c in password):
            score += 1
        if any(c.islower() for c in password):
            score += 1
        if any(c.isdigit() for c in password):
            score += 1
        if any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            score += 1
        
        # Complexity
        if len(set(password)) > len(password) * 0.7:  # Character diversity
            score += 1
        
        if score <= 2:
            return "weak"
        elif score <= 4:
            return "medium"
        elif score <= 6:
            return "strong"
        else:
            return "very_strong"
    
    # Exam-specific security
    def create_exam_session_token(self, user_id: str, exam_id: str, institute_id: str) -> str:
        """Create secure exam session token"""
        data = {
            "user_id": user_id,
            "exam_id": exam_id,
            "institute_id": institute_id,
            "session_type": "exam"
        }
        expire = datetime.utcnow() + timedelta(minutes=settings.EXAM_SESSION_TIMEOUT_MINUTES)
        data.update({
            "exp": expire,
            "type": "exam_session",
            "iat": datetime.utcnow()
        })
        return jwt.encode(data, self.secret_key, algorithm=self.algorithm)
    
    def verify_exam_session_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify exam session token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            if payload.get("type") != "exam_session":
                return None
            return payload
        except JWTError:
            return None
    
    # Rate limiting helpers
    def generate_rate_limit_key(self, identifier: str, action: str) -> str:
        """Generate rate limiting key"""
        return f"rate_limit:{action}:{identifier}"
    
    # Security headers
    def get_security_headers(self) -> Dict[str, str]:
        """Get security headers for responses"""
        return {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Content-Security-Policy": "default-src 'self'",
            "Referrer-Policy": "strict-origin-when-cross-origin"
        }


# Global security manager instance
security_manager = SecurityManager()


# Convenience functions
def hash_password(password: str) -> str:
    """Hash password"""
    return security_manager.hash_password(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password"""
    return security_manager.verify_password(plain_password, hashed_password)


def create_access_token(data: Dict[str, Any]) -> str:
    """Create access token"""
    return security_manager.create_access_token(data)


def create_refresh_token(data: Dict[str, Any]) -> str:
    """Create refresh token"""
    return security_manager.create_refresh_token(data)


def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """Verify token"""
    return security_manager.verify_token(token)


def validate_password_strength(password: str) -> Dict[str, Any]:
    """Validate password strength"""
    return security_manager.validate_password_strength(password)
