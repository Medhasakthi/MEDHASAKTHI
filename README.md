# 🎓 MEDHASAKTHI - Complete Indian Education Platform

> **AI-Powered Education System for India**  
> Supporting ALL Indian specializations, entrance exams, and certifications

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://docker.com)
[![AI Powered](https://img.shields.io/badge/AI-Powered-green.svg)](https://openai.com)

---

## 🚀 Quick Deployment

### Prerequisites
- Docker & Docker Compose installed
- Git installed

### Deploy in 3 Steps

1. **Clone the repository:**
```bash
git clone https://github.com/your-username/MEDHASAKTHI.git
cd MEDHASAKTHI
```

2. **Configure environment:**
```bash
# The .env file is already created with required fields
# Edit .env with your actual values (see Configuration Guide below)
```

3. **Deploy:**
```bash
# Windows
deploy.bat

# Linux/macOS/WSL
chmod +x deploy.sh
./deploy.sh
```

**⏱️ Deployment Time: 5 minutes!**

---

## 🔧 Configuration Guide

Update the `.env` file with your actual values:

### Required Fields:
- **Security Keys**: Generate strong random keys (32+ characters)
- **Database Password**: Strong password for PostgreSQL
- **Redis Password**: Strong password for Redis
- **Domain**: Your actual domain name
- **Email**: Gmail SMTP or SendGrid API key
- **OpenAI API Key**: For AI question generation
- **UPI ID**: Your business UPI ID for payments

### Example:
```bash
SECRET_KEY=your-super-secret-key-32-chars-minimum
POSTGRES_PASSWORD=your-strong-db-password
REDIS_PASSWORD=your-strong-redis-password
DOMAIN=yourdomain.com
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-gmail-app-password
OPENAI_API_KEY=sk-your-openai-key
UPI_PRIMARY_ID=yourbusiness@paytm
```

---

## 🏗️ Key Features

### 🎯 **Core Features**
- **Multi-Subject Support**: Engineering, Medical, Law, Business, etc.
- **AI Question Generation**: Powered by OpenAI GPT
- **Real-time Exams**: Live proctoring and monitoring
- **UPI Payments**: Integrated Indian payment system
- **Multi-language**: English, Hindi, Tamil, Telugu, Kannada

### 🔒 **Security Features**
- JWT Authentication
- Role-based Access Control
- Exam Security & Anti-cheating
- Data Encryption
- Rate Limiting

### 📊 **Analytics & Reporting**
- Performance Analytics
- Progress Tracking
- Detailed Reports
- AI-powered Insights

---

## 🌐 Access Your Application

After deployment, access:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

---

## 📱 Architecture

```
Frontend (React) → Backend (FastAPI) → Database (PostgreSQL)
                ↓
            Redis Cache
                ↓
            AI Services (OpenAI)
```

---

## 🛠️ Development

### Local Development
```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn main:app --reload

# Frontend
cd frontend
npm install
npm start
```

### Docker Development
```bash
docker-compose up --build
```

---

## 📚 Documentation

- **API Documentation**: Available at `/docs` endpoint
- **Configuration**: See `.env` file comments
- **Deployment**: Use provided deployment scripts

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🆘 Support

For support and questions:
- Create an issue on GitHub
- Email: support@medhasakthi.com

---

**Made with ❤️ for Indian Education**
