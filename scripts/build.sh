#!/bin/bash

# Exit on error
set -e

echo "🚀 Starting build process..."

# Create a temporary build directory
BUILD_DIR="build"
mkdir -p $BUILD_DIR

# Copy necessary files to build directory
echo "📦 Copying files to build directory..."
cp -r auto_lgtm $BUILD_DIR/
cp requirements.txt $BUILD_DIR/
cp .env $BUILD_DIR/

# Create a zip file
echo "🗜️ Creating deployment package..."
cd $BUILD_DIR
zip -r ../function.zip .
cd ..

echo "✅ Build completed successfully!" 