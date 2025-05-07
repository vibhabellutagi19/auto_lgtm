#!/bin/bash

# Exit on error
set -e

# Configuration
PROJECT_ID="your-project-id"  # Replace with your GCP project ID
BUCKET_NAME="auto-lgtm-deployments"  # Replace with your bucket name
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
ZIP_NAME="function_${TIMESTAMP}.zip"

echo "🚀 Starting upload process..."

# Check if function.zip exists
if [ ! -f "function.zip" ]; then
    echo "❌ function.zip not found. Please run build.sh first."
    exit 1
fi

# Create GCS bucket if it doesn't exist
if ! gsutil ls "gs://${BUCKET_NAME}" > /dev/null 2>&1; then
    echo "📦 Creating GCS bucket: ${BUCKET_NAME}"
    gsutil mb -p ${PROJECT_ID} "gs://${BUCKET_NAME}"
fi

# Upload the zip file
echo "📤 Uploading function.zip to GCS..."
gsutil cp function.zip "gs://${BUCKET_NAME}/${ZIP_NAME}"

echo "✅ Upload completed successfully!"
echo "📝 File uploaded to: gs://${BUCKET_NAME}/${ZIP_NAME}" 