#!/bin/bash

# MEDHASAKTHI Production Server Setup Script
# This script prepares a Ubuntu server for MEDHASAKTHI deployment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

echo -e "${BLUE}🚀 MEDHASAKTHI Production Server Setup${NC}"
echo "========================================"

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    print_warning "Running as root. Consider using a non-root user with sudo privileges."
fi

# Update system
print_info "Step 1: Updating system packages..."
sudo apt update && sudo apt upgrade -y
print_status "System updated"

# Install Docker
print_info "Step 2: Installing Docker..."
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    print_status "Docker installed"
else
    print_status "Docker already installed"
fi

# Install Docker Compose
print_info "Step 3: Installing Docker Compose..."
if ! command -v docker-compose &> /dev/null; then
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    print_status "Docker Compose installed"
else
    print_status "Docker Compose already installed"
fi

# Install Git
print_info "Step 4: Installing Git..."
if ! command -v git &> /dev/null; then
    sudo apt install -y git
    print_status "Git installed"
else
    print_status "Git already installed"
fi

# Install other dependencies
print_info "Step 5: Installing additional dependencies..."
sudo apt install -y curl wget unzip nginx certbot python3-certbot-nginx
print_status "Additional dependencies installed"

# Create application directory
print_info "Step 6: Setting up application directory..."
sudo mkdir -p /opt/medhasakthi
sudo chown $USER:$USER /opt/medhasakthi
print_status "Application directory created"

# Clone repository
print_info "Step 7: Cloning MEDHASAKTHI repository..."
cd /opt/medhasakthi
if [ ! -d ".git" ]; then
    git clone https://github.com/YOUR_USERNAME/MEDHASAKTHI.git .
    print_status "Repository cloned"
else
    print_status "Repository already exists"
fi

# Set up environment file
print_info "Step 8: Setting up environment file..."
if [ ! -f .env ]; then
    cp .env.example .env
    print_warning "Please edit .env file with your production values"
    print_info "Run: nano /opt/medhasakthi/.env"
else
    print_status "Environment file already exists"
fi

# Set up SSH key for GitHub Actions
print_info "Step 9: Setting up SSH key for GitHub Actions..."
if [ ! -f ~/.ssh/github_actions_key ]; then
    ssh-keygen -t rsa -b 4096 -C "github-actions@medhasakthi.com" -f ~/.ssh/github_actions_key -N ""
    cat ~/.ssh/github_actions_key.pub >> ~/.ssh/authorized_keys
    chmod 600 ~/.ssh/authorized_keys
    print_status "SSH key generated"
    
    echo ""
    print_info "🔑 IMPORTANT: Add this private key to GitHub Secrets as PRODUCTION_SSH_KEY:"
    echo "=================================================="
    cat ~/.ssh/github_actions_key
    echo "=================================================="
    echo ""
else
    print_status "SSH key already exists"
fi

# Set up firewall
print_info "Step 10: Configuring firewall..."
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443
sudo ufw --force enable
print_status "Firewall configured"

# Set up SSL certificate (optional)
print_info "Step 11: SSL Certificate setup..."
read -p "Do you want to set up SSL certificate now? (y/n): " setup_ssl
if [ "$setup_ssl" = "y" ]; then
    read -p "Enter your domain name (e.g., medhasakthi.com): " domain_name
    sudo certbot --nginx -d $domain_name -d www.$domain_name
    print_status "SSL certificate configured"
else
    print_warning "SSL certificate setup skipped. You can run 'sudo certbot --nginx -d yourdomain.com' later"
fi

# Create systemd service for auto-start
print_info "Step 12: Creating systemd service..."
sudo tee /etc/systemd/system/medhasakthi.service > /dev/null <<EOF
[Unit]
Description=MEDHASAKTHI Application
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/medhasakthi
ExecStart=/usr/local/bin/docker-compose up -d
ExecStop=/usr/local/bin/docker-compose down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable medhasakthi.service
print_status "Systemd service created"

# Initial deployment
print_info "Step 13: Initial deployment..."
cd /opt/medhasakthi
docker-compose build
docker-compose up -d
print_status "Initial deployment completed"

# Final checks
print_info "Step 14: Running final checks..."
sleep 30

if curl -f http://localhost:8080/health > /dev/null 2>&1; then
    print_status "Backend is running"
else
    print_warning "Backend health check failed"
fi

if curl -f http://localhost:3000 > /dev/null 2>&1; then
    print_status "Frontend is running"
else
    print_warning "Frontend health check failed"
fi

echo ""
print_status "🎉 Production server setup completed!"
echo ""
print_info "Next steps:"
echo "1. Edit /opt/medhasakthi/.env with your production values"
echo "2. Add the SSH private key (shown above) to GitHub Secrets as PRODUCTION_SSH_KEY"
echo "3. Add these GitHub Secrets:"
echo "   - PRODUCTION_HOST: $(curl -s ifconfig.me || hostname -I | awk '{print $1}')"
echo "   - PRODUCTION_USER: $USER"
echo "   - DOMAIN: your-domain.com"
echo "4. Push to main branch to trigger automatic deployment"
echo ""
print_info "Server Information:"
echo "   - Application Path: /opt/medhasakthi"
echo "   - SSH User: $USER"
echo "   - Server IP: $(curl -s ifconfig.me || hostname -I | awk '{print $1}')"
echo "   - Docker Status: $(sudo systemctl is-active docker)"
echo "   - Application Status: $(sudo systemctl is-active medhasakthi)"
echo ""
print_warning "Remember to:"
echo "   - Configure your domain DNS to point to this server"
echo "   - Update .env file with production values"
echo "   - Set up SSL certificate if not done already"
