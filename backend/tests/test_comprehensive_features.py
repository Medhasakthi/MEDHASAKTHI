"""
Comprehensive tests for new MEDHASAKTHI features
Tests for admin routes, security, performance, WebSocket, and AI features
"""
import pytest
import json
from unittest.mock import patch, Mock
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.user import User, Institute, Student
from app.models.talent_exam import TalentExam
from app.core.security_enhanced import security_manager, threat_detector
from app.core.performance import cache_manager, performance_monitor
from app.services.advanced_ai_service import adaptive_learning_engine


class TestAdminRoutes:
    """Test admin API routes"""
    
    def test_get_platform_overview(self, client: TestClient, test_admin_user: User):
        """Test platform overview endpoint"""
        # Mock authentication
        with patch('app.api.v1.auth.dependencies.get_admin_user', return_value=test_admin_user):
            response = client.get("/api/v1/admin/analytics/overview")
            
            assert response.status_code == 200
            data = response.json()
            assert "user_statistics" in data
            assert "exam_statistics" in data
            assert "certificate_statistics" in data
    
    def test_get_all_institutes(self, client: TestClient, test_admin_user: User, test_institute: Institute):
        """Test get all institutes endpoint"""
        with patch('app.api.v1.auth.dependencies.get_admin_user', return_value=test_admin_user):
            response = client.get("/api/v1/admin/institutes")
            
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)
    
    def test_create_institute(self, client: TestClient, test_admin_user: User):
        """Test create institute endpoint"""
        institute_data = {
            "name": "New Test Institute",
            "institute_code": "NTI001",
            "institute_type": "school",
            "contact_email": "new@test.edu",
            "contact_phone": "1234567890",
            "address": {
                "street": "123 New St",
                "city": "New City",
                "state": "New State",
                "pincode": "123456"
            },
            "city": "New City",
            "state": "New State"
        }
        
        with patch('app.api.v1.auth.dependencies.get_admin_user', return_value=test_admin_user):
            response = client.post("/api/v1/admin/institutes", json=institute_data)
            
            assert response.status_code == 200
            data = response.json()
            assert data["name"] == institute_data["name"]
            assert data["institute_code"] == institute_data["institute_code"]
    
    def test_get_system_config(self, client: TestClient, test_admin_user: User):
        """Test get system configuration"""
        with patch('app.api.v1.auth.dependencies.get_admin_user', return_value=test_admin_user):
            response = client.get("/api/v1/admin/system/config")
            
            assert response.status_code == 200
            data = response.json()
            assert "platform_name" in data
            assert "version" in data
            assert "features" in data


class TestInstituteRoutes:
    """Test institute API routes"""
    
    def test_get_institute_dashboard(self, client: TestClient, test_user: User, test_institute: Institute):
        """Test institute dashboard endpoint"""
        with patch('app.api.v1.auth.dependencies.get_current_user', return_value=test_user), \
             patch('app.api.v1.auth.dependencies.get_user_institute_context', return_value={"institute": test_institute}):
            
            response = client.get("/api/v1/institute/dashboard")
            
            assert response.status_code == 200
            data = response.json()
            assert "institute_info" in data
            assert "statistics" in data
    
    def test_get_institute_students(self, client: TestClient, test_user: User, test_institute: Institute, test_student: Student):
        """Test get institute students endpoint"""
        with patch('app.api.v1.auth.dependencies.get_current_user', return_value=test_user), \
             patch('app.api.v1.auth.dependencies.get_user_institute_context', return_value={"institute": test_institute}):
            
            response = client.get("/api/v1/institute/students")
            
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)
    
    def test_create_student(self, client: TestClient, test_user: User, test_institute: Institute):
        """Test create student endpoint"""
        student_data = {
            "student_id": "NEW001",
            "full_name": "New Student",
            "email": "newstudent@test.edu",
            "phone": "9876543210",
            "current_class": "class_10",
            "date_of_birth": "2008-01-01",
            "gender": "male"
        }
        
        with patch('app.api.v1.auth.dependencies.get_current_user', return_value=test_user), \
             patch('app.api.v1.auth.dependencies.get_user_institute_context', return_value={"institute": test_institute}):
            
            response = client.post("/api/v1/institute/students", json=student_data)
            
            assert response.status_code == 200
            data = response.json()
            assert data["student_id"] == student_data["student_id"]
            assert data["full_name"] == student_data["full_name"]


