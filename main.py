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
    page.wait_for_timeout(5000)

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
    # 2.5. EXTRACCIÓN DE SEGUIDORES CON HOVER Y BÚSQUEDA DINÁMICA DE POPOVER
    # ==========================================
    print("\n[SEGUIDORES] Abriendo lista de seguidores...")
    seguidores_detalle = []
    try:
        seguidores_trigger = page.get_by_text("seguidores", exact=False).first
        if seguidores_trigger.is_visible():
            seguidores_trigger.click()
            print("  [OK] Clic realizado en el botón de seguidores.")
            
            page.wait_for_selector("div[role='dialog']", timeout=10000)
            print("  [OK] Modal de seguidores desplegado.")
            time.sleep(2)

            seguidores_procesados = set()
            intentos_sin_nuevos = 0

            while len(seguidores_detalle) < 200 and intentos_sin_nuevos < 6:
                filas_usuarios = page.locator("div[role='dialog'] a[role='link'][href^='/']").all()
                cantidad_inicial = len(seguidores_detalle)

                for link_elem in filas_usuarios:
                    href = link_elem.get_attribute("href")
                    if not href or href.count('/') != 2 or "/explore/" in href:
                        continue
                    
                    username = href.strip('/')
                    if username in seguidores_procesados:
                        continue
                    
                    seguidores_procesados.add(username)

                    pub_seg = "No detectado"
                    foll_seg = "No detectado"
                    foll_ing = "No detectado"

                    try:
                        link_elem.hover()
                        # Pausa esencial para que Instagram renderice la tarjeta flotante
                        page.wait_for_timeout(1200)

                        # Búsqueda dinámica y robusta del popover en el DOM
                        pop_text = page.evaluate("""() => {
                            const divs = Array.from(document.querySelectorAll('div'));
                            const popovers = divs.filter(d => {
                                const text = d.innerText || '';
                                return text.includes('seguidores') && text.includes('seguidos') && text.length < 400;
                            });
                            if (popovers.length > 0) {
                                return popovers[popovers.length - 1].innerText;
                            }
                            return '';
                        }""")

                        if pop_text:
                            m_pub = re.search(r"([\d.,KkMm]+)\s+publicaciones", pop_text, re.IGNORECASE)
                            m_foll = re.search(r"([\d.,KkMm]+)\s+seguidores", pop_text, re.IGNORECASE)
                            m_ing = re.search(r"([\d.,KkMm]+)\s+seguidos", pop_text, re.IGNORECASE)

                            if m_pub: pub_seg = m_pub.group(1)
                            if m_foll: foll_seg = m_foll.group(1)
                            if m_ing: foll_ing = m_ing.group(1)

                    except Exception:
                        pass

                    seguidores_detalle.append({
                        "username": username,
                        "url_perfil": f"https://www.instagram.com/{username}/",
                        "estadisticas": {
                            "publicaciones": pub_seg,
                            "seguidores": foll_seg,
                            "seguidos": foll_ing
                        }
                    })

                    print(f"   + Seguidor [{len(seguidores_detalle)}]: @{username} | Pub: {pub_seg} | Seg: {foll_seg} | Seguidos: {foll_ing}")

                    if len(seguidores_detalle) >= 200:
                        break

                if len(seguidores_detalle) == cantidad_inicial:
                    intentos_sin_nuevos += 1
                else:
                    intentos_sin_nuevos = 0

                # Scroll interno dentro del modal de seguidores
                page.evaluate("""
                    const dialog = document.querySelector("div[role='dialog']");
                    if (dialog) {
                        const scrollable = dialog.querySelector("div._a1-z, div.x1n2onr6, div._a9z6") || dialog;
                        scrollable.scrollTop += 600;
                    }
                """)
                time.sleep(2)

            print(f"  [ÉXITO] Total de seguidores procesados: {len(seguidores_detalle)}")

            page.keyboard.press("Escape")
            time.sleep(1)

        else:
            print("  [AVISO] No se encontró el texto de seguidores.")
    except Exception as e:
        print(f"  [ERROR] Ocurrió un problema en seguidores: {e}")

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

            fecha_publicacion = "No disponible"
            try:
                time_elem = page.locator("time._a9ze, time[datetime]").first
                if time_elem.is_visible():
                    fecha_publicacion = time_elem.get_attribute("datetime") or time_elem.inner_text()
            except Exception:
                pass

            descripcion = ""
            try:
                caption_elem = page.locator("h1._ap3a, div._a9zs span").first
                if caption_elem.is_visible():
                    descripcion = caption_elem.inner_text().strip()
            except Exception:
                pass

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
        "total_seguidores_analizados": len(seguidores_detalle),
        "seguidores_detalle": seguidores_detalle,
        "total_publicaciones_analizadas": len(detalle_publicaciones),
        "publicaciones_detalle": detalle_publicaciones
    }

    archivo_json = "datos.json"
    with open(archivo_json, "w", encoding="utf-8") as f:
        json.dump(datos_extraidos, f, ensure_ascii=False, indent=4)

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