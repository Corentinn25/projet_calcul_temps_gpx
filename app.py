import streamlit as st
import pandas as pd
import plotly.express as px
from src.parser import parse_gpx
from src.segmenter import compute_segments
from src.calculateur import estimer_temps_itra

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="Trail Splitter Pro", layout="wide", page_icon="🏃")
st.title("🏃 Trail Splitter : Modèle 28.5")

# --- BARRE LATÉRALE ---
st.sidebar.header("📁 Données")
uploaded_file = st.sidebar.file_uploader("Charge ton fichier GPX", type=['gpx'])

if uploaded_file is not None:
    # 1. Parsing et calculs globaux
    df = parse_gpx(uploaded_file)
    total_dist = df['dist_cum'].max()
    total_dplus = df['ele_diff'].clip(lower=0).sum()
    km_e_total = total_dist + (total_dplus / 100)
    
    # Ajout du D+ cumulé pour l'info-bulle du graphique
    df['dplus_cum'] = df['ele_diff'].clip(lower=0).cumsum()

    # --- RÉGLAGES SECTIONS ---
    st.sidebar.divider()
    st.sidebar.header("⚙️ Réglages Sections")
    seuil_segment = st.sidebar.slider("Sensibilité (m)", 30, 200, 55, help="Seuil de dénivelé pour créer un nouveau segment.")
    tolerance = st.sidebar.slider("Tolérance (m)", 10, 100, 40, help="Lissage des petites variations de terrain.")

    # --- PERFORMANCE ITRA ---
    st.sidebar.divider()
    st.sidebar.header("⏱️ Performance (ITRA)")
    cote_itra = st.sidebar.number_input(
        "Ta Cote ITRA / UTMB", 
        200, 1000, 612, step=1,
        help="Ton indice de performance officiel ou visé."
    )

    # Calcul des métriques de l'algorithme 28.5
    t_min_total = estimer_temps_itra(total_dist, total_dplus, cote_itra)
    v_km_e_h = (km_e_total / t_min_total) * 60
    vap_decimal = 60 / v_km_e_h
    
    st.sidebar.metric("Vitesse de calcul", f"{v_km_e_h:.2f} km-e/h")
    
    # Affichage de l'allure VAP
    r_m = int(vap_decimal)
    r_s = int((vap_decimal % 1) * 60)
    st.sidebar.info(f"Allure VAP cible : **{r_m:02d}:{r_s:02d} min/km**")
    
    with st.sidebar.expander("ℹ️ C'est quoi la VAP ?"):
        st.write(f"""
        La **Vitesse à Plat (VAP)** est l'allure théorique que tu tiendrais sur du bitume plat avec le même niveau d'effort. 
        L'algorithme utilise cette base pour calculer ton temps réel sur les bosses.
        """)

    # --- ANALYSE VISUELLE (Graphique avec Info-bulle D+ cumulé) ---
    st.subheader(f"Profil d'élévation : {total_dist:.1f}km | {total_dplus:.0f}m D+")
    
    fig = px.area(
        df, 
        x='dist_cum', 
        y='ele', 
        color_discrete_sequence=['#2ecc71'],
        custom_data=['dist_cum', 'ele', 'dplus_cum']
    )

    # Configuration de l'info-bulle (hover) enrichie
    fig.update_traces(
        hovertemplate="<br>".join([
            "<b>Distance :</b> %{customdata[0]:.2f} km",
            "<b>Altitude :</b> %{customdata[1]:.0f} m",
            "<b>D+ cumulé :</b> %{customdata[2]:.0f} m",
            "<extra></extra>"
        ])
    )

    fig.update_layout(
        height=350, 
        margin=dict(l=0, r=0, t=0, b=0),
        xaxis_title="Distance (km)",
        yaxis_title="Altitude (m)",
        hovermode="x unified" # Ligne verticale pour lecture facile
    )
    
    st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # --- TABLEAU DE MARCHE ---
    st.header("📊 Ton Roadbook")
    df_segments = compute_segments(df, threshold=seuil_segment, tolerance=tolerance)

    if not df_segments.empty:
        # Application du calculateur
        df_segments['Minutes'] = df_segments.apply(
            lambda x: estimer_temps_itra(x['Distance (km)'], x['D+ (m)'], cote_itra), 
            axis=1
        )
        
        # Formatages des colonnes
        def format_pace(row):
            p = row['Minutes'] / row['Distance (km)']
            return f"{int(p):02d}:{int((p%1)*60):02d}"

        df_segments['Allure (min/km)'] = df_segments.apply(format_pace, axis=1)
        df_segments['Temps Cumulé'] = df_segments['Minutes'].cumsum()
        
        fmt_t = lambda m: f"{int(m//60)}h{int(m%60):02d}"
        df_segments['Chrono'] = df_segments['Minutes'].apply(fmt_t)
        df_segments['Passage'] = df_segments['Temps Cumulé'].apply(fmt_t)

        # Affichage du tableau final
        cols = ['Section', 'Distance (km)', 'Cumul (km)', 'D+ (m)', 'D- (m)', 'Pente moy (%)', 'Allure (min/km)', 'Chrono', 'Passage']
        st.dataframe(
            df_segments[cols].style.background_gradient(subset=['Pente moy (%)'], cmap='RdYlGn_r', vmin=-15, vmax=15).format(precision=1),
            use_container_width=True, hide_index=True
        )
        
        # Conclusion
        total_m = df_segments['Minutes'].sum()
        st.success(f"### **🏁 Temps total estimé : {fmt_t(total_m)}**")

else:
    st.info("👈 Charge ton fichier GPX pour analyser ton parcours et tes temps de passage.")