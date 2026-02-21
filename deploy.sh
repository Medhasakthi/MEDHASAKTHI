#!/bin/bash

# MEDHASAKTHI Simple Deployment Script
# Works on Linux/macOS/WSL

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

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

echo -e "${BLUE}🚀 MEDHASAKTHI Deployment${NC}"
echo "================================"

# Check prerequisites
print_info "Checking prerequisites..."

if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

print_status "Prerequisites check passed"

# Check .env file
if [ ! -f ".env" ]; then
    print_warning ".env file not found. Creating from template..."
    if [ -f "backend/.env.example" ]; then
        cp backend/.env.example .env
        print_warning "Please update the .env file with your actual values before continuing."
        print_info "Edit .env file and run this script again."
        exit 1
    else
        print_error "No .env template found. Please create .env file manually."
        exit 1
    fi
fi

print_status ".env file found"

# Create necessary directories
print_info "Creating application directories..."
mkdir -p uploads certificates logs backups
print_status "Directories created"

# Build and start services
print_info "Building and starting MEDHASAKTHI services..."

# Stop any existing containers
docker-compose down --remove-orphans

# Build images
docker-compose build --no-cache

# Start services
docker-compose up -d

print_status "Services started successfully"

# Wait for services to be ready
print_info "Waiting for services to start..."
sleep 30

# Health checks
print_info "Running health checks..."

# Check backend
if curl -f http://localhost:8080/health &> /dev/null; then
    print_status "Backend service is healthy"
else
    print_warning "Backend service may not be ready yet"
fi

# Check frontend
if curl -f http://localhost:3000 &> /dev/null; then
    print_status "Frontend service is healthy"
else
    print_warning "Frontend service may not be ready yet"
fi

echo ""
echo -e "${GREEN}🎉 MEDHASAKTHI Deployment Complete!${NC}"
echo ""
echo "Access your application:"
echo "  Frontend: http://localhost:3000"
echo "  Backend API: http://localhost:8080"
echo "  API Docs: http://localhost:8080/docs"
echo ""
echo "To view logs: docker-compose logs -f"
echo "To stop: docker-compose down"
echo ""
print_info "Make sure to update your .env file with production values!"
