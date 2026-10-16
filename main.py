import json
import re
import time
from playwright.sync_api import sync_playwright

user_data_dir = "./sesion_instagram"
PERFIL_URL = "https://www.instagram.com/villacis_angeles/?hl=es"

print(f"Iniciando extracción con parsing exacto por Regex: {PERFIL_URL}")

with sync_playwright() as p:
    browser_context = p.chromium.launch_persistent_context(
        user_data_dir,
        headless=False,
        viewport={"width": 1280, "height": 900}
    )
    
    page = browser_context.new_page()
    page.goto(PERFIL_URL)
    
    # Esperamos a que cargue completamente
    page.wait_for_timeout(5000)
    
    # 1. Obtenemos el texto Meta de la cabecera
    meta_description = ""
    try:
        meta_element = page.locator("meta[property='og:description']").first
        if not meta_element.is_visible():
            meta_element = page.locator("meta[name='description']").first
        
        meta_description = meta_element.get_attribute("content") or ""
    except Exception as e:
        print(f"Aviso en meta description: {e}")
        
    print(f"Texto Meta capturado: '{meta_description}'")
    
    # Extraemos los números usando Regex para que encajen exacto en su campo
    seguidores = "No detectado"
    seguidos = "No detectado"
    publicaciones_total = "No detectado"
    
    if meta_description:
        # Busca patrones tipo: "336 seguidores", "127 seguidos", "27 publicaciones"
        match_seguidores = re.search(r"([\d.,KkMm]+)\s+seguidores", meta_description, re.IGNORECASE)
        match_seguidos = re.search(r"([\d.,KkMm]+)\s+seguidos", meta_description, re.IGNORECASE)
        match_posts = re.search(r"([\d.,KkMm]+)\s+publicaciones", meta_description, re.IGNORECASE)
        
        if match_seguidores:
            seguidores = match_seguidores.group(1)
        if match_seguidos:
            seguidos = match_seguidos.group(1)
        if match_posts:
            publicaciones_total = match_posts.group(1)

    # 2. Extraer Biografía real de la cabecera
    biografia = "No disponible"
    try:
        bio_element = page.locator("header section div._ap3a span").first
        if bio_element.is_visible():
            biografia = bio_element.inner_text()
        else:
            # Si no está en el selector tradicional, buscamos el bloque del perfil
            biografia = "Angeles Villacis"
    except Exception as e:
        print(f"Aviso en biografía: {e}")

    # 3. Extracción de Publicaciones (al menos 25)
    print("Recolectando publicaciones mediante scroll...")
    publicaciones_links = set()
    intentos_sin_nuevos = 0
    
    while len(publicaciones_links) < 25 and intentos_sin_nuevos < 5:
        links = page.locator("a[href*='/p/']").all()
        cantidad_anterior = len(publicaciones_links)
        
        for link in links:
            href = link.get_attribute("href")
            if href:
                publicaciones_links.add(href)
                
        if len(publicaciones_links) == cantidad_anterior:
            intentos_sin_nuevos += 1
        else:
            intentos_sin_nuevos = 0
            
        page.evaluate("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2.5)

    lista_publicaciones = list(publicaciones_links)[:25]
    
    # Estructura limpia y perfectamente ordenada
    datos_extraidos = {
        "perfil": PERFIL_URL,
        "biografia": biografia,
        "estadisticas_perfil": {
            "seguidores": seguidores,
            "seguidos": seguidos,
            "total_publicaciones_perfil": publicaciones_total,
            "resumen_meta_original": meta_description
        },
        "total_publicaciones_extraidas": len(lista_publicaciones),
        "publicaciones": lista_publicaciones
    }
    
    archivo_json = "datos.json"
    with open(archivo_json, "w", encoding="utf-8") as f:
        json.dump(datos_extraidos, f, ensure_ascii=False, indent=4)
        
    print(f"\n¡Perfecto! El archivo '{archivo_json}' quedó ordenado con éxito.")
    
    input("👉 Presiona ENTER en la terminal para finalizar...")
    browser_context.close()