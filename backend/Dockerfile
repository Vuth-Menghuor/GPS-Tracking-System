FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Collect static files without exposing a production secret in the image.
RUN SECRET_KEY=build-placeholder DEBUG=False python manage.py collectstatic --noinput

# Expose port
EXPOSE 8000

# Run the application
CMD ["sh", "-c", "python manage.py migrate --noinput && gunicorn protrack.wsgi:application --bind 0.0.0.0:$PORT --timeout 300"]
