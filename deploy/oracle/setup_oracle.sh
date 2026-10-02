#!/usr/bin/env bash
#
# setup_oracle.sh - Provisionnement ORBITE sur Oracle Cloud Always Free.
#
#   Objectif : Ubuntu 24.04 (Ampere A1 : 4 OCPU / 24 Go recommandé), tout-en-un :
#   nginx + gunicorn + PostgreSQL + build frontend + HTTPS (Let's Encrypt optionnel).
#
#   Usage :
#     sudo bash setup_oracle.sh
#
#   Variables d'environnement optionnelles (exporter avant l'exécution) :
#     ORBITE_LLM_API_KEY     clé Groq (obligatoire pour l'IA réelle)
#     ORBITE_DOMAIN          domaine public (ex. orbite.duckdns.org) -> HTTPS auto
#     ORBITE_EMAIL           email Let's Encrypt (si domaine fourni)
#     ORBITE_SECRET_KEY      sinon générée
#     ORBITE_JWT_SIGNING_KEY sinon générée
#     ORBITE_DB_PASSWORD     sinon générée
#     ORBITE_STRIPE_*        facultatif (paiements Stripe)
#     ORBITE_TAVILY_API_KEY  facultatif (recherche web enrichie)
#     ORBITE_PUBLIC_IP       facultatif (deviner via api.ipify.org sinon)
#
#   Script idempotent : relançable sans dommage pour mettre à jour.
#
set -euo pipefail

if [[ $EUID -ne 0 ]]; then
  echo "ERREUR : exécuter avec sudo (root)." >&2
  exit 1
fi

APP_DIR="/opt/orbite/app"
VENV_DIR="/opt/orbite/venv"
RUNUSER="orbite"
PY_BIN="/usr/bin/python3"

# ---------------------------------------------------------------------------
# Paramètres (lecture de l'environnement ou valeurs par défaut)
# ---------------------------------------------------------------------------
: "${ORBITE_REPO:=https://github.com/diakitekabine38-pixel/ORBITE-Apprendre-avec-l-IA.git}"
: "${ORBITE_BRANCH:=main}"
: "${ORBITE_DOMAIN:=}"
: "${ORBITE_EMAIL:=}"
ORBITE_LLM_API_KEY="${ORBITE_LLM_API_KEY:-}"

# ---------------------------------------------------------------------------
# (1) Paquets système + Node.js LTS (build frontend)
# ---------------------------------------------------------------------------
echo "==> (1/8) Paquets système"
export DEBIAN_FRONTEND=noninteractive
apt-get update -y
apt-get install -y git curl ca-certificates gnupg nginx \
  python3 python3-pip python3-venv postgresql postgresql-contrib
if ! command -v node >/dev/null 2>&1; then
  curl -fsSL https://deb.nodesource.com/setup_22.x | bash -
  apt-get install -y nodejs
fi

# ---------------------------------------------------------------------------
# (2) Utilisateur applicatif
# ---------------------------------------------------------------------------
echo "==> (2/8) Utilisateur applicatif"
if ! id "$RUNUSER" >/dev/null 2>&1; then
  useradd -m -s /bin/bash "$RUNUSER"
fi
mkdir -p /opt/orbite "$APP_DIR" /var/log/orbite
chown -R "$RUNUSER:$RUNUSER" /opt/orbite /var/log/orbite

# ---------------------------------------------------------------------------
# (3) Code source (clone ou mise à jour)
# ---------------------------------------------------------------------------
echo "==> (3/8) Code source"
if [[ -d "$APP_DIR/.git" ]]; then
  sudo -u "$RUNUSER" git -C "$APP_DIR" fetch origin
  sudo -u "$RUNUSER" git -C "$APP_DIR" checkout "$ORBITE_BRANCH"
  sudo -u "$RUNUSER" git -C "$APP_DIR" pull --ff-only origin "$ORBITE_BRANCH"
else
  sudo -u "$RUNUSER" git clone --branch "$ORBITE_BRANCH" "$ORBITE_REPO" "$APP_DIR"
fi

# ---------------------------------------------------------------------------
# (4) Environnement Python + dépendances
# ---------------------------------------------------------------------------
echo "==> (4/8) Environnement Python"
if [[ ! -x "$VENV_DIR/bin/python" ]]; then
  sudo -u "$RUNUSER" "$PY_BIN" -m venv "$VENV_DIR"
