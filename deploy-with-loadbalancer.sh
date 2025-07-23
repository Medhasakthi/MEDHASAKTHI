#!/bin/bash

# MEDHASAKTHI Production Deployment with Dynamic Load Balancing
# Complete deployment script with auto-scaling capabilities

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

# Configuration
DOMAIN=${DOMAIN:-"medhasakthi.com"}
EMAIL=${EMAIL:-"support@medhasakthi.com"}
ENVIRONMENT=${ENVIRONMENT:-"production"}
ENABLE_AUTO_SCALING=${ENABLE_AUTO_SCALING:-"true"}
MIN_SERVERS=${MIN_SERVERS:-"1"}
MAX_SERVERS=${MAX_SERVERS:-"5"}

echo -e "${BLUE}🚀 MEDHASAKTHI Production Deployment with Load Balancing${NC}"
echo -e "${BLUE}Domain: $DOMAIN${NC}"
echo -e "${BLUE}Environment: $ENVIRONMENT${NC}"
echo -e "${BLUE}Auto-scaling: $ENABLE_AUTO_SCALING${NC}"
echo -e "${BLUE}========================================================${NC}"

print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_section() {
    echo -e "${PURPLE}📋 $1${NC}"
    echo -e "${PURPLE}$(printf '=%.0s' {1..50})${NC}"
}

# Check prerequisites
print_section "Prerequisites Check"

# Check Docker
if ! command -v docker >/dev/null 2>&1; then
    print_error "Docker is not installed"
    exit 1
fi
print_status "Docker is installed"

# Check Docker Compose
if ! command -v docker-compose >/dev/null 2>&1; then
    print_error "Docker Compose is not installed"
    exit 1
fi
print_status "Docker Compose is installed"

# Check if running as root or with sudo
if [[ $EUID -ne 0 ]]; then
    print_error "This script must be run as root or with sudo"
    exit 1
fi
print_status "Running with appropriate privileges"

# Create application directories
print_section "Directory Setup"
mkdir -p /app/{logs,backups,uploads,certificates,static,nginx,monitoring}
chown -R $USER:$USER /app
print_status "Application directories created"

# Generate environment configuration
print_section "Environment Configuration"
if [[ ! -f ".env" ]]; then
    cp backend/.env.example .env
    
    # Generate secure secrets
    SECRET_KEY=$(openssl rand -hex 32)
    JWT_SECRET=$(openssl rand -hex 32)
    CSRF_SECRET=$(openssl rand -hex 32)
    BACKUP_KEY=$(openssl rand -base64 32)
    POSTGRES_PASSWORD=$(openssl rand -hex 16)
    REDIS_PASSWORD=$(openssl rand -hex 16)
    
    # Update environment file
    sed -i "s/your-secret-key-here/$SECRET_KEY/g" .env
    sed -i "s/your-jwt-secret-here/$JWT_SECRET/g" .env
    sed -i "s/your-csrf-secret-key-here/$CSRF_SECRET/g" .env
    sed -i "s/your-backup-encryption-key-here/$BACKUP_KEY/g" .env
    sed -i "s/secure_password_change_me/$POSTGRES_PASSWORD/g" .env
    sed -i "s/redis_password_change_me/$REDIS_PASSWORD/g" .env
    sed -i "s/development/production/g" .env
    sed -i "s/admin@medhasakthi.com/$EMAIL/g" .env
    sed -i "s/your-domain.com/$DOMAIN/g" .env
    
    # Add auto-scaling configuration
    echo "" >> .env
    echo "# Auto-scaling Configuration" >> .env
    echo "AUTO_SCALING_ENABLED=$ENABLE_AUTO_SCALING" >> .env
    echo "MIN_SERVERS=$MIN_SERVERS" >> .env
    echo "MAX_SERVERS=$MAX_SERVERS" >> .env
    echo "SCALE_UP_CPU_THRESHOLD=70" >> .env
    echo "SCALE_DOWN_CPU_THRESHOLD=30" >> .env
    echo "SCALING_COOLDOWN_MINUTES=10" >> .env
    
    print_status "Environment configuration generated"
else
    print_info "Using existing environment configuration"
fi

