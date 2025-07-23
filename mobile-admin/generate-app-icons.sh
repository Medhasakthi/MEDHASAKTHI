#!/bin/bash

# MEDHASAKTHI Mobile Admin - App Icon Generator
# Generates all required app icon sizes for Android and iOS from the source logo

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

echo -e "${BLUE}🎨 MEDHASAKTHI App Icon Generator${NC}"
echo -e "${BLUE}=================================${NC}"

# Check if ImageMagick is installed
if ! command -v convert >/dev/null 2>&1; then
    print_error "ImageMagick not found. Please install ImageMagick:"
    echo "  Ubuntu/Debian: sudo apt-get install imagemagick"
    echo "  macOS: brew install imagemagick"
    echo "  Windows: Download from https://imagemagick.org/script/download.php"
    exit 1
fi
print_status "ImageMagick found"

# Source logo path
SOURCE_LOGO="src/assets/images/medhasakthi.png"

if [[ ! -f "$SOURCE_LOGO" ]]; then
    print_error "Source logo not found: $SOURCE_LOGO"
    exit 1
fi
print_status "Source logo found: $SOURCE_LOGO"

# Create directories
print_info "Creating icon directories..."

# Android directories
mkdir -p android/app/src/main/res/mipmap-mdpi
mkdir -p android/app/src/main/res/mipmap-hdpi
mkdir -p android/app/src/main/res/mipmap-xhdpi
mkdir -p android/app/src/main/res/mipmap-xxhdpi
mkdir -p android/app/src/main/res/mipmap-xxxhdpi

# iOS directories
mkdir -p ios/MEDHASAKTHIAdmin/Images.xcassets/AppIcon.appiconset

print_status "Directories created"

# Generate Android icons
print_info "Generating Android app icons..."

# Android icon sizes
convert "$SOURCE_LOGO" -resize 48x48 android/app/src/main/res/mipmap-mdpi/ic_launcher.png
convert "$SOURCE_LOGO" -resize 72x72 android/app/src/main/res/mipmap-hdpi/ic_launcher.png
convert "$SOURCE_LOGO" -resize 96x96 android/app/src/main/res/mipmap-xhdpi/ic_launcher.png
convert "$SOURCE_LOGO" -resize 144x144 android/app/src/main/res/mipmap-xxhdpi/ic_launcher.png
convert "$SOURCE_LOGO" -resize 192x192 android/app/src/main/res/mipmap-xxxhdpi/ic_launcher.png

# Android round icons
convert "$SOURCE_LOGO" -resize 48x48 android/app/src/main/res/mipmap-mdpi/ic_launcher_round.png
convert "$SOURCE_LOGO" -resize 72x72 android/app/src/main/res/mipmap-hdpi/ic_launcher_round.png
convert "$SOURCE_LOGO" -resize 96x96 android/app/src/main/res/mipmap-xhdpi/ic_launcher_round.png
convert "$SOURCE_LOGO" -resize 144x144 android/app/src/main/res/mipmap-xxhdpi/ic_launcher_round.png
convert "$SOURCE_LOGO" -resize 192x192 android/app/src/main/res/mipmap-xxxhdpi/ic_launcher_round.png

print_status "Android icons generated"

# Generate iOS icons
print_info "Generating iOS app icons..."

