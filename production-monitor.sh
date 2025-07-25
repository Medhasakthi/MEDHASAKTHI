#!/bin/bash

# MEDHASAKTHI Production Monitoring Script

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_header() {
    echo -e "${BLUE}📊 $1${NC}"
    echo "================================"
}

print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Main monitoring function
monitor_production() {
    clear
    echo -e "${BLUE}🚀 MEDHASAKTHI Production Monitor${NC}"
    echo "=================================="
    echo "$(date)"
    echo ""

    # Container Status
    print_header "Container Status"
    docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    echo ""

    # Resource Usage
    print_header "Resource Usage"
    docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}\t{{.NetIO}}\t{{.BlockIO}}"
    echo ""

    # System Resources
    print_header "System Resources"
    echo "CPU Usage:"
    top -bn1 | grep "Cpu(s)" | awk '{print $2 $3}' | sed 's/%us,/ User,/' | sed 's/%sy/ System/'
    
    echo ""
    echo "Memory Usage:"
    free -h
    
    echo ""
    echo "Disk Usage:"
    df -h /
    
    echo ""

    # Application Health
    print_header "Application Health"
    
    # Backend API
    if curl -f -s http://localhost:8000/health >/dev/null; then
        print_status "Backend API: Healthy"
    else
        print_error "Backend API: Unhealthy"
    fi
    
    # Frontend
    if curl -f -s http://localhost:3000 >/dev/null; then
        print_status "Frontend: Healthy"
    else
        print_warning "Frontend: Check required"
    fi
    
    # Database
    if docker exec medhasakthi-postgres pg_isready -U admin -d medhasakthi >/dev/null 2>&1; then
        print_status "Database: Connected"
    else
        print_error "Database: Connection failed"
    fi
    
    # Redis
    if docker exec medhasakthi-redis redis-cli ping >/dev/null 2>&1; then
        print_status "Redis: Connected"
    else
        print_error "Redis: Connection failed"
    fi
    
    echo ""

    # Recent Logs
    print_header "Recent Backend Logs (Last 10 lines)"
    docker logs medhasakthi-backend --tail 10
    
    echo ""
    print_header "Recent Frontend Logs (Last 5 lines)"
    docker logs medhasakthi-frontend --tail 5
    
    echo ""
    echo "Press Ctrl+C to exit, or wait 30 seconds for refresh..."
}

# Continuous monitoring
while true; do
    monitor_production
    sleep 30
done
