"""
Authentication service for user management
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_
import secrets
import json

from app.models.user import (
    User, UserProfile, Institute, Student, Teacher, 
    UserSession, PasswordResetToken, EmailVerificationToken,
    UserRole
)
from app.schemas.auth import (
    UserRegisterSchema, UserLoginSchema, DeviceInfoSchema
)
from app.core.security import security_manager
from app.core.database import session_manager, rate_limiter
from app.core.config import settings
from app.services.email_service import email_service


class AuthService:
    """Authentication service"""
    
    def __init__(self):
        self.security = security_manager
        self.session_manager = session_manager
        self.rate_limiter = rate_limiter
    
    async def register_user(
        self, 
        user_data: UserRegisterSchema, 
        db: Session,
        ip_address: str = None
    ) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """
        Register a new user
        
        Returns:
            (success, message, user_data)
        """
        try:
            # Check rate limiting
            rate_key = f"register:{ip_address or 'unknown'}"
            if not self.rate_limiter.is_allowed(rate_key, 5, 3600):  # 5 per hour
                return False, "Too many registration attempts. Please try again later.", None
            
            # Check if user already exists
            existing_user = db.query(User).filter(User.email == user_data.email).first()
            if existing_user:
                return False, "Email already registered", None
            
            # Validate institute code if required
            institute = None
            if user_data.institute_code:
                institute = db.query(Institute).filter(
                    and_(
                        Institute.code == user_data.institute_code,
                        Institute.is_active == True
                    )
                ).first()
                if not institute:
                    return False, "Invalid institute code", None
            
            # Validate password strength
            password_check = self.security.validate_password_strength(user_data.password)
            if not password_check["is_valid"]:
                return False, f"Password too weak: {', '.join(password_check['errors'])}", None
            
            # Create user
            hashed_password = self.security.hash_password(user_data.password)
            new_user = User(
                email=user_data.email,
                password_hash=hashed_password,
                role=user_data.role.value,
                password_changed_at=datetime.utcnow()
            )
            
            db.add(new_user)
            db.flush()  # Get user ID
            
            # Create user profile
            profile = UserProfile(
                user_id=new_user.id,
                first_name=user_data.first_name,
                last_name=user_data.last_name,
                phone=user_data.phone
            )
            db.add(profile)
            
            # Create role-specific records
            if user_data.role == UserRole.STUDENT and institute:
                student = Student(
                    user_id=new_user.id,
                    institute_id=institute.id,
                    student_id=user_data.student_id,
                    academic_year=str(datetime.now().year)
                )
                db.add(student)
            
            elif user_data.role == UserRole.TEACHER and institute:
                teacher = Teacher(
                    user_id=new_user.id,
                    institute_id=institute.id,
                    employee_id=user_data.employee_id
                )
                db.add(teacher)
            
            # Create email verification token
            verification_token = self.security.generate_verification_token()
            expires_at = datetime.utcnow() + timedelta(hours=24)
            
            email_token = EmailVerificationToken(
                user_id=new_user.id,
                token=verification_token,
                expires_at=expires_at
            )
            db.add(email_token)
            
            db.commit()
            
            # Send verification email
            await email_service.send_verification_email(
                user_data.email,
                user_data.first_name,
                verification_token
            )
            
            return True, "User registered successfully. Please check your email for verification.", {
                "user_id": str(new_user.id),
                "email": new_user.email,
                "role": new_user.role
            }
            
        except Exception as e:
            db.rollback()
            return False, f"Registration failed: {str(e)}", None
    
    async def login_user(
        self,
        login_data: UserLoginSchema,
        db: Session,
        ip_address: str = None,
        user_agent: str = None
    ) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """
        Authenticate user login
        
        Returns:
            (success, message, auth_data)
        """
        try:
            # Check rate limiting
            rate_key = f"login:{login_data.email}"
            if not self.rate_limiter.is_allowed(rate_key, 5, 900):  # 5 attempts per 15 minutes
                return False, "Too many login attempts. Please try again later.", None
            
            # Find user
            user = db.query(User).filter(User.email == login_data.email).first()
            if not user:
                return False, "Invalid credentials", None
            
            # Check if account is locked
            if user.locked_until and user.locked_until > datetime.utcnow():
                return False, "Account temporarily locked due to failed login attempts", None
            
            # Check if user is active
            if not user.is_active:
                return False, "Account is deactivated", None
            
            # Verify password
            if not self.security.verify_password(login_data.password, user.password_hash):
                # Increment failed attempts
                user.failed_login_attempts += 1
                if user.failed_login_attempts >= 5:
                    user.locked_until = datetime.utcnow() + timedelta(minutes=30)
                db.commit()
                return False, "Invalid credentials", None
            
            # Check email verification (skip for institutional students)
            student_profile = None
            if user.role == "student":
                student_profile = db.query(Student).filter(Student.user_id == user.id).first()

            # Skip email verification for institutional students with auto-generated emails
            if not user.is_verified and not (student_profile and student_profile.auto_generated_email):
                return False, "Please verify your email before logging in", None

            # Handle first-time login for institutional students
            if (student_profile and
                not student_profile.first_login_completed and
                student_profile.password_reset_required):

                return False, "password_change_required", {
                    "user_id": str(user.id),
                    "student_id": student_profile.student_id,
                    "institute_name": user.institute.name if user.institute else None,
                    "requires_password_change": True
                }

            # Check 2FA if enabled
            if user.is_2fa_enabled:
                if not login_data.totp_code:
                    return False, "Two-factor authentication code required", None

                if not self.security.verify_totp(login_data.totp_code, user.totp_secret):
                    return False, "Invalid two-factor authentication code", None
            
            # Reset failed attempts and update last login
            user.failed_login_attempts = 0
            user.locked_until = None
            user.last_login = datetime.utcnow()
            
            # Create tokens
            token_data = {"sub": str(user.id), "role": user.role, "email": user.email}
            access_token = self.security.create_access_token(token_data)
            refresh_token = self.security.create_refresh_token({"sub": str(user.id)})
            
            # Create session
            session_token = self.security.generate_session_token()
            expires_at = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
            
            session = UserSession(
                user_id=user.id,
                session_token=session_token,
                refresh_token=refresh_token,
                device_info=json.dumps(login_data.device_info) if login_data.device_info else None,
                user_agent=user_agent,
                ip_address=ip_address,
                expires_at=expires_at
            )
            db.add(session)
            
            # Store session in Redis
            self.session_manager.create_session(
                str(user.id),
                session_token,
                login_data.device_info
            )
            
            db.commit()
            
            # Get user profile
            profile = db.query(UserProfile).filter(UserProfile.user_id == user.id).first()
            
            return True, "Login successful", {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer",
                "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
                "user": {
                    "id": str(user.id),
                    "email": user.email,
                    "role": user.role,
                    "is_verified": user.is_verified,
                    "is_2fa_enabled": user.is_2fa_enabled,
                    "profile": {
                        "first_name": profile.first_name if profile else "",
                        "last_name": profile.last_name if profile else "",
                        "full_name": profile.full_name if profile else ""
                    } if profile else None
                }
            }
            
        except Exception as e:
            db.rollback()
            return False, f"Login failed: {str(e)}", None
    
    async def verify_email(self, token: str, db: Session) -> Tuple[bool, str]:
        """Verify user email with token"""
        try:
            # Find verification token
            email_token = db.query(EmailVerificationToken).filter(
                and_(
                    EmailVerificationToken.token == token,
                    EmailVerificationToken.used == False,
                    EmailVerificationToken.expires_at > datetime.utcnow()
                )
            ).first()
            
            if not email_token:
                return False, "Invalid or expired verification token"
            
            # Update user
            user = db.query(User).filter(User.id == email_token.user_id).first()
            if not user:
                return False, "User not found"
            
            user.is_verified = True
            email_token.used = True
            email_token.used_at = datetime.utcnow()
            
            db.commit()
            
            return True, "Email verified successfully"

        except Exception as e:
            db.rollback()
            return False, f"Email verification failed: {str(e)}"

    async def change_first_login_password(
        self,
        user_id: str,
        current_password: str,
        new_password: str,
        db: Session
    ) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """
        Change password for first-time institutional student login
        """
        try:
            # Find user
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return False, "User not found", None

            # Verify current password
            if not self.security.verify_password(current_password, user.password_hash):
                return False, "Current password is incorrect", None

            # Get student profile
            student_profile = db.query(Student).filter(Student.user_id == user.id).first()
            if not student_profile:
                return False, "Student profile not found", None

            # Validate new password strength
            if len(new_password) < 8:
                return False, "Password must be at least 8 characters long", None

            # Update password
            user.password_hash = self.security.hash_password(new_password)
            student_profile.default_password_changed = True
            student_profile.password_reset_required = False
            student_profile.first_login_completed = True

            db.commit()

            return True, "Password changed successfully", {
                "user_id": str(user.id),
                "student_id": student_profile.student_id
            }

        except Exception as e:
            db.rollback()
            return False, f"Password change failed: {str(e)}", None
    
    async def request_password_reset(
        self, 
        email: str, 
        db: Session,
        ip_address: str = None
    ) -> Tuple[bool, str]:
        """Request password reset"""
        try:
            # Check rate limiting
            rate_key = f"password_reset:{email}"
            if not self.rate_limiter.is_allowed(rate_key, 3, 3600):  # 3 per hour
                return False, "Too many password reset requests. Please try again later."
            
            # Find user
            user = db.query(User).filter(User.email == email).first()
            if not user:
                # Don't reveal if email exists
                return True, "If the email exists, a password reset link has been sent."
            
            # Create reset token
            reset_token = self.security.generate_reset_token()
            expires_at = datetime.utcnow() + timedelta(hours=1)
            
            password_token = PasswordResetToken(
                user_id=user.id,
                token=reset_token,
                expires_at=expires_at,
                ip_address=ip_address
            )
            db.add(password_token)
            db.commit()
            
            # Send reset email
            profile = db.query(UserProfile).filter(UserProfile.user_id == user.id).first()
            await email_service.send_password_reset_email(
                email,
                profile.first_name if profile else "User",
                reset_token
            )
            
            return True, "If the email exists, a password reset link has been sent."
            
        except Exception as e:
            db.rollback()
            return False, f"Password reset request failed: {str(e)}"
    
    async def reset_password(
        self, 
        token: str, 
        new_password: str, 
        db: Session
    ) -> Tuple[bool, str]:
        """Reset password with token"""
        try:
            # Find reset token
            reset_token = db.query(PasswordResetToken).filter(
                and_(
                    PasswordResetToken.token == token,
                    PasswordResetToken.used == False,
                    PasswordResetToken.expires_at > datetime.utcnow()
                )
            ).first()
            
            if not reset_token:
                return False, "Invalid or expired reset token"
            
            # Validate password strength
            password_check = self.security.validate_password_strength(new_password)
            if not password_check["is_valid"]:
                return False, f"Password too weak: {', '.join(password_check['errors'])}"
            
            # Update user password
            user = db.query(User).filter(User.id == reset_token.user_id).first()
            if not user:
                return False, "User not found"
            
            user.password_hash = self.security.hash_password(new_password)
            user.password_changed_at = datetime.utcnow()
            user.failed_login_attempts = 0
            user.locked_until = None
            
            reset_token.used = True
            reset_token.used_at = datetime.utcnow()
            
            # Invalidate all user sessions
            self.session_manager.invalidate_all_user_sessions(str(user.id))
            
            db.commit()
            
            return True, "Password reset successfully"
            
        except Exception as e:
            db.rollback()
            return False, f"Password reset failed: {str(e)}"
    
    def logout_user(self, session_token: str, db: Session) -> Tuple[bool, str]:
        """Logout user and invalidate session"""
        try:
            # Find and invalidate session
            session = db.query(UserSession).filter(
                UserSession.session_token == session_token
            ).first()
            
            if session:
                session.is_active = False
                self.session_manager.invalidate_session(session_token)
                db.commit()
            
            return True, "Logged out successfully"
            
        except Exception as e:
            db.rollback()
            return False, f"Logout failed: {str(e)}"


# Global auth service instance
auth_service = AuthService()
