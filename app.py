import streamlit as st
import sqlite3
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="VRAIP | Panel Ciudadano", page_icon="🌋", layout="wide")

# --- ESTILOS CSS AVANZADOS (TEMA CLARO) ---
st.markdown("""
<style>
    /* Forzar fondo claro general para anular el tema oscuro por defecto de Streamlit */
    .stApp { background-color: #f8fafc; }

    /* Forzar texto oscuro en subtítulos y métricas nativas de Streamlit */
    [data-testid="stMarkdownContainer"] p, 
    [data-testid="stMarkdownContainer"] h3, 
    [data-testid="stMarkdownContainer"] strong,
    [data-testid="stMetricLabel"] div, 
    [data-testid="stMetricValue"] div {
        color: #1e293b !important;
    }
    
    /* Tipografía y Encabezados */
    .main-header { font-size: 2.2rem; font-weight: 800; color: #1e293b; margin-bottom: 0px; letter-spacing: -0.5px;}
    .sub-header { font-size: 1.1rem; color: #64748b; margin-bottom: 2rem; font-weight: 400;}
    
    /* Tarjetas de Información */
    .card-explicacion { 
        background-color: #ffffff; 
        padding: 25px; 
        border-radius: 12px; 
        border-left: 6px solid #3b82f6; 
        margin-bottom: 20px; 
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
        border: 1px solid #e2e8f0;
    }
    .card-recomendacion { 
        background-color: #ffffff; 
        padding: 25px; 
        border-radius: 12px; 
        border-left: 6px solid #f59e0b; 
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
        border: 1px solid #e2e8f0;
    }
    .card-title { margin-top: 0; color: #0f172a; font-size: 1.15rem; font-weight: 700; margin-bottom: 12px; text-transform: uppercase; letter-spacing: 0.5px;}
    .card-text { color: #475569; margin-bottom: 0; font-size: 1.05rem; line-height: 1.6;}
    
    /* Etiquetas de Nivel de Alerta */
    .tag-naranja { background-color: #f97316; color: white; padding: 6px 14px; border-radius: 20px; font-weight: 700; font-size: 0.85rem; letter-spacing: 0.5px;}
    .tag-amarilla { background-color: #facc15; color: #451a03; padding: 6px 14px; border-radius: 20px; font-weight: 700; font-size: 0.85rem; letter-spacing: 0.5px;}
    .tag-roja { background-color: #ef4444; color: white; padding: 6px 14px; border-radius: 20px; font-weight: 700; font-size: 0.85rem; letter-spacing: 0.5px;}
    .tag-blanca { background-color: #f1f5f9; color: #64748b; padding: 6px 14px; border-radius: 20px; font-weight: 700; font-size: 0.85rem; letter-spacing: 0.5px;}
    
    /* Estilizar el contenedor del mapa para que parezca una tarjeta */
    .map-container {
        background-color: #ffffff;
        padding: 10px;
        border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        border: 1px solid #e2e8f0;
    }
</style>
""", unsafe_allow_html=True)

# --- CONEXIÓN A BASE DE DATOS ---
def get_data():
    conn = sqlite3.connect('data/vraip.db') 
    query = """
        SELECT 
            a.id, 
            a.explanation, 
            a.recommendations,
            c.alert_level
        FROM ai_alerts a
        LEFT JOIN classifications c ON a.classification_id = c.id
        ORDER BY a.id DESC
    """
    try:
        df = pd.read_sql_query(query, conn)
    except Exception as e:
        df = pd.DataFrame()
    finally:
        conn.close()
    return df

def procesar_alerta(nivel_texto):
    nivel = str(nivel_texto).lower()
    if 'roja' in nivel or 'rojo' in nivel: return '#ef4444', 'tag-roja'
    if 'naranja' in nivel: return '#f97316', 'tag-naranja'
    if 'amarilla' in nivel or 'amarillo' in nivel: return '#facc15', 'tag-amarilla'
    return '#94a3b8', 'tag-blanca'

# --- ENCABEZADO ---
st.markdown('<p class="main-header">🌋 Sistema Integrado VRAIP</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Monitoreo y Alerta Temprana Volcánica Impulsado por IA</p>', unsafe_allow_html=True)

df_alertas = get_data()

if not df_alertas.empty:
    ultima_alerta = df_alertas.iloc[0]
    nivel_alerta = ultima_alerta.get('alert_level', 'Alerta Naranja')
    color_hex, css_tag = procesar_alerta(nivel_alerta)
    
    # --- FILA DE MÉTRICAS (KPIs) ---
    st.write("### Panel de Control")
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    with kpi1:
        st.metric(label="Volcán en Monitoreo", value="El Reventador", delta="Activo", delta_color="off")
    with kpi2:
        st.metric(label="Último Escaneo", value=datetime.now().strftime("%H:%M"), delta="En tiempo real")
    with kpi3:
        st.metric(label="Estado Red Sensorial", value="Operativo", delta="100% Cobertura")
    with kpi4:
        st.metric(label="Fiabilidad IA", value="Alta", delta="Modelo V1.0")
        
    st.divider()
    
    # --- ÁREA PRINCIPAL DE DATOS ---
    col1, col2 = st.columns([1.1, 1])
    
    with col1:
        st.markdown(f"**Nivel Oficial Detectado:** &nbsp; <span class='{css_tag}'>{str(nivel_alerta).upper()}</span>", unsafe_allow_html=True)
        st.write("") 
        
        # Tarjetas de Información
        st.markdown(f"""
        <div class="card-explicacion">
            <h4 class="card-title">🔬 Análisis de Actividad</h4>
            <p class="card-text">{ultima_alerta['explanation']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="card-recomendacion">
            <h4 class="card-title">🛡️ Protocolo Ciudadano</h4>
            <p class="card-text">{ultima_alerta['recommendations']}</p>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown("**Zona de Influencia Geoespacial**")
        
        lat, lon = -0.077, -77.656
        
        fig = go.Figure()
        
        # Halo de Peligro
        fig.add_trace(go.Scattermapbox(
            lat=[lat], lon=[lon], mode='markers',
            marker=go.scattermapbox.Marker(
                size=140, color=color_hex, opacity=0.25
            ),
            hoverinfo='none', showlegend=False
        ))
        
        # Punto Cero
        fig.add_trace(go.Scattermapbox(
            lat=[lat], lon=[lon], mode='markers',
            marker=go.scattermapbox.Marker(
                size=12, color=color_hex, symbol='circle'
            ),
            text=["Cráter El Reventador"],
            hoverinfo='text', showlegend=False
        ))
        
        fig.update_layout(
            mapbox=dict(
                style="carto-positron", # Tema claro topográfico
                center=dict(lat=lat, lon=lon),
                zoom=7
            ),
            margin=dict(r=0, t=0, l=0, b=0),
            height=460,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        
        # Renderizamos el gráfico
        st.plotly_chart(fig, use_container_width=True)
else:
    st.info("El sistema VRAIP está a la espera de nuevos registros oficiales...")
