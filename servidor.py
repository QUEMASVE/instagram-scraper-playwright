import json  
import os
import re #para bucar expresiones regulares y patrones d etexto
import markdown # traduce el texto plano a codigo html bonito
from flask import Flask, render_template, redirect, url_for
#falsk es un framework que arma el servidor, levanta pagina, concta botones
from dotenv import load_dotenv #sirve para cargar de forma segura la contraseña de apikey 
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

# ==========================================
# RUTA: TABLA DE SEGUIDORES
# ==========================================
@app.route('/seguidores')
def ver_seguidores():
    if not os.path.exists('datos.json'):
        return "❌ Error: No existe 'datos.json'. Ejecuta primero la extracción.", 404
        
    try:
        with open('datos.json', 'r', encoding='utf-8') as f:
            datos = json.load(f)
    except Exception as e:
        datos = {"seguidores_detalle": [], "perfil": "Error al leer datos"}
        
    return render_template('seguidores.html', datos=datos)

# ==========================================
# LÓGICA Y RUTA: LEY DE BENFORD Y BOTS
# ==========================================
BENFORD_TEORICO = {
    1: 0.301, 2: 0.176, 3: 0.125, 4: 0.097, 
    5: 0.079, 6: 0.067, 7: 0.058, 8: 0.051, 9: 0.046
}

def extraer_primer_digito(texto_seguidores):
    if not texto_seguidores or texto_seguidores == "No detectado":
        return None
    texto = str(texto_seguidores).upper().strip()
    match = re.search(r'[1-9]', texto)
    if match:
        return int(match.group(0))
    return None

def calcular_ley_benford(seguidores_detalle):
    conteo = {i: 0 for i in range(1, 10)}
    total_validos = 0
    
    for seg in seguidores_detalle:
        est = seg.get("estadisticas", {})
        foll_str = est.get("seguidores", "No detectado") if isinstance(est, dict) else "No detectado"
        
        digito = extraer_primer_digito(foll_str)
        if digito:
            conteo[digito] += 1
            total_validos += 1
    
    real_pct = {}
    if total_validos > 0:
        for d in range(1, 10):
            real_pct[d] = conteo[d] / total_validos
    else:
        real_pct = {d: 0.0 for d in range(1, 10)}
        
    # Desviación Media Absoluta (MAD)
    mad = 0.0
    for d in range(1, 10):
        mad += abs(real_pct[d] - BENFORD_TEORICO[d])
    mad /= 9.0
    
    # Clasificación en 5 categorías de bots
    if mad < 0.025:
        categoria = "No es bot"
        color = "#28a745"
    elif mad < 0.050:
        categoria = "Probablemente no es bot"
        color = "#17a2b8"
    elif mad < 0.080:
        categoria = "Sospechoso"
        color = "#ffc107"
    elif mad < 0.120:
        categoria = "Probablemente bot"
        color = "#fd7e14"
    else:
        categoria = "Es bot"
        color = "#dc3545"
        
    return {
        "total_analizados": total_validos,
        "real_pct": {k: round(v * 100, 2) for k, v in real_pct.items()},
        "teorico_pct": {k: round(v * 100, 2) for k, v in BENFORD_TEORICO.items()},
        "mad": round(mad, 4),
        "categoria": categoria,
        "color": color
    }

@app.route('/calcular_benford')
def api_calcular_benford():
    if not os.path.exists('datos.json'):
        return "❌ Error: No existe 'datos.json'.", 404
        
    with open('datos.json', 'r', encoding='utf-8') as f:
        datos = json.load(f)
        
    resultado_benford = calcular_ley_benford(datos.get("seguidores_detalle", []))
    
    return render_template('seguidores.html', datos=datos, benford=resultado_benford)

if __name__ == '__main__':
    print("🚀 Servidor local activo en: http://127.0.0.1:5000")
    app.run(port=5000, debug=True)