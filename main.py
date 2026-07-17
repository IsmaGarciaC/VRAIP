import os
from modules.scraper import get_latest_bulletin
from modules.ingestion import extract_text_from_pdf, save_bulletin_to_db
from modules.classifier import classify_risk, save_classification
from modules.interpreter import generate_ai_interpretation, save_ai_alert

def run_pipeline():
    print("="*60)
    print("      🌋 INICIANDO PIPELINE AUTOMATIZADO VRAIP 🌋      ")
    print("="*60)

    # 1. Extracción de Datos (Web Scraping)
    pdf_path, pdf_filename = get_latest_bulletin()
    
    # 2. Ingestión (PDF a Texto)
    print(f"\n[*] Extrayendo texto puro de: {pdf_filename}...")
    raw_text = extract_text_from_pdf(pdf_path)
    
    if raw_text.startswith("Error"):
        print("[-] Fallo crítico en la lectura del PDF. Abortando.")
        return

    # ID 3 corresponde a El Reventador en nuestra base de datos
    volcano_id = 3 
    bulletin_id = save_bulletin_to_db(volcano_id, raw_text, pdf_filename)
    
    # 3. Clasificación (Reglas Deterministas)
    print(f"[*] Clasificando riesgo técnico (Boletín ID: {bulletin_id})...")
    alert_level, activity_type, emissions = classify_risk(raw_text)
    class_id = save_classification(bulletin_id, alert_level, activity_type, emissions)

    # 4. Interpretación IA (Gemini)
    print(f"[*] Conectando con IA para generar alerta ciudadana...")
    respuesta_ai = generate_ai_interpretation("Reventador", alert_level, activity_type, emissions)
    
    if respuesta_ai and "RECOMENDACIONES:" in respuesta_ai:
        partes = respuesta_ai.split("RECOMENDACIONES:")
        explicacion = partes[0].replace("EXPLICACIÓN:", "").strip()
        recomendaciones = partes[1].strip()
        
        nuevo_id = save_ai_alert(class_id, explicacion, recomendaciones)
        print("\n" + "="*60)
        print(f" [+] ¡ÉXITO! Pipeline completado. Alerta guardada (ID: {nuevo_id})")
        print(" [+] El Dashboard de Streamlit está listo para reflejar los cambios.")
        print("="*60 + "\n")
    else:
        print("\n[-] Error: La IA no devolvió el formato esperado o falló la conexión.")

if __name__ == "__main__":
    run_pipeline()
