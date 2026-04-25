FROM python:3.10-slim as base

# Set environment variables for production
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Install system dependencies in single RUN to reduce layers
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libfreetype6-dev \
    libjpeg-dev \
    libpng-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (better layer caching)
COPY modules/requisitos.txt .

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install -r requisitos.txt

# Copy application code
COPY modules/ ./modules/
COPY assets/ ./assets/
COPY *.html ./

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:9000/health', timeout=5)" || exit 1

# Run Flask with gunicorn for production (but allow override for dev)
CMD ["python", "modules/generar_libro.py"]
