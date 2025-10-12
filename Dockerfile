# Use Python 3.11 slim image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-client \
        build-essential \
        libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user
RUN useradd --create-home --shell /bin/bash appuser

# Copy requirements and install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . /app/

# Change ownership of the app directory to the non-root user
RUN chown -R appuser:appuser /app

# Make entrypoint executable
RUN chmod +x /app/entrypoint.sh

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Set default port if not provided
ENV PORT=8000

# Run entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]
