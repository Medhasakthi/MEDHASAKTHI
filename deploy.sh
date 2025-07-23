#!/bin/bash

# MEDHASAKTHI Production Deployment Script
# This script automates the complete deployment process

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
DOMAIN=${DOMAIN:-"medhasakthi.com"}
EMAIL=${EMAIL:-"support@medhasakthi.com"}
ENVIRONMENT=${ENVIRONMENT:-"production"}
BACKUP_ENABLED=${BACKUP_ENABLED:-"true"}

echo -e "${GREEN}🎉 Deploying MEDHASAKTHI to production domain: $DOMAIN${NC}"

echo -e "${BLUE}🚀 MEDHASAKTHI Production Deployment Script${NC}"
echo -e "${BLUE}===========================================${NC}"
echo ""

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Pre-deployment checks
echo -e "${BLUE}🔍 Running pre-deployment checks...${NC}"

# Check required commands
REQUIRED_COMMANDS=("docker" "docker-compose" "git" "curl" "openssl")
for cmd in "${REQUIRED_COMMANDS[@]}"; do
    if command_exists "$cmd"; then
        print_status "$cmd is installed"
    else
        print_error "$cmd is not installed. Please install it first."
        exit 1
    fi
done

# Check if running as root or with sudo
if [[ $EUID -eq 0 ]]; then
    print_warning "Running as root. This is not recommended for production."
fi

# Check available disk space (minimum 10GB)
AVAILABLE_SPACE=$(df / | awk 'NR==2 {print $4}')
if [[ $AVAILABLE_SPACE -lt 10485760 ]]; then  # 10GB in KB
    print_error "Insufficient disk space. At least 10GB required."
    exit 1
fi

print_status "Pre-deployment checks completed"
echo ""

# Environment setup
echo -e "${BLUE}⚙️  Setting up environment...${NC}"

# Create necessary directories
mkdir -p /app/logs
mkdir -p /app/backups
mkdir -p /app/uploads
mkdir -p /app/certificates
mkdir -p /app/static

# Set proper permissions
chmod 755 /app/logs
chmod 755 /app/backups
chmod 755 /app/uploads
chmod 755 /app/certificates

print_status "Directories created and permissions set"

# Generate secure secrets if not provided
if [[ ! -f ".env" ]]; then
    print_info "Generating production environment file..."
    
    # Generate secure random secrets
    SECRET_KEY=$(openssl rand -hex 32)
    JWT_SECRET=$(openssl rand -hex 32)
    CSRF_SECRET=$(openssl rand -hex 32)
    BACKUP_KEY=$(openssl rand -base64 32)
    
    # Create .env file from template
    cp backend/.env.example .env
    
    # Replace placeholders with actual values
    sed -i "s/your-secret-key-here/$SECRET_KEY/g" .env
    sed -i "s/your-jwt-secret-here/$JWT_SECRET/g" .env
    sed -i "s/your-csrf-secret-key-here/$CSRF_SECRET/g" .env
    sed -i "s/your-backup-encryption-key-here/$BACKUP_KEY/g" .env
    sed -i "s/development/$ENVIRONMENT/g" .env
    sed -i "s/admin@medhasakthi.com/$EMAIL/g" .env
    
    print_status "Environment file created with secure secrets"
else
    print_info "Using existing .env file"
fi

# SSL Certificate setup
echo ""
echo -e "${BLUE}🔒 Setting up SSL certificates...${NC}"

if [[ ! -f "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" ]]; then
    print_info "Setting up Let's Encrypt SSL certificate for $DOMAIN"
    
    # Install certbot if not present
    if ! command_exists certbot; then
        print_info "Installing certbot..."
        if command_exists apt-get; then
            sudo apt-get update
            sudo apt-get install -y certbot python3-certbot-nginx
        elif command_exists yum; then
            sudo yum install -y certbot python3-certbot-nginx
        else
            print_error "Unable to install certbot. Please install manually."
            exit 1
        fi
    fi
    
    # Generate SSL certificate
    print_info "Generating SSL certificate for $DOMAIN"
    sudo certbot certonly --standalone -d $DOMAIN -d www.$DOMAIN --email $EMAIL --agree-tos --non-interactive
    
    if [[ $? -eq 0 ]]; then
        print_status "SSL certificate generated successfully"
    else
        print_error "SSL certificate generation failed"
        exit 1
    fi
else
    print_status "SSL certificate already exists"
fi

# Update nginx configuration with domain
echo ""
echo -e "${BLUE}🌐 Configuring nginx...${NC}"

