# 🌋 VRAIP: Volcanic Risk Assessment & Interpretation Platform

Plataforma ciudadana impulsada por Inteligencia Artificial para la interpretación y monitoreo en tiempo real de la actividad volcánica en Ecuador (Instituto Geofísico EPN). 

Desarrollado como Proyecto Capstone (2026).

## 🚀 Características
- **Ingestión Automatizada:** Extracción de datos crudos de boletines técnicos (PDF).
- **Clasificador de Riesgo:** Motor de reglas que traduce indicadores técnicos a una escala de 4 niveles.
- **Inteligencia Artificial (Gemini):** Traducción de lenguaje técnico a recomendaciones ciudadanas empáticas y claras.
- **Dashboard Geoespacial:** Interfaz construida en Streamlit con mapas interactivos de Plotly.

## 🛠️ Tecnologías Utilizadas
- **Backend:** Python 3.13, SQLite3
- **Data Ingestion:** pdfplumber, Pandas
- **AI Integration:** Google Generative AI (Gemini 3.5 Flash)
- **Frontend:** Streamlit, Plotly Express

## ⚙️ Cómo ejecutar el proyecto
1. Clona el repositorio e instala las dependencias (`pip install -r requirements.txt`).
2. Configura tu API Key de Gemini en un archivo `.env`.
3. Inicializa la base de datos: `python database/db.py`
4. Ingesta un boletín: `python modules/ingestion.py`
5. Clasifica y genera la alerta: `python modules/interpreter.py`
6. Levanta el dashboard: `streamlit run app.py`
