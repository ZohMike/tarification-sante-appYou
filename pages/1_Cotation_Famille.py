import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.config import CLASSES_AGE, COLOR_MAIN, COLOR_SEC, COLOR_ACCENT, COLOR_PALETTE
from utils.pricing import calculer_prime_ttc, lookup_prime_pure, format_fcfa

st.set_page_config(page_title="Cotation Famille", page_icon="👨‍👩‍👧‍👦", layout="wide")

st.markdown("<h1 style='color: #8c4b27;'>👨‍👩‍👧‍👦 Cotation Famille</h1>", unsafe_allow_html=True)
st.markdown("<p style='font-size: 1.1rem; color: #555;'>Tarifiez un foyer complet (Assuré principal, conjoint, enfants) et obtenez la prime globale.</p>", unsafe_allow_html=True)
st.divider()

@st.cache_data
def load_data():
    return pd.read_csv("data/table_prime_pure_totale.csv")

try:
    df_totale = load_data()
except Exception as e:
    st.error(f"Erreur de chargement des données: {e}")
    st.stop()

# --- Paramètres Globaux du contrat ---
st.markdown("<h3 style='color: #8c4b27;'>🌍 Paramètres du Contrat</h3>", unsafe_allow_html=True)
col_z, col_c = st.columns(2)
with col_z:
    zone = st.selectbox("Zone Géographique du foyer", ["ABIDJAN", "HORS-ABIDJAN"])
with col_c:
    contrat = st.selectbox("Type de contrat", ["INDIVIDUEL", "COLLECTIF"])

st.markdown("<br>", unsafe_allow_html=True)

# --- Saisie de la composition familiale ---
st.markdown("<h3 style='color: #8c4b27;'>👥 Composition Familiale</h3>", unsafe_allow_html=True)

membres = [] # Liste pour stocker les profils à coter

# 1. Assuré Principal
st.markdown("#### 👤 Assuré Principal")
col1, col2, col3 = st.columns(3)
with col1:
    ap_age_label = st.selectbox("Classe d'âge (Principal)", list(CLASSES_AGE.values()), index=3, key="ap_age")
    ap_age = list(CLASSES_AGE.keys())[list(CLASSES_AGE.values()).index(ap_age_label)]
with col2:
    ap_sexe = st.radio("Sexe (Principal)", ["M", "F"], horizontal=True, key="ap_sexe")
with col3:
    ap_ald = st.radio("ALD (Principal)", ["Non", "Oui"], horizontal=True, key="ap_ald")

membres.append({
    "Rôle": "Assuré Principal",
    "Filiation": "ASSURÉ PRINCIPAL",
    "Age": ap_age,
    "Age_Label": ap_age_label,
    "Sexe": ap_sexe,
    "ALD": ap_ald
})

# 2. Conjoint
st.markdown("#### 👩‍❤️‍👨 Conjoint")
has_conjoint = st.checkbox("Ajouter un(e) conjoint(e)")
if has_conjoint:
    col1, col2, col3 = st.columns(3)
    with col1:
        cj_age_label = st.selectbox("Classe d'âge (Conjoint)", list(CLASSES_AGE.values()), index=3, key="cj_age")
        cj_age = list(CLASSES_AGE.keys())[list(CLASSES_AGE.values()).index(cj_age_label)]
    with col2:
        cj_sexe = st.radio("Sexe (Conjoint)", ["M", "F"], horizontal=True, key="cj_sexe")
    with col3:
        cj_ald = st.radio("ALD (Conjoint)", ["Non", "Oui"], horizontal=True, key="cj_ald")
    
    membres.append({
        "Rôle": "Conjoint",
        "Filiation": "CONJOINT",
        "Age": cj_age,
        "Age_Label": cj_age_label,
        "Sexe": cj_sexe,
        "ALD": cj_ald
    })

# 3. Enfants
st.markdown("#### 👧👦 Enfants")
nb_enfants = st.number_input("Nombre d'enfants", min_value=0, max_value=10, value=0, step=1)

for i in range(nb_enfants):
    st.markdown(f"**Enfant {i+1}**")
    col1, col2, col3 = st.columns(3)
    with col1:
        # Default age for children usually 0-18 (index 0)
        enf_age_label = st.selectbox(f"Classe d'âge (Enfant {i+1})", list(CLASSES_AGE.values()), index=0, key=f"enf_age_{i}")
        enf_age = list(CLASSES_AGE.keys())[list(CLASSES_AGE.values()).index(enf_age_label)]
    with col2:
        enf_sexe = st.radio(f"Sexe (Enfant {i+1})", ["M", "F"], horizontal=True, key=f"enf_sexe_{i}")
    with col3:
        enf_ald = st.radio(f"ALD (Enfant {i+1})", ["Non", "Oui"], horizontal=True, key=f"enf_ald_{i}")
        
    membres.append({
        "Rôle": f"Enfant {i+1}",
        "Filiation": "ENFANT",
        "Age": enf_age,
        "Age_Label": enf_age_label,
        "Sexe": enf_sexe,
        "ALD": enf_ald
    })

st.divider()

# --- CALCULS ---
st.markdown("<h3 style='color: #8c4b27;'>💰 Résultats de la Cotation</h3>", unsafe_allow_html=True)

total_prime_pure = 0
total_ttc = 0
resultats_liste = []
profils_introuvables = False

for m in membres:
    row = lookup_prime_pure(df_totale, m["Age"], m["Sexe"], m["Filiation"], m["ALD"], zone, contrat)
    if row is None:
        profils_introuvables = True
        resultats_liste.append({
            "Membre": m["Rôle"],
            "Profil": f"{m['Age_Label']}, {m['Sexe']}, ALD:{m['ALD']}",
            "Prime Pure": "-",
            "Prime TTC": "Erreur : Profil Inconnu"
        })
    else:
        pp = row['pp_totale']
        res = calculer_prime_ttc(pp)
        total_prime_pure += pp
        total_ttc += res['ttc']
        resultats_liste.append({
            "Membre": m["Rôle"],
            "Profil": f"{m['Age_Label']}, {m['Sexe']}, ALD:{m['ALD']}",
            "Prime Pure": format_fcfa(pp),
            "Prime TTC": format_fcfa(res['ttc'])
        })

if profils_introuvables:
    st.warning("⚠️ Certains profils saisis n'existent pas dans la base d'apprentissage (ex: Enfant dans la classe 61+ ans). Veuillez vérifier la saisie.")

# Affichage des métriques globales
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Membres Couverts", f"{len(membres)} personnes")
with col2:
    st.metric("Prime Pure Globale (Foyer)", format_fcfa(total_prime_pure))
with col3:
    st.metric("PRIME TTC GLOBALE (Foyer)", format_fcfa(total_ttc))

st.markdown("<br>", unsafe_allow_html=True)

# Tableau détaillé
st.markdown("#### Détail par membre")
df_res = pd.DataFrame(resultats_liste)
st.dataframe(df_res, use_container_width=True, hide_index=True)

