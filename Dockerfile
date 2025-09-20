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

# Add a meaningless 'echo' to bust the cache and force a rebuild
RUN echo "Triggering build: $(date)"

RUN python manage.py migrate
RUN python manage.py loaddata data.json
RUN python manage.py collectstatic --noinput


EXPOSE 8000

# Start command
CMD ["gunicorn", "myproject.wsgi:application", "--bind", "0.0.0.0:8000"]
