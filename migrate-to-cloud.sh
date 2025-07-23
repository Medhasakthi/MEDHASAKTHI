#!/bin/bash

# MEDHASAKTHI Cloud Migration Script
# Migrate from local PC to cloud server (AWS/DigitalOcean/etc.)

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
CLOUD_SERVER_IP=""
CLOUD_USER="ubuntu"  # or ec2-user for Amazon Linux
SSH_KEY=""

echo -e "${BLUE}🚀 MEDHASAKTHI Cloud Migration Tool${NC}"
echo -e "${BLUE}===================================${NC}"

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

# Get migration parameters
if [[ -z "$CLOUD_SERVER_IP" ]]; then
    echo -e "${YELLOW}Please provide cloud server details:${NC}"
    read -p "Cloud Server IP: " CLOUD_SERVER_IP
    read -p "SSH User (ubuntu/ec2-user): " CLOUD_USER
    read -p "SSH Key Path (optional): " SSH_KEY
fi

if [[ -z "$CLOUD_SERVER_IP" ]]; then
    print_error "Cloud server IP is required"
    exit 1
fi

# SSH command setup
if [[ -n "$SSH_KEY" ]]; then
    SSH_CMD="ssh -i $SSH_KEY $CLOUD_USER@$CLOUD_SERVER_IP"
    SCP_CMD="scp -i $SSH_KEY"
else
    SSH_CMD="ssh $CLOUD_USER@$CLOUD_SERVER_IP"
    SCP_CMD="scp"
fi

print_section "Pre-Migration Checks"

# Check if local deployment is running
if ! docker-compose -f docker-compose.local.yml ps | grep -q "Up"; then
    print_error "Local MEDHASAKTHI deployment is not running"
    print_info "Please start local deployment first: docker-compose -f docker-compose.local.yml up -d"
    exit 1
fi

print_status "Local deployment is running"

# Test cloud server connectivity
if ! $SSH_CMD "echo 'Connection test'" >/dev/null 2>&1; then
    print_error "Cannot connect to cloud server"
    print_info "Please check: IP address, SSH key, security groups/firewall"
    exit 1
fi

print_status "Cloud server is accessible"

print_section "Creating Backup"

# Create comprehensive backup
print_info "Creating full system backup..."
./backup-local.sh

# Export Docker volumes
print_info "Exporting Docker volumes..."
docker run --rm -v medhasakthi_postgres_data:/data -v $(pwd)/backups:/backup alpine tar czf /backup/postgres_volume.tar.gz -C /data .
docker run --rm -v medhasakthi_redis_data:/data -v $(pwd)/backups:/backup alpine tar czf /backup/redis_volume.tar.gz -C /data .

# Create migration package
print_info "Creating migration package..."
tar czf migration-package.tar.gz \
    .env \
    docker-compose.yml \
    nginx.conf \
    backups/ \
    uploads/ \
    certificates/ \
    backend/ \
    frontend/ \
    monitoring/

print_status "Migration package created"

print_section "Preparing Cloud Server"

# Install dependencies on cloud server
print_info "Installing dependencies on cloud server..."
$SSH_CMD "
    sudo apt update && sudo apt upgrade -y
    sudo apt install -y docker.io docker-compose git curl openssl nginx certbot
    sudo systemctl start docker
    sudo systemctl enable docker
    sudo usermod -a -G docker $CLOUD_USER
"

print_status "Dependencies installed on cloud server"

print_section "Transferring Data"

# Transfer migration package
print_info "Transferring migration package to cloud server..."
$SCP_CMD migration-package.tar.gz $CLOUD_USER@$CLOUD_SERVER_IP:/tmp/

