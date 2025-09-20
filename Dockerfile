# Use Python 3.12 slim image
FROM python:3.12-slim


# Environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y build-essential libpq-dev && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements-prod.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements-prod.txt

# Copy project code
COPY . .

# Run your pre-deploy commands as part of the build
# This guarantees they run and their output will be visible in the build logs
RUN python manage.py migrate
RUN python manage.py loaddata data/data.json
RUN python manage.py collectstatic --noinput

# Expose the port your app runs on
EXPOSE 8000

# Start command
CMD ["gunicorn", "myproject.wsgi:application", "--bind", "0.0.0.0:8000"]
