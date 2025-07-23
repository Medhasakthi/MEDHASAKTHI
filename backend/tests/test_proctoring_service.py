"""
Comprehensive tests for Proctoring Service
"""

import pytest
import asyncio
import json
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timedelta
from fastapi import WebSocket

from app.services.proctoring_service import ProctoringService
from app.models.exam import ExamSession, ProctoringEvent
from app.models.user import User

class TestProctoringService:
    """Test suite for Proctoring Service"""
    
    @pytest.fixture
    def proctoring_service(self):
        """Create proctoring service instance for testing"""
        return ProctoringService()
    
    @pytest.fixture
    def mock_db(self):
        """Mock database session"""
        return Mock()
    
    @pytest.fixture
    def mock_websocket(self):
        """Mock WebSocket connection"""
        websocket = Mock(spec=WebSocket)
        websocket.send_text = AsyncMock()
        websocket.close = AsyncMock()
        return websocket
    
    @pytest.fixture
    def sample_exam_session(self):
        """Sample exam session for testing"""
        return ExamSession(
            id="session-1",
            student_id="student-1",
            exam_id="exam-1",
            status="IN_PROGRESS",
            start_time=datetime.utcnow()
        )
    
    @pytest.mark.asyncio
    async def test_start_proctoring_session_success(
        self, 
        proctoring_service, 
        mock_db, 
        mock_websocket, 
        sample_exam_session
    ):
        """Test successful proctoring session start"""
        mock_db.query.return_value.filter.return_value.first.return_value = sample_exam_session
        
        with patch.object(proctoring_service, '_log_proctoring_event', new_callable=AsyncMock):
            result = await proctoring_service.start_proctoring_session(
                "session-1", mock_websocket, mock_db
            )
            
            assert result is True
            assert "session-1" in proctoring_service.active_sessions
            
            session_data = proctoring_service.active_sessions["session-1"]
            assert session_data["exam_session_id"] == "session-1"
            assert session_data["websocket"] == mock_websocket
            assert session_data["face_detection_enabled"] is True
    
    @pytest.mark.asyncio
    async def test_start_proctoring_session_not_found(
        self, 
        proctoring_service, 
        mock_db, 
        mock_websocket
    ):
        """Test proctoring session start with non-existent session"""
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        result = await proctoring_service.start_proctoring_session(
            "nonexistent-session", mock_websocket, mock_db
        )
        
        assert result is False
        assert "nonexistent-session" not in proctoring_service.active_sessions
    
    @pytest.mark.asyncio
    async def test_stop_proctoring_session(
        self, 
        proctoring_service, 
        mock_db, 
        mock_websocket, 
        sample_exam_session
    ):
        """Test stopping proctoring session"""
        # First start a session
        mock_db.query.return_value.filter.return_value.first.return_value = sample_exam_session
        
        with patch.object(proctoring_service, '_log_proctoring_event', new_callable=AsyncMock):
            await proctoring_service.start_proctoring_session(
                "session-1", mock_websocket, mock_db
            )
            
            # Now stop it
            await proctoring_service.stop_proctoring_session("session-1", mock_db)
            
            assert "session-1" not in proctoring_service.active_sessions
    
    @pytest.mark.asyncio
    async def test_process_video_frame_no_face(
        self, 
        proctoring_service, 
        mock_db, 
        mock_websocket, 
        sample_exam_session
    ):
        """Test video frame processing with no face detected"""
        # Setup active session
        mock_db.query.return_value.filter.return_value.first.return_value = sample_exam_session
        
        with patch.object(proctoring_service, '_log_proctoring_event', new_callable=AsyncMock):
            await proctoring_service.start_proctoring_session(
                "session-1", mock_websocket, mock_db
            )
            
            # Mock face detector to return no faces
            with patch.object(proctoring_service.face_detector, 'detect_faces', new_callable=AsyncMock) as mock_detect:
                mock_detect.return_value = []
                
                with patch.object(proctoring_service, '_handle_violation', new_callable=AsyncMock) as mock_handle:
                    frame_data = b"fake_frame_data"
                    await proctoring_service.process_video_frame("session-1", frame_data, mock_db)
                    
                    mock_handle.assert_called_once()
                    args = mock_handle.call_args[0]
                    assert args[1] == "NO_FACE_DETECTED"
    
    @pytest.mark.asyncio
    async def test_process_video_frame_multiple_faces(
        self, 
        proctoring_service, 
        mock_db, 
        mock_websocket, 
        sample_exam_session
    ):
        """Test video frame processing with multiple faces detected"""
        # Setup active session
        mock_db.query.return_value.filter.return_value.first.return_value = sample_exam_session
        
        with patch.object(proctoring_service, '_log_proctoring_event', new_callable=AsyncMock):
            await proctoring_service.start_proctoring_session(
                "session-1", mock_websocket, mock_db
            )
            
            # Mock face detector to return multiple faces
            with patch.object(proctoring_service.face_detector, 'detect_faces', new_callable=AsyncMock) as mock_detect:
                mock_detect.return_value = [{"id": 1}, {"id": 2}]  # Two faces
                
                with patch.object(proctoring_service, '_handle_violation', new_callable=AsyncMock) as mock_handle:
                    frame_data = b"fake_frame_data"
                    await proctoring_service.process_video_frame("session-1", frame_data, mock_db)
                    
                    mock_handle.assert_called_once()
                    args = mock_handle.call_args[0]
                    assert args[1] == "MULTIPLE_FACES"
    
    @pytest.mark.asyncio
    async def test_handle_browser_event_tab_switch(
        self, 
        proctoring_service, 
        mock_db, 
        mock_websocket, 
        sample_exam_session
    ):
        """Test handling tab switch browser event"""
        # Setup active session
        mock_db.query.return_value.filter.return_value.first.return_value = sample_exam_session
        
        with patch.object(proctoring_service, '_log_proctoring_event', new_callable=AsyncMock):
            await proctoring_service.start_proctoring_session(
                "session-1", mock_websocket, mock_db
            )
            
            with patch.object(proctoring_service, '_handle_violation', new_callable=AsyncMock) as mock_handle:
                await proctoring_service.handle_browser_event(
                    "session-1", 
                    "TAB_SWITCH", 
                    {"timestamp": datetime.utcnow().isoformat()}, 
                    mock_db
                )
                
                mock_handle.assert_called_once()
                args = mock_handle.call_args[0]
                assert args[1] == "TAB_SWITCH"
                assert "switched browser tabs" in args[2]
    
    @pytest.mark.asyncio
    async def test_handle_violation_warning_count(
        self, 
        proctoring_service, 
        mock_db, 
        mock_websocket, 
        sample_exam_session
    ):
        """Test violation handling and warning count increment"""
        # Setup active session
        mock_db.query.return_value.filter.return_value.first.return_value = sample_exam_session
        
        with patch.object(proctoring_service, '_log_proctoring_event', new_callable=AsyncMock):
            await proctoring_service.start_proctoring_session(
                "session-1", mock_websocket, mock_db
            )
            
            with patch.object(proctoring_service, '_notify_proctor', new_callable=AsyncMock):
                with patch.object(proctoring_service, '_send_student_warning', new_callable=AsyncMock):
                    await proctoring_service._handle_violation(
                        "session-1",
                        "TEST_VIOLATION",
                        "Test violation message",
                        {"test": "data"},
                        mock_db
                    )
                    
                    session_data = proctoring_service.active_sessions["session-1"]
                    assert session_data["warning_count"] == 1
                    assert len(session_data["violations"]) == 1
    
    @pytest.mark.asyncio
    async def test_handle_violation_exam_termination(
        self, 
        proctoring_service, 
        mock_db, 
        mock_websocket, 
        sample_exam_session
    ):
        """Test exam termination after multiple violations"""
        # Setup active session
        mock_db.query.return_value.filter.return_value.first.return_value = sample_exam_session
        
        with patch.object(proctoring_service, '_log_proctoring_event', new_callable=AsyncMock):
            await proctoring_service.start_proctoring_session(
                "session-1", mock_websocket, mock_db
            )
            
            # Set warning count to 2 (so next violation will trigger termination)
            proctoring_service.active_sessions["session-1"]["warning_count"] = 2
            
            with patch.object(proctoring_service, '_terminate_exam', new_callable=AsyncMock) as mock_terminate:
                with patch.object(proctoring_service, '_notify_proctor', new_callable=AsyncMock):
                    with patch.object(proctoring_service, '_send_student_warning', new_callable=AsyncMock):
                        await proctoring_service._handle_violation(
                            "session-1",
                            "FINAL_VIOLATION",
                            "Final violation",
                            {},
                            mock_db
                        )
                        
                        mock_terminate.assert_called_once_with("session-1", mock_db)
    
    @pytest.mark.asyncio
    async def test_send_student_warning(
        self, 
        proctoring_service, 
        mock_db, 
        mock_websocket, 
        sample_exam_session
    ):
        """Test sending warning message to student"""
        # Setup active session
        mock_db.query.return_value.filter.return_value.first.return_value = sample_exam_session
        
        with patch.object(proctoring_service, '_log_proctoring_event', new_callable=AsyncMock):
            await proctoring_service.start_proctoring_session(
                "session-1", mock_websocket, mock_db
            )
            
            await proctoring_service._send_student_warning("session-1", "Test warning")
            
            mock_websocket.send_text.assert_called_once()
            sent_data = json.loads(mock_websocket.send_text.call_args[0][0])
            assert sent_data["type"] == "WARNING"
            assert sent_data["message"] == "Test warning"
    
    @pytest.mark.asyncio
    async def test_terminate_exam(
        self, 
        proctoring_service, 
        mock_db, 
        mock_websocket, 
        sample_exam_session
    ):
        """Test exam termination process"""
        # Setup active session
        mock_db.query.return_value.filter.return_value.first.return_value = sample_exam_session
        
        with patch.object(proctoring_service, '_log_proctoring_event', new_callable=AsyncMock):
            await proctoring_service.start_proctoring_session(
                "session-1", mock_websocket, mock_db
            )
            
            # Mock database query for exam session update
            mock_db.query.return_value.filter.return_value.first.return_value = sample_exam_session
            
            with patch.object(proctoring_service, 'stop_proctoring_session', new_callable=AsyncMock):
                await proctoring_service._terminate_exam("session-1", mock_db)
                
                # Check that exam session was updated
                assert sample_exam_session.status == "TERMINATED"
                assert sample_exam_session.termination_reason == "Multiple proctoring violations"
                
                # Check that termination message was sent
                mock_websocket.send_text.assert_called()
                mock_websocket.close.assert_called()
    
    @pytest.mark.asyncio
    async def test_get_session_status(
        self, 
        proctoring_service, 
        mock_db, 
        mock_websocket, 
        sample_exam_session
    ):
        """Test getting session status"""
        # Setup active session
        mock_db.query.return_value.filter.return_value.first.return_value = sample_exam_session
        
        with patch.object(proctoring_service, '_log_proctoring_event', new_callable=AsyncMock):
            await proctoring_service.start_proctoring_session(
                "session-1", mock_websocket, mock_db
            )
            
            status = await proctoring_service.get_session_status("session-1")
            
            assert status is not None
            assert status["exam_session_id"] == "session-1"
            assert "websocket" not in status  # Should be removed from response
            assert "start_time" in status
            assert "violations" in status
    
    @pytest.mark.asyncio
    async def test_get_session_status_not_found(self, proctoring_service):
        """Test getting status for non-existent session"""
        status = await proctoring_service.get_session_status("nonexistent-session")
        assert status is None
    
    @pytest.mark.asyncio
    async def test_get_active_sessions(
        self, 
        proctoring_service, 
        mock_db, 
        mock_websocket, 
        sample_exam_session
    ):
        """Test getting list of active sessions"""
        # Setup active session
        mock_db.query.return_value.filter.return_value.first.return_value = sample_exam_session
        
        with patch.object(proctoring_service, '_log_proctoring_event', new_callable=AsyncMock):
            await proctoring_service.start_proctoring_session(
                "session-1", mock_websocket, mock_db
            )
            
            active_sessions = await proctoring_service.get_active_sessions()
            
            assert "session-1" in active_sessions
            assert len(active_sessions) == 1
    
    @pytest.mark.asyncio
    async def test_suspicious_gaze_detection(
        self, 
        proctoring_service, 
        mock_db, 
        mock_websocket, 
        sample_exam_session
    ):
        """Test suspicious gaze pattern detection"""
        # Setup active session
        mock_db.query.return_value.filter.return_value.first.return_value = sample_exam_session
        
        with patch.object(proctoring_service, '_log_proctoring_event', new_callable=AsyncMock):
            await proctoring_service.start_proctoring_session(
                "session-1", mock_websocket, mock_db
            )
            
            # Simulate multiple gaze-away detections
            faces = [{"gaze_direction": "away"}]
            
            with patch.object(proctoring_service, '_handle_violation', new_callable=AsyncMock) as mock_handle:
                # Simulate 6 consecutive gaze-away detections
                for _ in range(6):
                    await proctoring_service._analyze_face_detection("session-1", faces, mock_db)
                
                # Should trigger violation after 5 detections
                mock_handle.assert_called_once()
                args = mock_handle.call_args[0]
                assert args[1] == "SUSPICIOUS_GAZE"
    
    @pytest.mark.asyncio
    async def test_high_activity_detection(
        self, 
        proctoring_service, 
        mock_db, 
        mock_websocket, 
        sample_exam_session
    ):
        """Test high activity level detection"""
        # Setup active session
        mock_db.query.return_value.filter.return_value.first.return_value = sample_exam_session
        
        with patch.object(proctoring_service, '_log_proctoring_event', new_callable=AsyncMock):
            await proctoring_service.start_proctoring_session(
                "session-1", mock_websocket, mock_db
            )
            
            with patch.object(proctoring_service, '_handle_violation', new_callable=AsyncMock) as mock_handle:
                # Simulate high activity score
                await proctoring_service._analyze_activity("session-1", 0.9, mock_db)
                
                mock_handle.assert_called_once()
                args = mock_handle.call_args[0]
                assert args[1] == "HIGH_ACTIVITY"
    
    @pytest.mark.asyncio
    async def test_concurrent_sessions(
        self, 
        proctoring_service, 
        mock_db
    ):
        """Test handling multiple concurrent proctoring sessions"""
        # Create multiple mock sessions
        sessions = []
        websockets = []
        
        for i in range(3):
            session = ExamSession(
                id=f"session-{i}",
                student_id=f"student-{i}",
                exam_id=f"exam-{i}",
                status="IN_PROGRESS",
                start_time=datetime.utcnow()
            )
            sessions.append(session)
            
            websocket = Mock(spec=WebSocket)
            websocket.send_text = AsyncMock()
            websocket.close = AsyncMock()
            websockets.append(websocket)
        
        # Mock database to return appropriate session
        def mock_query_side_effect(*args):
            mock_query = Mock()
            mock_filter = Mock()
            mock_query.filter.return_value = mock_filter
            
            def mock_first():
                # Return session based on the filter (simplified)
                return sessions[0]  # Just return first session for simplicity
            
            mock_filter.first = mock_first
            return mock_query
        
        mock_db.query.side_effect = mock_query_side_effect
        
        with patch.object(proctoring_service, '_log_proctoring_event', new_callable=AsyncMock):
            # Start multiple sessions concurrently
            tasks = []
            for i in range(3):
                task = proctoring_service.start_proctoring_session(
                    f"session-{i}", websockets[i], mock_db
                )
                tasks.append(task)
            
            results = await asyncio.gather(*tasks)
            
            # All sessions should start successfully
            assert all(results)
            assert len(proctoring_service.active_sessions) == 3

@pytest.mark.integration
class TestProctoringServiceIntegration:
    """Integration tests for Proctoring Service"""
    
    @pytest.mark.asyncio
    async def test_end_to_end_proctoring_flow(self):
        """Test complete proctoring flow from start to finish"""
        # This would test the complete flow with real WebSocket
        # and database connections
        pass
    
    @pytest.mark.asyncio
    async def test_websocket_integration(self):
        """Test WebSocket integration with proctoring service"""
        # This would test actual WebSocket communication
        pass
