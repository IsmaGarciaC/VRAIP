import logging
import traceback
from modules.scraper import get_latest_bulletin
from modules.ingestion import extract_text_from_pdf, save_bulletin_to_db
from modules.classifier import classify_risk, save_classification
from modules.interpreter import generate_ai_interpretation, save_ai_alert

# --- CONFIGURACIÓN DEL SISTEMA DE LOGS ---
# Esto creará automáticamente el archivo vraip.log en la carpeta principal
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler("vraip.log", encoding='utf-8'), # Guarda en archivo
        logging.StreamHandler() # Muestra en la terminal al mismo tiempo
    ]
)

def run_pipeline():
    logging.info("="*60)
    logging.info(" 🌋 INICIANDO PIPELINE VRAIP MULTIVOLCÁN (MODO PRODUCCIÓN) 🌋 ")
    logging.info("="*60)

    volcanes_objetivo = {
        "Cotopaxi": 1,
        "Sangay": 2,
        "El Reventador": 3,
        "Tungurahua": 4
    }

    for volcan_nombre, volcano_id in volcanes_objetivo.items():
        logging.info("-" * 50)
        logging.info(f"📡 INICIANDO ESCANEO: {volcan_nombre.upper()} (ID: {volcano_id})")
        logging.info("-" * 50)

        try:
            # 1. Extracción de Datos
            pdf_path, pdf_filename = get_latest_bulletin(volcan_nombre)
            
            # 2. Ingestión 
            logging.info(f"Extrayendo texto puro de: {pdf_filename}...")
            raw_text = extract_text_from_pdf(pdf_path)
            
            if raw_text.startswith("Error"):
                logging.error(f"Fallo en la lectura del PDF para {volcan_nombre}. Saltando...")
                continue

            bulletin_id = save_bulletin_to_db(volcano_id, raw_text, pdf_filename)
            
            # 3. Clasificación
            logging.info(f"Clasificando riesgo técnico (Boletín ID: {bulletin_id})...")
            alert_level, activity_type, emissions = classify_risk(raw_text)
            class_id = save_classification(bulletin_id, alert_level, activity_type, emissions)

            # 4. Interpretación IA
            logging.info("Conectando con motor IA (Gemini) para generar alerta...")
            respuesta_ai = generate_ai_interpretation(volcan_nombre, alert_level, activity_type, emissions)
            
            if respuesta_ai and "RECOMENDACIONES:" in respuesta_ai:
                partes = respuesta_ai.split("RECOMENDACIONES:")
                explicacion = partes[0].replace("EXPLICACIÓN:", "").strip()
                recomendaciones = partes[1].strip()
                
                nuevo_id = save_ai_alert(class_id, explicacion, recomendaciones)
                logging.info(f"ÉXITO: Alerta guardada para {volcan_nombre} (ID BD: {nuevo_id})")
            else:
                logging.warning(f"Error IA: El formato devuelto no es el esperado para {volcan_nombre}.")
                
        except Exception as e:
            logging.error(f"Ocurrió un error inesperado procesando {volcan_nombre}: {e}")
            logging.error(traceback.format_exc())

    logging.info("="*60)
    logging.info(" BARRIDO DE MONITOREO MULTIVOLCÁN FINALIZADO.")
    logging.info("="*60 + "\n")

if __name__ == "__main__":
    run_pipeline()
