#!/usr/bin/env bash
#
# build.sh - Build ORBITE pour Render (exécuté par Render à chaque déploiement).
#   Le working directory est "backend" (Root Directory = backend).
#
set -euo pipefail

echo "==> Dépendances Python"
python -m pip install --upgrade pip
pip install -r requirements.txt

echo "==> Build frontend (React) dans ../frontend"
cd ../frontend
npm ci
npm run build

echo "==> Collecte des statiques (admin + WhiteNoise)"
cd ../backend
python manage.py collectstatic --noinput --clear