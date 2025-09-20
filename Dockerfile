# Build stage
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y build-essential libpq-dev && rm -rf /var/lib/apt/lists/*

COPY requirements-prod.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements-prod.txt

COPY . .

RUN echo "Triggering build: $(date)"

RUN python manage.py collectstatic --noinput

EXPOSE 8000

# Run migrations + load data at runtime before starting server
CMD ["sh", "-c", "python manage.py migrate && python manage.py loaddata data.json && gunicorn myproject.wsgi:application --bind 0.0.0.0:8000"]
