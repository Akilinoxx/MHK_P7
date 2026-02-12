#!/bin/bash

# Script pour exécuter le scraper ANEF
# Ce script arrête le container existant, le supprime, et le relance

set -e

PROJECT_DIR="/home/ubuntu/projects/MHK_P7"
CONTAINER_NAME="anef-scraper"
IMAGE_NAME="anef-scraper"

cd "$PROJECT_DIR"

echo "🔄 $(date): Démarrage du scraper ANEF..."

# Arrêter et supprimer le container s'il existe
if sudo docker ps -a | grep -q "$CONTAINER_NAME"; then
    echo "🛑 Arrêt du container existant..."
    sudo docker stop "$CONTAINER_NAME" || true
    sudo docker rm "$CONTAINER_NAME" || true
fi

# Lancer un nouveau container
echo "🚀 Lancement du container..."
sudo docker run -d \
  --name "$CONTAINER_NAME" \
  --env-file .env \
  -v "$(pwd)/TRUE CSV MHK - MHK_Avocats_Login_Cleaned - MHK - Feuille 1 (1)_FIXED_UPDATED.csv:/app/data/input.csv:ro" \
  -v "$(pwd)/results:/app/results" \
  "$IMAGE_NAME"

echo "✅ Container lancé avec succès!"

# Attendre que le container se termine (le script Python s'arrête tout seul)
echo "⏳ Attente de la fin du traitement..."
sudo docker wait "$CONTAINER_NAME"

# Afficher les logs finaux
echo "📋 Logs du traitement:"
sudo docker logs "$CONTAINER_NAME"

# Nettoyer le container
echo "🧹 Nettoyage du container..."
sudo docker rm "$CONTAINER_NAME"

echo "✅ $(date): Traitement terminé!"
