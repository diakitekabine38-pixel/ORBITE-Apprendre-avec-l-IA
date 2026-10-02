#!/usr/bin/env bash
#
# start.sh - Démarre ORBITE sur Render (gunicorn, Postgres via .env de Render).
#   Le working directory est "backend".
#
set -euo pipefail

echo "==> Migrations"
python manage.py migrate --noinput

echo "==> Démarrage gunicorn"
exec gunicorn config.wsgi:application \
  --bind 0.0.0.0:${PORT:-8000} \
  --workers 2 \
  --threads 4 \
  --timeout 180 \
  --access-logfile - \
  --error-logfile -