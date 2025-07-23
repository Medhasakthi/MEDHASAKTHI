#!/bin/bash

# MEDHASAKTHI System Status Check Script
# Comprehensive health check and status monitoring

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
DOMAIN=${DOMAIN:-"localhost"}
API_URL="https://${DOMAIN}"
FRONTEND_URL="https://${DOMAIN}"

echo -e "${BLUE}🔍 MEDHASAKTHI System Status Check${NC}"
echo -e "${BLUE}=================================${NC}"
echo ""

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_section() {
    echo -e "${PURPLE}📋 $1${NC}"
    echo -e "${PURPLE}$(printf '=%.0s' {1..50})${NC}"
}

# Function to check HTTP status
check_http() {
    local url=$1
    local expected=${2:-200}
    local timeout=${3:-10}
    
    local status=$(curl -s -o /dev/null -w "%{http_code}" --max-time $timeout "$url" 2>/dev/null || echo "000")
    
    if [[ "$status" == "$expected" ]]; then
        return 0
    else
        return 1
    fi
}

# Function to check service health
check_service() {
    local service=$1
    local status=$(docker-compose ps -q $service 2>/dev/null)
    
    if [[ -n "$status" ]]; then
        local running=$(docker inspect --format='{{.State.Running}}' $status 2>/dev/null)
        if [[ "$running" == "true" ]]; then
            return 0
        fi
    fi
    return 1
}

# System Information
print_section "System Information"

echo -e "${CYAN}Hostname:${NC} $(hostname)"
echo -e "${CYAN}Uptime:${NC} $(uptime -p)"
echo -e "${CYAN}Load Average:${NC} $(uptime | awk -F'load average:' '{print $2}')"
echo -e "${CYAN}Memory Usage:${NC} $(free -h | awk 'NR==2{printf "%.1f%% (%s/%s)", $3*100/$2, $3, $2}')"
echo -e "${CYAN}Disk Usage:${NC} $(df -h / | awk 'NR==2{printf "%s (%s)", $5, $4}')"
echo ""

# Docker Status
print_section "Docker Services Status"

SERVICES=("postgres" "redis" "backend" "frontend" "nginx" "prometheus" "grafana")

for service in "${SERVICES[@]}"; do
    if check_service $service; then
        print_status "$service is running"
    else
        print_error "$service is not running"
    fi
done
echo ""

# Database Health
print_section "Database Health"

if check_service "postgres"; then
    # Check PostgreSQL connection
    if docker-compose exec -T postgres pg_isready -U medhasakthi_user -d medhasakthi >/dev/null 2>&1; then
        print_status "PostgreSQL is accepting connections"
        
        # Get database size
        DB_SIZE=$(docker-compose exec -T postgres psql -U medhasakthi_user -d medhasakthi -t -c "SELECT pg_size_pretty(pg_database_size('medhasakthi'));" 2>/dev/null | xargs)
        echo -e "${CYAN}Database Size:${NC} $DB_SIZE"
        
        # Get connection count
        CONNECTIONS=$(docker-compose exec -T postgres psql -U medhasakthi_user -d medhasakthi -t -c "SELECT count(*) FROM pg_stat_activity;" 2>/dev/null | xargs)
        echo -e "${CYAN}Active Connections:${NC} $CONNECTIONS"
    else
        print_error "PostgreSQL connection failed"
    fi
else
    print_error "PostgreSQL service not running"
fi

if check_service "redis"; then
    # Check Redis connection
    if docker-compose exec -T redis redis-cli ping >/dev/null 2>&1; then
        print_status "Redis is responding"
        
        # Get Redis memory usage
        REDIS_MEMORY=$(docker-compose exec -T redis redis-cli info memory | grep used_memory_human | cut -d: -f2 | tr -d '\r')
        echo -e "${CYAN}Redis Memory Usage:${NC} $REDIS_MEMORY"
    else
        print_error "Redis connection failed"
    fi
else
    print_error "Redis service not running"
fi
echo ""

# Application Health
print_section "Application Health"