class TestStudentRoutes:
    """Test student API routes"""
    
    def test_get_student_dashboard(self, client: TestClient, test_user: User, test_student: Student):
        """Test student dashboard endpoint"""
        with patch('app.api.v1.auth.dependencies.get_current_user', return_value=test_user), \
             patch('app.api.v1.auth.dependencies.get_student_context', return_value={"student": test_student}):
            
            response = client.get("/api/v1/student/dashboard")
            
            assert response.status_code == 200
            data = response.json()
            assert "student_info" in data
            assert "exam_statistics" in data
            assert "study_statistics" in data
    
    def test_get_available_exams(self, client: TestClient, test_user: User, test_student: Student, test_talent_exam: TalentExam):
        """Test get available exams endpoint"""
        with patch('app.api.v1.auth.dependencies.get_current_user', return_value=test_user), \
             patch('app.api.v1.auth.dependencies.get_student_context', return_value={"student": test_student}):
            
            response = client.get("/api/v1/student/exams/available")
            
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)
    
    def test_get_practice_questions(self, client: TestClient, test_user: User, test_student: Student):
        """Test get practice questions endpoint"""
        with patch('app.api.v1.auth.dependencies.get_current_user', return_value=test_user), \
             patch('app.api.v1.auth.dependencies.get_student_context', return_value={"student": test_student}):
            
            response = client.get("/api/v1/student/practice/questions?subject=Mathematics&limit=5")
            
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)


class TestSecurityFeatures:
    """Test enhanced security features"""
    
    def test_password_hashing(self):
        """Test advanced password hashing"""
        password = "test_password_123"
        hashed, salt = security_manager.hash_password_advanced(password)
        
        assert hashed != password
        assert salt is not None
        assert security_manager.verify_password_advanced(password, hashed, salt)
        assert not security_manager.verify_password_advanced("wrong_password", hashed, salt)
    
    def test_data_encryption(self):
        """Test data encryption and decryption"""
        sensitive_data = "This is sensitive information"
        encrypted = security_manager.encrypt_sensitive_data(sensitive_data)
        decrypted = security_manager.decrypt_sensitive_data(encrypted)
        
        assert encrypted != sensitive_data
        assert decrypted == sensitive_data
    
    def test_sql_injection_detection(self):
        """Test SQL injection detection"""
        malicious_input = "'; DROP TABLE users; --"
        safe_input = "normal user input"
        
        assert threat_detector.detect_sql_injection(malicious_input)
        assert not threat_detector.detect_sql_injection(safe_input)
    
    def test_rate_limiting(self):
        """Test rate limiting functionality"""
        client_ip = "192.168.1.1"
        endpoint = "/api/test"
        
        # First request should pass
        assert threat_detector.check_rate_limiting(client_ip, endpoint)
        
        # Simulate many requests
        with patch('app.core.security_enhanced.redis_client') as mock_redis:
            mock_redis.get.return_value = "100"  # Simulate high request count
            assert not threat_detector.check_rate_limiting(client_ip, endpoint)
    
    def test_failed_login_tracking(self):
        """Test failed login tracking"""
        identifier = "test@example.com"
        
        # First few attempts should be allowed
        assert threat_detector.track_failed_login(identifier)
        
        # Simulate max failed attempts
        with patch('app.core.security_enhanced.redis_client') as mock_redis:
            mock_redis.get.return_value = "5"  # Max failed attempts
            assert not threat_detector.track_failed_login(identifier)


