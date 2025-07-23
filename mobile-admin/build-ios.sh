#!/bin/bash

# MEDHASAKTHI Mobile Admin - iOS Build Script
# Builds production-ready IPA for iOS

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

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

echo -e "${BLUE}🍎 MEDHASAKTHI Mobile Admin - iOS Build${NC}"
echo -e "${BLUE}======================================${NC}"

# Check if running on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    print_error "iOS builds can only be performed on macOS"
    exit 1
fi

# Check prerequisites
print_info "Checking prerequisites..."

# Check Node.js
if ! command -v node >/dev/null 2>&1; then
    print_error "Node.js not found. Please install Node.js 16+"
    exit 1
fi
print_status "Node.js found: $(node --version)"

# Check Xcode
if ! command -v xcodebuild >/dev/null 2>&1; then
    print_error "Xcode not found. Please install Xcode from App Store"
    exit 1
fi
print_status "Xcode found: $(xcodebuild -version | head -n 1)"

# Check CocoaPods
if ! command -v pod >/dev/null 2>&1; then
    print_error "CocoaPods not found. Install with: sudo gem install cocoapods"
    exit 1
fi
print_status "CocoaPods found: $(pod --version)"

# Install dependencies
print_info "Installing dependencies..."
npm install
print_status "Dependencies installed"

# Install iOS dependencies
print_info "Installing iOS dependencies..."
cd ios
pod install --repo-update
cd ..
print_status "iOS dependencies installed"

# Clean previous builds
print_info "Cleaning previous builds..."
npm run clean
cd ios
xcodebuild clean -workspace MEDHASAKTHIAdmin.xcworkspace -scheme MEDHASAKTHIAdmin
cd ..
print_status "Clean completed"

# Build for simulator (development)
print_info "Building for iOS Simulator..."
npx react-native run-ios --simulator="iPhone 14 Pro"
print_status "Simulator build completed"

# Build for device (if provisioning profile exists)
print_info "Checking for provisioning profiles..."
PROFILES_DIR="$HOME/Library/MobileDevice/Provisioning Profiles"
if [ -d "$PROFILES_DIR" ] && [ "$(ls -A $PROFILES_DIR)" ]; then
    print_status "Provisioning profiles found"
    
    print_info "Building for iOS device..."
    cd ios
    
    # Archive the project
    xcodebuild archive \
        -workspace MEDHASAKTHIAdmin.xcworkspace \
        -scheme MEDHASAKTHIAdmin \
        -configuration Release \
        -destination generic/platform=iOS \
        -archivePath MEDHASAKTHIAdmin.xcarchive
    
    # Export IPA (requires export options plist)
    if [ -f "ExportOptions.plist" ]; then
        print_info "Exporting IPA..."
        xcodebuild -exportArchive \
            -archivePath MEDHASAKTHIAdmin.xcarchive \
            -exportPath ./build \
            -exportOptionsPlist ExportOptions.plist
        print_status "IPA exported to ios/build/"
    else
        print_warning "ExportOptions.plist not found. Archive created but IPA not exported."
        print_info "Create ExportOptions.plist for IPA export"
    fi
    
    cd ..
else
    print_warning "No provisioning profiles found. Device build skipped."
    print_info "To build for device:"
    print_info "1. Register device in Apple Developer Portal"
    print_info "2. Create provisioning profile"
    print_info "3. Download and install profile"
fi

# Generate build info
BUILD_DATE=$(date '+%Y-%m-%d %H:%M:%S')
BUILD_COMMIT=$(git rev-parse --short HEAD 2>/dev/null || echo "unknown")

cat > build-info.json << EOF
{
  "platform": "ios",
  "buildDate": "$BUILD_DATE",
  "commit": "$BUILD_COMMIT",
  "version": "1.0.0",
  "buildType": "production",
  "artifacts": {
    "simulator": "ios/build/Build/Products/Debug-iphonesimulator/MEDHASAKTHIAdmin.app",
    "archive": "ios/MEDHASAKTHIAdmin.xcarchive",
    "ipa": "ios/build/MEDHASAKTHIAdmin.ipa"
  }
}
EOF

print_status "Build info generated: build-info.json"

echo ""
echo -e "${GREEN}🎉 iOS Build Completed Successfully!${NC}"
echo -e "${GREEN}===================================${NC}"
echo ""
echo -e "${BLUE}📱 Build Artifacts:${NC}"
echo -e "   📱 Simulator App: Available in iOS Simulator"
if [ -f "ios/MEDHASAKTHIAdmin.xcarchive" ]; then
    echo -e "   📦 Archive: ios/MEDHASAKTHIAdmin.xcarchive"
fi
if [ -f "ios/build/MEDHASAKTHIAdmin.ipa" ]; then
    echo -e "   📦 IPA: ios/build/MEDHASAKTHIAdmin.ipa"
fi
echo ""
echo -e "${BLUE}📋 Next Steps:${NC}"
echo -e "   1. Test the app in iOS Simulator"
echo -e "   2. Test on physical iOS devices"
echo -e "   3. Upload to App Store Connect for distribution"
echo -e "   4. Configure app signing for production release"
echo ""
echo -e "${GREEN}🚀 MEDHASAKTHI Mobile Admin is ready for iOS!${NC}"
