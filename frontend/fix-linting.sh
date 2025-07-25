#!/bin/bash

# MEDHASAKTHI Frontend Linting Auto-Fix Script

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

echo -e "${BLUE}🔧 MEDHASAKTHI Frontend Auto-Fix Linting Issues${NC}"
echo "=================================================="

# Check if we're in the frontend directory
if [ ! -f "package.json" ]; then
    print_error "Not in frontend directory. Please run from frontend folder."
    exit 1
fi

print_info "Step 1: Running ESLint auto-fix..."
npm run lint:fix || true

print_info "Step 2: Running Prettier formatting..."
npm run format || true

print_info "Step 3: Fixing common console statements..."
# Remove console.log statements
find src -name "*.tsx" -o -name "*.ts" | xargs sed -i 's/console\.log.*;//g' 2>/dev/null || true
find src -name "*.tsx" -o -name "*.ts" | xargs sed -i 's/console\.error.*;//g' 2>/dev/null || true
find src -name "*.tsx" -o -name "*.ts" | xargs sed -i 's/console\.warn.*;//g' 2>/dev/null || true

print_info "Step 4: Adding curly braces to if statements..."
# This is a basic fix - manual review may be needed
find src -name "*.tsx" -o -name "*.ts" | xargs sed -i 's/if (\(.*\)) return \(.*\);/if (\1) {\n    return \2;\n  }/g' 2>/dev/null || true

print_info "Step 5: Running final linting check..."
if npm run lint; then
    print_status "All linting issues fixed!"
else
    print_warning "Some issues may require manual fixing"
    print_info "Running type check..."
    npm run type-check || print_warning "TypeScript issues found - may need manual fixing"
fi

print_info "Auto-fix complete. Please review changes and commit."
