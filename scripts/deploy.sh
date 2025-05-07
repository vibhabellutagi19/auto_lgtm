#!/bin/bash

# Exit on error
set -e

# Configuration
PROJECT_ID="your-project-id"  # Replace with your GCP project ID
FUNCTION_NAME="auto-lgtm-webhook"
REGION="us-central1"
RUNTIME="python311"
MEMORY="256MB"
TIMEOUT="540s"
BUCKET_NAME="auto-lgtm-deployments"
ZIP_NAME=$(ls -t function_*.zip | head -n1)

echo "🚀 Starting deployment process..."

# Check if zip file exists
if [ ! -f "$ZIP_NAME" ]; then
    echo "❌ No zip file found. Please run build.sh and upload.sh first."
    exit 1
fi

# Deploy the function
echo "🚀 Deploying function to Cloud Functions..."
gcloud functions deploy ${FUNCTION_NAME} \
    --project=${PROJECT_ID} \
    --region=${REGION} \
    --runtime=${RUNTIME} \
    --memory=${MEMORY} \
    --timeout=${TIMEOUT} \
    --source=${ZIP_NAME} \
    --entry-point=app \
    --trigger-http \
    --allow-unauthenticated \
    --set-env-vars="GITHUB_TOKEN=${GITHUB_TOKEN},GITHUB_WEBHOOK_SECRET=${GITHUB_WEBHOOK_SECRET}"

echo "✅ Deployment completed successfully!" 