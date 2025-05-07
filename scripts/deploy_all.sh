#!/bin/bash

# Exit on error
set -e

echo "🚀 Starting full deployment process..."

# Run build script
echo "📦 Building application..."
./scripts/build.sh

# Run upload script
echo "📤 Uploading to GCS..."
./scripts/upload.sh

# Run deploy script
echo "🚀 Deploying to Cloud Functions..."
./scripts/deploy.sh

echo "✅ Full deployment process completed successfully!" 