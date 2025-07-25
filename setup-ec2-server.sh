#!/bin/bash

# MEDHASAKTHI EC2 Server Setup Script
# This script automates the initial setup of an EC2 instance for MEDHASAKTHI deployment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
DOMAIN="${DOMAIN:-medhasakthi.com}"
EMAIL="${EMAIL:-admin@medhasakthi.com}"
GITHUB_REPO="${GITHUB_REPO:-https://github.com/Medhasakthi/MEDHASAKTHI.git}"

echo -e "${BLUE}🚀 MEDHASAKTHI EC2 Server Setup${NC}"
echo -e "${BLUE}Domain: $DOMAIN${NC}"
echo -e "${BLUE}Email: $EMAIL${NC}"
echo -e "${BLUE}Repository: $GITHUB_REPO${NC}"
echo -e "${BLUE}================================${NC}"

print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   print_error "This script should not be run as root. Please run as a regular user with sudo privileges."
   exit 1
fi

# Check if running on EC2 (optional)
if curl -s --max-time 5 http://169.254.169.254/latest/meta-data/instance-id >/dev/null 2>&1; then
    INSTANCE_ID=$(curl -s http://169.254.169.254/latest/meta-data/instance-id)
    PUBLIC_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)
    print_info "Detected EC2 instance: $INSTANCE_ID"
    print_info "Public IP: $PUBLIC_IP"
else
    print_warning "Not running on EC2 or metadata service unavailable"
    PUBLIC_IP=$(curl -s ifconfig.me || echo "unknown")
    print_info "Public IP: $PUBLIC_IP"
fi

# Update system packages
print_info "Updating system packages..."
sudo apt update && sudo apt upgrade -y
print_status "System packages updated"

# Install essential packages
print_info "Installing essential packages..."
sudo apt install -y \
    curl \
    wget \
    git \
    unzip \
    software-properties-common \
    apt-transport-https \
    ca-certificates \
    gnupg \
    lsb-release \
    openssl \
    nginx \
    certbot \
    python3-certbot-nginx \
    htop \
    tree \
    jq

print_status "Essential packages installed"

# Install Docker
print_info "Installing Docker..."
if ! command -v docker >/dev/null 2>&1; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    rm get-docker.sh
    print_status "Docker installed"
else
    print_info "Docker already installed"
fi

# Install Docker Compose
print_info "Installing Docker Compose..."
if ! command -v docker-compose >/dev/null 2>&1; then
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    print_status "Docker Compose installed"
else
    print_info "Docker Compose already installed"
fi

# Install AWS CLI (optional but recommended)
print_info "Installing AWS CLI..."
if ! command -v aws >/dev/null 2>&1; then
    curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
    unzip awscliv2.zip
    sudo ./aws/install
    rm -rf aws awscliv2.zip
    print_status "AWS CLI installed"
else
    print_info "AWS CLI already installed"
fi

# Create application directories
print_info "Creating application directories..."
sudo mkdir -p /opt/medhasakthi
sudo chown $USER:$USER /opt/medhasakthi

cd /opt/medhasakthi
mkdir -p {logs,backups,uploads,certificates,static}
mkdir -p database/{backups,init}
mkdir -p nginx/{ssl,logs}
mkdir -p monitoring/{grafana,prometheus}
mkdir -p logging

print_status "Application directories created"

# Clone repository
print_info "Cloning MEDHASAKTHI repository..."
if [[ -d ".git" ]]; then
    git pull origin main
    print_info "Repository updated"
else
    git clone $GITHUB_REPO .
    print_status "Repository cloned"
fi

# Generate environment configuration
print_info "Generating production environment..."
if [[ ! -f ".env" ]]; then
    if [[ -f "backend/.env.example" ]]; then
        cp backend/.env.example .env
    else
        print_warning ".env.example not found, creating basic .env file"
        cat > .env << EOF
# Database Configuration
DATABASE_URL=postgresql://medhasakthi_user:\${DB_PASSWORD}@postgres:5432/medhasakthi_prod
DB_PASSWORD=change_me_in_production

