FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements/base.txt requirements/prod.txt ./
RUN pip install --no-cache-dir -r prod.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p logs instance

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=app
ENV FLASK_ENV=production
ENV FLASK_DEBUG=0

# Expose port
EXPOSE 5000

# Run the application with gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "120", "app:create_app()"] 