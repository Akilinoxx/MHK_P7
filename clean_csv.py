import pandas as pd
import re
from typing import Tuple, Optional

def extract_credentials(log_anef: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Extrait l'identifiant et le mot de passe de la colonne Log ANEF.
    
    Returns:
        Tuple[identifiant, mot_de_passe]
    """
    if pd.isna(log_anef) or not isinstance(log_anef, str):
        return None, None
    
    # Nettoyer le texte
    text = log_anef.strip()
    
    # Initialiser les variables
    identifiant = None
    mdp = None
    
    # Pattern 1: Recherche d'identifiant avec différents préfixes
    id_patterns = [
        r'(?:ID|id|Id|identifiant|compte\s+ANEF|Numéro\s+fiscal|N°\s+étranger)\s*[:\s=]\s*([^\n]+)',
        r'^(\d{10,})$',  # Numéro seul sur une ligne
        r'^([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})$',  # Email seul
    ]
    
    for pattern in id_patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
        if match:
            identifiant = match.group(1).strip()
            # Nettoyer les annotations entre parenthèses et autres infos
            identifiant = re.sub(r'\s*\([^)]*\)', '', identifiant)
            identifiant = identifiant.split('\n')[0].strip()
            break
    
    # Si pas d'identifiant trouvé avec pattern, chercher un numéro ou email au début
    if not identifiant:
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            # Chercher un numéro de 10+ chiffres
            num_match = re.match(r'^(\d{10,})', line)
            if num_match:
                identifiant = num_match.group(1)
                break
            # Chercher un email
            email_match = re.match(r'^([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', line)
            if email_match:
                identifiant = email_match.group(1)
                break
    
    # Pattern 2: Recherche de mot de passe avec différents préfixes
    mdp_patterns = [
        r'(?:MDP|mdp|Mdp|mot\s+de\s+passe|password)\s*[:\s=]\s*([^\n]+)',
        r'(?:Nouveau\s+mdp\s+ANEF|MAJ\s+mdp\s+ANEF)\s*[:\s]\s*([^\n]+)',
    ]
    
    for pattern in mdp_patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
        if match:
            mdp = match.group(1).strip()
            # Nettoyer les annotations
            mdp = re.sub(r'\s*\([^)]*\)', '', mdp)
            mdp = re.sub(r'\s*(au|neg|MDP\s+KO).*$', '', mdp, flags=re.IGNORECASE)
            mdp = mdp.strip()
            break
    
    # Si pas de MDP trouvé avec pattern, chercher sur la deuxième ligne
    if not mdp and identifiant:
        lines = text.split('\n')
        if len(lines) > 1:
            # La deuxième ligne pourrait être le MDP
            potential_mdp = lines[1].strip()
            # Vérifier que ce n'est pas un autre identifiant
            if not re.match(r'(?:ID|id|identifiant)', potential_mdp, re.IGNORECASE):
                mdp = potential_mdp
                mdp = re.sub(r'\s*\([^)]*\)', '', mdp)
                mdp = mdp.strip()
    
    # Cas spécial: format "ID ... MDP ..." sur une ligne
    single_line_match = re.search(
        r'(?:ID|id)\s*[:\s]?\s*([^\s]+)\s+(?:MDP|mdp)\s+([^\s]+)',
        text,
        re.IGNORECASE
    )
    if single_line_match and not identifiant:
        identifiant = single_line_match.group(1).strip()
        mdp = single_line_match.group(2).strip()
    
    # Nettoyer les valeurs finales
    if identifiant:
        identifiant = identifiant.replace(',', '').strip()
    if mdp:
        mdp = mdp.replace(',', '').strip()
        # Retirer les statuts
        if mdp.upper() in ['MDP KO', 'MDP À RÉINITIALISER', '']:
            mdp = None
    
    return identifiant, mdp


def clean_csv(input_file: str, output_file: str):
    """
    Nettoie le fichier CSV en extrayant les identifiants et mots de passe.
    """
    print(f"Lecture du fichier: {input_file}")
    df = pd.read_csv(input_file, encoding='utf-8')
    
    print(f"Nombre de lignes: {len(df)}")
    print(f"Colonnes: {df.columns.tolist()}")
    
    # Extraire les credentials
    print("\nExtraction des identifiants et mots de passe...")
    credentials = df['Log ANEF'].apply(extract_credentials)
    
    # Créer les nouvelles colonnes
    df['Identifiant'] = credentials.apply(lambda x: x[0])
    df['Mot_de_passe'] = credentials.apply(lambda x: x[1])
    
    # Réorganiser les colonnes pour mettre Identifiant et Mot_de_passe après Log ANEF
    cols = df.columns.tolist()
    log_anef_idx = cols.index('Log ANEF')
    new_cols = cols[:log_anef_idx+1] + ['Identifiant', 'Mot_de_passe'] + [c for c in cols[log_anef_idx+1:] if c not in ['Identifiant', 'Mot_de_passe']]
    df = df[new_cols]
    
    # Sauvegarder
    print(f"\nSauvegarde du fichier nettoyé: {output_file}")
    df.to_csv(output_file, index=False, encoding='utf-8')
    
    # Statistiques
    total = len(df)
    with_id = df['Identifiant'].notna().sum()
    with_mdp = df['Mot_de_passe'].notna().sum()
    with_both = ((df['Identifiant'].notna()) & (df['Mot_de_passe'].notna())).sum()
    
    print("\n=== STATISTIQUES ===")
    print(f"Total de lignes: {total}")
    print(f"Avec identifiant: {with_id} ({with_id/total*100:.1f}%)")
    print(f"Avec mot de passe: {with_mdp} ({with_mdp/total*100:.1f}%)")
    print(f"Avec les deux: {with_both} ({with_both/total*100:.1f}%)")
    print(f"Sans identifiant: {total - with_id}")
    print(f"Sans mot de passe: {total - with_mdp}")
    
    # Afficher quelques exemples pour vérification
    print("\n=== EXEMPLES (5 premières lignes avec données) ===")
    sample = df[df['Log ANEF'].notna()].head(5)
    for idx, row in sample.iterrows():
        print(f"\nLigne {idx + 2}:")
        print(f"  Client: {row['웃 Client Name']}")
        print(f"  Log ANEF original: {row['Log ANEF'][:100]}...")
        print(f"  → Identifiant extrait: {row['Identifiant']}")
        print(f"  → Mot de passe extrait: {row['Mot_de_passe']}")
    
    # Identifier les cas problématiques
    print("\n=== CAS PROBLÉMATIQUES (sans identifiant OU sans MDP) ===")
    problematic = df[(df['Log ANEF'].notna()) & ((df['Identifiant'].isna()) | (df['Mot_de_passe'].isna()))]
    if len(problematic) > 0:
        print(f"Nombre de cas: {len(problematic)}")
        for idx, row in problematic.head(10).iterrows():
            print(f"\nLigne {idx + 2} - {row['웃 Client Name']}:")
            print(f"  Log ANEF: {row['Log ANEF']}")
            print(f"  → ID: {row['Identifiant']}, MDP: {row['Mot_de_passe']}")
    else:
        print("Aucun cas problématique détecté!")
    
    return df


if __name__ == "__main__":
    input_file = r"c:\Users\Antoi\Desktop\ProjetAnef\MHK Avocats - Suivi ANEF - Demandes de naturalisation.xlsx - TOTAL CRM.csv"
    output_file = r"c:\Users\Antoi\Desktop\ProjetAnef\MHK_Avocats_CLEANED.csv"
    
    df_cleaned = clean_csv(input_file, output_file)
    print("\n✅ Nettoyage terminé!")
