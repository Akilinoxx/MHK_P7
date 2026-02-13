# -*- coding: utf-8 -*-
import asyncio
import json
import os
import sys
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig
from typing import Optional, Dict
import pandas as pd
import requests

# Configurer l'encodage UTF-8 pour la console Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# URL du webhook (peut être surchargée par variable d'environnement)
WEBHOOK_URL = os.getenv('WEBHOOK_URL', "https://n8n.wesype.com/webhook/4b437fa0-b785-4ccb-9621-e3c52984dd2e")

def send_webhook_notification(client_name: str, username: str, password: str, email: str, mobile: str, case: str, notification_type: str = ""):
    """
    Envoie une notification webhook pour chaque compte traité.
    
    Args:
        client_name: Nom du client
        username: Identifiant ANEF
        password: Mot de passe ANEF
        email: Adresse email
        mobile: Numéro de téléphone
        case: Type de cas ("Aucune notification", "Nouvelle notification", "Identifiants incorrects")
        notification_type: Type de notification si applicable
    """
    try:
        payload = {
            "client_name": client_name,
            "username": username,
            "password": password,
            "email": email,
            "mobile": mobile,
            "case": case,
            "notification_type": notification_type
        }
        
        print(f"  🔗 Webhook URL: {WEBHOOK_URL}")
        response = requests.post(WEBHOOK_URL, json=payload, timeout=10)
        
        if response.status_code == 200:
            print(f"  📤 Webhook envoyé: {case}")
        else:
            print(f"  ⚠️ Webhook erreur {response.status_code}")
            print(f"  📄 Réponse: {response.text[:200]}")
            
    except Exception as e:
        print(f"  ❌ Erreur webhook: {e}")