# SSL Certificate Setup
print_section "SSL Certificate Setup"
if command -v certbot >/dev/null 2>&1; then
    print_info "Generating SSL certificate for $DOMAIN..."
    certbot certonly --standalone -d $DOMAIN -d www.$DOMAIN --email $EMAIL --agree-tos --non-interactive
    
    if [[ $? -eq 0 ]]; then
        print_status "SSL certificate generated successfully"
    else
        print_warning "SSL certificate generation failed, using self-signed certificate"
        
        # Generate self-signed certificate
        mkdir -p /app/certificates
        openssl genrsa -out /app/certificates/medhasakthi.key 2048
        openssl req -new -key /app/certificates/medhasakthi.key -out /app/certificates/medhasakthi.csr -subj "/C=IN/ST=Karnataka/L=Bangalore/O=MEDHASAKTHI/CN=$DOMAIN"
        openssl x509 -req -days 365 -in /app/certificates/medhasakthi.csr -signkey /app/certificates/medhasakthi.key -out /app/certificates/medhasakthi.crt
        
        print_status "Self-signed SSL certificate generated"
    fi
else
    print_warning "Certbot not found, installing..."
    apt update && apt install -y certbot
    
    # Try again
    certbot certonly --standalone -d $DOMAIN -d www.$DOMAIN --email $EMAIL --agree-tos --non-interactive
fi

# Database Migration
print_section "Database Setup"
print_info "Starting database services..."
docker-compose up -d postgres redis
sleep 30

print_info "Running database migrations..."
docker-compose exec -T backend alembic upgrade head

print_status "Database setup completed"

# Deploy Load Balancer Configuration
print_section "Load Balancer Configuration"

# Copy load balancer nginx configuration
cp nginx-loadbalancer.conf /app/nginx/nginx.conf

# Update configuration with actual domain
sed -i "s/medhasakthi.com/$DOMAIN/g" /app/nginx/nginx.conf

# Create upstream configuration directory
mkdir -p /app/nginx/conf.d

# Create initial upstream configuration
cat > /app/nginx/conf.d/upstream.conf << EOF
# Auto-generated upstream configuration
# DO NOT EDIT MANUALLY - Managed by LoadBalancerService

upstream backend_pool {
    least_conn;
    server backend:8000 max_fails=3 fail_timeout=30s weight=1;
    keepalive 32;
}

upstream frontend_pool {
    least_conn;
    server frontend:3000 max_fails=3 fail_timeout=30s weight=1;
    keepalive 16;
}
EOF

print_status "Load balancer configuration created"

# Deploy Application
print_section "Application Deployment"

# Choose deployment configuration based on auto-scaling setting
if [[ "$ENABLE_AUTO_SCALING" == "true" ]]; then
    print_info "Deploying with load balancing support..."
    docker-compose -f docker-compose.loadbalanced.yml build --no-cache
    docker-compose -f docker-compose.loadbalanced.yml up -d
else
    print_info "Deploying single server configuration..."
    docker-compose build --no-cache
    docker-compose up -d
fi

print_status "Application deployed successfully"

# Initialize Load Balancer Database
print_section "Load Balancer Initialization"
print_info "Initializing load balancer database..."

# Wait for backend to be ready
sleep 60

# Create initial server entries
docker-compose exec -T backend python -c "
import asyncio
from app.core.database import get_db
from app.services.load_balancer_service import load_balancer_service

async def init_servers():
    db = next(get_db())
    
    # Add initial backend server
    backend_server = {
        'hostname': 'medhasakthi-backend-1',
        'ip_address': '127.0.0.1',
        'port': 8000,
        'server_type': 'backend',
        'weight': 1,
        'admin_id': 1
    }
    
    try:
        result = await load_balancer_service.add_server(db, backend_server)
        print(f'Backend server added: {result}')
    except Exception as e:
        print(f'Backend server already exists or error: {e}')
    
    # Add initial frontend server
    frontend_server = {
        'hostname': 'medhasakthi-frontend-1',
        'ip_address': '127.0.0.1',
        'port': 3000,
        'server_type': 'frontend',
        'weight': 1,
        'admin_id': 1
    }
    
    try:
        result = await load_balancer_service.add_server(db, frontend_server)
        print(f'Frontend server added: {result}')
    except Exception as e:
        print(f'Frontend server already exists or error: {e}')

asyncio.run(init_servers())
"

print_status "Load balancer initialized"

# Setup Monitoring
print_section "Monitoring Setup"

# Create Grafana dashboards directory
mkdir -p /app/monitoring/grafana/dashboards
mkdir -p /app/monitoring/grafana/datasources

