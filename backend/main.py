"""
MEDHASAKTHI FastAPI Application
"""
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import time
import logging

from app.core.config import settings, get_cors_origins
from app.core.database import create_tables, db_manager
from app.api.v1.auth import router as auth_router
from app.middleware.security_middleware import (
    security_headers_middleware,
    advanced_rate_limit_middleware,
    threat_detection_middleware,
    device_tracking_middleware,
    compliance_middleware
)
from app.middleware.advanced_security_middleware import advanced_security_middleware
from app.middleware.csrf_middleware import csrf_middleware
from app.integrations.sentry_integration import sentry_middleware, sentry_manager


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting MEDHASAKTHI API...")
    
    # Check database connection
    if db_manager.check_connection():
        logger.info("✅ Database connection successful")
        # Create tables if they don't exist
        create_tables()
        logger.info("✅ Database tables ready")
    else:
        logger.error("❌ Database connection failed")
    
    # Check Redis connection
    if db_manager.check_redis_connection():
        logger.info("✅ Redis connection successful")
    else:
        logger.warning("⚠️ Redis connection failed - some features may not work")

    # Initialize Sentry for error tracking
    sentry_manager.initialize()
    logger.info("✅ Sentry integration initialized")

    logger.info("🚀 MEDHASAKTHI API started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down MEDHASAKTHI API...")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-Powered Adaptive Examination Platform API",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Add trusted host middleware for production
if not settings.DEBUG:
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["medhasakthi.com", "*.medhasakthi.com", "localhost"]
    )

# Add advanced security middleware
app.add_middleware(csrf_middleware)  # CSRF protection
app.add_middleware(advanced_security_middleware)  # New comprehensive security middleware
app.add_middleware(sentry_middleware)  # Sentry error tracking and performance monitoring
app.add_middleware(security_headers_middleware)
app.add_middleware(advanced_rate_limit_middleware)
app.add_middleware(threat_detection_middleware)
app.add_middleware(device_tracking_middleware)
app.add_middleware(compliance_middleware)


# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add processing time to response headers"""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


# Note: Security headers are now handled by advanced security middleware


# Exception handlers
@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    """Handle 404 errors"""
    return JSONResponse(
        status_code=404,
        content={
            "error": "Not Found",
            "message": "The requested resource was not found",
            "path": str(request.url.path)
        }
    )


@app.exception_handler(500)
async def internal_error_handler(request: Request, exc):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred"
        }
    )


# Health check endpoints
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "version": settings.APP_VERSION
    }


@app.get("/health/detailed")
async def detailed_health_check():
    """Detailed health check with database and Redis status"""
    db_status = db_manager.get_db_info()
    redis_status = db_manager.get_redis_info()
    
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "version": settings.APP_VERSION,
        "database": db_status,
        "redis": redis_status,
        "environment": "development" if settings.DEBUG else "production"
    }


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to MEDHASAKTHI API",
        "version": settings.APP_VERSION,
        "docs": "/docs" if settings.DEBUG else "Documentation not available in production",
        "health": "/health"
    }


# API version info
@app.get("/api/v1")
async def api_v1_info():
    """API v1 information"""
    return {
        "version": "1.0",
        "endpoints": {
            "authentication": "/api/v1/auth",
            "ai_services": "/api/v1/ai",
            "certificates": "/api/v1/certificates",
            "talent_exams": "/api/v1/talent-exams",
            "admin": "/api/v1/admin",
            "institute": "/api/v1/institute",
            "student": "/api/v1/student",
            "websocket": "/api/v1/ws",
            "integrations": "/api/v1/integrations",
            "monitoring": "/api/v1/monitoring",
            "subjects": "/api/v1/subjects"
        }
    }


# Include routers
app.include_router(
    auth_router,
    prefix="/api/v1/auth",
    tags=["Authentication"]
)

# Import and include AI router
from app.api.v1.ai import router as ai_router
app.include_router(
    ai_router,
    prefix="/api/v1/ai",
    tags=["AI Services"]
)

# Import and include Certificate router
from app.api.v1.certificates import router as certificate_router
app.include_router(
    certificate_router,
    prefix="/api/v1/certificates",
    tags=["Certificates"]
)

# Import and include Talent Exam router
from app.api.v1.talent_exams.routes import router as talent_exam_router
app.include_router(
    talent_exam_router,
    prefix="/api/v1/talent-exams",
    tags=["Talent Exams"]
)

# Import and include Admin router
from app.api.v1.admin.routes import router as admin_router
app.include_router(
    admin_router,
    prefix="/api/v1/admin",
    tags=["Admin"]
)

