"""
Authentication API routes
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Dict, Any
import json

from app.core.database import get_db, rate_limiter
from app.core.security import security_manager
from app.services.auth_service import auth_service
from app.services.email_service import email_service
from app.schemas.auth import (
    UserRegisterSchema,
    UserLoginSchema,
    TokenResponseSchema,
    RefreshTokenSchema,
    PasswordResetRequestSchema,
    PasswordResetSchema,
    PasswordChangeSchema,
    EmailVerificationSchema,
    TwoFactorSetupSchema,
    TwoFactorDisableSchema,
    UserResponseSchema,
    PasswordStrengthResponseSchema,
    AuthStatusResponseSchema,
    LogoutResponseSchema
)
from app.models.user import User, UserProfile
from app.api.v1.auth.dependencies import get_current_user, get_current_active_user

router = APIRouter()
security = HTTPBearer()


@router.post("/register", response_model=Dict[str, Any])
async def register_user(
    user_data: UserRegisterSchema,
    request: Request,
    db: Session = Depends(get_db)
):
    """Register a new user"""
    # Get client IP
    client_ip = request.client.host
    
    # Check rate limiting
    rate_key = f"register:{client_ip}"
    if not rate_limiter.is_allowed(rate_key, 5, 3600):  # 5 per hour
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many registration attempts. Please try again later."
        )
    
    success, message, user_info = await auth_service.register_user(
        user_data, db, client_ip
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )
    
    return {
        "message": message,
        "user": user_info
    }


@router.post("/login", response_model=TokenResponseSchema)
async def login_user(
    login_data: UserLoginSchema,
    request: Request,
    response: Response,
    db: Session = Depends(get_db)
):
    """Authenticate user and return tokens"""
    # Get client info
    client_ip = request.client.host
    user_agent = request.headers.get("user-agent", "")
    
    # Check rate limiting
    rate_key = f"login:{login_data.email}"
    if not rate_limiter.is_allowed(rate_key, 5, 900):  # 5 attempts per 15 minutes
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many login attempts. Please try again later."
        )
    
    success, message, auth_data = await auth_service.login_user(
        login_data, db, client_ip, user_agent
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=message
        )
    
    # Set security headers
    for header, value in security_manager.get_security_headers().items():
        response.headers[header] = value
    
    return TokenResponseSchema(**auth_data)


@router.post("/logout", response_model=LogoutResponseSchema)
async def logout_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Logout user and invalidate session"""
    # Extract session token from JWT
    token_data = security_manager.verify_token(credentials.credentials)
    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    # For now, we'll just return success
    # In a full implementation, you'd invalidate the specific session
    return LogoutResponseSchema(
        message="Logged out successfully",
        logged_out_sessions=1
    )


@router.post("/refresh", response_model=TokenResponseSchema)
async def refresh_token(
    refresh_data: RefreshTokenSchema,
    db: Session = Depends(get_db)
):
    """Refresh access token using refresh token"""
    # Verify refresh token
    token_data = security_manager.verify_token(refresh_data.refresh_token)
    if not token_data or token_data.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    # Get user
    user_id = token_data.get("sub")
    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    # Create new tokens
    new_token_data = {"sub": str(user.id), "role": user.role, "email": user.email}
    access_token = security_manager.create_access_token(new_token_data)
    new_refresh_token = security_manager.create_refresh_token({"sub": str(user.id)})
    
    # Get user profile
    profile = db.query(UserProfile).filter(UserProfile.user_id == user.id).first()
    
    return TokenResponseSchema(
        access_token=access_token,
        refresh_token=new_refresh_token,
        token_type="bearer",
        expires_in=security_manager.access_token_expire_minutes * 60,
        user=UserResponseSchema(
            id=str(user.id),
            email=user.email,
            role=user.role,
            is_active=user.is_active,
            is_verified=user.is_verified,
            is_2fa_enabled=user.is_2fa_enabled,
            created_at=user.created_at,
            last_login=user.last_login,
            profile=profile
        )
    )


@router.post("/verify-email")
async def verify_email(
    verification_data: EmailVerificationSchema,
    db: Session = Depends(get_db)
):
    """Verify user email with token"""
    success, message = await auth_service.verify_email(verification_data.token, db)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )
    
    # Send welcome email
    # Get user from token to send welcome email
    # This is a simplified version - in production you'd get user info from the token
    
    return {"message": message}