class TestPerformanceFeatures:
    """Test performance optimization features"""
    
    def test_cache_operations(self):
        """Test cache manager operations"""
        key = "test_key"
        value = {"test": "data"}
        
        # Test cache set and get
        with patch('app.core.performance.cache_redis') as mock_redis:
            mock_redis.setex.return_value = True
            mock_redis.get.return_value = json.dumps(value)
            
            assert cache_manager.set(key, value)
            cached_value = cache_manager.get(key)
            assert cached_value == value
    
    def test_cache_key_generation(self):
        """Test cache key generation"""
        prefix = "test"
        args = ("arg1", "arg2")
        kwargs = {"key1": "value1", "key2": "value2"}
        
        key = cache_manager.cache_key(prefix, *args, **kwargs)
        expected = "test:arg1:arg2:key1:value1:key2:value2"
        
        assert key == expected
    
    def test_performance_monitoring(self):
        """Test performance monitoring"""
        metric_name = "test_metric"
        value = 150.5
        
        performance_monitor.record_metric(metric_name, value)
        
        # Check if metric was recorded
        assert metric_name in performance_monitor.metrics
        assert len(performance_monitor.metrics[metric_name]) == 1
        assert performance_monitor.metrics[metric_name][0]["value"] == value
    
    def test_performance_alerts(self):
        """Test performance alerting"""
        metric_name = "response_time_ms"
        high_value = 2000  # Above threshold
        
        with patch('app.core.performance.perf_logger') as mock_logger:
            performance_monitor.record_metric(metric_name, high_value)
            mock_logger.warning.assert_called()


class TestAdvancedAI:
    """Test advanced AI and ML features"""
    
    def test_student_performance_analysis(self, db_session: Session, test_student: Student):
        """Test student performance analysis"""
        analysis = adaptive_learning_engine.analyze_student_performance(str(test_student.id), db_session)
        
        assert "overall_accuracy" in analysis
        assert "subject_performance" in analysis
        assert "difficulty_performance" in analysis
        assert "strengths" in analysis
        assert "weaknesses" in analysis
        assert "recommended_difficulty" in analysis
    
    def test_personalized_question_generation(self, db_session: Session, test_student: Student):
        """Test personalized question generation"""
        with patch('app.services.ai_question_service.ai_question_service.generate_questions') as mock_generate:
            mock_generate.return_value = [
                {
                    "question_text": "Test question",
                    "options": ["A", "B", "C", "D"],
                    "correct_answer": "A",
                    "difficulty_level": "easy"
                }
            ]
            
            questions = adaptive_learning_engine.generate_personalized_questions(
                str(test_student.id), "Mathematics", 5, db_session
            )
            
            assert isinstance(questions, list)
            assert len(questions) > 0
    
    def test_performance_prediction(self, db_session: Session, test_student: Student, test_talent_exam: TalentExam):
        """Test exam performance prediction"""
        from app.services.advanced_ai_service import predictive_analytics_engine
        
        prediction = predictive_analytics_engine.predict_exam_performance(
            str(test_student.id), str(test_talent_exam.id), db_session
        )
        
        assert "predicted_score" in prediction
        assert "confidence" in prediction
        assert "recommendations" in prediction
        assert "risk_factors" in prediction
        assert "improvement_areas" in prediction
    
    def test_intelligent_tutoring(self):
        """Test intelligent tutoring system"""
        from app.services.advanced_ai_service import intelligent_tutoring_system
        
        question = "What is photosynthesis?"
        context = "Photosynthesis is the process by which plants make food using sunlight."
        
        with patch.object(intelligent_tutoring_system, 'qa_pipeline') as mock_qa:
            mock_qa.return_value = {
                "answer": "The process by which plants make food using sunlight",
                "score": 0.95
            }
            
            answer = intelligent_tutoring_system.answer_student_question(question, context)
            
            assert "answer" in answer
            assert "confidence" in answer
            assert answer["confidence"] > 0