# Backend API Health
if check_http "${API_URL}/api/health" 200 10; then
    print_status "Backend API is healthy"
    
    # Get API version
    API_VERSION=$(curl -s "${API_URL}/api/health" 2>/dev/null | grep -o '"version":"[^"]*"' | cut -d'"' -f4 || echo "unknown")
    echo -e "${CYAN}API Version:${NC} $API_VERSION"
else
    print_error "Backend API health check failed"
fi

# Frontend Health
if check_http "${FRONTEND_URL}/" 200 10; then
    print_status "Frontend is accessible"
else
    print_error "Frontend accessibility check failed"
fi

# API Documentation
if check_http "${API_URL}/api/docs" 200 10; then
    print_status "API documentation is accessible"
else
    print_warning "API documentation check failed"
fi
echo ""

# Security Status
print_section "Security Status"

# SSL Certificate Check
if command -v openssl >/dev/null 2>&1; then
    SSL_INFO=$(echo | openssl s_client -servername $DOMAIN -connect $DOMAIN:443 2>/dev/null | openssl x509 -noout -dates 2>/dev/null)
    if [[ $? -eq 0 ]]; then
        print_status "SSL certificate is valid"
        
        # Get certificate expiry
        EXPIRY=$(echo "$SSL_INFO" | grep notAfter | cut -d= -f2)
        echo -e "${CYAN}Certificate Expires:${NC} $EXPIRY"
    else
        print_warning "SSL certificate check failed"
    fi
fi

# Security Headers Check
SECURITY_HEADERS=("Strict-Transport-Security" "X-Content-Type-Options" "X-Frame-Options" "X-XSS-Protection")

for header in "${SECURITY_HEADERS[@]}"; do
    if curl -s -I "${FRONTEND_URL}/" | grep -i "$header" >/dev/null 2>&1; then
        print_status "$header header is present"
    else
        print_warning "$header header is missing"
    fi
done
echo ""

# Monitoring Status
print_section "Monitoring Status"

# Prometheus
if check_http "http://localhost:9090/-/healthy" 200 5; then
    print_status "Prometheus is healthy"
else
    print_warning "Prometheus health check failed"
fi

# Grafana
if check_http "http://localhost:3001/api/health" 200 5; then
    print_status "Grafana is healthy"
else
    print_warning "Grafana health check failed"
fi
echo ""

# Backup Status
print_section "Backup Status"

BACKUP_DIR="/app/backups"
if [[ -d "$BACKUP_DIR" ]]; then
    BACKUP_COUNT=$(find "$BACKUP_DIR" -name "*.gz.enc" -mtime -7 | wc -l)
    if [[ $BACKUP_COUNT -gt 0 ]]; then
        print_status "Recent backups found ($BACKUP_COUNT in last 7 days)"
        
        # Get latest backup info
        LATEST_BACKUP=$(find "$BACKUP_DIR" -name "*.gz.enc" -printf '%T@ %p\n' | sort -n | tail -1 | cut -d' ' -f2-)
        if [[ -n "$LATEST_BACKUP" ]]; then
            BACKUP_DATE=$(stat -c %y "$LATEST_BACKUP" | cut -d' ' -f1)
            BACKUP_SIZE=$(du -h "$LATEST_BACKUP" | cut -f1)
            echo -e "${CYAN}Latest Backup:${NC} $BACKUP_DATE ($BACKUP_SIZE)"
        fi
    else
        print_warning "No recent backups found"
    fi
else
    print_warning "Backup directory not found"
fi
echo ""

# Performance Metrics
print_section "Performance Metrics"

# Response Time Check
RESPONSE_TIME=$(curl -o /dev/null -s -w "%{time_total}" "${FRONTEND_URL}/" 2>/dev/null || echo "0")
if (( $(echo "$RESPONSE_TIME < 2.0" | bc -l) )); then
    print_status "Frontend response time: ${RESPONSE_TIME}s (Good)"
