# Multi-stage Dockerfile for Lethai Concierge Referral Bot
FROM python:3.11-slim as base
RUN apt-get update && \
    apt-get install -y fonts-dejavu-core && \
    rm -rf /var/lib/apt/lists/*
# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create directories for data and logs
RUN mkdir -p /app/data /app/logs

# Create non-root user for security
RUN groupadd -r botuser && useradd -r -g botuser botuser && \
    chown -R botuser:botuser /app

# Switch to non-root user
USER botuser

# Expose port (if needed for webhooks in future)
EXPOSE 8080

# Note: Health check is configured in docker-compose.yml
# (Bot uses long polling, not HTTP server, so process check is used)

# Default command
CMD ["python", "main.py"]

