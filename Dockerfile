# Utiliser l'image officielle Playwright avec Python
FROM mcr.microsoft.com/playwright/python:v1.48.0-jammy

# Définir les locales et timezone français
ENV LANG=fr_FR.UTF-8 \
    LANGUAGE=fr_FR:fr \
    LC_ALL=fr_FR.UTF-8 \
    TZ=Europe/Paris \
    DEBIAN_FRONTEND=noninteractive

# Installer fonts et locales pour éviter la détection via canvas fingerprinting
RUN apt-get update && apt-get install -y \
    fonts-liberation \
    fonts-dejavu-core \
    fonts-noto-color-emoji \
    fonts-noto-cjk \
    fonts-freefont-ttf \
    fontconfig \
    locales \
    tzdata \
    && locale-gen fr_FR.UTF-8 \
    && ln -snf /usr/share/zoneinfo/$TZ /etc/localtime \
    && echo $TZ > /etc/timezone \
    && dpkg-reconfigure -f noninteractive tzdata \
    && fc-cache -f -v \
    && rm -rf /var/lib/apt/lists/*

# Définir le répertoire de travail
WORKDIR /app

# Copier les fichiers de dépendances
COPY requirements.txt .

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Installer les navigateurs Playwright (chromium pour crawl4ai)
RUN playwright install chromium
RUN playwright install-deps chromium

# Copier les fichiers du projet
COPY anef_login.py .
COPY clean_csv.py .
COPY fix_mobile_numbers.py .
COPY add_test_account.py .

# Variables d'environnement pour le webhook
ENV WEBHOOK_URL="https://n8n.wesype.com/webhook-test/4b437fa0-b785-4ccb-9621-e3c52984dd2e"

# L'image Playwright a déjà un utilisateur pwuser (UID 1000)
RUN chown -R pwuser:pwuser /app

# Créer le répertoire pour les résultats
RUN mkdir -p /app/results && chown -R pwuser:pwuser /app/results

USER pwuser

ENV LANGUAGE=fr_FR:fr \
    LANG=fr_FR.UTF-8

# Volume pour les fichiers CSV et résultats
VOLUME ["/app/data", "/app/results"]

# Lancer directement le script Python
CMD ["python", "anef_login.py"]
