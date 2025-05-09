#!/bin/bash

# Replace these variables
PROJECT_ID=$1
PROJECT_NUMBER=$2

add_iam_binding() {
    local role=$1
    echo "Adding role: $role"
    gcloud projects add-iam-policy-binding $PROJECT_ID \
        --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
        --role="$role"
}

# Core Cloud Build permissions
add_iam_binding "roles/cloudbuild.builds.builder"
add_iam_binding "roles/storage.objectViewer"
add_iam_binding "roles/storage.objectCreator"
add_iam_binding "roles/logging.logWriter"

# Container Registry permissions
add_iam_binding "roles/storage.admin"

# Cloud Run permissions
add_iam_binding "roles/run.admin"

# Secret Manager permissions
add_iam_binding "roles/secretmanager.secretAccessor"

echo "All permissions have been set up for Cloud Build service account"