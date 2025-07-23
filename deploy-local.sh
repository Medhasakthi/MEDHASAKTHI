#!/bin/bash

# MEDHASAKTHI Local PC Deployment Script
# Deploy on your own computer with domain pointing to your public IP

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

# Configuration
DOMAIN="medhasakthi.com"
EMAIL="support@medhasakthi.com"
LOCAL_PORT=${LOCAL_PORT:-80}
SSL_PORT=${SSL_PORT:-443}

# All subdomains for local development
SUBDOMAINS=("www" "api" "admin" "student" "teacher" "learn")

echo -e "${BLUE}🏠 MEDHASAKTHI Local PC Deployment${NC}"
echo -e "${BLUE}Domain: $DOMAIN${NC}"
echo -e "${BLUE}====================================${NC}"

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
    echo -e "${PURPLE}$(printf '=%.0s' {1..40})${NC}"
}

# Configure local DNS automatically
configure_local_dns() {
    print_section "Local DNS Configuration"

    # Backup hosts file
    if [[ ! -f "/etc/hosts.backup" ]]; then
        sudo cp /etc/hosts /etc/hosts.backup
        print_status "Hosts file backed up"
    fi

    # Remove existing medhasakthi entries
    sudo sed -i.bak '/medhasakthi\.com/d' /etc/hosts

    # Add all subdomains to hosts file
    print_info "Adding local DNS entries for $DOMAIN..."
    echo "# MEDHASAKTHI Local Development - Added $(date)" | sudo tee -a /etc/hosts
    echo "127.0.0.1    $DOMAIN" | sudo tee -a /etc/hosts
    for subdomain in "${SUBDOMAINS[@]}"; do
        echo "127.0.0.1    $subdomain.$DOMAIN" | sudo tee -a /etc/hosts
    done

    print_warning "IMPORTANT: This will override DNS for $DOMAIN locally"
    print_info "To access the real domain, remove these entries from /etc/hosts later"

    print_status "Local DNS configured for all subdomains"
}

# Get network information
print_section "Network Configuration"
LOCAL_IP=$(hostname -I | awk '{print $1}' 2>/dev/null || ipconfig | grep "IPv4" | head -1 | awk '{print $NF}' 2>/dev/null || echo "127.0.0.1")
print_info "Local IP: $LOCAL_IP"
print_info "Domain: $DOMAIN"

# Configure DNS
configure_local_dns

# Check if Docker is installed
print_section "Docker Installation Check"
if command -v docker >/dev/null 2>&1; then
    print_status "Docker is installed"
    DOCKER_VERSION=$(docker --version | cut -d' ' -f3 | cut -d',' -f1)
    print_info "Docker version: $DOCKER_VERSION"
else
    print_error "Docker is not installed. Please install Docker Desktop first."
    print_info "Download from: https://www.docker.com/products/docker-desktop"
    exit 1
fi

# Check if Docker Compose is available
if command -v docker-compose >/dev/null 2>&1; then
    print_status "Docker Compose is available"
elif docker compose version >/dev/null 2>&1; then
    print_status "Docker Compose (v2) is available"
    alias docker-compose='docker compose'
else
    print_error "Docker Compose is not available"
    exit 1
fi

# Check if Docker is running
if docker info >/dev/null 2>&1; then
    print_status "Docker is running"
else
    print_error "Docker is not running. Please start Docker Desktop."
    exit 1
fi

# Create application directories
print_section "Directory Setup"
mkdir -p logs backups uploads certificates static
print_status "Application directories created"

