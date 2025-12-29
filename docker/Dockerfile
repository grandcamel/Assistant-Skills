# Assistant Skills Test Environment
# Supports both unit tests and live integration tests

ARG PYTHON_VERSION=3.11
FROM python:${PYTHON_VERSION}-slim

LABEL maintainer="Jason Krueger <grandcamel@github.com>"
LABEL description="Test environment for Assistant Skills project"

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt /tmp/requirements.txt

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install -r /tmp/requirements.txt && \
    pip install \
        requests>=2.28.0 \
        python-dotenv>=1.0.0

# Copy the entire project
COPY . /app/

# Make scripts executable
RUN chmod +x /app/scripts/*.sh 2>/dev/null || true

# Create output directory for test results
RUN mkdir -p /app/test-results

# Default command runs unit tests
CMD ["pytest", "skills/assistant-builder/tests/", "-v", "--tb=short"]
