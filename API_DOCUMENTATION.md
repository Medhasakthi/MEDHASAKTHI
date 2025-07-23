# MEDHASAKTHI API Documentation

Complete API reference for the MEDHASAKTHI platform.

## 🎯 **CURRENT API IMPLEMENTATION STATUS**

### ⭐ **FULLY IMPLEMENTED ENDPOINTS**

#### **Authentication APIs** ✅
- `POST /api/v1/auth/login` - User authentication with JWT tokens
- `POST /api/v1/auth/logout` - Secure logout with token invalidation
- `POST /api/v1/auth/refresh` - Token refresh mechanism

#### **UPI Payment APIs** ✅ **COMPLETE SYSTEM**
- `POST /api/v1/payments/upi/create-payment` - Create payment request with QR code
- `POST /api/v1/payments/upi/submit-proof/{payment_id}` - Submit payment proof
- `GET /api/v1/payments/upi/status/{payment_id}` - Get payment status
- `GET /api/v1/payments/upi/my-payments` - User payment history
- `GET /api/v1/payments/upi/admin/pending-verifications` - Admin verification queue
- `POST /api/v1/payments/upi/admin/verify/{payment_id}` - Admin payment verification
- `POST /api/v1/payments/upi/admin/config` - UPI configuration management
- `GET /api/v1/payments/upi/admin/analytics` - Payment analytics

#### **Independent Learner APIs** ✅ **COMPLETE SYSTEM**
- `POST /api/v1/independent/register` - Learner registration
- `GET /api/v1/independent/programs` - Available certification programs
- `GET /api/v1/independent/pricing/{program_id}` - Dynamic pricing calculation
- `GET /api/v1/independent/dashboard` - Learner dashboard data

#### **Student APIs** ✅
- `GET /api/v1/student/dashboard` - Student dashboard with analytics
- `GET /api/v1/student/exams` - Student exam history
- `GET /api/v1/student/results` - Student results and certificates

#### **Teacher APIs** ✅
- `GET /api/v1/teacher/dashboard` - Teacher dashboard with class analytics
- `GET /api/v1/teacher/classes` - Assigned classes and students
- `GET /api/v1/teacher/students/performance` - Student performance tracking

#### **Admin Configuration APIs** ✅
- `POST /api/v1/admin/pricing/global-config` - Global pricing configuration
- `GET /api/v1/admin/pricing/global-config` - Get pricing configuration
- `POST /api/v1/admin/upi/config` - UPI payment configuration
- `GET /api/v1/admin/analytics` - Platform analytics

### 🔄 **IN DEVELOPMENT**
- **AI Services APIs** - Question generation and content validation
- **Advanced Exam APIs** - Proctoring and adaptive testing
- **Certificate APIs** - Digital certificate management
- **WebSocket APIs** - Real-time communication

## 📚 Table of Contents

