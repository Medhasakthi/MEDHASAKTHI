# 🚀 MEDHASAKTHI Quick Start Guide

## ⚡ One-Command Setup (Recommended)

Since you haven't installed any software yet, use this single command to install everything and deploy MEDHASAKTHI:

```bash
chmod +x setup-medhasakthi.sh && ./setup-medhasakthi.sh
```

This will automatically:
- ✅ Install Docker, Node.js, Python, and all dependencies
- ✅ Configure local DNS for medhasakthi.com
- ✅ Generate SSL certificates
- ✅ Deploy the complete MEDHASAKTHI platform
- ✅ Set up monitoring and analytics

## 📋 What Gets Installed

### Required Software
- **Docker & Docker Compose**: Container orchestration
- **Git**: Version control
- **OpenSSL**: SSL certificate generation
- **Curl/Wget**: Download utilities

### Optional Development Tools
- **Node.js & npm**: Frontend development
- **Python & pip**: Backend development

### MEDHASAKTHI Services
- **PostgreSQL**: Database
- **Redis**: Caching and sessions
- **FastAPI Backend**: API server
- **React Frontend**: Web applications
- **Nginx**: Reverse proxy with SSL
- **Prometheus**: Monitoring
- **Grafana**: Analytics dashboard

## 🌐 Access URLs (After Setup)

### Main Application
- 🏠 **Landing Page**: https://medhasakthi.com
- 👨‍🎓 **Student Portal**: https://student.medhasakthi.com
- 👨‍🏫 **Teacher Portal**: https://teacher.medhasakthi.com
- 🏢 **Admin Portal**: https://admin.medhasakthi.com
- 🎯 **Learn Portal**: https://learn.medhasakthi.com

### Development Tools
- 🔧 **API Documentation**: https://api.medhasakthi.com/docs
- 📊 **Grafana Dashboard**: http://localhost:3001 (admin/admin123)
- 🔍 **Prometheus Metrics**: http://localhost:9090

## 👤 Default Login

```
Email: admin@medhasakthi.com
Password: admin123
```

## 🔧 Manual Setup (If Needed)

If you prefer to run steps manually:

### 1. Install Dependencies
```bash
chmod +x install-dependencies.sh
./install-dependencies.sh
```

### 2. Deploy MEDHASAKTHI
```bash
chmod +x deploy-local.sh
sudo ./deploy-local.sh
```

### 3. Install SSL Certificates
```bash
chmod +x install-ssl-certificate.sh
./install-ssl-certificate.sh
```

## 🛠️ Post-Setup Configuration

### 1. Update Environment Variables
Edit the `.env` file to configure:

```bash
# Email Configuration (Required for user verification)
EMAIL_USERNAME=your-email@gmail.com
EMAIL_PASSWORD=your-app-password

# OpenAI API Key (Required for AI features)
OPENAI_API_KEY=your-openai-api-key-here

# Optional: Error tracking
SENTRY_DSN=your-sentry-dsn
```

### 2. Test the Application
1. Visit https://medhasakthi.com
2. Click "Login / Sign Up"
3. Select a user category (Student, Teacher, Admin, Learner)
4. Test the redirect to appropriate portal

## 🔄 Common Commands

### View Logs
```bash
docker-compose -f docker-compose.local.yml logs -f
```

### Restart Services
```bash
docker-compose -f docker-compose.local.yml restart
```

### Stop Application
```bash
docker-compose -f docker-compose.local.yml down
```

### Start Application
```bash
docker-compose -f docker-compose.local.yml up -d
```

### Restore Real DNS (Access real medhasakthi.com)
```bash
./restore-dns.sh
```

## 🐛 Troubleshooting

### SSL Certificate Warnings
If you see "Your connection is not private":
```bash
./install-ssl-certificate.sh
```
Then restart your browser.

### Docker Not Running
```bash
# Linux
sudo systemctl start docker

# Windows/macOS
# Start Docker Desktop manually
```

### Services Not Starting
```bash
# Check logs
docker-compose -f docker-compose.local.yml logs

# Check Docker status
docker info
```

### Domain Not Resolving
Check if DNS entries are in `/etc/hosts`:
```bash
cat /etc/hosts | grep medhasakthi
```

## 📞 Support

If you encounter issues:
1. Check the logs: `docker-compose -f docker-compose.local.yml logs`
2. Verify Docker is running: `docker info`
3. Check DNS configuration: `cat /etc/hosts | grep medhasakthi`
4. Restart services: `docker-compose -f docker-compose.local.yml restart`

## 🎯 Success Indicators

Your setup is successful when:
- ✅ https://medhasakthi.com loads without SSL warnings
- ✅ Category selection works in login flow
- ✅ All subdomains are accessible
- ✅ API documentation loads at https://api.medhasakthi.com/docs
- ✅ Grafana dashboard is accessible at http://localhost:3001

## 🚀 Next Steps

1. **Configure Email**: Set up SMTP for user verification
2. **Add API Keys**: Configure OpenAI for AI question generation
3. **Test Features**: Create users, exams, and test payments
4. **Customize**: Update branding, logos, and content
5. **Plan Production**: Prepare for real server deployment

---

## ⚡ TL;DR - Just Run This:

```bash
chmod +x setup-medhasakthi.sh && ./setup-medhasakthi.sh
```

Then visit: **https://medhasakthi.com** 🎉
