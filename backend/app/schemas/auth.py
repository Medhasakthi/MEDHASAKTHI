"""
Pydantic schemas for authentication
"""
from pydantic import BaseModel, EmailStr, validator, Field
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum

from app.models.user import UserRole


class UserRegisterSchema(BaseModel):
    """Schema for user registration"""
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    confirm_password: str
    role: UserRole
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    
    # Institute-specific fields
    institute_code: Optional[str] = Field(None, max_length=50)  # Required for students/teachers
    student_id: Optional[str] = Field(None, max_length=50)  # Required for students
    employee_id: Optional[str] = Field(None, max_length=50)  # Required for teachers
    
    @validator('confirm_password')
    def passwords_match(cls, v, values, **kwargs):
        if 'password' in values and v != values['password']:
            raise ValueError('Passwords do not match')
        return v
    
    @validator('role')
    def validate_role(cls, v):
        if v not in UserRole:
            raise ValueError('Invalid user role')
        return v
    
    @validator('institute_code')
    def validate_institute_code(cls, v, values, **kwargs):
        role = values.get('role')
        if role in [UserRole.STUDENT, UserRole.TEACHER, UserRole.PARENT] and not v:
            raise ValueError('Institute code is required for students, teachers, and parents')
        return v
    
    @validator('student_id')
    def validate_student_id(cls, v, values, **kwargs):
        role = values.get('role')
        if role == UserRole.STUDENT and not v:
            raise ValueError('Student ID is required for students')
        return v
    
    @validator('employee_id')
    def validate_employee_id(cls, v, values, **kwargs):
        role = values.get('role')
        if role == UserRole.TEACHER and not v:
            raise ValueError('Employee ID is required for teachers')
        return v


class UserLoginSchema(BaseModel):
    """Schema for user login"""
    email: EmailStr
    password: str
    totp_code: Optional[str] = Field(None, min_length=6, max_length=6)
    remember_me: bool = False
    device_info: Optional[Dict[str, Any]] = None


class TokenResponseSchema(BaseModel):
    """Schema for token response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: "UserResponseSchema"


class RefreshTokenSchema(BaseModel):
    """Schema for token refresh"""
    refresh_token: str


class PasswordResetRequestSchema(BaseModel):
    """Schema for password reset request"""
    email: EmailStr


class PasswordResetSchema(BaseModel):
    """Schema for password reset"""
    token: str
    new_password: str = Field(..., min_length=8, max_length=128)
    confirm_password: str
    
    @validator('confirm_password')
    def passwords_match(cls, v, values, **kwargs):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('Passwords do not match')
        return v


class PasswordChangeSchema(BaseModel):
    """Schema for password change (authenticated user)"""
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=128)
    confirm_password: str
    
    @validator('confirm_password')
    def passwords_match(cls, v, values, **kwargs):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('Passwords do not match')
        return v


class EmailVerificationSchema(BaseModel):
    """Schema for email verification"""
    token: str


class TwoFactorSetupSchema(BaseModel):
    """Schema for 2FA setup"""
    totp_code: str = Field(..., min_length=6, max_length=6)


class TwoFactorDisableSchema(BaseModel):
    """Schema for 2FA disable"""
    password: str
    totp_code: str = Field(..., min_length=6, max_length=6)


class UserResponseSchema(BaseModel):
    """Schema for user response"""
    id: str
    email: str
    role: str
    is_active: bool
    is_verified: bool
    is_2fa_enabled: bool
    created_at: datetime
    last_login: Optional[datetime]
    profile: Optional["UserProfileResponseSchema"] = None
    
    class Config:
        from_attributes = True


class UserProfileResponseSchema(BaseModel):
    """Schema for user profile response"""
    first_name: str
    last_name: str
    phone: Optional[str]
    profile_picture_url: Optional[str]
    timezone: str
    language: str
    
    class Config:
        from_attributes = True


class UserSessionResponseSchema(BaseModel):
    """Schema for user session response"""
    id: str
    device_info: Optional[str]
    ip_address: Optional[str]
    location: Optional[str]
    is_active: bool
    created_at: datetime
    last_activity: datetime
    expires_at: datetime
    
    class Config:
        from_attributes = True


class PasswordStrengthResponseSchema(BaseModel):
    """Schema for password strength response"""
    is_valid: bool
    errors: list[str]
    strength: str


class AuthStatusResponseSchema(BaseModel):
    """Schema for authentication status"""
    is_authenticated: bool
    user: Optional[UserResponseSchema] = None
    session_expires_at: Optional[datetime] = None


class LogoutResponseSchema(BaseModel):
    """Schema for logout response"""
    message: str
    logged_out_sessions: int


class BulkUserRegistrationSchema(BaseModel):
    """Schema for bulk user registration (CSV upload)"""
    institute_code: str
    users: list[Dict[str, Any]]
    send_welcome_email: bool = True
    auto_generate_passwords: bool = True


class UserUpdateSchema(BaseModel):
    """Schema for user profile update"""
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    timezone: Optional[str] = Field(None, max_length=50)
    language: Optional[str] = Field(None, max_length=10)
    bio: Optional[str] = Field(None, max_length=500)


class DeviceInfoSchema(BaseModel):
    """Schema for device information"""
    device_type: str  # mobile, desktop, tablet
    os: str  # iOS, Android, Windows, macOS, Linux
    browser: str  # Chrome, Safari, Firefox, etc.
    app_version: Optional[str] = None
    device_id: Optional[str] = None


class SecurityEventSchema(BaseModel):
    """Schema for security events"""
    event_type: str  # login, logout, password_change, 2fa_enable, etc.
    ip_address: str
    user_agent: str
    location: Optional[str] = None
    success: bool
    details: Optional[Dict[str, Any]] = None


# Update forward references
TokenResponseSchema.model_rebuild()
UserResponseSchema.model_rebuild()
