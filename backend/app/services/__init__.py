"""
Services module for MEDHASAKTHI
"""
from .auth_service import auth_service
from .email_service import email_service
from .ai_question_service import ai_question_generator

__all__ = [
    "auth_service",
    "email_service",
    "ai_question_generator"
]