# Redis Configuration
REDIS_URL=redis://redis:6379
REDIS_PASSWORD=change_me_in_production

# Security
SECRET_KEY=change_me_in_production
JWT_SECRET=change_me_in_production
CSRF_SECRET=change_me_in_production

# Email Configuration
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USERNAME=your_email@gmail.com
EMAIL_PASSWORD=your_app_password

# Domain
DOMAIN=$DOMAIN
EMAIL=$EMAIL

# Environment
ENVIRONMENT=production
LOG_LEVEL=INFO
EOF
    fi
    
    # Generate secure secrets
    SECRET_KEY=$(openssl rand -hex 32)
    JWT_SECRET=$(openssl rand -hex 32)
    CSRF_SECRET=$(openssl rand -hex 32)
    DB_PASSWORD=$(openssl rand -hex 16)
    REDIS_PASSWORD=$(openssl rand -hex 16)
    GRAFANA_PASSWORD=$(openssl rand -hex 12)
    
    # Update environment file
    sed -i "s/change_me_in_production/$SECRET_KEY/g" .env
    sed -i "s/your-jwt-secret-here/$JWT_SECRET/g" .env
    sed -i "s/your-csrf-secret-key-here/$CSRF_SECRET/g" .env
    sed -i "s/secure_password_change_me/$DB_PASSWORD/g" .env
    sed -i "s/redis_password_change_me/$REDIS_PASSWORD/g" .env
    sed -i "s/development/production/g" .env
    sed -i "s/your-domain.com/$DOMAIN/g" .env
    
    # Add Grafana password if not present
    if ! grep -q "GRAFANA_PASSWORD" .env; then
        echo "GRAFANA_PASSWORD=$GRAFANA_PASSWORD" >> .env
    fi
    
    print_status "Environment configuration generated"
    print_warning "Please review and update .env file with your specific configuration"
else
    print_info "Using existing environment configuration"
fi

# Create deployment script
print_info "Creating deployment script..."
cat > deploy.sh << 'EOF'
#!/bin/bash
set -e

echo "🚀 Starting MEDHASAKTHI deployment..."

# Navigate to application directory
cd /opt/medhasakthi

# Pull latest changes
git pull origin main

# Stop services gracefully
docker-compose -f docker-compose.production.yml down --remove-orphans

# Pull latest images
docker-compose -f docker-compose.production.yml pull

# Build updated images
docker-compose -f docker-compose.production.yml build --no-cache

# Start services
docker-compose -f docker-compose.production.yml up -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 60

# Run database migrations
docker-compose -f docker-compose.production.yml exec -T backend alembic upgrade head

# Clean up old images
docker system prune -f

# Health check
echo "🔍 Running health checks..."
sleep 30

if curl -f https://$DOMAIN/health >/dev/null 2>&1; then
    echo "✅ Frontend health check passed"
else
    echo "❌ Frontend health check failed"
    exit 1
fi

if curl -f https://$DOMAIN/api/health >/dev/null 2>&1; then
    echo "✅ Backend health check passed"
else
    echo "❌ Backend health check failed"
    exit 1
fi

echo "🎉 Deployment completed successfully!"
EOF

chmod +x deploy.sh
print_status "Deployment script created"

# Create health check script
print_info "Creating health check script..."
cat > health-check.sh << 'EOF'
#!/bin/bash

echo "🔍 MEDHASAKTHI Health Check"
echo "=========================="

# Check Docker services
echo "📦 Docker Services:"
docker-compose -f docker-compose.production.yml ps

# Check disk space
echo -e "\n💾 Disk Usage:"
df -h /

# Check memory usage
echo -e "\n🧠 Memory Usage:"
free -h

# Check SSL certificate
echo -e "\n🔒 SSL Certificate:"
if [[ -f "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" ]]; then
    echo | openssl s_client -servername $DOMAIN -connect $DOMAIN:443 2>/dev/null | openssl x509 -noout -dates
