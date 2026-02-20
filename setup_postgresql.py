# -*- coding: utf-8 -*-
"""
Script pour créer la table PostgreSQL et importer les données du CSV
"""
import pandas as pd
import psycopg2
from psycopg2 import sql
import sys

# Configuration PostgreSQL
DATABASE_URL = "postgresql://postgres:QfGHYQavuwnCcNSaLQCAdxVGnCXklNyi@mainline.proxy.rlwy.net:56424/railway"
CSV_PATH = r"C:\Users\Antoi\Desktop\ProjetAnef\MHK_ANEF_MERGED.csv"

def create_table(conn):
    """Créer la table anef_accounts si elle n'existe pas"""
    cursor = conn.cursor()
    
    create_table_query = """
    CREATE TABLE IF NOT EXISTS anef_accounts (
        id SERIAL PRIMARY KEY,
        statut VARCHAR(100),
        referent_traitant VARCHAR(255),
        client_name VARCHAR(255),
        log_anef TEXT,
        identifiant VARCHAR(100),
        mot_de_passe VARCHAR(255),
        commentaire_robot TEXT,
        derniere_verification DATE,
        email VARCHAR(255),
        mobile VARCHAR(50),
        type_demarche_vf VARCHAR(100),
        localisation_juridiction VARCHAR(255),
        date_prise_en_charge DATE,
        date_depot_prefecture DATE,
        date_envoi_dossier DATE,
        adresse TEXT,
        mailing_city VARCHAR(100),
        mailing_zip VARCHAR(20),
        type_institution VARCHAR(100),
        client_owner_id VARCHAR(100),
        nom_du_client VARCHAR(255),
        type_notification VARCHAR(100),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    
    CREATE INDEX IF NOT EXISTS idx_identifiant ON anef_accounts(identifiant);
    CREATE INDEX IF NOT EXISTS idx_email ON anef_accounts(email);
    """
    
    cursor.execute(create_table_query)
    conn.commit()
    print("✅ Table 'anef_accounts' créée avec succès")
    cursor.close()

def parse_date(date_str):
    """Parser une date en gérant différents formats et valeurs invalides"""
    if pd.isna(date_str) or date_str == '' or date_str is None:
        return None
    
    date_str = str(date_str).strip()
    
    # Si c'est juste un mois/année incomplet, retourner None
    if len(date_str) < 8:  # Format minimum: DD/MM/YY
        return None
    
    try:
        # Essayer le format français DD/MM/YYYY
        from datetime import datetime
        return datetime.strptime(date_str, '%d/%m/%Y').date()
    except:
        try:
            # Essayer le format DD/MM/YY
            from datetime import datetime
            return datetime.strptime(date_str, '%d/%m/%y').date()
        except:
            return None