# iOS icon sizes (all required sizes for iOS)
convert "$SOURCE_LOGO" -resize 20x20 ios/MEDHASAKTHIAdmin/Images.xcassets/AppIcon.appiconset/Icon-20.png
convert "$SOURCE_LOGO" -resize 40x40 ios/MEDHASAKTHIAdmin/Images.xcassets/AppIcon.appiconset/Icon-20@2x.png
convert "$SOURCE_LOGO" -resize 60x60 ios/MEDHASAKTHIAdmin/Images.xcassets/AppIcon.appiconset/Icon-20@3x.png
convert "$SOURCE_LOGO" -resize 29x29 ios/MEDHASAKTHIAdmin/Images.xcassets/AppIcon.appiconset/Icon-29.png
convert "$SOURCE_LOGO" -resize 58x58 ios/MEDHASAKTHIAdmin/Images.xcassets/AppIcon.appiconset/Icon-29@2x.png
convert "$SOURCE_LOGO" -resize 87x87 ios/MEDHASAKTHIAdmin/Images.xcassets/AppIcon.appiconset/Icon-29@3x.png
convert "$SOURCE_LOGO" -resize 40x40 ios/MEDHASAKTHIAdmin/Images.xcassets/AppIcon.appiconset/Icon-40.png
convert "$SOURCE_LOGO" -resize 80x80 ios/MEDHASAKTHIAdmin/Images.xcassets/AppIcon.appiconset/Icon-40@2x.png
convert "$SOURCE_LOGO" -resize 120x120 ios/MEDHASAKTHIAdmin/Images.xcassets/AppIcon.appiconset/Icon-40@3x.png
convert "$SOURCE_LOGO" -resize 120x120 ios/MEDHASAKTHIAdmin/Images.xcassets/AppIcon.appiconset/Icon-60@2x.png
convert "$SOURCE_LOGO" -resize 180x180 ios/MEDHASAKTHIAdmin/Images.xcassets/AppIcon.appiconset/Icon-60@3x.png
convert "$SOURCE_LOGO" -resize 76x76 ios/MEDHASAKTHIAdmin/Images.xcassets/AppIcon.appiconset/Icon-76.png
convert "$SOURCE_LOGO" -resize 152x152 ios/MEDHASAKTHIAdmin/Images.xcassets/AppIcon.appiconset/Icon-76@2x.png
convert "$SOURCE_LOGO" -resize 167x167 ios/MEDHASAKTHIAdmin/Images.xcassets/AppIcon.appiconset/Icon-83.5@2x.png
convert "$SOURCE_LOGO" -resize 1024x1024 ios/MEDHASAKTHIAdmin/Images.xcassets/AppIcon.appiconset/Icon-1024.png

print_status "iOS icons generated"

# Create iOS Contents.json
print_info "Creating iOS Contents.json..."

cat > ios/MEDHASAKTHIAdmin/Images.xcassets/AppIcon.appiconset/Contents.json << 'EOF'
{
  "images" : [
    {
      "idiom" : "iphone",
      "scale" : "2x",
      "size" : "20x20",
      "filename" : "Icon-20@2x.png"
    },
    {
      "idiom" : "iphone",
      "scale" : "3x",
      "size" : "20x20",
      "filename" : "Icon-20@3x.png"
    },
    {
      "idiom" : "iphone",
      "scale" : "1x",
      "size" : "29x29",
      "filename" : "Icon-29.png"
    },
    {
      "idiom" : "iphone",
      "scale" : "2x",
      "size" : "29x29",
      "filename" : "Icon-29@2x.png"
    },
    {
      "idiom" : "iphone",
      "scale" : "3x",
      "size" : "29x29",
      "filename" : "Icon-29@3x.png"
    },
    {
      "idiom" : "iphone",
      "scale" : "2x",
      "size" : "40x40",
      "filename" : "Icon-40@2x.png"
    },
    {
      "idiom" : "iphone",
      "scale" : "3x",
      "size" : "40x40",
      "filename" : "Icon-40@3x.png"
    },
    {
      "idiom" : "iphone",
      "scale" : "2x",
      "size" : "60x60",
      "filename" : "Icon-60@2x.png"
    },
    {
      "idiom" : "iphone",
      "scale" : "3x",
      "size" : "60x60",
      "filename" : "Icon-60@3x.png"
    },
    {
      "idiom" : "ipad",
      "scale" : "1x",
      "size" : "20x20",
      "filename" : "Icon-20.png"
    },
    {
      "idiom" : "ipad",
      "scale" : "2x",
      "size" : "20x20",
      "filename" : "Icon-20@2x.png"
    },
    {
      "idiom" : "ipad",
      "scale" : "1x",
      "size" : "29x29",
      "filename" : "Icon-29.png"
    },
    {
      "idiom" : "ipad",
      "scale" : "2x",
      "size" : "29x29",
      "filename" : "Icon-29@2x.png"
    },
    {
      "idiom" : "ipad",
      "scale" : "1x",
      "size" : "40x40",
      "filename" : "Icon-40.png"
    },
    {
      "idiom" : "ipad",
      "scale" : "2x",
      "size" : "40x40",
      "filename" : "Icon-40@2x.png"
    },
    {
      "idiom" : "ipad",
      "scale" : "1x",
      "size" : "76x76",
      "filename" : "Icon-76.png"
    },
    {
      "idiom" : "ipad",
      "scale" : "2x",
      "size" : "76x76",
      "filename" : "Icon-76@2x.png"
    },
    {
      "idiom" : "ipad",
      "scale" : "2x",
      "size" : "83.5x83.5",
      "filename" : "Icon-83.5@2x.png"
    },
    {
      "idiom" : "ios-marketing",
      "scale" : "1x",
      "size" : "1024x1024",
      "filename" : "Icon-1024.png"
    }
  ],
  "info" : {
    "author" : "xcode",
    "version" : 1
  }
}
EOF