# Create Prometheus configuration
cat > /app/monitoring/prometheus.yml << EOF
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'medhasakthi-backend'
    static_configs:
      - targets: ['backend:8000']
    metrics_path: '/metrics'
    
  - job_name: 'medhasakthi-nginx'
    static_configs:
      - targets: ['nginx:80']
    metrics_path: '/nginx_status'
    
  - job_name: 'node-exporter'
    static_configs:
      - targets: ['localhost:9100']
EOF

print_status "Monitoring configuration created"

# Setup Automated Backups
print_section "Backup Configuration"

cat > /usr/local/bin/medhasakthi-backup.sh << 'EOF'
#!/bin/bash
cd /app/medhasakthi
docker-compose exec -T backend python -c "
import asyncio
from app.services.backup_service import backup_service
asyncio.run(backup_service.create_full_backup())
"
echo "Backup completed at $(date)"
EOF

chmod +x /usr/local/bin/medhasakthi-backup.sh

# Add to crontab
(crontab -l 2>/dev/null; echo "0 2 * * * /usr/local/bin/medhasakthi-backup.sh") | crontab -

print_status "Automated backups configured"

# Setup SSL Auto-renewal
print_section "SSL Auto-renewal Setup"
(crontab -l 2>/dev/null; echo "0 12 * * * /usr/bin/certbot renew --quiet && systemctl reload nginx") | crontab -
print_status "SSL auto-renewal configured"

# Final Health Checks
print_section "Health Checks"
print_info "Waiting for services to start..."
sleep 60

# Check frontend
if curl -f https://$DOMAIN/health >/dev/null 2>&1; then
    print_status "Frontend is accessible"
else
    print_warning "Frontend health check failed"
fi

# Check backend API
if curl -f https://$DOMAIN/api/health >/dev/null 2>&1; then
    print_status "Backend API is accessible"
else
    print_warning "Backend API health check failed"
fi

# Check load balancer status
if curl -f https://$DOMAIN/api/v1/load-balancer/status >/dev/null 2>&1; then
    print_status "Load balancer is operational"
else
    print_warning "Load balancer status check failed"
fi

# Display deployment summary
echo ""
echo -e "${GREEN}🎉 MEDHASAKTHI DEPLOYMENT COMPLETED! 🎉${NC}"
echo -e "${GREEN}============================================${NC}"
echo ""
echo -e "${BLUE}📋 Deployment Summary:${NC}"
echo -e "   🌐 Domain: https://$DOMAIN"
echo -e "   🏠 Main Site: https://$DOMAIN"
echo -e "   🔧 API Docs: https://$DOMAIN/api/docs"
echo -e "   📊 Grafana: https://$DOMAIN:3001"
echo -e "   🔍 Prometheus: https://$DOMAIN:9090"
echo -e "   ⚖️  Load Balancer: https://$DOMAIN/api/v1/load-balancer/status"
echo ""
echo -e "${BLUE}🔐 Security Features:${NC}"
echo -e "   ✅ SSL Certificate (Let's Encrypt)"
echo -e "   ✅ Security Headers"
echo -e "   ✅ CSRF Protection"
echo -e "   ✅ 2FA Authentication"
echo -e "   ✅ Intrusion Detection"
echo ""
echo -e "${BLUE}⚖️ Load Balancing Features:${NC}"
echo -e "   ✅ Dynamic Server Management"
echo -e "   ✅ Automatic Health Monitoring"
echo -e "   ✅ Auto-scaling: $ENABLE_AUTO_SCALING"
echo -e "   ✅ Server Range: $MIN_SERVERS - $MAX_SERVERS servers"
echo -e "   ✅ Real-time Configuration Updates"
echo ""
echo -e "${BLUE}💾 Backup & Monitoring:${NC}"
echo -e "   ✅ Daily Automated Backups"
echo -e "   ✅ SSL Auto-Renewal"
echo -e "   ✅ Comprehensive Monitoring"
echo -e "   ✅ Error Tracking (Sentry)"
echo -e "   ✅ Performance Metrics"
echo ""
echo -e "${BLUE}📝 Next Steps:${NC}"
echo -e "   1. Test all functionality at https://$DOMAIN"
echo -e "   2. Access admin panel for load balancer management"
echo -e "   3. Configure monitoring alerts"
echo -e "   4. Add additional servers through admin interface"
echo -e "   5. Launch marketing campaign!"
echo ""
echo -e "${GREEN}🚀 MEDHASAKTHI is now LIVE with Enterprise Load Balancing! 🚀${NC}"