else
    echo "SSL certificate not found"
fi

# Check application endpoints
echo -e "\n🌐 Application Health:"
curl -s https://$DOMAIN/health && echo " ✅ Frontend OK" || echo " ❌ Frontend Failed"
curl -s https://$DOMAIN/api/health && echo " ✅ Backend OK" || echo " ❌ Backend Failed"

# Check database connection
echo -e "\n🗄️ Database Connection:"
docker-compose -f docker-compose.production.yml exec -T postgres pg_isready -U medhasakthi_user -d medhasakthi_prod && echo " ✅ Database OK" || echo " ❌ Database Failed"

# Check Redis connection
echo -e "\n📦 Redis Connection:"
docker-compose -f docker-compose.production.yml exec -T redis redis-cli ping && echo " ✅ Redis OK" || echo " ❌ Redis Failed"

echo -e "\n🎉 Health check completed!"
EOF

chmod +x health-check.sh
print_status "Health check script created"

# Setup backup script
print_info "Setting up backup script..."
sudo tee /usr/local/bin/medhasakthi-backup.sh << 'EOF'
#!/bin/bash
set -e

BACKUP_DIR="/opt/medhasakthi/backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="medhasakthi_backup_${DATE}.sql"

echo "🗄️ Starting database backup..."

# Create backup directory if it doesn't exist
mkdir -p $BACKUP_DIR

# Create database backup
cd /opt/medhasakthi
docker-compose -f docker-compose.production.yml exec -T postgres pg_dump -U medhasakthi_user medhasakthi_prod > $BACKUP_DIR/$BACKUP_FILE

# Compress backup
gzip $BACKUP_DIR/$BACKUP_FILE

# Upload to S3 (if configured)
if [[ -n "$AWS_S3_BACKUP_BUCKET" ]] && command -v aws >/dev/null 2>&1; then
    aws s3 cp $BACKUP_DIR/${BACKUP_FILE}.gz s3://$AWS_S3_BACKUP_BUCKET/database/
fi

# Keep only last 7 days of backups locally
find $BACKUP_DIR -name "medhasakthi_backup_*.sql.gz" -mtime +7 -delete

echo "✅ Backup completed: ${BACKUP_FILE}.gz"
EOF

sudo chmod +x /usr/local/bin/medhasakthi-backup.sh
print_status "Backup script created"

# Display completion message
echo ""
echo -e "${GREEN}🎉 EC2 SERVER SETUP COMPLETED! 🎉${NC}"
echo -e "${GREEN}================================${NC}"
echo ""
echo -e "${BLUE}📋 Setup Summary:${NC}"
echo -e "   📁 Application Directory: /opt/medhasakthi"
echo -e "   🌐 Domain: $DOMAIN"
echo -e "   📧 Email: $EMAIL"
echo -e "   🖥️  Public IP: $PUBLIC_IP"
echo ""
echo -e "${BLUE}📝 Next Steps:${NC}"
echo -e "   1. Configure DNS: Point $DOMAIN to $PUBLIC_IP"
echo -e "   2. Update .env file with your specific configuration"
echo -e "   3. Generate SSL certificate: sudo certbot --nginx -d $DOMAIN"
echo -e "   4. Configure GitHub Actions secrets"
echo -e "   5. Push to main branch to trigger deployment"
echo ""
echo -e "${BLUE}🔧 Available Scripts:${NC}"
echo -e "   • ./deploy.sh - Deploy application"
echo -e "   • ./health-check.sh - Check system health"
echo -e "   • /usr/local/bin/medhasakthi-backup.sh - Backup database"
echo ""
echo -e "${YELLOW}⚠️  Important:${NC}"
echo -e "   • Review and update the .env file before deployment"
echo -e "   • Configure your domain DNS settings"
echo -e "   • Set up GitHub Actions secrets for automated deployment"
echo -e "   • Log out and log back in for Docker group changes to take effect"
echo ""
echo -e "${GREEN}🚀 Your server is ready for MEDHASAKTHI deployment! 🚀${NC}"
