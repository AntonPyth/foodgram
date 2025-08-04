#!/bin/bash

set -e

echo "Running migrations..."
python manage.py makemigrations
python manage.py migrate

echo "Loading initial data..."
python manage.py load_db

echo "Starting server..."
gunicorn --bind 0.0.0.0:8080 foodgram.wsgi 