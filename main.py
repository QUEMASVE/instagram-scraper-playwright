import json
import os
import re
import time
import webbrowser
from playwright.sync_api import sync_playwright

user_data_dir = "./sesion_instagram"  # Carpeta de sesión persistente
PERFIL_URL = "https://www.instagram.com/villacis_angeles/?hl=es"

print(f"Iniciando extracción optimizada: {PERFIL_URL}")

with sync_playwright() as p:
    browser_context = p.chromium.launch_persistent_context(
        user_data_dir, headless=False, viewport={"width": 1280, "height": 900}
    )

    page = browser_context.new_page()
    page.goto(PERFIL_URL, timeout=60000, wait_until="domcontentloaded")
    page.wait_for_timeout(4000)

    # ==========================================
    # 1. EXTRACCIÓN DE METADATOS Y ESTADÍSTICAS
    # ==========================================
    meta_description = ""
    try:
        meta_element = page.locator("meta[property='og:description']").first
        if not meta_element.is_visible():
            meta_element = page.locator("meta[name='description']").first

        meta_description = meta_element.get_attribute("content") or ""
    except Exception as e:
        print(f"Aviso en meta description: {e}")

    seguidores = "No detectado"
    seguidos = "No detectado"
    publicaciones_total = "No detectado"

    if meta_description:
        match_seguidores = re.search(r"([\d.,KkMm]+)\s+seguidores", meta_description, re.IGNORECASE)
        match_seguidos = re.search(r"([\d.,KkMm]+)\s+seguidos", meta_description, re.IGNORECASE)
        match_posts = re.search(r"([\d.,KkMm]+)\s+publicaciones", meta_description, re.IGNORECASE)

        if match_seguidores:
            seguidores = match_seguidores.group(1)
        if match_seguidos:
            seguidos = match_seguidos.group(1)
        if match_posts:
            publicaciones_total = match_posts.group(1)

    # ==========================================
    # 2. EXTRACCIÓN DE BIOGRAFÍA
    # ==========================================
    biografia = "No disponible"
    try:
        bio_element = page.locator("header section div._ap3a span").first
        if bio_element.is_visible():
            biografia = bio_element.inner_text()
    except Exception as e:
        print(f"Aviso en biografía: {e}")

    # ==========================================
    # 3. RECOLECCIÓN DE URLS DE PUBLICACIONES (HASTA 25)
    # ==========================================
    print("\nRecolectando enlaces de publicaciones mediante scroll...")
    publicaciones_links = set()
    intentos_sin_nuevos = 0

    while len(publicaciones_links) < 25 and intentos_sin_nuevos < 6:
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

    lista_links = list(publicaciones_links)[:25]

    # ==========================================
    # 4. INSPECCIÓN PROFUNDA DE CADA POST
    # ==========================================
    print(f"\nAnalizando detalles de {len(lista_links)} publicaciones...")
    detalle_publicaciones = []

    for idx, link in enumerate(lista_links, 1):
        url_post = link if link.startswith("http") else f"https://www.instagram.com{link}"
        print(f"   [{idx}/{len(lista_links)}] Procesando: {url_post}")

        try:
            page.goto(url_post, timeout=30000, wait_until="domcontentloaded")
            time.sleep(2)

            # --- Conteo de Likes y Comentarios ---
            meta_post = page.locator("meta[property='og:description']").first
            text_post = meta_post.get_attribute("content") if meta_post else ""

            likes = "No detectado"
            comentarios = "No detectado"

            match_likes = re.search(r"([\d.,KkMm]+)\s+(likes|me gusta)", text_post, re.IGNORECASE)
            match_comments = re.search(r"([\d.,KkMm]+)\s+(comments|comentarios)", text_post, re.IGNORECASE)

            if match_likes:
                likes = match_likes.group(1)
            if match_comments:
                comentarios = match_comments.group(1)

            # --- Fecha exacta de la publicación ---
            fecha_publicacion = "No disponible"
            try:
                time_elem = page.locator("time._a9ze, time[datetime]").first
                if time_elem.is_visible():
                    fecha_publicacion = time_elem.get_attribute("datetime") or time_elem.inner_text()
            except Exception:
                pass

            # --- Descripción limpia del post ---
            descripcion = ""
            try:
                caption_elem = page.locator("h1._ap3a, div._a9zs span").first
                if caption_elem.is_visible():
                    descripcion = caption_elem.inner_text().strip()
            except Exception:
                pass

            # --- Tipo de contenido (Imagen, Vídeo, Carrusel) ---
            tipo_post = "Imagen"
            try:
                if page.locator("video").count() > 0 or "reel" in url_post.lower():
                    tipo_post = "Vídeo / Reel"
                elif page.locator("button[aria-label*='Siguiente'], button[aria-label*='Next']").count() > 0:
                    tipo_post = "Carrusel"
            except Exception:
                pass

            tiene_texto = len(descripcion) > 0

            detalle_publicaciones.append({
                "url": url_post,
                "tipo_post": tipo_post,
                "fecha_publicacion": fecha_publicacion,
                "likes": likes,
                "comentarios": comentarios,
                "descripcion": descripcion,
                "tiene_texto": tiene_texto,
                "resumen_meta": text_post
            })
        except Exception as err:
            print(f"    Error al inspeccionar {url_post}: {err}")
            detalle_publicaciones.append({"url": url_post, "error": str(err)})

    # Retornamos al perfil principal
    page.goto(PERFIL_URL, timeout=60000, wait_until="domcontentloaded")
    time.sleep(2)

    # ==========================================
    # 5. ESTRUCTURA Y GUARDADO EN JSON Y JS
    # ==========================================
    datos_extraidos = {
        "perfil": PERFIL_URL,
        "biografia": biografia,
        "estadisticas_perfil": {
            "seguidores": seguidores,
            "seguidos": seguidos,
            "total_publicaciones_perfil": publicaciones_total,
            "resumen_meta_original": meta_description
        },
        "total_publicaciones_analizadas": len(detalle_publicaciones),
        "publicaciones_detalle": detalle_publicaciones
    }

    # Guardado en JSON
    archivo_json = "datos.json"
    with open(archivo_json, "w", encoding="utf-8") as f:
        json.dump(datos_extraidos, f, ensure_ascii=False, indent=4)

    # Guardado directo en JS
    archivo_js = "datos.js"
    with open(archivo_js, "w", encoding="utf-8") as f:
        f.write(f"const datosInstagram = {json.dumps(datos_extraidos, ensure_ascii=False, indent=4)};")

    print(f"\n¡Proceso completado con éxito! Archivos '{archivo_json}' y '{archivo_js}' generados.")
    browser_context.close()

# ==========================================
# 6. LANZAR SERVIDOR WEB INTERACTIVO
# ==========================================
print("\n🌐 Abriendo tu panel web interactivo en http://127.0.0.1:5000 ...")
webbrowser.open("http://127.0.0.1:5000")

try:
    os.system("python servidor.py")
except KeyboardInterrupt:
    print("\n👋 Servidor detenido por el usuario.")