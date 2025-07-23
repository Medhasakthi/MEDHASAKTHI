"""
Authentication API module
"""
from .routes import router
from .dependencies import (
    get_current_user,
    get_current_active_user,
    get_current_verified_user,
    get_super_admin_user,
    get_institute_admin_user,
    get_teacher_user,
    get_student_user,
    get_parent_user,
    get_current_user_optional,
    get_exam_session_user,
    get_user_institute_context
)

__all__ = [
    "router",
    "get_current_user",
    "get_current_active_user", 
    "get_current_verified_user",
    "get_super_admin_user",
    "get_institute_admin_user",
    "get_teacher_user",
    "get_student_user",
    "get_parent_user",
    "get_current_user_optional",
    "get_exam_session_user",
    "get_user_institute_context"
]
