#!/bin/bash

# MEDHASAKTHI Complete Setup Script
# This script installs dependencies and deploys MEDHASAKTHI locally

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

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
    echo -e "${PURPLE}$(printf '=%.0s' {1..60})${NC}"
}

print_banner() {
    echo -e "${CYAN}"
    echo "███╗   ███╗███████╗██████╗ ██╗  ██╗ █████╗ ███████╗ █████╗ ██╗  ██╗████████╗██╗  ██╗██╗"
    echo "████╗ ████║██╔════╝██╔══██╗██║  ██║██╔══██╗██╔════╝██╔══██╗██║ ██╔╝╚══██╔══╝██║  ██║██║"
    echo "██╔████╔██║█████╗  ██║  ██║███████║███████║███████╗███████║█████╔╝    ██║   ███████║██║"
    echo "██║╚██╔╝██║██╔══╝  ██║  ██║██╔══██║██╔══██║╚════██║██╔══██║██╔═██╗    ██║   ██╔══██║██║"
    echo "██║ ╚═╝ ██║███████╗██████╔╝██║  ██║██║  ██║███████║██║  ██║██║  ██╗   ██║   ██║  ██║██║"
    echo "╚═╝     ╚═╝╚══════╝╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝╚═╝"
    echo -e "${NC}"
    echo -e "${BLUE}🚀 Complete Local Desktop Deployment Setup${NC}"
    echo -e "${BLUE}===========================================${NC}"
    echo ""
}

# Check if running as root
check_root() {
    if [[ $EUID -eq 0 ]]; then
        print_error "This script should not be run as root"
        print_info "Please run as a regular user with sudo privileges"
        exit 1
    fi
}

# Check system requirements
check_system_requirements() {
    print_section "System Requirements Check"
    
    # Check available memory
    if command -v free >/dev/null 2>&1; then
        MEMORY_GB=$(free -g | awk '/^Mem:/{print $2}')
        if [ "$MEMORY_GB" -lt 4 ]; then
            print_warning "Less than 4GB RAM detected (${MEMORY_GB}GB). Performance may be affected."
        else
            print_status "Memory check passed (${MEMORY_GB}GB available)"
        fi
    elif command -v vm_stat >/dev/null 2>&1; then
        # macOS memory check
        MEMORY_BYTES=$(sysctl -n hw.memsize)
        MEMORY_GB=$((MEMORY_BYTES / 1024 / 1024 / 1024))
        if [ "$MEMORY_GB" -lt 4 ]; then
            print_warning "Less than 4GB RAM detected (${MEMORY_GB}GB). Performance may be affected."
        else
            print_status "Memory check passed (${MEMORY_GB}GB available)"
        fi
    fi
    
    # Check disk space
    DISK_SPACE=$(df -BG . | awk 'NR==2 {print $4}' | sed 's/G//')
    if [ "$DISK_SPACE" -lt 10 ]; then
        print_error "Insufficient disk space. At least 10GB required, ${DISK_SPACE}GB available."
        exit 1
    else
        print_status "Disk space check passed (${DISK_SPACE}GB available)"
    fi
    
    # Check internet connectivity
    if ping -c 1 google.com >/dev/null 2>&1; then
        print_status "Internet connectivity check passed"
    else
        print_error "No internet connection. Please check your network."
        exit 1
    fi
}

# Install dependencies
install_dependencies() {
    print_section "Installing Dependencies"
    
    if [[ ! -f "install-dependencies.sh" ]]; then
        print_error "install-dependencies.sh not found"
        exit 1
    fi
    
    chmod +x install-dependencies.sh
    print_info "Running dependency installation..."
    ./install-dependencies.sh
    
    print_status "Dependencies installation completed"
}

# Check if Docker is running
check_docker() {
    print_section "Docker Service Check"
    
    if ! command -v docker >/dev/null 2>&1; then
        print_error "Docker is not installed. Please run the dependency installation first."
        exit 1
    fi
    
    # Try to start Docker if it's not running
    if ! docker info >/dev/null 2>&1; then
        print_info "Docker is not running. Attempting to start..."
        
        if [[ "$OSTYPE" == "linux-gnu"* ]]; then
            sudo systemctl start docker
            sleep 5
        else
            print_warning "Please start Docker Desktop manually and run this script again"
            exit 1
        fi
        
        if ! docker info >/dev/null 2>&1; then
            print_error "Failed to start Docker. Please start Docker Desktop manually."
            exit 1
        fi
    fi
    
    print_status "Docker is running"
}

# Deploy MEDHASAKTHI
deploy_medhasakthi() {
    print_section "Deploying MEDHASAKTHI"
    
    if [[ ! -f "deploy-local.sh" ]]; then
        print_error "deploy-local.sh not found"
        exit 1
    fi
    
    chmod +x deploy-local.sh
    print_info "Running MEDHASAKTHI deployment..."
    sudo ./deploy-local.sh
    
    print_status "MEDHASAKTHI deployment completed"
}

