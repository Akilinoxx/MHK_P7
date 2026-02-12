#!/bin/bash

# Démarrer Xvfb
Xvfb :99 -screen 0 1920x1080x24 -nolisten tcp -ac +extension GLX +render -noreset &
XVFB_PID=$!

# Attendre que Xvfb démarre
sleep 2

# Démarrer le gestionnaire de fenêtres
fluxbox &

# Démarrer x11vnc (sans mot de passe pour simplifier, accessible sur le port 5900)
x11vnc -display :99 -forever -nopw -quiet -bg

# Attendre que VNC démarre
sleep 1

echo "🖥️ VNC Server démarré sur le port 5900"
echo "📺 Connectez-vous avec un client VNC à localhost:5900"

# Lancer le script Python
python anef_login.py

# Garder le container actif si le script se termine
wait $XVFB_PID
