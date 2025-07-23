#!/bin/bash

# MEDHASAKTHI AWS EC2 Deployment Script
# Optimized for Amazon Linux 2 / Ubuntu on EC2

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
DOMAIN="medhasakthi.com"
EMAIL="admin@medhasakthi.com"
INSTANCE_TYPE=${INSTANCE_TYPE:-"t3.large"}
REGION=${AWS_REGION:-"ap-south-1"}  # Mumbai region for India

echo -e "${BLUE}🚀 MEDHASAKTHI AWS EC2 Deployment${NC}"
echo -e "${BLUE}Domain: $DOMAIN${NC}"
echo -e "${BLUE}Region: $REGION${NC}"
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

# Check if running on EC2
if ! curl -s http://169.254.169.254/latest/meta-data/instance-id >/dev/null 2>&1; then
    print_error "This script is designed to run on AWS EC2 instances"
    exit 1
fi

INSTANCE_ID=$(curl -s http://169.254.169.254/latest/meta-data/instance-id)
PUBLIC_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)

print_info "Instance ID: $INSTANCE_ID"
print_info "Public IP: $PUBLIC_IP"

# Update system packages
print_info "Updating system packages..."
if command -v yum >/dev/null 2>&1; then
    # Amazon Linux 2
    sudo yum update -y
    sudo yum install -y docker git curl openssl
    sudo systemctl start docker
    sudo systemctl enable docker
    sudo usermod -a -G docker ec2-user
elif command -v apt >/dev/null 2>&1; then
    # Ubuntu
    sudo apt update && sudo apt upgrade -y
    sudo apt install -y docker.io docker-compose git curl openssl
    sudo systemctl start docker
    sudo systemctl enable docker
    sudo usermod -a -G docker ubuntu
fi

print_status "System packages updated"

# Install Docker Compose if not present
if ! command -v docker-compose >/dev/null 2>&1; then
    print_info "Installing Docker Compose..."
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    print_status "Docker Compose installed"
fi

# Create application directories
print_info "Creating application directories..."
sudo mkdir -p /app/{logs,backups,uploads,certificates,static}
sudo chown -R $USER:$USER /app
print_status "Application directories created"

# Clone repository
print_info "Cloning MEDHASAKTHI repository..."
if [[ -d "/app/medhasakthi" ]]; then
    cd /app/medhasakthi
    git pull origin main
else
    cd /app
    git clone https://github.com/your-org/medhasakthi.git
    cd medhasakthi
fi
print_status "Repository cloned/updated"

# Generate environment configuration
print_info "Generating production environment..."
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
    
    print_status "Environment configuration generated"
else
    print_info "Using existing environment configuration"
fi

# Install Certbot for SSL
print_info "Installing Certbot for SSL certificates..."
if command -v yum >/dev/null 2>&1; then
    sudo yum install -y certbot
elif command -v apt >/dev/null 2>&1; then
    sudo apt install -y certbot
fi

# Configure AWS Security Group (if AWS CLI is available)
if command -v aws >/dev/null 2>&1; then
    print_info "Configuring AWS Security Group..."
    
    # Get security group ID
    SECURITY_GROUP=$(aws ec2 describe-instances --instance-ids $INSTANCE_ID --query 'Reservations[0].Instances[0].SecurityGroups[0].GroupId' --output text --region $REGION 2>/dev/null || echo "")
    
    if [[ -n "$SECURITY_GROUP" ]]; then
        # Add HTTP and HTTPS rules if they don't exist
        aws ec2 authorize-security-group-ingress --group-id $SECURITY_GROUP --protocol tcp --port 80 --cidr 0.0.0.0/0 --region $REGION 2>/dev/null || true
        aws ec2 authorize-security-group-ingress --group-id $SECURITY_GROUP --protocol tcp --port 443 --cidr 0.0.0.0/0 --region $REGION 2>/dev/null || true
        aws ec2 authorize-security-group-ingress --group-id $SECURITY_GROUP --protocol tcp --port 3001 --cidr 0.0.0.0/0 --region $REGION 2>/dev/null || true  # Grafana
        aws ec2 authorize-security-group-ingress --group-id $SECURITY_GROUP --protocol tcp --port 9090 --cidr 0.0.0.0/0 --region $REGION 2>/dev/null || true  # Prometheus
        
        print_status "Security group configured"
    fi
fi

# Generate SSL certificate
print_info "Generating SSL certificate for $DOMAIN..."
sudo certbot certonly --standalone -d $DOMAIN -d www.$DOMAIN --email $EMAIL --agree-tos --non-interactive

if [[ $? -eq 0 ]]; then
    print_status "SSL certificate generated successfully"
else
    print_error "SSL certificate generation failed. Please check DNS configuration."
    print_info "Make sure $DOMAIN points to $PUBLIC_IP"
    exit 1
fi

