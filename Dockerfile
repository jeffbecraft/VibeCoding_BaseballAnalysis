# Multi-stage Dockerfile for MLB Statistics Analysis System
# Optimized for production deployment with minimal image size

# Stage 1: Build stage
FROM python:3.11-slim as builder

# Set working directory
WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt requirements_web.txt ./

# Create virtual environment and install dependencies
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir -r requirements_web.txt

# Stage 2: Runtime stage
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/opt/venv/bin:$PATH" \
    ENVIRONMENT=production

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash mlbuser && \
    mkdir -p /app /app/data/cache /app/data/ai_code_cache && \
    chown -R mlbuser:mlbuser /app

# Set working directory
WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder --chown=mlbuser:mlbuser /opt/venv /opt/venv

# Copy application code
COPY --chown=mlbuser:mlbuser src/ ./src/
COPY --chown=mlbuser:mlbuser utils/ ./utils/
COPY --chown=mlbuser:mlbuser streamlit_app.py ./
COPY --chown=mlbuser:mlbuser .env.example ./

# Create .env from example if not exists
RUN if [ ! -f .env ]; then cp .env.example .env; fi

# Switch to non-root user
USER mlbuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8501/_stcore/health', timeout=5)"

# Expose Streamlit port
EXPOSE 8501

# Run Streamlit app
CMD ["streamlit", "run", "streamlit_app.py", \
     "--server.port=8501", \
     "--server.address=0.0.0.0", \
     "--server.headless=true", \
     "--server.fileWatcherType=none", \
     "--browser.gatherUsageStats=false"]