# Create nginx configuration
cat > nginx.conf << EOF
server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN;
    return 301 https://\$server_name\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name $DOMAIN www.$DOMAIN;

    ssl_certificate /etc/letsencrypt/live/$DOMAIN/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/$DOMAIN/privkey.pem;
    
    # SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Content-Type-Options nosniff always;
    add_header X-Frame-Options DENY always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;

    # Frontend
    location / {
        proxy_pass http://frontend:3000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    # Backend API
    location /api/ {
        proxy_pass http://backend:8000/api/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # Increase timeout for long-running requests
        proxy_read_timeout 300;
        proxy_connect_timeout 300;
        proxy_send_timeout 300;
    }

    # Static files
    location /static/ {
        alias /app/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Health check
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
}
EOF

print_status "Nginx configuration created"

# Database setup
echo ""
echo -e "${BLUE}🗄️  Setting up database...${NC}"

# Start database container first
docker-compose up -d postgres redis

# Wait for database to be ready
print_info "Waiting for database to be ready..."
sleep 30

# Run database migrations
print_info "Running database migrations..."
docker-compose exec -T backend alembic upgrade head

if [[ $? -eq 0 ]]; then
    print_status "Database migrations completed"
else
    print_error "Database migrations failed"
    exit 1
fi

# Build and start all services
echo ""
echo -e "${BLUE}🏗️  Building and starting services...${NC}"

# Build images
print_info "Building Docker images..."
docker-compose build --no-cache

# Start all services
print_info "Starting all services..."
docker-compose up -d

# Wait for services to be ready
print_info "Waiting for services to start..."
sleep 60

# Health checks
echo ""
echo -e "${BLUE}🏥 Running health checks...${NC}"

# Check backend health
BACKEND_HEALTH=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health)
if [[ $BACKEND_HEALTH -eq 200 ]]; then
    print_status "Backend service is healthy"
else
    print_error "Backend service health check failed (HTTP $BACKEND_HEALTH)"
fi

# Check frontend health
FRONTEND_HEALTH=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000)
if [[ $FRONTEND_HEALTH -eq 200 ]]; then
    print_status "Frontend service is healthy"
else
    print_error "Frontend service health check failed (HTTP $FRONTEND_HEALTH)"
fi

# Check database connection
DB_HEALTH=$(docker-compose exec -T backend python -c "from app.core.database import db_manager; print('OK' if db_manager.check_db_connection() else 'FAIL')")
if [[ $DB_HEALTH == *"OK"* ]]; then
    print_status "Database connection is healthy"
else
    print_error "Database connection health check failed"
fi

# Setup monitoring
echo ""
echo -e "${BLUE}📊 Setting up monitoring...${NC}"

# Start monitoring services
docker-compose up -d prometheus grafana

print_status "Monitoring services started"

# Setup backup cron job
if [[ $BACKUP_ENABLED == "true" ]]; then
    echo ""
    echo -e "${BLUE}💾 Setting up automated backups...${NC}"
    
    # Create backup script
    cat > /usr/local/bin/medhasakthi-backup.sh << 'EOF'
#!/bin/bash
cd /app
docker-compose exec -T backend python -c "
import asyncio
from app.services.backup_service import backup_service
asyncio.run(backup_service.create_full_backup())
"
EOF
    
    chmod +x /usr/local/bin/medhasakthi-backup.sh
    
    # Add to crontab (daily at 2 AM)
    (crontab -l 2>/dev/null; echo "0 2 * * * /usr/local/bin/medhasakthi-backup.sh") | crontab -
    
    print_status "Automated backups configured"
fi

# Final verification
echo ""
echo -e "${BLUE}🔍 Final verification...${NC}"

# Test HTTPS endpoint
HTTPS_TEST=$(curl -s -o /dev/null -w "%{http_code}" https://$DOMAIN/health)
if [[ $HTTPS_TEST -eq 200 ]]; then
    print_status "HTTPS endpoint is working"
else
    print_warning "HTTPS endpoint test failed (HTTP $HTTPS_TEST)"
fi

# Display deployment summary
echo ""
echo -e "${GREEN}🎉 DEPLOYMENT COMPLETED SUCCESSFULLY! 🎉${NC}"
echo -e "${GREEN}====================================${NC}"
echo ""
echo -e "${BLUE}📋 Deployment Summary:${NC}"
echo -e "   🌐 Domain: https://$DOMAIN"
echo -e "   🔒 SSL: Enabled with Let's Encrypt"
echo -e "   🗄️  Database: PostgreSQL with Redis"
echo -e "   📊 Monitoring: Prometheus + Grafana"
echo -e "   💾 Backups: $(if [[ $BACKUP_ENABLED == "true" ]]; then echo "Enabled (daily)"; else echo "Disabled"; fi)"
echo -e "   📧 Admin Email: $EMAIL"
echo ""
echo -e "${BLUE}🔗 Important URLs:${NC}"
echo -e "   🏠 Main Site: https://$DOMAIN"
echo -e "   🔧 API Docs: https://$DOMAIN/api/docs"
echo -e "   📊 Grafana: https://$DOMAIN:3001 (admin/admin)"
echo -e "   🔍 Prometheus: https://$DOMAIN:9090"
echo ""
echo -e "${BLUE}📝 Next Steps:${NC}"
echo -e "   1. Update DNS records to point to this server"
echo -e "   2. Test all functionality thoroughly"
echo -e "   3. Set up monitoring alerts"
echo -e "   4. Configure backup notifications"
echo -e "   5. Launch marketing campaign!"
echo ""
echo -e "${GREEN}🚀 MEDHASAKTHI is now live and ready to serve users! 🚀${NC}"
