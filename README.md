# 📊 Instagram Profile Scraper, Big Five IA & Bot Audit (Ley de Benford)

Proyecto universitario de ingeniería para la extracción automatizada de métricas, estadísticas avanzadas y metadatos de perfiles de Instagram utilizando **Python**, **Playwright** y **Regex**, complementado con un servidor web local unificado en **Flask**, análisis exploratorio de personalidad mediante **IA (Groq API / Big Five)** y auditoría estadística de cuentas falsas aplicando la **Ley de Benford**.

---

## 🚀 Características Clave

- **Sesión Persistente:** Reutiliza cookies y estado de sesión local (`sesion_instagram`) mediante `launch_persistent_context` para navegar sin necesidad de autenticarse repetidamente.
- **Parsing Exacto con Regex:** Extrae métricas exactas (seguidores, seguidos, publicaciones totales) utilizando expresiones regulares sobre metadatos Open Graph (`og:description`).
- **Inspección Profunda de Publicaciones y Red:** Analiza publicaciones individuales para capturar likes, comentarios y descripciones, además de mapear la red de seguidores recopilados.
- **Arquitectura Web Interactiva (Flask):** Servidor centralizado en el puerto `5000` que conecta la extracción con una interfaz dinámica utilizando plantillas HTML y Jinja2.
- **Análisis Exploratorio de Personalidad (Big Five):** Integración con la API de Groq para procesar lingüísticamente los textos del perfil y generar un informe estructurado en Markdown y HTML.
- **Auditoría de Bots (Ley de Benford):** Implementación de análisis estadístico sobre los primeros dígitos de los seguidores, calculando la Desviación Media Absoluta (MAD) y clasificando la autenticidad en 5 categorías con gráficas dinámicas de **Chart.js**.
- **Seguridad y Privacidad:** Gestión de credenciales sensibles mediante variables de entorno (`.env`), protegiendo la clave de API contra exposiciones públicas en control de versiones.

---

## 🛠️ Tecnologías Utilizadas

- **Lenguaje Principal:** Python 3.x
- **Backend / Servidor:** Flask, Python-dotenv
- **Inteligencia Artificial:** Groq API (Modelos de lenguaje avanzados)
- **Automatización Web:** Playwright (Python API)
- **Visualización de Datos:** Chart.js (Gráficas interactivas por CDN)
- **Frontend:** HTML5, CSS3, Jinja2 Templates
- **Control de Versiones:** Git & GitHub

---

## 📁 Estructura del Proyecto

```text
web scrapyng/
├── sesion_instagram/       # Directorio con datos de sesión persistente (cookies - Ignorado)
├── templates/              # Vistas HTML (index.html, resultado.html y seguidores.html)
├── .env                    # Variables de entorno locales (Ignorado en Git)
├── .env.example            # Plantilla de configuración de variables de entorno
├── .gitignore              # Archivos y carpetas excluidas del repositorio Git
├── datos.json              # Base de datos local con perfiles y seguidores extraídos
├── datos.js                # Archivo auxiliar de datos para el cliente
├── main.py                 # Script principal de automatización y scraping con Playwright
├── resultado_big_five.md   # Respaldo en Markdown del último análisis de personalidad
├── servidor.py             # Servidor Flask centralizado (Puerto 5000)
└── README.md               # Documentación oficial del proyecto


---

## 📁 Instrucciones de uso

1. Clonar el repositorio y configurar el entorno:
Crea tu archivo .env basado en .env.example e ingresa tu clave de API de Groq (GROQ_API_KEY).

2.Ejecutar la extracción de datos (Scraping):
python main.py

despues de ejecutar main, se abrira en el Navegador:
http://127.0.0.1:5000 para acceder al panel principal, el análisis Big Five y la auditoría de seguidores con la Ley de Benford.