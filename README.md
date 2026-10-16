# 📊 Instagram Profile Scraper & Web Dashboard

Proyecto universitario de ingeniería para la extracción automatizada de métricas y metadatos de perfiles de Instagram utilizando Python y Playwright, con visualización mediante un panel web estático.

## 🚀 Características
- **Extracción automatizada (Python + Playwright):** Reutiliza una sesión persistente para navegar de forma segura, extrayendo la biografía, contadores de seguidores/seguidos y las últimas 25+ publicaciones.
- **Persistencia de Datos (`datos.json`):** Almacena de forma estructurada toda la información recolectada del perfil.
- **Interfaz Web (`index.html`):** Un panel local estilizado que consume el archivo JSON para mostrar las estadísticas y enlaces de forma limpia e interactiva.

## 🛠️ Tecnologías Utilizadas
- Python
- Playwright (Automatización de navegador)
- JavaScript / HTML5 / CSS3 (Dashboard web)
- Git & GitHub (Control de versiones)

## ⚙️ Instrucciones de Uso
1. Ejecuta el script de extracción en tu terminal:
   ```bash
   python main.py