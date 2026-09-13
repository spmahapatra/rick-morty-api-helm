FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    FLASK_ENV=production \
    PYTHONPATH=/app:$PYTHONPATH

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app.py .
COPY config.py .
COPY init_db.py .
COPY src/ ./src/
COPY docker_build_validation.sh .

# Make validation script executable
RUN chmod +x docker_build_validation.sh

# Create non-root user for security
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5000/health')" || exit 1

# Run application with pre-flight validation and database initialization
CMD ["sh", "-c", "./docker_build_validation.sh && python init_db.py && gunicorn -w 2 -b 0.0.0.0:5000 --timeout 120 --access-logfile - --error-logfile - app:app"]

