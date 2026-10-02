#!/usr/bin/env bash
#
# setup.sh - Préparation ORBITE sur alwaysdata (plan Free, jamais endormi).
#   À exécuter dans le SSH/python shell alwaysdata (ou Terminal web).
#
#   Usage :
#     bash ~/orbite-setup.sh            (clone + environnements + migrations)
#   Variables d'environnement à fournir :
#     ORBITE_LLM_API_KEY     clé Groq (obligatoire pour l'IA réelle)
#     ORBITE_SECRET_KEY      secret Django (sinon généré)
#     ORBITE_SITE_URL        ex. https://moncompte.alwaysdata.net (sinon "*")
#
#   Idempotent : relançable pour appliquer les mises à jour du dépôt.
#
set -euo pipefail

APP="${1:-$HOME/orbite}"

echo "==> Code source"
if [[ -d "$APP/.git" ]]; then
  git -C "$APP" fetch origin
  git -C "$APP" pull --ff-only origin main
else
  git clone --branch main https://github.com/diakitekabine38-pixel/ORBITE-Apprendre-avec-l-IA.git "$APP"
fi

echo "==> Environnement Python"
if [[ ! -x "$APP/venv/bin/python" ]]; then
  python3 -m venv "$APP/venv"
fi
"$APP/venv/bin/pip" install --upgrade pip wheel
"$APP/venv/bin/pip" install -r "$APP/backend/requirements.txt"

echo "==> Configuration (.env)"
ORBITE_SECRET_KEY="${ORBITE_SECRET_KEY:-$(python3 -c 'import secrets;print(secrets.token_hex(32))')}"
: > "$APP/backend/.env"
printf 'ORBITE_DEBUG=0\n' >> "$APP/backend/.env"
printf 'ORBITE_SECRET_KEY=%s\n' "$ORBITE_SECRET_KEY" >> "$APP/backend/.env"
printf 'ORBITE_ALLOWED_HOSTS=%s\n' "${ORBITE_ALLOWED_HOSTS:-*}" >> "$APP/backend/.env"
printf 'ORBITE_SITE_URL=%s\n' "${ORBITE_SITE_URL:-*}" >> "$APP/backend/.env"
printf 'ORBITE_CORS_ORIGINS=%s\n' "${ORBITE_SITE_URL:-*}" >> "$APP/backend/.env"
printf 'ORBITE_LLM_PROVIDER=%s\n' "${ORBITE_LLM_PROVIDER:-openai}" >> "$APP/backend/.env"
printf 'ORBITE_LLM_MODEL=%s\n' "${ORBITE_LLM_MODEL:-openai/gpt-oss-120b}" >> "$APP/backend/.env"
printf 'ORBITE_LLM_API_KEY=%s\n' "${ORBITE_LLM_API_KEY:-}" >> "$APP/backend/.env"
printf 'ORBITE_WEB_SEARCH=1\n' >> "$APP/backend/.env"
printf 'ORBITE_TAVILY_API_KEY=%s\n' "${ORBITE_TAVILY_API_KEY:-}" >> "$APP/backend/.env"
printf 'ORBITE_STRIPE_SECRET_KEY=%s\n' "${ORBITE_STRIPE_SECRET_KEY:-}" >> "$APP/backend/.env"
printf 'ORBITE_STRIPE_PUBLISHABLE_KEY=%s\n' "${ORBITE_STRIPE_PUBLISHABLE_KEY:-}" >> "$APP/backend/.env"
printf 'ORBITE_STRIPE_WEBHOOK_SECRET=%s\n' "${ORBITE_STRIPE_WEBHOOK_SECRET:-}" >> "$APP/backend/.env"
chmod 600 "$APP/backend/.env"

echo "==> Migrations + statiques (frontend déjà buildé dans le dépôt)"
cd "$APP/backend"
"$APP/venv/bin/python" manage.py migrate --noinput
"$APP/venv/bin/python" manage.py collectstatic --noinput --clear

echo
echo "OK - maintenant, dans le panneau alwaysdata :"
echo "  Site : type Python (WSGI)."
echo "  Chemin d'application : $APP/backend/config/wsgi.py"
echo "  Répertoire de travail : $APP/backend"
echo "  Environnement Python : $APP/venv"
echo "  Version Python : 3.12 (celle du venv)"