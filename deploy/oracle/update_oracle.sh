#!/usr/bin/env bash
#
# update_oracle.sh - Mise à jour d'ORBITE sur le VPS Oracle.
#   Récupère le code (main), réinstalle les dépendances, rebuild le frontend,
#   applique les migrations puis redémarre gunicorn.
#
#   Usage : sudo bash /opt/orbite/app/deploy/oracle/update_oracle.sh
#
set -euo pipefail

if [[ $EUID -ne 0 ]]; then
  echo "ERREUR : exécuter avec sudo (root)." >&2
  exit 1
fi

APP_DIR="/opt/orbite/app"
VENV_DIR="/opt/orbite/venv"
RUNUSER="orbite"

echo "==> Pull du code"
sudo -u "$RUNUSER" git -C "$APP_DIR" pull --ff-only origin main

echo "==> Dépendances Python"
sudo -u "$RUNUSER" "$VENV_DIR/bin/pip" install -r "$APP_DIR/backend/requirements.txt"

echo "==> Build frontend"
cd "$APP_DIR/frontend"
sudo -u "$RUNUSER" env CI=true npm ci
sudo -u "$RUNUSER" npm run build
chown -R "$RUNUSER:$RUNUSER" "$APP_DIR/frontend/dist"

echo "==> Migrations + statiques"
cd "$APP_DIR/backend"
sudo -u "$RUNUSER" "$VENV_DIR/bin/python" manage.py migrate --noinput
sudo -u "$RUNUSER" "$VENV_DIR/bin/python" manage.py collectstatic --noinput --clear

echo "==> Redémarrage du service"
systemctl restart orbite
sleep 3

if curl -fsS http://127.0.0.1:8000/api/health/ >/dev/null 2>&1; then
  echo "OK - ORBITE à jour et en ligne."
else
  echo "ATTENTION : le health-check a échoué. Logs : sudo journalctl -u orbite -n 50"
fi