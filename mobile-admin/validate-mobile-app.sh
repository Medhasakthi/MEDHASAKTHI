#!/bin/bash

# MEDHASAKTHI Mobile Admin - Comprehensive Validation Script
# Validates both Android and iOS platform files and configurations

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

echo -e "${BLUE}📱 MEDHASAKTHI Mobile Admin - Platform Validation${NC}"
echo -e "${BLUE}================================================${NC}"

# 1. React Native Core Validation
print_section "React Native Core Validation"

# Check package.json
if [[ -f "package.json" ]]; then
    print_status "package.json exists"
    
    # Check React Native version
    if grep -q "react-native" package.json; then
        RN_VERSION=$(grep "react-native" package.json | head -n 1 | cut -d'"' -f4)
        print_status "React Native version: $RN_VERSION"
    else
        print_error "React Native not found in dependencies"
    fi
    
    # Check critical dependencies
    CRITICAL_DEPS=("react" "react-native" "@react-navigation/native" "react-native-vector-icons")
    for dep in "${CRITICAL_DEPS[@]}"; do
        if grep -q "\"$dep\"" package.json; then
            print_status "Dependency found: $dep"
        else
            print_warning "Missing dependency: $dep"
        fi
    done
else
    print_error "package.json not found"
fi

# Check core files
CORE_FILES=("index.js" "App.tsx" "app.json" "metro.config.js" "react-native.config.js")
for file in "${CORE_FILES[@]}"; do
    if [[ -f "$file" ]]; then
        print_status "Core file exists: $file"
    else
        print_error "Missing core file: $file"
    fi
done

# 2. Android Platform Validation
print_section "Android Platform Validation"

if [[ -d "android" ]]; then
    print_status "Android directory exists"
    
    # Check Android build files
    ANDROID_FILES=(
        "android/build.gradle"
        "android/settings.gradle"
        "android/gradle.properties"
        "android/app/build.gradle"
        "android/app/src/main/AndroidManifest.xml"
        "android/app/src/main/java/com/medhasakthi/admin/MainActivity.java"
        "android/app/src/main/java/com/medhasakthi/admin/MainApplication.java"
    )
    
    for file in "${ANDROID_FILES[@]}"; do
        if [[ -f "$file" ]]; then
            print_status "Android file exists: $(basename $file)"
        else
            print_error "Missing Android file: $file"
        fi
    done
    
    # Check Android resources
    ANDROID_RESOURCES=(
        "android/app/src/main/res/values/strings.xml"
        "android/app/src/main/res/values/styles.xml"
        "android/app/src/main/res/values/colors.xml"
    )
    
    for resource in "${ANDROID_RESOURCES[@]}"; do
        if [[ -f "$resource" ]]; then
            print_status "Android resource exists: $(basename $resource)"
        else
            print_error "Missing Android resource: $resource"
        fi
    done
    
    # Check package name consistency
    if [[ -f "android/app/src/main/AndroidManifest.xml" ]]; then
        if grep -q "com.medhasakthi.admin" android/app/src/main/AndroidManifest.xml; then
            print_status "Android package name is consistent"
        else
            print_warning "Android package name may be inconsistent"
        fi
    fi
    
else
    print_error "Android directory not found"
fi

# 3. iOS Platform Validation
print_section "iOS Platform Validation"

if [[ -d "ios" ]]; then
    print_status "iOS directory exists"
    
    # Check iOS build files
    IOS_FILES=(
        "ios/Podfile"
        "ios/MEDHASAKTHIAdmin/Info.plist"
        "ios/MEDHASAKTHIAdmin/AppDelegate.h"
        "ios/MEDHASAKTHIAdmin/AppDelegate.mm"
        "ios/MEDHASAKTHIAdmin/LaunchScreen.storyboard"
    )
    
    for file in "${IOS_FILES[@]}"; do
        if [[ -f "$file" ]]; then
            print_status "iOS file exists: $(basename $file)"
        else
            print_error "Missing iOS file: $file"
        fi
    done
    
    # Check bundle identifier consistency
    if [[ -f "ios/MEDHASAKTHIAdmin/Info.plist" ]]; then
        if grep -q "MEDHASAKTHIAdmin" ios/MEDHASAKTHIAdmin/Info.plist; then
            print_status "iOS bundle identifier is consistent"
        else
            print_warning "iOS bundle identifier may be inconsistent"
        fi
    fi
    
    # Check if Podfile has required dependencies
    if [[ -f "ios/Podfile" ]]; then
        if grep -q "react-native" ios/Podfile; then
            print_status "Podfile has React Native configuration"
        else
            print_warning "Podfile may be missing React Native configuration"
        fi
    fi
    
else
    print_error "iOS directory not found"
fi

# 4. Build Scripts Validation
print_section "Build Scripts Validation"