class ANEFConnector:
    """
    Connecteur pour la plateforme ANEF utilisant Crawl4AI.
    """
    
    def __init__(self, headless: bool = True, keep_browser_open: bool = False):
        """
        Initialise le connecteur ANEF.
        
        Args:
            headless: Si True, le navigateur s'exécute en mode invisible
            keep_browser_open: Si True, garde le navigateur ouvert après connexion
        """
        self.home_url = "https://administration-etrangers-en-france.interieur.gouv.fr/particuliers/#/"
        self.login_url = "https://sso.anef.dgef.interieur.gouv.fr/auth/realms/anef-usagers/protocol/openid-connect/auth?client_id=anef-usagers&theme=portail-anef&redirect_uri=https%3A%2F%2Fadministration-etrangers-en-france.interieur.gouv.fr%2Fparticuliers%2F%23&response_mode=fragment&response_type=code&scope=openid"
        self.headless = headless
        self.keep_browser_open = keep_browser_open
        
    async def login(self, username: str, password: str, session_id: str = "anef_session") -> Dict:
        """
        Se connecte à la plateforme ANEF avec les identifiants fournis.
        
        Args:
            username: Identifiant ANEF
            password: Mot de passe ANEF
            session_id: ID de session pour maintenir la connexion
            
        Returns:
            Dict contenant le résultat de la connexion
        """
        browser_config = BrowserConfig(
            headless=self.headless,
            viewport_width=1920,
            viewport_height=1080,
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            headers={
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
                "Accept-Language": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7",
                "Accept-Encoding": "gzip, deflate, br",
                "DNT": "1",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "none",
                "Sec-Fetch-User": "?1",
                "Cache-Control": "max-age=0"
            },
            extra_args=[
                "--disable-blink-features=AutomationControlled",
                "--disable-dev-shm-usage",
                "--no-sandbox"
            ]
        )
        
        async with AsyncWebCrawler(config=browser_config) as crawler:
            print(f"🔐 Accès direct à la page de connexion SSO...")
            
            # JavaScript pour masquer l'automatisation et remplir le formulaire
            login_js = f"""
            // Masquer les traces d'automatisation
            Object.defineProperty(navigator, 'webdriver', {{
                get: () => undefined
            }});
            
            // Ajouter des propriétés manquantes pour ressembler à un vrai navigateur
            window.chrome = {{
                runtime: {{}}
            }};
            
            Object.defineProperty(navigator, 'plugins', {{
                get: () => [1, 2, 3, 4, 5]
            }});
            
            Object.defineProperty(navigator, 'languages', {{
                get: () => ['fr-FR', 'fr', 'en-US', 'en']
            }});
            
            const waitForElement = (selector, timeout = 10000) => {{
                return new Promise((resolve, reject) => {{
                    const startTime = Date.now();
                    const checkElement = () => {{
                        const element = document.querySelector(selector);
                        if (element) {{
                            resolve(element);
                        }} else if (Date.now() - startTime > timeout) {{
                            reject(new Error(`Element ${{selector}} not found`));
                        }} else {{
                            setTimeout(checkElement, 100);
                        }}
                    }};
                    checkElement();
                }});
            }};
            
            try {{
                console.log('🔍 Recherche des champs du formulaire...');
                
                // Attendre les champs du formulaire
                const usernameField = await waitForElement('input[name="username"]');
                const passwordField = await waitForElement('input[name="password"]');
                const submitButton = await waitForElement('button[type="submit"]');
                
                console.log('✅ Champs trouvés');
                
                // Simuler une saisie humaine avec délais
                await new Promise(resolve => setTimeout(resolve, 300 + Math.random() * 200));
                
                // Remplir le champ username caractère par caractère (simulation)
                usernameField.focus();
                usernameField.value = '{username}';
                usernameField.dispatchEvent(new Event('input', {{ bubbles: true }}));
                usernameField.dispatchEvent(new Event('change', {{ bubbles: true }}));
                
                console.log('✅ Identifiant: {username}');
                
                // Délai entre les champs
                await new Promise(resolve => setTimeout(resolve, 400 + Math.random() * 300));
                
                // Remplir le champ password
                passwordField.focus();
                passwordField.value = '{password}';
                passwordField.dispatchEvent(new Event('input', {{ bubbles: true }}));
                passwordField.dispatchEvent(new Event('change', {{ bubbles: true }}));
                
                console.log('✅ Mot de passe: ***');
                
                // Attendre avant de soumettre (comme un humain qui vérifie)
                await new Promise(resolve => setTimeout(resolve, 800 + Math.random() * 400));
                
                console.log('🚀 Soumission du formulaire...');
                
                // Soumettre
                submitButton.click();
                
                console.log('✅ Formulaire soumis!');

                // Attendre que la soumission soit envoyée et la redirection commence
                await new Promise(resolve => setTimeout(resolve, 5000));

                console.log('✅ Formulaire soumis, en attente de redirection...');
                return 'submitted';
                
            }} catch (error) {{
                console.error('❌ Erreur:', error.message);
            }}
            """
            
            # Étape 1 : Naviguer vers la page SSO et soumettre le formulaire
            login_config = CrawlerRunConfig(
                session_id=session_id,
                page_timeout=20000,
                js_code=login_js,
                screenshot=False,
                remove_overlay_elements=False,
                # js_only=False (défaut) : navigation complète vers l'URL SSO
            )

            result = await crawler.arun(
                url=self.login_url,
                config=login_config
            )

            print(f"📍 Étape 1 terminée (soumission formulaire)")

            import re

            result_html = result.html or ""

            # Vérifier si UPDATE_PASSWORD est déjà visible après la soumission
            if "UPDATE_PASSWORD" in result_html or "required-action" in result_html or "Réinitialisez votre mot de passe" in result_html:
                print("🔍 Détection UPDATE_PASSWORD après soumission")
                final_html = result_html
                login_success = False
                is_update_password = True
                login_error = False
            # Vérifier si le SSO affiche une erreur d'identifiants
            elif "fr-alert--error" in result_html or "mot de passe invalide" in result_html.lower() or "invalid" in result_html.lower():
                print("❌ Erreur d'identifiants détectée après soumission")
                final_html = result_html
                login_success = False
                is_update_password = False
                login_error = True
            else:
                # Étape 2 : Naviguer vers le dashboard dans la même session
                # Si le login a réussi, les cookies sont en place et on arrivera sur le dashboard
                # Sinon, on sera redirigé vers le SSO
                print("🔄 Étape 2: Navigation vers le dashboard...")

                dashboard_config = CrawlerRunConfig(
                    session_id=session_id,
                    page_timeout=40000,
                    screenshot=False,
                    remove_overlay_elements=False,
                    delay_before_return_html=5.0,  # Attendre 5s que la SPA se charge complètement
                )

                dashboard_result = await crawler.arun(
                    url=self.home_url,
                    config=dashboard_config
                )

                final_html = dashboard_result.html or ""
                is_update_password = False
                login_error = False

                # Déterminer si on est sur le dashboard en analysant le contenu HTML

                # Indicateurs positifs : éléments spécifiques au dashboard ANEF (cherchés dans le HTML brut, pas en minuscules)
                dashboard_indicators = {
                    "notification-table": "tableau notifications",
                    "fa-bell": "icône cloche",
                    "tableau-de-bord": "titre dashboard",
                    "mes-dossiers": "section dossiers",
                }

                # Indicateurs négatifs : on est sur la page de login SSO ou erreur
                login_indicators = {
                    'name="username"': "champ username",
                    'name="password"': "champ password",
                    "kc-login": "classe Keycloak",
                    "kc-form-login": "formulaire Keycloak",
                    "fr-alert--error": "alerte erreur SSO",
                    "mot de passe invalide": "erreur identifiants",
                    "mot de passe oubli": "lien mdp oublié",
                }

                matched_dashboard = [desc for ind, desc in dashboard_indicators.items() if ind in final_html]
                matched_login = [desc for ind, desc in login_indicators.items() if ind in final_html.lower()]

                has_dashboard = len(matched_dashboard) > 0
                has_login_form = len(matched_login) > 0

                login_success = has_dashboard and not has_login_form

                if login_success:
                    print(f"✅ Dashboard détecté via: {', '.join(matched_dashboard)}")
                elif has_login_form:
                    print(f"❌ Page de login SSO détectée via: {', '.join(matched_login)}")
                    login_error = True
                else:
                    print(f"⚠️ Page non identifiée, HTML length={len(final_html)}")
                    print(f"   Premiers 500 chars: {final_html[:500]}")

                # Vérifier aussi UPDATE_PASSWORD dans le HTML du dashboard
                if "UPDATE_PASSWORD" in final_html or "required-action" in final_html or "Réinitialisez votre mot de passe" in final_html:
                    print("🔍 Détection UPDATE_PASSWORD dans le HTML")
                    is_update_password = True
                    login_success = False

            # Construire la réponse
            response = {
                "success": False,
                "username": username,
                "url": self.home_url if login_success else self.login_url,
                "session_id": session_id,
                "screenshot": None,
                "message": "",
                "crawler": crawler if self.keep_browser_open else None
            }

            if is_update_password:
                response["success"] = False
                response["notifications"] = "UPDATE_PASSWORD"
                response["message"] = "⚠️ Mise à jour du mot de passe requise"
                print(f"⚠️ UPDATE_PASSWORD requis pour {username}")
            elif login_error:
                response["success"] = False
                response["notifications"] = "N/A"
                response["message"] = "❌ Erreur de connexion - Identifiants incorrects"
                print(f"❌ Identifiants incorrects pour {username}")
            elif login_success:
                response["success"] = True
                response["message"] = "✅ Connexion réussie!"
                print(f"✅ Connexion réussie pour {username}")

                # Vérifier les notifications dans le tableau notification-table
                response["notifications"] = "NON"
                response["type_notification"] = ""

                # Extraire le contenu du tableau notification-table
                table_match = re.search(
                    r'<table[^>]*class="notification-table[^"]*"[^>]*>(.*?)</table>',
                    final_html, re.DOTALL | re.IGNORECASE
                )

                if table_match:
                    table_html = table_match.group(1)
                    # Chercher les lignes avec ui-icon-not-read (enveloppe non lue)
                    if "ui-icon-not-read" in table_html or "ui-msg-not-read" in table_html:
                        response["notifications"] = "OUI"

                        # Extraire le type de notification depuis <span class="ui-msg-not-read">
                        notif_pattern = r'<span[^>]*class="ui-msg-not-read"[^>]*>\s*(.*?)\s*</span>'
                        matches = re.findall(notif_pattern, table_html, re.DOTALL | re.IGNORECASE)
                        if matches:
                            notif_types = [re.sub(r'\s+', ' ', m.strip()) for m in matches if m.strip()]
                            response["type_notification"] = notif_types[0] if notif_types else ""

                print(f"🔔 Notifications: {response['notifications']}")
                if response.get("type_notification"):
                    print(f"   Type: {response['type_notification']}")
            else:
                response["success"] = False
                response["notifications"] = "N/A"

                if "error" in final_html.lower() or "erreur" in final_html.lower():
                    response["message"] = "❌ Erreur de connexion - Identifiants incorrects"
                    print(f"❌ Identifiants incorrects pour {username}")
                elif "maintenance" in final_html.lower():
                    response["message"] = "❌ Page de maintenance - Site indisponible"
                    print(f"❌ Page de maintenance pour {username}")
                else:
                    response["message"] = "❌ Dashboard non atteint - Vérifier manuellement"
                    print(f"❌ Dashboard non atteint pour {username}")
            
            # Screenshots désactivés pour accélérer le traitement
            response["screenshot_path"] = None
            
            # Attendre AVANT de fermer le crawler pour laisser le navigateur visible
            if not self.headless and not self.keep_browser_open:
                print("⏳ Attente de 4 secondes avant passage au compte suivant...")
                await asyncio.sleep(4)
            
            # Si keep_browser_open est activé, attendre avant de fermer
            if self.keep_browser_open:
                print("\n" + "="*60)
                print("🌐 NAVIGATEUR OUVERT - Vous pouvez observer la page")
                print("="*60)
                print("Appuyez sur Entrée pour fermer le navigateur...")
                input()
            
            return response
    
    async def get_dashboard_info(self, session_id: str = "anef_session") -> Dict:
        """
        Récupère les informations du tableau de bord après connexion.
        
        Args:
            session_id: ID de session établi lors de la connexion
            
        Returns:
            Dict contenant les informations du tableau de bord
        """
        dashboard_url = "https://administration-etrangers-en-france.interieur.gouv.fr/particuliers/"
        
        browser_config = BrowserConfig(
            headless=self.headless,
            viewport_width=1920,
            viewport_height=1080
        )
        
        crawler_config = CrawlerRunConfig(
            session_id=session_id,
            page_timeout=30000,
            screenshot=True,
            wait_for="css:body"
        )
        
        async with AsyncWebCrawler(config=browser_config) as crawler:
            result = await crawler.arun(
                url=dashboard_url,
                config=crawler_config
            )
            
            return {
                "success": result.success,
                "url": result.url,
                "title": result.metadata.get("title", ""),
                "markdown": result.markdown[:1000],  # Premiers 1000 caractères
                "screenshot": result.screenshot
            }


