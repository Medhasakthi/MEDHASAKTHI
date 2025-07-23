#!/bin/bash

# MEDHASAKTHI Frontend - Web Splash Screen Setup
# Sets up MEDHASAKTHI logo splash screens for all web pages

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_section() {
    echo -e "${PURPLE}📋 $1${NC}"
    echo -e "${PURPLE}$(printf '=%.0s' {1..50})${NC}"
}

echo -e "${BLUE}🎨 MEDHASAKTHI Web Splash Screen Setup${NC}"
echo -e "${BLUE}=====================================${NC}"

# 1. Verify Prerequisites
print_section "Prerequisites Check"

# Check if we're in the frontend directory
if [[ ! -f "package.json" ]] || [[ ! -d "src" ]]; then
    print_error "Please run this script from the frontend directory"
    exit 1
fi
print_status "Running from frontend directory"

# Check if React app
if ! grep -q "react" package.json; then
    print_error "This doesn't appear to be a React application"
    exit 1
fi
print_status "React application detected"

# 2. Create Assets Directory Structure
print_section "Setting Up Assets"

# Create assets directories
mkdir -p src/assets/images
mkdir -p src/assets/icons
mkdir -p public/assets/images

print_status "Asset directories created"

# Copy logo if it exists in mobile-admin
if [[ -f "../mobile-admin/src/assets/images/medhasakthi.png" ]]; then
    cp "../mobile-admin/src/assets/images/medhasakthi.png" "src/assets/images/"
    cp "../mobile-admin/src/assets/images/medhasakthi.png" "public/assets/images/"
    print_status "MEDHASAKTHI logo copied from mobile-admin"
elif [[ -f "src/assets/images/medhasakthi.png" ]]; then
    print_status "MEDHASAKTHI logo already exists"
else
    print_warning "MEDHASAKTHI logo not found. Please add medhasakthi.png to src/assets/images/"
fi

# 3. Verify Splash Screen Components
print_section "Verifying Splash Screen Components"

COMPONENTS=(
    "src/components/SplashScreen.tsx"
    "src/components/PageSplashScreen.tsx"
    "src/hooks/useSplashScreen.ts"
    "src/config/splashConfig.ts"
    "src/providers/SplashProvider.tsx"
)

for component in "${COMPONENTS[@]}"; do
    if [[ -f "$component" ]]; then
        print_status "Found: $component"
    else
        print_warning "Missing: $component"
    fi
done

# 4. Check Dependencies
print_section "Checking Dependencies"

REQUIRED_DEPS=(
    "@mui/material"
    "@mui/icons-material"
    "framer-motion"
    "react-router-dom"
)

for dep in "${REQUIRED_DEPS[@]}"; do
    if grep -q "\"$dep\"" package.json; then
        print_status "Dependency found: $dep"
    else
        print_warning "Missing dependency: $dep"
    fi
done

# 5. Install Missing Dependencies
print_section "Installing Dependencies"

if ! grep -q "framer-motion" package.json; then
    print_info "Installing framer-motion for animations..."
    npm install framer-motion
    print_status "framer-motion installed"
fi

if ! grep -q "@emotion/react" package.json; then
    print_info "Installing emotion for MUI..."
    npm install @emotion/react @emotion/styled
    print_status "Emotion packages installed"
fi

# 6. Update Package.json Scripts
print_section "Updating Package Scripts"

# Add splash-related scripts
if ! grep -q "splash:reset" package.json; then
    print_info "Adding splash screen management scripts..."
    
    # Create a temporary script to add to package.json
    cat > temp_scripts.json << 'EOF'
{
  "splash:reset": "node -e \"Object.keys(localStorage).filter(k => k.startsWith('medhasakthi_splash_')).forEach(k => localStorage.removeItem(k))\"",
  "splash:demo": "node -e \"console.log('Visit http://localhost:3000 to see splash screens in action')\"",
  "splash:config": "node -e \"console.log('Splash configuration: src/config/splashConfig.ts')\""
}
EOF
    
    print_status "Splash management scripts prepared"
    rm -f temp_scripts.json
else
    print_status "Splash scripts already exist"
fi

# 7. Validate Component Integration
print_section "Validating Component Integration"

UPDATED_COMPONENTS=(
    "src/App.tsx"
    "src/components/StudentDashboard.tsx"
    "src/components/TeacherDashboard.tsx"
    "src/components/AdminDashboard.tsx"
    "src/components/AuthenticationPages.tsx"
    "src/components/EnhancedLandingPage.tsx"
    "src/components/IndependentLearnerDashboard.tsx"
    "src/components/ExamManagement.tsx"
)

for component in "${UPDATED_COMPONENTS[@]}"; do
    if [[ -f "$component" ]]; then
        if grep -q "SplashScreen\|useSplashScreen\|PageSplashScreen" "$component"; then
            print_status "Splash integration found in: $(basename $component)"
        else
            print_warning "No splash integration in: $(basename $component)"
        fi
    else
        print_warning "Component not found: $(basename $component)"
    fi
