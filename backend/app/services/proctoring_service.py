"""
Real-time Proctoring Service for MEDHASAKTHI
Handles exam monitoring, suspicious activity detection, and security enforcement
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from uuid import UUID

import cv2
import numpy as np
from fastapi import WebSocket
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.exam import Exam, ExamSession, ProctoringEvent
from app.models.user import User
from app.services.notification_service import NotificationService
from app.utils.ai_detection import FaceDetector, ActivityAnalyzer

logger = logging.getLogger(__name__)

class ProctoringService:
    """Real-time proctoring service with AI-powered monitoring"""
    
    def __init__(self):
        self.active_sessions: Dict[str, Dict] = {}
        self.face_detector = FaceDetector()
        self.activity_analyzer = ActivityAnalyzer()
        self.notification_service = NotificationService()
        
    async def start_proctoring_session(
        self,
        exam_session_id: str,
        websocket: WebSocket,
        db: Session
    ) -> bool:
        """Start a new proctoring session"""
        try:
            # Get exam session details
            exam_session = db.query(ExamSession).filter(
                ExamSession.id == exam_session_id
            ).first()
            
            if not exam_session:
                logger.error(f"Exam session not found: {exam_session_id}")
                return False
            
            # Initialize session data
            session_data = {
                "exam_session_id": exam_session_id,
                "student_id": exam_session.student_id,
                "exam_id": exam_session.exam_id,
                "websocket": websocket,
                "start_time": datetime.utcnow(),
                "violations": [],
                "face_detection_enabled": True,
                "screen_monitoring_enabled": True,
                "audio_monitoring_enabled": True,
                "last_heartbeat": datetime.utcnow(),
                "suspicious_activity_count": 0,
                "warning_count": 0
            }
            
            self.active_sessions[exam_session_id] = session_data
            
            # Log proctoring start
            await self._log_proctoring_event(
                exam_session_id,
                "PROCTORING_STARTED",
                {"message": "Proctoring session initiated"},
                db
            )
            
            logger.info(f"Proctoring session started for exam session: {exam_session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error starting proctoring session: {str(e)}")
            return False
    
    async def stop_proctoring_session(self, exam_session_id: str, db: Session):
        """Stop proctoring session"""
        try:
            if exam_session_id in self.active_sessions:
                session_data = self.active_sessions[exam_session_id]
                
                # Calculate session duration
                duration = datetime.utcnow() - session_data["start_time"]
                
                # Log proctoring end
                await self._log_proctoring_event(
                    exam_session_id,
                    "PROCTORING_ENDED",
                    {
                        "duration_minutes": duration.total_seconds() / 60,
                        "total_violations": len(session_data["violations"]),
                        "suspicious_activity_count": session_data["suspicious_activity_count"]
                    },
                    db
                )
                
                # Remove from active sessions
                del self.active_sessions[exam_session_id]
                
                logger.info(f"Proctoring session ended for exam session: {exam_session_id}")
                
        except Exception as e:
            logger.error(f"Error stopping proctoring session: {str(e)}")
    
    async def process_video_frame(
        self,
        exam_session_id: str,
        frame_data: bytes,
        db: Session
    ):
        """Process video frame for face detection and activity analysis"""
        try:
            if exam_session_id not in self.active_sessions:
                return
            
            session_data = self.active_sessions[exam_session_id]
            
            # Convert frame data to OpenCV format
            nparr = np.frombuffer(frame_data, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if frame is None:
                return
            
            # Face detection
            faces = await self.face_detector.detect_faces(frame)
            await self._analyze_face_detection(exam_session_id, faces, db)
            
            # Activity analysis
            activity_score = await self.activity_analyzer.analyze_activity(frame)
            await self._analyze_activity(exam_session_id, activity_score, db)
            
            # Update last heartbeat
            session_data["last_heartbeat"] = datetime.utcnow()
            
        except Exception as e:
            logger.error(f"Error processing video frame: {str(e)}")
    
    async def process_screen_capture(
        self,
        exam_session_id: str,
        screen_data: bytes,
        db: Session
    ):
        """Process screen capture for tab switching and suspicious activity"""
        try:
            if exam_session_id not in self.active_sessions:
                return
            
            # Analyze screen for suspicious content
            suspicious_elements = await self._analyze_screen_content(screen_data)
            
            if suspicious_elements:
                await self._handle_screen_violation(
                    exam_session_id,
                    suspicious_elements,
                    db
                )
                
        except Exception as e:
            logger.error(f"Error processing screen capture: {str(e)}")
    
    async def handle_browser_event(
        self,
        exam_session_id: str,
        event_type: str,
        event_data: Dict,
        db: Session
    ):
        """Handle browser events (tab switch, window focus, etc.)"""
        try:
            if exam_session_id not in self.active_sessions:
                return
            
            session_data = self.active_sessions[exam_session_id]
            
            # Check for violations
            violation_detected = False
            violation_message = ""
            
            if event_type == "TAB_SWITCH":
                violation_detected = True
                violation_message = "Student switched browser tabs"
                
            elif event_type == "WINDOW_BLUR":
                violation_detected = True
                violation_message = "Student left exam window"
                
            elif event_type == "FULLSCREEN_EXIT":
                violation_detected = True
                violation_message = "Student exited fullscreen mode"
                
            elif event_type == "COPY_PASTE":
                violation_detected = True
                violation_message = "Copy/paste activity detected"
                
            elif event_type == "RIGHT_CLICK":
                violation_detected = True
                violation_message = "Right-click context menu accessed"
            
            if violation_detected:
                await self._handle_violation(
                    exam_session_id,
                    event_type,
                    violation_message,
                    event_data,
                    db
                )
                
        except Exception as e:
            logger.error(f"Error handling browser event: {str(e)}")
    
    async def _analyze_face_detection(
        self,
        exam_session_id: str,
        faces: List[Dict],
        db: Session
    ):
        """Analyze face detection results"""
        session_data = self.active_sessions[exam_session_id]
        
        if len(faces) == 0:
            # No face detected
            await self._handle_violation(
                exam_session_id,
                "NO_FACE_DETECTED",
                "No face detected in video feed",
                {"face_count": 0},
                db
            )
            
        elif len(faces) > 1:
            # Multiple faces detected
            await self._handle_violation(
                exam_session_id,
                "MULTIPLE_FACES",
                "Multiple faces detected",
                {"face_count": len(faces)},
                db
            )
            
        else:
            # Single face detected - analyze for suspicious behavior
            face = faces[0]
            
            # Check gaze direction
            if face.get("gaze_direction") == "away":
                session_data["suspicious_activity_count"] += 1
                
                if session_data["suspicious_activity_count"] > 5:
                    await self._handle_violation(
                        exam_session_id,
                        "SUSPICIOUS_GAZE",
                        "Student looking away frequently",
                        {"gaze_direction": face.get("gaze_direction")},
                        db
                    )
    
    async def _analyze_activity(
        self,
        exam_session_id: str,
        activity_score: float,
        db: Session
    ):
        """Analyze activity level for suspicious behavior"""
        if activity_score > 0.8:  # High activity threshold
            await self._handle_violation(
                exam_session_id,
                "HIGH_ACTIVITY",
                "Unusual high activity detected",
                {"activity_score": activity_score},
                db
            )
    
    async def _analyze_screen_content(self, screen_data: bytes) -> List[str]:
        """Analyze screen content for suspicious elements"""
        # This would use OCR and image analysis to detect:
        # - Other browser windows
        # - Chat applications
        # - Search engines
        # - Educational websites
        # - Note-taking apps
        
        suspicious_elements = []
        
        # Placeholder implementation
        # In real implementation, use OCR libraries like Tesseract
        # and image classification models
        
        return suspicious_elements
    
    async def _handle_violation(
        self,
        exam_session_id: str,
        violation_type: str,
        message: str,
        metadata: Dict,
        db: Session
    ):
        """Handle proctoring violation"""
        try:
            session_data = self.active_sessions[exam_session_id]
            
            # Record violation
            violation = {
                "type": violation_type,
                "message": message,
                "timestamp": datetime.utcnow().isoformat(),
                "metadata": metadata
            }
            
            session_data["violations"].append(violation)
            session_data["warning_count"] += 1
            
            # Log proctoring event
            await self._log_proctoring_event(
                exam_session_id,
                violation_type,
                {
                    "message": message,
                    "metadata": metadata,
                    "warning_count": session_data["warning_count"]
                },
                db
            )
            
            # Send real-time notification to proctor
            await self._notify_proctor(exam_session_id, violation, db)
            
            # Send warning to student
            await self._send_student_warning(exam_session_id, message)
            
            # Check if exam should be terminated
            if session_data["warning_count"] >= 3:
                await self._terminate_exam(exam_session_id, db)
                
        except Exception as e:
            logger.error(f"Error handling violation: {str(e)}")
    
    async def _handle_screen_violation(
        self,
        exam_session_id: str,
        suspicious_elements: List[str],
        db: Session
    ):
        """Handle screen-based violations"""
        message = f"Suspicious screen content detected: {', '.join(suspicious_elements)}"
        
        await self._handle_violation(
            exam_session_id,
            "SUSPICIOUS_SCREEN_CONTENT",
            message,
            {"suspicious_elements": suspicious_elements},
            db
        )
    
    async def _log_proctoring_event(
        self,
        exam_session_id: str,
        event_type: str,
        event_data: Dict,
        db: Session
    ):
        """Log proctoring event to database"""
        try:
            proctoring_event = ProctoringEvent(
                exam_session_id=exam_session_id,
                event_type=event_type,
                event_data=event_data,
                timestamp=datetime.utcnow()
            )
            
            db.add(proctoring_event)
            db.commit()
            
        except Exception as e:
            logger.error(f"Error logging proctoring event: {str(e)}")
            db.rollback()
    
    async def _notify_proctor(
        self,
        exam_session_id: str,
        violation: Dict,
        db: Session
    ):
        """Send real-time notification to proctor"""
        try:
            # Get exam session details
            exam_session = db.query(ExamSession).filter(
                ExamSession.id == exam_session_id
            ).first()
            
            if exam_session:
                # Send notification to exam proctors
                await self.notification_service.send_proctor_alert(
                    exam_id=exam_session.exam_id,
                    student_id=exam_session.student_id,
                    violation_type=violation["type"],
                    message=violation["message"],
                    metadata=violation["metadata"]
                )
                
        except Exception as e:
            logger.error(f"Error notifying proctor: {str(e)}")
    
    async def _send_student_warning(self, exam_session_id: str, message: str):
        """Send warning message to student"""
        try:
            if exam_session_id in self.active_sessions:
                session_data = self.active_sessions[exam_session_id]
                websocket = session_data["websocket"]
                
                warning_message = {
                    "type": "WARNING",
                    "message": message,
                    "timestamp": datetime.utcnow().isoformat()
                }
                
                await websocket.send_text(json.dumps(warning_message))
                
        except Exception as e:
            logger.error(f"Error sending student warning: {str(e)}")
    
    async def _terminate_exam(self, exam_session_id: str, db: Session):
        """Terminate exam due to violations"""
        try:
            # Update exam session status
            exam_session = db.query(ExamSession).filter(
                ExamSession.id == exam_session_id
            ).first()
            
            if exam_session:
                exam_session.status = "TERMINATED"
                exam_session.end_time = datetime.utcnow()
                exam_session.termination_reason = "Multiple proctoring violations"
                
                db.commit()
                
                # Send termination message to student
                if exam_session_id in self.active_sessions:
                    session_data = self.active_sessions[exam_session_id]
                    websocket = session_data["websocket"]
                    
                    termination_message = {
                        "type": "EXAM_TERMINATED",
                        "message": "Exam terminated due to multiple violations",
                        "timestamp": datetime.utcnow().isoformat()
                    }
                    
                    await websocket.send_text(json.dumps(termination_message))
                    await websocket.close()
                
                # Stop proctoring session
                await self.stop_proctoring_session(exam_session_id, db)
                
                logger.warning(f"Exam terminated for session: {exam_session_id}")
                
        except Exception as e:
            logger.error(f"Error terminating exam: {str(e)}")
    
    async def get_session_status(self, exam_session_id: str) -> Optional[Dict]:
        """Get current proctoring session status"""
        if exam_session_id in self.active_sessions:
            session_data = self.active_sessions[exam_session_id].copy()
            
            # Remove websocket from response
            session_data.pop("websocket", None)
            
            # Convert datetime objects to strings
            session_data["start_time"] = session_data["start_time"].isoformat()
            session_data["last_heartbeat"] = session_data["last_heartbeat"].isoformat()
            
            return session_data
        
        return None
    
    async def get_active_sessions(self) -> List[str]:
        """Get list of active proctoring sessions"""
        return list(self.active_sessions.keys())

# Global proctoring service instance
proctoring_service = ProctoringService()