print_status "iOS Contents.json created"

# Generate splash screen images
print_info "Generating splash screen images..."

# Create splash screen with logo
mkdir -p android/app/src/main/res/drawable
mkdir -p ios/MEDHASAKTHIAdmin/Images.xcassets/LaunchImage.launchimage

# Android splash screen (create a simple drawable)
cat > android/app/src/main/res/drawable/splash_screen.xml << 'EOF'
<?xml version="1.0" encoding="utf-8"?>
<layer-list xmlns:android="http://schemas.android.com/apk/res/android">
    <item android:drawable="@color/primary_color" />
    <item>
        <bitmap
            android:gravity="center"
            android:src="@mipmap/ic_launcher" />
    </item>
</layer-list>
EOF

# Android launch screen
cat > android/app/src/main/res/drawable/launch_screen.xml << 'EOF'
<?xml version="1.0" encoding="utf-8"?>
<layer-list xmlns:android="http://schemas.android.com/apk/res/android">
    <item android:drawable="@color/primary_color" />
    <item>
        <bitmap
            android:gravity="center"
            android:src="@mipmap/ic_launcher" />
    </item>
    <item android:bottom="100dp">
        <bitmap
            android:gravity="center|bottom"
            android:src="@mipmap/ic_launcher" />
    </item>
</layer-list>
EOF

print_status "Splash screen resources created"

# Update package.json scripts
print_info "Updating package.json scripts..."

# Add icon generation script to package.json
if grep -q "generate:icons" package.json; then
    print_info "Icon generation script already exists in package.json"
else
    # Add the script (this would need manual editing in a real scenario)
    print_info "Add this script to package.json manually:"
    echo '  "generate:icons": "./generate-app-icons.sh"'
fi

# Generate build summary
BUILD_DATE=$(date '+%Y-%m-%d %H:%M:%S')

cat > icon-generation-report.json << EOF
{
  "generatedAt": "$BUILD_DATE",
  "sourceImage": "$SOURCE_LOGO",
  "androidIcons": {
    "mdpi": "48x48",
    "hdpi": "72x72", 
    "xhdpi": "96x96",
    "xxhdpi": "144x144",
    "xxxhdpi": "192x192"
  },
  "iosIcons": {
    "iPhone": ["20@2x", "20@3x", "29", "29@2x", "29@3x", "40@2x", "40@3x", "60@2x", "60@3x"],
    "iPad": ["20", "20@2x", "29", "29@2x", "40", "40@2x", "76", "76@2x", "83.5@2x"],
    "AppStore": ["1024"]
  },
  "splashScreens": {
    "android": "splash_screen.xml, launch_screen.xml",
    "ios": "LaunchScreen.storyboard"
  }
}
EOF

print_status "Icon generation report created"

echo ""
echo -e "${GREEN}🎉 App Icon Generation Completed!${NC}"
echo -e "${GREEN}===================================${NC}"
echo ""
echo -e "${BLUE}📱 Generated Icons:${NC}"
echo -e "   🤖 Android: 10 icon sizes (mdpi to xxxhdpi)"
echo -e "   🍎 iOS: 19 icon sizes (iPhone, iPad, App Store)"
echo -e "   🎨 Splash Screens: Android XML drawables"
echo ""
echo -e "${BLUE}📁 Icon Locations:${NC}"
echo -e "   📂 Android: android/app/src/main/res/mipmap-*/"
echo -e "   📂 iOS: ios/MEDHASAKTHIAdmin/Images.xcassets/AppIcon.appiconset/"
echo ""
echo -e "${BLUE}📋 Next Steps:${NC}"
echo -e "   1. Build the app to see the new icons"
echo -e "   2. Test on both Android and iOS devices"
echo -e "   3. Verify icons appear correctly in app stores"
echo ""
echo -e "${GREEN}🚀 MEDHASAKTHI logo is now your app icon!${NC}"
