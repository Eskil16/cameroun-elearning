#!/bin/bash
# ============================================================
# SCRIPT 3 — add_domain.sh
# Ajouter un nom de domaine + SSL Let's Encrypt gratuit
#
# Usage : bash add_domain.sh votre-domaine.cm
# ============================================================
set -e

DOMAIN=${1:-""}
if [ -z "$DOMAIN" ]; then
    echo "❌ Usage : bash add_domain.sh votre-domaine.cm"
    exit 1
fi

echo ""
echo "🌐 Configuration du domaine : $DOMAIN"
echo ""

# ── Mettre à jour .env avec le domaine ───────────────────────
ENV_FILE="/opt/cameroun_elearning/backend/.env"
SERVER_IP=$(curl -s ifconfig.me)

# Remplace ALLOWED_HOSTS
sed -i "s|ALLOWED_HOSTS=.*|ALLOWED_HOSTS=localhost,127.0.0.1,$SERVER_IP,$DOMAIN,www.$DOMAIN|" "$ENV_FILE"
sed -i "s|CORS_ALLOWED_ORIGINS=.*|CORS_ALLOWED_ORIGINS=https://$DOMAIN,https://www.$DOMAIN|" "$ENV_FILE"

# ── Mettre à jour la config Nginx ────────────────────────────
cat > /etc/nginx/sites-available/elearning << NGINXEOF
# Redirection HTTP → HTTPS
server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN;
    return 301 https://\$host\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name $DOMAIN www.$DOMAIN;

    # SSL (géré par Certbot)
    ssl_certificate     /etc/letsencrypt/live/$DOMAIN/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/$DOMAIN/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;

    # Compression
    gzip on;
    gzip_vary on;
    gzip_types text/plain text/css application/json application/javascript;

    root /opt/cameroun_elearning/frontend;
    index index.html;

    location / {
        try_files \$uri \$uri.html /index.html;
        expires 30d;
    }

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

    location /static/ {
        alias /opt/cameroun_elearning/backend/staticfiles/;
        expires 30d;
    }

    location /media/ {
        alias /opt/cameroun_elearning/backend/media/;
        expires 7d;
        location ~* \.(php|py|sh)\$ { deny all; }
        location /media/videos/ {
            alias /opt/cameroun_elearning/backend/media/videos/;
            limit_rate 600k;
        }
    }

    access_log /var/log/nginx/elearning_access.log;
    error_log  /var/log/nginx/elearning_error.log;
}
NGINXEOF

nginx -t && systemctl reload nginx

# ── Certificat SSL gratuit ────────────────────────────────────
echo "🔐 Obtention du certificat SSL Let's Encrypt..."
certbot --nginx -d "$DOMAIN" -d "www.$DOMAIN" --non-interactive --agree-tos \
    --email "admin@$DOMAIN" --redirect

# ── Redémarrer l'application ──────────────────────────────────
systemctl restart elearning

echo ""
echo "✅ Domaine configuré !"
echo "   https://$DOMAIN  →  Réseau Académique Camerounais"
echo "   Certificat SSL valide 90 jours (renouvellement automatique)"
echo ""
