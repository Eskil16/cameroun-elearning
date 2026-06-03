# 🚀 Guide de Déploiement — VPS Faible Coût (Cameroun)

Déploiement sur un VPS Ubuntu 22.04 avec Gunicorn + Nginx.
Optimisé pour les connexions mobiles camerounaises (4G/3G, MTN, Orange, Nexttel).

---

## 📋 Prérequis VPS

- Ubuntu 22.04 LTS (recommandé : VPS 2 vCPU / 2 Go RAM / 20 Go SSD)
- Accès root ou sudo
- Nom de domaine (optionnel — on peut utiliser l'IP du VPS)

Hébergeurs recommandés pour le Cameroun :
- **Contabo** (EU, ~4€/mois) — bon rapport qualité/prix
- **DigitalOcean** (5$/mois, Droplet)
- **Scaleway** (EU, 3€/mois)
- **Hetzner** (EU, 3€/mois)

---

## 1. Mise à jour et dépendances système

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3.11 python3.11-venv python3-pip \
    postgresql postgresql-contrib nginx certbot python3-certbot-nginx \
    git ffmpeg libmagic1
```

---

## 2. Base de données PostgreSQL

```bash
sudo -u postgres psql
```

```sql
CREATE DATABASE cameroun_elearning;
CREATE USER elearning_user WITH PASSWORD 'MotDePasseTresSecret123!';
ALTER ROLE elearning_user SET client_encoding TO 'utf8';
ALTER ROLE elearning_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE elearning_user SET timezone TO 'Africa/Douala';
GRANT ALL PRIVILEGES ON DATABASE cameroun_elearning TO elearning_user;
\q
```

---

## 3. Déploiement du code

```bash
cd /opt
sudo git clone https://github.com/votre-repo/cameroun_elearning.git
sudo chown -R $USER:$USER /opt/cameroun_elearning
cd /opt/cameroun_elearning/backend

python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install gunicorn
```

### Fichier .env de production

```bash
nano /opt/cameroun_elearning/backend/.env
```

```ini
SECRET_KEY=cle-secrete-tres-longue-generee-avec-python-secrets
DEBUG=False
ALLOWED_HOSTS=votre-domaine.cm,www.votre-domaine.cm,IP.DU.VPS

DB_NAME=cameroun_elearning
DB_USER=elearning_user
DB_PASSWORD=MotDePasseTresSecret123!
DB_HOST=localhost
DB_PORT=5432

EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=votre@email.cm
EMAIL_HOST_PASSWORD=votre-mot-de-passe-application
DEFAULT_FROM_EMAIL=noreply@votre-domaine.cm

CORS_ALLOWED_ORIGINS=https://votre-domaine.cm,https://www.votre-domaine.cm
```

### Migrations et initialisation

```bash
source venv/bin/activate
python manage.py migrate
python manage.py collectstatic --noinput
python init_db.py
```

---

## 4. Service Gunicorn (systemd)

```bash
sudo nano /etc/systemd/system/elearning.service
```

```ini
[Unit]
Description=Réseau Académique Camerounais — Gunicorn
After=network.target

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
```

```bash
sudo mkdir -p /var/log/elearning
sudo chown www-data:www-data /var/log/elearning
sudo chown -R www-data:www-data /opt/cameroun_elearning

sudo systemctl daemon-reload
sudo systemctl enable elearning
sudo systemctl start elearning
sudo systemctl status elearning
```

---

## 5. Configuration Nginx

```bash
sudo nano /etc/nginx/sites-available/elearning
```

```nginx
# Redirection HTTP → HTTPS
server {
    listen 80;
    server_name votre-domaine.cm www.votre-domaine.cm;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name votre-domaine.cm www.votre-domaine.cm;

    # SSL (géré par Certbot)
    ssl_certificate     /etc/letsencrypt/live/votre-domaine.cm/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/votre-domaine.cm/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;

    # Optimisation mobile / bande passante
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css application/json application/javascript
               text/xml application/xml image/svg+xml;

    # Cache navigateur
    location ~* \.(css|js|jpg|jpeg|png|gif|ico|woff2|svg)$ {
        expires 30d;
        add_header Cache-Control "public, immutable";
        root /opt/cameroun_elearning/frontend;
    }

    # Frontend statique
    location / {
        root /opt/cameroun_elearning/frontend;
        try_files $uri $uri.html /index.html;
    }

    # API Django
    location /api/ {
        include proxy_params;
        proxy_pass http://unix:/run/elearning.sock;
        proxy_read_timeout 120;
        client_max_body_size 310M;  # 300 Mo vidéo + marge
    }

    # Admin Django
    location /admin/ {
        include proxy_params;
        proxy_pass http://unix:/run/elearning.sock;
    }

    # Fichiers statiques Django
    location /static/ {
        alias /opt/cameroun_elearning/backend/staticfiles/;
        expires 30d;
    }

    # Uploads médias
    location /media/ {
        alias /opt/cameroun_elearning/backend/media/;
        expires 7d;
        # Sécurité : ne pas exécuter les fichiers uploadés
        location ~* \.(php|py|sh|cgi)$ { deny all; }
    }

    # Logs
    access_log /var/log/nginx/elearning_access.log;
    error_log  /var/log/nginx/elearning_error.log;
}
```

```bash
sudo ln -s /etc/nginx/sites-available/elearning /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

---

## 6. SSL gratuit avec Let's Encrypt

```bash
sudo certbot --nginx -d votre-domaine.cm -d www.votre-domaine.cm
# Renouvellement automatique
sudo systemctl enable certbot.timer
```

---

## 7. Firewall

```bash
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'
sudo ufw enable
sudo ufw status
```

---

## 8. Optimisation pour mobile 4G/3G

### Compression vidéo automatique (FFmpeg)

Pour compresser les vidéos uploadées en 360p :

```bash
# Script à exécuter après chaque upload (ou en tâche cron)
cat > /opt/compress_video.sh << 'EOF'
#!/bin/bash
INPUT="$1"
OUTPUT="${INPUT%.mp4}_360p.mp4"
ffmpeg -i "$INPUT" \
    -vf scale=640:360 \
    -c:v libx264 -crf 28 -preset fast \
    -c:a aac -b:a 64k \
    -movflags +faststart \
    "$OUTPUT"
echo "Compressé : $OUTPUT"
EOF
chmod +x /opt/compress_video.sh
```

### Paramètres Nginx pour mobile lent

Ajoutez dans le bloc `server` Nginx :

```nginx
# Optimisation pour connexions lentes
tcp_nopush on;
tcp_nodelay on;
sendfile on;
keepalive_timeout 65;

# Limiter le débit d'envoi des fichiers vidéo (évite congestion)
location /media/videos/ {
    alias /opt/cameroun_elearning/backend/media/videos/;
    limit_rate 500k;  # 500 Ko/s max par connexion
}
```

---

## 9. Maintenance et mise à jour

### Mettre à jour l'application

```bash
cd /opt/cameroun_elearning
git pull origin main

cd backend
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput

sudo systemctl restart elearning
sudo systemctl reload nginx
```

### Sauvegarde automatique de la BDD (cron)

```bash
sudo nano /etc/cron.d/elearning-backup
```

```cron
# Sauvegarde quotidienne à 2h du matin (heure Douala)
0 2 * * * postgres pg_dump cameroun_elearning | gzip > /var/backups/elearning_$(date +\%Y\%m\%d).sql.gz
# Garder 7 jours de sauvegardes
0 3 * * * find /var/backups/ -name "elearning_*.sql.gz" -mtime +7 -delete
```

### Surveiller les logs

```bash
# Logs Gunicorn
sudo journalctl -u elearning -f

# Logs d'accès Nginx
sudo tail -f /var/log/nginx/elearning_access.log

# Logs d'erreur Gunicorn
sudo tail -f /var/log/elearning/error.log
```

---

## 10. Checklist avant mise en production

- [ ] `DEBUG=False` dans `.env`
- [ ] `SECRET_KEY` longue et aléatoire (générez avec : `python -c "import secrets; print(secrets.token_urlsafe(50))"`)
- [ ] SSL Let's Encrypt activé
- [ ] `ALLOWED_HOSTS` configuré avec votre domaine
- [ ] Sauvegarde automatique configurée
- [ ] `python manage.py check --deploy` sans erreurs critiques
- [ ] Email SMTP configuré (vérification des comptes)
- [ ] `media/` hors de la racine Git (`.gitignore`)
- [ ] Firewall UFW activé
- [ ] Rotation des logs Nginx configurée

---

## 📊 Performances attendues

| Métrique | Valeur cible |
|----------|--------------|
| Charge page index (3G) | < 3 secondes |
| Taille page index (gzip) | < 150 Ko |
| Module "faible bande passante" | < 50 Mo |
| Compression vidéo 360p | ~80% de réduction |
| Cache statiques | 30 jours |
| Utilisateurs simultanés (VPS 2 Go) | 50-100 |

---

## 🆘 Support

- Interface admin Django : `https://votre-domaine.cm/admin/`
- Logs : `/var/log/elearning/` et `/var/log/nginx/`
- Redémarrer Gunicorn : `sudo systemctl restart elearning`
- Reload Nginx (sans interruption) : `sudo systemctl reload nginx`
