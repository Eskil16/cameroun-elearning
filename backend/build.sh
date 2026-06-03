#!/usr/bin/env bash
# ============================================================
# build.sh — Script de build Railway
# Exécuté automatiquement par Railway à chaque déploiement
# ============================================================
set -o errexit  # Arrête si erreur

echo "🔧 Installation des dépendances..."
pip install -r requirements.txt

echo "📊 Application des migrations..."
python manage.py migrate --noinput

echo "📁 Collecte des fichiers statiques..."
python manage.py collectstatic --noinput --clear

echo "🌱 Initialisation des données (si première fois)..."
python -c "
import django, os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(email='admin@elearning.cm').exists():
    import subprocess
    subprocess.run(['python', 'init_db.py'], check=True)
    print('Données initiales créées.')
else:
    print('Données déjà présentes, skip.')
"

echo "✅ Build terminé avec succès !"
