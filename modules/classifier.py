import sqlite3
import os
import re

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "vraip.db")

def get_bulletin_text(bulletin_id):
    """Obtiene el texto crudo de un boletín específico desde la BD."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT raw_text FROM bulletins WHERE id = ?", (bulletin_id,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else None
    except Exception as e:
        print(f"Error al conectar con la BD: {e}")
        return None

def classify_risk(raw_text):
    """
    Motor de reglas basado en expresiones regulares y palabras clave
    para mapear texto técnico a una escala de 4 colores.
    """
    texto = raw_text.lower()
    
    # 1. Determinar el nivel de alerta (Reglas deterministas)
    alert_level = "Verde" # Por defecto
    
    if any(word in texto for word in ["erupción inminente", "muy alta", "flujos piroclásticos"]):
        alert_level = "Roja"
    elif "alta" in texto or "emisión de ceniza fuerte" in texto:
        alert_level = "Naranja"
    elif "moderada" in texto or "actividad sísmica" in texto:
        alert_level = "Amarilla"
        
    # 2. Extraer tipo de actividad (Buscamos la línea "Nivel de Actividad")
    activity_type = "No especificada"
    match_actividad = re.search(r'superficial:\s*(\w+)', texto, re.IGNORECASE)
    if match_actividad:
        activity_type = match_actividad.group(1).capitalize()
        
    # 3. Detectar emisiones (ceniza o gases)
    emissions_flag = 1 if "ceniza" in texto or "gases" in texto else 0
    
    return alert_level, activity_type, emissions_flag

def save_classification(bulletin_id, alert_level, activity_type, emissions_flag):
    """Guarda los resultados de la clasificación en la tabla 'classifications'."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO classifications (bulletin_id, alert_level, activity_type, emissions_flag)
            VALUES (?, ?, ?, ?)
        """, (bulletin_id, alert_level, activity_type, emissions_flag))
        
        conn.commit()
        class_id = cursor.lastrowid
        conn.close()
        return class_id
    except Exception as e:
        print(f"Error al guardar clasificación: {e}")
        return None

# --- Bloque de Prueba Local ---
if __name__ == "__main__":
    bulletin_id_a_procesar = 1 # El ID que tu script de ingestión acaba de crear
    
    print(f"[*] Buscando boletín ID {bulletin_id_a_procesar} en la base de datos...")
    texto_boletin = get_bulletin_text(bulletin_id_a_procesar)
    
    if texto_boletin:
        print("[*] Boletín encontrado. Ejecutando motor de clasificación...")
        alerta, actividad, emisiones = classify_risk(texto_boletin)
        
        print("\n" + "="*40)
        print("      RESULTADO DE LA CLASIFICACIÓN      ")
        print("="*40)
        print(f" Nivel de Alerta : {alerta}")
        print(f" Tipo Actividad  : {actividad}")
        print(f" Hay Emisiones   : {'Sí' if emisiones == 1 else 'No'}")
        print("="*40 + "\n")
        
        print("[*] Guardando resultados en la BD...")
        nuevo_id = save_classification(bulletin_id_a_procesar, alerta, actividad, emisiones)
        
        if nuevo_id:
            print(f"[+] ¡ÉXITO! Clasificación guardada con el ID: {nuevo_id}")
    else:
        print("[-] No se encontró el boletín. ¿Seguro que corriste ingestion.py primero?")
