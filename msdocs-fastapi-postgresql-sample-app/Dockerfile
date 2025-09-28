# Use Python 3.12 slim image as base
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements files
COPY requirements.txt .
COPY src/requirements.txt ./src/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir -r src/requirements.txt

# Copy the application code
COPY . .

# Install the app as editable package
RUN pip install -e src

# Make entrypoint script executable
RUN chmod +x src/entrypoint.sh

# Expose port 8000
EXPOSE 8000

# Set environment variables
ENV PYTHONPATH=/app/src
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Run the application
CMD ["python3", "-m", "uvicorn", "fastapi_app:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]