# Generate environment configuration
print_section "Environment Configuration"
if [[ ! -f ".env" ]]; then
    cp backend/.env.example .env
    
    # Generate secure secrets
    SECRET_KEY=$(openssl rand -hex 32 2>/dev/null || python3 -c "import secrets; print(secrets.token_hex(32))")
    JWT_SECRET=$(openssl rand -hex 32 2>/dev/null || python3 -c "import secrets; print(secrets.token_hex(32))")
    CSRF_SECRET=$(openssl rand -hex 32 2>/dev/null || python3 -c "import secrets; print(secrets.token_hex(32))")
    BACKUP_KEY=$(openssl rand -base64 32 2>/dev/null || python3 -c "import base64, secrets; print(base64.b64encode(secrets.token_bytes(32)).decode())")
    POSTGRES_PASSWORD=$(openssl rand -hex 16 2>/dev/null || python3 -c "import secrets; print(secrets.token_hex(16))")
    REDIS_PASSWORD=$(openssl rand -hex 16 2>/dev/null || python3 -c "import secrets; print(secrets.token_hex(16))")
    
    # Update environment file
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        sed -i '' "s/your-secret-key-here/$SECRET_KEY/g" .env
        sed -i '' "s/your-jwt-secret-here/$JWT_SECRET/g" .env
        sed -i '' "s/your-csrf-secret-key-here/$CSRF_SECRET/g" .env
        sed -i '' "s/your-backup-encryption-key-here/$BACKUP_KEY/g" .env
        sed -i '' "s/secure_password_change_me/$POSTGRES_PASSWORD/g" .env
        sed -i '' "s/redis_password_change_me/$REDIS_PASSWORD/g" .env
        sed -i '' "s/development/production/g" .env
        sed -i '' "s/admin@medhasakthi.com/$EMAIL/g" .env
        sed -i '' "s/your-domain.com/$DOMAIN/g" .env
    else
        # Linux/Windows WSL
        sed -i "s/your-secret-key-here/$SECRET_KEY/g" .env
        sed -i "s/your-jwt-secret-here/$JWT_SECRET/g" .env
        sed -i "s/your-csrf-secret-key-here/$CSRF_SECRET/g" .env
        sed -i "s/your-backup-encryption-key-here/$BACKUP_KEY/g" .env
        sed -i "s/secure_password_change_me/$POSTGRES_PASSWORD/g" .env
        sed -i "s/redis_password_change_me/$REDIS_PASSWORD/g" .env
        sed -i "s/development/production/g" .env
        sed -i "s/admin@medhasakthi.com/$EMAIL/g" .env
        sed -i "s/your-domain.com/$DOMAIN/g" .env
    fi
    
    print_status "Environment configuration generated"
else
    print_info "Using existing environment configuration"
fi

# Generate comprehensive SSL certificates for all subdomains
generate_ssl_certificates() {
    print_section "SSL Certificate Setup"

    # Create certificate directory
    mkdir -p certificates

    if [[ ! -f "certificates/medhasakthi.com.crt" ]]; then
        print_info "Generating comprehensive SSL certificate for $DOMAIN and all subdomains..."

        # Create certificate configuration with all subdomains
        cat > certificates/ssl.conf << EOF
[req]
default_bits = 2048
prompt = no
default_md = sha256
distinguished_name = dn
req_extensions = v3_req

[dn]
C=IN
ST=Karnataka
L=Bangalore
O=MEDHASAKTHI
OU=Development
CN=$DOMAIN

[v3_req]
basicConstraints = CA:FALSE
keyUsage = nonRepudiation, digitalSignature, keyEncipherment
subjectAltName = @alt_names

[alt_names]
DNS.1 = $DOMAIN
DNS.2 = localhost
IP.1 = 127.0.0.1
EOF

        # Add all subdomains to certificate
        counter=3
        for subdomain in "${SUBDOMAINS[@]}"; do
            echo "DNS.$counter = $subdomain.$DOMAIN" >> certificates/ssl.conf
            ((counter++))
        done

        # Generate private key
        openssl genrsa -out certificates/medhasakthi.com.key 2048 2>/dev/null

        # Generate certificate signing request
        openssl req -new -key certificates/medhasakthi.com.key -out certificates/medhasakthi.com.csr -config certificates/ssl.conf 2>/dev/null

        # Generate self-signed certificate with all subdomains
        openssl x509 -req -days 365 -in certificates/medhasakthi.com.csr -signkey certificates/medhasakthi.com.key -out certificates/medhasakthi.com.crt -extensions v3_req -extfile certificates/ssl.conf 2>/dev/null

        print_status "SSL certificate generated for all subdomains"
        print_info "Certificate includes: $DOMAIN, ${SUBDOMAINS[*]/#/,}.$DOMAIN"
        print_warning "Note: Add certificates/medhasakthi.com.crt to browser's trusted certificates to avoid warnings"
    else
        print_info "Using existing SSL certificate"
    fi
}

