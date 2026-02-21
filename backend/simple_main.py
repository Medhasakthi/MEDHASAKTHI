"""
Simple MEDHASAKTHI Backend for Local Development
This is a minimal version that works without complex dependencies
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env.local')

# Create FastAPI app
app = FastAPI(
    title="MEDHASAKTHI API",
    description="Educational Excellence Platform - Local Development",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://localhost:3002"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class User(BaseModel):
    id: str
    name: str
    email: str
    user_type: str

class LoginRequest(BaseModel):
    email: str
    password: str

class DashboardData(BaseModel):
    total_students: int
    total_exams: int
    active_sessions: int
    system_health: str

# Mock data for development
mock_users = [
    {"id": "1", "name": "Admin User", "email": "admin@medhasakthi.com", "user_type": "admin"},
    {"id": "2", "name": "Student User", "email": "student@medhasakthi.com", "user_type": "student"},
    {"id": "3", "name": "Teacher User", "email": "teacher@medhasakthi.com", "user_type": "teacher"},
]

# Routes
@app.get("/")
async def root():
    return {
        "message": "Welcome to MEDHASAKTHI API",
        "status": "running",
        "environment": "local_development",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "MEDHASAKTHI Backend",
        "environment": "local",
        "timestamp": "2025-01-26T04:54:20Z"
    }

@app.post("/api/auth/login")
async def login(login_data: LoginRequest):
    # Simple mock authentication
    for user in mock_users:
        if user["email"] == login_data.email:
            return {
                "access_token": f"mock_token_{user['id']}",
                "token_type": "bearer",
                "user": user
            }
    
    raise HTTPException(status_code=401, detail="Invalid credentials")

@app.get("/api/users/me")
async def get_current_user():
    # Return mock current user
    return mock_users[0]

@app.get("/api/admin/dashboard")
async def get_admin_dashboard():
    return {
        "total_students": 1250,
        "total_exams": 45,
        "active_sessions": 23,
        "system_health": "excellent",
        "recent_activities": [
            {"action": "New student registration", "time": "2 minutes ago"},
            {"action": "Exam completed", "time": "5 minutes ago"},
            {"action": "System backup completed", "time": "1 hour ago"}
        ],
        "performance_metrics": {
            "cpu_usage": 45,
            "memory_usage": 62,
            "disk_usage": 78
        }
    }

@app.get("/api/student/dashboard")
async def get_student_dashboard():
    return {
        "enrolled_courses": 5,
        "completed_exams": 12,
        "pending_assignments": 3,
        "overall_progress": 78,
        "recent_activities": [
            {"action": "Completed Math Quiz", "score": "85%", "time": "1 hour ago"},
            {"action": "Started Physics Course", "time": "2 days ago"},
            {"action": "Submitted Assignment", "time": "3 days ago"}
        ],
        "upcoming_exams": [
            {"subject": "Mathematics", "date": "2025-01-28", "time": "10:00 AM"},
            {"subject": "Physics", "date": "2025-01-30", "time": "2:00 PM"}
        ]
    }

@app.get("/api/system/health")
async def get_system_health():
    return {
        "status": "healthy",
        "services": {
            "database": "connected",
            "cache": "running",
            "api": "operational"
        },
        "metrics": {
            "response_time": "45ms",
            "uptime": "99.9%",
            "active_users": 156
        }
    }

@app.get("/api/exams")
async def get_exams():
    return [
        {"id": "1", "title": "Mathematics Final", "subject": "Math", "duration": 120, "questions": 50},
        {"id": "2", "title": "Physics Midterm", "subject": "Physics", "duration": 90, "questions": 40},
        {"id": "3", "title": "Chemistry Quiz", "subject": "Chemistry", "duration": 60, "questions": 30}
    ]

@app.get("/api/subjects")
async def get_subjects():
    return [
        {"id": "1", "name": "Mathematics", "description": "Advanced Mathematics", "enrolled": 450},
        {"id": "2", "name": "Physics", "description": "Applied Physics", "enrolled": 380},
        {"id": "3", "name": "Chemistry", "description": "Organic Chemistry", "enrolled": 320}
    ]

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting MEDHASAKTHI Backend (Simple Mode)")
    print("📍 Server: http://localhost:8080")
    print("📚 API Docs: http://localhost:8080/docs")
    print("🔄 Auto-reload enabled")
    
    uvicorn.run(
        "simple_main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
