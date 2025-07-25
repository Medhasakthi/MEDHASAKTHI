#!/bin/bash

# MEDHASAKTHI Frontend Production Linting Script

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

echo -e "${BLUE}🔍 MEDHASAKTHI Frontend Production Linting${NC}"
echo "=============================================="

# Check if we're in the frontend directory
if [ ! -f "package.json" ]; then
    print_error "Not in frontend directory. Please run from frontend folder."
    exit 1
fi

print_info "Running ESLint checks..."

# Run ESLint
if npm run lint; then
    print_status "ESLint checks passed"
else
    print_error "ESLint checks failed"
    echo ""
    print_info "Attempting to auto-fix issues..."
    
    if npm run lint:fix; then
        print_status "Auto-fix completed. Re-running checks..."
        
        if npm run lint; then
            print_status "All ESLint issues resolved"
        else
            print_warning "Some ESLint issues require manual fixing"
        fi
    else
        print_error "Auto-fix failed. Manual intervention required"
        exit 1
    fi
fi

echo ""
print_info "Running Prettier formatting..."

# Run Prettier
if npm run format; then
    print_status "Code formatting completed"
else
    print_error "Prettier formatting failed"
    exit 1
fi

echo ""
print_info "Running TypeScript type checking..."

# Run TypeScript check
if npx tsc --noEmit; then
    print_status "TypeScript type checking passed"
else
    print_error "TypeScript type checking failed"
    exit 1
fi

echo ""
print_status "All linting checks passed! Code is production-ready."
echo ""
print_info "Summary:"
echo "  ✅ ESLint: Passed"
echo "  ✅ Prettier: Passed"
echo "  ✅ TypeScript: Passed"
echo ""
print_info "Ready for production build!"
