import logging
import traceback
import time  # <-- IMPORTAMOS LA LIBRERÍA DE TIEMPO

from modules.scraper import get_latest_bulletin
from modules.ingestion import extract_text_from_pdf, save_bulletin_to_db
from modules.classifier import classify_risk, save_classification
from modules.interpreter import generate_ai_interpretation, save_ai_alert

# --- CONFIGURACIÓN DEL SISTEMA DE LOGS ---
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler("vraip.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)

def run_pipeline():
    # INICIA EL CRONÓMETRO GLOBAL
    tiempo_inicio_total = time.time()
    
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
        # INICIA EL CRONÓMETRO INDIVIDUAL POR VOLCÁN
        tiempo_inicio_volcan = time.time()
        
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
            
        finally:
            # DETIENE EL CRONÓMETRO INDIVIDUAL Y CALCULA LA DIFERENCIA
            tiempo_fin_volcan = time.time()
            duracion_volcan = tiempo_fin_volcan - tiempo_inicio_volcan
            logging.info(f"⏱️ Tiempo de procesamiento para {volcan_nombre}: {duracion_volcan:.2f} segundos.")

    # DETIENE EL CRONÓMETRO GLOBAL Y CALCULA EL TOTAL
    tiempo_fin_total = time.time()
    duracion_total = tiempo_fin_total - tiempo_inicio_total

    logging.info("="*60)
    logging.info(f" BARRIDO MULTIVOLCÁN FINALIZADO.")
    logging.info(f" 🚀 TIEMPO TOTAL DE EJECUCIÓN: {duracion_total:.2f} segundos ({duracion_total/60:.2f} minutos).")
    logging.info("="*60 + "\n")

if __name__ == "__main__":
    run_pipeline()
