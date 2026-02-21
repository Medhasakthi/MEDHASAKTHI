"""
Advanced AI and ML Service for MEDHASAKTHI
Next-generation AI capabilities including adaptive learning, personalization,
predictive analytics, and intelligent automation
"""
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, mean_squared_error
import joblib
import openai
from transformers import pipeline, AutoTokenizer, AutoModel
import torch
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.user import Student
from app.models.ai_question import Question, QuestionAttempt
from app.models.talent_exam import TalentExamSession, TalentExamRegistration
from app.services.ai_question_service import ai_question_service


class AdaptiveLearningEngine:
    """Adaptive learning system that personalizes content based on student performance"""
    
    def __init__(self):
        self.difficulty_model = None
        self.topic_recommendation_model = None
        self.scaler = StandardScaler()
        self.load_models()
    
    def load_models(self):
        """Load pre-trained ML models"""
        try:
            self.difficulty_model = joblib.load('models/difficulty_predictor.pkl')
            self.topic_recommendation_model = joblib.load('models/topic_recommender.pkl')
            self.scaler = joblib.load('models/feature_scaler.pkl')
        except FileNotFoundError:
            # Initialize new models if not found
            self.difficulty_model = RandomForestClassifier(n_estimators=100, random_state=42)
            self.topic_recommendation_model = KMeans(n_clusters=10, random_state=42)
    
    def analyze_student_performance(self, student_id: str, db: Session) -> Dict[str, Any]:
        """Analyze student's learning patterns and performance"""
        
        # Get student's question attempts
        attempts = db.query(QuestionAttempt).filter(
            QuestionAttempt.student_id == student_id
        ).order_by(QuestionAttempt.attempted_at.desc()).limit(1000).all()
        
        if not attempts:
            return self._default_analysis()
        
        # Calculate performance metrics
        total_attempts = len(attempts)
        correct_attempts = sum(1 for attempt in attempts if attempt.is_correct)
        accuracy = correct_attempts / total_attempts if total_attempts > 0 else 0
        
        # Subject-wise performance
        subject_performance = {}
        for attempt in attempts:
            if attempt.question and attempt.question.subject:
                subject = attempt.question.subject
                if subject not in subject_performance:
                    subject_performance[subject] = {"total": 0, "correct": 0}
                subject_performance[subject]["total"] += 1
                if attempt.is_correct:
                    subject_performance[subject]["correct"] += 1
        
        # Calculate subject accuracies
        for subject in subject_performance:
            total = subject_performance[subject]["total"]
            correct = subject_performance[subject]["correct"]
            subject_performance[subject]["accuracy"] = correct / total if total > 0 else 0
        
        # Difficulty level performance
        difficulty_performance = {}
        for attempt in attempts:
            if attempt.question and attempt.question.difficulty_level:
                difficulty = attempt.question.difficulty_level
                if difficulty not in difficulty_performance:
                    difficulty_performance[difficulty] = {"total": 0, "correct": 0}
                difficulty_performance[difficulty]["total"] += 1
                if attempt.is_correct:
                    difficulty_performance[difficulty]["correct"] += 1
        
        # Calculate difficulty accuracies
        for difficulty in difficulty_performance:
            total = difficulty_performance[difficulty]["total"]
            correct = difficulty_performance[difficulty]["correct"]
            difficulty_performance[difficulty]["accuracy"] = correct / total if total > 0 else 0
        
        # Learning velocity (improvement over time)
        recent_attempts = attempts[:100]  # Last 100 attempts
        older_attempts = attempts[100:200] if len(attempts) > 100 else []
        
        recent_accuracy = sum(1 for a in recent_attempts if a.is_correct) / len(recent_attempts) if recent_attempts else 0
        older_accuracy = sum(1 for a in older_attempts if a.is_correct) / len(older_attempts) if older_attempts else 0
        learning_velocity = recent_accuracy - older_accuracy
        
        return {
            "overall_accuracy": accuracy,
            "total_attempts": total_attempts,
            "subject_performance": subject_performance,
            "difficulty_performance": difficulty_performance,
            "learning_velocity": learning_velocity,
            "strengths": self._identify_strengths(subject_performance),
            "weaknesses": self._identify_weaknesses(subject_performance),
            "recommended_difficulty": self._recommend_difficulty(difficulty_performance)
        }
    
    def _default_analysis(self) -> Dict[str, Any]:
        """Default analysis for new students"""
        return {
            "overall_accuracy": 0.0,
            "total_attempts": 0,
            "subject_performance": {},
            "difficulty_performance": {},
            "learning_velocity": 0.0,
            "strengths": [],
            "weaknesses": [],
            "recommended_difficulty": "easy"
        }
    
    def _identify_strengths(self, subject_performance: Dict[str, Any]) -> List[str]:
        """Identify student's strong subjects"""
        strengths = []
        for subject, perf in subject_performance.items():
            if perf["accuracy"] > 0.8 and perf["total"] >= 10:
                strengths.append(subject)
        return strengths
    
    def _identify_weaknesses(self, subject_performance: Dict[str, Any]) -> List[str]:
        """Identify student's weak subjects"""
        weaknesses = []
        for subject, perf in subject_performance.items():
            if perf["accuracy"] < 0.6 and perf["total"] >= 10:
                weaknesses.append(subject)
        return weaknesses
    
    def _recommend_difficulty(self, difficulty_performance: Dict[str, Any]) -> str:
        """Recommend appropriate difficulty level"""
        if not difficulty_performance:
            return "easy"
        
        easy_acc = difficulty_performance.get("easy", {}).get("accuracy", 0)
        medium_acc = difficulty_performance.get("medium", {}).get("accuracy", 0)
        hard_acc = difficulty_performance.get("hard", {}).get("accuracy", 0)
        
        if easy_acc > 0.9 and medium_acc > 0.7:
            return "hard"
        elif easy_acc > 0.8:
            return "medium"
        else:
            return "easy"
    
    def generate_personalized_questions(
        self, 
        student_id: str, 
        subject: str, 
        count: int, 
        db: Session
    ) -> List[Dict[str, Any]]:
        """Generate personalized questions based on student's learning profile"""
        
        analysis = self.analyze_student_performance(student_id, db)
        recommended_difficulty = analysis["recommended_difficulty"]
        
        # Get weak topics for focused practice
        weak_subjects = analysis["weaknesses"]
        if subject in weak_subjects:
            # Focus on this weak subject
            difficulty_distribution = {"easy": 0.5, "medium": 0.3, "hard": 0.2}
        else:
            # Normal distribution based on recommended difficulty
            if recommended_difficulty == "easy":
                difficulty_distribution = {"easy": 0.6, "medium": 0.3, "hard": 0.1}
            elif recommended_difficulty == "medium":
                difficulty_distribution = {"easy": 0.3, "medium": 0.5, "hard": 0.2}
            else:
                difficulty_distribution = {"easy": 0.2, "medium": 0.3, "hard": 0.5}
        
        # Generate questions with appropriate difficulty distribution
        questions = []
        for difficulty, ratio in difficulty_distribution.items():
            difficulty_count = int(count * ratio)
            if difficulty_count > 0:
                generated = ai_question_service.generate_questions(
                    subject=subject,
                    difficulty_level=difficulty,
                    count=difficulty_count,
                    question_type="single_choice"
                )
                questions.extend(generated)
        
        return questions


