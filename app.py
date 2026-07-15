import streamlit as st
from database.db import init_db

# ─── Config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="VRAIP",
    page_icon="🌋",
    layout="wide"
)

# Initialize DB on first run
init_db()

# ─── Sidebar navigation ─────────────────────────────────────────────────────
st.sidebar.title("🌋 VRAIP")
st.sidebar.markdown("*Sistema de Alertas Volcánicas*")
st.sidebar.divider()

page = st.sidebar.radio(
    "Navegación",
    ["Vista Principal", "Detalle de Volcán"],
    label_visibility="collapsed"
)

# ─── Pages ──────────────────────────────────────────────────────────────────
if page == "Vista Principal":
    st.title("Estado Actual — Volcanes Monitoreados")
    st.info("Módulos en construcción. La base de datos está lista.")

elif page == "Detalle de Volcán":
    st.title("Detalle de Volcán")
    st.info("Vista de detalle en construcción.")
