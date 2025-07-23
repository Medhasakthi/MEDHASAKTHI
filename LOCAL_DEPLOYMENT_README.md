# 🏠 MEDHASAKTHI Local Desktop Deployment

## 🎯 Overview
Deploy MEDHASAKTHI on your local desktop/PC while using your real domain `medhasakthi.com`. This setup allows you to:

- ✅ Use your actual domain `medhasakthi.com` locally
- ✅ Test all subdomains (student, teacher, admin, learn)
- ✅ Automatic DNS and SSL configuration
- ✅ Full production-like environment
- ✅ Easy migration to cloud later

## 🚀 Quick Start (One Command Deployment)

```bash
# Clone the repository (if not already done)
git clone https://github.com/yourusername/medhasakthi.git
cd medhasakthi

# Run the automated deployment script
sudo ./deploy-local.sh
```

That's it! The script will automatically:
1. Configure local DNS for all subdomains
2. Generate SSL certificates
3. Set up Docker containers
4. Deploy the complete application

## 📋 Prerequisites

### System Requirements
- **OS**: Linux, macOS, or Windows (with WSL)
- **RAM**: Minimum 4GB (8GB recommended)
- **Storage**: 50GB+ free space
- **CPU**: 2+ cores

### Required Software
- **Docker Desktop**: [Download here](https://www.docker.com/products/docker-desktop)
- **Git**: For cloning the repository
- **OpenSSL**: For certificate generation (usually pre-installed)

## 🌐 How It Works

### Local DNS Configuration
The script automatically adds these entries to your `/etc/hosts` file:
```
127.0.0.1    medhasakthi.com
127.0.0.1    www.medhasakthi.com
127.0.0.1    api.medhasakthi.com
127.0.0.1    admin.medhasakthi.com
127.0.0.1    student.medhasakthi.com
127.0.0.1    teacher.medhasakthi.com
127.0.0.1    learn.medhasakthi.com
```

### SSL Certificate Generation
- Generates a comprehensive SSL certificate for all subdomains
- Self-signed certificate valid for 365 days
- Includes all necessary Subject Alternative Names (SANs)

### Docker Services
The deployment includes:
- **PostgreSQL**: Database server
- **Redis**: Caching and sessions
- **Backend API**: FastAPI application
- **Frontend**: React landing page
- **Nginx**: Reverse proxy with SSL termination
- **Prometheus**: Monitoring
- **Grafana**: Analytics dashboard

## 🔧 Manual Configuration Steps

### 1. Environment Variables
Update `.env` file with your specific values:
```bash
# Email Configuration (Required for full functionality)
EMAIL_USERNAME=your-email@gmail.com
EMAIL_PASSWORD=your-app-password

# OpenAI API Key (Required for AI features)
OPENAI_API_KEY=your-openai-api-key-here

# Other optional configurations
SENTRY_DSN=your-sentry-dsn-for-error-tracking
```

### 2. SSL Certificate Installation
To avoid browser security warnings:
```bash
# Run the SSL certificate installer
./install-ssl-certificate.sh
```

This will add the certificate to your system's trusted store.

## 🌍 Access URLs

After deployment, access your application at:

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

## 👤 Default Admin Account

```
Email: admin@medhasakthi.com
Password: admin123
```

**⚠️ Important**: Change this password immediately after first login!

## 🔄 Common Commands

### View Logs
```bash
# View all service logs
docker-compose -f docker-compose.local.yml logs -f

# View specific service logs
docker-compose -f docker-compose.local.yml logs -f backend
docker-compose -f docker-compose.local.yml logs -f frontend
```

### Restart Services
```bash
# Restart all services
docker-compose -f docker-compose.local.yml restart

# Restart specific service
docker-compose -f docker-compose.local.yml restart backend
```

### Stop/Start Application
```bash
# Stop all services
docker-compose -f docker-compose.local.yml down

# Start all services
docker-compose -f docker-compose.local.yml up -d
```

### Database Operations
```bash
# Access database
docker-compose -f docker-compose.local.yml exec postgres psql -U medhasakthi_user -d medhasakthi

# Run migrations
docker-compose -f docker-compose.local.yml exec backend alembic upgrade head

# Create backup
./backup-local.sh
```

## 🔒 Security Considerations

### For Local Development
- ✅ Self-signed certificates are acceptable
- ✅ Default passwords are fine for testing
- ✅ Debug mode can be enabled

### Before Going Live
- ❌ Replace self-signed certificates with real SSL
- ❌ Change all default passwords
- ❌ Disable debug mode
- ❌ Configure proper email service
- ❌ Set up monitoring and backups

## 🚀 Migration to Production

When ready to deploy to a real server:

### Option 1: Cloud Migration
```bash
# Export data
docker-compose -f docker-compose.local.yml exec backend python scripts/export_data.py

# Deploy to cloud platform (Heroku, AWS, etc.)
# Import data to cloud database
```

### Option 2: VPS Migration
```bash
# Create backup
./backup-local.sh

# Copy backup to VPS
scp backups/latest.sql user@your-server:/path/to/medhasakthi/

# Deploy on VPS using production script
ssh user@your-server
cd /path/to/medhasakthi
./deploy-production.sh
```

## 🛠️ Troubleshooting

### Common Issues

#### 1. Browser Security Warnings
**Problem**: "Your connection is not private" error
**Solution**: 
```bash
./install-ssl-certificate.sh
# Then restart your browser
```

#### 2. Domain Not Resolving
**Problem**: medhasakthi.com not loading
**Solution**: Check `/etc/hosts` file has the entries:
```bash
cat /etc/hosts | grep medhasakthi
```

#### 3. Docker Services Not Starting
**Problem**: Services failing to start
**Solution**: 
```bash
# Check Docker is running
docker info

# Check logs
docker-compose -f docker-compose.local.yml logs
```

#### 4. Port Conflicts
**Problem**: Ports 80/443 already in use
**Solution**: Stop conflicting services:
```bash
# Stop Apache/Nginx if running
sudo systemctl stop apache2 nginx

# Or change ports in docker-compose.local.yml
```

### Getting Help

1. **Check Logs**: Always start with `docker-compose logs`
2. **Health Checks**: Visit https://api.medhasakthi.com/health
3. **Database**: Ensure PostgreSQL is running and accessible
4. **DNS**: Verify `/etc/hosts` entries are correct
5. **SSL**: Ensure certificates are generated and trusted

## 📞 Support

For issues or questions:
- 📧 Email: admin@medhasakthi.com
- 📱 Phone: +91-XXXX-XXXX
- 💬 GitHub Issues: Create an issue in the repository

## 🎉 Success Indicators

Your deployment is successful when:
- ✅ https://medhasakthi.com loads without SSL warnings
- ✅ All subdomains are accessible
- ✅ Login flow works with category selection
- ✅ API documentation is available
- ✅ Database connections are healthy
- ✅ Email verification works (if configured)

---

## 🔄 Next Steps

1. **Configure Email**: Set up SMTP for user verification
2. **Add API Keys**: Configure OpenAI for AI features
3. **Test Features**: Try creating users, exams, payments
4. **Customize Branding**: Update logos, colors, content
5. **Plan Production**: Prepare for real domain deployment

**🎯 You now have a fully functional MEDHASAKTHI platform running locally with your real domain!**
