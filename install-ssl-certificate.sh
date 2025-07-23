#!/bin/bash

# MEDHASAKTHI SSL Certificate Installation Script
# This script helps install the self-signed certificate to avoid browser warnings

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

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

echo -e "${BLUE}🔒 MEDHASAKTHI SSL Certificate Installation${NC}"
echo -e "${BLUE}===========================================${NC}"
echo ""

# Check if certificate exists
if [[ ! -f "certificates/medhasakthi.com.crt" ]]; then
    print_error "SSL certificate not found. Please run ./deploy-local.sh first."
    exit 1
fi

# Detect operating system
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    print_info "Detected Linux system"
    
    # Check if running on Ubuntu/Debian
    if command -v apt-get >/dev/null 2>&1; then
        print_info "Installing certificate for Ubuntu/Debian..."
        
        # Copy certificate to system store
        sudo cp certificates/medhasakthi.com.crt /usr/local/share/ca-certificates/medhasakthi.com.crt
        sudo update-ca-certificates
        
        print_status "Certificate installed system-wide"
        print_info "For browsers, you may need to:"
        print_info "1. Open Chrome/Firefox settings"
        print_info "2. Go to Privacy & Security > Certificates"
        print_info "3. Import certificates/medhasakthi.com.crt"
        
    elif command -v yum >/dev/null 2>&1; then
        print_info "Installing certificate for CentOS/RHEL..."
        
        # Copy certificate to system store
        sudo cp certificates/medhasakthi.com.crt /etc/pki/ca-trust/source/anchors/
        sudo update-ca-trust
        
        print_status "Certificate installed system-wide"
        
    else
        print_warning "Unsupported Linux distribution"
        print_info "Please manually add certificates/medhasakthi.com.crt to your browser's trusted certificates"
    fi
    
elif [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    print_info "Detected macOS system"
    print_info "Installing certificate to macOS Keychain..."
    
    # Add to system keychain
    sudo security add-trusted-cert -d -r trustRoot -k /Library/Keychains/System.keychain certificates/medhasakthi.com.crt
    
    print_status "Certificate installed to macOS Keychain"
    print_info "The certificate should now be trusted by Safari and Chrome"
    
elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
    # Windows
    print_info "Detected Windows system"
    print_info "Installing certificate to Windows Certificate Store..."
    
    # Convert to Windows path
    CERT_PATH=$(cygpath -w "$(pwd)/certificates/medhasakthi.com.crt")
    
    # Import certificate
    certlm.exe -add -c "$CERT_PATH" -s -r localMachine root
    
    print_status "Certificate installed to Windows Certificate Store"
    print_info "The certificate should now be trusted by Edge and Chrome"
    
else
    print_warning "Unsupported operating system: $OSTYPE"
    print_info "Please manually add certificates/medhasakthi.com.crt to your browser's trusted certificates"
fi

echo ""
print_info "Manual Browser Installation (if automatic installation didn't work):"
echo ""
echo "Chrome/Edge:"
echo "1. Go to chrome://settings/certificates"
echo "2. Click 'Authorities' tab"
echo "3. Click 'Import' and select certificates/medhasakthi.com.crt"
echo "4. Check 'Trust this certificate for identifying websites'"
echo ""
echo "Firefox:"
echo "1. Go to about:preferences#privacy"
echo "2. Scroll to 'Certificates' and click 'View Certificates'"
echo "3. Click 'Authorities' tab"
echo "4. Click 'Import' and select certificates/medhasakthi.com.crt"
echo "5. Check 'Trust this CA to identify websites'"
echo ""
echo "Safari (macOS):"
echo "1. Double-click certificates/medhasakthi.com.crt"
echo "2. In Keychain Access, find the certificate"
echo "3. Double-click it and expand 'Trust'"
echo "4. Set 'When using this certificate' to 'Always Trust'"
echo ""

print_status "SSL certificate installation completed!"
print_info "You may need to restart your browser for changes to take effect."
print_info "After installation, https://medhasakthi.com should load without warnings."
