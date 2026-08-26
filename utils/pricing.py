import pandas as pd
from .config import MAJORATION, ACCESSOIRES, DECES, PSY, TAXE, POSTES

def calculer_prime_ttc(prime_pure):
    if prime_pure is None:
        return None
    
    majoration = prime_pure * MAJORATION
    prime_majoree = prime_pure + majoration
    prime_nette = prime_majoree + ACCESSOIRES + DECES + PSY
    taxes = prime_nette * TAXE
    ttc = prime_nette + taxes
    
    return {
        "prime_pure": prime_pure,
        "majoration": majoration,
        "prime_majoree": prime_majoree,
        "accessoires": ACCESSOIRES,
        "deces": DECES,
        "psy": PSY,
        "prime_nette": prime_nette,
        "taxes": taxes,
        "ttc": ttc
    }

def lookup_prime_pure(df_totale, classe_age, sexe, filiation, ald, zone, contrat):
    ald_val = 1 if ald in ["Oui", 1] else 0
    mask = (
        (df_totale['CLASSE_AGE'] == classe_age) &
        (df_totale['SEXE'] == sexe) &
        (df_totale['FILIATION'] == filiation) &
        (df_totale['AFFECTION_CHR_NUM'] == ald_val) &
        (df_totale['ZONE_GEO'] == zone) &
        (df_totale['TYPE_CONTRAT'] == contrat)
    )
    res = df_totale[mask]
    if not res.empty:
        return res.iloc[0]
    return None

def lookup_prime_par_poste(df_complete, classe_age, sexe, filiation, ald, zone, contrat):
    ald_val = 1 if ald in ["Oui", 1] else 0
    mask = (
        (df_complete['CLASSE_AGE'] == classe_age) &
        (df_complete['SEXE'] == sexe) &
        (df_complete['FILIATION'] == filiation) &
        (df_complete['AFFECTION_CHR_NUM'] == ald_val) &
        (df_complete['ZONE_GEO'] == zone) &
        (df_complete['TYPE_CONTRAT'] == contrat)
    )
    res = df_complete[mask].copy()
    if not res.empty:
        return res
    return pd.DataFrame()

def format_fcfa(amount):
    if pd.isna(amount):
        return "-"
    return f"{int(round(amount)):,} FCFA".replace(",", " ")
