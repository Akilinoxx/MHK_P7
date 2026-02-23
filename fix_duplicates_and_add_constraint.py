# -*- coding: utf-8 -*-
"""
Script pour gérer les doublons et ajouter la contrainte UNIQUE
"""
import psycopg2
import sys

# Configuration PostgreSQL
DATABASE_URL = "postgresql://postgres:QfGHYQavuwnCcNSaLQCAdxVGnCXklNyi@mainline.proxy.rlwy.net:56424/railway"

def find_duplicates(conn):
    """Trouver les identifiants en double"""
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT identifiant, COUNT(*) as count
        FROM anef_accounts
        WHERE identifiant IS NOT NULL
        GROUP BY identifiant
        HAVING COUNT(*) > 1
        ORDER BY count DESC;
    """)
    
    duplicates = cursor.fetchall()
    cursor.close()
    
    return duplicates

def merge_duplicates(conn):
    """Fusionner les doublons en gardant le plus récent"""
    cursor = conn.cursor()
    
    # Trouver les doublons
    duplicates = find_duplicates(conn)
    
    if not duplicates:
        print("✅ Aucun doublon trouvé")
        return 0
    
    print(f"⚠️  {len(duplicates)} identifiants en double trouvés")
    
    merged = 0
    for identifiant, count in duplicates:
        print(f"\n  📋 Identifiant: {identifiant} ({count} occurrences)")
        
        # Récupérer tous les enregistrements avec cet identifiant
        cursor.execute("""
            SELECT id, client_name, email, mot_de_passe, updated_at
            FROM anef_accounts
            WHERE identifiant = %s
            ORDER BY updated_at DESC NULLS LAST, id DESC;
        """, (identifiant,))
        
        records = cursor.fetchall()
        
        if len(records) > 1:
            # Garder le premier (le plus récent)
            keep_id = records[0][0]
            keep_name = records[0][1]
            
            # Supprimer les autres
            delete_ids = [r[0] for r in records[1:]]
            
            print(f"     ✅ Garder: ID {keep_id} - {keep_name}")
            print(f"     🗑️  Supprimer: {len(delete_ids)} doublons")
            
            cursor.execute("""
                DELETE FROM anef_accounts
                WHERE id = ANY(%s);
            """, (delete_ids,))
            
            merged += len(delete_ids)
    
    conn.commit()
    cursor.close()
    
    return merged

def add_unique_constraint(conn):
    """Ajouter une contrainte UNIQUE sur la colonne identifiant"""
    cursor = conn.cursor()
    
    try:
        print("\n📝 Ajout de la contrainte UNIQUE sur identifiant...")
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
    print("🚀 Nettoyage des doublons et ajout de contrainte UNIQUE")
    
    try:
        # Connexion à PostgreSQL
        print("\n🔌 Connexion à PostgreSQL...")
        conn = psycopg2.connect(DATABASE_URL)
        print("✅ Connexion établie")
        
        # Fusionner les doublons
        print("\n🔍 Recherche et fusion des doublons...")
        merged = merge_duplicates(conn)
        
        if merged > 0:
            print(f"\n✅ {merged} doublons supprimés")
        
        # Ajouter la contrainte
        add_unique_constraint(conn)
        
        # Vérifier le total
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM anef_accounts;")
        count = cursor.fetchone()[0]
        cursor.close()
        
        print(f"\n✅ Total: {count} comptes dans la base de données")
        
        conn.close()
        print("\n✅ Terminé!")
        
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
