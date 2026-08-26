import streamlit as st
import pandas as pd
import io
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.pricing import calculer_prime_ttc, lookup_prime_pure, format_fcfa

st.title("Cotation Groupe")

@st.cache_data
def load_data():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    try:
        return pd.read_csv(os.path.join(base_dir, 'data', 'table_prime_pure_totale.csv'))
    except FileNotFoundError:
        return None

df_totale = load_data()

if df_totale is None:
    st.error("Données introuvables. Assurez-vous que le fichier csv est présent.")
    st.stop()

st.write("Téléchargez un fichier Excel ou CSV contenant les profils à coter.")

template = pd.DataFrame({
    'CLASSE_AGE': [3, 4],
    'SEXE': ['M', 'F'],
    'FILIATION': ['ASSURÉ PRINCIPAL', 'CONJOINT'],
    'ALD': ['Non', 'Oui'],
    'ZONE_GEO': ['ABIDJAN', 'HORS-ABIDJAN'],
    'TYPE_CONTRAT': ['COLLECTIF', 'COLLECTIF']
})

csv_template = template.to_csv(index=False).encode('utf-8')
st.download_button("Télécharger le template", csv_template, "template_groupe.csv", "text/csv")

uploaded_file = st.file_uploader("Fichier de profils", type=["csv", "xlsx"])

if uploaded_file:
    if uploaded_file.name.endswith('.csv'):
        df_input = pd.read_csv(uploaded_file)
    else:
        df_input = pd.read_excel(uploaded_file)
    
    results = []
    for _, row in df_input.iterrows():
        try:
            pp_row = lookup_prime_pure(
                df_totale, 
                row['CLASSE_AGE'], 
                row['SEXE'], 
                row['FILIATION'], 
                row['ALD'], 
                row['ZONE_GEO'], 
                row['TYPE_CONTRAT']
            )
            if pp_row is not None:
                ttc_data = calculer_prime_ttc(pp_row['pp_totale'])
                res = row.to_dict()
                res['Prime Pure'] = pp_row['pp_totale']
                res['TTC Final'] = ttc_data['ttc']
                results.append(res)
            else:
                res = row.to_dict()
                res['Prime Pure'] = None
                res['TTC Final'] = None
                results.append(res)
        except Exception as e:
            res = row.to_dict()
            res['Prime Pure'] = None
            res['TTC Final'] = None
            results.append(res)
            
    df_results = pd.DataFrame(results)
    st.dataframe(df_results, use_container_width=True)
    
    valid_results = df_results.dropna(subset=['TTC Final'])
    if not valid_results.empty:
        st.subheader("Résumé")
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("Nombre", len(valid_results))
        col2.metric("Moyenne", format_fcfa(valid_results['TTC Final'].mean()))
        col3.metric("Min", format_fcfa(valid_results['TTC Final'].min()))
        col4.metric("Max", format_fcfa(valid_results['TTC Final'].max()))
        col5.metric("Total", format_fcfa(valid_results['TTC Final'].sum()))
        
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df_results.to_excel(writer, index=False)
        st.download_button(
            label="Télécharger les résultats (Excel)",
            data=output.getvalue(),
            file_name="resultats_cotation_groupe.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
