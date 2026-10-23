import json
import os
import markdown
from flask import Flask, render_template, redirect, url_for
from dotenv import load_dotenv
from groq import Groq

# Cargar el .env usando la ruta absoluta del directorio actual de forma segura
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

app = Flask(__name__)

# ==========================================
# CONFIGURACIÓN SEGURA DE LA API KEY DE GROQ
# ==========================================
API_KEY = os.environ.get("GROQ_API_KEY", "")

if not API_KEY:
    print("❌ Error: No se encontró la GROQ_API_KEY en el archivo .env.")

# Inicializamos el cliente oficial de Groq
client = Groq(api_key=API_KEY)
MODELO = "qwen/qwen3.8-27b"  # El modelo activo verificado en tu cuenta

@app.route('/')
def index():
    if not os.path.exists('datos.json'):
        return "❌ Error: No existe 'datos.json'. Ejecuta primero la extracción.", 404
    
    with open('datos.json', 'r', encoding='utf-8') as f:
        datos = json.load(f)
        
    return render_template('index.html', datos=datos)

@app.route('/analizar')
def analizar():
    if not API_KEY:
        return "❌ Error crítico: La API Key de Groq no está configurada en el archivo .env.", 500

    if not os.path.exists('datos.json'):
        return "❌ Error: No existe 'datos.json'. Ejecuta primero la extracción.", 404

    with open('datos.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    perfil_url = data.get("perfil", "Desconocido")
    biografia = data.get("biografia", "Sin biografía")
    publicaciones = data.get("publicaciones_detalle", [])

    textos = []
    if biografia and biografia != "No disponible":
        textos.append(f"Biografía: {biografia}")

    for idx, post in enumerate(publicaciones, 1):
        desc = post.get("descripcion", "").strip() or post.get("resumen_meta", "").strip()
        if desc:
            textos.append(f"Post #{idx}: {desc}")

    contenido_consolidado = "\n".join(textos)

    prompt = f"""
    Actúa como un analista de datos especializado en lingüística computacional y psicología exploratoria.
    Realiza un ANÁLISIS EXPLORATORIO de los rasgos de personalidad basados en el modelo Big Five:
    1. Apertura a la experiencia
    2. Responsabilidad
    3. Extraversión
    4. Amabilidad
    5. Neuroticismo

    DATOS DEL PERFIL ({perfil_url}):
    {contenido_consolidado}

    Presenta tu análisis estructurado en formato Markdown en castellano, incluyendo una tabla resumen al final.
    """

    try:
        completion = client.chat.completions.create(
            model=MODELO,
            messages=[
                {"role": "system", "content": "Eres un analista experto en psicología exploratoria."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
        )
        
        resultado_md = completion.choices[0].message.content
        
        # Guardar archivo Markdown por respaldo
        with open("resultado_big_five.md", "w", encoding="utf-8") as f:
            f.write(resultado_md)

        # Convertir Markdown a HTML para renderizar en la web
        resultado_html = markdown.markdown(resultado_md, extensions=['tables'])
        
        return render_template('resultado.html', contenido_html=resultado_html)

    except Exception as e:
        return f"❌ Error al consultar la IA: {e}", 500

if __name__ == '__main__':
    print("🚀 Servidor local activo en: http://127.0.0.1:5000")
    app.run(port=5000, debug=True)