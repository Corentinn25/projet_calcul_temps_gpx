import streamlit as st
from src.parser import parse_gpx
import plotly.express as px

st.set_page_config(page_title="Trail Splitter", layout="wide")

st.title("🏃 Trail Splitter")

# Zone d'upload
uploaded_file = st.sidebar.file_uploader("Charge ton fichier GPX", type=['gpx'])

if uploaded_file is not None:
    df = parse_gpx(uploaded_file)
    
    # On arrondit pour l'affichage
    df['dist_cum_label'] = df['dist_cum'].round(2)
    df['dplus_cum_label'] = df['dplus_cum'].astype(int)
    df['pente_label'] = df['pente'].round(1)

    st.subheader("Profil d'élévation")
    
    # Création du graphique
   # Création du graphique
    fig = px.area(
        df, 
        x='dist_cum', 
        y='ele',
        custom_data=['dplus_cum_label', 'pente_label'],
        color_discrete_sequence=['#2ecc71']
    )

    # Configuration simplifiée du Hover
    fig.update_traces(
        hovertemplate="""
        <b>Données</b><br>
        Distance: %{x:.2f} km<br>
        Altitude: %{y} m<br>
        D+ cumulé: %{customdata[0]} m<br>
        Pente: %{customdata[1]} %
        <extra></extra>
        """
    )

    fig.update_layout(
        hovermode="x", # "x" permet d'avoir l'info-bulle sans le titre noir en haut
        xaxis_title="Distance (km)",
        yaxis_title="Altitude (m)",
        hoverlabel=dict(namelength=0) # Sécurité pour cacher les noms de traces
    )

    st.plotly_chart(fig, use_container_width=True)
    
else:
    st.info("👈 Commence par charger un fichier GPX dans la barre latérale !")

    #test