BUILD_SCRIPTS=("build-android.sh" "build-ios.sh")
for script in "${BUILD_SCRIPTS[@]}"; do
    if [[ -f "$script" ]]; then
        print_status "Build script exists: $script"
        
        # Check if executable
        if [[ -x "$script" ]]; then
            print_status "Script is executable: $script"
        else
            print_warning "Script not executable: $script (run: chmod +x $script)"
        fi
    else
        print_error "Missing build script: $script"
    fi
done

# Check package.json scripts
if [[ -f "package.json" ]]; then
    REQUIRED_SCRIPTS=("android" "ios" "build:android" "build:ios" "start")
    for script in "${REQUIRED_SCRIPTS[@]}"; do
        if grep -q "\"$script\":" package.json; then
            print_status "NPM script exists: $script"
        else
            print_error "Missing NPM script: $script"
        fi
    done
fi

# 5. Source Code Validation
print_section "Source Code Validation"

if [[ -d "src" ]]; then
    print_status "Source directory exists"
    
    # Check main source files
    SRC_FILES=("src/App.tsx" "src/navigation" "src/screens" "src/components")
    for item in "${SRC_FILES[@]}"; do
        if [[ -e "src/$item" ]] || [[ -e "$item" ]]; then
            print_status "Source item exists: $item"
        else
            print_warning "Source item missing: $item"
        fi
    done
else
    print_warning "Source directory not found (may be in root)"
fi

# Check TypeScript configuration
if [[ -f "tsconfig.json" ]]; then
    print_status "TypeScript configuration exists"
else
    print_warning "TypeScript configuration not found"
fi

# 6. Asset Validation
print_section "Asset Validation"

# Check for app icons
ICON_PATHS=(
    "android/app/src/main/res/mipmap-hdpi"
    "android/app/src/main/res/mipmap-mdpi"
    "android/app/src/main/res/mipmap-xhdpi"
    "android/app/src/main/res/mipmap-xxhdpi"
    "android/app/src/main/res/mipmap-xxxhdpi"
    "ios/MEDHASAKTHIAdmin/Images.xcassets"
)

for path in "${ICON_PATHS[@]}"; do
    if [[ -d "$path" ]]; then
        print_status "Icon directory exists: $(basename $path)"
    else
        print_warning "Icon directory missing: $path"
    fi
done

# 7. Configuration Validation
print_section "Configuration Validation"

# Check app.json configuration
if [[ -f "app.json" ]]; then
    if grep -q "MEDHASAKTHIAdmin" app.json; then
        print_status "App name configured correctly"
    else
        print_warning "App name may not be configured correctly"
    fi
    
    if grep -q "1.0.0" app.json; then
        print_status "App version configured"
    else
        print_warning "App version not found"
    fi
fi

# Check metro configuration
if [[ -f "metro.config.js" ]]; then
    print_status "Metro bundler configuration exists"
else
    print_warning "Metro configuration missing"
fi

# 8. Generate Final Report
print_section "Validation Summary"

TOTAL=$((PASSED + WARNINGS + ERRORS))
if [[ $TOTAL -gt 0 ]]; then
    SUCCESS_RATE=$(( (PASSED * 100) / TOTAL ))
else
    SUCCESS_RATE=0
fi

echo -e "${BLUE}📊 Mobile App Validation Results:${NC}"
echo -e "   ✅ Passed: $PASSED"
echo -e "   ⚠️  Warnings: $WARNINGS"
echo -e "   ❌ Errors: $ERRORS"
echo -e "   📈 Success Rate: $SUCCESS_RATE%"

echo ""
echo -e "${BLUE}📱 Platform Readiness Assessment:${NC}"

if [[ $ERRORS -eq 0 ]]; then
    if [[ $WARNINGS -eq 0 ]]; then
        echo -e "${GREEN}🟢 FULLY READY${NC} - Both Android and iOS platforms are ready for build!"
        echo ""
        echo -e "${GREEN}🚀 Next Steps:${NC}"
        echo -e "   📱 Android: Run 'npm run build:android' to build APK"
        echo -e "   🍎 iOS: Run 'npm run build:ios' to build for iOS (macOS only)"
        echo -e "   📦 Both: Run 'npm run build:both' to build for both platforms"
        exit 0
    elif [[ $WARNINGS -le 5 ]]; then
        echo -e "${YELLOW}🟡 MOSTLY READY${NC} - Minor warnings only. Safe to build with monitoring."
        echo ""
        echo -e "${YELLOW}⚠️  Recommended Actions:${NC}"
        echo -e "   1. Review warnings above"
        echo -e "   2. Add missing app icons for better user experience"
        echo -e "   3. Configure signing certificates for production"
        exit 0
    else
        echo -e "${YELLOW}🟠 READY WITH CAUTION${NC} - Multiple warnings. Review before building."
        exit 1
    fi
else
    echo -e "${RED}🔴 NOT READY${NC} - Critical errors must be fixed before building."
    echo ""
    echo -e "${RED}❌ Fix the following errors before building:${NC}"
    echo "   - Ensure all platform-specific files are present"
    echo "   - Check package.json dependencies"
    echo "   - Verify Android and iOS configurations"
    echo "   - Run this script again after fixes"
    exit 2
fi
