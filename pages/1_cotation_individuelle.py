import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os
import sys

# Append parent dir to path to import utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.config import CLASSES_AGE, COLOR_MAIN, COLOR_SEC, COLOR_ACCENT, COLOR_PALETTE
from utils.pricing import calculer_prime_ttc, lookup_prime_pure, lookup_prime_par_poste, format_fcfa

st.set_page_config(page_title="Cotation Individuelle", page_icon="👤", layout="wide")

st.markdown("<h1 style='color: #8c4b27;'>👤 Cotation Individuelle</h1>", unsafe_allow_html=True)
st.markdown("<p style='font-size: 1.1rem; color: #555;'>Simulez un profil client et visualisez la composition de la prime technique et commerciale.</p>", unsafe_allow_html=True)
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
ald_str = st.sidebar.radio("Affections Longue Durée (ALD)", ["Non", "Oui"], horizontal=True)
ald = 1 if ald_str == "Oui" else 0
zone = st.sidebar.selectbox("Zone Géographique", ["ABIDJAN", "HORS-ABIDJAN"])
contrat = st.sidebar.selectbox("Type de contrat", ["COLLECTIF", "INDIVIDUEL"])

# Lookup
row = lookup_prime_pure(df_totale, classe_age, sexe, filiation, ald, zone, contrat)

if row is None:
    st.warning("⚠️ Ce profil exact n'existe pas dans la base d'apprentissage des modèles (ex: Enfant de 61+ ans). Veuillez ajuster les paramètres.")
else:
    pp_val = row['pp_totale']
    res = calculer_prime_ttc(pp_val)
    
    # --- Section KPI (Metrics) ---
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(label="Prime Pure Modèle", value=format_fcfa(res['prime_pure']), help="Espérance brute de la sinistralité")
    with col2:
        st.metric(label="Majoration Risque (+45%)", value=format_fcfa(res['majoration']), help="Couverture anti-sélection et aléa moral")
    with col3:
        frais = res['accessoires'] + res['deces'] + res['psy'] + res['taxes']
        st.metric(label="Frais, Garanties & Taxes", value=format_fcfa(frais), help="Décès (20k), Psy (35k), Acc (10k), Taxes (8%)")
    with col4:
        st.metric(label="PRIME TTC FINALE", value=format_fcfa(res['ttc']))
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    # --- Détails ---
    col_chart1, col_chart2 = st.columns([1, 1])
    
    # Waterfall Chart
    with col_chart1:
        st.markdown("<h3 style='color: #8c4b27; text-align: center;'>Cascade Tarifaire</h3>", unsafe_allow_html=True)
        fig_wf = go.Figure(go.Waterfall(
            name="20", orientation="v",
            measure=["absolute", "relative", "relative", "relative", "relative", "relative", "total"],
            x=["Prime Pure", "Risque (+45%)", "Accessoires", "Décès", "Assistance", "Taxes (8%)", "TTC"],
            textposition="outside",
            text=[format_fcfa(res['prime_pure']), format_fcfa(res['majoration']), format_fcfa(res['accessoires']), format_fcfa(res['deces']), format_fcfa(res['psy']), format_fcfa(res['taxes']), format_fcfa(res['ttc'])],
            y=[res['prime_pure'], res['majoration'], res['accessoires'], res['deces'], res['psy'], res['taxes'], res['ttc']],
            connector={"line":{"color":"#e1d3c1"}},
            decreasing={"marker":{"color": COLOR_SEC}},
            increasing={"marker":{"color": COLOR_MAIN}},
            totals={"marker":{"color": COLOR_ACCENT}}
        ))
        fig_wf.update_layout(
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=20, r=20, t=30, b=20),
            yaxis=dict(showgrid=True, gridcolor="#f0e9e1", zeroline=False),
            xaxis=dict(showgrid=False)
        )
        st.plotly_chart(fig_wf, use_container_width=True)

    # Donut Chart
    with col_chart2:
        df_postes = lookup_prime_par_poste(df_complete, classe_age, sexe, filiation, ald_str, zone, contrat)
        if df_postes is not None and not df_postes.empty:
            st.markdown("<h3 style='color: #8c4b27; text-align: center;'>Répartition par Poste</h3>", unsafe_allow_html=True)
            # Remove Total row if exists for pie chart
            df_pie = df_postes[df_postes['POSTE_CONSOMMATION'] != 'TOTAL']
            
            fig_pie = go.Figure(data=[go.Pie(
                labels=df_pie['POSTE_CONSOMMATION'], 
                values=df_pie['prime_pure'], 
                hole=.45,
                textinfo='label+percent',
                textposition='inside',
                insidetextorientation='radial'
            )])
            fig_pie.update_layout(
                plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=20, r=20, t=30, b=20),
                showlegend=False
            )
            fig_pie.update_traces(marker=dict(colors=COLOR_PALETTE, line=dict(color='#FFFFFF', width=2)))
            st.plotly_chart(fig_pie, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
    
    # Table of breakdown
    st.markdown("<h3 style='color: #8c4b27;'>Détail par Poste de Consommation</h3>", unsafe_allow_html=True)
    if df_postes is not None and not df_postes.empty:
        df_display = df_postes.copy()
        
        # Format the numbers nicely for the table
        df_display['Fréquence'] = df_display['freq_predite'].apply(lambda x: f"{x:.2f}" if pd.notnull(x) else "")
        df_display['Sévérité'] = df_display['cout_predit'].apply(lambda x: format_fcfa(x) if pd.notnull(x) else "")
        df_display['Prime Pure'] = df_display['prime_pure'].apply(format_fcfa)
        
        # Majoration and Chargee
        df_display['Risque (+45%)'] = (df_postes['prime_pure'] * 0.45).apply(format_fcfa)
        df_display['Prime Chargée'] = (df_postes['prime_pure'] * 1.45).apply(format_fcfa)
        
        df_display = df_display[['POSTE_CONSOMMATION', 'Fréquence', 'Sévérité', 'Prime Pure', 'Risque (+45%)', 'Prime Chargée']]
        df_display.rename(columns={'POSTE_CONSOMMATION': 'Poste de Soin'}, inplace=True)
        
        # Display using dataframe with custom styling via pandas styler if needed, or simply st.dataframe
        st.dataframe(df_display, use_container_width=True, hide_index=True)
        
    st.info(f"**Intervalle de Confiance** (95%) : La prime pure estimée est de **{format_fcfa(pp_val)}**, avec une fourchette Bootstrap allant de {format_fcfa(row['pp_ic_low'])} à {format_fcfa(row['pp_ic_high'])}.")

