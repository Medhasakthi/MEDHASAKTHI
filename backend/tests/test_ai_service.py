"""
Comprehensive tests for AI Service
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from sqlalchemy.orm import Session

from app.services.ai_service import AIService
from app.models.question import Question, QuestionType, DifficultyLevel
from app.models.subject import Subject
from app.core.database import get_db

class TestAIService:
    """Test suite for AI Service"""
    
    @pytest.fixture
    def ai_service(self):
        """Create AI service instance for testing"""
        return AIService()
    
    @pytest.fixture
    def mock_db(self):
        """Mock database session"""
        return Mock(spec=Session)
    
    @pytest.fixture
    def sample_subject(self):
        """Sample subject for testing"""
        return Subject(
            id="subject-1",
            name="Mathematics",
            code="MATH",
            description="Mathematics subject"
        )
    
    @pytest.fixture
    def sample_question_request(self):
        """Sample question generation request"""
        return {
            "subject_id": "subject-1",
            "topic_id": "topic-1",
            "question_type": QuestionType.MULTIPLE_CHOICE,
            "difficulty_level": DifficultyLevel.INTERMEDIATE,
            "count": 5,
            "grade_level": "10",
            "learning_objective": "Solve quadratic equations",
            "context": "Algebra chapter"
        }
    
    @pytest.mark.asyncio
    async def test_generate_questions_success(self, ai_service, mock_db, sample_question_request):
        """Test successful question generation"""
        # Mock OpenAI response
        mock_response = {
            "questions": [
                {
                    "question_text": "What is the solution to x² + 5x + 6 = 0?",
                    "options": [
                        {"id": "A", "text": "x = -2, -3", "is_correct": True},
                        {"id": "B", "text": "x = 2, 3", "is_correct": False},
                        {"id": "C", "text": "x = -1, -6", "is_correct": False},
                        {"id": "D", "text": "x = 1, 6", "is_correct": False}
                    ],
                    "explanation": "Factor the quadratic equation",
                    "difficulty_level": "intermediate",
                    "estimated_time": 3
                }
            ]
        }
        
        with patch.object(ai_service, '_call_openai_api', return_value=mock_response):
            result = await ai_service.generate_questions(sample_question_request, mock_db)
            
            assert result["success"] is True
            assert len(result["questions"]) == 1
            assert result["questions_generated"] == 1
            assert "generation_time" in result
    
    @pytest.mark.asyncio
    async def test_generate_questions_api_failure(self, ai_service, mock_db, sample_question_request):
        """Test question generation with API failure"""
        with patch.object(ai_service, '_call_openai_api', side_effect=Exception("API Error")):
            result = await ai_service.generate_questions(sample_question_request, mock_db)
            
            assert result["success"] is False
            assert "error" in result
            assert result["questions_generated"] == 0
    
    @pytest.mark.asyncio
    async def test_validate_question_content_valid(self, ai_service):
        """Test question content validation with valid question"""
        question_data = {
            "question_text": "What is 2 + 2?",
            "options": [
                {"id": "A", "text": "3", "is_correct": False},
                {"id": "B", "text": "4", "is_correct": True},
                {"id": "C", "text": "5", "is_correct": False},
                {"id": "D", "text": "6", "is_correct": False}
            ],
            "explanation": "Basic addition"
        }
        
        is_valid, errors = await ai_service._validate_question_content(question_data)
        
        assert is_valid is True
        assert len(errors) == 0
    
    @pytest.mark.asyncio
    async def test_validate_question_content_invalid(self, ai_service):
        """Test question content validation with invalid question"""
        question_data = {
            "question_text": "",  # Empty question text
            "options": [
                {"id": "A", "text": "3", "is_correct": True},
                {"id": "B", "text": "4", "is_correct": True},  # Multiple correct answers
            ],
            "explanation": ""  # Empty explanation
        }
        
        is_valid, errors = await ai_service._validate_question_content(question_data)
        
        assert is_valid is False
        assert len(errors) > 0
        assert any("question_text" in error for error in errors)
        assert any("multiple correct answers" in error for error in errors)
    
    @pytest.mark.asyncio
    async def test_estimate_difficulty_easy(self, ai_service):
        """Test difficulty estimation for easy question"""
        question_text = "What is 1 + 1?"
        
        with patch.object(ai_service, '_analyze_text_complexity', return_value=0.2):
            difficulty = await ai_service._estimate_difficulty(question_text)
            assert difficulty == DifficultyLevel.BEGINNER
    
    @pytest.mark.asyncio
    async def test_estimate_difficulty_hard(self, ai_service):
        """Test difficulty estimation for hard question"""
        question_text = "Solve the differential equation dy/dx + 2y = e^(-x)"
        
        with patch.object(ai_service, '_analyze_text_complexity', return_value=0.9):
            difficulty = await ai_service._estimate_difficulty(question_text)
            assert difficulty == DifficultyLevel.EXPERT
    
    @pytest.mark.asyncio
    async def test_generate_explanation(self, ai_service):
        """Test explanation generation"""
        question = "What is the derivative of x²?"
        answer = "2x"
        
        mock_explanation = "Using the power rule: d/dx(x^n) = nx^(n-1)"
        
        with patch.object(ai_service, '_call_openai_api', return_value={"explanation": mock_explanation}):
            explanation = await ai_service._generate_explanation(question, answer)
            assert explanation == mock_explanation
    
    @pytest.mark.asyncio
    async def test_batch_generation_with_retry(self, ai_service, mock_db, sample_question_request):
        """Test batch generation with retry mechanism"""
        # First call fails, second succeeds
        mock_responses = [
            Exception("Temporary API error"),
            {
                "questions": [
                    {
                        "question_text": "Test question",
                        "options": [
                            {"id": "A", "text": "Option A", "is_correct": True},
                            {"id": "B", "text": "Option B", "is_correct": False}
                        ],
                        "explanation": "Test explanation",
                        "difficulty_level": "intermediate",
                        "estimated_time": 2
                    }
                ]
            }
        ]
        
        with patch.object(ai_service, '_call_openai_api', side_effect=mock_responses):
            result = await ai_service.generate_questions(sample_question_request, mock_db)
            
            assert result["success"] is True
            assert len(result["questions"]) == 1
    
    @pytest.mark.asyncio
    async def test_cost_calculation(self, ai_service, sample_question_request):
        """Test cost calculation for question generation"""
        with patch.object(ai_service, '_calculate_token_usage', return_value=1000):
            cost = await ai_service._calculate_generation_cost(sample_question_request)
            
            # Assuming $0.002 per 1K tokens
            expected_cost = 1000 * 0.000002
            assert abs(cost - expected_cost) < 0.0001
    
    @pytest.mark.asyncio
    async def test_quality_scoring(self, ai_service):
        """Test question quality scoring"""
        question_data = {
            "question_text": "What is the capital of France?",
            "options": [
                {"id": "A", "text": "London", "is_correct": False},
                {"id": "B", "text": "Paris", "is_correct": True},
                {"id": "C", "text": "Berlin", "is_correct": False},
                {"id": "D", "text": "Madrid", "is_correct": False}
            ],
            "explanation": "Paris is the capital and largest city of France."
        }
        
        quality_score = await ai_service._calculate_quality_score(question_data)
        
        assert 0 <= quality_score <= 1
        assert quality_score > 0.5  # Should be decent quality
    
    @pytest.mark.asyncio
    async def test_subject_context_integration(self, ai_service, mock_db, sample_subject):
        """Test integration of subject context in question generation"""
        mock_db.query.return_value.filter.return_value.first.return_value = sample_subject
        
        context = await ai_service._get_subject_context("subject-1", mock_db)
        
        assert context["subject_name"] == "Mathematics"
        assert context["subject_code"] == "MATH"
    
    @pytest.mark.asyncio
    async def test_concurrent_generation(self, ai_service, mock_db):
        """Test concurrent question generation"""
        requests = [
            {
                "subject_id": "subject-1",
                "question_type": QuestionType.MULTIPLE_CHOICE,
                "difficulty_level": DifficultyLevel.BEGINNER,
                "count": 2
            },
            {
                "subject_id": "subject-2", 
                "question_type": QuestionType.TRUE_FALSE,
                "difficulty_level": DifficultyLevel.INTERMEDIATE,
                "count": 3
            }
        ]
        
        mock_response = {
            "questions": [
                {
                    "question_text": "Test question",
                    "options": [{"id": "A", "text": "True", "is_correct": True}],
                    "explanation": "Test explanation",
                    "difficulty_level": "beginner",
                    "estimated_time": 1
                }
            ]
        }
        
        with patch.object(ai_service, '_call_openai_api', return_value=mock_response):
            tasks = [ai_service.generate_questions(req, mock_db) for req in requests]
            results = await asyncio.gather(*tasks)
            
            assert len(results) == 2
            assert all(result["success"] for result in results)
    
    def test_prompt_template_generation(self, ai_service):
        """Test prompt template generation for different question types"""
        request_data = {
            "subject": "Mathematics",
            "topic": "Algebra",
            "question_type": QuestionType.MULTIPLE_CHOICE,
            "difficulty_level": DifficultyLevel.INTERMEDIATE,
            "grade_level": "10",
            "learning_objective": "Solve quadratic equations"
        }
        
        prompt = ai_service._generate_prompt_template(request_data)
        
        assert "Mathematics" in prompt
        assert "Algebra" in prompt
        assert "multiple choice" in prompt.lower()
        assert "intermediate" in prompt.lower()
        assert "quadratic equations" in prompt
    
    @pytest.mark.asyncio
    async def test_error_handling_and_logging(self, ai_service, mock_db, sample_question_request):
        """Test error handling and logging"""
        with patch.object(ai_service, '_call_openai_api', side_effect=Exception("Network error")):
            with patch('app.services.ai_service.logger') as mock_logger:
                result = await ai_service.generate_questions(sample_question_request, mock_db)
                
                assert result["success"] is False
                mock_logger.error.assert_called()
    
    @pytest.mark.asyncio
    async def test_rate_limiting(self, ai_service, mock_db, sample_question_request):
        """Test rate limiting functionality"""
        # This would test the rate limiting mechanism
        # Implementation depends on the specific rate limiting strategy
        
        with patch.object(ai_service, '_check_rate_limit', return_value=False):
            result = await ai_service.generate_questions(sample_question_request, mock_db)
            
            assert result["success"] is False
            assert "rate limit" in result.get("error", "").lower()

@pytest.mark.integration
class TestAIServiceIntegration:
    """Integration tests for AI Service"""
    
    @pytest.mark.asyncio
    async def test_end_to_end_question_generation(self):
        """Test end-to-end question generation flow"""
        # This would test the complete flow with real database
        # and potentially real API calls (in a test environment)
        pass
    
    @pytest.mark.asyncio
    async def test_database_integration(self):
        """Test database operations during question generation"""
        # This would test actual database operations
        pass
