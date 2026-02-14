# ========================
# HOPE Backend - Production Dockerfile
# Multi-stage build for minimal image size
# ========================

# Stage 1: Build dependencies
FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install (including gunicorn)
COPY requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt

# Stage 2: Production image
FROM python:3.11-slim

WORKDIR /app

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && useradd -m -r appuser

# Copy wheels from builder
COPY --from=builder /app/wheels /wheels
RUN pip install --no-cache-dir /wheels/* && rm -rf /wheels

# Copy application code
COPY src/ ./src/
COPY alembic/ ./alembic/
COPY alembic.ini .

# Set Python path
ENV PYTHONPATH=/app/src
ENV PYTHONUNBUFFERED=1

# Switch to non-root user
USER appuser

# Azure App Service injects PORT env var - default to 8000 for local
ENV PORT=8000

# Workers = 2 * CPU cores + 1 (auto-detect via --workers flag)
ENV WEB_CONCURRENCY=4

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

# Run with Gunicorn + UvicornWorker for production multi-process serving
CMD gunicorn hope.main:app --bind 0.0.0.0:$PORT --worker-class uvicorn.workers.UvicornWorker --workers ${WEB_CONCURRENCY} --timeout 120 --graceful-timeout 30 --access-logfile - --error-logfile -
