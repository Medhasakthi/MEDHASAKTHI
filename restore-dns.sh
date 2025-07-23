#!/bin/bash

# MEDHASAKTHI DNS Restore Script
# This script removes local DNS entries to access the real domain

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

echo -e "${BLUE}🌐 MEDHASAKTHI DNS Restore Script${NC}"
echo -e "${BLUE}=================================${NC}"
echo ""

# Check if backup exists
if [[ ! -f "/etc/hosts.backup" ]]; then
    print_error "No backup found. Cannot restore DNS settings."
    print_info "You may need to manually remove medhasakthi.com entries from /etc/hosts"
    exit 1
fi

print_info "This will restore your original DNS settings"
print_warning "After running this script, medhasakthi.com will point to the real domain"
print_warning "Your local MEDHASAKTHI deployment will not be accessible via the domain"
echo ""

# Ask for confirmation
read -p "Do you want to continue? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    print_info "Operation cancelled"
    exit 0
fi

# Restore original hosts file
print_info "Restoring original /etc/hosts file..."
sudo cp /etc/hosts.backup /etc/hosts

print_status "DNS settings restored successfully!"
print_info "medhasakthi.com now points to the real domain"
echo ""

print_info "To access your local deployment again:"
echo "1. Run ./deploy-local.sh to reconfigure local DNS"
echo "2. Or manually add entries back to /etc/hosts"
echo ""

print_info "Current DNS status:"
if grep -q "medhasakthi.com" /etc/hosts; then
    print_warning "medhasakthi.com entries still found in /etc/hosts"
    echo "Entries found:"
    grep "medhasakthi.com" /etc/hosts
else
    print_status "No local medhasakthi.com entries found"
    print_info "Domain will resolve to real IP address"
fi

echo ""
print_status "DNS restore completed!"
