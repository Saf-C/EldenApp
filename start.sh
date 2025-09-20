#!/bin/sh

# Apply database migrations
echo "Applying database migrations..."
python manage.py migrate --noinput

# Load data into the database
echo "Loading fixture data..."
python manage.py loaddata data.json

# Start the Gunicorn server
echo "Starting Gunicorn server..."
gunicorn myproject.wsgi:application --bind 0.0.0.0:8000