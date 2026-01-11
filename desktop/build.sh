#!/bin/bash

# Build Rentala Desktop App

set -e

echo "Building Rentala Desktop Application..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo -e "${RED}Node.js is not installed. Please install Node.js v16 or higher.${NC}"
    exit 1
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo -e "${RED}npm is not installed. Please install npm.${NC}"
    exit 1
fi

# Navigate to electron directory
cd electron

# Install dependencies
echo -e "${YELLOW}Installing dependencies...${NC}"
npm install

# Create necessary directories
mkdir -p dist
mkdir -p resources

echo -e "${YELLOW}Creating icons...${NC}"

# Create placeholder icons (in production, you should have proper icon files)
if [ ! -f resources/icon.png ]; then
    echo "Creating placeholder icon..."
    # Create a simple icon using ImageMagick if available
    if command -v convert &> /dev/null; then
        convert -size 512x512 xc:#0d6efd -fill white -pointsize 100 -gravity center -draw "text 0,0 'R'" resources/icon.png
        convert resources/icon.png -resize 256x256 resources/icon.ico
        convert resources/icon.png -resize 256x256 resources/icon.icns
    else
        echo "ImageMagick not found. Please create icon files manually:"
        echo "- resources/icon.png (512x512)"
        echo "- resources/icon.ico (Windows)"
        echo "- resources/icon.icns (macOS)"
        echo "- resources/tray.png (16x16 or 32x32)"
        exit 1
    fi
fi

# Build for current platform
echo -e "${YELLOW}Building application...${NC}"

if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    echo -e "${GREEN}Building for macOS...${NC}"
    npm run build:mac
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    echo -e "${GREEN}Building for Linux...${NC}"
    npm run build:linux
elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    # Windows
    echo -e "${GREEN}Building for Windows...${NC}"
    npm run build:win
else
    echo -e "${YELLOW}Unknown OS. Building for all platforms...${NC}"
    npm run build:all
fi

echo -e "${GREEN}Build completed!${NC}"
echo -e "Check the 'dist' directory for the built applications."

# List built files
if [ -d "dist" ]; then
    echo -e "\n${YELLOW}Built files:${NC}"
    find dist -type f -name "*.exe" -o -name "*.dmg" -o -name "*.AppImage" -o -name "*.deb" -o -name "*.rpm" | while read file; do
        echo "  - $(basename "$file")"
    done
fi

cd ..
echo -e "\n${GREEN}Desktop app build process completed!${NC}"