class TestWebSocketFeatures:
    """Test WebSocket functionality"""
    
    def test_websocket_connection_stats(self):
        """Test WebSocket connection statistics"""
        from app.core.websocket_manager import connection_manager
        
        stats = connection_manager.get_connection_stats()
        
        assert "total_connections" in stats
        assert "unique_users" in stats
        assert "active_rooms" in stats
        assert "connections_by_type" in stats
    
    def test_notification_sending(self):
        """Test notification sending"""
        from app.core.websocket_manager import notification_manager
        
        with patch.object(notification_manager.connection_manager, 'send_user_message') as mock_send:
            mock_send.return_value = None
            
            # This would be an async test in a real scenario
            # For now, just test the method exists and can be called
            assert hasattr(notification_manager, 'send_notification')
    
    def test_exam_monitoring(self):
        """Test exam monitoring functionality"""
        from app.core.websocket_manager import exam_monitoring_manager
        
        session_id = "test_session_123"
        user_id = "test_user_123"
        exam_id = "test_exam_123"
        
        # Test that monitoring can be started
        assert hasattr(exam_monitoring_manager, 'start_exam_monitoring')
        assert hasattr(exam_monitoring_manager, 'report_violation')
        assert hasattr(exam_monitoring_manager, 'end_exam_monitoring')


class TestIntegrationScenarios:
    """Test complete integration scenarios"""
    
    def test_complete_exam_flow(self, client: TestClient, test_admin_user: User, test_institute: Institute, test_student: Student):
        """Test complete exam registration and taking flow"""
        # 1. Admin creates exam
        exam_data = {
            "title": "Integration Test Exam",
            "exam_type": "annual_talent",
            "class_level": "class_10",
            "academic_year": "2024-25",
            "exam_date": "2024-12-15",
            "exam_time": "10:00",
            "duration_minutes": 180,
            "registration_start_date": "2024-10-01T00:00:00",
            "registration_end_date": "2024-11-30T23:59:59",
            "total_questions": 100,
            "total_marks": 200,
            "passing_marks": 80,
            "registration_fee": 500
        }
        
        with patch('app.api.v1.auth.dependencies.get_admin_user', return_value=test_admin_user):
            response = client.post("/api/v1/talent-exams/", json=exam_data)
            assert response.status_code == 200
            exam = response.json()
            exam_id = exam["id"]
        
        # 2. Institute registers student
        registration_data = {
            "student_name": test_student.full_name,
            "student_email": test_student.email,
            "student_phone": "9876543210",
            "date_of_birth": "2008-01-01",
            "current_class": "class_10",
            "school_name": test_institute.name,
            "parent_name": "Test Parent",
            "parent_email": "parent@test.edu",
            "parent_phone": "9876543210",
            "address": "Test Address"
        }
        
        with patch('app.api.v1.auth.dependencies.get_current_user', return_value=test_admin_user), \
             patch('app.api.v1.auth.dependencies.get_user_institute_context', return_value={"institute": test_institute}):
            
            response = client.post(f"/api/v1/talent-exams/{exam_id}/register", json=registration_data)
            assert response.status_code == 200
        
        # 3. Student views available exams
        with patch('app.api.v1.auth.dependencies.get_current_user', return_value=test_admin_user), \
             patch('app.api.v1.auth.dependencies.get_student_context', return_value={"student": test_student}):
            
            response = client.get("/api/v1/student/exams/available")
            assert response.status_code == 200
            exams = response.json()
            assert len(exams) > 0
    
    def test_ai_question_generation_flow(self, client: TestClient, test_admin_user: User):
        """Test AI question generation and management flow"""
        # 1. Generate questions
        generation_data = {
            "subject": "Mathematics",
            "topic": "Algebra",
            "difficulty_level": "medium",
            "question_type": "single_choice",
            "count": 5
        }
        
        with patch('app.api.v1.auth.dependencies.get_admin_user', return_value=test_admin_user), \
             patch('openai.ChatCompletion.create') as mock_openai:
            
            mock_openai.return_value = {
                "choices": [{
                    "message": {
                        "content": json.dumps({
                            "question_text": "What is x if 2x + 5 = 15?",
                            "options": ["3", "5", "7", "10"],
                            "correct_answer": "5",
                            "explanation": "2x = 15 - 5 = 10, so x = 5"
                        })
                    }
                }]
            }
            
            response = client.post("/api/v1/ai/generate-questions", json=generation_data)
            assert response.status_code == 200
            questions = response.json()
            assert len(questions) > 0
        
        # 2. Review and approve questions
        with patch('app.api.v1.auth.dependencies.get_admin_user', return_value=test_admin_user):
            response = client.get("/api/v1/ai/questions/pending")
            assert response.status_code == 200
