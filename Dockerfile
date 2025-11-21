FROM python:3.11-slim

LABEL maintainer="Nathan Poinsette <nathan@echo.ai>"
LABEL description="Echo - Hybrid Intelligence Framework"

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY echo-os ./echo-os
COPY echo-vault ./echo-vault
COPY echo-engines ./echo-engines
COPY api ./api
COPY connectors ./connectors
COPY config ./config

# Create directories for runtime data
RUN mkdir -p /app/echo-vault/data \
    /app/echo-os/runtime \
    /app/logs

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application
CMD ["uvicorn", "api.rest.server:app", "--host", "0.0.0.0", "--port", "8000"]
