#!/bin/bash
# ============================================================
# SCRIPT 2 — deploy_app.sh
# Déploiement de l'application Django + Frontend
#
# Usage : bash deploy_app.sh
# ============================================================
set -e

APP_DIR="/opt/cameroun_elearning"
VENV="$APP_DIR/backend/venv"

echo ""
echo "🚀 =============================================="
echo "   Déploiement de l'application"
echo "================================================"
echo ""

# ── 1. Cloner ou mettre à jour le projet ─────────────────────
if [ -d "$APP_DIR" ]; then
    echo "🔄 [1/7] Mise à jour du code..."
    cd "$APP_DIR" && git pull origin main
else
    echo "📥 [1/7] Clonage du projet..."
    mkdir -p /opt
    # Copie locale (si pas de git remote, on copie depuis /tmp)
    cp -r /tmp/cameroun_elearning "$APP_DIR"
fi

# ── 2. Permissions ────────────────────────────────────────────
echo "🔑 [2/7] Configuration des permissions..."
chown -R www-data:www-data "$APP_DIR"
chmod -R 755 "$APP_DIR"
mkdir -p "$APP_DIR/backend/media"
chown -R www-data:www-data "$APP_DIR/backend/media"

# ── 3. Environnement virtuel Python ──────────────────────────
echo "🐍 [3/7] Création de l'environnement virtuel..."
cd "$APP_DIR/backend"
python3.11 -m venv venv
source "$VENV/bin/activate"
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn

# ── 4. Fichier .env de production ────────────────────────────
echo "⚙️  [4/7] Configuration .env..."
if [ ! -f "$APP_DIR/backend/.env" ]; then
    # Génère une SECRET_KEY aléatoire
    SECRET=$(python3 -c "import secrets; print(secrets.token_urlsafe(50))")
    cat > "$APP_DIR/backend/.env" << ENVEOF
SECRET_KEY=$SECRET
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,$(curl -s ifconfig.me)

DB_NAME=cameroun_elearning
DB_USER=elearning_user
DB_PASSWORD=EL3arning_Cam237!
DB_HOST=localhost
DB_PORT=5432

EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
DEFAULT_FROM_EMAIL=noreply@elearning.cm

CORS_ALLOWED_ORIGINS=http://localhost,http://127.0.0.1
ENVEOF
    echo "   → .env créé (pensez à ajouter votre domaine dans ALLOWED_HOSTS)"
else
    echo "   → .env déjà présent, pas de modification"
fi

# ── 5. Migrations et collectstatic ───────────────────────────
echo "📊 [5/7] Migrations Django..."
source "$VENV/bin/activate"
cd "$APP_DIR/backend"
python manage.py migrate --noinput
python manage.py collectstatic --noinput

echo "🌱 Initialisation des données de démo..."
python init_db.py || true   # Ne bloque pas si déjà initialisé

# ── 6. Service Gunicorn (systemd) ─────────────────────────────
echo "⚙️  [6/7] Configuration du service Gunicorn..."
mkdir -p /var/log/elearning

cat > /etc/systemd/system/elearning.service << 'SVCEOF'
[Unit]
Description=Reseau Academique Camerounais — Gunicorn
After=network.target postgresql.service

[Service]
User=www-data
Group=www-data
WorkingDirectory=/opt/cameroun_elearning/backend
Environment="DJANGO_SETTINGS_MODULE=config.settings"
ExecStart=/opt/cameroun_elearning/backend/venv/bin/gunicorn \
    --access-logfile /var/log/elearning/access.log \
    --error-logfile  /var/log/elearning/error.log \
    --workers 3 \
    --bind unix:/run/elearning.sock \
    --timeout 120 \
    config.wsgi:application
Restart=on-failure
RestartSec=5s

[Install]
WantedBy=multi-user.target
SVCEOF

chown -R www-data:www-data /var/log/elearning
systemctl daemon-reload
systemctl enable elearning
systemctl restart elearning
sleep 2
systemctl status elearning --no-pager

# ── 7. Configuration Nginx ────────────────────────────────────
echo "🌐 [7/7] Configuration Nginx..."
SERVER_IP=$(curl -s ifconfig.me)

cat > /etc/nginx/sites-available/elearning << NGINXEOF
server {
    listen 80;
    server_name $SERVER_IP _;

    # Compression gzip — économise la bande passante mobile
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css application/json
               application/javascript text/xml application/xml
               image/svg+xml;

    # Frontend statique (HTML, CSS, JS)
    root /opt/cameroun_elearning/frontend;
    index index.html;

    location / {
        try_files \$uri \$uri.html /index.html;
        expires 30d;
        add_header Cache-Control "public, must-revalidate";
    }

    # API Django — proxy vers Gunicorn
    location /api/ {
        include proxy_params;
        proxy_pass http://unix:/run/elearning.sock;
        proxy_read_timeout 120;
        client_max_body_size 310M;
    }

    location /admin/ {
        include proxy_params;
        proxy_pass http://unix:/run/elearning.sock;
    }

    # Fichiers statiques Django (admin, etc.)
    location /static/ {
        alias /opt/cameroun_elearning/backend/staticfiles/;
        expires 30d;
    }

    # Médias uploadés (vidéos, PDFs, avatars)
    location /media/ {
        alias /opt/cameroun_elearning/backend/media/;
        expires 7d;
        # Sécurité : pas d'exécution des fichiers uploadés
        location ~* \.(php|py|sh|cgi|pl)\$ { deny all; }
        # Limite débit vidéo — évite congestion réseau mobile
        location /media/videos/ {
            alias /opt/cameroun_elearning/backend/media/videos/;
            limit_rate 600k;
        }
    }

    access_log /var/log/nginx/elearning_access.log;
    error_log  /var/log/nginx/elearning_error.log;
}
NGINXEOF

# Activer le site
ln -sf /etc/nginx/sites-available/elearning /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t && systemctl reload nginx

echo ""
echo "✅ =============================================="
echo "   Déploiement terminé avec succès !"
echo ""
echo "   L'application est accessible sur :"
echo "   http://$SERVER_IP"
echo ""
echo "   API : http://$SERVER_IP/api/v1/"
echo "   Admin : http://$SERVER_IP/admin/"
echo "   Login admin : admin@elearning.cm / admin123"
echo ""
echo "   Étape suivante (optionnel) :"
echo "   bash add_domain.sh votre-domaine.cm"
echo "================================================"