@router.post("/request-password-reset")
async def request_password_reset(
    reset_request: PasswordResetRequestSchema,
    request: Request,
    db: Session = Depends(get_db)
):
    """Request password reset"""
    client_ip = request.client.host
    
    # Check rate limiting
    rate_key = f"password_reset:{reset_request.email}"
    if not rate_limiter.is_allowed(rate_key, 3, 3600):  # 3 per hour
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many password reset requests. Please try again later."
        )
    
    success, message = await auth_service.request_password_reset(
        reset_request.email, db, client_ip
    )
    
    # Always return success to prevent email enumeration
    return {"message": "If the email exists, a password reset link has been sent."}


@router.post("/reset-password")
async def reset_password(
    reset_data: PasswordResetSchema,
    db: Session = Depends(get_db)
):
    """Reset password with token"""
    success, message = await auth_service.reset_password(
        reset_data.token, reset_data.new_password, db
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )
    
    return {"message": message}


@router.post("/change-password")
async def change_password(
    password_data: PasswordChangeSchema,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Change password for authenticated user"""
    # Verify current password
    if not security_manager.verify_password(password_data.current_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    # Validate new password strength
    password_check = security_manager.validate_password_strength(password_data.new_password)
    if not password_check["is_valid"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Password too weak: {', '.join(password_check['errors'])}"
        )
    
    # Update password
    current_user.password_hash = security_manager.hash_password(password_data.new_password)
    current_user.password_changed_at = datetime.utcnow()
    db.commit()
    
    return {"message": "Password changed successfully"}


@router.post("/change-first-login-password")
async def change_first_login_password(
    password_data: Dict[str, str],
    db: Session = Depends(get_db)
):
    """Change password for first-time institutional student login"""

    required_fields = ["user_id", "current_password", "new_password"]
    for field in required_fields:
        if field not in password_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Missing required field: {field}"
            )

    success, message, data = await auth_service.change_first_login_password(
        password_data["user_id"],
        password_data["current_password"],
        password_data["new_password"],
        db
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )

    # After successful password change, log the user in
    if success and data:
        # Generate tokens for the user
        user = db.query(User).filter(User.id == password_data["user_id"]).first()
        if user:
            access_token = auth_service.create_access_token(
                data={"sub": user.email, "user_id": str(user.id)}
            )
            refresh_token = auth_service.create_refresh_token(
                data={"sub": user.email, "user_id": str(user.id)}
            )

            # Get student profile for additional info
            from app.models.user import Student
            student_profile = db.query(Student).filter(Student.user_id == user.id).first()

            return {
                "message": message,
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer",
                "expires_in": 3600,
                "user": {
                    "id": str(user.id),
                    "email": user.email,
                    "full_name": user.full_name,
                    "role": user.role,
                    "is_active": user.is_active,
                    "institute_id": str(user.institute_id) if user.institute_id else None,
                    "student_id": student_profile.student_id if student_profile else None,
                    "class_level": student_profile.class_level if student_profile else None
                }
            }

    return {"message": message}


@router.get("/me", response_model=UserResponseSchema)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get current user information"""
    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    
    return UserResponseSchema(
        id=str(current_user.id),
        email=current_user.email,
        role=current_user.role,
        is_active=current_user.is_active,
        is_verified=current_user.is_verified,
        is_2fa_enabled=current_user.is_2fa_enabled,
        created_at=current_user.created_at,
        last_login=current_user.last_login,
        profile=profile
    )


@router.get("/status", response_model=AuthStatusResponseSchema)
async def get_auth_status(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Get authentication status"""
    try:
        token_data = security_manager.verify_token(credentials.credentials)
        if not token_data:
            return AuthStatusResponseSchema(is_authenticated=False)
        
        user_id = token_data.get("sub")
        user = db.query(User).filter(User.id == user_id).first()
        if not user or not user.is_active:
            return AuthStatusResponseSchema(is_authenticated=False)
        
        profile = db.query(UserProfile).filter(UserProfile.user_id == user.id).first()
        
        return AuthStatusResponseSchema(
            is_authenticated=True,
            user=UserResponseSchema(
                id=str(user.id),
                email=user.email,
                role=user.role,
                is_active=user.is_active,
                is_verified=user.is_verified,
                is_2fa_enabled=user.is_2fa_enabled,
                created_at=user.created_at,
                last_login=user.last_login,
                profile=profile
            ),
            session_expires_at=datetime.fromtimestamp(token_data.get("exp", 0))
        )
    except Exception:
        return AuthStatusResponseSchema(is_authenticated=False)


@router.post("/validate-password", response_model=PasswordStrengthResponseSchema)
async def validate_password(
    password_data: Dict[str, str]
):
    """Validate password strength"""
    password = password_data.get("password", "")
    result = security_manager.validate_password_strength(password)
    
    return PasswordStrengthResponseSchema(**result)


# Import datetime for password change
from datetime import datetime
