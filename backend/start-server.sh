#!/bin/bash

set -e

mkdir -p /app/media/avatars
chown -R root:root /app/media
chmod -R 755 /app/media

echo "Running migrations..."
python manage.py makemigrations
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Loading initial data..."
python manage.py load_db

echo "Starting server..."
gunicorn --bind 0.0.0.0:8080 foodgram.wsgi