fi
sudo -u "$RUNUSER" "$VENV_DIR/bin/pip" install --upgrade pip
sudo -u "$RUNUSER" "$VENV_DIR/bin/pip" install -r "$APP_DIR/backend/requirements.txt"

# ---------------------------------------------------------------------------
# (5) Secrets + .env de production
# ---------------------------------------------------------------------------
echo "==> (5/8) Secrets et configuration (.env)"
ORBITE_SECRET_KEY="${ORBITE_SECRET_KEY:-$(openssl rand -hex 32)}"
ORBITE_JWT_SIGNING_KEY="${ORBITE_JWT_SIGNING_KEY:-$(openssl rand -hex 32)}"
ORBITE_DB_PASSWORD="${ORBITE_DB_PASSWORD:-$(openssl rand -hex 20)}"

if [[ -n "$ORBITE_DOMAIN" ]]; then
  ORBITE_SITE_URL="${ORBITE_SITE_URL:-https://$ORBITE_DOMAIN}"
  ORBITE_ALLOWED_HOSTS="${ORBITE_ALLOWED_HOSTS:-$ORBITE_DOMAIN}"
  ORBITE_CORS_ORIGINS="${ORBITE_CORS_ORIGINS:-https://$ORBITE_DOMAIN}"
  : "${ORBITE_SECURE_SSL:=1}"
  SERVER_NAME="$ORBITE_DOMAIN"
else
  PUB_IP="${ORBITE_PUBLIC_IP:-$(curl -4 -s -m 10 https://api.ipify.org || true)}"
  PUB_IP="${PUB_IP:-127.0.0.1}"
  ORBITE_SITE_URL="${ORBITE_SITE_URL:-http://$PUB_IP}"
  ORBITE_ALLOWED_HOSTS="${ORBITE_ALLOWED_HOSTS:-$PUB_IP,localhost,127.0.0.1}"
  ORBITE_CORS_ORIGINS="${ORBITE_CORS_ORIGINS:-http://$PUB_IP}"
  : "${ORBITE_SECURE_SSL:=0}"
  SERVER_NAME="_"
fi

write_env() { # write_env KEY VALUE
  printf '%s=%s\n' "$1" "$2" >> "$APP_DIR/backend/.env"
}
: > "$APP_DIR/backend/.env"
write_env ORBITE_DEBUG "0"
write_env ORBITE_SECRET_KEY "$ORBITE_SECRET_KEY"
write_env ORBITE_JWT_SIGNING_KEY "$ORBITE_JWT_SIGNING_KEY"
write_env ORBITE_ALLOWED_HOSTS "$ORBITE_ALLOWED_HOSTS"
write_env ORBITE_SITE_URL "$ORBITE_SITE_URL"
write_env ORBITE_CORS_ORIGINS "$ORBITE_CORS_ORIGINS"
write_env ORBITE_DB "postgres"
write_env ORBITE_DB_NAME "orbite"
write_env ORBITE_DB_USER "$RUNUSER"
write_env ORBITE_DB_PASSWORD "$ORBITE_DB_PASSWORD"
write_env ORBITE_DB_HOST "127.0.0.1"
write_env ORBITE_DB_PORT "5432"
write_env ORBITE_SECURE_SSL "$ORBITE_SECURE_SSL"
write_env ORBITE_WEB_SEARCH "${ORBITE_WEB_SEARCH:-1}"
write_env ORBITE_LLM_PROVIDER "${ORBITE_LLM_PROVIDER:-openai}"
write_env ORBITE_LLM_MODEL "${ORBITE_LLM_MODEL:-openai/gpt-oss-120b}"
write_env ORBITE_LLM_API_KEY "$ORBITE_LLM_API_KEY"
write_env ORBITE_TAVILY_API_KEY "${ORBITE_TAVILY_API_KEY:-}"
write_env ORBITE_STRIPE_SECRET_KEY "${ORBITE_STRIPE_SECRET_KEY:-}"
write_env ORBITE_STRIPE_PUBLISHABLE_KEY "${ORBITE_STRIPE_PUBLISHABLE_KEY:-}"
write_env ORBITE_STRIPE_WEBHOOK_SECRET "${ORBITE_STRIPE_WEBHOOK_SECRET:-}"
chown "$RUNUSER:$RUNUSER" "$APP_DIR/backend/.env"
chmod 600 "$APP_DIR/backend/.env"

