#!/bin/bash

# MEDHASAKTHI Deployment Fix Script
# This script fixes common deployment issues

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

echo -e "${BLUE}🔧 MEDHASAKTHI Deployment Fix${NC}"
echo "=================================="

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker first."
    exit 1
fi

print_info "Step 1: Stopping existing containers..."
docker-compose down || true

print_info "Step 2: Removing old images..."
docker-compose down --rmi all --volumes --remove-orphans || true

print_info "Step 3: Building fresh images..."
docker-compose build --no-cache

print_info "Step 4: Starting services..."
docker-compose up -d

print_info "Step 5: Waiting for services to start..."
sleep 30

print_info "Step 6: Checking service status..."
docker-compose ps

print_info "Step 7: Checking frontend container..."
if docker-compose exec frontend ls -la /usr/share/nginx/html/ | grep -q index.html; then
    print_status "Frontend build files found"
else
    print_error "Frontend build files missing"
    print_info "Checking build directory..."
    docker-compose exec frontend ls -la /usr/share/nginx/html/
fi

print_info "Step 8: Testing endpoints..."
echo "Testing main frontend..."
if curl -f http://localhost:3000/ > /dev/null 2>&1; then
    print_status "Frontend is responding"
else
    print_warning "Frontend not responding directly"
fi

echo "Testing through nginx proxy..."
if curl -f http://localhost/ > /dev/null 2>&1; then
    print_status "Nginx proxy is working"
else
    print_warning "Nginx proxy not responding"
fi

echo "Testing backend..."
if curl -f http://localhost:8080/health > /dev/null 2>&1; then
    print_status "Backend is responding"
else
    print_warning "Backend not responding"
fi

print_info "Step 9: Showing logs for debugging..."
echo "Frontend logs:"
docker-compose logs --tail=20 frontend

echo "Nginx logs:"
docker-compose logs --tail=20 nginx

echo "Backend logs:"
docker-compose logs --tail=20 backend

print_status "Deployment fix completed!"
print_info "Access your application at:"
echo "  🌐 Main site: http://localhost"
echo "  🌐 Frontend direct: http://localhost:3000"
echo "  🌐 Backend API: http://localhost:8080"
echo "  📚 API docs: http://localhost:8080/docs"

print_info "If you're still seeing file listings instead of the app:"
echo "  1. Check if the React build completed successfully"
echo "  2. Verify nginx is serving from the correct directory"
echo "  3. Ensure index.html exists in the build output"
echo "  4. Check browser console for JavaScript errors"
