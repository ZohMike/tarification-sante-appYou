import streamlit as st
import pandas as pd
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from utils.config import CLASSES_AGE, COLOR_MAIN, COLOR_SEC, COLOR_ACCENT, COLOR_PALETTE
from utils.pricing import calculer_prime_ttc, lookup_prime_pure, lookup_prime_par_poste, format_fcfa

st.set_page_config(page_title="Cotation Individuelle", page_icon="👤", layout="wide")

st.markdown("""
<style>
    :root {
        --primary: #8c4b27;
        --secondary: #d48b59;
        --accent: #c0392b;
        --bg-light: #fdfaf6;
        --text-color: #333333;
    }
    .stApp { background-color: var(--bg-light); color: var(--text-color); font-family: 'Inter', sans-serif; }
    div[data-testid="metric-container"] {
        background-color: white; border: 1px solid #e1d3c1; padding: 1rem 1.5rem;
        border-radius: 0.75rem; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
    }
    div[data-testid="metric-container"] label { color: var(--primary) !important; font-weight: 600 !important; font-size: 1.1rem !important; }
    div[data-testid="metric-container"] div[data-testid="stMetricValue"] { color: #2c3e50 !important; font-size: 1.8rem !important; font-weight: 800 !important; }
    section[data-testid="stSidebar"] { background-color: #f6efe8; border-right: 1px solid #e1d3c1; }
    h1, h2, h3 { color: var(--primary) !important; font-weight: 700 !important; }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1>👤 Cotation Individuelle</h1>", unsafe_allow_html=True)
st.markdown("<p style='font-size: 1.1rem; color: #555;'>Simulez un profil client et visualisez la prime technique et commerciale.</p>", unsafe_allow_html=True)
st.divider()

@st.cache_data
def load_data():
    df_totale = pd.read_csv("data/table_prime_pure_totale.csv")
    df_complete = pd.read_csv("data/table_prime_pure_complete.csv")
    return df_totale, df_complete

try:
    df_totale, df_complete = load_data()
except Exception as e:
    st.error(f"Erreur de chargement des données: {e}")
    st.stop()

# --- Sidebar Inputs ---
st.sidebar.markdown("<h3 style='color: #8c4b27;'>⚙️ Paramètres du Profil</h3>", unsafe_allow_html=True)

classe_age_label = st.sidebar.selectbox("Classe d'âge", list(CLASSES_AGE.values()), index=3)
classe_age = list(CLASSES_AGE.keys())[list(CLASSES_AGE.values()).index(classe_age_label)]
sexe = st.sidebar.radio("Sexe", ["M", "F"], horizontal=True)
filiation = st.sidebar.selectbox("Filiation", ["ASSURÉ PRINCIPAL", "CONJOINT", "ENFANT"])
ald_str = "Oui"
zone = st.sidebar.selectbox("Zone Géographique", ["ABIDJAN", "HORS-ABIDJAN"])
contrat = st.sidebar.selectbox("Type de contrat", ["COLLECTIF", "INDIVIDUEL"])

row = lookup_prime_pure(df_totale, classe_age, sexe, filiation, ald_str, zone, contrat)

if row is None:
    st.warning("⚠️ Ce profil exact n'existe pas dans la base d'apprentissage des modèles (ex: Enfant de 61+ ans). Veuillez ajuster les paramètres.")
else:
    pp_val = row['pp_totale']
    res = calculer_prime_ttc(pp_val)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(label="Prime Pure Modèle", value=format_fcfa(res['prime_pure']))
    with col2:
        st.metric(label="Majoration Risque (+45%)", value=format_fcfa(res['majoration']))
    with col3:
        frais = res['accessoires'] + res['deces'] + res['psy'] + res['taxes']
        st.metric(label="Frais, Garanties & Taxes", value=format_fcfa(frais))
    with col4:
        st.metric(label="PRIME TTC FINALE", value=format_fcfa(res['ttc']))
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Table of breakdown
    df_postes = lookup_prime_par_poste(df_complete, classe_age, sexe, filiation, ald_str, zone, contrat)
    st.markdown("### Détail par Poste de Consommation", unsafe_allow_html=True)
    if df_postes is not None and not df_postes.empty:
        df_display = df_postes.copy()
        df_display['Fréquence'] = df_display['freq_predite'].apply(lambda x: f"{x:.2f}" if pd.notnull(x) else "")
        df_display['Sévérité'] = df_display['cout_predit'].apply(lambda x: format_fcfa(x) if pd.notnull(x) else "")
        df_display['Prime Pure'] = df_display['prime_pure'].apply(format_fcfa)
        df_display['Risque (+45%)'] = (df_postes['prime_pure'] * 0.45).apply(format_fcfa)
        df_display['Prime Chargée'] = (df_postes['prime_pure'] * 1.45).apply(format_fcfa)
        
        df_display = df_display[['POSTE_CONSOMMATION', 'Fréquence', 'Sévérité', 'Prime Pure', 'Risque (+45%)', 'Prime Chargée']]
        df_display.rename(columns={'POSTE_CONSOMMATION': 'Poste de Soin'}, inplace=True)
        st.dataframe(df_display, use_container_width=True, hide_index=True)
        
    st.info(f"**Intervalle de Confiance** (95%) : La prime pure estimée est de **{format_fcfa(pp_val)}**, avec une fourchette Bootstrap allant de {format_fcfa(row['pp_ic_low'])} à {format_fcfa(row['pp_ic_high'])}.")
