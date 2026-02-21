"""
Pytest configuration and fixtures for MEDHASAKTHI tests
"""

import pytest
import asyncio
from typing import Generator, AsyncGenerator
from unittest.mock import Mock, AsyncMock

import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from app.main import app
from app.core.database import get_db, Base
from app.core.config import settings
from app.models.user import User, UserProfile
from app.models.institute import Institute
from app.models.subject import Subject
from app.models.exam import Exam, ExamSession
from app.models.question import Question, QuestionType, DifficultyLevel
from app.services.ai_service import AIService
from app.services.proctoring_service import ProctoringService
from app.services.notification_service import NotificationService

# Test database URL
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

# Create test engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="function")
def db_session() -> Generator[Session, None, None]:
    """Create a fresh database session for each test."""
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Create session
    session = TestingSessionLocal()
    
    try:
        yield session
    finally:
        session.close()
        # Drop all tables after test
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db_session: Session) -> Generator[TestClient, None, None]:
    """Create a test client with database dependency override."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()

@pytest.fixture
def sample_user(db_session: Session) -> User:
    """Create a sample user for testing."""
    user = User(
        email="test@example.com",
        hashed_password="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # "secret"
        role="student",
        is_active=True,
        is_verified=True
    )
    
    profile = UserProfile(
        first_name="Test",
        last_name="User",
        phone="+1234567890"
    )
    user.profile = profile
    
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    
    return user

@pytest.fixture
def sample_admin_user(db_session: Session) -> User:
    """Create a sample admin user for testing."""
    user = User(
        email="admin@example.com",
        hashed_password="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # "secret"
        role="admin",
        is_active=True,
        is_verified=True
    )
    
    profile = UserProfile(
        first_name="Admin",
        last_name="User",
        phone="+1234567890"
    )
    user.profile = profile
    
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    
    return user

@pytest.fixture
def sample_institute(db_session: Session, sample_admin_user: User) -> Institute:
    """Create a sample institute for testing."""
    institute = Institute(
        name="Test Institute",
        code="TEST001",
        admin_user_id=sample_admin_user.id,
        description="A test institute",
        email="contact@testinstitute.edu",
        phone="+1234567890",
        subscription_plan="premium",
        max_students=1000,
        max_teachers=50,
        is_active=True,
        is_verified=True
    )
    
    db_session.add(institute)
    db_session.commit()
    db_session.refresh(institute)
    
    return institute

@pytest.fixture
def sample_subject(db_session: Session, sample_institute: Institute) -> Subject:
    """Create a sample subject for testing."""
    subject = Subject(
        name="Mathematics",
        code="MATH101",
        description="Basic Mathematics",
        institute_id=sample_institute.id
    )
    
    db_session.add(subject)
    db_session.commit()
    db_session.refresh(subject)
    
    return subject

@pytest.fixture
def sample_question(db_session: Session, sample_subject: Subject) -> Question:
    """Create a sample question for testing."""
    question = Question(
        question_text="What is 2 + 2?",
        question_type=QuestionType.MULTIPLE_CHOICE,
        difficulty_level=DifficultyLevel.BEGINNER,
        subject_id=sample_subject.id,
        options=[
            {"id": "A", "text": "3", "is_correct": False},
            {"id": "B", "text": "4", "is_correct": True},
            {"id": "C", "text": "5", "is_correct": False},
            {"id": "D", "text": "6", "is_correct": False}
        ],
        correct_answer="B",
        explanation="2 + 2 equals 4",
        estimated_time=1,
        points=1
    )
    
    db_session.add(question)
    db_session.commit()
    db_session.refresh(question)
    
    return question

@pytest.fixture
def sample_exam(db_session: Session, sample_institute: Institute, sample_subject: Subject) -> Exam:
    """Create a sample exam for testing."""
    exam = Exam(
        title="Test Exam",
        description="A test examination",
        institute_id=sample_institute.id,
        subject_id=sample_subject.id,
        duration_minutes=60,
        total_points=100,
        passing_score=60,
        is_proctored=True,
        is_active=True
    )
    
    db_session.add(exam)
    db_session.commit()
    db_session.refresh(exam)
    
    return exam

@pytest.fixture
def sample_exam_session(
    db_session: Session, 
    sample_exam: Exam, 
    sample_user: User
) -> ExamSession:
    """Create a sample exam session for testing."""
    session = ExamSession(
        exam_id=sample_exam.id,
        student_id=sample_user.id,
        status="IN_PROGRESS"
    )
    
    db_session.add(session)
    db_session.commit()
    db_session.refresh(session)
    
    return session

@pytest.fixture
def mock_ai_service() -> Mock:
    """Create a mock AI service for testing."""
    mock_service = Mock(spec=AIService)
    mock_service.generate_questions = AsyncMock()
    mock_service.validate_question = AsyncMock()
    mock_service.estimate_difficulty = AsyncMock()
    return mock_service

@pytest.fixture
def mock_proctoring_service() -> Mock:
    """Create a mock proctoring service for testing."""
    mock_service = Mock(spec=ProctoringService)
    mock_service.start_proctoring_session = AsyncMock()
    mock_service.stop_proctoring_session = AsyncMock()
    mock_service.process_video_frame = AsyncMock()
    mock_service.handle_browser_event = AsyncMock()
    return mock_service

@pytest.fixture
def mock_notification_service() -> Mock:
    """Create a mock notification service for testing."""
    mock_service = Mock(spec=NotificationService)
    mock_service.send_email = AsyncMock()
    mock_service.send_sms = AsyncMock()
    mock_service.send_push_notification = AsyncMock()
    mock_service.send_real_time_notification = AsyncMock()
    return mock_service

@pytest.fixture
def auth_headers(sample_user: User) -> dict:
    """Create authentication headers for testing."""
    # This would normally create a JWT token
    # For testing, we'll use a mock token
    return {"Authorization": "Bearer test_token"}

@pytest.fixture
def admin_auth_headers(sample_admin_user: User) -> dict:
    """Create admin authentication headers for testing."""
    return {"Authorization": "Bearer admin_test_token"}

@pytest.fixture
def mock_openai_response():
    """Mock OpenAI API response for testing."""
    return {
        "questions": [
            {
                "question_text": "What is the derivative of x²?",
                "question_type": "multiple_choice",
                "options": [
                    {"id": "A", "text": "x", "is_correct": False},
                    {"id": "B", "text": "2x", "is_correct": True},
                    {"id": "C", "text": "x²", "is_correct": False},
                    {"id": "D", "text": "2", "is_correct": False}
                ],
                "correct_answer": "B",
                "explanation": "Using the power rule: d/dx(x^n) = nx^(n-1)",
                "difficulty_level": "intermediate",
                "estimated_time": 3,
                "points": 2
            }
        ],
        "generation_metadata": {
            "model_used": "gpt-4",
            "tokens_used": 150,
            "generation_time": 2.5,
            "cost": 0.003
        }
    }

@pytest.fixture
def mock_websocket():
    """Create a mock WebSocket for testing."""
    websocket = Mock()
    websocket.accept = AsyncMock()
    websocket.send_text = AsyncMock()
    websocket.receive_text = AsyncMock()
    websocket.close = AsyncMock()
    return websocket

# Async fixtures
@pytest_asyncio.fixture
async def async_client(db_session: Session) -> AsyncGenerator:
    """Create an async test client."""
    from httpx import AsyncClient
    
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()

# Markers for different test types
pytest.mark.unit = pytest.mark.unit
pytest.mark.integration = pytest.mark.integration
pytest.mark.e2e = pytest.mark.e2e
pytest.mark.slow = pytest.mark.slow

# Test configuration
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "unit: mark test as a unit test")
    config.addinivalue_line("markers", "integration: mark test as an integration test")
    config.addinivalue_line("markers", "e2e: mark test as an end-to-end test")
    config.addinivalue_line("markers", "slow: mark test as slow running")

def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers based on file location."""
    for item in items:
        # Add unit marker to tests in test_* files
        if "test_" in item.nodeid and "/unit/" not in item.nodeid:
            item.add_marker(pytest.mark.unit)
        
        # Add integration marker to tests in integration/ directory
        if "/integration/" in item.nodeid:
            item.add_marker(pytest.mark.integration)
        
        # Add e2e marker to tests in e2e/ directory
        if "/e2e/" in item.nodeid:
            item.add_marker(pytest.mark.e2e)
        
        # Add slow marker to tests that might be slow
        if any(keyword in item.nodeid for keyword in ["ai_service", "proctoring", "websocket"]):
            item.add_marker(pytest.mark.slow)
