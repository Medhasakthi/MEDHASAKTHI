"""
Database models for MEDHASAKTHI
"""
from .user import (
    User,
    UserProfile,
    Institute,
    InstituteType,
    Student,
    Teacher,
    UserSession,
    PasswordResetToken,
    EmailVerificationToken,
    UserRole,
    SubscriptionPlan
)
from .question import (
    Subject,
    Topic,
    Question,
    QuestionBank,
    QuestionBankQuestion,
    AIQuestionGeneration,
    QuestionFeedback,
    QuestionType,
    DifficultyLevel,
    QuestionStatus
)
from .certificate import (
    CertificateTemplate,
    Certificate,
    CertificateGeneration,
    CertificateType,
    CertificateStatus,
    ProfessionCategory
)
from .talent_exam import (
    TalentExam,
    TalentExamRegistration,
    ExamCenter,
    TalentExamSession,
    TalentExamNotification,
    ExamStatus,
    RegistrationStatus,
    ExamType,
    ClassLevel
)
from .school_education import (
    SchoolSubject,
    SchoolTopic,
    SchoolCurriculum,
    SchoolAcademicYear,
    SchoolGradingSystem,
    EducationBoard,
    EducationLevel,
    Stream,
    MediumOfInstruction
)

__all__ = [
    "User",
    "UserProfile",
    "Institute",
    "InstituteType",
    "Student",
    "Teacher",
    "UserSession",
    "PasswordResetToken",
    "EmailVerificationToken",
    "UserRole",
    "SubscriptionPlan",
    "Subject",
    "Topic",
    "Question",
    "QuestionBank",
    "QuestionBankQuestion",
    "AIQuestionGeneration",
    "QuestionFeedback",
    "QuestionType",
    "DifficultyLevel",
    "QuestionStatus",
    "CertificateTemplate",
    "Certificate",
    "CertificateGeneration",
    "CertificateType",
    "CertificateStatus",
    "ProfessionCategory",
    "TalentExam",
    "TalentExamRegistration",
    "ExamCenter",
    "TalentExamSession",
    "TalentExamNotification",
    "ExamStatus",
    "RegistrationStatus",
    "ExamType",
    "ClassLevel",

    # School Education models
    "SchoolSubject",
    "SchoolTopic",
    "SchoolCurriculum",
    "SchoolAcademicYear",
    "SchoolGradingSystem",
    "EducationBoard",
    "EducationLevel",
    "Stream",
    "MediumOfInstruction"
]