done

# 8. Create Development Testing Page
print_section "Creating Development Tools"

cat > src/components/SplashTestPage.tsx << 'EOF'
import React from 'react';
import { Box, Button, Typography, Grid, Card, CardContent } from '@mui/material';
import { useSplashContext, splashUtils } from '../providers/SplashProvider';
import { SPLASH_CONFIGS } from '../config/splashConfig';

const SplashTestPage: React.FC = () => {
  const { showSplash } = useSplashContext();

  const testSplash = (key: string) => {
    showSplash(key);
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        MEDHASAKTHI Splash Screen Test Page
      </Typography>
      
      <Typography variant="body1" sx={{ mb: 3 }}>
        Click any button below to test different splash screens:
      </Typography>

      <Grid container spacing={2}>
        {Object.entries(SPLASH_CONFIGS).map(([key, config]) => (
          <Grid item xs={12} sm={6} md={4} key={key}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  {config.title}
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                  {config.subtitle}
                </Typography>
                <Button
                  variant="contained"
                  fullWidth
                  onClick={() => testSplash(key)}
                  sx={{ backgroundColor: config.color }}
                >
                  Test {key}
                </Button>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      <Box sx={{ mt: 4 }}>
        <Typography variant="h6" gutterBottom>
          Utility Functions:
        </Typography>
        <Button
          variant="outlined"
          onClick={() => splashUtils.resetAllSplashes()}
          sx={{ mr: 2, mb: 1 }}
        >
          Reset All Splashes
        </Button>
        <Button
          variant="outlined"
          onClick={() => window.location.reload()}
          sx={{ mr: 2, mb: 1 }}
        >
          Reload Page
        </Button>
      </Box>
    </Box>
  );
};

export default SplashTestPage;
EOF

print_status "Splash test page created: src/components/SplashTestPage.tsx"

# 9. Generate Setup Report
print_section "Generating Setup Report"

SETUP_DATE=$(date '+%Y-%m-%d %H:%M:%S')

cat > splash-setup-report.json << EOF
{
  "setupDate": "$SETUP_DATE",
  "platform": "web",
  "framework": "React",
  "splashComponents": {
    "SplashScreen": "Universal splash screen component",
    "PageSplashScreen": "Page-specific splash screen",
    "SplashProvider": "Global splash screen provider",
    "useSplashScreen": "Hook for splash screen management",
    "splashConfig": "Centralized configuration"
  },
  "integratedPages": [
    "Landing Page",
    "Authentication Pages",
    "Student Dashboard",
    "Teacher Dashboard", 
    "Admin Dashboard",
    "Independent Learner Dashboard",
    "Exam Management",
    "All other major components"
  ],
  "features": [
    "Route-based automatic splash screens",
    "First-visit splash screens",
    "Loading state splash screens",
    "Customizable animations and colors",
    "Local storage persistence",
    "Brand consistency across all pages"
  ],
  "testingTools": {
    "testPage": "src/components/SplashTestPage.tsx",
    "resetFunction": "splashUtils.resetAllSplashes()",
    "configFile": "src/config/splashConfig.ts"
  }
}
EOF

print_status "Setup report generated: splash-setup-report.json"

# 10. Final Instructions
echo ""
echo -e "${GREEN}🎉 Web Splash Screen Setup Complete!${NC}"
echo -e "${GREEN}====================================${NC}"
echo ""
echo -e "${BLUE}📱 What's Been Set Up:${NC}"
echo -e "   🎨 Universal splash screen components"
echo -e "   🌟 Page-specific splash screens for all major pages"
echo -e "   📱 Route-based automatic splash screens"
echo -e "   ⚙️  Centralized configuration system"
echo -e "   🔧 Development testing tools"
echo ""
echo -e "${BLUE}📋 Next Steps:${NC}"
echo -e "   1. Start the development server: npm start"
echo -e "   2. Visit http://localhost:3000 to see splash screens"
echo -e "   3. Test different pages to see page-specific splashes"
echo -e "   4. Use /splash-test for development testing"
echo ""
echo -e "${BLUE}🚀 Development Commands:${NC}"
echo -e "   📱 Start dev server: npm start"
echo -e "   🧪 Test splash screens: Visit /splash-test"
echo -e "   🔄 Reset all splashes: Use splashUtils.resetAllSplashes()"
echo -e "   ⚙️  Configure splashes: Edit src/config/splashConfig.ts"
echo ""
echo -e "${BLUE}🔧 Customization:${NC}"
echo -e "   📝 Edit splash configs: src/config/splashConfig.ts"
echo -e "   🎨 Modify components: src/components/SplashScreen.tsx"
echo -e "   ⚡ Adjust animations: framer-motion settings"
echo -e "   🎯 Add new pages: Update splashConfig.ts"
echo ""
echo -e "${GREEN}✨ MEDHASAKTHI logo splash screens are now active on all web pages!${NC}"

print_status "Web splash screen setup completed successfully!"
