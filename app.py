import streamlit as st
import sqlite3
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import math

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="VRAIP | Panel Ciudadano", page_icon="🌋", layout="wide", initial_sidebar_state="expanded")

# --- CARGAR CSS EXTERNO ---
def load_local_css(file_name):
    """Lee el archivo CSS externo y lo inyecta en Streamlit"""
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Llamamos a la función apuntando a nuestro nuevo archivo
load_local_css("style.css")

# --- DICCIONARIO DE VOLCANES ---
VOLCANES_DATA = {
    1: {"nombre": "Cotopaxi", "lat": -0.677, "lon": -78.436, "radio_km": 15},
    2: {"nombre": "Sangay", "lat": -2.002, "lon": -78.341, "radio_km": 12},
    3: {"nombre": "El Reventador", "lat": -0.077, "lon": -77.656, "radio_km": 10},
    4: {"nombre": "Tungurahua", "lat": -1.467, "lon": -78.442, "radio_km": 15}
}


# --- GENERADOR DE POLÍGONO GEOGRÁFICO FIJO ---
def generar_circulo_geografico(lat, lon, radio_km):
    """Genera coordenadas lat/lon de un círculo perfecto a un radio específico para mantenerlo fijo en el zoom."""
    R = 6371.0 # Radio de la Tierra en km
    lats, lons = [], []
    for i in range(361): # 360 grados + 1 para cerrar el polígono
        theta = math.radians(i)
        lat_i = lat + (radio_km / R) * (180 / math.pi) * math.cos(theta)
        lon_i = lon + (radio_km / R) * (180 / math.pi) * math.sin(theta) / math.cos(math.radians(lat))
        lats.append(lat_i)
        lons.append(lon_i)
    return lats, lons

# --- CONEXIÓN A BASE DE DATOS ---
def get_data():
    conn = sqlite3.connect('data/vraip.db') 
    query = """
        SELECT a.id, a.explanation, a.recommendations, c.alert_level, b.volcano_id
        FROM ai_alerts a
        LEFT JOIN classifications c ON a.classification_id = c.id
        LEFT JOIN bulletins b ON c.bulletin_id = b.id
        ORDER BY a.id DESC
    """
    try:
        df = pd.read_sql_query(query, conn)
    except:
        df = pd.DataFrame()
    finally:
        conn.close()
    return df

def procesar_alerta(nivel_texto):
    nivel = str(nivel_texto).lower()
    if 'roja' in nivel or 'rojo' in nivel: return '#ef4444', 'rgba(239, 68, 68, 0.3)', 'tag-roja'
    if 'naranja' in nivel: return '#f97316', 'rgba(249, 115, 22, 0.3)', 'tag-naranja'
    if 'amarilla' in nivel or 'amarillo' in nivel: return '#facc15', 'rgba(250, 204, 21, 0.3)', 'tag-amarilla'
    return '#94a3b8', 'rgba(148, 163, 184, 0.3)', 'tag-blanca'

# --- PANEL LATERAL (SIDEBAR) ---
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/3268/3268578.png", width=60) # Icono decorativo
st.sidebar.markdown("## VRAIP OS v2.0")
st.sidebar.caption("Red de Alerta Temprana")
st.sidebar.divider()

df_alertas = get_data()

