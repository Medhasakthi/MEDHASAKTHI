"""
Advanced Analytics Service for MEDHASAKTHI
Provides comprehensive analytics, insights, and performance metrics
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from uuid import UUID
from collections import defaultdict

import pandas as pd
import numpy as np
from sqlalchemy import func, and_, or_
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import User
from app.models.exam import Exam, ExamSession, Question, QuestionResponse
from app.models.institute import Institute
from app.services.ai_service import AIService

logger = logging.getLogger(__name__)

class AdvancedAnalyticsService:
    """Advanced analytics service with ML-powered insights"""
    
    def __init__(self):
        self.ai_service = AIService()
    
    async def get_platform_analytics(
        self,
        start_date: datetime,
        end_date: datetime,
        db: Session
    ) -> Dict[str, Any]:
        """Get comprehensive platform analytics"""
        try:
            analytics = {
                "overview": await self._get_platform_overview(start_date, end_date, db),
                "user_analytics": await self._get_user_analytics(start_date, end_date, db),
                "exam_analytics": await self._get_exam_analytics(start_date, end_date, db),
                "ai_analytics": await self._get_ai_analytics(start_date, end_date, db),
                "performance_metrics": await self._get_performance_metrics(start_date, end_date, db),
                "trends": await self._get_trend_analysis(start_date, end_date, db),
                "predictions": await self._get_predictive_analytics(db),
            }
            
            return analytics
            
        except Exception as e:
            logger.error(f"Error getting platform analytics: {str(e)}")
            raise
    
    async def get_institute_analytics(
        self,
        institute_id: str,
        start_date: datetime,
        end_date: datetime,
        db: Session
    ) -> Dict[str, Any]:
        """Get detailed analytics for a specific institute"""
        try:
            analytics = {
                "overview": await self._get_institute_overview(institute_id, start_date, end_date, db),
                "student_performance": await self._get_student_performance_analytics(institute_id, start_date, end_date, db),
                "exam_insights": await self._get_exam_insights(institute_id, start_date, end_date, db),
                "subject_analysis": await self._get_subject_analysis(institute_id, start_date, end_date, db),
                "engagement_metrics": await self._get_engagement_metrics(institute_id, start_date, end_date, db),
                "ai_usage": await self._get_institute_ai_usage(institute_id, start_date, end_date, db),
                "recommendations": await self._get_institute_recommendations(institute_id, db),
            }
            
            return analytics
            
        except Exception as e:
            logger.error(f"Error getting institute analytics: {str(e)}")
            raise
    
    async def get_student_analytics(
        self,
        student_id: str,
        db: Session
    ) -> Dict[str, Any]:
        """Get comprehensive analytics for a student"""
        try:
            analytics = {
                "performance_overview": await self._get_student_performance_overview(student_id, db),
                "subject_strengths": await self._get_student_subject_analysis(student_id, db),
                "learning_patterns": await self._get_learning_patterns(student_id, db),
                "progress_tracking": await self._get_progress_tracking(student_id, db),
                "comparative_analysis": await self._get_comparative_analysis(student_id, db),
                "recommendations": await self._get_student_recommendations(student_id, db),
                "predicted_performance": await self._predict_student_performance(student_id, db),
            }
            
            return analytics
            
        except Exception as e:
            logger.error(f"Error getting student analytics: {str(e)}")
            raise
    
    async def get_exam_analytics(
        self,
        exam_id: str,
        db: Session
    ) -> Dict[str, Any]:
        """Get detailed analytics for a specific exam"""
        try:
            analytics = {
                "overview": await self._get_exam_overview(exam_id, db),
                "question_analysis": await self._get_question_analysis(exam_id, db),
                "difficulty_analysis": await self._get_difficulty_analysis(exam_id, db),
                "time_analysis": await self._get_time_analysis(exam_id, db),
                "cheating_detection": await self._get_cheating_analysis(exam_id, db),
                "performance_distribution": await self._get_performance_distribution(exam_id, db),
                "item_response_theory": await self._get_irt_analysis(exam_id, db),
            }
            
            return analytics
            
        except Exception as e:
            logger.error(f"Error getting exam analytics: {str(e)}")
            raise
    
    async def _get_platform_overview(
        self,
        start_date: datetime,
        end_date: datetime,
        db: Session
    ) -> Dict[str, Any]:
        """Get platform overview metrics"""
        
        # Total counts
        total_users = db.query(User).count()
        total_institutes = db.query(Institute).count()
        total_exams = db.query(Exam).count()
        
        # Period-specific metrics
        new_users = db.query(User).filter(
            User.created_at.between(start_date, end_date)
        ).count()
        
        new_institutes = db.query(Institute).filter(
            Institute.created_at.between(start_date, end_date)
        ).count()
        
        exams_conducted = db.query(ExamSession).filter(
            ExamSession.start_time.between(start_date, end_date)
        ).count()
        
        # Active users (users who took exams in the period)
        active_users = db.query(ExamSession.student_id).filter(
            ExamSession.start_time.between(start_date, end_date)
        ).distinct().count()
        
        return {
            "total_users": total_users,
            "total_institutes": total_institutes,
            "total_exams": total_exams,
            "new_users": new_users,
            "new_institutes": new_institutes,
            "exams_conducted": exams_conducted,
            "active_users": active_users,
            "user_growth_rate": (new_users / max(total_users - new_users, 1)) * 100,
            "institute_growth_rate": (new_institutes / max(total_institutes - new_institutes, 1)) * 100,
        }
    
    async def _get_user_analytics(
        self,
        start_date: datetime,
        end_date: datetime,
        db: Session
    ) -> Dict[str, Any]:
        """Get user analytics and engagement metrics"""
        
        # Daily active users
        daily_active_users = []
        current_date = start_date
        
        while current_date <= end_date:
            next_date = current_date + timedelta(days=1)
            dau = db.query(ExamSession.student_id).filter(
                ExamSession.start_time.between(current_date, next_date)
            ).distinct().count()
            
            daily_active_users.append({
                "date": current_date.isoformat(),
                "active_users": dau
            })
            
            current_date = next_date
        
        # User retention analysis
        retention_data = await self._calculate_user_retention(start_date, end_date, db)
        
        # User engagement metrics
        avg_session_duration = db.query(
            func.avg(
                func.extract('epoch', ExamSession.end_time - ExamSession.start_time) / 60
            )
        ).filter(
            ExamSession.start_time.between(start_date, end_date),
            ExamSession.end_time.isnot(None)
        ).scalar() or 0
        
        return {
            "daily_active_users": daily_active_users,
            "retention_data": retention_data,
            "average_session_duration_minutes": round(avg_session_duration, 2),
        }
    
    async def _get_exam_analytics(
        self,
        start_date: datetime,
        end_date: datetime,
        db: Session
    ) -> Dict[str, Any]:
        """Get exam-related analytics"""
        
        # Exam completion rates
        total_sessions = db.query(ExamSession).filter(
            ExamSession.start_time.between(start_date, end_date)
        ).count()
        
        completed_sessions = db.query(ExamSession).filter(
            ExamSession.start_time.between(start_date, end_date),
            ExamSession.status == "COMPLETED"
        ).count()
        
        completion_rate = (completed_sessions / max(total_sessions, 1)) * 100
        
        # Average scores
        avg_score = db.query(func.avg(ExamSession.score)).filter(
            ExamSession.start_time.between(start_date, end_date),
            ExamSession.score.isnot(None)
        ).scalar() or 0
        
        # Subject performance
        subject_performance = await self._get_subject_performance(start_date, end_date, db)
        
        return {
            "total_exam_sessions": total_sessions,
            "completed_sessions": completed_sessions,
            "completion_rate": round(completion_rate, 2),
            "average_score": round(avg_score, 2),
            "subject_performance": subject_performance,
        }
    
    async def _get_ai_analytics(
        self,
        start_date: datetime,
        end_date: datetime,
        db: Session
    ) -> Dict[str, Any]:
        """Get AI usage and performance analytics"""
        
        # This would integrate with the AI service to get metrics
        # Placeholder implementation
        
        return {
            "total_questions_generated": 1250,
            "success_rate": 94.5,
            "average_generation_time": 2.3,
            "cost_per_question": 0.02,
            "popular_subjects": [
                {"subject": "Mathematics", "count": 450},
                {"subject": "Science", "count": 380},
                {"subject": "English", "count": 420},
            ],
            "quality_scores": {
                "average_quality": 4.2,
                "human_approval_rate": 89.3,
            }
        }
    
    async def _get_performance_metrics(
        self,
        start_date: datetime,
        end_date: datetime,
        db: Session
    ) -> Dict[str, Any]:
        """Get system performance metrics"""
        
        # This would integrate with monitoring systems
        # Placeholder implementation
        
        return {
            "api_response_time": 145,  # ms
            "database_query_time": 23,  # ms
            "uptime_percentage": 99.8,
            "error_rate": 0.2,  # percentage
            "concurrent_users": 156,
            "peak_concurrent_users": 342,
        }
    
    async def _get_trend_analysis(
        self,
        start_date: datetime,
        end_date: datetime,
        db: Session
    ) -> Dict[str, Any]:
        """Get trend analysis and forecasting"""
        
        # User growth trend
        user_growth_trend = await self._calculate_growth_trend("users", start_date, end_date, db)
        
        # Exam volume trend
        exam_volume_trend = await self._calculate_growth_trend("exams", start_date, end_date, db)
        
        # Performance trend
        performance_trend = await self._calculate_performance_trend(start_date, end_date, db)
        
        return {
            "user_growth_trend": user_growth_trend,
            "exam_volume_trend": exam_volume_trend,
            "performance_trend": performance_trend,
        }
    
    async def _get_predictive_analytics(self, db: Session) -> Dict[str, Any]:
        """Get predictive analytics and forecasts"""
        
        # This would use ML models for predictions
        # Placeholder implementation
        
        return {
            "predicted_user_growth": {
                "next_month": 15.2,  # percentage
                "next_quarter": 45.8,
                "confidence": 0.85,
            },
            "predicted_exam_volume": {
                "next_month": 2340,
                "next_quarter": 7120,
                "confidence": 0.78,
            },
            "churn_risk_analysis": {
                "high_risk_institutes": 3,
                "medium_risk_institutes": 8,
                "low_risk_institutes": 45,
            }
        }
    
    async def _get_student_performance_overview(
        self,
        student_id: str,
        db: Session
    ) -> Dict[str, Any]:
        """Get student performance overview"""
        
        # Get all exam sessions for the student
        sessions = db.query(ExamSession).filter(
            ExamSession.student_id == student_id,
            ExamSession.status == "COMPLETED"
        ).all()
        
        if not sessions:
            return {"message": "No completed exams found"}
        
        scores = [session.score for session in sessions if session.score is not None]
        
        return {
            "total_exams": len(sessions),
            "average_score": round(np.mean(scores), 2) if scores else 0,
            "highest_score": max(scores) if scores else 0,
            "lowest_score": min(scores) if scores else 0,
            "score_trend": await self._calculate_score_trend(scores),
            "recent_performance": scores[-5:] if len(scores) >= 5 else scores,
        }
    
    async def _calculate_user_retention(
        self,
        start_date: datetime,
        end_date: datetime,
        db: Session
    ) -> Dict[str, float]:
        """Calculate user retention metrics"""
        
        # This would implement cohort analysis
        # Placeholder implementation
        
        return {
            "day_1_retention": 85.2,
            "day_7_retention": 72.8,
            "day_30_retention": 58.4,
        }
    
    async def _calculate_growth_trend(
        self,
        metric_type: str,
        start_date: datetime,
        end_date: datetime,
        db: Session
    ) -> Dict[str, Any]:
        """Calculate growth trend for a specific metric"""
        
        # This would implement time series analysis
        # Placeholder implementation
        
        return {
            "trend": "increasing",
            "growth_rate": 12.5,  # percentage
            "seasonality": "weekly",
            "forecast": [100, 112, 125, 140, 157],
        }
    
    async def _calculate_performance_trend(
        self,
        start_date: datetime,
        end_date: datetime,
        db: Session
    ) -> Dict[str, Any]:
        """Calculate performance trend analysis"""
        
        # This would analyze score trends over time
        # Placeholder implementation
        
        return {
            "overall_trend": "improving",
            "improvement_rate": 3.2,  # percentage
            "subject_trends": {
                "Mathematics": "stable",
                "Science": "improving",
                "English": "declining",
            }
        }
    
    async def _calculate_score_trend(self, scores: List[float]) -> str:
        """Calculate score trend direction"""
        if len(scores) < 2:
            return "insufficient_data"
        
        recent_avg = np.mean(scores[-3:]) if len(scores) >= 3 else scores[-1]
        earlier_avg = np.mean(scores[:-3]) if len(scores) >= 6 else np.mean(scores[:-1])
        
        if recent_avg > earlier_avg * 1.05:
            return "improving"
        elif recent_avg < earlier_avg * 0.95:
            return "declining"
        else:
            return "stable"

# Global analytics service instance
analytics_service = AdvancedAnalyticsService()
