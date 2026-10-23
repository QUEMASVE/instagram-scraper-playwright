# 📊 Instagram Profile Scraper & Web Dashboard (Big Five IA)

Proyecto universitario de ingeniería para la extracción automatizada de métricas, estadísticas avanzadas y metadatos de perfiles de Instagram utilizando **Python**, **Playwright** y **Regex**, complementado con un servidor web local en **Flask** y análisis exploratorio de personalidad mediante **IA (Groq API / Big Five)**.

---

## 🚀 Características Clave

- **Sesión Persistente:** Reutiliza cookies y estado de sesión local (`sesion_instagram`) mediante `launch_persistent_context` para navegar sin necesidad de autenticarse repetidamente.
- **Parsing Exacto con Regex:** Extrae métricas exactas (seguidores, seguidos, publicaciones totales) utilizando expresiones regulares sobre metadatos Open Graph (`og:description`).
- **Inspección Profunda de Publicaciones:** Analiza automáticamente hasta 25 publicaciones individuales para capturar la cantidad exacta de **Likes**, **Comentarios**, descripciones y fechas de publicación.
- **Arquitectura Web Interactiva (Flask):** Servidor local integrado que conecta la extracción con una interfaz dinámica utilizando plantillas HTML y Jinja2.
- **Análisis Exploratorio de Personalidad (Big Five):** Integración con la API de Groq para procesar lingüísticamente los textos del perfil y generar un informe estructurado en Markdown y HTML.
- **Seguridad y Privacidad:** Gestión de credenciales sensibles mediante variables de entorno (`.env`), protegiendo la clave de API contra exposiciones públicas en control de versiones.

---

## 🛠️ Tecnologías Utilizadas

- **Lenguaje Principal:** Python 3.x
- **Backend / Servidor:** Flask, Python-dotenv
- **Inteligencia Artificial:** Groq API (Modelos de lenguaje avanzados)
- **Automatización Web:** Playwright (Python API)
- **Frontend:** HTML5, CSS3, Jinja2 Templates
- **Control de Versiones:** Git & GitHub

---

## 📁 Estructura del Proyecto

```text
arquitectura/
├── sesion_instagram/      # Directorio con datos de sesión persistente (cookies - Ignorado)
├── templates/             # Vistas HTML (index.html y resultado.html)
├── .env.example           # Plantilla de configuración de variables de entorno
├── .gitignore             # Archivos y carpetas excluidas del repositorio Git
├── analizador_ia.py       # Script de conexión y análisis con la API de Groq
├── main.py                # Script principal de automatización, scraping y despliegue web
├── servidor.py            # Servidor Flask para la interfaz interactiva local
└── README.md              # Documentación oficial del proyecto