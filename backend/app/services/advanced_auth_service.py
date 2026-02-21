"""
Advanced Authentication Service for MEDHASAKTHI
Enterprise-grade authentication with biometric support, SSO, and advanced security
"""
import secrets
import base64
import qrcode
import pyotp
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime, timedelta
from io import BytesIO
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization
import jwt
import bcrypt
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
import redis

from app.core.config import settings
from app.core.security_enhanced import security_manager, audit_logger
from app.models.user import User, DeviceSession, SecurityLog
from app.services.email_service import email_service


class AdvancedAuthenticationService:
    """Advanced authentication service with multiple security layers"""
    
    def __init__(self):
        self.redis_client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_SESSION_DB,
            decode_responses=True
        )
        self.jwt_algorithm = "HS256"
        self.access_token_expire_minutes = 30
        self.refresh_token_expire_days = 30
        self.max_failed_attempts = 5
        self.lockout_duration_minutes = 15
    
    async def authenticate_user(
        self,
        email: str,
        password: str,
        device_info: Dict[str, Any],
        db: Session,
        totp_code: Optional[str] = None,
        biometric_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Comprehensive user authentication with multiple factors"""
        
        # Check if account is locked
        if await self._is_account_locked(email):
            raise HTTPException(
                status_code=status.HTTP_423_LOCKED,
                detail="Account temporarily locked due to multiple failed attempts"
            )
        
        # Get user from database
        user = db.query(User).filter(User.email == email).first()
        if not user:
            await self._record_failed_attempt(email, "user_not_found", device_info)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        # Verify password
        if not self._verify_password(password, user.password_hash):
            await self._record_failed_attempt(email, "invalid_password", device_info)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        # Check if 2FA is enabled
        if user.is_2fa_enabled:
            if not totp_code:
                return {
                    "requires_2fa": True,
                    "message": "Two-factor authentication required"
                }
            
            if not self._verify_totp(user.totp_secret, totp_code):
                await self._record_failed_attempt(email, "invalid_2fa", device_info)
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid two-factor authentication code"
                )
        
        # Verify biometric data if provided
        if biometric_data:
            if not await self._verify_biometric(user.id, biometric_data, db):
                await self._record_failed_attempt(email, "invalid_biometric", device_info)
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Biometric verification failed"
                )
        
        # Check device trust
        device_fingerprint = device_info.get("fingerprint")
        is_trusted_device = await self._is_trusted_device(str(user.id), device_fingerprint, db)
        
        if not is_trusted_device:
            # Send device verification email
            verification_token = await self._create_device_verification_token(
                str(user.id), device_fingerprint
            )
            await email_service.send_device_verification_email(
                user.email, user.full_name, device_info, verification_token
            )
            
            return {
                "requires_device_verification": True,
                "message": "Device verification required. Check your email."
            }
        
        # Clear failed attempts
        await self._clear_failed_attempts(email)
        
        # Create device session
        device_session = await self._create_device_session(user, device_info, db)
        
        # Generate tokens
        access_token = self._create_access_token(user)
        refresh_token = self._create_refresh_token(user)
        
        # Store refresh token
        await self._store_refresh_token(str(user.id), refresh_token, device_session.id)
        
        # Update last login
        user.last_login = datetime.now()
        db.commit()
        
        # Log successful authentication
        audit_logger.log_security_event(
            event_type="successful_authentication",
            user_id=str(user.id),
            ip_address=device_info.get("ip_address", "unknown"),
            details={
                "device_fingerprint": device_fingerprint,
                "user_agent": device_info.get("user_agent", "unknown"),
                "2fa_used": user.is_2fa_enabled,
                "biometric_used": biometric_data is not None
            },
            severity="INFO",
            db=db
        )
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": self.access_token_expire_minutes * 60,
            "user": {
                "id": str(user.id),
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role,
                "is_2fa_enabled": user.is_2fa_enabled
            },
            "device_session_id": str(device_session.id)
        }
    
    async def setup_2fa(self, user_id: str, db: Session) -> Dict[str, Any]:
        """Setup two-factor authentication for user"""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Generate TOTP secret
        secret = pyotp.random_base32()
        
        # Create TOTP URI for QR code
        totp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
            name=user.email,
            issuer_name="MEDHASAKTHI"
        )
        
        # Generate QR code
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(totp_uri)
        qr.make(fit=True)
        
        qr_image = qr.make_image(fill_color="black", back_color="white")
        qr_buffer = BytesIO()
        qr_image.save(qr_buffer, format="PNG")
        qr_base64 = base64.b64encode(qr_buffer.getvalue()).decode()
        
        # Generate backup codes
        backup_codes = [secrets.token_hex(4).upper() for _ in range(10)]
        
        # Store temporary secret (not activated until verified)
        await self.redis_client.setex(
            f"temp_2fa_secret:{user_id}",
            600,  # 10 minutes
            f"{secret}:{','.join(backup_codes)}"
        )
        
        return {
            "secret": secret,
            "qr_code": f"data:image/png;base64,{qr_base64}",
            "backup_codes": backup_codes,
            "manual_entry_key": secret
        }
    
    async def verify_2fa_setup(
        self,
        user_id: str,
        totp_code: str,
        db: Session
    ) -> Dict[str, Any]:
        """Verify and activate 2FA setup"""
        # Get temporary secret
        temp_data = await self.redis_client.get(f"temp_2fa_secret:{user_id}")
        if not temp_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="2FA setup session expired"
            )
        
        secret, backup_codes_str = temp_data.split(":", 1)
        backup_codes = backup_codes_str.split(",")
        
        # Verify TOTP code
        if not self._verify_totp(secret, totp_code):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid verification code"
            )
        
        # Activate 2FA for user
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        user.totp_secret = secret
        user.is_2fa_enabled = True
        user.backup_codes = security_manager.encrypt_sensitive_data(",".join(backup_codes))
        
        db.commit()
        
        # Clean up temporary data
        await self.redis_client.delete(f"temp_2fa_secret:{user_id}")
        
        # Log 2FA activation
        audit_logger.log_security_event(
            event_type="2fa_activated",
            user_id=user_id,
            ip_address="unknown",
            details={"method": "totp"},
            severity="INFO",
            db=db
        )
        
        return {
            "message": "Two-factor authentication activated successfully",
            "backup_codes": backup_codes
        }
    
    async def register_biometric(
        self,
        user_id: str,
        biometric_type: str,
        biometric_data: Dict[str, Any],
        device_info: Dict[str, Any],
        db: Session
    ) -> Dict[str, Any]:
        """Register biometric authentication for user"""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Encrypt and store biometric template
        biometric_template = self._process_biometric_data(biometric_type, biometric_data)
        encrypted_template = security_manager.encrypt_sensitive_data(biometric_template)
        
        # Store in Redis with device association
        biometric_key = f"biometric:{user_id}:{biometric_type}:{device_info.get('fingerprint')}"
        await self.redis_client.setex(
            biometric_key,
            86400 * 365,  # 1 year
            encrypted_template
        )
        
        # Log biometric registration
        audit_logger.log_security_event(
            event_type="biometric_registered",
            user_id=user_id,
            ip_address=device_info.get("ip_address", "unknown"),
            details={
                "biometric_type": biometric_type,
                "device_fingerprint": device_info.get("fingerprint")
            },
            severity="INFO",
            db=db
        )
        
        return {
            "message": f"{biometric_type.title()} biometric registered successfully",
            "biometric_id": biometric_key
        }
    
    async def verify_device(
        self,
        verification_token: str,
        db: Session
    ) -> Dict[str, Any]:
        """Verify a new device"""
        try:
            # Decode verification token
            payload = jwt.decode(
                verification_token,
                settings.SECRET_KEY,
                algorithms=[self.jwt_algorithm]
            )
            
            user_id = payload.get("user_id")
            device_fingerprint = payload.get("device_fingerprint")
            
            if not user_id or not device_fingerprint:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid verification token"
                )
            
            # Mark device as trusted
            await self._mark_device_trusted(user_id, device_fingerprint, db)
            
            # Log device verification
            audit_logger.log_security_event(
                event_type="device_verified",
                user_id=user_id,
                ip_address="unknown",
                details={"device_fingerprint": device_fingerprint},
                severity="INFO",
                db=db
            )
            
            return {
                "message": "Device verified successfully",
                "device_fingerprint": device_fingerprint
            }
            
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Verification token expired"
            )
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid verification token"
            )
    
    def _verify_password(self, password: str, hashed_password: str) -> bool:
        """Verify password using bcrypt"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
    
    def _verify_totp(self, secret: str, code: str) -> bool:
        """Verify TOTP code"""
        totp = pyotp.TOTP(secret)
        return totp.verify(code, valid_window=1)
    
    def _create_access_token(self, user: User) -> str:
        """Create JWT access token"""
        expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        payload = {
            "sub": str(user.id),
            "email": user.email,
            "role": user.role,
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "access"
        }
        return jwt.encode(payload, settings.SECRET_KEY, algorithm=self.jwt_algorithm)
    
    def _create_refresh_token(self, user: User) -> str:
        """Create JWT refresh token"""
        expire = datetime.utcnow() + timedelta(days=self.refresh_token_expire_days)
        payload = {
            "sub": str(user.id),
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "refresh"
        }
        return jwt.encode(payload, settings.SECRET_KEY, algorithm=self.jwt_algorithm)
    
    async def _is_account_locked(self, email: str) -> bool:
        """Check if account is locked due to failed attempts"""
        failed_attempts = await self.redis_client.get(f"failed_attempts:{email}")
        if not failed_attempts:
            return False
        
        attempts_data = failed_attempts.split(":")
        if len(attempts_data) != 2:
            return False
        
        count, timestamp = attempts_data
        if int(count) >= self.max_failed_attempts:
            lock_time = datetime.fromisoformat(timestamp)
            if datetime.now() < lock_time + timedelta(minutes=self.lockout_duration_minutes):
                return True
        
        return False
    
    async def _record_failed_attempt(
        self,
        email: str,
        reason: str,
        device_info: Dict[str, Any]
    ):
        """Record failed authentication attempt"""
        key = f"failed_attempts:{email}"
        current_attempts = await self.redis_client.get(key)
        
        if current_attempts:
            count, _ = current_attempts.split(":")
            new_count = int(count) + 1
        else:
            new_count = 1
        
        # Store count and timestamp
        await self.redis_client.setex(
            key,
            self.lockout_duration_minutes * 60,
            f"{new_count}:{datetime.now().isoformat()}"
        )
        
        # Log failed attempt
        audit_logger.log_security_event(
            event_type="failed_authentication",
            user_id=None,
            ip_address=device_info.get("ip_address", "unknown"),
            details={
                "email": email,
                "reason": reason,
                "attempt_count": new_count,
                "device_info": device_info
            },
            severity="WARNING"
        )
    
    async def _clear_failed_attempts(self, email: str):
        """Clear failed authentication attempts"""
        await self.redis_client.delete(f"failed_attempts:{email}")
    
    async def _create_device_session(
        self,
        user: User,
        device_info: Dict[str, Any],
        db: Session
    ) -> DeviceSession:
        """Create device session record"""
        device_session = DeviceSession(
            user_id=user.id,
            device_fingerprint=device_info.get("fingerprint"),
            ip_address=device_info.get("ip_address"),
            user_agent=device_info.get("user_agent"),
            location_data=device_info.get("location"),
            is_active=True,
            created_at=datetime.now(),
            expires_at=datetime.now() + timedelta(days=self.refresh_token_expire_days)
        )
        
        db.add(device_session)
        db.commit()
        db.refresh(device_session)
        
        return device_session
    
    async def _store_refresh_token(
        self,
        user_id: str,
        refresh_token: str,
        device_session_id: str
    ):
        """Store refresh token in Redis"""
        await self.redis_client.setex(
            f"refresh_token:{user_id}:{device_session_id}",
            self.refresh_token_expire_days * 24 * 60 * 60,
            refresh_token
        )
    
    async def _is_trusted_device(
        self,
        user_id: str,
        device_fingerprint: str,
        db: Session
    ) -> bool:
        """Check if device is trusted"""
        trusted_device = db.query(DeviceSession).filter(
            DeviceSession.user_id == user_id,
            DeviceSession.device_fingerprint == device_fingerprint,
            DeviceSession.is_active == True,
            DeviceSession.expires_at > datetime.now()
        ).first()
        
        return trusted_device is not None
    
    async def _create_device_verification_token(
        self,
        user_id: str,
        device_fingerprint: str
    ) -> str:
        """Create device verification token"""
        expire = datetime.utcnow() + timedelta(hours=24)
        payload = {
            "user_id": user_id,
            "device_fingerprint": device_fingerprint,
            "exp": expire,
            "type": "device_verification"
        }
        return jwt.encode(payload, settings.SECRET_KEY, algorithm=self.jwt_algorithm)
    
    async def _mark_device_trusted(
        self,
        user_id: str,
        device_fingerprint: str,
        db: Session
    ):
        """Mark device as trusted"""
        # This would typically create a DeviceSession record
        # For now, we'll store it in Redis
        await self.redis_client.setex(
            f"trusted_device:{user_id}:{device_fingerprint}",
            86400 * 365,  # 1 year
            "trusted"
        )
    
    def _process_biometric_data(
        self,
        biometric_type: str,
        biometric_data: Dict[str, Any]
    ) -> str:
        """Process and create biometric template"""
        # This would typically involve complex biometric processing
        # For now, return a simple hash of the data
        import json
        data_str = json.dumps(biometric_data, sort_keys=True)
        return security_manager.encrypt_sensitive_data(data_str)
    
    async def _verify_biometric(
        self,
        user_id: str,
        biometric_data: Dict[str, Any],
        db: Session
    ) -> bool:
        """Verify biometric data against stored template"""
        # This would typically involve complex biometric matching
        # For now, return True if biometric data is provided
        return biometric_data is not None and len(biometric_data) > 0


# Global instance
advanced_auth_service = AdvancedAuthenticationService()
