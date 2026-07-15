import os
import sqlite3
import google.generativeai as genai
from dotenv import load_dotenv

# 1. Cargar la API Key de forma segura
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY or GEMINI_API_KEY == "your_gemini_api_key_here":
    print("[-] ERROR: Por favor, coloca tu API Key real en el archivo .env")
    exit()

# Configurar Gemini
genai.configure(api_key=GEMINI_API_KEY)
DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "vraip.db")

def get_classification_data(class_id):
    """Obtiene los datos de la clasificación, uniéndolos con el nombre del volcán."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT c.id, v.name, c.alert_level, c.activity_type, c.emissions_flag
        FROM classifications c
        JOIN bulletins b ON c.bulletin_id = b.id
        JOIN volcanoes v ON b.volcano_id = v.id
        WHERE c.id = ?
    """, (class_id,))
    result = cursor.fetchone()
    conn.close()
    return result

def generate_ai_interpretation(volcano_name, alert_level, activity_type, emissions):
    """Prueba dinámicamente los modelos de la nueva generación de forma silenciosa."""
    
    modelos_a_probar = [
        "gemini-3.5-flash",
        "gemini-flash-latest",
        "gemini-3-flash-preview",
        "gemini-2.0-flash"
    ]
    
    emisiones_texto = "con emisiones de ceniza y gases" if emissions else "sin emisiones significativas"
    
    prompt = f"""
    Eres un experto en gestión de riesgos de Ecuador. Tu objetivo es traducir alertas técnicas a lenguaje ciudadano.
    
    Contexto actual:
    - Volcán: {volcano_name}
    - Alerta: {alert_level}
    - Actividad: {activity_type} {emisiones_texto}.
    
    Redacta exactamente en este formato:
    
    EXPLICACIÓN:
    (Escribe 2 líneas simples explicando qué significa esto para la gente que vive cerca).
    
    RECOMENDACIONES:
    - (Acción preventiva 1)
    - (Acción preventiva 2)
    - (Acción preventiva 3)
    """
    
    for nombre_modelo in modelos_a_probar:
        try:
            print(f"[*] Intentando conectar con: {nombre_modelo}...")
            model = genai.GenerativeModel(nombre_modelo)
            response = model.generate_content(prompt)
            print(f"[+] ¡Conexión exitosa con {nombre_modelo}!")
            return response.text
        except Exception as e:
            error_msg = str(e)
            # Manejo silencioso de errores esperados (404 o 429)
            if "429" in error_msg or "404" in error_msg:
                print(f"    [-] Modelo {nombre_modelo} ocupado. Saltando al siguiente...")
            else:
                # Solo imprime errores graves que no esperábamos
                print(f"    [-] Error inesperado con {nombre_modelo}: {e}")
            continue
            
    print("\n[-] ERROR CRÍTICO: Ninguno de los modelos funcionó.")
    return None

def save_ai_alert(classification_id, explanation, recommendations):
    """Guarda la respuesta en la tabla ai_alerts."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO ai_alerts (classification_id, explanation, recommendations)
            VALUES (?, ?, ?)
        """, (classification_id, explanation, recommendations))
        conn.commit()
        ai_id = cursor.lastrowid
        conn.close()
        return ai_id
    except Exception as e:
        print(f"Error al guardar en BD: {e}")
        return None

# --- Bloque de Prueba Local ---
if __name__ == "__main__":
    class_id = 1
    
    print(f"[*] Buscando datos de la clasificación ID {class_id}...")
    datos = get_classification_data(class_id)
    
    if datos:
        c_id, volc, alerta, act, em = datos
        print(f"[*] Conectando con IA para: {volc} (Alerta {alerta})...")
        
        respuesta_ai = generate_ai_interpretation(volc, alerta, act, em)
        
        if respuesta_ai:
            print("\n" + "="*60)
            print("                RESPUESTA DE LA IA                ")
            print("="*60)
            print(respuesta_ai)
            print("="*60 + "\n")
            
            if "RECOMENDACIONES:" in respuesta_ai:
                partes = respuesta_ai.split("RECOMENDACIONES:")
                explicacion = partes[0].replace("EXPLICACIÓN:", "").strip()
                recomendaciones = partes[1].strip()
                
                print("[*] Guardando interpretación en la tabla 'ai_alerts'...")
                nuevo_id = save_ai_alert(class_id, explicacion, recomendaciones)
                if nuevo_id:
                    print(f"[+] ¡ÉXITO! Alerta ciudadana guardada con ID: {nuevo_id}")
            else:
                print("[-] La IA no devolvió el formato esperado.")
