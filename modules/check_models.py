import os
import google.generativeai as genai
from dotenv import load_dotenv

# Cargamos tu llave
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

print("\n[*] Consultando el catálogo de Google AI Studio...")
print("[*] Modelos habilitados para generar texto con tu cuenta:\n")

try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f" -> {m.name}")
    print("\n[*] Escaneo completado.")
except Exception as e:
    print(f"\n[-] Error al consultar a Google: {e}")
