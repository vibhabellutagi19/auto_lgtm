#!/bin/bash

if [ -z "$GOOGLE_CLOUD_PROJECT" ]; then
    echo "Error: GOOGLE_CLOUD_PROJECT environment variable is not set"
    exit 1
fi

if [ -z "$SECRET_ID" ]; then
    echo "Error: SECRET_ID environment variable is not set"
    exit 1
fi

if [ -z "$GITHUB_INSTALLATION_ID" ]; then
    echo "Error: GITHUB_INSTALLATION_ID environment variable is not set"
    exit 1
fi

echo "Submitting build to Cloud Build..."
gcloud builds submit --config cloudbuild.yaml

# Check if the service exists
if ! gcloud run services describe auto-lgtm --region us-central1 &>/dev/null; then
    echo "Creating new Cloud Run service..."
    gcloud run deploy auto-lgtm \
        --image gcr.io/$GOOGLE_CLOUD_PROJECT/auto-lgtm \
        --region us-central1 \
        --platform managed \
        --allow-unauthenticated \
        --set-env-vars SECRET_ID="$SECRET_ID",GITHUB_INSTALLATION_ID="$GITHUB_INSTALLATION_ID" || exit 1
else
    echo "Updating existing Cloud Run service..."
    gcloud run services update auto-lgtm \
        --region us-central1 \
        --update-env-vars SECRET_ID="$SECRET_ID",GITHUB_INSTALLATION_ID="$GITHUB_INSTALLATION_ID" || exit 1
fi

echo "Build and deployment completed successfully!" 