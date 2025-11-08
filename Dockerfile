# Use official Python runtime as a parent image
FROM python:3.10-slim

# Set environment
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . /app

# Expose port used by Render
EXPOSE 10000

# Run the app with gunicorn
CMD ["gunicorn", "-b", "0.0.0.0:10000", "main:app"]
