# -*- coding: utf-8 -*-
"""
Script pour fusionner le nouveau fichier CSV avec les logs ANEF
avec le fichier CSV actuel en matchant par email ou identifiant.
"""
import pandas as pd
import sys

# Fichiers
NEW_CSV = r"C:\Users\Antoi\Desktop\ProjetAnef\[MHK] New Logs ANEF - Feuille 1 (1).csv"
OLD_CSV = r"C:\Users\Antoi\Desktop\ProjetAnef\TRUE CSV MHK - MHK_Avocats_Login_Cleaned - MHK - Feuille 1 (1)_FIXED_UPDATED.csv"
OUTPUT_CSV = r"C:\Users\Antoi\Desktop\ProjetAnef\MHK_ANEF_MERGED.csv"

print("📊 Chargement des fichiers CSV...")

# Charger le nouveau fichier avec les nouveaux logs
df_new = pd.read_csv(NEW_CSV, encoding='utf-8')
print(f"✅ Nouveau fichier chargé: {len(df_new)} lignes")
print(f"   Colonnes: {list(df_new.columns)}")

# Charger l'ancien fichier (celui actuellement utilisé par le code)
try:
    df_old = pd.read_csv(OLD_CSV, encoding='utf-8')
    print(f"✅ Ancien fichier chargé: {len(df_old)} lignes")
    print(f"   Colonnes: {list(df_old.columns)}")
except Exception as e:
    print(f"❌ Erreur lors du chargement de l'ancien fichier: {e}")
    print("ℹ️  Création d'un nouveau fichier à partir des nouveaux logs...")
    df_old = pd.DataFrame()

# Créer un dictionnaire pour matcher les nouveaux identifiants/mots de passe
# Clé: ID (email ou numéro), Valeur: PASSWORD
new_credentials = {}
for _, row in df_new.iterrows():
    id_val = str(row['ID']).strip()
    password_val = str(row['PASSWORD']).strip()
    new_credentials[id_val] = password_val

print(f"\n🔑 {len(new_credentials)} nouveaux identifiants/mots de passe à intégrer")

# Mettre à jour l'ancien fichier avec les nouveaux credentials
updated_count = 0
new_entries = []

if not df_old.empty:
    # Mettre à jour les lignes existantes
    for idx, row in df_old.iterrows():
        identifiant = str(row.get('Identifiant', '')).strip()
        email = str(row.get('Email', '')).strip()
        
        # Chercher une correspondance par identifiant ou email
        if identifiant in new_credentials:
            df_old.at[idx, 'Mot_de_passe'] = new_credentials[identifiant]
            updated_count += 1
            # Retirer de la liste pour tracker ce qui reste
            del new_credentials[identifiant]
        elif email in new_credentials:
            df_old.at[idx, 'Mot_de_passe'] = new_credentials[email]
            updated_count += 1
            del new_credentials[email]
    
    print(f"✅ {updated_count} mots de passe mis à jour dans les comptes existants")
    
    # Ajouter les nouveaux comptes qui n'ont pas été matchés
    if new_credentials:
        print(f"\n➕ {len(new_credentials)} nouveaux comptes à ajouter")
        for id_val, password_val in new_credentials.items():
            # Déterminer si c'est un email ou un identifiant
            if '@' in id_val:
                new_entry = {
                    'Nom du client': 'NOUVEAU COMPTE',
                    'Identifiant': '',
                    'Mot_de_passe': password_val,
                    'Email': id_val,
                    'Mobile': '',
                    'Commentaire robot': 'Nouveau compte ajouté',
                    'Type de notification': ''
                }
            else:
                new_entry = {
                    'Nom du client': 'NOUVEAU COMPTE',
                    'Identifiant': id_val,
                    'Mot_de_passe': password_val,
                    'Email': '',
                    'Mobile': '',
                    'Commentaire robot': 'Nouveau compte ajouté',
                    'Type de notification': ''
                }
            new_entries.append(new_entry)
        
        # Ajouter les nouvelles lignes
        df_new_entries = pd.DataFrame(new_entries)
        df_old = pd.concat([df_old, df_new_entries], ignore_index=True)
        print(f"✅ {len(new_entries)} nouveaux comptes ajoutés")
else:
    # Si l'ancien fichier est vide, créer un nouveau à partir des nouveaux logs
    print("\n📝 Création d'un nouveau fichier à partir des nouveaux logs...")
    for id_val, password_val in new_credentials.items():
        if '@' in id_val:
            new_entry = {
                'Nom du client': 'NOUVEAU COMPTE',
                'Identifiant': '',
                'Mot_de_passe': password_val,
                'Email': id_val,
                'Mobile': '',
                'Commentaire robot': '',
                'Type de notification': ''
            }
        else:
            new_entry = {
                'Nom du client': 'NOUVEAU COMPTE',
                'Identifiant': id_val,
                'Mot_de_passe': password_val,
                'Email': '',
                'Mobile': '',
                'Commentaire robot': '',
                'Type de notification': ''
            }
        new_entries.append(new_entry)
    
    df_old = pd.DataFrame(new_entries)
    print(f"✅ {len(new_entries)} comptes créés")

# Sauvegarder le fichier fusionné
df_old.to_csv(OUTPUT_CSV, index=False, encoding='utf-8')
print(f"\n💾 Fichier fusionné sauvegardé: {OUTPUT_CSV}")
print(f"   Total de lignes: {len(df_old)}")
print(f"   Colonnes: {list(df_old.columns)}")

print("\n✅ Fusion terminée avec succès!")
