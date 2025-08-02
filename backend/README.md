# MEDHASAKTHI Backend API

AI-Powered Adaptive Examination Platform Backend built with FastAPI.

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- PostgreSQL 12+
- Redis 6+

### Installation

1. **Clone and navigate to backend directory**
```bash
cd backend
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. **Set up database**
```bash
# Create PostgreSQL database
createdb medhasakthi

# Update DATABASE_URL in .env file
DATABASE_URL=postgresql://username:password@localhost:5432/medhasakthi
```

6. **Start Redis server**
```bash
redis-server
```

7. **Run the application**
```bash
python main.py
```

The API will be available at:
- **API**: http://localhost:8080
- **Documentation**: http://localhost:8080/docs
- **Health Check**: http://localhost:8080/health

## 📚 API Documentation

### Authentication Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/register` | Register new user |
| POST | `/api/v1/auth/login` | User login |
| POST | `/api/v1/auth/logout` | User logout |
| POST | `/api/v1/auth/refresh` | Refresh access token |
| POST | `/api/v1/auth/verify-email` | Verify email address |
| POST | `/api/v1/auth/request-password-reset` | Request password reset |
| POST | `/api/v1/auth/reset-password` | Reset password |
| POST | `/api/v1/auth/change-password` | Change password |
| GET | `/api/v1/auth/me` | Get current user info |
| GET | `/api/v1/auth/status` | Get auth status |

### User Roles

- **Super Admin**: Platform administrators
- **Institute Admin**: School/college administrators  
- **Teacher**: Subject teachers
- **Student**: Exam takers
- **Parent**: Student guardians

## 🔒 Security Features

- **JWT Authentication** with access and refresh tokens
- **Password Hashing** using bcrypt
- **Two-Factor Authentication** (TOTP)
- **Account Lockout** after failed attempts
- **Rate Limiting** on sensitive endpoints
- **Email Verification** for new accounts
- **Secure Password Reset** with time-limited tokens
- **Session Management** with Redis
- **Role-Based Access Control** (RBAC)

## 🗄️ Database Schema

### Core Tables
- `users` - Main authentication table
- `user_profiles` - Extended user information
- `institutes` - Educational institutions
- `students` - Student-specific data
- `teachers` - Teacher-specific data
- `user_sessions` - Session tracking
- `password_reset_tokens` - Password reset tokens
- `email_verification_tokens` - Email verification tokens

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | Required |
| `REDIS_URL` | Redis connection string | `redis://localhost:6379` |
| `SECRET_KEY` | JWT secret key | Required |
| `SENDGRID_API_KEY` | SendGrid API key for emails | Optional |
| `DEBUG` | Enable debug mode | `false` |

### Email Configuration

The application uses SendGrid for email delivery. Set up:

1. Create SendGrid account
2. Get API key
3. Set `SENDGRID_API_KEY` in environment
4. Configure `FROM_EMAIL` and `FROM_NAME`

## 🧪 Testing

### Run Tests
```bash
pytest
```

### Test Coverage
```bash
pytest --cov=app
```

### Manual Testing
```bash
# Test registration
curl -X POST "http://localhost:8080/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePass123!",
    "confirm_password": "SecurePass123!",
    "role": "student",
    "first_name": "Test",
    "last_name": "User",
    "institute_code": "TEST001",
    "student_id": "STU001"
  }'

# Test login
curl -X POST "http://localhost:8080/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePass123!"
  }'
```

## 🚀 Deployment

### Docker Deployment
```bash
# Build image
docker build -t medhasakthi-backend .

# Run container
docker run -p 8000:8000 --env-file .env medhasakthi-backend
```

### Production Checklist
- [ ] Set `DEBUG=false`
- [ ] Use strong `SECRET_KEY`
- [ ] Configure production database
- [ ] Set up Redis cluster
- [ ] Configure email service
- [ ] Set up monitoring (Sentry)
- [ ] Configure HTTPS
- [ ] Set up backup strategy

## 📊 Monitoring

### Health Checks
- **Basic**: `/health`
- **Detailed**: `/health/detailed`

### Logging
Logs are structured and include:
- Request/response times
- Authentication events
- Error tracking
- Performance metrics

## 🔄 Development

### Code Style
```bash
# Format code
black app/

# Lint code
flake8 app/

# Type checking
mypy app/
```

### Database Migrations
```bash
# Generate migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Make changes
4. Add tests
5. Submit pull request

## 📄 License

Copyright © 2024 MEDHASAKTHI. All rights reserved.

## 🆘 Support

For support and questions:
- Email: support@medhasakthi.com
- Documentation: `/docs` endpoint
- Health Status: `/health` endpoint
