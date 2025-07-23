#!/bin/bash

# MEDHASAKTHI Dependencies Installation Script
# This script installs all required software for local deployment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
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
    echo -e "${PURPLE}$(printf '=%.0s' {1..50})${NC}"
}

echo -e "${BLUE}🚀 MEDHASAKTHI Dependencies Installation${NC}"
echo -e "${BLUE}=======================================${NC}"
echo ""

# Check if running as root
if [[ $EUID -eq 0 ]]; then
    print_error "This script should not be run as root"
    print_info "Please run as a regular user with sudo privileges"
    exit 1
fi

# Detect operating system
detect_os() {
    print_section "System Detection"
    
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if [ -f /etc/os-release ]; then
            . /etc/os-release
            OS=$NAME
            VER=$VERSION_ID
        fi
        print_info "Detected: $OS $VER"
        
        if command -v apt-get >/dev/null 2>&1; then
            PACKAGE_MANAGER="apt"
            print_info "Package Manager: APT (Ubuntu/Debian)"
        elif command -v yum >/dev/null 2>&1; then
            PACKAGE_MANAGER="yum"
            print_info "Package Manager: YUM (CentOS/RHEL)"
        elif command -v dnf >/dev/null 2>&1; then
            PACKAGE_MANAGER="dnf"
            print_info "Package Manager: DNF (Fedora)"
        else
            print_error "Unsupported Linux distribution"
            exit 1
        fi
        
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macOS"
        VER=$(sw_vers -productVersion)
        PACKAGE_MANAGER="brew"
        print_info "Detected: macOS $VER"
        print_info "Package Manager: Homebrew"
        
    elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
        OS="Windows"
        PACKAGE_MANAGER="choco"
        print_info "Detected: Windows with $OSTYPE"
        print_info "Package Manager: Chocolatey"
        
    else
        print_error "Unsupported operating system: $OSTYPE"
        exit 1
    fi
}

# Update package repositories
update_repositories() {
    print_section "Updating Package Repositories"
    
    case $PACKAGE_MANAGER in
        "apt")
            print_info "Updating APT repositories..."
            sudo apt-get update
            print_status "APT repositories updated"
            ;;
        "yum")
            print_info "Updating YUM repositories..."
            sudo yum update -y
            print_status "YUM repositories updated"
            ;;
        "dnf")
            print_info "Updating DNF repositories..."
            sudo dnf update -y
            print_status "DNF repositories updated"
            ;;
        "brew")
            print_info "Updating Homebrew..."
            brew update
            print_status "Homebrew updated"
            ;;
        "choco")
            print_info "Updating Chocolatey..."
            choco upgrade chocolatey -y
            print_status "Chocolatey updated"
            ;;
    esac
}

# Install basic tools
install_basic_tools() {
    print_section "Installing Basic Tools"
    
    case $PACKAGE_MANAGER in
        "apt")
            sudo apt-get install -y curl wget git openssl ca-certificates gnupg lsb-release
            ;;
        "yum")
            sudo yum install -y curl wget git openssl ca-certificates
            ;;
        "dnf")
            sudo dnf install -y curl wget git openssl ca-certificates
            ;;
        "brew")
            brew install curl wget git openssl
            ;;
        "choco")
            choco install -y curl wget git openssl
            ;;
    esac
    
    print_status "Basic tools installed"
}

# Install Docker
install_docker() {
    print_section "Installing Docker"
    
    if command -v docker >/dev/null 2>&1; then
        print_info "Docker is already installed"
        DOCKER_VERSION=$(docker --version | cut -d' ' -f3 | cut -d',' -f1)
        print_info "Docker version: $DOCKER_VERSION"
        return
    fi
    
    case $PACKAGE_MANAGER in
        "apt")
            print_info "Installing Docker for Ubuntu/Debian..."
            
            # Add Docker's official GPG key
            sudo mkdir -p /etc/apt/keyrings
            curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
            
            # Add Docker repository
            echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
            
            # Install Docker
            sudo apt-get update
            sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
            ;;
            
        "yum")
            print_info "Installing Docker for CentOS/RHEL..."
            sudo yum install -y yum-utils
            sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
            sudo yum install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
            ;;
            
        "dnf")
            print_info "Installing Docker for Fedora..."
            sudo dnf -y install dnf-plugins-core
            sudo dnf config-manager --add-repo https://download.docker.com/linux/fedora/docker-ce.repo
            sudo dnf install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
            ;;
            
        "brew")
            print_info "Installing Docker Desktop for macOS..."
            print_warning "Please download Docker Desktop from: https://www.docker.com/products/docker-desktop"
            print_warning "This script cannot automatically install Docker Desktop on macOS"
            print_info "After installing Docker Desktop, please restart this script"
            exit 1
            ;;
            
        "choco")
            print_info "Installing Docker Desktop for Windows..."
            choco install -y docker-desktop
            print_warning "Please restart your computer after Docker Desktop installation"
            ;;
    esac
    
    # Start and enable Docker service (Linux only)
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        sudo systemctl start docker
        sudo systemctl enable docker
        
        # Add current user to docker group
        sudo usermod -aG docker $USER
        print_warning "You need to log out and log back in for Docker group changes to take effect"
    fi
    
    print_status "Docker installed successfully"
}

