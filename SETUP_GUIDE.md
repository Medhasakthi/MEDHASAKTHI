# 🚀 MEDHASAKTHI Setup Guide

## Step 1: Update .env Configuration

The `.env` file is already created with all required fields. Update these values:

### 🔐 Security Keys (CRITICAL)
Generate strong random keys (32+ characters):
```bash
SECRET_KEY=your-super-secret-key-32-chars-minimum-production
JWT_SECRET_KEY=your-strong-jwt-secret-key-production
CSRF_SECRET_KEY=your-strong-csrf-secret-key-production
BACKUP_ENCRYPTION_KEY=your-strong-backup-key-production
```

### 🗄️ Database Configuration
```bash
POSTGRES_PASSWORD=your-strong-db-password
# Update the same password in DATABASE_URL
DATABASE_URL=postgresql://admin:your-strong-db-password@postgres:5432/medhasakthi
```

### 🔴 Redis Configuration
```bash
REDIS_PASSWORD=your-strong-redis-password
# Update the same password in REDIS_URL
REDIS_URL=redis://:your-strong-redis-password@redis:6379
```

### 🌐 Domain Configuration
```bash
DOMAIN=yourdomain.com
FRONTEND_URL=https://yourdomain.com
BACKEND_CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

### 📧 Email Configuration (Choose ONE)

**Option A: Gmail SMTP (Recommended)**
1. Enable 2FA on Gmail
2. Generate App Password: https://myaccount.google.com/apppasswords
```bash
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-16-char-app-password
```

**Option B: SendGrid**
```bash
SENDGRID_API_KEY=your-sendgrid-api-key
```

### 🤖 AI Services
```bash
OPENAI_API_KEY=sk-your-openai-api-key-here
```

### 💳 UPI Payment
```bash
UPI_ENABLED=true
UPI_PRIMARY_ID=yourbusiness@paytm
```

## Step 2: Deploy

### Windows:
```bash
deploy.bat
```

### Linux/macOS/WSL:
```bash
chmod +x deploy.sh
./deploy.sh
```

## Step 3: Access Your Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8080
- **API Docs**: http://localhost:8080/docs

## 🔧 Useful Commands

```bash
# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Restart services
docker-compose restart

# View running containers
docker-compose ps
```

## 🆘 Troubleshooting

### Common Issues:

1. **Port already in use**
   ```bash
   docker-compose down
   # Wait 30 seconds, then try again
   ```

2. **Database connection failed**
   - Check POSTGRES_PASSWORD in .env
   - Ensure passwords match in DATABASE_URL

3. **Email not working**
   - For Gmail: Use App Password, not regular password
   - Check SMTP settings

4. **AI features not working**
   - Verify OPENAI_API_KEY is correct
   - Check OpenAI account has credits

### Getting Help:
- Check logs: `docker-compose logs -f backend`
- Create GitHub issue
- Email: support@medhasakthi.com

---

**🎉 You're ready to go! Happy learning with MEDHASAKTHI!**
