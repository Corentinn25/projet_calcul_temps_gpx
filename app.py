import streamlit as st
import pandas as pd
import plotly.express as px
from src.parser import parse_gpx
from src.segmenter import compute_segments
from src.calculateur import estimer_temps_utmb_2_0

# --- CONFIGURATION & STYLE ---
st.set_page_config(page_title="Trail Splitter Pro", layout="wide", page_icon="🏃")

# Correction de l'argument unsafe_allow_html
st.markdown("""
    <style>
    [data-testid="stMetricValue"] { font-size: 1.8rem !important; color: #2ecc71 !important; }
    [data-testid="stMetric"] { background-color: #f8f9fa; padding: 15px; border-radius: 10px; border: 1px solid #e9ecef; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏃 Trail Splitter : Planificateur de Course")

# --- BARRE LATÉRALE ---
st.sidebar.header("📁 Données")
uploaded_file = st.sidebar.file_uploader("Fichier GPX", type=['gpx'])

if uploaded_file is not None:
    # 1. Parsing et calculs globaux
    df = parse_gpx(uploaded_file)
    total_dist = df['dist_cum'].max()
    total_dplus = df['ele_diff'].clip(lower=0).sum()
    # Calcul du D- total pour le nouveau moteur de calcul
    total_dmoins = abs(df['ele_diff'].clip(upper=0).sum())
    
    # Distance-Effort totale (Logique UTMB : D+/100 + D-/200)
    km_e_total = total_dist + (total_dplus / 100) + (total_dmoins / 200)
    df['dplus_cum'] = df['ele_diff'].clip(lower=0).cumsum()

    # Pourcentage pente
    df['dplus_cum'] = df['ele_diff'].clip(lower=0).cumsum()
    # Pente % = (différence altitude / différence distance) * 100
    # On évite la division par zéro avec fillna
    dist_diff = df['dist_cum'].diff().fillna(0)
    df['pente'] = (df['ele_diff'] / (dist_diff * 1000)) * 100 
    df['pente'] = df['pente'].fillna(0).replace([float('inf'), float('-inf')], 0)

    # 2. Réglages utilisateur
    st.sidebar.divider()
    seuil_segment = st.sidebar.slider("Sensibilité du relief (m)", 30, 200, 50)
    tolerance = st.sidebar.slider("Lissage terrain (m)", 10, 100, 50)
    cote_utmb = st.sidebar.number_input("Ta Cote UTMB", 300, 999, 600)





   # 3. Segmentation & Calcul des temps
    df_segments = compute_segments(df, threshold=seuil_segment, tolerance=tolerance)
    
    if not df_segments.empty:
        # Calcul du temps segment par segment (pour éviter l'explosion du facteur fatigue)
        df_segments['Minutes'] = df_segments.apply(
            lambda x: estimer_temps_utmb_2_0(x['Distance (km)'], x['D+ (m)'], x['D- (m)'], cote_utmb), 
            axis=1
        )
        t_min_total = df_segments['Minutes'].sum()
    else:
        t_min_total = estimer_temps_utmb_2_0(total_dist, total_dplus, total_dmoins, cote_utmb)

    # --- 3. Métriques de performance (Sidebar) ---
    allure_reelle_dec = t_min_total / total_dist
    allure_effort_dec = t_min_total / km_e_total
    
    def fmt_ms(m): return f"{int(m)}:{int((m%1)*60):02d}"
    def fmt_hms(m): return f"{int(m//60)}h{int(m%60):02d}"

    st.sidebar.markdown("### 📊 Analyse de la course")
    
    # Affichage des textes demandés
    st.sidebar.write(f"**Temps estimé :** {fmt_hms(t_min_total)}")
    st.sidebar.write(f"**Allure :** {fmt_ms(allure_reelle_dec)} min/km")
    st.sidebar.write(f"**Allure km effort :** {fmt_ms(allure_effort_dec)} min/km*")
    
    # L'astérisque avec le détail du calcul
    st.sidebar.caption(f"*Le kilomètre-effort (km-e) simule la difficulté du dénivelé. "
                       f"Calcul pour ce GPX : {total_dist:.1f}km + {total_dplus:.0f}m D+/100 + {total_dmoins:.0f}m D-/200 "
                       f"= **{km_e_total:.2f} km-e**.")





    # 4. Graphique Altitométrique
    st.subheader(f"Profil Altitométrique : {total_dist:.1f}km | {total_dplus:.0f}m D+ | {total_dmoins:.0f}m D-")
    
    fig = px.area(df, x='dist_cum', y='ele', color_discrete_sequence=['#2ecc71'], 
                  custom_data=['dist_cum', 'ele', 'dplus_cum', 'pente'])

    if not df_segments.empty:
        for i, row in df_segments.iterrows():
            # Alternance de couleurs pour la lisibilité
            bg_color = "rgba(46, 204, 113, 0.15)" if i % 2 == 0 else "rgba(52, 152, 219, 0.1)"
            
            start_x = row['Cumul (km)'] - row['Distance (km)']
            end_x = row['Cumul (km)']
            
            # Correction Error ValueError: gestion des noms de sections textuels
            label = f"S{row['Section']}" if str(row['Section']).isdigit() else row['Section']
            
            fig.add_vrect(
                x0=start_x, x1=end_x,
                fillcolor=bg_color, layer="below", line_width=1,
                line_color="rgba(0,0,0,0.1)"
            )
            
            fig.add_annotation(
                x=(start_x + end_x) / 2,
                y=df['ele'].max() * 1.05,
                text=label,
                showarrow=False,
                textangle=-45,
                font=dict(size=10, color="white"),
                bgcolor="rgba(0,0,0,0.5)",
                borderpad=2
            )
    
    fig.update_traces(
        hovertemplate="<b>Dist :</b> %{customdata[0]:.2f}km<br>" +
                      "<b>Alt :</b> %{customdata[1]:.0f}m<br>" +
                      "<b>Pente :</b> %{customdata[3]:.1f}%<br>" + # <-- La nouvelle ligne
                      "<b>D+ cum :</b> %{customdata[2]:.0f}m<extra></extra>"
    )

    fig.update_layout(
        height=500, 
        margin=dict(l=0, r=0, t=50, b=0), 
        hovermode="x unified",
        yaxis=dict(range=[0, df['ele'].max() * 1.25])
    )
    st.plotly_chart(fig, use_container_width=True)



    # 5. Tableau de marche (Roadbook)
    st.divider()
    if not df_segments.empty:
        # Application du nouveau calculateur sur chaque ligne
        df_segments['Minutes'] = df_segments.apply(
            lambda x: estimer_temps_utmb_2_0(x['Distance (km)'], x['D+ (m)'], x['D- (m)'], cote_utmb), 
            axis=1
        )
        df_segments['Temps Cumulé'] = df_segments['Minutes'].cumsum()
        
        def format_pace(row):
            p = row['Minutes'] / row['Distance (km)']
            return f"{int(p):02d}:{int((p%1)*60):02d}"

        df_segments['Allure (min/km)'] = df_segments.apply(format_pace, axis=1)
        fmt_t = lambda m: f"{int(m//60)}h{int(m%60):02d}"
        df_segments['Chrono'] = df_segments['Minutes'].apply(fmt_t)
        df_segments['Passage'] = df_segments['Temps Cumulé'].apply(fmt_t)

        st.dataframe(
            df_segments[['Section', 'Distance (km)', 'Cumul (km)', 'D+ (m)', 'D- (m)', 'Pente moy (%)', 'Allure (min/km)', 'Chrono', 'Passage']]
            .style.background_gradient(subset=['Pente moy (%)'], cmap='RdYlGn_r', vmin=-15, vmax=15)
            .format({"Distance (km)": "{:.1f}", "Cumul (km)": "{:.1f}", "D+ (m)": "{:.0f}", "D- (m)": "{:.0f}", "Pente moy (%)": "{:.1f}"}),
            use_container_width=True, hide_index=True
        )
        st.success(f"### **🏁 Objectif de temps total : {fmt_t(df_segments['Minutes'].sum())}**")
else:
    st.info("👈 Charge ton fichier GPX pour commencer la planification.")