elif (( $(echo "$RESPONSE_TIME < 5.0" | bc -l) )); then
    print_warning "Frontend response time: ${RESPONSE_TIME}s (Acceptable)"
else
    print_error "Frontend response time: ${RESPONSE_TIME}s (Slow)"
fi

API_RESPONSE_TIME=$(curl -o /dev/null -s -w "%{time_total}" "${API_URL}/api/health" 2>/dev/null || echo "0")
if (( $(echo "$API_RESPONSE_TIME < 1.0" | bc -l) )); then
    print_status "API response time: ${API_RESPONSE_TIME}s (Good)"
elif (( $(echo "$API_RESPONSE_TIME < 3.0" | bc -l) )); then
    print_warning "API response time: ${API_RESPONSE_TIME}s (Acceptable)"
else
    print_error "API response time: ${API_RESPONSE_TIME}s (Slow)"
fi
echo ""

# Resource Usage
print_section "Resource Usage"

# Docker container stats
if command -v docker >/dev/null 2>&1; then
    echo -e "${CYAN}Container Resource Usage:${NC}"
    docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}" | head -10
fi
echo ""

# Log Analysis
print_section "Recent Log Analysis"

# Check for errors in backend logs
ERROR_COUNT=$(docker-compose logs --tail=100 backend 2>/dev/null | grep -i error | wc -l)
if [[ $ERROR_COUNT -eq 0 ]]; then
    print_status "No recent errors in backend logs"
else
    print_warning "$ERROR_COUNT errors found in recent backend logs"
fi

# Check for warnings
WARNING_COUNT=$(docker-compose logs --tail=100 backend 2>/dev/null | grep -i warning | wc -l)
if [[ $WARNING_COUNT -eq 0 ]]; then
    print_status "No recent warnings in backend logs"
else
    print_info "$WARNING_COUNT warnings found in recent backend logs"
fi
echo ""

# Summary
print_section "System Status Summary"

# Calculate overall health score
TOTAL_CHECKS=20
PASSED_CHECKS=0

# Count successful checks (simplified)
if check_service "postgres"; then ((PASSED_CHECKS++)); fi
if check_service "redis"; then ((PASSED_CHECKS++)); fi
if check_service "backend"; then ((PASSED_CHECKS++)); fi
if check_service "frontend"; then ((PASSED_CHECKS++)); fi
if check_http "${API_URL}/api/health" 200 10; then ((PASSED_CHECKS++)); fi
if check_http "${FRONTEND_URL}/" 200 10; then ((PASSED_CHECKS++)); fi

HEALTH_PERCENTAGE=$((PASSED_CHECKS * 100 / 6))

if [[ $HEALTH_PERCENTAGE -ge 90 ]]; then
    echo -e "${GREEN}🎉 System Status: EXCELLENT (${HEALTH_PERCENTAGE}%)${NC}"
elif [[ $HEALTH_PERCENTAGE -ge 75 ]]; then
    echo -e "${YELLOW}⚠️  System Status: GOOD (${HEALTH_PERCENTAGE}%)${NC}"
elif [[ $HEALTH_PERCENTAGE -ge 50 ]]; then
    echo -e "${YELLOW}⚠️  System Status: FAIR (${HEALTH_PERCENTAGE}%)${NC}"
else
    echo -e "${RED}❌ System Status: POOR (${HEALTH_PERCENTAGE}%)${NC}"
fi

echo ""
echo -e "${BLUE}📊 Quick Access URLs:${NC}"
echo -e "   🏠 Main Site: ${FRONTEND_URL}"
echo -e "   🔧 API Docs: ${API_URL}/api/docs"
echo -e "   📊 Grafana: http://localhost:3001"
echo -e "   🔍 Prometheus: http://localhost:9090"
echo ""
echo -e "${BLUE}📝 For detailed logs:${NC}"
echo -e "   Backend: docker-compose logs -f backend"
echo -e "   Frontend: docker-compose logs -f frontend"
echo -e "   Database: docker-compose logs -f postgres"
echo ""
echo -e "${GREEN}✅ Status check completed at $(date)${NC}"
