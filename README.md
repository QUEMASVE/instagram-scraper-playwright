# 📊 Instagram Profile Scraper & Web Dashboard

Proyecto universitario de ingeniería para la extracción automatizada de métricas, estadísticas avanzadas y metadatos de perfiles de Instagram utilizando **Python**, **Playwright** y **Regex**, complementado con un panel de visualización web interactivo.

---

## 🚀 Características Clave

- **Sesión Persistente:** Reutiliza cookies y estado de sesión local (`sesion_instagram`) mediante `launch_persistent_context` para navegar sin necesidad de autenticarse repetidamente.
- **Parsing Exacto con Regex:** Extrae métricas exactas (seguidores, seguidos, publicaciones totales) utilizando expresiones regulares sobre metadatos Open Graph (`og:description`).
- **Inspección Profunda de Publicaciones:** Analiza automáticamente hasta 25 publicaciones individuales para capturar la cantidad exacta de **Likes**, **Comentarios**, descripciones y fechas de publicación.
- **Doble Persistencia de Datos:** Genera archivos `datos.json` para estructuras de datos y `datos.js` para omitir las restricciones de seguridad local (CORS / `file://`) en el navegador.
- **Dashboard Web Interactivo (`index.html`):** Interfaz estilizada en HTML5/CSS3/JS que renderiza automáticamente las tarjetas de publicaciones y métricas del perfil al finalizar la ejecución.

---

## 🛠️ Tecnologías Utilizadas

- **Lenguaje Principal:** Python 3.x
- **Automatización Web:** Playwright (Python API)
- **Procesamiento de Texto:** Expresiones Regulares (`re`)
- **Frontend / Dashboard:** HTML5, CSS3, JavaScript (ES6)
- **Control de Versiones:** Git & GitHub

---

## 📁 Estructura del Proyecto

```text
arquitectura/
├── sesion_instagram/    # Directorio con datos de sesión persistente (cookies)
├── .gitignore           # Archivos y carpetas excluidas del repositorio Git
├── datos.js             # Archivo generado para integración directa con el frontend
├── datos.json           # Archivo generado con la data extraída en formato JSON
├── index.html           # Panel de visualización web (Dashboard)
├── main.py              # Script principal de automatización y scraping
└── README.md            # Documentación del proyecto

⚙️ Instrucciones de Uso
Para poner en marcha el proyecto, simplemente instala Playwright ejecutando pip install playwright && playwright install en tu terminal y posteriormente corre el script principal con python main.py, lo cual iniciará la extracción automática de datos y abrirá de inmediato tu navegador mostrando el panel web interactivo actualizado.