# Import and include Institute router
from app.api.v1.institute.routes import router as institute_router
app.include_router(
    institute_router,
    prefix="/api/v1/institute",
    tags=["Institute"]
)

# Import and include Student router
from app.api.v1.student.routes import router as student_router
app.include_router(
    student_router,
    prefix="/api/v1/student",
    tags=["Student"]
)

# Import and include Teacher router
from app.api.v1.teacher.routes import router as teacher_router
app.include_router(
    teacher_router,
    prefix="/api/v1/teacher",
    tags=["Teacher"]
)

# Import and include UPI Payments router
from app.api.v1.payments.upi_routes import router as upi_router
app.include_router(
    upi_router,
    prefix="/api/v1/payments/upi",
    tags=["UPI Payments"]
)

# Import and include Independent Learner router
from app.api.v1.independent.routes import router as independent_router
app.include_router(
    independent_router,
    prefix="/api/v1/independent",
    tags=["Independent Learners"]
)

# Import and include WebSocket router
from app.api.v1.websocket.routes import router as websocket_router
app.include_router(
    websocket_router,
    prefix="/api/v1/ws",
    tags=["WebSocket"]
)

# Import and include Integration router
from app.api.v1.integrations.routes import router as integrations_router
app.include_router(
    integrations_router,
    prefix="/api/v1/integrations",
    tags=["Enterprise Integrations"]
)

# Import and include Monitoring router
from app.api.v1.monitoring.routes import router as monitoring_router
app.include_router(
    monitoring_router,
    prefix="/api/v1/monitoring",
    tags=["Monitoring & Observability"]
)

# Import and include Subjects router
from app.api.v1.subjects.routes import router as subjects_router
app.include_router(
    subjects_router,
    prefix="/api/v1/subjects",
    tags=["School Subjects & Curriculum"]
)

# Import and include Load Balancer router
from app.api.v1.endpoints.load_balancer import router as load_balancer_router
app.include_router(
    load_balancer_router,
    prefix="/api/v1/load-balancer",
    tags=["Load Balancer Management"]
)

# Placeholder for other routers (to be implemented)
# app.include_router(admin_router, prefix="/api/v1/admin", tags=["Admin"])
# app.include_router(institute_router, prefix="/api/v1/institute", tags=["Institute"])
# app.include_router(student_router, prefix="/api/v1/student", tags=["Student"])


# Development endpoints (only available in debug mode)
if settings.DEBUG:
    @app.get("/debug/config")
    async def debug_config():
        """Debug configuration (development only)"""
        return {
            "app_name": settings.APP_NAME,
            "debug": settings.DEBUG,
            "database_url": settings.DATABASE_URL.split("@")[1] if "@" in settings.DATABASE_URL else "hidden",
            "redis_url": settings.REDIS_URL,
            "cors_origins": settings.BACKEND_CORS_ORIGINS,
            "frontend_url": settings.FRONTEND_URL
        }
    
    @app.post("/debug/test-email")
    async def test_email(email_data: dict):
        """Test email sending (development only)"""
        from app.services.email_service import email_service
        
        success = await email_service.send_verification_email(
            email_data.get("email", "test@example.com"),
            email_data.get("name", "Test User"),
            "test-token-123"
        )
        
        return {
            "success": success,
            "message": "Test email sent" if success else "Email sending failed"
        }


# Startup message
@app.on_event("startup")
async def startup_message():
    """Print startup message and initialize services"""
    print("\n" + "="*60)
    print("🚀 MEDHASAKTHI API Server Started")
    print("="*60)
    print(f"📱 Application: {settings.APP_NAME}")
    print(f"🔢 Version: {settings.APP_VERSION}")
    print(f"🌍 Environment: {'Development' if settings.DEBUG else 'Production'}")
    print(f"📚 Documentation: http://localhost:8080/docs" if settings.DEBUG else "📚 Documentation: Disabled in production")
    print(f"🏥 Health Check: http://localhost:8080/health")
    print("="*60)

    # Start scaling scheduler
    print("⚖️ Starting auto-scaling scheduler...")
    from app.services.scaling_scheduler import scaling_scheduler
    await scaling_scheduler.start()

    print("✅ Ready to serve requests!")
    print("="*60 + "\n")

@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event"""
    print("\n🛑 MEDHASAKTHI API Server Shutting Down...")

    # Stop scaling scheduler
    from app.services.scaling_scheduler import scaling_scheduler
    await scaling_scheduler.stop()

    print("✅ Shutdown completed!")


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8080,
        reload=settings.DEBUG,
        log_level="info"
    )
