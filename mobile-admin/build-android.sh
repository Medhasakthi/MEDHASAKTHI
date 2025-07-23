#!/bin/bash

# MEDHASAKTHI Mobile Admin - Android Build Script
# Builds production-ready APK for Android

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

echo -e "${BLUE}🤖 MEDHASAKTHI Mobile Admin - Android Build${NC}"
echo -e "${BLUE}===========================================${NC}"

# Check prerequisites
print_info "Checking prerequisites..."

# Check Node.js
if ! command -v node >/dev/null 2>&1; then
    print_error "Node.js not found. Please install Node.js 16+"
    exit 1
fi
print_status "Node.js found: $(node --version)"

# Check npm
if ! command -v npm >/dev/null 2>&1; then
    print_error "npm not found"
    exit 1
fi
print_status "npm found: $(npm --version)"

# Check Java
if ! command -v java >/dev/null 2>&1; then
    print_error "Java not found. Please install JDK 11+"
    exit 1
fi
print_status "Java found: $(java --version | head -n 1)"

# Check Android SDK
if [ -z "$ANDROID_HOME" ]; then
    print_error "ANDROID_HOME not set. Please install Android SDK"
    exit 1
fi
print_status "Android SDK found: $ANDROID_HOME"

# Install dependencies
print_info "Installing dependencies..."
npm install
print_status "Dependencies installed"

# Clean previous builds
print_info "Cleaning previous builds..."
npm run clean
cd android
./gradlew clean
cd ..
print_status "Clean completed"

# Generate bundle
print_info "Generating React Native bundle..."
npx react-native bundle \
    --platform android \
    --dev false \
    --entry-file index.js \
    --bundle-output android/app/src/main/assets/index.android.bundle \
    --assets-dest android/app/src/main/res/
print_status "Bundle generated"

# Build APK
print_info "Building Android APK..."
cd android

# Build debug APK
print_info "Building debug APK..."
./gradlew assembleDebug
print_status "Debug APK built: android/app/build/outputs/apk/debug/app-debug.apk"

# Build release APK (if keystore exists)
if [ -f "app/my-upload-key.keystore" ]; then
    print_info "Building release APK..."
    ./gradlew assembleRelease
    print_status "Release APK built: android/app/build/outputs/apk/release/app-release.apk"
else
    print_warning "Release keystore not found. Only debug APK built."
    print_info "To build release APK:"
    print_info "1. Generate keystore: keytool -genkeypair -v -keystore my-upload-key.keystore -alias my-key-alias -keyalg RSA -keysize 2048 -validity 10000"
    print_info "2. Place keystore in android/app/"
    print_info "3. Configure gradle.properties with keystore details"
fi

cd ..

# Generate build info
BUILD_DATE=$(date '+%Y-%m-%d %H:%M:%S')
BUILD_COMMIT=$(git rev-parse --short HEAD 2>/dev/null || echo "unknown")

cat > build-info.json << EOF
{
  "platform": "android",
  "buildDate": "$BUILD_DATE",
  "commit": "$BUILD_COMMIT",
  "version": "1.0.0",
  "buildType": "production",
  "artifacts": {
    "debug": "android/app/build/outputs/apk/debug/app-debug.apk",
    "release": "android/app/build/outputs/apk/release/app-release.apk"
  }
}
EOF

print_status "Build info generated: build-info.json"

echo ""
echo -e "${GREEN}🎉 Android Build Completed Successfully!${NC}"
echo -e "${GREEN}=======================================${NC}"
echo ""
echo -e "${BLUE}📱 Build Artifacts:${NC}"
echo -e "   📦 Debug APK: android/app/build/outputs/apk/debug/app-debug.apk"
if [ -f "android/app/build/outputs/apk/release/app-release.apk" ]; then
    echo -e "   📦 Release APK: android/app/build/outputs/apk/release/app-release.apk"
fi
echo ""
echo -e "${BLUE}📋 Next Steps:${NC}"
echo -e "   1. Test the APK on Android devices"
echo -e "   2. Upload to Google Play Console for distribution"
echo -e "   3. Configure app signing for production release"
echo ""
echo -e "${GREEN}🚀 MEDHASAKTHI Mobile Admin is ready for Android!${NC}"
