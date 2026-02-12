# -*- coding: utf-8 -*-
import pandas as pd

# Charger le CSV
csv_path = r"C:\Users\Antoi\Desktop\ProjetAnef\MHK_Avocats_Login_Cleaned - MHK - Feuille 1 (1)_FIXED.csv"
df = pd.read_csv(csv_path, encoding='utf-8')

print(f"📊 Fichier chargé: {len(df)} lignes")

# ID à rechercher et supprimer
test_id = "7703079734"

# Supprimer les lignes avec cet ID si elles existent
df_filtered = df[df['Identifiant'].astype(str) != test_id]
removed_count = len(df) - len(df_filtered)

if removed_count > 0:
    print(f"🗑️ {removed_count} ligne(s) supprimée(s) avec l'ID {test_id}")
else:
    print(f"ℹ️ Aucune ligne trouvée avec l'ID {test_id}")

# Créer la nouvelle ligne de test
test_row = {
    'Statut': 'Client - Actif',
    'Référent traitant': 'Test',
    '웃 Client Name': 'TEST ACCOUNT',
    'Log ANEF': f'ID: {test_id}\nMDP: Kossingou77380@',
    'Identifiant': test_id,
    'Mot_de_passe': 'Kossingou77380@',
    'Commentaire robot': '',
    'Derniere vérification (date)': '',
    'Email': 'test@example.com',
    'Mobile': '0600000000',
    'Type de démarche VF': 'Test',
    'Localisation de la juridiction': 'Test',
    'Date de prise en charge': '',
    'Date de dépôt en Préfecture': '',
    'Date d\'envoi dossier': '',
    'Adresse': 'Test',
    'Mailing City': 'Test',
    'Mailing Zip': '75000',
    'Type d\'institution': 'Test',
    '웃 Client Owner.id': 'test'
}

# Créer un DataFrame avec la nouvelle ligne
test_df = pd.DataFrame([test_row])

# Concaténer la nouvelle ligne en première position
df_final = pd.concat([test_df, df_filtered], ignore_index=True)

print(f"✅ Compte de test ajouté en première ligne")
print(f"📊 Nouveau total: {len(df_final)} lignes")

# Sauvegarder le CSV modifié
df_final.to_csv(csv_path, index=False, encoding='utf-8')
print(f"💾 Fichier sauvegardé: {csv_path}")
print(f"\n🔑 Compte de test:")
print(f"   ID: {test_id}")
print(f"   MDP: Kossingou77380@")
