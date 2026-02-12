# 🖥️ Visualiser le navigateur avec VNC

Ce guide explique comment visualiser le navigateur Chrome en temps réel pendant le scraping Docker.

## 📋 Prérequis

Installer un client VNC sur votre machine :

### Windows
- **TightVNC Viewer** : https://www.tightvnc.com/download.php
- **RealVNC Viewer** : https://www.realvnc.com/fr/connect/download/viewer/

### macOS
- **RealVNC Viewer** : https://www.realvnc.com/fr/connect/download/viewer/
- Ou utiliser l'application native **Screen Sharing** (Finder > Go > Connect to Server > `vnc://localhost:5900`)

### Linux
```bash
sudo apt-get install tigervnc-viewer
# ou
sudo apt-get install remmina
```

## 🚀 Configuration

### 1. Modifier le fichier `.env`

```bash
# Activer le mode visible
HEADLESS=false

# Limiter le nombre de comptes pour tester (optionnel)
ACCOUNT_LIMIT=1
```

### 2. Reconstruire et lancer le container

```bash
# Arrêter le container actuel
docker-compose down

# Reconstruire l'image avec VNC
docker-compose build

# Lancer le container
docker-compose up -d

# Vérifier que VNC est démarré
docker-compose logs anef-scraper | grep VNC
```

Vous devriez voir :
```
🖥️ VNC Server démarré sur le port 5900
📺 Connectez-vous avec un client VNC à localhost:5900
```

## 🔌 Se connecter au VNC

### Avec TightVNC / RealVNC
1. Ouvrir le client VNC
2. Se connecter à : `localhost:5900`
3. Pas de mot de passe requis (appuyer sur Entrée)

### Avec macOS Screen Sharing
1. Finder > Go > Connect to Server (⌘K)
2. Entrer : `vnc://localhost:5900`
3. Cliquer sur "Connect"

## 👀 Que verrez-vous ?

- Un bureau virtuel avec le gestionnaire de fenêtres Fluxbox
- Le navigateur Chrome s'ouvrant automatiquement
- Les pages ANEF se chargeant en temps réel
- Les formulaires se remplissant automatiquement
- Les redirections et notifications

## 🛠️ Dépannage

### Le port 5900 est déjà utilisé
```bash
# Changer le port dans docker-compose.yml
ports:
  - "5901:5900"  # Utiliser 5901 au lieu de 5900
```

### L'écran VNC est noir
```bash
# Vérifier les logs
docker-compose logs -f anef-scraper

# Redémarrer le container
docker-compose restart anef-scraper
```

### Le navigateur ne s'affiche pas
Vérifier que `HEADLESS=false` dans le fichier `.env`

## 📊 Mode production vs développement

**Développement** (avec VNC) :
```bash
HEADLESS=false
ACCOUNT_LIMIT=1
```

**Production** (sans VNC, plus rapide) :
```bash
HEADLESS=true
ACCOUNT_LIMIT=all
```

## 🔒 Sécurité

⚠️ **Important** : Le serveur VNC n'a pas de mot de passe par défaut. Ne pas exposer le port 5900 sur Internet.

Pour un usage en production avec VNC, configurer un mot de passe :
```bash
# Dans start_vnc.sh, remplacer :
x11vnc -display :99 -forever -nopw -quiet -bg

# Par :
x11vnc -display :99 -forever -passwd VOTRE_MOT_DE_PASSE -quiet -bg
```
