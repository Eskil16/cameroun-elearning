#!/usr/bin/env bash
# Build phase — pas d'accès BDD ici
set -o errexit

echo "🔧 Installation des dépendances..."
pip install -r requirements.txt

echo "📁 Collecte des fichiers statiques..."
python manage.py collectstatic --noinput --clear

echo "✅ Build terminé !"
