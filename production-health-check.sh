#!/bin/bash

# MEDHASAKTHI Production Health Check Script

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

echo -e "${BLUE}🔍 MEDHASAKTHI Production Health Check${NC}"
echo "========================================"

# Check if Docker is running
if ! docker ps >/dev/null 2>&1; then
    print_error "Docker is not running"
    exit 1
fi

print_status "Docker is running"

# Check if containers are running
print_info "Checking container status..."

containers=("medhasakthi-postgres" "medhasakthi-redis" "medhasakthi-backend" "medhasakthi-frontend")
all_running=true

for container in "${containers[@]}"; do
    if docker ps --format "table {{.Names}}" | grep -q "^$container$"; then
        print_status "Container $container is running"
    else
        print_error "Container $container is not running"
        all_running=false
    fi
done

if [ "$all_running" = false ]; then
    print_error "Some containers are not running"
    exit 1
fi

# Check health endpoints
print_info "Checking health endpoints..."

# Backend health check
if curl -f -s http://localhost:8000/health >/dev/null; then
    print_status "Backend health check passed"
else
    print_error "Backend health check failed"
    exit 1
fi

# Frontend health check
if curl -f -s http://localhost:3000 >/dev/null; then
    print_status "Frontend health check passed"
else
    print_warning "Frontend health check failed (may be normal if using nginx)"
fi

# Database connection check
print_info "Checking database connection..."
if docker exec medhasakthi-postgres pg_isready -U admin -d medhasakthi >/dev/null 2>&1; then
    print_status "Database connection is healthy"
else
    print_error "Database connection failed"
    exit 1
fi

# Redis connection check
print_info "Checking Redis connection..."
if docker exec medhasakthi-redis redis-cli ping >/dev/null 2>&1; then
    print_status "Redis connection is healthy"
else
    print_error "Redis connection failed"
    exit 1
fi

# Check disk space
print_info "Checking disk space..."
disk_usage=$(df / | awk 'NR==2 {print $5}' | sed 's/%//')
if [ "$disk_usage" -gt 80 ]; then
    print_warning "Disk usage is high: ${disk_usage}%"
elif [ "$disk_usage" -gt 90 ]; then
    print_error "Disk usage is critical: ${disk_usage}%"
    exit 1
else
    print_status "Disk usage is normal: ${disk_usage}%"
fi

# Check memory usage
print_info "Checking memory usage..."
memory_usage=$(free | awk 'NR==2{printf "%.0f", $3*100/$2}')
if [ "$memory_usage" -gt 80 ]; then
    print_warning "Memory usage is high: ${memory_usage}%"
elif [ "$memory_usage" -gt 90 ]; then
    print_error "Memory usage is critical: ${memory_usage}%"
else
    print_status "Memory usage is normal: ${memory_usage}%"
fi

# Check .env file
print_info "Checking .env configuration..."
if [ -f ".env" ]; then
    if grep -q "CHANGE_ME" .env; then
        print_error ".env file contains placeholder values"
        exit 1
    else
        print_status ".env file is properly configured"
    fi
else
    print_error ".env file is missing"
    exit 1
fi

echo ""
print_status "All production health checks passed!"
echo ""
print_info "Production system is healthy and ready"
