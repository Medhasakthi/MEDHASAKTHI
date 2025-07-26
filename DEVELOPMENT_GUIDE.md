# 🚀 MEDHASAKTHI Development Guide

## Quick Start (Recommended)

### 1. Initial Setup
```bash
# Windows
dev-setup.bat

# Linux/macOS/WSL
chmod +x dev-setup.sh
./dev-setup.sh
```

### 2. Install Dependencies
```bash
npm install
npm run install:all
```

### 3. Start Development
```bash
# Option A: Start all services at once
npm run dev:all

# Option B: Start services individually
npm run dev:backend    # Backend API (http://localhost:8000)
npm run dev:frontend   # Frontend App (http://localhost:3000)
npm run dev:web-institute  # Institute Portal (http://localhost:3001)
npm run dev:web-student    # Student Portal (http://localhost:3002)
```

## 🔧 Development Commands

### Core Development
```bash
npm run dev:backend     # Start backend with hot reload
npm run dev:frontend    # Start frontend with hot reload
npm run dev:all         # Start all services concurrently
npm run dev:stop        # Stop all development services
npm run dev:restart     # Restart development services
npm run dev:logs        # View development logs
```

### Database & Services
```bash
# Database services only (PostgreSQL + Redis)
docker-compose -f docker-compose.dev.yml up -d postgres redis

# Reset database (WARNING: Deletes all data)
npm run dev:clean
```

### Testing & Quality
```bash
npm run test:frontend   # Run frontend tests
npm run test:backend    # Run backend tests
npm run lint:all        # Lint all code
npm run build:all       # Build all applications
```

## 🌐 Development URLs

| Service | URL | Description |
|---------|-----|-------------|
| Frontend | http://localhost:3000 | Main React application |
| Backend API | http://localhost:8000 | FastAPI backend |
| API Documentation | http://localhost:8000/docs | Swagger UI |
| Institute Portal | http://localhost:3001 | Next.js institute app |
| Student Portal | http://localhost:3002 | Next.js student app |
| Database | localhost:5432 | PostgreSQL (admin/devpassword123) |
| Redis | localhost:6379 | Redis cache (password: devredis123) |

## 📁 Project Structure

```
MEDHASAKTHI/
├── backend/              # FastAPI backend
│   ├── app/             # Application code
│   ├── alembic/         # Database migrations
│   ├── tests/           # Backend tests
│   └── requirements.txt # Python dependencies
├── frontend/            # React TypeScript frontend
│   ├── src/            # Source code
│   ├── public/         # Static assets
│   └── package.json    # Node dependencies
├── web-institute/       # Next.js institute portal
├── web-student/         # Next.js student portal
├── mobile-admin/        # React Native admin app
└── docker-compose.dev.yml # Development services
```

## 🔄 Development Workflow

### 1. Feature Development
```bash
# Start development environment
npm run dev:all

# Make your changes in respective directories
# - Backend: ./backend/
# - Frontend: ./frontend/src/
# - Institute: ./web-institute/src/
# - Student: ./web-student/src/

# Test your changes
npm run test:frontend
npm run test:backend
```

### 2. Database Changes
```bash
# Create migration (in backend container)
docker-compose -f docker-compose.dev.yml exec backend alembic revision --autogenerate -m "Your migration message"

# Apply migration
docker-compose -f docker-compose.dev.yml exec backend alembic upgrade head
```

### 3. Adding Dependencies

**Frontend:**
```bash
cd frontend
npm install package-name
```

**Backend:**
```bash
# Add to requirements.txt, then rebuild container
docker-compose -f docker-compose.dev.yml build backend
```

## 🐛 Troubleshooting

### Common Issues

**Port already in use:**
```bash
npm run dev:stop
# Wait 30 seconds
npm run dev:backend
```

**Database connection failed:**
```bash
# Check if database is running
docker-compose -f docker-compose.dev.yml ps

# Restart database
docker-compose -f docker-compose.dev.yml restart postgres
```

**Frontend not loading:**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm start
```

**Backend not starting:**
```bash
# Check logs
npm run dev:logs

# Rebuild backend
docker-compose -f docker-compose.dev.yml build backend
```

### Reset Everything
```bash
# Nuclear option - resets everything
npm run dev:clean
npm run install:all
npm run dev:all
```

## 🚀 Moving to Production

When ready to deploy:

1. **Test locally first:**
   ```bash
   npm run build:all
   npm run test:frontend
   npm run test:backend
   ```

2. **Update production environment:**
   - Copy `.env.development` to `.env`
   - Update all passwords and secrets
   - Set `ENVIRONMENT=production`

3. **Deploy:**
   ```bash
   # Windows
   deploy.bat
   
   # Linux/macOS
   ./deploy.sh
   ```

## 💡 Tips

- **Hot Reload**: All services support hot reload - changes reflect immediately
- **Database**: Development database is separate from production
- **Logs**: Use `npm run dev:logs` to debug issues
- **Performance**: Only run services you're actively developing
- **Testing**: Always test locally before pushing to git

---

**Happy coding! 🎉**
