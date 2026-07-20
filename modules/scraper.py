import os
import datetime
import time
import glob
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Ruta absoluta a la carpeta data
DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))

def get_latest_bulletin():
    """
    Usa un navegador fantasma (Selenium) para sortear la seguridad JSF del IG-EPN,
    hacer clic en los menús desplegables y descargar el último informe.
    """
    url = "https://www.igepn.edu.ec/servicios/busqueda-informes"
    
    # Asegurar que la carpeta data exista
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

    # Configuración del Robot (Modo Fantasma + Ruta de descarga automática)
    chrome_options = Options()
    chrome_options.add_argument("--headless=new") # Navegador invisible
    chrome_options.add_argument("--window-size=1920,1080") # <-- ¡NUEVO: Visión en HD!
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36") # <-- ¡NUEVO: Camuflaje humano!
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    prefs = {
        "download.default_directory": DATA_DIR,
        "download.prompt_for_download": False,
        "plugins.always_open_pdf_externally": True # Obliga a descargar en vez de abrir
    }
    chrome_options.add_experimental_option("prefs", prefs)
    
    print(f"[*] Iniciando Robot de Scraping en: {url}")
    
    try:
        # Iniciamos el navegador
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        driver.get(url)
        wait = WebDriverWait(driver, 15) # Esperará hasta 15 segundos a que carguen las cosas

        print("[*] Robot conectado. Dando tiempo al sitio para cargar...")
        time.sleep(4)
        
        # 1. Detector de iFrames
        iframes = driver.find_elements(By.TAG_NAME, "iframe")
        if len(iframes) > 0:
            print("[*] ¡Iframe detectado! Cambiando el foco a la ventana interna...")
            driver.switch_to.frame(iframes[0])
            time.sleep(2)

        # FUNCIÓN MAESTRA: Acomoda la cámara y hace un clic humano real
        def seleccionar_menu(trigger_xpath, opcion_xpath, wait_time):
            # Paso A: Abrir el menú desplegable
            trigger = wait.until(EC.element_to_be_clickable((By.XPATH, trigger_xpath)))
            driver.execute_script("arguments[0].scrollIntoView({behavior: 'auto', block: 'center'});", trigger)
            time.sleep(1)
            trigger.click() # Clic humano real
            time.sleep(1.5) # Esperar a que la lista termine de bajar
            
            # Paso B: Seleccionar la opción de la lista
            opcion = wait.until(EC.element_to_be_clickable((By.XPATH, opcion_xpath)))
            driver.execute_script("arguments[0].scrollIntoView({behavior: 'auto', block: 'center'});", opcion)
            time.sleep(1)
            opcion.click() # Clic humano real que dispara el filtro del servidor
            time.sleep(wait_time) 

                
        # --- PASO 1: Tipo ---
        print("[*] Seleccionando 'Grupo de Informes Volcánicos'...")
        # Busca la palabra "Tipo:" (ignorando "Tipo de informe") y toca su menú
        seleccionar_menu(
            "(//*[contains(text(), 'Tipo:') and not(contains(text(), 'informe'))]/following::div[contains(@class, 'ui-selectonemenu-trigger')])[1]", 
            "//li[contains(text(), 'Grupo de Informes Volc')]", 
            4
        )
        
        # --- PASO 2: Volcán ---
        print("[*] Seleccionando 'El Reventador'...")
        # Busca la palabra "Volcán:" y toca el menú que está a su lado
        seleccionar_menu(
            "(//*[contains(text(), 'Volcán:')]/following::div[contains(@class, 'ui-selectonemenu-trigger')])[1]", 
            "//li[contains(text(), 'El Reventador')]", 
            4
        )
        
        # --- PASO 3: Año Actual ---
        ano_actual = str(datetime.datetime.now().year)
        print(f"[*] Seleccionando el año actual ({ano_actual})...")
        # Busca la palabra "Año:" y toca su menú
        seleccionar_menu(
            "(//*[contains(text(), 'Año:')]/following::div[contains(@class, 'ui-selectonemenu-trigger')])[1]", 
            f"//li[contains(text(), '{ano_actual}')]", 
            2
        )
        
        # --- PASO 4: Buscar ---
        print("[*] Formulario completo. Ejecutando búsqueda...")
        btn_buscar = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Buscar')]")))
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'auto', block: 'center'});", btn_buscar)
        time.sleep(1)
        btn_buscar.click()

        # --- PASO 5: Descargar ---
        btn_descargar = wait.until(EC.element_to_be_clickable((By.XPATH, "(//span[contains(text(), 'Descargar Informe')])[1]")))
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'auto', block: 'center'});", btn_descargar)
        time.sleep(1)
        btn_descargar.click()
        print("[*] ¡Botón de descarga presionado!")
        
        print("[*] Esperando a que el archivo llegue al disco...")
        time.sleep(5)
       
        # 4. Buscar el archivo PDF más nuevo en la carpeta data
        archivos_pdf = glob.glob(os.path.join(DATA_DIR, "*.pdf"))
        if not archivos_pdf:
            raise FileNotFoundError("El robot hizo clic, pero el archivo no se descargó.")
            
        archivo_mas_reciente = max(archivos_pdf, key=os.path.getctime)
        nombre_archivo = os.path.basename(archivo_mas_reciente)
        
        print(f"[+] ¡Descarga exitosa automatizada: {nombre_archivo}!")
        return archivo_mas_reciente, nombre_archivo
        
    except Exception as e:
        print(f"[-] Error en el robot de Scraping: {e}")
        try:
            foto_path = os.path.join(DATA_DIR, "debug_robot.png")
            driver.save_screenshot(foto_path)
            print(f"[*] 📸 ¡Cámara de seguridad activada! Foto guardada en: {foto_path}")
            driver.quit()
        except:
            pass
        return use_fallback()

def use_fallback():
    """Plan B: Usa el archivo local si la web del gobierno cambia su diseño."""
    print("[*] (Fallback) Activando protocolo de emergencia: Usando archivo local.")
    fallback_name = "boletin_prueba.pdf"
    fallback_path = os.path.join(DATA_DIR, fallback_name)
    return fallback_path, fallback_name

if __name__ == "__main__":
    ruta, nombre = get_latest_bulletin()
    print(f"\n[INFO] Archivo listo: {nombre}")
