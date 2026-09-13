#!/bin/sh

set -e

# Wait for PostgreSQL database host to be ready
if [ "$DB_ENGINE" = "django.db.backends.postgresql" ] || [ -n "$DB_HOST" ]; then
    echo "Waiting for database at ${DB_HOST:-db}:${DB_PORT:-5432}..."
    while ! nc -z "${DB_HOST:-db}" "${DB_PORT:-5432}"; do
        sleep 1
    done
    echo "PostgreSQL is available and ready."
fi

# Run Django migrations
echo "Applying database migrations..."
python manage.py migrate --noinput

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

exec "$@"

