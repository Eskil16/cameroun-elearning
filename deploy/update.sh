#!/bin/bash
# ============================================================
# SCRIPT 4 — update.sh
# Mettre à jour l'application en production (sans downtime)
#
# Usage : bash update.sh
# ============================================================
set -e

APP_DIR="/opt/cameroun_elearning"
VENV="$APP_DIR/backend/venv"

echo "🔄 Mise à jour en cours..."

cd "$APP_DIR"
git pull origin main

source "$VENV/bin/activate"
cd backend
pip install -r requirements.txt --quiet
python manage.py migrate --noinput
python manage.py collectstatic --noinput --clear

systemctl restart elearning
systemctl reload nginx

echo "✅ Mise à jour terminée ! $(date)"
systemctl status elearning --no-pager | head -5