class PredictiveAnalyticsEngine:
    """Predictive analytics for performance forecasting and early intervention"""
    
    def __init__(self):
        self.performance_predictor = GradientBoostingRegressor(n_estimators=100, random_state=42)
        self.dropout_predictor = RandomForestClassifier(n_estimators=100, random_state=42)
        self.feature_scaler = StandardScaler()
    
    def predict_exam_performance(self, student_id: str, exam_id: str, db: Session) -> Dict[str, Any]:
        """Predict student's performance in upcoming exam"""
        
        # Get student's historical performance
        attempts = db.query(QuestionAttempt).filter(
            QuestionAttempt.student_id == student_id
        ).all()
        
        if not attempts:
            return {"predicted_score": 50, "confidence": 0.1, "recommendations": []}
        
        # Extract features
        features = self._extract_performance_features(attempts, db)
        
        # Make prediction (mock implementation)
        predicted_score = min(100, max(0, 50 + np.random.normal(0, 15)))
        confidence = min(1.0, len(attempts) / 100)  # Higher confidence with more data
        
        # Generate recommendations
        recommendations = self._generate_performance_recommendations(features, predicted_score)
        
        return {
            "predicted_score": round(predicted_score, 2),
            "confidence": round(confidence, 2),
            "recommendations": recommendations,
            "risk_factors": self._identify_risk_factors(features),
            "improvement_areas": self._identify_improvement_areas(features)
        }
    
    def _extract_performance_features(self, attempts: List[QuestionAttempt], db: Session) -> Dict[str, float]:
        """Extract features for performance prediction"""
        if not attempts:
            return {}
        
        total_attempts = len(attempts)
        correct_attempts = sum(1 for a in attempts if a.is_correct)
        accuracy = correct_attempts / total_attempts
        
        # Time-based features
        avg_time_per_question = np.mean([a.time_taken_seconds for a in attempts if a.time_taken_seconds])
        
        # Recent performance trend
        recent_attempts = attempts[-50:] if len(attempts) > 50 else attempts
        recent_accuracy = sum(1 for a in recent_attempts if a.is_correct) / len(recent_attempts)
        
        # Consistency (standard deviation of recent performance)
        recent_scores = [1 if a.is_correct else 0 for a in recent_attempts]
        consistency = 1 - np.std(recent_scores) if len(recent_scores) > 1 else 0
        
        return {
            "overall_accuracy": accuracy,
            "recent_accuracy": recent_accuracy,
            "avg_time_per_question": avg_time_per_question or 60,
            "consistency": consistency,
            "total_practice": total_attempts,
            "learning_velocity": recent_accuracy - accuracy
        }
    
    def _generate_performance_recommendations(self, features: Dict[str, float], predicted_score: float) -> List[str]:
        """Generate personalized recommendations"""
        recommendations = []
        
        if predicted_score < 60:
            recommendations.append("Focus on fundamental concepts and practice more basic questions")
            recommendations.append("Consider reviewing study materials and seeking help from teachers")
        
        if features.get("consistency", 0) < 0.5:
            recommendations.append("Work on consistency by practicing regularly rather than cramming")
        
        if features.get("avg_time_per_question", 60) > 120:
            recommendations.append("Practice time management and quick problem-solving techniques")
        
        if features.get("total_practice", 0) < 100:
            recommendations.append("Increase practice volume to improve familiarity with question patterns")
        
        return recommendations
    
    def _identify_risk_factors(self, features: Dict[str, float]) -> List[str]:
        """Identify risk factors for poor performance"""
        risk_factors = []
        
        if features.get("recent_accuracy", 0) < 0.5:
            risk_factors.append("Low recent performance")
        
        if features.get("learning_velocity", 0) < -0.1:
            risk_factors.append("Declining performance trend")
        
        if features.get("total_practice", 0) < 50:
            risk_factors.append("Insufficient practice")
        
        return risk_factors
    
    def _identify_improvement_areas(self, features: Dict[str, float]) -> List[str]:
        """Identify areas for improvement"""
        areas = []
        
        if features.get("avg_time_per_question", 60) > 90:
            areas.append("Speed and time management")
        
        if features.get("consistency", 0) < 0.7:
            areas.append("Consistency in performance")
        
        if features.get("overall_accuracy", 0) < 0.7:
            areas.append("Conceptual understanding")
        
        return areas


