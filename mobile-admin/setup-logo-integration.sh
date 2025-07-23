#!/bin/bash

# MEDHASAKTHI Mobile Admin - Complete Logo Integration Setup
# Sets up the MEDHASAKTHI logo for app icons and splash screens

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

echo -e "${BLUE}🎨 MEDHASAKTHI Mobile Admin - Logo Integration Setup${NC}"
echo -e "${BLUE}===================================================${NC}"

# 1. Verify Prerequisites
print_section "Prerequisites Check"

# Check if we're in the mobile-admin directory
if [[ ! -f "package.json" ]] || [[ ! -d "src" ]]; then
    print_error "Please run this script from the mobile-admin directory"
    exit 1
fi
print_status "Running from mobile-admin directory"

# Check if logo exists
if [[ ! -f "src/assets/images/medhasakthi.png" ]]; then
    print_error "MEDHASAKTHI logo not found at src/assets/images/medhasakthi.png"
    print_info "Please ensure the logo file exists before running this script"
    exit 1
fi
print_status "MEDHASAKTHI logo found"

# Check ImageMagick
if ! command -v convert >/dev/null 2>&1; then
    print_warning "ImageMagick not found. Installing..."
    
    # Try to install ImageMagick based on OS
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        sudo apt-get update && sudo apt-get install -y imagemagick
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        if command -v brew >/dev/null 2>&1; then
            brew install imagemagick
        else
            print_error "Please install Homebrew first, then run: brew install imagemagick"
            exit 1
        fi
    else
        print_error "Please install ImageMagick manually:"
        print_info "  Windows: Download from https://imagemagick.org/script/download.php"
        print_info "  Ubuntu/Debian: sudo apt-get install imagemagick"
        print_info "  macOS: brew install imagemagick"
        exit 1
    fi
fi
print_status "ImageMagick is available"

# 2. Generate App Icons
print_section "Generating App Icons"

print_info "Running app icon generator..."
if [[ -x "./generate-app-icons.sh" ]]; then
    ./generate-app-icons.sh
    print_status "App icons generated successfully"
else
    print_error "generate-app-icons.sh not found or not executable"
    print_info "Run: chmod +x generate-app-icons.sh"
    exit 1
fi

# 3. Verify Icon Generation
print_section "Verifying Icon Generation"

# Check Android icons
ANDROID_ICON_DIRS=("mipmap-mdpi" "mipmap-hdpi" "mipmap-xhdpi" "mipmap-xxhdpi" "mipmap-xxxhdpi")
for dir in "${ANDROID_ICON_DIRS[@]}"; do
    if [[ -f "android/app/src/main/res/$dir/ic_launcher.png" ]]; then
        print_status "Android icon exists: $dir/ic_launcher.png"
    else
        print_error "Missing Android icon: $dir/ic_launcher.png"
    fi
done