1. [Overview](#overview)
2. [Authentication](#authentication)
3. [UPI Payment System](#upi-payment-system)
4. [Independent Learner System](#independent-learner-system)
5. [Student & Teacher APIs](#student--teacher-apis)
6. [Admin Configuration](#admin-configuration)
7. [AI Services](#ai-services)
8. [Exam Management](#exam-management)
9. [Error Handling](#error-handling)
10. [Rate Limiting](#rate-limiting)

## 🌟 Overview

### **Base URL**
```
Production: https://api.medhasakthi.com
Staging: https://staging-api.medhasakthi.com
Development: http://localhost:8000
```

### **API Version**
Current version: `v1`

All endpoints are prefixed with `/api/v1/`

### **Content Type**
All requests and responses use `application/json` unless specified otherwise.

### **Response Format**
```json
{
  "success": true,
  "data": {},
  "message": "Operation completed successfully",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

## 🔐 Authentication

### **JWT Token Authentication**

#### **Login**
```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123",
  "totp_code": "123456",
  "remember_me": true,
  "device_info": {
    "device_type": "web",
    "os": "Windows 10",
    "browser": "Chrome 91.0"
  }
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "expires_in": 3600,
    "user": {
      "id": "user-123",
      "email": "user@example.com",
      "role": "student",
      "profile": {
        "first_name": "John",
        "last_name": "Doe"
      }
    }
  }
}
```

#### **Token Refresh**
```http
POST /api/v1/auth/refresh
Content-Type: application/json

{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

#### **Using Tokens**
Include the access token in the Authorization header:
```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### **API Key Authentication**
For server-to-server communication:
```http
X-API-Key: your-api-key-here
```

## 🔧 Core Endpoints

### **User Management**

#### **Get Current User**
```http
GET /api/v1/auth/me
Authorization: Bearer {token}
```

#### **Update Profile**
```http
PUT /api/v1/users/profile
Authorization: Bearer {token}
Content-Type: application/json

{
  "first_name": "John",
  "last_name": "Doe",
  "phone": "+1234567890",
  "timezone": "America/New_York"
}
```

#### **Change Password**
```http
POST /api/v1/users/change-password
Authorization: Bearer {token}
Content-Type: application/json

{
  "current_password": "oldpassword",
  "new_password": "newpassword123",
  "confirm_password": "newpassword123"
}
```

### **Institute Management**

#### **Get Institutes**
```http
GET /api/v1/institutes?page=1&page_size=20&search=university
Authorization: Bearer {token}
```

#### **Create Institute**
```http
POST /api/v1/institutes
Authorization: Bearer {token}
Content-Type: application/json

{
  "name": "Example University",
  "code": "EXUNI001",
  "description": "A leading educational institution",
  "admin_email": "admin@example.edu",
  "admin_first_name": "Jane",
  "admin_last_name": "Smith",
  "subscription_plan": "premium",
  "max_students": 1000,
  "max_teachers": 50
}
```

#### **Update Institute**
```http
PUT /api/v1/institutes/{institute_id}
Authorization: Bearer {token}
Content-Type: application/json

{
  "name": "Updated University Name",
  "description": "Updated description",
  "is_active": true
}
```

## 🤖 AI Services

### **Generate Questions**

#### **Basic Generation**
```http
POST /api/v1/ai/generate-questions
Authorization: Bearer {token}
Content-Type: application/json

{
  "subject_id": "subject-123",
  "topic_id": "topic-456",
  "question_type": "multiple_choice",
  "difficulty_level": "intermediate",
  "count": 5,
  "grade_level": "10",
  "learning_objective": "Solve quadratic equations",
  "context": "Algebra chapter covering quadratic functions"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "questions": [
      {
        "id": "q-789",
        "question_text": "What is the solution to x² + 5x + 6 = 0?",
        "question_type": "multiple_choice",
        "options": [
          {"id": "A", "text": "x = -2, -3", "is_correct": true},
          {"id": "B", "text": "x = 2, 3", "is_correct": false},
          {"id": "C", "text": "x = -1, -6", "is_correct": false},
          {"id": "D", "text": "x = 1, 6", "is_correct": false}
        ],
        "correct_answer": "A",
        "explanation": "Factor the quadratic: (x+2)(x+3) = 0",
        "difficulty_level": "intermediate",
        "estimated_time": 3,
        "points": 2,
        "quality_score": 0.92
      }
    ],
    "generation_metadata": {
      "questions_requested": 5,
      "questions_generated": 5,
      "generation_time": 12.5,
      "cost": 0.15,
      "model_used": "gpt-4",
      "success_rate": 100
    }
  }
}
```

#### **Batch Generation**
```http
POST /api/v1/ai/generate-questions/batch
Authorization: Bearer {token}
Content-Type: application/json

{
  "requests": [
    {
      "subject_id": "math-101",
      "question_type": "multiple_choice",
      "difficulty_level": "beginner",
      "count": 10
    },
    {
      "subject_id": "science-101",
      "question_type": "true_false",
      "difficulty_level": "intermediate",
      "count": 5
    }
  ]
}
```

### **Question Validation**
```http
POST /api/v1/ai/validate-question
Authorization: Bearer {token}
Content-Type: application/json

{
  "question_text": "What is 2 + 2?",
  "options": [
    {"id": "A", "text": "3", "is_correct": false},
    {"id": "B", "text": "4", "is_correct": true}
  ],
  "explanation": "Basic addition"
}
```

### **Cost Estimation**
```http
POST /api/v1/ai/estimate-cost
Authorization: Bearer {token}
Content-Type: application/json

{
  "question_type": "essay",
  "difficulty_level": "expert",
  "count": 10,
  "context_length": "detailed"
}
```

## 📝 Exam Management

### **Exams**

#### **Create Exam**
```http
POST /api/v1/exams
Authorization: Bearer {token}
Content-Type: application/json

{
  "title": "Midterm Mathematics Exam",
  "description": "Comprehensive exam covering algebra and geometry",
  "subject_id": "math-101",
  "duration_minutes": 120,
  "total_points": 100,
  "passing_score": 70,
  "is_proctored": true,
  "proctoring_settings": {
    "camera_required": true,
    "screen_sharing": true,
    "browser_lockdown": true,
    "violation_threshold": 3
  },
  "schedule": {
    "start_time": "2024-01-15T09:00:00Z",
    "end_time": "2024-01-15T17:00:00Z",
    "timezone": "America/New_York"
  },
  "questions": [
    {
      "question_id": "q-123",
      "points": 5,
      "order": 1
    }
  ]
}
```

#### **Get Exam Details**
```http
GET /api/v1/exams/{exam_id}
Authorization: Bearer {token}
```

#### **Update Exam**
```http
PUT /api/v1/exams/{exam_id}
Authorization: Bearer {token}
Content-Type: application/json

{
  "title": "Updated Exam Title",
  "duration_minutes": 150,
  "is_active": true
}
```

### **Exam Sessions**

#### **Start Exam Session**
```http
POST /api/v1/exams/{exam_id}/start
Authorization: Bearer {token}
Content-Type: application/json

{
  "student_id": "student-123",
  "proctoring_enabled": true
}
```

#### **Submit Answer**
```http
POST /api/v1/exam-sessions/{session_id}/answers
Authorization: Bearer {token}
Content-Type: application/json

{
  "question_id": "q-123",
  "answer": "B",
  "time_spent": 45,
  "is_flagged": false
}
```

#### **Submit Exam**
```http
POST /api/v1/exam-sessions/{session_id}/submit
Authorization: Bearer {token}
Content-Type: application/json

{
  "final_answers": {
    "q-123": "B",
    "q-124": "A"
  },
  "time_spent": 3600
}
```

## 👁️ Proctoring APIs

### **Proctoring Session Management**

#### **Start Proctoring**
```http
POST /api/v1/proctoring/sessions/{session_id}/start
Authorization: Bearer {token}
Content-Type: application/json

{
  "camera_enabled": true,
  "microphone_enabled": true,
  "screen_sharing_enabled": true
}
```

#### **Report Violation**
```http
POST /api/v1/proctoring/sessions/{session_id}/violations
Authorization: Bearer {token}
Content-Type: application/json

{
  "violation_type": "TAB_SWITCH",
  "description": "Student switched to another browser tab",
  "timestamp": "2024-01-01T10:30:00Z",
  "severity": "medium",
  "evidence": {
    "screenshot": "base64_image_data",
    "metadata": {}
  }
}
```

#### **Get Proctoring Status**
```http
GET /api/v1/proctoring/sessions/{session_id}/status
Authorization: Bearer {token}
```

### **Proctoring Events**

#### **Get Violation History**
```http
GET /api/v1/proctoring/sessions/{session_id}/violations
Authorization: Bearer {token}
```

#### **Update Violation Status**
```http
PUT /api/v1/proctoring/violations/{violation_id}
Authorization: Bearer {token}
Content-Type: application/json

{
  "status": "reviewed",
  "action_taken": "warning_issued",
  "notes": "Student was warned about the violation"
}
```

## 📊 Analytics APIs

### **Platform Analytics**

#### **Get Platform Overview**
```http
GET /api/v1/analytics/platform?start_date=2024-01-01&end_date=2024-01-31
Authorization: Bearer {token}
```

#### **Get User Analytics**
```http
GET /api/v1/analytics/users?period=30d&group_by=day
Authorization: Bearer {token}
```

#### **Get Exam Analytics**
```http
GET /api/v1/analytics/exams/{exam_id}
Authorization: Bearer {token}
```

### **Student Performance**

#### **Get Student Performance**
```http
GET /api/v1/analytics/students/{student_id}/performance
Authorization: Bearer {token}
```

#### **Get Class Performance**
```http
GET /api/v1/analytics/classes/{class_id}/performance
Authorization: Bearer {token}
```

### **AI Usage Analytics**

#### **Get AI Usage Statistics**
```http
GET /api/v1/analytics/ai/usage?period=7d
Authorization: Bearer {token}
```

#### **Get Cost Analysis**
```http
GET /api/v1/analytics/ai/costs?start_date=2024-01-01&end_date=2024-01-31
Authorization: Bearer {token}
```

## 🔌 WebSocket APIs

### **Real-time Notifications**

#### **Connect to Notifications**
```javascript
const ws = new WebSocket('wss://api.medhasakthi.com/ws/notifications/{user_id}');

ws.onmessage = function(event) {
  const notification = JSON.parse(event.data);
  console.log('Received notification:', notification);
};
```

#### **Message Format**
```json
{
  "type": "EXAM_STARTED",
  "data": {
    "exam_id": "exam-123",
    "exam_title": "Mathematics Midterm",
    "start_time": "2024-01-01T10:00:00Z"
  },
  "timestamp": "2024-01-01T10:00:00Z"
}
```

### **Proctoring WebSocket**

#### **Connect to Proctoring**
```javascript
const ws = new WebSocket('wss://api.medhasakthi.com/ws/proctoring/{session_id}');

// Send video frame
ws.send(JSON.stringify({
  type: 'VIDEO_FRAME',
  data: base64_video_data
}));

// Send browser event
ws.send(JSON.stringify({
  type: 'BROWSER_EVENT',
  event_type: 'TAB_SWITCH',
  event_data: { timestamp: Date.now() }
}));
```

### **Live Analytics**

#### **Connect to Live Analytics**
```javascript
const ws = new WebSocket('wss://api.medhasakthi.com/ws/live-analytics/{user_id}');

ws.onmessage = function(event) {
  const metrics = JSON.parse(event.data);
  updateDashboard(metrics.data);
};
```

## ❌ Error Handling

### **Error Response Format**
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": {
      "field": "email",
      "reason": "Invalid email format"
    }
  },
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### **HTTP Status Codes**

| Code | Description |
|------|-------------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 422 | Validation Error |
| 429 | Rate Limited |
| 500 | Internal Server Error |

### **Error Codes**

| Code | Description |
|------|-------------|
| `VALIDATION_ERROR` | Input validation failed |
| `AUTHENTICATION_ERROR` | Authentication failed |
| `AUTHORIZATION_ERROR` | Insufficient permissions |
| `RESOURCE_NOT_FOUND` | Requested resource not found |
| `RATE_LIMIT_EXCEEDED` | Too many requests |
| `AI_SERVICE_ERROR` | AI service unavailable |
| `PROCTORING_ERROR` | Proctoring system error |

## 🚦 Rate Limiting

### **Rate Limits**

| Endpoint Category | Limit | Window |
|------------------|-------|--------|
| Authentication | 5 requests | 1 minute |
| AI Generation | 10 requests | 1 minute |
| General API | 100 requests | 1 minute |
| WebSocket | 1000 messages | 1 minute |

### **Rate Limit Headers**
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640995200
```

### **Rate Limit Response**
```json
{
  "success": false,
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Too many requests. Please try again later.",
    "retry_after": 60
  }
}
```

## 📋 SDK Examples

### **Python SDK**
```python
from medhasakthi import MEDHASAKTHIClient

client = MEDHASAKTHIClient(api_key="your-api-key")

# Generate questions
questions = client.ai.generate_questions(
    subject_id="math-101",
    question_type="multiple_choice",
    difficulty_level="intermediate",
    count=5
)

# Create exam
exam = client.exams.create(
    title="Test Exam",
    subject_id="math-101",
    duration_minutes=60
)
```

### **JavaScript SDK**
```javascript
import { MEDHASAKTHIClient } from '@medhasakthi/sdk';

const client = new MEDHASAKTHIClient({
  apiKey: 'your-api-key',
  baseURL: 'https://api.medhasakthi.com'
});

// Generate questions
const questions = await client.ai.generateQuestions({
  subjectId: 'math-101',
  questionType: 'multiple_choice',
  difficultyLevel: 'intermediate',
  count: 5
});

// Start exam session
const session = await client.exams.startSession('exam-123');
```

---

**📚 Complete API reference available at [docs.medhasakthi.com](https://docs.medhasakthi.com)**

**🔧 Need help? Contact our developer support team!**