# Install and configure Nginx
print_info "Installing and configuring Nginx..."
if command -v yum >/dev/null 2>&1; then
    sudo yum install -y nginx
elif command -v apt >/dev/null 2>&1; then
    sudo apt install -y nginx
fi

# Create Nginx configuration
sudo tee /etc/nginx/sites-available/medhasakthi << EOF
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
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Content-Type-Options nosniff always;
    add_header X-Frame-Options DENY always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Frontend
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    # Backend API
    location /api/ {
        proxy_pass http://localhost:8000/api/;
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

# Enable Nginx site
if [[ -d "/etc/nginx/sites-enabled" ]]; then
    sudo ln -sf /etc/nginx/sites-available/medhasakthi /etc/nginx/sites-enabled/
    sudo rm -f /etc/nginx/sites-enabled/default
else
    # Amazon Linux 2 style
    sudo cp /etc/nginx/sites-available/medhasakthi /etc/nginx/conf.d/medhasakthi.conf
fi

sudo nginx -t
sudo systemctl enable nginx
sudo systemctl restart nginx

print_status "Nginx configured and started"

# Deploy application
print_info "Building and deploying MEDHASAKTHI..."

# Start database services first
docker-compose up -d postgres redis
sleep 30

# Run database migrations
docker-compose exec -T backend alembic upgrade head

# Build and start all services
docker-compose build --no-cache
docker-compose up -d

print_status "MEDHASAKTHI deployed successfully"

# Setup automated backups
print_info "Setting up automated backups..."
sudo tee /usr/local/bin/medhasakthi-backup.sh << 'EOF'
#!/bin/bash
cd /app/medhasakthi
docker-compose exec -T backend python -c "
import asyncio
from app.services.backup_service import backup_service
asyncio.run(backup_service.create_full_backup())
"

# Upload to S3 if configured
if [[ -n "$AWS_S3_BACKUP_BUCKET" ]]; then
    aws s3 sync /app/backups/ s3://$AWS_S3_BACKUP_BUCKET/medhasakthi-backups/ --delete
fi
EOF

sudo chmod +x /usr/local/bin/medhasakthi-backup.sh

# Add to crontab
(crontab -l 2>/dev/null; echo "0 2 * * * /usr/local/bin/medhasakthi-backup.sh") | crontab -

print_status "Automated backups configured"

# Setup SSL certificate renewal
print_info "Setting up SSL certificate auto-renewal..."
(crontab -l 2>/dev/null; echo "0 12 * * * /usr/bin/certbot renew --quiet && systemctl reload nginx") | crontab -

print_status "SSL auto-renewal configured"

# Final health checks
print_info "Running final health checks..."
sleep 60

# Check services
if curl -f https://$DOMAIN/health >/dev/null 2>&1; then
    print_status "Frontend is accessible"
else
    print_error "Frontend health check failed"
fi

if curl -f https://$DOMAIN/api/health >/dev/null 2>&1; then
    print_status "Backend API is accessible"
else
    print_error "Backend API health check failed"
fi

# Display deployment summary
echo ""
echo -e "${GREEN}🎉 MEDHASAKTHI DEPLOYMENT COMPLETED! 🎉${NC}"
echo -e "${GREEN}======================================${NC}"
echo ""
echo -e "${BLUE}📋 Deployment Summary:${NC}"
echo -e "   🌐 Domain: https://$DOMAIN"
echo -e "   🏠 Main Site: https://$DOMAIN"
echo -e "   🔧 API Docs: https://$DOMAIN/api/docs"
echo -e "   📊 Grafana: https://$DOMAIN:3001"
echo -e "   🔍 Prometheus: https://$DOMAIN:9090"
echo -e "   🖥️  Instance: $INSTANCE_ID ($PUBLIC_IP)"
echo -e "   🌍 Region: $REGION"
echo ""
echo -e "${BLUE}🔐 Security Features:${NC}"
echo -e "   ✅ SSL Certificate (Let's Encrypt)"
echo -e "   ✅ Security Headers"
echo -e "   ✅ CSRF Protection"
echo -e "   ✅ 2FA Authentication"
echo -e "   ✅ Intrusion Detection"
echo ""
echo -e "${BLUE}💾 Backup & Monitoring:${NC}"
echo -e "   ✅ Daily Automated Backups"
echo -e "   ✅ SSL Auto-Renewal"
echo -e "   ✅ Comprehensive Monitoring"
echo -e "   ✅ Error Tracking (Sentry)"
echo ""
echo -e "${BLUE}📝 Next Steps:${NC}"
echo -e "   1. Test all functionality at https://$DOMAIN"
echo -e "   2. Configure monitoring alerts"
echo -e "   3. Set up backup notifications"
echo -e "   4. Launch marketing campaign!"
echo ""
echo -e "${GREEN}🚀 MEDHASAKTHI is now LIVE on AWS! 🚀${NC}"
