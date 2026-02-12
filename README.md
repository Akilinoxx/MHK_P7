# MHK_P7 - ANEF Login Automation

Automatisation de la connexion et de la vérification des notifications sur la plateforme ANEF (Administration des Étrangers en France).

## 📋 Description

Ce projet automatise le processus de connexion à la plateforme ANEF pour plusieurs comptes, détecte les notifications et envoie des webhooks avec les résultats.

## 🚀 Fonctionnalités

- **Connexion automatisée** : Traitement en batch de plusieurs comptes depuis un fichier CSV
- **Détection des notifications** : Identification des nouvelles notifications sur les comptes
- **Webhooks** : Envoi automatique de notifications pour chaque compte traité
- **Gestion des erreurs** : Détection des identifiants incorrects et des mots de passe expirés
- **Rapports détaillés** : Génération de fichiers CSV avec les résultats

## 📦 Installation

### Option 1 : Installation locale

```bash
# Cloner le repository
git clone https://github.com/Akilinoxx/MHK_P7.git
cd MHK_P7

# Installer les dépendances
pip install -r requirements.txt
```

### Option 2 : Docker (recommandé)

```bash
# Cloner le repository
git clone https://github.com/Akilinoxx/MHK_P7.git
cd MHK_P7

# Créer le fichier .env à partir de l'exemple
cp .env.example .env

# Modifier l'URL du webhook dans .env si nécessaire
# WEBHOOK_URL=https://votre-webhook-url.com

# Créer le dossier results
mkdir results

# Construire et lancer le container
docker-compose up -d

# Voir les logs
docker-compose logs -f
```

## 🔧 Configuration

1. Préparer votre fichier CSV avec les colonnes suivantes :
   - `Identifiant` : Identifiant ANEF
   - `Mot_de_passe` : Mot de passe ANEF
   - `웃 Client Name` : Nom du client
   - `Email` : Adresse email
   - `Mobile` : Numéro de téléphone (format 06/07)

2. Configurer l'URL du webhook dans `anef_login.py` :
```python
WEBHOOK_URL = "https://votre-webhook-url.com"
```

## 📊 Utilisation

### Mode local

#### Mode batch (traitement CSV)
```bash
python anef_login.py
```

#### Mode test (compte unique)
```bash
python anef_login.py <identifiant> <mot_de_passe>
```

### Mode Docker

#### Lancer le scraping
```bash
# Démarrer le container
docker-compose up -d

# Suivre les logs en temps réel
docker-compose logs -f anef-scraper

# Arrêter le container
docker-compose down
```

#### Récupérer les résultats
Les fichiers de résultats sont automatiquement sauvegardés dans le dossier `./results/` :
- `*_UPDATED.csv` : CSV mis à jour avec les erreurs dans la colonne G
- `anef_login_results.csv` : Rapport détaillé de tous les comptes traités

#### Commandes Docker utiles
```bash
# Reconstruire l'image après modification du code
docker-compose build

# Voir les logs
docker-compose logs -f

# Entrer dans le container
docker-compose exec anef-scraper bash

# Nettoyer les containers et images
docker-compose down --rmi all
```

## 📤 Cas de webhooks

Le script envoie un webhook pour chaque compte avec les cas suivants :

1. **Aucune notification** : Connexion réussie, pas de notification
2. **Nouvelle notification** : Connexion réussie avec notification détectée
3. **Identifiants incorrects** : Échec de connexion
4. **Réinitialisation mot de passe requise** : Mot de passe expiré

## 📁 Structure du projet

```
MHK_P7/
├── anef_login.py           # Script principal
├── clean_csv.py            # Nettoyage des données CSV
├── fix_mobile_numbers.py   # Formatage des numéros de téléphone
├── add_test_account.py     # Ajout de comptes de test
├── requirements.txt        # Dépendances Python
└── README.md              # Documentation
```

## 🛠️ Technologies utilisées

- **Python 3.11+**
- **crawl4ai** : Automatisation web
- **pandas** : Manipulation de données
- **requests** : Envoi de webhooks

## ⚠️ Notes importantes

- Les fichiers CSV avec données sensibles sont exclus du repository (voir `.gitignore`)
- Le navigateur peut être configuré en mode headless ou visible
- Les délais d'attente sont optimisés pour la stabilité

## 📝 License

Ce projet est privé et destiné à un usage interne.
