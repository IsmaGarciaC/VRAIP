import os
import pdfplumber
import sqlite3
from datetime import datetime

# Ruta absoluta hacia tu base de datos
DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "vraip.db")

def extract_text_from_pdf(pdf_path):
    """
    Extrae todo el texto de un archivo PDF usando pdfplumber.
    """
    if not os.path.exists(pdf_path):
        return f"Error: No se encontró el archivo en {pdf_path}"

    texto_completo = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for pagina in pdf.pages:
                texto_extraido = pagina.extract_text()
                if texto_extraido:
                    texto_completo += texto_extraido + "\n"
        return texto_completo
    except Exception as e:
        return f"Error al leer el PDF: {e}"

def save_bulletin_to_db(volcano_id, raw_text, pdf_filename):
    """
    Guarda el texto crudo del boletín en la tabla 'bulletins' de SQLite.
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Guardamos la fecha exacta de cuándo procesamos esto
        published_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        source_url = "Ingestión Local (Offline)"
        
        # Insertamos los datos en la tabla bulletins
        cursor.execute("""
            INSERT INTO bulletins (volcano_id, published_at, source_url, raw_text, pdf_filename)
            VALUES (?, ?, ?, ?, ?)
        """, (volcano_id, published_at, source_url, raw_text, pdf_filename))
        
        conn.commit()
        bulletin_id = cursor.lastrowid  # Obtenemos el ID que SQLite le asignó
        conn.close()
        
        return bulletin_id
    except Exception as e:
        print(f"Error en BD: {e}")
        return None

# --- Bloque de Prueba Local ---
if __name__ == "__main__":
    # 1. Definimos la ruta de nuestro PDF
    nombre_archivo = "boletin_prueba.pdf"
    ruta_pdf = os.path.join(os.path.dirname(__file__), "..", "data", nombre_archivo)
    
    print(f"[*] Extrayendo texto de: {nombre_archivo}...")
    texto = extract_text_from_pdf(ruta_pdf)
    
    # 2. Si extrajo algo, lo guardamos en la base de datos
    if not texto.startswith("Error"):
        # NOTA: Usamos volcano_id = 3 porque en tu db.py "Reventador" era el 3er volcán.
        id_volcan = 3 
        
        print("[*] Guardando en la base de datos SQLite...")
        nuevo_id = save_bulletin_to_db(id_volcan, texto, nombre_archivo)
        
        if nuevo_id:
            print(f"\n[+] ¡ÉXITO! Boletín guardado correctamente en la tabla 'bulletins'.")
            print(f"[+] ID asignado en BD: {nuevo_id}")
            print(f"[+] Longitud del texto guardado: {len(texto)} caracteres.")
        else:
            print("\n[-] Hubo un problema al guardar en la base de datos.")
    else:
        print(texto)
