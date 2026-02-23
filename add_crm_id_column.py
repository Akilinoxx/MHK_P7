# -*- coding: utf-8 -*-
"""
Script pour ajouter une colonne crm_id et importer les ID depuis le CSV Zoho
"""
import pandas as pd
import psycopg2
import sys

# Configuration PostgreSQL
DATABASE_URL = "postgresql://postgres:QfGHYQavuwnCcNSaLQCAdxVGnCXklNyi@mainline.proxy.rlwy.net:56424/railway"
CSV_PATH = r"C:\Users\Antoi\Desktop\ProjetAnef\Matching ID zoho - Sheet0.csv"

def add_crm_id_column(conn):
    """Ajouter une colonne crm_id dans la table anef_accounts"""
    cursor = conn.cursor()
    
    try:
        print("📝 Ajout de la colonne crm_id...")
        cursor.execute("""
            ALTER TABLE anef_accounts 
            ADD COLUMN IF NOT EXISTS crm_id VARCHAR(50);
        """)
        conn.commit()
        print("✅ Colonne crm_id ajoutée")
    except Exception as e:
        print(f"⚠️  Erreur lors de l'ajout de la colonne: {e}")
        conn.rollback()
    finally:
        cursor.close()

def import_crm_ids(conn, csv_path):
    """
    Importer les ID CRM depuis le CSV Zoho en matchant par email
    """
    print(f"\n📊 Chargement du CSV: {csv_path}")
    df = pd.read_csv(csv_path, encoding='utf-8')
    
    print(f"   Lignes: {len(df)}")
    print(f"   Colonnes: {list(df.columns)}")
    
    cursor = conn.cursor()
    
    updated = 0
    not_found = 0
    errors = 0
    
    for idx, row in df.iterrows():
        record_id = row.get('Record Id')
        email = row.get('Email')
        log_anef = row.get('Log ANEF')
        
        # Ignorer les lignes sans email ou record_id
        if pd.isna(email) or pd.isna(record_id) or email == '' or record_id == '':
            continue
        
        email = str(email).strip().lower()
        record_id = str(record_id).strip()
        
        try:
            # Chercher le compte par email
            cursor.execute(
                "SELECT id, client_name FROM anef_accounts WHERE LOWER(email) = %s",
                (email,)
            )
            result = cursor.fetchone()
            
            if result:
                account_id = result[0]
                client_name = result[1]
                
                # Mettre à jour le crm_id
                cursor.execute(
                    "UPDATE anef_accounts SET crm_id = %s WHERE id = %s",
                    (record_id, account_id)
                )
                updated += 1
                print(f"  ✅ {client_name} ({email}) → CRM ID: {record_id}")
            else:
                # Essayer de matcher par identifiant si l'email ne match pas
                if not pd.isna(log_anef) and log_anef != '':
                    log_anef = str(log_anef).strip()
                    cursor.execute(
                        "SELECT id, client_name FROM anef_accounts WHERE identifiant = %s",
                        (log_anef,)
                    )
                    result = cursor.fetchone()
                    
                    if result:
                        account_id = result[0]
                        client_name = result[1]
                        
                        # Mettre à jour le crm_id ET l'email
                        cursor.execute(
                            "UPDATE anef_accounts SET crm_id = %s, email = %s WHERE id = %s",
                            (record_id, email, account_id)
                        )
                        updated += 1
                        print(f"  ✅ {client_name} ({log_anef}) → CRM ID: {record_id} + Email: {email}")
                    else:
                        not_found += 1
                        print(f"  ⚠️  Non trouvé: {email} / {log_anef}")
                else:
                    not_found += 1
                    print(f"  ⚠️  Non trouvé: {email}")
            
            conn.commit()
            
        except Exception as e:
            errors += 1
            print(f"  ⚠️  Erreur ligne {idx} ({email}): {e}")
            conn.rollback()
    
    cursor.close()
    
    print(f"\n✅ Import terminé:")
    print(f"   - {updated} comptes mis à jour avec CRM ID")
    print(f"   - {not_found} comptes non trouvés")
    if errors > 0:
        print(f"   - {errors} erreurs")

def main():
    print("🚀 Ajout de la colonne CRM ID et import des données")
    
    try:
        # Connexion à PostgreSQL
        print("\n🔌 Connexion à PostgreSQL...")
        conn = psycopg2.connect(DATABASE_URL)
        print("✅ Connexion établie")
        
        # Ajouter la colonne crm_id
        add_crm_id_column(conn)
        
        # Importer les CRM ID
        import_crm_ids(conn, CSV_PATH)
        
        # Vérifier le total
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM anef_accounts WHERE crm_id IS NOT NULL;")
        count_with_crm = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM anef_accounts;")
        count_total = cursor.fetchone()[0]
        cursor.close()
        
        print(f"\n✅ Total: {count_with_crm}/{count_total} comptes avec CRM ID")
        
        conn.close()
        
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