def import_csv_data(conn, csv_path):
    """Importer les données du CSV dans PostgreSQL"""
    print(f"📊 Chargement du CSV: {csv_path}")
    df = pd.read_csv(csv_path, encoding='utf-8')
    
    print(f"   Lignes: {len(df)}")
    print(f"   Colonnes: {list(df.columns)}")
    
    # Mapper les colonnes du CSV aux colonnes de la table
    column_mapping = {
        'Statut': 'statut',
        'Référent traitant': 'referent_traitant',
        '웃 Client Name': 'client_name',
        'Log ANEF': 'log_anef',
        'Identifiant': 'identifiant',
        'Mot_de_passe': 'mot_de_passe',
        'Commentaire robot': 'commentaire_robot',
        'Derniere vérification (date)': 'derniere_verification',
        'Email': 'email',
        'Mobile': 'mobile',
        'Type de démarche VF': 'type_demarche_vf',
        'Localisation de la juridiction': 'localisation_juridiction',
        'Date de prise en charge': 'date_prise_en_charge',
        'Date de dépôt en Préfecture': 'date_depot_prefecture',
        "Date d'envoi dossier": 'date_envoi_dossier',
        'Adresse': 'adresse',
        'Mailing City': 'mailing_city',
        'Mailing Zip': 'mailing_zip',
        "Type d'institution": 'type_institution',
        '웃 Client Owner.id': 'client_owner_id',
        'Nom du client': 'nom_du_client',
        'Type de notification': 'type_notification'
    }
    
    # Renommer les colonnes
    df = df.rename(columns=column_mapping)
    
    # Remplacer NaN par None pour PostgreSQL
    df = df.where(pd.notna(df), None)
    
    # Parser les colonnes de dates
    date_columns = ['derniere_verification', 'date_prise_en_charge', 'date_depot_prefecture', 'date_envoi_dossier']
    for col in date_columns:
        if col in df.columns:
            df[col] = df[col].apply(parse_date)
    
    cursor = conn.cursor()
    
    # Vider la table avant l'import
    cursor.execute("TRUNCATE TABLE anef_accounts RESTART IDENTITY;")
    print("🗑️  Table vidée")
    
    # Insérer les données
    insert_query = """
    INSERT INTO anef_accounts (
        statut, referent_traitant, client_name, log_anef, identifiant, 
        mot_de_passe, commentaire_robot, derniere_verification, email, mobile,
        type_demarche_vf, localisation_juridiction, date_prise_en_charge,
        date_depot_prefecture, date_envoi_dossier, adresse, mailing_city,
        mailing_zip, type_institution, client_owner_id, nom_du_client,
        type_notification
    ) VALUES (
        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
    )
    """
    
    def safe_get(row, key):
        """Récupérer une valeur en convertissant NaN en None"""
        val = row.get(key)
        if pd.isna(val):
            return None
        return val
    
    inserted = 0
    errors = 0
    for idx, row in df.iterrows():
        try:
            cursor.execute(insert_query, (
                safe_get(row, 'statut'),
                safe_get(row, 'referent_traitant'),
                safe_get(row, 'client_name'),
                safe_get(row, 'log_anef'),
                safe_get(row, 'identifiant'),
                safe_get(row, 'mot_de_passe'),
                safe_get(row, 'commentaire_robot'),
                safe_get(row, 'derniere_verification'),
                safe_get(row, 'email'),
                safe_get(row, 'mobile'),
                safe_get(row, 'type_demarche_vf'),
                safe_get(row, 'localisation_juridiction'),
                safe_get(row, 'date_prise_en_charge'),
                safe_get(row, 'date_depot_prefecture'),
                safe_get(row, 'date_envoi_dossier'),
                safe_get(row, 'adresse'),
                safe_get(row, 'mailing_city'),
                safe_get(row, 'mailing_zip'),
                safe_get(row, 'type_institution'),
                safe_get(row, 'client_owner_id'),
                safe_get(row, 'nom_du_client'),
                safe_get(row, 'type_notification')
            ))
            inserted += 1
            if inserted % 100 == 0:
                print(f"   Importé: {inserted}/{len(df)}")
        except Exception as e:
            errors += 1
            if errors <= 5:  # Afficher seulement les 5 premières erreurs
                print(f"⚠️  Erreur ligne {idx}: {e}")
            conn.rollback()  # Rollback de la transaction en erreur
            # Continuer avec la ligne suivante
    
    conn.commit()
    cursor.close()
    print(f"✅ {inserted} lignes importées avec succès")
    if errors > 0:
        print(f"⚠️  {errors} lignes en erreur (ignorées)")

def main():
    print("🚀 Configuration de PostgreSQL pour ANEF")
    print(f"📍 Base de données: {DATABASE_URL.split('@')[1]}")
    
    try:
        # Connexion à PostgreSQL
        print("\n🔌 Connexion à PostgreSQL...")
        conn = psycopg2.connect(DATABASE_URL)
        print("✅ Connexion établie")
        
        # Créer la table
        print("\n📋 Création de la table...")
        create_table(conn)
        
        # Importer les données
        print("\n📥 Import des données du CSV...")
        import_csv_data(conn, CSV_PATH)
        
        # Vérifier l'import
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM anef_accounts;")
        count = cursor.fetchone()[0]
        cursor.close()
        
        print(f"\n✅ Import terminé! Total: {count} comptes dans la base de données")
        
        conn.close()
        
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
