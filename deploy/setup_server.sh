#!/bin/bash
# ============================================================
# SCRIPT 1 — setup_server.sh
# Installation complète du serveur VPS (Ubuntu 22.04)
# Exécuter en root UNE SEULE FOIS après réception du VPS
#
# Usage : bash setup_server.sh
# ============================================================
set -e  # Arrête si une commande échoue

echo ""
echo "🇨🇲 =============================================="
echo "   Réseau Académique Camerounais — Setup VPS"
echo "================================================"
echo ""

# ── 1. Mise à jour système ────────────────────────────────────
echo "📦 [1/8] Mise à jour du système..."
apt update && apt upgrade -y
apt install -y curl wget git unzip software-properties-common

# ── 2. Python 3.11 ───────────────────────────────────────────
echo "🐍 [2/8] Installation de Python 3.11..."
add-apt-repository ppa:deadsnakes/ppa -y
apt update
apt install -y python3.11 python3.11-venv python3.11-dev python3-pip

# ── 3. PostgreSQL ─────────────────────────────────────────────
echo "🐘 [3/8] Installation de PostgreSQL 14..."
apt install -y postgresql postgresql-contrib
systemctl enable postgresql
systemctl start postgresql

# ── 4. Nginx ─────────────────────────────────────────────────
echo "🌐 [4/8] Installation de Nginx..."
apt install -y nginx
systemctl enable nginx

# ── 5. Certbot (SSL Let's Encrypt) ───────────────────────────
echo "🔐 [5/8] Installation de Certbot..."
apt install -y certbot python3-certbot-nginx

# ── 6. FFmpeg (compression vidéo) ────────────────────────────
echo "🎬 [6/8] Installation de FFmpeg..."
apt install -y ffmpeg libmagic1

# ── 7. Firewall UFW ──────────────────────────────────────────
echo "🛡️  [7/8] Configuration du firewall..."
ufw --force enable
ufw allow OpenSSH
ufw allow 'Nginx Full'
ufw status

# ── 8. Créer la base de données PostgreSQL ───────────────────
echo "🗄️  [8/8] Création de la base de données..."
sudo -u postgres psql << 'EOSQL'
CREATE DATABASE cameroun_elearning;
CREATE USER elearning_user WITH PASSWORD 'EL3arning_Cam237!';
ALTER ROLE elearning_user SET client_encoding TO 'utf8';
ALTER ROLE elearning_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE elearning_user SET timezone TO 'Africa/Douala';
GRANT ALL PRIVILEGES ON DATABASE cameroun_elearning TO elearning_user;
\q
EOSQL

echo ""
echo "✅ Serveur configuré avec succès !"
echo ""
echo "Prochaine étape : bash deploy_app.sh"
echo "================================================"
