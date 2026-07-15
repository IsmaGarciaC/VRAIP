import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import os

# 1. Configuración de la página web
st.set_page_config(page_title="VRAIP Dashboard", page_icon="🌋", layout="wide")

# Ruta a la base de datos
DB_PATH = os.path.join(os.path.dirname(__file__), "data", "vraip.db")

def load_data():
    """Extrae la información de SQLite para mostrarla en pantalla."""
    conn = sqlite3.connect(DB_PATH)
    
    # Cargar todos los volcanes para el mapa
    df_volcanoes = pd.read_sql_query("SELECT * FROM volcanoes", conn)
    
    # Cargar la última alerta procesada por la IA
    query_alerts = """
        SELECT v.name as volc_name, c.alert_level, a.explanation, a.recommendations, b.published_at 
        FROM ai_alerts a 
        JOIN classifications c ON a.classification_id = c.id 
        JOIN bulletins b ON c.bulletin_id = b.id 
        JOIN volcanoes v ON b.volcano_id = v.id 
        ORDER BY a.id DESC LIMIT 1
    """
    df_latest_alert = pd.read_sql_query(query_alerts, conn)
    conn.close()
    
    return df_volcanoes, df_latest_alert

# --- INTERFAZ DE USUARIO ---
st.title("🌋 VRAIP: Plataforma de Inteligencia Volcánica")
st.markdown("Monitoreo ciudadano en tiempo real impulsado por Inteligencia Artificial.")
st.markdown("---")

try:
    df_volcanes, df_alerta = load_data()
    
    # Dividimos la pantalla: 70% mapa, 30% panel de alertas
    col1, col2 = st.columns([2, 1])
    
    # Columna Izquierda: El Mapa Geoespacial
    with col1:
        st.subheader("🗺️ Mapa de Monitoreo (Ecuador)")
        
        # Crear mapa interactivo
        fig = px.scatter_mapbox(
            df_volcanes, 
            lat="latitude", 
            lon="longitude", 
            hover_name="name", 
            hover_data=["igepn_code"],
            color_discrete_sequence=["red"],
            zoom=5.5, 
            height=500
        )
        fig.update_layout(mapbox_style="open-street-map")
        fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
        
        st.plotly_chart(fig, use_container_width=True)
        
    # Columna Derecha: El Panel de la IA
    with col2:
        st.subheader("⚠️ Última Alerta Ciudadana")
        
        if not df_alerta.empty:
            alerta = df_alerta.iloc[0]
            
            # Asignar color dinámico según la alerta
            color = "orange" if alerta['alert_level'] == "Naranja" else "red" if alerta['alert_level'] == "Roja" else "green"
            
            st.markdown(f"### Volcán {alerta['volc_name']}")
            st.markdown(f"**Nivel de Alerta Técnica:** :{color}[**{alerta['alert_level'].upper()}**]")
            st.caption(f"Fecha del reporte: {alerta['published_at']}")
            
            st.info(f"**¿Qué significa esto?**\n\n{alerta['explanation']}")
            st.warning(f"**¿Qué debes hacer?**\n\n{alerta['recommendations']}")
        else:
            st.write("No hay alertas procesadas aún.")
            
except Exception as e:
    st.error(f"Error al cargar el dashboard: {e}")
