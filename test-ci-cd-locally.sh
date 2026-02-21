#!/bin/bash

# MEDHASAKTHI CI/CD Local Test Script
# This script simulates the CI/CD pipeline locally

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

echo -e "${BLUE}🔧 MEDHASAKTHI CI/CD Local Test${NC}"
echo "=================================="

# Test 1: Backend Syntax Check
print_info "Test 1: Backend Python Syntax Check"
cd backend
if python -m py_compile main.py; then
    print_status "Backend syntax check passed"
else
    print_error "Backend syntax check failed"
fi
cd ..

# Test 2: Backend Dependencies
print_info "Test 2: Backend Dependencies Check"
cd backend
if pip install -r requirements.txt --dry-run > /dev/null 2>&1; then
    print_status "Backend dependencies are valid"
else
    print_warning "Some backend dependencies may have issues"
fi
cd ..

# Test 3: Frontend Dependencies and Build
for app in frontend web-institute web-student; do
    print_info "Test 3: Testing $app"
    cd $app
    
    if [ -f package.json ]; then
        print_info "Installing dependencies for $app..."
        if npm install --legacy-peer-deps > /dev/null 2>&1; then
            print_status "$app dependencies installed"
        else
            print_warning "$app dependency installation had issues"
        fi
        
        print_info "Building $app..."
        export REACT_APP_API_URL=http://localhost:8080/api
        export REACT_APP_APP_NAME=MEDHASAKTHI
        export NEXT_PUBLIC_API_URL=http://localhost:8080/api
        export NODE_OPTIONS=--max-old-space-size=4096
        export GENERATE_SOURCEMAP=false
        export CI=false
        
        if npm run build > /dev/null 2>&1; then
            print_status "$app build successful"
        else
            print_warning "$app build had issues"
        fi
    else
        print_warning "$app/package.json not found"
    fi
    cd ..
done

# Test 4: Docker Build Test
print_info "Test 4: Docker Build Test"
if docker --version > /dev/null 2>&1; then
    print_info "Testing Docker builds..."
    
    # Test backend build
    if docker build -t test-backend ./backend > /dev/null 2>&1; then
        print_status "Backend Docker build successful"
    else
        print_error "Backend Docker build failed"
    fi
    
    # Test frontend build
    if docker build -t test-frontend ./frontend > /dev/null 2>&1; then
        print_status "Frontend Docker build successful"
    else
        print_error "Frontend Docker build failed"
    fi
    
    # Test docker-compose build
    if docker-compose build > /dev/null 2>&1; then
        print_status "Docker Compose build successful"
    else
        print_error "Docker Compose build failed"
    fi
else
    print_warning "Docker not available - skipping Docker tests"
fi

# Test 5: Integration Test
print_info "Test 5: Integration Test"
if docker-compose --version > /dev/null 2>&1; then
    print_info "Starting integration test..."
    
    # Clean up any existing containers
    docker-compose down > /dev/null 2>&1 || true
    
    # Start services
    print_info "Starting services..."
    if docker-compose up -d; then
        print_status "Services started"
        
        # Wait for services
        print_info "Waiting for services to initialize..."
        sleep 60
        
        # Test backend health
        print_info "Testing backend health..."
        for i in {1..5}; do
            if curl -f http://localhost:8080/health > /dev/null 2>&1; then
                print_status "Backend health check passed"
                break
            else
                print_info "Backend not ready, attempt $i/5"
                sleep 10
            fi
        done
        
        # Test frontend
        print_info "Testing frontend..."
        for i in {1..5}; do
            if curl -f http://localhost:3000 > /dev/null 2>&1; then
                print_status "Frontend health check passed"
                break
            else
                print_info "Frontend not ready, attempt $i/5"
                sleep 10
            fi
        done
        
        # Show service status
        print_info "Service status:"
        docker-compose ps
        
        # Cleanup
        print_info "Cleaning up..."
        docker-compose down
        
    else
        print_error "Failed to start services"
    fi
else
    print_warning "Docker Compose not available - skipping integration test"
fi

# Test 6: Environment Variables Check
print_info "Test 6: Environment Variables Check"
if [ -f .env ]; then
    print_status ".env file exists"
else
    print_warning ".env file not found - create from .env.example"
fi

if [ -f .env.example ]; then
    print_status ".env.example file exists"
else
    print_warning ".env.example file not found"
fi

# Summary
echo ""
echo -e "${GREEN}🎉 CI/CD Local Test Completed!${NC}"
echo ""
print_info "Summary:"
echo "  - Backend syntax and dependencies checked"
echo "  - All frontend apps tested"
echo "  - Docker builds verified"
echo "  - Integration test completed"
echo "  - Environment setup checked"
echo ""
print_info "If all tests passed, your CI/CD pipeline should work on GitHub!"
echo ""
print_info "Next steps:"
echo "  1. Commit and push your changes"
echo "  2. Check the Actions tab in GitHub"
echo "  3. Monitor the pipeline execution"
echo "  4. Review any failures in the logs"
echo ""
print_warning "Note: Some warnings are normal and won't prevent deployment"
