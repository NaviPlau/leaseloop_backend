#!/usr/bin/env bash
set -e

echo "⏳ Waiting for PostgreSQL at db:5432..."

# Warte maximal 60 Sekunden auf PostgreSQL
for i in {1..60}; do
  if nc -z db 5432; then
    echo "✅ PostgreSQL is up!"
    break
  fi
  echo "⏱ Waiting for db... ($i/60)"
  sleep 1
done

# Abbrechen, wenn DB nach 60s nicht erreichbar ist
if ! nc -z db 5432; then
  echo "❌ PostgreSQL is not available after 60 seconds. Exiting."
  exit 1
fi

echo "PostgreSQL is up – starting migrations..."

python manage.py collectstatic --noinput
python manage.py makemigrations
python manage.py migrate

echo "Running demo data generation..."
python manage.py regenerate_demo_data

echo "Creating superuser..."

python manage.py shell << END
import os
from django.contrib.auth import get_user_model

User = get_user_model()
username = os.environ.get("DJANGO_SUPERUSER_USERNAME")
email = os.environ.get("DJANGO_SUPERUSER_EMAIL")
password = os.environ.get("DJANGO_SUPERUSER_PASSWORD")

if username and not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username, email, password)
    print("Superuser created")
else:
    print("Superuser already exists or username missing")
END


echo "Postgresql migrations finished – starting Gunicorn..."
# start gunicorn on port 8030
exec gunicorn leaseloop_backend.wsgi:application --bind 0.0.0.0:8030