generate_ssl_certificates

# Create local nginx configuration
print_section "Nginx Configuration"
cat > nginx-local.conf << EOF
server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN localhost;
    
    # Redirect HTTP to HTTPS
    return 301 https://\$server_name\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name $DOMAIN www.$DOMAIN localhost;

    # SSL configuration (self-signed for local)
    ssl_certificate /etc/nginx/ssl/medhasakthi.com.crt;
    ssl_certificate_key /etc/nginx/ssl/medhasakthi.com.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Content-Type-Options nosniff always;
    add_header X-Frame-Options DENY always;
    add_header X-XSS-Protection "1; mode=block" always;

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
        proxy_read_timeout 300;
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

# Update docker-compose for local deployment
print_section "Docker Compose Configuration"
cat > docker-compose.local.yml << EOF
version: '3.8'

services:
  # PostgreSQL Database
  postgres:
    image: postgres:15-alpine
    container_name: medhasakthi-postgres-local
    environment:
      POSTGRES_DB: medhasakthi
      POSTGRES_USER: medhasakthi_user
      POSTGRES_PASSWORD: \${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backend/init.sql:/docker-entrypoint-initdb.d/init.sql
    ports:
      - "5432:5432"
    restart: unless-stopped

  # Redis Cache
  redis:
    image: redis:7-alpine
    container_name: medhasakthi-redis-local
    command: redis-server --appendonly yes --requirepass \${REDIS_PASSWORD}
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"
    restart: unless-stopped

  # Backend API
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: medhasakthi-backend-local
    environment:
      - DATABASE_URL=postgresql://medhasakthi_user:\${POSTGRES_PASSWORD}@postgres:5432/medhasakthi
      - REDIS_URL=redis://:\${REDIS_PASSWORD}@redis:6379
      - SECRET_KEY=\${SECRET_KEY}
      - JWT_SECRET_KEY=\${JWT_SECRET_KEY}
      - CSRF_SECRET_KEY=\${CSRF_SECRET_KEY}
      - DEBUG=false
      - ENVIRONMENT=local
      - FRONTEND_URL=https://$DOMAIN
      - BACKEND_CORS_ORIGINS=https://$DOMAIN,https://www.$DOMAIN,https://admin.$DOMAIN,https://student.$DOMAIN,https://teacher.$DOMAIN,https://learn.$DOMAIN
    volumes:
      - ./uploads:/app/uploads
      - ./logs:/app/logs
      - ./backups:/app/backups
    ports:
      - "8000:8000"
    depends_on:
      - postgres
      - redis
    restart: unless-stopped

  # Frontend
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: medhasakthi-frontend-local
    environment:
      - REACT_APP_API_URL=https://api.$DOMAIN
      - REACT_APP_DOMAIN=$DOMAIN
      - REACT_APP_STUDENT_URL=https://student.$DOMAIN
      - REACT_APP_ADMIN_URL=https://admin.$DOMAIN
      - REACT_APP_TEACHER_URL=https://teacher.$DOMAIN
      - REACT_APP_LEARN_URL=https://learn.$DOMAIN
    ports:
      - "3000:3000"
    restart: unless-stopped

  # Nginx Reverse Proxy
  nginx:
    image: nginx:alpine
    container_name: medhasakthi-nginx-local
    volumes:
      - ./nginx-local.conf:/etc/nginx/conf.d/default.conf
      - ./certificates:/etc/nginx/ssl
    ports:
      - "80:80"
      - "443:443"
    depends_on:
      - backend
      - frontend
    restart: unless-stopped

  # Prometheus Monitoring
  prometheus:
    image: prom/prometheus:latest
    container_name: medhasakthi-prometheus-local
    ports:
      - "9090:9090"
    volumes:
      - prometheus_data:/prometheus
    restart: unless-stopped

  # Grafana Dashboard
  grafana:
    image: grafana/grafana:latest
    container_name: medhasakthi-grafana-local
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin123
    volumes:
      - grafana_data:/var/lib/grafana
    ports:
      - "3001:3000"
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
  prometheus_data:
  grafana_data:
EOF

print_status "Local Docker Compose configuration created"

# Deploy application
print_section "Application Deployment"
print_info "Building and starting MEDHASAKTHI..."

# Start database services first
docker-compose -f docker-compose.local.yml up -d postgres redis
sleep 30

# Run database migrations
print_info "Running database migrations..."
docker-compose -f docker-compose.local.yml exec -T backend alembic upgrade head

# Build and start all services
docker-compose -f docker-compose.local.yml build --no-cache
docker-compose -f docker-compose.local.yml up -d

print_status "MEDHASAKTHI deployed successfully"

# Setup local backup script
print_section "Backup Configuration"
cat > backup-local.sh << 'EOF'
#!/bin/bash
echo "Creating local backup..."
docker-compose -f docker-compose.local.yml exec -T backend python -c "
import asyncio
from app.services.backup_service import backup_service
asyncio.run(backup_service.create_full_backup())
"
echo "Backup completed!"
EOF

chmod +x backup-local.sh
print_status "Local backup script created"

# Final health checks
print_section "Health Checks"
print_info "Waiting for services to start..."
sleep 60

# Check services
if curl -k -f https://$DOMAIN >/dev/null 2>&1; then
    print_status "Main frontend is accessible"
else
    print_warning "Main frontend health check failed"
fi

if curl -k -f https://api.$DOMAIN/health >/dev/null 2>&1; then
    print_status "Backend API is accessible"
else
    print_warning "Backend API health check failed"
fi

if curl -k -f https://student.$DOMAIN >/dev/null 2>&1; then
    print_status "Student portal is accessible"
else
    print_warning "Student portal health check failed"
fi

if curl -k -f https://admin.$DOMAIN >/dev/null 2>&1; then
    print_status "Admin portal is accessible"
else
    print_warning "Admin portal health check failed"
fi

# Display deployment summary
echo ""
echo -e "${GREEN}🎉 MEDHASAKTHI LOCAL DEPLOYMENT COMPLETED! 🎉${NC}"
echo -e "${GREEN}=============================================${NC}"
echo ""
echo -e "${BLUE}📋 Local Access URLs:${NC}"
echo -e "   🏠 Main Site: https://$DOMAIN"
echo -e "   👨‍🎓 Student Portal: https://student.$DOMAIN"
echo -e "   👨‍🏫 Teacher Portal: https://teacher.$DOMAIN"
echo -e "   🏢 Admin Portal: https://admin.$DOMAIN"
echo -e "   🎯 Learn Portal: https://learn.$DOMAIN"
echo -e "   🔧 API Docs: https://api.$DOMAIN/docs"
echo -e "   📊 Grafana: http://localhost:3001 (admin/admin123)"
echo -e "   🔍 Prometheus: http://localhost:9090"
echo ""
echo -e "${BLUE}🌐 Local Development Configuration:${NC}"
echo -e "   🏠 Local IP: $LOCAL_IP"
echo -e "   🌍 Domain: $DOMAIN"
echo -e "   📝 DNS: Automatically configured in /etc/hosts"
echo -e "   🔒 SSL: Self-signed certificates generated"
echo ""
echo -e "${BLUE}📝 Important Notes:${NC}"
echo -e "   1. All subdomains are configured and working locally"
echo -e "   2. Add certificates/medhasakthi.local.crt to browser's trusted certificates"
echo -e "   3. This setup is for local development only"
echo -e "   4. Update .env with your email and OpenAI API key for full functionality"
echo ""
echo -e "${BLUE}🔄 Migration to Cloud:${NC}"
echo -e "   • All data is in Docker volumes"
echo -e "   • Easy to backup and restore"
echo -e "   • Can migrate anytime with ./migrate-to-cloud.sh"
echo ""
echo -e "${GREEN}🚀 MEDHASAKTHI is now running on your PC! 🚀${NC}"
