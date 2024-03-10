#!/bin/bash

echo "Applying database migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

exec gunicorn --bind "0.0.0.0:8000" "mailing_service.wsgi:application"
