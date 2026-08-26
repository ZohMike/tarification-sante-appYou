import streamlit as st
import pandas as pd
import plotly.express as px
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.config import COLOR_MAIN, COLOR_SEC, COLOR_ACCENT

st.title("Impact du Réseau de Soins")

@st.cache_data
def load_network_data():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data = {}
    for f in ['scenarios.csv', 'impact_poste.csv', 'scoring_data.csv', 'redirection.csv']:
        path = os.path.join(base_dir, 'data', f)
        if os.path.exists(path):
            data[f.split('.')[0]] = pd.read_csv(path)
        else:
            data[f.split('.')[0]] = None
    return data

data = load_network_data()

if data.get('scenarios') is not None:
    st.subheader("Comparaison des Scénarios")
    scen_df = data['scenarios']
    st.dataframe(scen_df, use_container_width=True)
    if 'economie' in scen_df.columns and 'scenario' in scen_df.columns:
        fig = px.bar(scen_df, x='scenario', y='economie', title="Economies par scénario", color_discrete_sequence=[COLOR_MAIN])
        st.plotly_chart(fig, use_container_width=True)

if data.get('impact_poste') is not None:
    st.subheader("Impact par Poste")
    ip_df = data['impact_poste']
    st.dataframe(ip_df, use_container_width=True)

if data.get('scoring_data') is not None:
    st.subheader("Scoring des Prestataires")
    sd_df = data['scoring_data']
    st.dataframe(sd_df, use_container_width=True)

if data.get('redirection') is not None:
    st.subheader("Top 15 des Opportunités de Redirection")
    red_df = data['redirection']
    st.dataframe(red_df.head(15), use_container_width=True)

if all(v is None for v in data.values()):
    st.info("Aucune donnée de réseau de soins disponible.")
