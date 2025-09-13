FROM python:3.9-slim

WORKDIR /app

# Install system dependencies (SQLite è incluso in Python)
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create directories
RUN mkdir -p data ml_models

# Expose port
EXPOSE 5000

# Set environment variables
ENV FLASK_APP=run.py
ENV FLASK_ENV=production
ENV DATABASE_URL=sqlite:///data/bike_sharing.db

# Command to run the application
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "run:app"]
