import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.config import COLOR_MAIN, COLOR_SEC, COLOR_ACCENT, COLOR_PALETTE
from utils.pricing import format_fcfa

st.set_page_config(page_title="Tableau de Bord", page_icon="📊", layout="wide")

st.markdown("<h1 style='color: #8c4b27;'>📊 Tableau de Bord du Portefeuille</h1>", unsafe_allow_html=True)
st.markdown("<p style='font-size: 1.1rem; color: #555;'>Visualisation globale des 481 segments tarifaires modélisés.</p>", unsafe_allow_html=True)
st.divider()

@st.cache_data
def load_data():
    return pd.read_csv("data/table_prime_pure_totale.csv")

try:
    df = load_data()
except Exception as e:
    st.error(f"Erreur de chargement: {e}")
    st.stop()

col1, col2 = st.columns(2)

with col1:
    st.markdown("<h3 style='color: #8c4b27; text-align: center;'>Distribution de la Prime Pure</h3>", unsafe_allow_html=True)
    fig_hist = px.histogram(
        df, x="pp_totale", 
        nbins=40, 
        color_discrete_sequence=[COLOR_MAIN],
        labels={"pp_totale": "Prime Pure (FCFA)"}
    )
    fig_hist.update_layout(
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        yaxis_title="Nombre de Profils",
        xaxis=dict(showgrid=True, gridcolor="#f0e9e1"),
        yaxis=dict(showgrid=True, gridcolor="#f0e9e1")
    )
    st.plotly_chart(fig_hist, use_container_width=True)

with col2:
    st.markdown("<h3 style='color: #8c4b27; text-align: center;'>Courbe d'Âge par Sexe</h3>", unsafe_allow_html=True)
    df_mean_age = df.groupby(['CLASSE_AGE', 'SEXE'])['pp_totale'].mean().reset_index()
    fig_line = px.line(
        df_mean_age, x="CLASSE_AGE", y="pp_totale", color="SEXE",
        markers=True,
        color_discrete_map={"M": COLOR_SEC, "F": COLOR_ACCENT},
        labels={"CLASSE_AGE": "Classe d'Âge (1=Jeune, 10=Senior)", "pp_totale": "Prime Pure Moyenne (FCFA)"}
    )
    fig_line.update_layout(
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showgrid=True, gridcolor="#f0e9e1", tickmode='linear'),
        yaxis=dict(showgrid=True, gridcolor="#f0e9e1"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig_line, use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)

col3, col4 = st.columns(2)

with col3:
    st.markdown("<h3 style='color: #8c4b27;'>🔴 Top 5 Profils les plus coûteux</h3>", unsafe_allow_html=True)
    top_5 = df.nlargest(5, 'pp_totale')[['CLASSE_AGE', 'SEXE', 'FILIATION', 'AFFECTION_CHR_NUM', 'pp_totale']]
    top_5['AFFECTION_CHR_NUM'] = top_5['AFFECTION_CHR_NUM'].map({1: 'Oui', 0: 'Non'})
    top_5['pp_totale'] = top_5['pp_totale'].apply(format_fcfa)
    top_5.columns = ['Âge', 'Sexe', 'Filiation', 'ALD', 'Prime Pure']
    st.dataframe(top_5, use_container_width=True, hide_index=True)

with col4:
    st.markdown("<h3 style='color: #8c4b27;'>🟢 Top 5 Profils les plus économiques</h3>", unsafe_allow_html=True)
    bot_5 = df.nsmallest(5, 'pp_totale')[['CLASSE_AGE', 'SEXE', 'FILIATION', 'AFFECTION_CHR_NUM', 'pp_totale']]
    bot_5['AFFECTION_CHR_NUM'] = bot_5['AFFECTION_CHR_NUM'].map({1: 'Oui', 0: 'Non'})
    bot_5['pp_totale'] = bot_5['pp_totale'].apply(format_fcfa)
    bot_5.columns = ['Âge', 'Sexe', 'Filiation', 'ALD', 'Prime Pure']
    st.dataframe(bot_5, use_container_width=True, hide_index=True)