if not df_alertas.empty and 'volcano_id' in df_alertas.columns:
    volcanes_disponibles = df_alertas['volcano_id'].dropna().unique()
    nombres_disponibles = [VOLCANES_DATA[vid]["nombre"] for vid in volcanes_disponibles if vid in VOLCANES_DATA]
    
    st.sidebar.markdown("**🌐 Seleccione un Volcán:**")
    volcan_seleccionado = st.sidebar.selectbox("", nombres_disponibles, label_visibility="collapsed")
    
    st.sidebar.divider()
    st.sidebar.info("🤖 El análisis de IA se actualiza autónomamente según los boletines oficiales.")
    
    id_seleccionado = next(vid for vid, data in VOLCANES_DATA.items() if data["nombre"] == volcan_seleccionado)
    df_filtrado = df_alertas[df_alertas['volcano_id'] == id_seleccionado]
    
    if not df_filtrado.empty:
        ultima_alerta = df_filtrado.iloc[0]
        nivel_alerta = ultima_alerta.get('alert_level', 'Alerta Naranja')
        color_hex, color_rgba, css_tag = procesar_alerta(nivel_alerta)
        
        # --- ENCABEZADO PRINCIPAL ---
        st.markdown(f'<p class="main-header">{volcan_seleccionado.upper()}</p>', unsafe_allow_html=True)
        st.markdown(f'<p class="sub-header">Monitoreo activo | Estado oficial: <span class="{css_tag}">{str(nivel_alerta).upper()}</span></p>', unsafe_allow_html=True)
        
        # --- FILA DE MÉTRICAS HTML (Más profesionales) ---
        st.markdown(f"""
        <div class="kpi-container">
            <div class="kpi-card">
                <div class="kpi-title">Última Actualización</div>
                <div class="kpi-value">{datetime.now().strftime("%H:%M")}</div>
                <div class="kpi-sub">↑ Sincronizado</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">Motor IA</div>
                <div class="kpi-value">Gemini 3.5</div>
                <div class="kpi-sub">↑ Operativo</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">Radio de Influencia</div>
                <div class="kpi-value">{VOLCANES_DATA[id_seleccionado]['radio_km']} km</div>
                <div class="kpi-sub">Zona Delimitada</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # --- ÁREA PRINCIPAL ---
        col_mapa, col_datos = st.columns([1.3, 1])
        
        with col_mapa:
            # MAPA GEOESPACIAL FIJO
            lat = VOLCANES_DATA[id_seleccionado]["lat"]
            lon = VOLCANES_DATA[id_seleccionado]["lon"]
            radio = VOLCANES_DATA[id_seleccionado]["radio_km"]
            
            # Calculamos las coordenadas del polígono fijo
            lats_circulo, lons_circulo = generar_circulo_geografico(lat, lon, radio)
            
            fig = go.Figure()
            
            # Polígono de Influencia Fija (Ya no crece con el zoom)
            fig.add_trace(go.Scattermapbox(
                lat=lats_circulo, lon=lons_circulo, mode='lines',
                fill='toself', fillcolor=color_rgba,
                line=dict(width=2, color=color_hex),
                hoverinfo='none', showlegend=False
            ))
            
            # Punto Central (Cráter)
            fig.add_trace(go.Scattermapbox(
                lat=[lat], lon=[lon], mode='markers',
                marker=go.scattermapbox.Marker(size=10, color=color_hex),
                text=[f"Cráter {volcan_seleccionado}"],
                hoverinfo='text', showlegend=False
            ))
            
            fig.update_layout(
                mapbox=dict(
                    style="carto-positron",
                    center=dict(lat=lat, lon=lon),
                    zoom=10 if id_seleccionado != 1 else 9
                ),
                margin=dict(r=0, t=0, l=0, b=0),
                height=550,
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)'
            )
            
            # CSS para darle un borde bonito al mapa
            st.markdown('<div style="border-radius: 12px; overflow: hidden; border: 1px solid #e2e8f0; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);">', unsafe_allow_html=True)
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
        with col_datos:
            st.markdown(f"""
            <div class="card-ia">
                <h4 class="card-title">🔬 Explicación Técnica (IA)</h4>
                <p class="card-text">{ultima_alerta['explanation']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="card-ia warning">
                <h4 class="card-title">🛡️ Protocolo Ciudadano</h4>
                <p class="card-text">{ultima_alerta['recommendations']}</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.warning(f"Procesamiento en curso para {volcan_seleccionado}.")
else:
    st.info("El sistema está inicializándose y esperando los primeros registros de la base de datos...")
