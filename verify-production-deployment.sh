#!/bin/bash

# MEDHASAKTHI Production Deployment Verification Script
# This script verifies that the production deployment is working correctly

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

# Get domain from environment or use default
DOMAIN=${1:-"medhasakthi.com"}
BACKEND_URL="https://$DOMAIN/api"
FRONTEND_URL="https://$DOMAIN"

echo -e "${BLUE}🔍 MEDHASAKTHI Production Deployment Verification${NC}"
echo "=================================================="
echo "Domain: $DOMAIN"
echo "Backend URL: $BACKEND_URL"
echo "Frontend URL: $FRONTEND_URL"
echo ""

# Test 1: Backend Health Check
print_info "Test 1: Backend Health Check"
if curl -f -s "$BACKEND_URL/health" > /dev/null; then
    print_status "Backend health check passed"
    
    # Get health details
    health_response=$(curl -s "$BACKEND_URL/health")
    echo "   Response: $health_response"
else
    print_error "Backend health check failed"
    echo "   URL: $BACKEND_URL/health"
fi

# Test 2: Frontend Accessibility
print_info "Test 2: Frontend Accessibility"
if curl -f -s "$FRONTEND_URL" > /dev/null; then
    print_status "Frontend is accessible"
    
    # Check if it's serving the React app
    if curl -s "$FRONTEND_URL" | grep -q "MEDHASAKTHI"; then
        print_status "Frontend is serving MEDHASAKTHI application"
    else
        print_warning "Frontend accessible but may not be serving the correct application"
    fi
else
    print_error "Frontend accessibility check failed"
    echo "   URL: $FRONTEND_URL"
fi

# Test 3: API Documentation
print_info "Test 3: API Documentation"
if curl -f -s "$BACKEND_URL/docs" > /dev/null; then
    print_status "API documentation is accessible"
else
    print_warning "API documentation check failed (may be disabled in production)"
fi

# Test 4: Database Connection
print_info "Test 4: Database Connection"
db_response=$(curl -s "$BACKEND_URL/health" | grep -o '"database":"[^"]*"' | cut -d'"' -f4)
if [ "$db_response" = "connected" ]; then
    print_status "Database connection is healthy"
else
    print_warning "Database connection status unclear"
fi

# Test 5: Redis Connection
print_info "Test 5: Redis Connection"
redis_response=$(curl -s "$BACKEND_URL/health" | grep -o '"redis":"[^"]*"' | cut -d'"' -f4)
if [ "$redis_response" = "connected" ]; then
    print_status "Redis connection is healthy"
else
    print_warning "Redis connection status unclear"
fi

# Test 6: SSL Certificate
print_info "Test 6: SSL Certificate"
if echo | openssl s_client -servername "$DOMAIN" -connect "$DOMAIN:443" 2>/dev/null | openssl x509 -noout -dates > /dev/null 2>&1; then
    print_status "SSL certificate is valid"
    
    # Get certificate expiry
    expiry=$(echo | openssl s_client -servername "$DOMAIN" -connect "$DOMAIN:443" 2>/dev/null | openssl x509 -noout -enddate | cut -d= -f2)
    echo "   Expires: $expiry"
else
    print_warning "SSL certificate check failed or not configured"
fi

# Test 7: Response Time
print_info "Test 7: Response Time Analysis"
backend_time=$(curl -o /dev/null -s -w "%{time_total}" "$BACKEND_URL/health")
frontend_time=$(curl -o /dev/null -s -w "%{time_total}" "$FRONTEND_URL")

echo "   Backend response time: ${backend_time}s"
echo "   Frontend response time: ${frontend_time}s"

if (( $(echo "$backend_time < 2.0" | bc -l) )); then
    print_status "Backend response time is good"
else
    print_warning "Backend response time is slow (>${backend_time}s)"
fi

if (( $(echo "$frontend_time < 3.0" | bc -l) )); then
    print_status "Frontend response time is good"
else
    print_warning "Frontend response time is slow (>${frontend_time}s)"
fi

# Test 8: Docker Services Status (if running on server)
if command -v docker &> /dev/null; then
    print_info "Test 8: Docker Services Status"
    
    if docker-compose ps | grep -q "Up"; then
        print_status "Docker services are running"
        echo "   Services status:"
        docker-compose ps --format "table {{.Name}}\t{{.State}}\t{{.Ports}}"
    else
        print_error "Docker services are not running properly"
    fi
else
    print_info "Test 8: Skipped (not running on server)"
fi

# Test 9: Disk Space Check (if running on server)
if [ -d "/opt/medhasakthi" ]; then
    print_info "Test 9: Disk Space Check"
    
    disk_usage=$(df /opt/medhasakthi | awk 'NR==2 {print $5}' | sed 's/%//')
    echo "   Disk usage: ${disk_usage}%"
    
    if [ "$disk_usage" -lt 80 ]; then
        print_status "Disk space is sufficient"
    elif [ "$disk_usage" -lt 90 ]; then
        print_warning "Disk space is getting low (${disk_usage}%)"
    else
        print_error "Disk space is critically low (${disk_usage}%)"
    fi
else
    print_info "Test 9: Skipped (not running on server)"
fi

# Test 10: Log Analysis (if running on server)
if [ -d "/opt/medhasakthi" ]; then
    print_info "Test 10: Recent Error Analysis"
    
    cd /opt/medhasakthi
    error_count=$(docker-compose logs --since="1h" 2>/dev/null | grep -i error | wc -l)
    warning_count=$(docker-compose logs --since="1h" 2>/dev/null | grep -i warning | wc -l)
    
    echo "   Errors in last hour: $error_count"
    echo "   Warnings in last hour: $warning_count"
    
    if [ "$error_count" -eq 0 ]; then
        print_status "No errors in recent logs"
    elif [ "$error_count" -lt 5 ]; then
        print_warning "Few errors in recent logs ($error_count)"
    else
        print_error "Many errors in recent logs ($error_count)"
    fi
else
    print_info "Test 10: Skipped (not running on server)"
fi

# Summary
echo ""
echo "=================================================="
print_info "Deployment Verification Summary"
echo "=================================================="

# Count successful tests
total_tests=10
if command -v docker &> /dev/null; then
    server_tests=3
else
    server_tests=0
fi

echo "Domain: $DOMAIN"
echo "Timestamp: $(date)"
echo ""

print_info "Quick Access URLs:"
echo "   🌐 Website: $FRONTEND_URL"
echo "   📚 API Docs: $BACKEND_URL/docs"
echo "   🏥 Health Check: $BACKEND_URL/health"
echo ""

print_info "Recommendations:"
echo "   - Monitor response times regularly"
echo "   - Set up automated health checks"
echo "   - Configure log rotation"
echo "   - Schedule regular backups"
echo "   - Monitor SSL certificate expiry"
echo ""

if [ "$error_count" -gt 0 ] 2>/dev/null; then
    print_warning "Check application logs for recent errors"
fi

print_status "Verification completed!"