# Extract on cloud server
print_info "Extracting migration package on cloud server..."
$SSH_CMD "
    cd /home/$CLOUD_USER
    tar xzf /tmp/migration-package.tar.gz
    sudo mkdir -p /app/{logs,backups,uploads,certificates,static}
    sudo chown -R $CLOUD_USER:$CLOUD_USER /app
    cp -r uploads/* /app/uploads/ 2>/dev/null || true
    cp -r backups/* /app/backups/ 2>/dev/null || true
    cp -r certificates/* /app/certificates/ 2>/dev/null || true
"

print_status "Data transferred to cloud server"

print_section "Setting Up Cloud Environment"

# Generate SSL certificate on cloud server
print_info "Generating SSL certificate on cloud server..."
$SSH_CMD "
    sudo certbot certonly --standalone -d $DOMAIN -d www.$DOMAIN --email admin@$DOMAIN --agree-tos --non-interactive
"

# Configure nginx on cloud server
print_info "Configuring nginx on cloud server..."
$SSH_CMD "
    sudo cp nginx.conf /etc/nginx/sites-available/medhasakthi
    sudo ln -sf /etc/nginx/sites-available/medhasakthi /etc/nginx/sites-enabled/
    sudo rm -f /etc/nginx/sites-enabled/default
    sudo nginx -t
    sudo systemctl enable nginx
    sudo systemctl restart nginx
"

print_status "Cloud environment configured"

print_section "Deploying Application"

# Start database services and restore data
print_info "Starting database services on cloud server..."
$SSH_CMD "
    cd /home/$CLOUD_USER
    docker-compose up -d postgres redis
    sleep 30
"

# Restore database data
print_info "Restoring database data..."
$SSH_CMD "
    cd /home/$CLOUD_USER
    # Restore PostgreSQL volume
    docker run --rm -v medhasakthi_postgres_data:/data -v /app/backups:/backup alpine tar xzf /backup/postgres_volume.tar.gz -C /data
    
    # Restore Redis volume
    docker run --rm -v medhasakthi_redis_data:/data -v /app/backups:/backup alpine tar xzf /backup/redis_volume.tar.gz -C /data
    
    # Restart database services
    docker-compose restart postgres redis
    sleep 30
"

# Deploy full application
print_info "Deploying full application on cloud server..."
$SSH_CMD "
    cd /home/$CLOUD_USER
    docker-compose build --no-cache
    docker-compose up -d
"

print_status "Application deployed on cloud server"

print_section "DNS Migration"

print_warning "IMPORTANT: DNS Update Required"
print_info "Update your DNS records to point to the cloud server:"
print_info "  A Record: $DOMAIN -> $CLOUD_SERVER_IP"
print_info "  A Record: www.$DOMAIN -> $CLOUD_SERVER_IP"
print_info ""
print_info "DNS propagation may take up to 24 hours"

print_section "Verification"

# Wait for services to start
print_info "Waiting for services to start on cloud server..."
sleep 60

# Test cloud deployment
print_info "Testing cloud deployment..."
if $SSH_CMD "curl -f http://localhost/health" >/dev/null 2>&1; then
    print_status "Cloud deployment is healthy"
else
    print_warning "Cloud deployment health check failed"
fi

print_section "Migration Cleanup"

print_info "Migration completed successfully!"
print_warning "Local deployment is still running. You can:"
print_info "1. Keep it running as backup until cloud is stable"
print_info "2. Stop it now: docker-compose -f docker-compose.local.yml down"
print_info "3. Remove local data: docker-compose -f docker-compose.local.yml down -v"

# Create post-migration verification script
cat > verify-migration.sh << 'EOF'
#!/bin/bash
echo "🔍 Verifying cloud migration..."

# Test cloud endpoints
echo "Testing cloud server..."
if curl -f https://medhasakthi.com/health >/dev/null 2>&1; then
    echo "✅ Cloud frontend is accessible"
else
    echo "❌ Cloud frontend is not accessible"
fi

if curl -f https://medhasakthi.com/api/health >/dev/null 2>&1; then
    echo "✅ Cloud API is accessible"
else
    echo "❌ Cloud API is not accessible"
fi

echo "Migration verification completed!"
EOF

chmod +x verify-migration.sh

# Display migration summary
echo ""
echo -e "${GREEN}🎉 MIGRATION COMPLETED SUCCESSFULLY! 🎉${NC}"
echo -e "${GREEN}====================================${NC}"
echo ""
echo -e "${BLUE}📋 Migration Summary:${NC}"
echo -e "   🌐 Domain: $DOMAIN"
echo -e "   ☁️  Cloud Server: $CLOUD_SERVER_IP"
echo -e "   🔄 Status: Data migrated, services deployed"
echo ""
echo -e "${BLUE}📝 Next Steps:${NC}"
echo -e "   1. Update DNS records to point to $CLOUD_SERVER_IP"
echo -e "   2. Wait for DNS propagation (up to 24 hours)"
echo -e "   3. Test cloud deployment: ./verify-migration.sh"
echo -e "   4. Monitor cloud services for 24-48 hours"
echo -e "   5. Stop local deployment when confident"
echo ""
echo -e "${BLUE}🔗 Cloud Access URLs:${NC}"
echo -e "   🏠 Main Site: https://$DOMAIN (after DNS update)"
echo -e "   🔧 API Docs: https://$DOMAIN/api/docs"
echo -e "   📊 Grafana: https://$DOMAIN:3001"
echo ""
echo -e "${BLUE}🔧 Cloud Server Management:${NC}"
echo -e "   📝 SSH: $SSH_CMD"
echo -e "   📝 Logs: $SSH_CMD 'docker-compose logs -f'"
echo -e "   📝 Status: $SSH_CMD 'docker-compose ps'"
echo ""
echo -e "${GREEN}🚀 MEDHASAKTHI is now running in the cloud! 🚀${NC}"
