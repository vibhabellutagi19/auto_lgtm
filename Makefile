# Configuration
IMAGE_NAME ?= auto-lgtm-local

.PHONY: help
help:
	@echo "Available commands:"
	@echo "  make docker-build      - Build the Docker image"
	@echo "  make docker-run        - Run the Docker container locally"
	@echo "  make docker-shell      - Get a shell inside the Docker container"
	@echo "  make run-dev           - Run FastAPI locally with uvicorn"
	@echo "  make test              - Run tests"
	@echo "  make clean             - Clean build artifacts"

.PHONY: docker-build
docker-build:
	@echo "🐳 Building Docker image..."
	docker build -t $(IMAGE_NAME):latest .

.PHONY: docker-run
docker-run:
	@echo "🐳 Running Docker container on http://localhost:8080 ..."
	docker run -p 8080:8080 -e PORT=8080 $(IMAGE_NAME):latest

.PHONY: docker-shell
docker-shell:
	@echo "🐚 Starting shell in Docker container..."
	docker run -it --entrypoint /bin/sh $(IMAGE_NAME):latest

.PHONY: run-dev
run-dev:
	@echo "🚀 Starting development server..."
	uvicorn auto_lgtm.webhook:app --reload --port 8000

.PHONY: test
test:
	@echo "🧪 Running tests..."
	python -m pytest tests/

.PHONY: clean
clean:
	@echo "🧹 Cleaning build artifacts..."
	rm -rf build/
	rm -f function.zip
	rm -f function_*.zip
	@echo "✅ Clean completed"

.DEFAULT_GOAL := help 