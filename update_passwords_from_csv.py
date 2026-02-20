# -*- coding: utf-8 -*-
"""
Script pour mettre à jour les mots de passe dans PostgreSQL à partir d'un nouveau CSV
"""
import pandas as pd
import psycopg2
import sys

# Configuration PostgreSQL
DATABASE_URL = "postgresql://postgres:QfGHYQavuwnCcNSaLQCAdxVGnCXklNyi@mainline.proxy.rlwy.net:56424/railway"
CSV_PATH = r"C:\Users\Antoi\Desktop\ProjetAnef\[MHK] New Logs ANEF - Feuille 1 (2).csv"

def update_passwords_from_csv(conn, csv_path):
    """
    Mettre à jour les mots de passe dans PostgreSQL à partir du CSV
    Si l'identifiant existe, mettre à jour le mot de passe
    Sinon, créer un nouveau compte avec les informations minimales
    """
    print(f"📊 Chargement du CSV: {csv_path}")
    df = pd.read_csv(csv_path, encoding='utf-8')
    
    print(f"   Lignes: {len(df)}")
    print(f"   Colonnes: {list(df.columns)}")
    
    cursor = conn.cursor()
    
    updated = 0
    added = 0
    errors = 0
    
    for idx, row in df.iterrows():
        identifiant = row.get('ID')
        password = row.get('PASSWORD')
        
        # Ignorer les lignes sans identifiant ou mot de passe
        if pd.isna(identifiant) or pd.isna(password) or identifiant == '' or password == '':
            continue
        
        identifiant = str(identifiant).strip()
        password = str(password).strip()
        
        try:
            # Vérifier si le compte existe déjà
            cursor.execute(
                "SELECT id, client_name FROM anef_accounts WHERE identifiant = %s OR email = %s",
                (identifiant, identifiant)
            )
            result = cursor.fetchone()
            
            if result:
                # Mettre à jour le mot de passe
                account_id = result[0]
                client_name = result[1]
                cursor.execute(
                    "UPDATE anef_accounts SET mot_de_passe = %s, updated_at = CURRENT_TIMESTAMP WHERE id = %s",
                    (password, account_id)
                )
                updated += 1
                print(f"  ✅ Mis à jour: {client_name} ({identifiant})")
            else:
                # Créer un nouveau compte
                # Déterminer si c'est un email ou un numéro
                is_email = '@' in identifiant
                
                cursor.execute(
                    """
                    INSERT INTO anef_accounts (
                        identifiant, mot_de_passe, email, client_name, commentaire_robot
                    ) VALUES (%s, %s, %s, %s, %s)
                    """,
                    (
                        identifiant,
                        password,
                        identifiant if is_email else None,
                        f"Nouveau compte - {identifiant}",
                        "Nouveau compte ajouté depuis CSV"
                    )
                )
                added += 1
                print(f"  ➕ Ajouté: Nouveau compte - {identifiant}")
            
            conn.commit()
            
        except Exception as e:
            errors += 1
            print(f"  ⚠️  Erreur ligne {idx} ({identifiant}): {e}")
            conn.rollback()
    
    cursor.close()
    
    print(f"\n✅ Traitement terminé:")
    print(f"   - {updated} comptes mis à jour")
    print(f"   - {added} nouveaux comptes ajoutés")
    if errors > 0:
        print(f"   - {errors} erreurs")

def main():
    print("🚀 Mise à jour des mots de passe dans PostgreSQL")
    print(f"📍 Base de données: {DATABASE_URL.split('@')[1]}")
    
    try:
        # Connexion à PostgreSQL
        print("\n🔌 Connexion à PostgreSQL...")
        conn = psycopg2.connect(DATABASE_URL)
        print("✅ Connexion établie")
        
        # Mettre à jour les mots de passe
        print("\n📝 Mise à jour des mots de passe...")
        update_passwords_from_csv(conn, CSV_PATH)
        
        # Vérifier le total
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM anef_accounts;")
        count = cursor.fetchone()[0]
        cursor.close()
        
        print(f"\n✅ Total: {count} comptes dans la base de données")
        
        conn.close()
        
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