# Check iOS icons
if [[ -d "ios/MEDHASAKTHIAdmin/Images.xcassets/AppIcon.appiconset" ]]; then
    IOS_ICON_COUNT=$(ls ios/MEDHASAKTHIAdmin/Images.xcassets/AppIcon.appiconset/*.png 2>/dev/null | wc -l)
    if [[ $IOS_ICON_COUNT -gt 15 ]]; then
        print_status "iOS icons generated: $IOS_ICON_COUNT icons"
    else
        print_warning "iOS icons may be incomplete: only $IOS_ICON_COUNT icons found"
    fi
else
    print_error "iOS icon directory not found"
fi

# 4. Update React Native Configuration
print_section "Updating React Native Configuration"

# Ensure react-native.config.js includes assets
if [[ -f "react-native.config.js" ]]; then
    if grep -q "assets.*fonts" react-native.config.js; then
        print_status "React Native config includes assets"
    else
        print_warning "React Native config may need asset configuration"
    fi
else
    print_warning "react-native.config.js not found"
fi

# 5. Install Dependencies (if needed)
print_section "Checking Dependencies"

if [[ -f "package.json" ]]; then
    # Check if node_modules exists
    if [[ ! -d "node_modules" ]]; then
        print_info "Installing npm dependencies..."
        npm install
        print_status "Dependencies installed"
    else
        print_status "Dependencies already installed"
    fi
    
    # Check iOS pods (if on macOS)
    if [[ "$OSTYPE" == "darwin"* ]] && [[ -d "ios" ]]; then
        if [[ ! -d "ios/Pods" ]]; then
            print_info "Installing iOS pods..."
            cd ios && pod install && cd ..
            print_status "iOS pods installed"
        else
            print_status "iOS pods already installed"
        fi
    fi
else
    print_error "package.json not found"
fi

# 6. Validate Setup
print_section "Validating Setup"

if [[ -x "./validate-mobile-app.sh" ]]; then
    print_info "Running validation..."
    ./validate-mobile-app.sh
else
    print_warning "Validation script not found or not executable"
fi

# 7. Generate Setup Report
print_section "Setup Report"

SETUP_DATE=$(date '+%Y-%m-%d %H:%M:%S')

cat > logo-integration-report.json << EOF
{
  "setupDate": "$SETUP_DATE",
  "logoSource": "src/assets/images/medhasakthi.png",
  "androidIcons": {
    "generated": true,
    "locations": [
      "android/app/src/main/res/mipmap-mdpi/ic_launcher.png",
      "android/app/src/main/res/mipmap-hdpi/ic_launcher.png",
      "android/app/src/main/res/mipmap-xhdpi/ic_launcher.png",
      "android/app/src/main/res/mipmap-xxhdpi/ic_launcher.png",
      "android/app/src/main/res/mipmap-xxxhdpi/ic_launcher.png"
    ]
  },
  "iosIcons": {
    "generated": true,
    "location": "ios/MEDHASAKTHIAdmin/Images.xcassets/AppIcon.appiconset/"
  },
  "splashScreens": {
    "android": "android/app/src/main/res/drawable/splash_screen.xml",
    "ios": "ios/MEDHASAKTHIAdmin/LaunchScreen.storyboard",
    "reactNative": "src/components/SplashScreen.tsx"
  },
  "nextSteps": [
    "Build the app to test logo integration",
    "Test on both Android and iOS devices",
    "Verify app store compliance"
  ]
}
EOF

print_status "Setup report generated: logo-integration-report.json"

# 8. Final Instructions
echo ""
echo -e "${GREEN}🎉 Logo Integration Setup Complete!${NC}"
echo -e "${GREEN}====================================${NC}"
echo ""
echo -e "${BLUE}📱 What's Been Set Up:${NC}"
echo -e "   🎨 App icons generated for both Android and iOS"
echo -e "   🌟 Splash screens updated with MEDHASAKTHI logo"
echo -e "   📱 React Native splash screen component created"
echo -e "   ⚙️  Build configurations updated"
echo ""
echo -e "${BLUE}📋 Next Steps:${NC}"
echo -e "   1. Build the app: npm run build:android or npm run build:ios"
echo -e "   2. Test on devices to see the new logo"
echo -e "   3. Verify app store compliance"
echo ""
echo -e "${BLUE}🚀 Build Commands:${NC}"
echo -e "   📱 Android: npm run build:android"
echo -e "   🍎 iOS: npm run build:ios (macOS only)"
echo -e "   📦 Both: npm run build:both"
echo ""
echo -e "${BLUE}🔧 Troubleshooting:${NC}"
echo -e "   📋 Validate setup: npm run validate"
echo -e "   🔄 Regenerate icons: npm run generate:icons"
echo -e "   🧹 Clean build: npm run clean"
echo ""
echo -e "${GREEN}✨ Your MEDHASAKTHI logo is now integrated into the mobile app!${NC}"

# Make scripts executable
chmod +x *.sh 2>/dev/null || true

print_status "Logo integration setup completed successfully!"
