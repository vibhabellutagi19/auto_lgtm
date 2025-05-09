FROM python:3.9-slim

WORKDIR /app

RUN pip install uv && \
    apt-get update && \
    apt-get install -y curl && \
    rm -rf /var/lib/apt/lists/*

COPY pyproject.toml .

RUN uv pip compile pyproject.toml -o requirements.txt && \
    pip install -r requirements.txt

COPY auto_lgtm/ auto_lgtm/

ENV PORT=8080

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

CMD exec gunicorn --bind 0.0.0.0:$PORT --workers 1 --worker-class uvicorn.workers.UvicornWorker --threads 8 auto_lgtm.webhook:app 