"""
Two-Factor Authentication Service for MEDHASAKTHI
Implements TOTP, SMS, and Email-based 2FA with backup codes
"""

import secrets
import qrcode
import io
import base64
import pyotp
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from sqlalchemy.orm import Session
import redis

from app.core.database import get_db, get_redis
from app.core.config import settings
from app.models.user import User
from app.services.email_service import EmailService
from app.services.sms_service import SMSService

logger = logging.getLogger(__name__)

class TwoFactorAuthService:
    """Comprehensive Two-Factor Authentication Service"""
    
    def __init__(self):
        self.redis_client = get_redis()
        self.email_service = EmailService()
        self.sms_service = SMSService()
        
        # 2FA Configuration
        self.totp_issuer = "MEDHASAKTHI"
        self.code_validity_minutes = 5
        self.backup_codes_count = 10
        self.max_attempts = 3
        self.lockout_duration_minutes = 30
    
    async def setup_totp(self, user_id: str, db: Session) -> Dict:
        """Setup TOTP (Time-based One-Time Password) for user"""
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                raise ValueError("User not found")
            
            # Generate secret key
            secret = pyotp.random_base32()
            
            # Create TOTP object
            totp = pyotp.TOTP(secret)
            
            # Generate QR code
            provisioning_uri = totp.provisioning_uri(
                name=user.email,
                issuer_name=self.totp_issuer
            )
            
            qr_code_url = await self._generate_qr_code(provisioning_uri)
            
            # Store secret temporarily (user needs to verify before enabling)
            temp_key = f"2fa_setup:{user_id}"
            await self.redis_client.setex(temp_key, 600, secret)  # 10 minutes
            
            # Generate backup codes
            backup_codes = self._generate_backup_codes()
            backup_key = f"2fa_backup_setup:{user_id}"
            await self.redis_client.setex(backup_key, 600, ",".join(backup_codes))
            
            return {
                "qr_code_url": qr_code_url,
                "secret": secret,  # For manual entry
                "backup_codes": backup_codes,
                "setup_token": secrets.token_urlsafe(32)
            }
            
        except Exception as e:
            logger.error(f"Error setting up TOTP for user {user_id}: {e}")
            raise
    
    async def verify_totp_setup(self, user_id: str, code: str, db: Session) -> bool:
        """Verify TOTP setup and enable 2FA"""
        try:
            # Get temporary secret
            temp_key = f"2fa_setup:{user_id}"
            secret = await self.redis_client.get(temp_key)
            
            if not secret:
                return False
            
            # Verify code
            totp = pyotp.TOTP(secret.decode())
            if not totp.verify(code, valid_window=1):
                return False
            
            # Enable 2FA for user
            user = db.query(User).filter(User.id == user_id).first()
            if user:
                user.two_factor_enabled = True
                user.two_factor_secret = secret.decode()
                user.two_factor_method = "totp"
                
                # Store backup codes
                backup_key = f"2fa_backup_setup:{user_id}"
                backup_codes = await self.redis_client.get(backup_key)
                if backup_codes:
                    user.backup_codes = backup_codes.decode()
                
                db.commit()
                
                # Clean up temporary data
                await self.redis_client.delete(temp_key)
                await self.redis_client.delete(backup_key)
                
                # Send confirmation email
                await self.email_service.send_2fa_enabled_notification(user.email, user.name)
                
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error verifying TOTP setup for user {user_id}: {e}")
            return False
    
    async def setup_sms_2fa(self, user_id: str, phone_number: str, db: Session) -> Dict:
        """Setup SMS-based 2FA"""
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                raise ValueError("User not found")
            
            # Generate and send verification code
            verification_code = self._generate_numeric_code()
            
            # Store code temporarily
            code_key = f"2fa_sms_setup:{user_id}"
            await self.redis_client.setex(code_key, 300, verification_code)  # 5 minutes
            
            # Send SMS
            await self.sms_service.send_verification_code(phone_number, verification_code)
            
            return {
                "message": "Verification code sent to your phone",
                "phone_number": phone_number[-4:].rjust(len(phone_number), '*')  # Mask phone number
            }
            
        except Exception as e:
            logger.error(f"Error setting up SMS 2FA for user {user_id}: {e}")
            raise
    
    async def verify_sms_setup(self, user_id: str, code: str, phone_number: str, db: Session) -> bool:
        """Verify SMS setup and enable 2FA"""
        try:
            # Get stored code
            code_key = f"2fa_sms_setup:{user_id}"
            stored_code = await self.redis_client.get(code_key)
            
            if not stored_code or stored_code.decode() != code:
                return False
            
            # Enable SMS 2FA
            user = db.query(User).filter(User.id == user_id).first()
            if user:
                user.two_factor_enabled = True
                user.two_factor_method = "sms"
                user.phone_number = phone_number
                
                # Generate backup codes
                backup_codes = self._generate_backup_codes()
                user.backup_codes = ",".join(backup_codes)
                
                db.commit()
                
                # Clean up
                await self.redis_client.delete(code_key)
                
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error verifying SMS setup for user {user_id}: {e}")
            return False
    
    async def send_2fa_code(self, user_id: str, db: Session) -> Dict:
        """Send 2FA code based on user's preferred method"""
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user or not user.two_factor_enabled:
                raise ValueError("2FA not enabled for user")
            
            # Check for rate limiting
            if await self._is_rate_limited(user_id):
                raise ValueError("Too many 2FA requests. Please wait.")
            
            if user.two_factor_method == "sms":
                return await self._send_sms_code(user)
            elif user.two_factor_method == "email":
                return await self._send_email_code(user)
            else:
                return {"message": "Use your authenticator app to generate code"}
                
        except Exception as e:
            logger.error(f"Error sending 2FA code for user {user_id}: {e}")
            raise
    
    async def verify_2fa_code(self, user_id: str, code: str, db: Session) -> bool:
        """Verify 2FA code"""
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user or not user.two_factor_enabled:
                return False
            
            # Check for lockout
            if await self._is_locked_out(user_id):
                return False
            
            # Verify based on method
            is_valid = False
            
            if user.two_factor_method == "totp":
                is_valid = await self._verify_totp_code(user, code)
            elif user.two_factor_method == "sms":
                is_valid = await self._verify_sms_code(user_id, code)
            elif user.two_factor_method == "email":
                is_valid = await self._verify_email_code(user_id, code)
            
            # Check backup codes if primary method fails
            if not is_valid:
                is_valid = await self._verify_backup_code(user, code, db)
            
            # Handle verification result
            if is_valid:
                await self._clear_failed_attempts(user_id)
                await self._log_successful_2fa(user_id)
            else:
                await self._increment_failed_attempts(user_id)
            
            return is_valid
            
        except Exception as e:
            logger.error(f"Error verifying 2FA code for user {user_id}: {e}")
            return False
    
    async def disable_2fa(self, user_id: str, db: Session) -> bool:
        """Disable 2FA for user"""
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return False
            
            user.two_factor_enabled = False
            user.two_factor_secret = None
            user.two_factor_method = None
            user.backup_codes = None
            
            db.commit()
            
            # Send notification
            await self.email_service.send_2fa_disabled_notification(user.email, user.name)
            
            return True
            
        except Exception as e:
            logger.error(f"Error disabling 2FA for user {user_id}: {e}")
            return False
    
    async def generate_new_backup_codes(self, user_id: str, db: Session) -> List[str]:
        """Generate new backup codes"""
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user or not user.two_factor_enabled:
                raise ValueError("2FA not enabled")
            
            backup_codes = self._generate_backup_codes()
            user.backup_codes = ",".join(backup_codes)
            
            db.commit()
            
            return backup_codes
            
        except Exception as e:
            logger.error(f"Error generating backup codes for user {user_id}: {e}")
            raise
    
    # Private helper methods
    
    async def _generate_qr_code(self, provisioning_uri: str) -> str:
        """Generate QR code as base64 image"""
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(provisioning_uri)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to base64
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        img_str = base64.b64encode(buffer.getvalue()).decode()
        
        return f"data:image/png;base64,{img_str}"
    
    def _generate_backup_codes(self) -> List[str]:
        """Generate backup codes"""
        return [secrets.token_hex(4).upper() for _ in range(self.backup_codes_count)]
    
    def _generate_numeric_code(self, length: int = 6) -> str:
        """Generate numeric verification code"""
        return ''.join([str(secrets.randbelow(10)) for _ in range(length)])
    
    async def _send_sms_code(self, user: User) -> Dict:
        """Send SMS verification code"""
        code = self._generate_numeric_code()
        
        # Store code
        code_key = f"2fa_sms:{user.id}"
        await self.redis_client.setex(code_key, 300, code)  # 5 minutes
        
        # Send SMS
        await self.sms_service.send_2fa_code(user.phone_number, code)
        
        return {"message": "Code sent to your phone"}
    
    async def _send_email_code(self, user: User) -> Dict:
        """Send email verification code"""
        code = self._generate_numeric_code()
        
        # Store code
        code_key = f"2fa_email:{user.id}"
        await self.redis_client.setex(code_key, 300, code)  # 5 minutes
        
        # Send email
        await self.email_service.send_2fa_code(user.email, user.name, code)
        
        return {"message": "Code sent to your email"}
    
    async def _verify_totp_code(self, user: User, code: str) -> bool:
        """Verify TOTP code"""
        if not user.two_factor_secret:
            return False
        
        totp = pyotp.TOTP(user.two_factor_secret)
        return totp.verify(code, valid_window=1)
    
    async def _verify_sms_code(self, user_id: str, code: str) -> bool:
        """Verify SMS code"""
        code_key = f"2fa_sms:{user_id}"
        stored_code = await self.redis_client.get(code_key)
        
        if stored_code and stored_code.decode() == code:
            await self.redis_client.delete(code_key)
            return True
        
        return False
    
    async def _verify_email_code(self, user_id: str, code: str) -> bool:
        """Verify email code"""
        code_key = f"2fa_email:{user_id}"
        stored_code = await self.redis_client.get(code_key)
        
        if stored_code and stored_code.decode() == code:
            await self.redis_client.delete(code_key)
            return True
        
        return False
    
    async def _verify_backup_code(self, user: User, code: str, db: Session) -> bool:
        """Verify backup code"""
        if not user.backup_codes:
            return False
        
        backup_codes = user.backup_codes.split(",")
        
        if code.upper() in backup_codes:
            # Remove used backup code
            backup_codes.remove(code.upper())
            user.backup_codes = ",".join(backup_codes)
            db.commit()
            
            # Alert user about backup code usage
            await self.email_service.send_backup_code_used_alert(user.email, user.name)
            
            return True
        
        return False
    
    async def _is_rate_limited(self, user_id: str) -> bool:
        """Check if user is rate limited"""
        key = f"2fa_rate_limit:{user_id}"
        count = await self.redis_client.get(key)
        
        if count and int(count) >= 5:  # Max 5 requests per hour
            return True
        
        # Increment counter
        await self.redis_client.incr(key)
        await self.redis_client.expire(key, 3600)  # 1 hour
        
        return False
    
    async def _is_locked_out(self, user_id: str) -> bool:
        """Check if user is locked out due to failed attempts"""
        key = f"2fa_lockout:{user_id}"
        return bool(await self.redis_client.get(key))
    
    async def _increment_failed_attempts(self, user_id: str):
        """Increment failed 2FA attempts"""
        key = f"2fa_failed:{user_id}"
        count = await self.redis_client.incr(key)
        await self.redis_client.expire(key, 1800)  # 30 minutes
        
        if count >= self.max_attempts:
            # Lock out user
            lockout_key = f"2fa_lockout:{user_id}"
            await self.redis_client.setex(lockout_key, self.lockout_duration_minutes * 60, "1")
    
    async def _clear_failed_attempts(self, user_id: str):
        """Clear failed attempts counter"""
        key = f"2fa_failed:{user_id}"
        await self.redis_client.delete(key)
    
    async def _log_successful_2fa(self, user_id: str):
        """Log successful 2FA verification"""
        log_key = f"2fa_success:{user_id}:{int(datetime.utcnow().timestamp())}"
        await self.redis_client.setex(log_key, 86400, "1")  # 24 hours
