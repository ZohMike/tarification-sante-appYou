import streamlit as st

st.set_page_config(
    page_title="Simulateur de Cotation Santé",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS pour rendre l'interface beaucoup plus belle
st.markdown("""
<style>
    :root {
        --primary: #8c4b27;
        --secondary: #d48b59;
        --accent: #c0392b;
        --bg-light: #fdfaf6;
        --text-color: #333333;
    }
    
    /* Couleur de fond générale */
    .stApp {
        background-color: var(--bg-light);
        color: var(--text-color);
        font-family: 'Inter', sans-serif;
    }
    
    /* Customiser les cartes (Metrics) */
    div[data-testid="metric-container"] {
        background-color: white;
        border: 1px solid #e1d3c1;
        padding: 1rem 1.5rem;
        border-radius: 0.75rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
        transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
    }
    div[data-testid="metric-container"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
        border-color: var(--secondary);
    }
    
    /* Couleurs du texte des metrics */
    div[data-testid="metric-container"] label {
        color: var(--primary) !important;
        font-weight: 600 !important;
        font-size: 1.1rem !important;
    }
    div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
        color: #2c3e50 !important;
        font-size: 1.8rem !important;
        font-weight: 800 !important;
    }
    
    /* Customiser la sidebar */
    section[data-testid="stSidebar"] {
        background-color: #f6efe8;
        border-right: 1px solid #e1d3c1;
    }
    section[data-testid="stSidebar"] .stMarkdown h1 {
        color: var(--primary);
    }
    
    /* Titres des pages */
    h1, h2, h3 {
        color: var(--primary) !important;
        font-weight: 700 !important;
    }
    
    /* Tables/DataFrames */
    .stDataFrame {
        border-radius: 0.5rem;
        overflow: hidden;
        border: 1px solid #e1d3c1;
    }
    
    /* Boutons */
    .stButton>button {
        background-color: var(--primary);
        color: white;
        border-radius: 0.5rem;
        border: none;
        padding: 0.5rem 1rem;
        font-weight: 600;
        transition: all 0.2s ease;
    }
    .stButton>button:hover {
        background-color: var(--accent);
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        color: white;
    }
</style>
""", unsafe_allow_html=True)

st.sidebar.markdown(
    """
    <div style='text-align: center; margin-bottom: 20px;'>
        <h1 style='color: #8c4b27; margin-bottom: 0px;'>🏥 Actuaria</h1>
        <p style='color: #d48b59; font-size: 14px; margin-top: 0px;'>Moteur de Tarification Santé</p>
    </div>
    """, 
    unsafe_allow_html=True
)

st.sidebar.divider()
st.sidebar.info("Sélectionnez un outil de cotation dans le menu ci-dessus.")

def main():
    st.markdown("<h1 style='text-align: center; margin-top: 50px;'>Bienvenue dans l'espace Tarification Santé</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 18px; color: #555;'>Moteur actuariel Fréquence × Sévérité basé sur les modèles GLM et Machine Learning.</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div style='background-color: white; padding: 20px; border-radius: 10px; border: 1px solid #e1d3c1; text-align: center; height: 200px;'>
            <h3 style='font-size: 40px; margin: 0;'>👤</h3>
            <h4 style='color: #8c4b27;'>Cotation Individuelle</h4>
            <p style='color: #666; font-size: 14px;'>Simulez un profil client spécifique et visualisez la décomposition tarifaire.</p>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown("""
        <div style='background-color: white; padding: 20px; border-radius: 10px; border: 1px solid #e1d3c1; text-align: center; height: 200px;'>
            <h3 style='font-size: 40px; margin: 0;'>👨‍👩‍👧‍👦</h3>
            <h4 style='color: #8c4b27;'>Cotation Famille</h4>
            <p style='color: #666; font-size: 14px;'>Simulez instantanément la tarification globale pour un foyer (assuré, conjoint, enfants).</p>
        </div>
        """, unsafe_allow_html=True)
        
    with col3:
        st.markdown("""
        <div style='background-color: white; padding: 20px; border-radius: 10px; border: 1px solid #e1d3c1; text-align: center; height: 200px;'>
            <h3 style='font-size: 40px; margin: 0;'>⚕️</h3>
            <h4 style='color: #8c4b27;'>Impact Réseaux</h4>
            <p style='color: #666; font-size: 14px;'>Mesurez l'impact du choix de réseau de soins sur la prime d'assurance.</p>
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