# ---------------------------------------------------------------------------
# (6) Build frontend (React -> frontend/dist, servi par WhiteNoise)
# ---------------------------------------------------------------------------
echo "==> (6/8) Build frontend"
cd "$APP_DIR/frontend"
sudo -u "$RUNUSER" env CI=true npm ci
sudo -u "$RUNUSER" npm run build
chown -R "$RUNUSER:$RUNUSER" "$APP_DIR/frontend/dist"

# ---------------------------------------------------------------------------
# (7) PostgreSQL + migrations + statiques
# ---------------------------------------------------------------------------
echo "==> (7/8) Base de données et migrations"
if ! systemctl is-active --quiet postgresql; then
  systemctl start postgresql
fi
if [[ "$(sudo -u postgres psql -tAc "SELECT 1 FROM pg_roles WHERE rolname='$RUNUSER'")" != "1" ]]; then
  sudo -u postgres psql -c "CREATE ROLE $RUNUSER LOGIN PASSWORD '$ORBITE_DB_PASSWORD';"
fi
if [[ "$(sudo -u postgres psql -tAc "SELECT 1 FROM pg_database WHERE datname='orbite'")" != "1" ]]; then
  sudo -u postgres createdb -O "$RUNUSER" orbite
fi
cd "$APP_DIR/backend"
sudo -u "$RUNUSER" "$VENV_DIR/bin/python" manage.py migrate --noinput
sudo -u "$RUNUSER" "$VENV_DIR/bin/python" manage.py collectstatic --noinput --clear

# ---------------------------------------------------------------------------
# (8) Service systemd (gunicorn) + nginx (+ HTTPS si domaine)
# ---------------------------------------------------------------------------
echo "==> (8/8) Service web (gunicorn + nginx)"
mkdir -p /var/log/orbite
chown "$RUNUSER:$RUNUSER" /var/log/orbite

cat > /etc/systemd/system/orbite.service <<EOF
[Unit]
Description=ORBITE (Django via Gunicorn)
After=network.target postgresql.service
Wants=network.target

[Service]
User=$RUNUSER
Group=$RUNUSER
WorkingDirectory=$APP_DIR/backend
ExecStart=$VENV_DIR/bin/gunicorn config.wsgi:application --bind 127.0.0.1:8000 --workers 3 --threads 4 --timeout 180 --access-logfile /var/log/orbite/access.log --error-logfile /var/log/orbite/error.log --capture-output
Restart=always
RestartSec=3
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
EOF

cat > /etc/nginx/sites-available/orbite <<EOF
server {
    listen 80;
    server_name $SERVER_NAME;

    client_max_body_size 25m;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_read_timeout 300s;
        proxy_connect_timeout 60s;
    }
}
EOF

ln -sf /etc/nginx/sites-available/orbite /etc/nginx/sites-enabled/orbite
rm -f /etc/nginx/sites-enabled/default
nginx -t && systemctl reload nginx

systemctl daemon-reload
systemctl enable orbite >/dev/null 2>&1
systemctl restart orbite

if [[ -n "$ORBITE_DOMAIN" ]]; then
  echo "==> HTTPS (Let's Encrypt) pour $ORBITE_DOMAIN"
  apt-get install -y certbot python3-certbot-nginx
  certbot --nginx -d "$ORBITE_DOMAIN" --non-interactive --agree-tos --redirect -m "$ORBITE_EMAIL"
fi

sleep 3
echo
echo "============================================================"
if curl -fsS http://127.0.0.1:8000/api/health/ >/dev/null 2>&1; then
  echo "ORBITE est EN LIGNE sur : $ORBITE_SITE_URL"
else
  echo "ATTENTION : le health-check local a échoué."
  echo "  Logs : sudo journalctl -u orbite -n 50"
fi
echo "============================================================"
echo
echo "Etapes suivantes :"
echo "  1. Ouvrir les ports 80 et 443 dans la Security List OCI (voir README)."
echo "  2. Créer l'administrateur :"
echo "     sudo -u orbite /opt/orbite/venv/bin/python /opt/orbite/app/backend/manage.py createsuperuser"
echo "  3. Mises à jour futures : sudo bash /opt/orbite/app/deploy/oracle/update_oracle.sh"
echo