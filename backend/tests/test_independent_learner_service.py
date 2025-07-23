"""
Unit tests for Independent Learner Service
"""
import pytest
from unittest.mock import Mock, patch
from decimal import Decimal
from datetime import datetime, date
from sqlalchemy.orm import Session

from app.services.independent_learner_service import independent_learner_service
from app.models.independent_learner import (
    IndependentLearner, LearnerCategory, EducationLevel,
    CertificationProgram, IndependentExamRegistration
)
from app.models.pricing_config import GlobalPricingConfig
from app.models.user import User


class TestIndependentLearnerService:
    """Test cases for Independent Learner Service"""
    
    @pytest.fixture
    def mock_db(self):
        """Mock database session"""
        return Mock(spec=Session)
    
    @pytest.fixture
    def sample_registration_data(self):
        """Sample registration data for testing"""
        return {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com",
            "phone": "+91-9876543210",
            "date_of_birth": "1995-05-15",
            "gender": "male",
            "category": "working_professional",
            "education_level": "undergraduate",
            "current_occupation": "Software Developer",
            "address_line1": "123 Main Street",
            "city": "Mumbai",
            "state": "Maharashtra",
            "country": "India",
            "postal_code": "400001"
        }
    
    @pytest.fixture
    def sample_user(self):
        """Sample user object"""
        user = Mock(spec=User)
        user.id = "user-123"
        user.email = "john.doe@example.com"
        user.full_name = "John Doe"
        user.role = "independent_learner"
        return user
    
    @pytest.fixture
    def sample_learner(self):
        """Sample independent learner object"""
        learner = Mock(spec=IndependentLearner)
        learner.id = "learner-123"
        learner.learner_id = "IL202401123456"
        learner.first_name = "John"
        learner.last_name = "Doe"
        learner.category = LearnerCategory.WORKING_PROFESSIONAL
        learner.education_level = EducationLevel.UNDERGRADUATE
        learner.referral_code = "JOHDOE1234"
        return learner
    
    @pytest.fixture
    def sample_program(self):
        """Sample certification program"""
        program = Mock(spec=CertificationProgram)
        program.id = "program-123"
        program.program_code = "WD101"
        program.title = "Web Development Fundamentals"
        program.base_price = Decimal("1000.00")
        program.category = "Technology"
        program.level = "Beginner"
        program.is_active = True
        return program
    
    @pytest.fixture
    def sample_pricing_config(self):
        """Sample global pricing configuration"""
        config = Mock(spec=GlobalPricingConfig)
        config.id = "config-123"
        config.is_active = True
        config.approval_status = "active"
        config.base_exam_fee = Decimal("500.00")
        config.base_certification_fee = Decimal("1000.00")
        config.student_multiplier = Decimal("0.7")
        config.professional_multiplier = Decimal("1.0")
        config.country_pricing_multipliers = {"India": 1.0}
        config.state_pricing_multipliers = {"Maharashtra": 1.1}
        config.primary_currency = "INR"
        return config
    
    def test_generate_learner_id(self):
        """Test learner ID generation"""
        learner_id = independent_learner_service._generate_learner_id()
        
        assert learner_id.startswith("IL")
        assert len(learner_id) == 14  # IL + YYYYMM + 6 digits
        assert learner_id[2:8].isdigit()  # YYYYMM part
        assert learner_id[8:].isdigit()   # Random 6 digits
    
    def test_generate_referral_code(self):
        """Test referral code generation"""
        referral_code = independent_learner_service._generate_referral_code("John", "Doe")
        
        assert len(referral_code) == 10  # 3 + 3 + 4 characters
        assert referral_code.startswith("JOH")
        assert referral_code[3:6] == "DOE"
        assert referral_code[6:].isdigit()
    
    @patch('app.services.independent_learner_service.bcrypt.hashpw')
    @patch('app.services.independent_learner_service.email_service.send_email')
    def test_register_independent_learner_success(
        self, 
        mock_send_email, 
        mock_hashpw, 
        mock_db, 
        sample_registration_data
    ):
        """Test successful independent learner registration"""
        # Setup mocks
        mock_hashpw.return_value = b"hashed_password"
        mock_send_email.return_value = True
        mock_db.query.return_value.filter.return_value.first.return_value = None  # No existing user
        mock_db.add = Mock()
        mock_db.commit = Mock()
        
        # Test registration
        success, message, data = independent_learner_service.register_independent_learner(
            sample_registration_data, mock_db
        )
        
        # Assertions
        assert success is True
        assert "successfully registered" in message.lower()
        assert "learner_id" in data
        assert "referral_code" in data
        assert mock_db.add.call_count == 2  # User and Learner objects
        assert mock_db.commit.called
        assert mock_send_email.called
    
    def test_register_independent_learner_existing_email(self, mock_db, sample_registration_data):
        """Test registration with existing email"""
        # Setup mock to return existing user
        existing_user = Mock()
        mock_db.query.return_value.filter.return_value.first.return_value = existing_user
        
        # Test registration
        success, message, data = independent_learner_service.register_independent_learner(
            sample_registration_data, mock_db
        )
        
        # Assertions
        assert success is False
        assert "already registered" in message.lower()
        assert data is None
    
    def test_get_available_programs(self, mock_db, sample_program):
        """Test getting available certification programs"""
        # Setup mock
        mock_db.query.return_value.filter.return_value.order_by.return_value.all.return_value = [sample_program]
        
        # Test
        programs = independent_learner_service.get_available_programs(db=mock_db)
        
        # Assertions
        assert len(programs) == 1
        assert programs[0]["program_code"] == "WD101"
        assert programs[0]["title"] == "Web Development Fundamentals"
        assert programs[0]["base_price"] == 1000.00
    
    def test_calculate_program_pricing_with_config(
        self, 
        mock_db, 
        sample_program, 
        sample_pricing_config, 
        sample_learner
    ):
        """Test program pricing calculation with global config"""
        # Setup mocks
        mock_db.query.return_value.filter.return_value.first.side_effect = [
            sample_pricing_config,  # Global config query
            sample_learner          # Learner query
        ]
        
        # Test
        pricing = independent_learner_service.calculate_program_pricing(
            program_id="program-123",
            learner_id="learner-123",
            db=mock_db
        )
        
        # Assertions
        assert "base_price" in pricing
        assert "final_price" in pricing
        assert "discounts_applied" in pricing
        assert "currency" in pricing
        assert pricing["currency"] == "INR"
    
    def test_get_learner_dashboard(self, mock_db, sample_learner):
        """Test getting learner dashboard data"""
        # Setup mocks
        mock_db.query.return_value.filter.return_value.first.return_value = sample_learner
        mock_db.query.return_value.filter.return_value.count.return_value = 5
        mock_db.query.return_value.filter.return_value.order_by.return_value.limit.return_value.all.return_value = []
        
        # Test
        dashboard_data = independent_learner_service.get_learner_dashboard("learner-123", mock_db)
        
        # Assertions
        assert "learner_info" in dashboard_data
        assert "statistics" in dashboard_data
        assert "recent_registrations" in dashboard_data
        assert "available_programs" in dashboard_data
        assert dashboard_data["learner_info"]["learner_id"] == "IL202401123456"
    
    def test_pricing_calculation_student_discount(self, mock_db, sample_program, sample_pricing_config):
        """Test pricing calculation with student discount"""
        # Setup student learner
        student_learner = Mock(spec=IndependentLearner)
        student_learner.category = LearnerCategory.SCHOOL_STUDENT
        student_learner.city = "Mumbai"
        student_learner.state = "Maharashtra"
        student_learner.country = "India"
        
        # Setup mocks
        mock_db.query.return_value.filter.return_value.first.side_effect = [
            sample_pricing_config,
            student_learner
        ]
        
        # Test
        pricing = independent_learner_service.calculate_program_pricing(
            program_id="program-123",
            learner_id="student-123",
            db=mock_db
        )
        
        # Assertions
        assert pricing["base_price"] == 1000.00
        # Should apply student multiplier (0.7) and state multiplier (1.1)
        expected_price = 1000.00 * 0.7 * 1.1  # 770.00
        assert abs(pricing["final_price"] - expected_price) < 0.01
    
    def test_pricing_calculation_no_learner(self, mock_db, sample_program, sample_pricing_config):
        """Test pricing calculation without learner (guest pricing)"""
        # Setup mocks
        mock_db.query.return_value.filter.return_value.first.side_effect = [
            sample_pricing_config,
            None  # No learner found
        ]
        
        # Test
        pricing = independent_learner_service.calculate_program_pricing(
            program_id="program-123",
            learner_id=None,
            db=mock_db
        )
        
        # Assertions
        assert pricing["base_price"] == 1000.00
        assert pricing["final_price"] == 1000.00  # No discounts applied
        assert len(pricing["discounts_applied"]) == 0
    
    def test_pricing_calculation_no_config(self, mock_db, sample_program):
        """Test pricing calculation without global config"""
        # Setup mocks
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        # Test
        pricing = independent_learner_service.calculate_program_pricing(
            program_id="program-123",
            learner_id="learner-123",
            db=mock_db
        )
        
        # Assertions
        assert pricing["base_price"] == 1000.00
        assert pricing["final_price"] == 1000.00  # Base price only
        assert pricing["currency"] == "INR"
    
    def test_validate_registration_data_missing_fields(self):
        """Test registration data validation with missing fields"""
        incomplete_data = {
            "first_name": "John",
            # Missing required fields
        }
        
        is_valid, errors = independent_learner_service._validate_registration_data(incomplete_data)
        
        assert is_valid is False
        assert len(errors) > 0
        assert any("email" in error.lower() for error in errors)
    
    def test_validate_registration_data_invalid_email(self):
        """Test registration data validation with invalid email"""
        invalid_data = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "invalid-email",
            "phone": "+91-9876543210",
            "category": "working_professional",
            "education_level": "undergraduate"
        }
        
        is_valid, errors = independent_learner_service._validate_registration_data(invalid_data)
        
        assert is_valid is False
        assert any("email" in error.lower() for error in errors)
    
    def test_validate_registration_data_valid(self, sample_registration_data):
        """Test registration data validation with valid data"""
        is_valid, errors = independent_learner_service._validate_registration_data(sample_registration_data)
        
        assert is_valid is True
        assert len(errors) == 0
    
    @patch('app.services.independent_learner_service.datetime')
    def test_generate_learner_id_format(self, mock_datetime):
        """Test learner ID format with specific date"""
        # Mock datetime to return specific date
        mock_datetime.now.return_value.strftime.return_value = "202401"
        
        learner_id = independent_learner_service._generate_learner_id()
        
        assert learner_id.startswith("IL202401")
        assert len(learner_id) == 14
    
    def test_get_learner_dashboard_no_learner(self, mock_db):
        """Test dashboard data when learner not found"""
        # Setup mock to return None
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        # Test should raise exception or return error
        with pytest.raises(Exception):
            independent_learner_service.get_learner_dashboard("invalid-id", mock_db)
    
    def test_calculate_pricing_multiple_discounts(self, mock_db, sample_program, sample_pricing_config):
        """Test pricing calculation with multiple applicable discounts"""
        # Setup learner with multiple discount eligibility
        learner = Mock(spec=IndependentLearner)
        learner.category = LearnerCategory.COLLEGE_STUDENT
        learner.city = "Mumbai"
        learner.state = "Maharashtra"
        learner.country = "India"
        
        # Setup pricing config with multiple multipliers
        sample_pricing_config.student_multiplier = Decimal("0.7")  # 30% discount
        sample_pricing_config.state_pricing_multipliers = {"Maharashtra": 1.1}  # 10% increase
        
        mock_db.query.return_value.filter.return_value.first.side_effect = [
            sample_pricing_config,
            learner
        ]
        
        # Test
        pricing = independent_learner_service.calculate_program_pricing(
            program_id="program-123",
            learner_id="learner-123",
            db=mock_db
        )
        
        # Verify multiple discounts are applied
        assert len(pricing["discounts_applied"]) >= 1
        assert any("student" in discount["type"].lower() for discount in pricing["discounts_applied"])


if __name__ == "__main__":
    pytest.main([__file__])
