# -*- coding: utf-8 -*-
"""
Script pour ajouter une contrainte UNIQUE sur la colonne identifiant
"""
import psycopg2
import sys

# Configuration PostgreSQL
DATABASE_URL = "postgresql://postgres:QfGHYQavuwnCcNSaLQCAdxVGnCXklNyi@mainline.proxy.rlwy.net:56424/railway"

def add_unique_constraint(conn):
    """Ajouter une contrainte UNIQUE sur la colonne identifiant"""
    cursor = conn.cursor()
    
    try:
        print("📝 Ajout de la contrainte UNIQUE sur identifiant...")
        cursor.execute("""
            ALTER TABLE anef_accounts 
            ADD CONSTRAINT unique_identifiant UNIQUE (identifiant);
        """)
        conn.commit()
        print("✅ Contrainte UNIQUE ajoutée avec succès")
    except Exception as e:
        if "already exists" in str(e):
            print("ℹ️  La contrainte existe déjà")
        else:
            raise e
    finally:
        cursor.close()

def main():
    print("🚀 Ajout de contrainte UNIQUE sur PostgreSQL")
    
    try:
        # Connexion à PostgreSQL
        print("\n🔌 Connexion à PostgreSQL...")
        conn = psycopg2.connect(DATABASE_URL)
        print("✅ Connexion établie")
        
        # Ajouter la contrainte
        add_unique_constraint(conn)
        
        conn.close()
        print("\n✅ Terminé!")
        
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
