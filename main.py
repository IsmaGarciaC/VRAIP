from modules.scraper import get_latest_bulletin
from modules.ingestion import extract_text_from_pdf, save_bulletin_to_db
from modules.classifier import classify_risk, save_classification
from modules.interpreter import generate_ai_interpretation, save_ai_alert
import traceback

def run_pipeline():
    print("="*60)
    print("      🌋 INICIANDO PIPELINE VRAIP MULTIVOLCÁN 🌋      ")
    print("="*60)

    # Diccionario maestro: Mapea el nombre exacto de la web con el ID de tu base de datos.
    # Ajusta los IDs (1, 2, 4) según cómo los hayas creado en tu tabla original.
    volcanes_objetivo = {
        "Cotopaxi": 1,
        "Sangay": 2,
        "El Reventador": 3,
        "Tungurahua": 4
    }

    for volcan_nombre, volcano_id in volcanes_objetivo.items():
        print(f"\n" + "-"*50)
        print(f" 📡 INICIANDO ESCANEO: {volcan_nombre.upper()} (ID: {volcano_id})")
        print("-"*50)

        try:
            # 1. Extracción de Datos (Web Scraping)
            # Ahora le pasamos el nombre al scraper
            pdf_path, pdf_filename = get_latest_bulletin(volcan_nombre)
            
            # 2. Ingestión (PDF a Texto)
            print(f"\n[*] Extrayendo texto puro de: {pdf_filename}...")
            raw_text = extract_text_from_pdf(pdf_path)
            
            if raw_text.startswith("Error"):
                print(f"[-] Fallo en la lectura del PDF para {volcan_nombre}. Saltando...")
                continue # Si falla un volcán, pasa al siguiente de la lista

            bulletin_id = save_bulletin_to_db(volcano_id, raw_text, pdf_filename)
            
            # 3. Clasificación (Reglas Deterministas)
            print(f"[*] Clasificando riesgo técnico (Boletín ID: {bulletin_id})...")
            alert_level, activity_type, emissions = classify_risk(raw_text)
            class_id = save_classification(bulletin_id, alert_level, activity_type, emissions)

            # 4. Interpretación IA (Gemini)
            print(f"[*] Conectando con IA para generar alerta ciudadana...")
            respuesta_ai = generate_ai_interpretation(volcan_nombre, alert_level, activity_type, emissions)
            
            if respuesta_ai and "RECOMENDACIONES:" in respuesta_ai:
                partes = respuesta_ai.split("RECOMENDACIONES:")
                explicacion = partes[0].replace("EXPLICACIÓN:", "").strip()
                recomendaciones = partes[1].strip()
                
                nuevo_id = save_ai_alert(class_id, explicacion, recomendaciones)
                print(f" [+] ÉXITO: Alerta guardada para {volcan_nombre} (ID BD: {nuevo_id})")
            else:
                print(f"[-] Error IA: Formato incorrecto para {volcan_nombre}.")
                
        except Exception as e:
            print(f"[-] Ocurrió un error inesperado procesando {volcan_nombre}: {e}")
            # Esto evita que si falla un volcán, se caiga todo el programa
            traceback.print_exc()

    print("\n" + "="*60)
    print(" [+] BARRIDO DE MONITOREO MULTIVOLCÁN FINALIZADO.")
    print(" [+] El Dashboard de Streamlit está listo para reflejar los cambios.")
    print("="*60 + "\n")

if __name__ == "__main__":
    run_pipeline()