# Install SSL certificates
install_ssl() {
    print_section "Installing SSL Certificates"
    
    if [[ ! -f "install-ssl-certificate.sh" ]]; then
        print_error "install-ssl-certificate.sh not found"
        exit 1
    fi
    
    chmod +x install-ssl-certificate.sh
    print_info "Installing SSL certificates to avoid browser warnings..."
    ./install-ssl-certificate.sh
    
    print_status "SSL certificates installed"
}

# Final verification
verify_deployment() {
    print_section "Deployment Verification"
    
    print_info "Waiting for services to start..."
    sleep 30
    
    # Check if main site is accessible
    if curl -k -f https://medhasakthi.com >/dev/null 2>&1; then
        print_status "Main site is accessible: https://medhasakthi.com"
    else
        print_warning "Main site health check failed"
    fi
    
    # Check API
    if curl -k -f https://api.medhasakthi.com/health >/dev/null 2>&1; then
        print_status "API is accessible: https://api.medhasakthi.com"
    else
        print_warning "API health check failed"
    fi
    
    # Check subdomains
    for subdomain in student teacher admin learn; do
        if curl -k -f https://$subdomain.medhasakthi.com >/dev/null 2>&1; then
            print_status "$subdomain portal is accessible"
        else
            print_warning "$subdomain portal health check failed"
        fi
    done
}

# Show final instructions
show_final_instructions() {
    echo ""
    echo -e "${GREEN}🎉 MEDHASAKTHI DEPLOYMENT COMPLETED SUCCESSFULLY! 🎉${NC}"
    echo -e "${GREEN}====================================================${NC}"
    echo ""
    
    echo -e "${CYAN}📱 Access Your Application:${NC}"
    echo -e "   🏠 Main Site: ${YELLOW}https://medhasakthi.com${NC}"
    echo -e "   👨‍🎓 Student Portal: ${YELLOW}https://student.medhasakthi.com${NC}"
    echo -e "   👨‍🏫 Teacher Portal: ${YELLOW}https://teacher.medhasakthi.com${NC}"
    echo -e "   🏢 Admin Portal: ${YELLOW}https://admin.medhasakthi.com${NC}"
    echo -e "   🎯 Learn Portal: ${YELLOW}https://learn.medhasakthi.com${NC}"
    echo -e "   🔧 API Docs: ${YELLOW}https://api.medhasakthi.com/docs${NC}"
    echo ""
    
    echo -e "${CYAN}👤 Default Admin Credentials:${NC}"
    echo -e "   📧 Email: ${YELLOW}admin@medhasakthi.com${NC}"
    echo -e "   🔑 Password: ${YELLOW}admin123${NC}"
    echo ""
    
    echo -e "${CYAN}🛠️ Development Tools:${NC}"
    echo -e "   📊 Grafana: ${YELLOW}http://localhost:3001${NC} (admin/admin123)"
    echo -e "   🔍 Prometheus: ${YELLOW}http://localhost:9090${NC}"
    echo ""
    
    echo -e "${CYAN}⚙️ Configuration:${NC}"
    echo -e "   📝 Update email settings in ${YELLOW}.env${NC} file"
    echo -e "   🔑 Add OpenAI API key for AI features"
    echo -e "   📧 Configure SMTP for email verification"
    echo ""
    
    echo -e "${CYAN}🔄 Useful Commands:${NC}"
    echo -e "   📊 View logs: ${YELLOW}docker-compose -f docker-compose.local.yml logs -f${NC}"
    echo -e "   🔄 Restart: ${YELLOW}docker-compose -f docker-compose.local.yml restart${NC}"
    echo -e "   🛑 Stop: ${YELLOW}docker-compose -f docker-compose.local.yml down${NC}"
    echo -e "   🌐 Restore DNS: ${YELLOW}./restore-dns.sh${NC}"
    echo ""
    
    echo -e "${CYAN}📋 Next Steps:${NC}"
    echo "   1. Visit https://medhasakthi.com in your browser"
    echo "   2. Click 'Login / Sign Up' to test category selection"
    echo "   3. Update .env file with your email and API keys"
    echo "   4. Test all user portals and features"
    echo "   5. Customize branding and content as needed"
    echo ""
    
    print_warning "If you see SSL warnings, the certificates may need a few minutes to be trusted"
    print_info "You can also manually trust the certificate in your browser settings"
    echo ""
    
    echo -e "${GREEN}🚀 MEDHASAKTHI is now running locally with your real domain! 🚀${NC}"
}

# Main execution
main() {
    print_banner
    check_root
    check_system_requirements
    
    print_info "This script will:"
    echo "   1. Install all required dependencies (Docker, Node.js, Python, etc.)"
    echo "   2. Configure local DNS for medhasakthi.com"
    echo "   3. Generate SSL certificates"
    echo "   4. Deploy the complete MEDHASAKTHI platform"
    echo "   5. Set up monitoring and analytics"
    echo ""
    
    read -p "Do you want to continue? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_info "Setup cancelled"
        exit 0
    fi
    
    echo ""
    print_info "Starting MEDHASAKTHI setup..."
    echo ""
    
    install_dependencies
    check_docker
    deploy_medhasakthi
    install_ssl
    verify_deployment
    show_final_instructions
}

# Run main function
main "$@"
