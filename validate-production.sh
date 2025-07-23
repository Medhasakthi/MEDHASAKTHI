#!/bin/bash

# MEDHASAKTHI Production Validation Script
# Comprehensive validation before deployment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

# Counters
PASSED=0
WARNINGS=0
ERRORS=0

print_status() {
    echo -e "${GREEN}✅ $1${NC}"
    ((PASSED++))
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
    ((WARNINGS++))
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
    ((ERRORS++))
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_section() {
    echo -e "${PURPLE}📋 $1${NC}"
    echo -e "${PURPLE}$(printf '=%.0s' {1..50})${NC}"
}

echo -e "${BLUE}🔍 MEDHASAKTHI Production Validation${NC}"
echo -e "${BLUE}=====================================${NC}"

# 1. Environment Validation
print_section "Environment Validation"

# Check Python version
if command -v python3 >/dev/null 2>&1; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    if [[ "$PYTHON_VERSION" > "3.8" ]]; then
        print_status "Python version: $PYTHON_VERSION"
    else
        print_error "Python version too old: $PYTHON_VERSION (requires 3.8+)"
    fi
else
    print_error "Python 3 not found"
fi

# Check Node.js version
if command -v node >/dev/null 2>&1; then
    NODE_VERSION=$(node --version)
    print_status "Node.js version: $NODE_VERSION"
else
    print_warning "Node.js not found (required for frontend)"
fi

# Check Docker
if command -v docker >/dev/null 2>&1; then
    DOCKER_VERSION=$(docker --version | cut -d' ' -f3 | cut -d',' -f1)
    print_status "Docker version: $DOCKER_VERSION"
else
    print_warning "Docker not found (required for containerized deployment)"
fi

# Check Docker Compose
if command -v docker-compose >/dev/null 2>&1; then
    COMPOSE_VERSION=$(docker-compose --version | cut -d' ' -f3 | cut -d',' -f1)
    print_status "Docker Compose version: $COMPOSE_VERSION"
else
    print_warning "Docker Compose not found"
fi

# 2. Backend Validation
print_section "Backend Validation"

cd backend

# Check requirements.txt
if [[ -f "requirements.txt" ]]; then
    print_status "requirements.txt exists"
    
    # Check critical dependencies
    CRITICAL_DEPS=("fastapi" "sqlalchemy" "alembic" "redis" "aiohttp")
    for dep in "${CRITICAL_DEPS[@]}"; do
        if grep -q "$dep" requirements.txt; then
            print_status "Dependency found: $dep"
        else
            print_error "Missing critical dependency: $dep"
        fi
    done
else
    print_error "requirements.txt not found"
fi

# Check main.py
if [[ -f "main.py" ]]; then
    print_status "main.py exists"
else
    print_error "main.py not found"
fi

# Check app structure
REQUIRED_DIRS=("app/models" "app/services" "app/api" "app/core")
for dir in "${REQUIRED_DIRS[@]}"; do
    if [[ -d "$dir" ]]; then
        print_status "Directory exists: $dir"
    else
        print_error "Missing directory: $dir"
    fi
done

# Check critical files
CRITICAL_FILES=(
    "app/core/auth.py"
    "app/core/config.py"
    "app/core/database.py"
    "app/models/server.py"
    "app/models/user.py"
    "app/services/load_balancer_service.py"
    "app/api/v1/endpoints/load_balancer.py"
)

for file in "${CRITICAL_FILES[@]}"; do
    if [[ -f "$file" ]]; then
        print_status "Critical file exists: $file"
    else
        print_error "Missing critical file: $file"
    fi
done

# Run Python validation
print_info "Running Python validation..."
if python3 production_validation.py; then
    print_status "Python validation passed"
else
    print_error "Python validation failed"
fi

cd ..

# 3. Frontend Validation
print_section "Frontend Validation"

if [[ -d "frontend" ]]; then
    cd frontend
    
    # Check package.json
    if [[ -f "package.json" ]]; then
        print_status "package.json exists"
        
        # Check critical dependencies
        CRITICAL_DEPS=("react" "@mui/material" "framer-motion" "recharts")
        for dep in "${CRITICAL_DEPS[@]}"; do
            if grep -q "\"$dep\"" package.json; then
                print_status "Frontend dependency found: $dep"
            else
                print_error "Missing frontend dependency: $dep"
            fi
        done
    else
        print_error "Frontend package.json not found"
    fi
    
    # Check src structure
    if [[ -d "src/components" ]]; then
        print_status "Frontend components directory exists"
        
        # Check critical components
        CRITICAL_COMPONENTS=(
            "LoadBalancerManagement.tsx"
            "LoadBalancerDashboard.tsx"
            "AdminDashboard.tsx"
        )
        
        for component in "${CRITICAL_COMPONENTS[@]}"; do
            if [[ -f "src/components/$component" ]]; then
                print_status "Component exists: $component"
            else
                print_error "Missing component: $component"
            fi
        done
    else
        print_error "Frontend components directory not found"
    fi
    
    cd ..
else
    print_warning "Frontend directory not found"
fi

# 4. Configuration Validation
print_section "Configuration Validation"

# Check environment files
if [[ -f ".env.example" ]]; then
    print_status ".env.example exists"
else
    print_warning ".env.example not found"
fi

# Check Docker configurations
DOCKER_FILES=("docker-compose.yml" "docker-compose.production.yml" "docker-compose.loadbalanced.yml")
for file in "${DOCKER_FILES[@]}"; do
    if [[ -f "$file" ]]; then
        print_status "Docker config exists: $file"
    else
        print_warning "Docker config missing: $file"
    fi
done

# Check deployment scripts
DEPLOY_SCRIPTS=("deploy.sh" "deploy-aws.sh" "deploy-digitalocean.sh" "deploy-with-loadbalancer.sh")
for script in "${DEPLOY_SCRIPTS[@]}"; do
    if [[ -f "$script" ]]; then
        print_status "Deployment script exists: $script"
        
        # Check if executable
        if [[ -x "$script" ]]; then
            print_status "Script is executable: $script"
        else
            print_warning "Script not executable: $script"
        fi
    else
        print_warning "Deployment script missing: $script"
    fi
done

# 5. Database Migration Validation
print_section "Database Migration Validation"

if [[ -d "backend/alembic/versions" ]]; then
    print_status "Alembic versions directory exists"
    
    MIGRATION_COUNT=$(ls backend/alembic/versions/*.py 2>/dev/null | wc -l)
    if [[ $MIGRATION_COUNT -gt 0 ]]; then
        print_status "Found $MIGRATION_COUNT database migrations"
        
        # Check for load balancer migration
        if ls backend/alembic/versions/*load_balancer*.py >/dev/null 2>&1; then
            print_status "Load balancer migration exists"
        else
            print_error "Load balancer migration not found"
        fi
    else
        print_error "No database migrations found"
    fi
else
    print_error "Alembic versions directory not found"
fi

# 6. Security Validation
print_section "Security Validation"

# Check for default secrets
if [[ -f "backend/.env.example" ]]; then
    if grep -q "your-secret-key-here" backend/.env.example; then
        print_status "Default secrets found in .env.example (good)"
    fi
fi

if [[ -f ".env" ]]; then
    if grep -q "your-secret-key-here" .env; then
        print_error "Default secrets in .env file - SECURITY RISK!"
    else
        print_status "Custom secrets in .env file"
    fi
fi

# Check SSL configuration
if [[ -f "nginx-loadbalancer.conf" ]]; then
    if grep -q "ssl_certificate" nginx-loadbalancer.conf; then
        print_status "SSL configuration found in nginx config"
    else
        print_warning "SSL configuration not found in nginx config"
    fi
fi

# 7. Generate Final Report
print_section "Validation Summary"

TOTAL=$((PASSED + WARNINGS + ERRORS))
if [[ $TOTAL -gt 0 ]]; then
    SUCCESS_RATE=$(( (PASSED * 100) / TOTAL ))
else
    SUCCESS_RATE=0
fi

echo -e "${BLUE}📊 Validation Results:${NC}"
echo -e "   ✅ Passed: $PASSED"
echo -e "   ⚠️  Warnings: $WARNINGS"
echo -e "   ❌ Errors: $ERRORS"
echo -e "   📈 Success Rate: $SUCCESS_RATE%"

echo ""
echo -e "${BLUE}🎯 Production Readiness Assessment:${NC}"

if [[ $ERRORS -eq 0 ]]; then
    if [[ $WARNINGS -eq 0 ]]; then
        echo -e "${GREEN}🟢 FULLY READY${NC} - No issues found! Ready for production deployment."
        exit 0
    elif [[ $WARNINGS -le 3 ]]; then
        echo -e "${YELLOW}🟡 MOSTLY READY${NC} - Minor warnings only. Safe to deploy with monitoring."
        exit 0
    else
        echo -e "${YELLOW}🟠 READY WITH CAUTION${NC} - Multiple warnings. Review before deployment."
        exit 1
    fi
else
    echo -e "${RED}🔴 NOT READY${NC} - Critical errors must be fixed before deployment."
    echo ""
    echo -e "${RED}❌ Fix the following errors before deploying:${NC}"
    echo "   - Check missing files and dependencies"
    echo "   - Ensure all critical components are present"
    echo "   - Verify configuration files"
    echo "   - Run backend validation script"
    exit 2
fi
