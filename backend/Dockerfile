# backend/Dockerfile

FROM python:3.11-slim

# Create app directory
WORKDIR /app

# Prevent Python from writing .pyc files and buffering stdout
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files into image
COPY . .

# Default command
CMD ["gunicorn", "backend.wsgi:application", "--bind", "0.0.0.0:8000"]
