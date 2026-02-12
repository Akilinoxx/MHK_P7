# -*- coding: utf-8 -*-
import pandas as pd
import re

def format_mobile_number(mobile):
    """
    Reformate un numéro de téléphone au format français standard (06XXXXXXXX ou 07XXXXXXXX).
    
    Args:
        mobile: Numéro de téléphone à formater (peut être float, int ou string)
    
    Returns:
        Numéro formaté en string ou chaîne vide si invalide
    """
    if pd.isna(mobile):
        return ''
    
    # Convertir en string et enlever les espaces
    mobile_str = str(mobile).strip()
    
    # Enlever le .0 si c'est un float
    if mobile_str.endswith('.0'):
        mobile_str = mobile_str[:-2]
    
    # Enlever tous les caractères non numériques
    digits = re.sub(r'\D', '', mobile_str)
    
    # Si le numéro commence par +33, enlever le +33 et ajouter 0
    if digits.startswith('33') and len(digits) == 11:
        digits = '0' + digits[2:]
    
    # Si le numéro a 9 chiffres et commence par 6 ou 7, ajouter 0 au début
    if len(digits) == 9 and digits[0] in ['6', '7']:
        digits = '0' + digits
    
    # Vérifier que le numéro a 10 chiffres et commence par 06 ou 07
    if len(digits) == 10 and digits[:2] in ['06', '07']:
        return digits
    
    # Si le format n'est pas reconnu, retourner le numéro original
    return mobile_str

# Charger le CSV
csv_path = r"C:\Users\Antoi\Desktop\ProjetAnef\MHK_Avocats_Login_Cleaned - MHK - Feuille 1 (1).csv"
df = pd.read_csv(csv_path, encoding='utf-8')

print(f"📊 Fichier chargé: {len(df)} lignes")
print(f"\n🔍 Analyse des numéros de téléphone...")

# Afficher quelques exemples avant formatage
print("\n📱 Exemples AVANT formatage:")
for i, mobile in enumerate(df['Mobile'].head(10)):
    print(f"  {i+1}. {mobile}")

# Formater tous les numéros
df['Mobile'] = df['Mobile'].apply(format_mobile_number)

# Afficher quelques exemples après formatage
print("\n✅ Exemples APRÈS formatage:")
for i, mobile in enumerate(df['Mobile'].head(10)):
    print(f"  {i+1}. {mobile}")

# Sauvegarder le CSV avec les numéros reformatés
output_path = csv_path.replace('.csv', '_FIXED.csv')
df.to_csv(output_path, index=False, encoding='utf-8')

print(f"\n💾 Fichier sauvegardé: {output_path}")
print(f"✅ Numéros de téléphone reformatés au format 06/07")