class IntelligentTutoringSystem:
    """AI-powered tutoring system with natural language processing"""
    
    def __init__(self):
        self.qa_pipeline = pipeline("question-answering", model="distilbert-base-cased-distilled-squad")
        self.text_generator = pipeline("text-generation", model="gpt2")
        
    def answer_student_question(self, question: str, context: str = None) -> Dict[str, Any]:
        """Answer student's question using AI"""
        
        if not context:
            context = self._get_relevant_context(question)
        
        try:
            # Use QA pipeline to answer question
            result = self.qa_pipeline(question=question, context=context)
            
            return {
                "answer": result["answer"],
                "confidence": result["score"],
                "context_used": context[:200] + "..." if len(context) > 200 else context
            }
        except Exception as e:
            return {
                "answer": "I'm sorry, I couldn't understand your question. Please try rephrasing it.",
                "confidence": 0.0,
                "error": str(e)
            }
    
    def _get_relevant_context(self, question: str) -> str:
        """Get relevant context for answering the question"""
        # This would typically search through educational content database
        # For now, return a generic educational context
        return """
        Mathematics is the study of numbers, shapes, and patterns. It includes arithmetic, 
        algebra, geometry, and calculus. Science covers physics, chemistry, and biology, 
        exploring how the natural world works. English language arts focuses on reading, 
        writing, grammar, and literature comprehension.
        """
    
    def generate_explanation(self, topic: str, difficulty_level: str = "medium") -> str:
        """Generate explanation for a topic"""
        
        prompt = f"Explain {topic} in simple terms suitable for {difficulty_level} level students:"
        
        try:
            result = self.text_generator(prompt, max_length=200, num_return_sequences=1)
            return result[0]["generated_text"].replace(prompt, "").strip()
        except Exception as e:
            return f"I can help explain {topic}. Please ask a specific question about this topic."
    
    def suggest_study_plan(self, student_analysis: Dict[str, Any], target_exam_date: datetime) -> Dict[str, Any]:
        """Generate personalized study plan"""
        
        days_until_exam = (target_exam_date - datetime.now()).days
        weak_subjects = student_analysis.get("weaknesses", [])
        strong_subjects = student_analysis.get("strengths", [])
        
        # Allocate study time based on weaknesses
        total_study_hours = min(days_until_exam * 2, 100)  # Max 2 hours per day
        
        study_plan = {
            "total_days": days_until_exam,
            "total_study_hours": total_study_hours,
            "daily_schedule": [],
            "subject_allocation": {},
            "milestones": []
        }
        
        # Allocate more time to weak subjects
        if weak_subjects:
            weak_subject_hours = total_study_hours * 0.6
            hours_per_weak_subject = weak_subject_hours / len(weak_subjects)
            
            for subject in weak_subjects:
                study_plan["subject_allocation"][subject] = hours_per_weak_subject
        
        # Allocate remaining time to strong subjects for maintenance
        if strong_subjects:
            strong_subject_hours = total_study_hours * 0.4
            hours_per_strong_subject = strong_subject_hours / len(strong_subjects)
            
            for subject in strong_subjects:
                study_plan["subject_allocation"][subject] = hours_per_strong_subject
        
        # Generate daily schedule
        for day in range(min(days_until_exam, 30)):  # Plan for next 30 days max
            daily_plan = self._generate_daily_plan(day, study_plan["subject_allocation"])
            study_plan["daily_schedule"].append(daily_plan)
        
        # Generate milestones
        study_plan["milestones"] = self._generate_milestones(days_until_exam, weak_subjects)
        
        return study_plan
    
    def _generate_daily_plan(self, day: int, subject_allocation: Dict[str, float]) -> Dict[str, Any]:
        """Generate daily study plan"""
        subjects = list(subject_allocation.keys())
        if not subjects:
            return {"day": day + 1, "subjects": [], "total_hours": 0}
        
        # Rotate subjects to ensure variety
        daily_subjects = subjects[day % len(subjects):] + subjects[:day % len(subjects)]
        daily_subjects = daily_subjects[:2]  # Max 2 subjects per day
        
        return {
            "day": day + 1,
            "subjects": daily_subjects,
            "total_hours": 2,
            "activities": [
                f"Practice {subject} questions (1 hour)" for subject in daily_subjects
            ]
        }
    
    def _generate_milestones(self, days_until_exam: int, weak_subjects: List[str]) -> List[Dict[str, Any]]:
        """Generate study milestones"""
        milestones = []
        
        if days_until_exam > 7:
            milestones.append({
                "day": 7,
                "title": "Week 1 Assessment",
                "description": "Complete practice tests for weak subjects",
                "subjects": weak_subjects[:2] if weak_subjects else []
            })
        
        if days_until_exam > 14:
            milestones.append({
                "day": 14,
                "title": "Mid-preparation Review",
                "description": "Full-length practice exam",
                "subjects": "all"
            })
        
        if days_until_exam > 3:
            milestones.append({
                "day": max(1, days_until_exam - 3),
                "title": "Final Review",
                "description": "Review key concepts and formulas",
                "subjects": "all"
            })
        
        return milestones


# Global instances
adaptive_learning_engine = AdaptiveLearningEngine()
predictive_analytics_engine = PredictiveAnalyticsEngine()
intelligent_tutoring_system = IntelligentTutoringSystem()
