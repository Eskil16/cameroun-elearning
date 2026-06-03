#!/bin/bash
# ============================================================
# SCRIPT LOCAL (Windows Git Bash / WSL / Mac/Linux)
# Uploade le projet sur le VPS via SCP
#
# Usage : bash upload_to_vps.sh IP_DU_VPS
# Exemple : bash upload_to_vps.sh 94.130.12.45
# ============================================================

VPS_IP=${1:-""}
if [ -z "$VPS_IP" ]; then
    echo "Usage : bash upload_to_vps.sh IP_DU_VPS"
    exit 1
fi

echo "📤 Upload du projet vers $VPS_IP..."

# Crée une archive du projet (sans .env, media/, venv/)
tar --exclude='./backend/venv' \
    --exclude='./backend/media' \
    --exclude='./backend/.env' \
    --exclude='./backend/staticfiles' \
    --exclude='.git' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    -czf /tmp/cameroun_elearning.tar.gz \
    -C "$(dirname "$0")/.." .

echo "📦 Archive créée : /tmp/cameroun_elearning.tar.gz"

# Upload vers le VPS
scp /tmp/cameroun_elearning.tar.gz root@$VPS_IP:/tmp/

# Extraction sur le VPS
ssh root@$VPS_IP "
    rm -rf /tmp/cameroun_elearning
    mkdir -p /tmp/cameroun_elearning
    tar -xzf /tmp/cameroun_elearning.tar.gz -C /tmp/cameroun_elearning
    echo 'Extraction terminée'
"

echo "✅ Projet uploadé sur $VPS_IP:/tmp/cameroun_elearning"
echo ""
echo "Maintenant, sur le VPS :"
echo "  cd /tmp/cameroun_elearning/deploy"
echo "  bash setup_server.sh    # (une seule fois)"
echo "  bash deploy_app.sh"
