# Configuration
PROJECT_ID ?= 
BUCKET_NAME ?= auto-lgtm
FUNCTION_NAME ?= auto-lgtm-webhook
REGION ?= us-central1

# Default target
.PHONY: help
help:
	@echo "Available commands:"
	@echo "  make build        - Build the application"
	@echo "  make upload       - Upload the build to GCS"
	@echo "  make deploy       - Deploy to Cloud Functions"
	@echo "  make all          - Run build, upload, and deploy in sequence"
	@echo "  make clean        - Clean build artifacts"
	@echo "  make test         - Run tests"
	@echo "  make install      - Install dependencies using uv"
	@echo "  make venv         - Create virtual environment"
	@echo ""
	@echo "Configuration:"
	@echo "  PROJECT_ID        - GCP Project ID (default: $(PROJECT_ID))"
	@echo "  BUCKET_NAME       - GCS Bucket name (default: $(BUCKET_NAME))"
	@echo "  FUNCTION_NAME     - Cloud Function name (default: $(FUNCTION_NAME))"
	@echo "  REGION           - GCP Region (default: $(REGION))"

# Build the application
.PHONY: build
build:
	@echo "🚀 Building application..."
	@./scripts/build.sh

# Upload to GCS
.PHONY: upload
upload:
	@echo "📤 Uploading to GCS..."
	@PROJECT_ID=$(PROJECT_ID) BUCKET_NAME=$(BUCKET_NAME) ./scripts/upload.sh

# Deploy to Cloud Functions
.PHONY: deploy
deploy:
	@echo "🚀 Deploying to Cloud Functions..."
	@PROJECT_ID=$(PROJECT_ID) \
	FUNCTION_NAME=$(FUNCTION_NAME) \
	REGION=$(REGION) \
	./scripts/deploy.sh

# Run all steps in sequence
.PHONY: all
all: build upload deploy
	@echo "✅ Full deployment process completed successfully!"

# Clean build artifacts
.PHONY: clean
clean:
	@echo "🧹 Cleaning build artifacts..."
	@rm -rf build/
	@rm -f function.zip
	@rm -f function_*.zip
	@echo "✅ Clean completed"

.PHONY: test
test:
	@echo "🧪 Running tests..."
	@python -m pytest tests/

.PHONY: dev
dev:
	@echo "🚀 Starting development server..."
	@uvicorn auto_lgtm.webhook:app --reload --port 8000

# Check environment variables
.PHONY: check-env
check-env:
	@echo "🔍 Checking environment variables..."
	@if [ -z "$(GITHUB_TOKEN)" ]; then \
		echo "❌ GITHUB_TOKEN is not set"; \
		exit 1; \
	fi
	@if [ -z "$(GITHUB_WEBHOOK_SECRET)" ]; then \
		echo "❌ GITHUB_WEBHOOK_SECRET is not set"; \
		exit 1; \
	fi
	@echo "✅ Environment variables check passed"

# Install dependencies using uv
.PHONY: install
install:
	@echo "📦 Installing dependencies using uv..."
	@uv pip install -r requirements.txt
	@echo "✅ Dependencies installed"

# Install development dependencies
.PHONY: install-dev
install-dev:
	@echo "📦 Installing development dependencies using uv..."
	@uv pip install -r requirements-dev.txt
	@echo "✅ Development dependencies installed"

# Create virtual environment and install dependencies
.PHONY: venv
venv:
	@echo "🔧 Creating virtual environment..."
	@uv venv
	@echo "✅ Virtual environment created"
	@echo "To activate the virtual environment, run:"
	@echo "  source .venv/bin/activate"
	@echo "Then install dependencies with:"
	@echo "  make install"

# Update dependencies
.PHONY: update
update:
	@echo "🔄 Updating dependencies..."
	@uv pip compile requirements.in -o requirements.txt
	@echo "✅ Dependencies updated"

# Default target
.DEFAULT_GOAL := help 