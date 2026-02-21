"""
Authentication dependencies for FastAPI
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.core.security import security_manager
from app.models.user import User, UserRole

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Verify token
        payload = security_manager.verify_token(credentials.credentials)
        if payload is None:
            raise credentials_exception
        
        # Get user ID from token
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        
        # Get user from database
        user = db.query(User).filter(User.id == user_id).first()
        if user is None:
            raise credentials_exception
        
        return user
        
    except Exception:
        raise credentials_exception


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current active user"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user


async def get_current_verified_user(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """Get current verified user"""
    if not current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email not verified"
        )
    return current_user


# Role-based dependencies
async def get_super_admin_user(
    current_user: User = Depends(get_current_verified_user)
) -> User:
    """Require super admin role"""
    if current_user.role != UserRole.SUPER_ADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Super admin access required"
        )
    return current_user


async def get_institute_admin_user(
    current_user: User = Depends(get_current_verified_user)
) -> User:
    """Require institute admin role or higher"""
    allowed_roles = [UserRole.SUPER_ADMIN.value, UserRole.INSTITUTE_ADMIN.value]
    if current_user.role not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Institute admin access required"
        )
    return current_user


async def get_teacher_user(
    current_user: User = Depends(get_current_verified_user)
) -> User:
    """Require teacher role or higher"""
    allowed_roles = [
        UserRole.SUPER_ADMIN.value,
        UserRole.INSTITUTE_ADMIN.value,
        UserRole.TEACHER.value
    ]
    if current_user.role not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Teacher access required"
        )
    return current_user


async def get_teacher_user(
    current_user: User = Depends(get_current_verified_user)
) -> User:
    """Require teacher role"""
    if current_user.role != UserRole.TEACHER.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Teacher access required"
        )
    return current_user


async def get_student_user(
    current_user: User = Depends(get_current_verified_user)
) -> User:
    """Require student role"""
    if current_user.role != UserRole.STUDENT.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Student access required"
        )
    return current_user


async def get_parent_user(
    current_user: User = Depends(get_current_verified_user)
) -> User:
    """Require parent role"""
    if current_user.role != UserRole.PARENT.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Parent access required"
        )
    return current_user


# Optional authentication (for public endpoints that can benefit from user context)
async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """Get current user if authenticated, None otherwise"""
    if credentials is None:
        return None
    
    try:
        payload = security_manager.verify_token(credentials.credentials)
        if payload is None:
            return None
        
        user_id: str = payload.get("sub")
        if user_id is None:
            return None
        
        user = db.query(User).filter(User.id == user_id).first()
        if user is None or not user.is_active:
            return None
        
        return user
        
    except Exception:
        return None


# Exam-specific dependencies
async def get_exam_session_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> dict:
    """Get user from exam session token"""
    try:
        # Verify exam session token
        payload = security_manager.verify_exam_session_token(credentials.credentials)
        if payload is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid exam session token"
            )
        
        # Get user
        user_id = payload.get("user_id")
        user = db.query(User).filter(User.id == user_id).first()
        if user is None or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid user"
            )
        
        return {
            "user": user,
            "exam_id": payload.get("exam_id"),
            "institute_id": payload.get("institute_id"),
            "session_data": payload
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid exam session"
        )


# Rate limiting dependency
def check_rate_limit(key: str, limit: int = 60, window: int = 60):
    """Rate limiting dependency factory"""
    def rate_limit_dependency():
        from app.core.database import rate_limiter
        if not rate_limiter.is_allowed(key, limit, window):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded"
            )
        return True
    return rate_limit_dependency


# Institute context dependency
async def get_user_institute_context(
    current_user: User = Depends(get_current_verified_user),
    db: Session = Depends(get_db)
) -> dict:
    """Get user's institute context"""
    from app.models.user import Student, Teacher, Institute
    
    context = {
        "user": current_user,
        "institute": None,
        "role_data": None
    }
    
    if current_user.role == UserRole.STUDENT.value:
        student = db.query(Student).filter(Student.user_id == current_user.id).first()
        if student:
            institute = db.query(Institute).filter(Institute.id == student.institute_id).first()
            context["institute"] = institute
            context["role_data"] = student
    
    elif current_user.role == UserRole.TEACHER.value:
        teacher = db.query(Teacher).filter(Teacher.user_id == current_user.id).first()
        if teacher:
            institute = db.query(Institute).filter(Institute.id == teacher.institute_id).first()
            context["institute"] = institute
            context["role_data"] = teacher
    
    elif current_user.role == UserRole.INSTITUTE_ADMIN.value:
        institute = db.query(Institute).filter(Institute.admin_user_id == current_user.id).first()
        context["institute"] = institute
    
    return context