# Install Docker Compose (if not included with Docker)
install_docker_compose() {
    print_section "Installing Docker Compose"
    
    if command -v docker-compose >/dev/null 2>&1; then
        print_info "Docker Compose is already installed"
        COMPOSE_VERSION=$(docker-compose --version | cut -d' ' -f3 | cut -d',' -f1)
        print_info "Docker Compose version: $COMPOSE_VERSION"
        return
    fi
    
    if docker compose version >/dev/null 2>&1; then
        print_info "Docker Compose (v2) is already installed"
        return
    fi
    
    print_info "Installing Docker Compose..."
    
    # Install Docker Compose v2
    COMPOSE_VERSION=$(curl -s https://api.github.com/repos/docker/compose/releases/latest | grep 'tag_name' | cut -d\" -f4)
    
    case $PACKAGE_MANAGER in
        "apt"|"yum"|"dnf")
            sudo curl -L "https://github.com/docker/compose/releases/download/${COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
            sudo chmod +x /usr/local/bin/docker-compose
            ;;
        "brew")
            brew install docker-compose
            ;;
        "choco")
            choco install -y docker-compose
            ;;
    esac
    
    print_status "Docker Compose installed successfully"
}

# Install Node.js and npm (for frontend development)
install_nodejs() {
    print_section "Installing Node.js and npm"
    
    if command -v node >/dev/null 2>&1; then
        print_info "Node.js is already installed"
        NODE_VERSION=$(node --version)
        NPM_VERSION=$(npm --version)
        print_info "Node.js version: $NODE_VERSION"
        print_info "npm version: $NPM_VERSION"
        return
    fi
    
    case $PACKAGE_MANAGER in
        "apt")
            # Install Node.js 18.x LTS
            curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
            sudo apt-get install -y nodejs
            ;;
        "yum")
            curl -fsSL https://rpm.nodesource.com/setup_18.x | sudo bash -
            sudo yum install -y nodejs npm
            ;;
        "dnf")
            curl -fsSL https://rpm.nodesource.com/setup_18.x | sudo bash -
            sudo dnf install -y nodejs npm
            ;;
        "brew")
            brew install node
            ;;
        "choco")
            choco install -y nodejs
            ;;
    esac
    
    print_status "Node.js and npm installed successfully"
}

# Install Python and pip (for backend development)
install_python() {
    print_section "Installing Python and pip"
    
    if command -v python3 >/dev/null 2>&1; then
        print_info "Python 3 is already installed"
        PYTHON_VERSION=$(python3 --version)
        print_info "Python version: $PYTHON_VERSION"
        
        if command -v pip3 >/dev/null 2>&1; then
            print_info "pip3 is already installed"
            return
        fi
    fi
    
    case $PACKAGE_MANAGER in
        "apt")
            sudo apt-get install -y python3 python3-pip python3-venv
            ;;
        "yum")
            sudo yum install -y python3 python3-pip
            ;;
        "dnf")
            sudo dnf install -y python3 python3-pip
            ;;
        "brew")
            brew install python
            ;;
        "choco")
            choco install -y python
            ;;
    esac
    
    print_status "Python and pip installed successfully"
}

# Verify installations
verify_installations() {
    print_section "Verifying Installations"
    
    # Check Docker
    if command -v docker >/dev/null 2>&1; then
        print_status "Docker: $(docker --version)"
    else
        print_error "Docker installation failed"
    fi
    
    # Check Docker Compose
    if command -v docker-compose >/dev/null 2>&1; then
        print_status "Docker Compose: $(docker-compose --version)"
    elif docker compose version >/dev/null 2>&1; then
        print_status "Docker Compose: $(docker compose version)"
    else
        print_error "Docker Compose installation failed"
    fi
    
    # Check Node.js
    if command -v node >/dev/null 2>&1; then
        print_status "Node.js: $(node --version)"
    else
        print_warning "Node.js not installed (optional for development)"
    fi
    
    # Check Python
    if command -v python3 >/dev/null 2>&1; then
        print_status "Python: $(python3 --version)"
    else
        print_warning "Python not installed (optional for development)"
    fi
    
    # Check Git
    if command -v git >/dev/null 2>&1; then
        print_status "Git: $(git --version)"
    else
        print_error "Git installation failed"
    fi
    
    # Check OpenSSL
    if command -v openssl >/dev/null 2>&1; then
        print_status "OpenSSL: $(openssl version)"
    else
        print_error "OpenSSL installation failed"
    fi
}

# Main installation process
main() {
    detect_os
    update_repositories
    install_basic_tools
    install_docker
    install_docker_compose
    install_nodejs
    install_python
    verify_installations
    
    echo ""
    print_status "🎉 All dependencies installed successfully!"
    echo ""
    
    print_info "Next Steps:"
    echo "1. If on Linux, log out and log back in (for Docker group changes)"
    echo "2. Start Docker Desktop (if on Windows/macOS)"
    echo "3. Run: sudo ./deploy-local.sh"
    echo ""
    
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        print_warning "IMPORTANT: You need to log out and log back in for Docker to work properly"
        print_info "Or run: newgrp docker"
    fi
    
    print_info "Ready to deploy MEDHASAKTHI! 🚀"
}

# Run main function
main "$@"