async def test_single_login(username: str, password: str, headless: bool = False):
    """
    Test de connexion pour un seul compte.
    
    Args:
        username: Identifiant ANEF
        password: Mot de passe ANEF
        headless: Mode sans interface graphique
    """
    connector = ANEFConnector(headless=headless, keep_browser_open=True)
    
    # Tentative de connexion
    result = await connector.login(username, password)
    
    print("\n" + "="*60)
    print("RÉSULTAT DE LA CONNEXION")
    print("="*60)
    print(f"Username: {result['username']}")
    print(f"Success: {result['success']}")
    print(f"Message: {result['message']}")
    if "screenshot_path" in result:
        print(f"Screenshot: {result['screenshot_path']}")
    print("="*60)
    
    return result


async def batch_login_from_csv(csv_path: str, headless: bool = True, max_concurrent: int = 1, limit: int = None):
    """
    Connexion en batch à partir du fichier CSV nettoyé (traitement séquentiel).
    Mettre à jour la colonne G (Commentaire robot) en cas d'erreur.
    
    Args:
        csv_path: Chemin vers le fichier CSV
        headless: Mode sans interface graphique
        max_concurrent: Non utilisé (traitement séquentiel)
        limit: Nombre maximum de comptes à traiter (None = tous)
    """
    # Charger le CSV
    df = pd.read_csv(csv_path, encoding='utf-8')
    
    # Convertir la colonne 'Commentaire robot' en type string pour éviter les erreurs de dtype
    if 'Commentaire robot' in df.columns:
        df['Commentaire robot'] = df['Commentaire robot'].astype(str)
        # Remplacer 'nan' par chaîne vide
        df['Commentaire robot'] = df['Commentaire robot'].replace('nan', '')
    
    # Filtrer les lignes avec identifiant ET mot de passe
    df_valid = df[(df['Identifiant'].notna()) & (df['Mot_de_passe'].notna())].copy()
    
    # Limiter le nombre de comptes si spécifié
    if limit:
        df_valid = df_valid.head(limit)
    
    print(f"📊 {len(df_valid)} comptes à traiter sur {len(df)} lignes totales")
    print(f"🚀 Démarrage des connexions (traitement séquentiel)...\n")
    
    connector = ANEFConnector(headless=headless)
    results = []
    
    # Traiter compte par compte
    for idx, row in df_valid.iterrows():
        username = str(row['Identifiant'])
        password = str(row['Mot_de_passe'])
        client_name = row['웃 Client Name']
        email = str(row.get('Email', '')) if pd.notna(row.get('Email')) else ''
        mobile = str(row.get('Mobile', '')) if pd.notna(row.get('Mobile')) else ''
        
        print(f"\n[{idx+1}/{len(df_valid)}] Traitement de {client_name}...")
        
        session_id = f"anef_session_{idx}"
        result = await connector.login(username, password, session_id)
        
        # Ajouter les infos du client
        result['client_name'] = client_name
        result['row_index'] = idx
        
        # Mettre à jour la colonne G (Commentaire robot) en cas d'erreur
        if not result['success']:
            df.loc[idx, 'Commentaire robot'] = result['message']
        else:
            # Effacer le commentaire si la connexion réussit
            df.loc[idx, 'Commentaire robot'] = ''
        
        results.append(result)
        
        # Envoyer le webhook selon le cas
        if result.get('notifications') == 'UPDATE_PASSWORD':
            # CAS 4: Réinitialisation du mot de passe requise
            send_webhook_notification(
                client_name=client_name,
                username=username,
                password=password,
                email=email,
                mobile=mobile,
                case="Réinitialisation mot de passe requise"
            )
        elif not result['success']:
            # CAS 3: Identifiants incorrects
            send_webhook_notification(
                client_name=client_name,
                username=username,
                password=password,
                email=email,
                mobile=mobile,
                case="Identifiants incorrects"
            )
        elif result.get('notifications') == 'OUI':
            # CAS 2: Nouvelle notification
            send_webhook_notification(
                client_name=client_name,
                username=username,
                password=password,
                email=email,
                mobile=mobile,
                case="Nouvelle notification",
                notification_type=result.get('type_notification', '')
            )
        elif result.get('notifications') == 'NON':
            # CAS 1: Aucune notification
            send_webhook_notification(
                client_name=client_name,
                username=username,
                password=password,
                email=email,
                mobile=mobile,
                case="Aucune notification"
            )
        
        # Pause entre les connexions pour éviter les blocages
        if idx < len(df_valid) - 1:
            await asyncio.sleep(2)  # 2 secondes entre chaque connexion
    
    # Résumé des résultats
    print("\n" + "="*60)
    print("RÉSUMÉ DES CONNEXIONS")
    print("="*60)
    
    successful = [r for r in results if r['success']]
    failed = [r for r in results if not r['success']]
    
    print(f"✅ Réussies: {len(successful)}/{len(results)}")
    print(f"❌ Échouées: {len(failed)}/{len(results)}")
    
    if failed:
        print("\n❌ Échecs:")
        for r in failed:
            print(f"  - {r['client_name']} ({r['username']}): {r['message']}")
    
    # Sauvegarder le CSV original avec la colonne G mise à jour dans /app/results/
    import os
    results_dir = "/app/results" if os.path.exists("/app/results") else "results"
    os.makedirs(results_dir, exist_ok=True)
    
    csv_filename = os.path.basename(csv_path).replace('.csv', '_UPDATED.csv')
    updated_csv_path = os.path.join(results_dir, csv_filename)
    df.to_csv(updated_csv_path, index=False, encoding='utf-8')
    print(f"\n💾 CSV mis à jour sauvegardé dans: {updated_csv_path}")
    print(f"   → Colonne G (Commentaire robot) mise à jour avec les erreurs")
    
    # Sauvegarder aussi un rapport détaillé dans /app/results/
    results_df = pd.DataFrame(results)
    # Sélectionner les colonnes importantes pour le rapport
    columns_to_save = ['client_name', 'username', 'success', 'notifications', 'type_notification', 'message', 'screenshot_path']
    results_df = results_df[[col for col in columns_to_save if col in results_df.columns]]
    
    results_path = os.path.join(results_dir, "anef_login_results.csv")
    results_df.to_csv(results_path, index=False, encoding='utf-8')
    print(f"💾 Rapport détaillé sauvegardé dans: {results_path}")
    
    # Afficher un résumé des notifications
    if 'notifications' in results_df.columns:
        notif_oui = len(results_df[results_df['notifications'] == 'OUI'])
        notif_non = len(results_df[results_df['notifications'] == 'NON'])
        update_pwd = len(results_df[results_df['notifications'] == 'UPDATE_PASSWORD'])
        print(f"\n🔔 Notifications: {notif_oui} OUI, {notif_non} NON")
        if update_pwd > 0:
            print(f"⚠️  UPDATE_PASSWORD requis: {update_pwd}")
    
    return results


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # Mode test avec un seul compte
        if len(sys.argv) == 3:
            username = sys.argv[1]
            password = sys.argv[2]
            print(f"🧪 Mode test - Connexion unique")
            asyncio.run(test_single_login(username, password, headless=False))
        else:
            print("Usage: python anef_login.py <username> <password>")
            print("   ou: python anef_login.py  (pour traiter le CSV)")
    else:
        # Mode batch depuis le CSV
        # Utiliser le chemin Docker si le fichier existe, sinon utiliser le chemin local
        import os
        docker_csv_path = "/app/data/input.csv"
        local_csv_path = r"C:\Users\Antoi\Desktop\ProjetAnef\TRUE CSV MHK - MHK_Avocats_Login_Cleaned - MHK - Feuille 1 (1)_FIXED_UPDATED.csv"
        
        csv_path = docker_csv_path if os.path.exists(docker_csv_path) else local_csv_path
        print(f"📁 Mode batch - Traitement du CSV: {csv_path}")
        
        # Vérifier si on est en mode Docker (pas de TTY)
        is_docker = not sys.stdin.isatty()
        
        if is_docker:
            # Mode Docker : utiliser les variables d'environnement
            limit_env = os.getenv('ACCOUNT_LIMIT', 'all')
            if limit_env.lower() == 'all':
                limit = None
            else:
                try:
                    limit = int(limit_env)
                except:
                    limit = None
            
            # Vérifier si on veut afficher le navigateur
            headless_env = os.getenv('HEADLESS', 'true').lower()
            headless = headless_env in ['true', '1', 'yes']
            
            print(f"🐳 Mode Docker détecté")
            print(f"📊 Comptes à traiter: {limit if limit else 'TOUS'}")
            print(f"🖥️ Mode navigateur: {'Headless' if headless else 'Visible (VNC)'}")
            print(f"🚀 Démarrage automatique...\n")
            asyncio.run(batch_login_from_csv(csv_path, headless=headless, max_concurrent=1, limit=limit))
        else:
            # Mode interactif : demander à l'utilisateur
            limit_input = input("\n🔢 Combien de comptes traiter? (défaut: tous, entrez un nombre pour limiter): ")
            if limit_input.strip() == '':
                limit = None  # Traiter tous les comptes par défaut
            elif limit_input.lower() == 'all':
                limit = None
            else:
                try:
                    limit = int(limit_input)
                except:
                    limit = 10
            
            response = input(f"\n⚠️ Lancer les connexions pour {limit if limit else 'TOUS les'} comptes? (oui/non): ")
            if response.lower() in ['oui', 'o', 'yes', 'y']:
                asyncio.run(batch_login_from_csv(csv_path, headless=True, max_concurrent=1, limit=limit))
            else:
                print("❌ Opération annulée")
