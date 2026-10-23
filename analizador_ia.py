import json
import os
from dotenv import load_dotenv
from groq import Groq

# ==========================================
# CONFIGURACIÓN SEGURA DE LA API KEY DE GROQ
# ==========================================
# Cargar el .env usando la ruta absoluta del directorio actual de forma segura
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

API_KEY = os.environ.get("GROQ_API_KEY", "")

if not API_KEY or API_KEY == "TU_API_KEY_GROQ_AQUI":
    print("❌ Error: No se encontró la GROQ_API_KEY en las variables de entorno ni en el archivo .env.")
    print("💡 Asegúrate de crear un archivo '.env' en la raíz de tu proyecto con tu clave.")
    exit(1)

# Inicializamos el cliente oficial de Groq
client = Groq(api_key=API_KEY)

# ==========================================
# MODELO SELECCIONADO DE TU LISTA
# ==========================================
MODELO = "qwen/qwen3.8-27b" 

# ==========================================
# LECTURA DE DATOS LOCALES (datos.json)
# ==========================================
archivo_json = "datos.json"
if not os.path.exists(archivo_json):
    print(f"❌ No se encontró el archivo '{archivo_json}'. Ejecuta primero main.py para extraer los datos.")
    exit(1)

print(f"Leyendo datos desde '{archivo_json}'...")
with open(archivo_json, "r", encoding="utf-8") as f:
    data = json.load(f)

perfil_url = data.get("perfil", "Desconocido")
biografia = data.get("biografia", "Sin biografía")
publicaciones = data.get("publicaciones_detalle", [])

# Filtramos textos con respaldo inteligente
textos_para_analisis = []
if biografia and biografia != "No disponible":
    textos_para_analisis.append(f"Biografía del perfil: {biografia}")

for idx, post in enumerate(publicaciones, 1):
    desc = post.get("descripcion", "").strip()
    if not desc:
        desc = post.get("resumen_meta", "").strip()
    
    if desc:
        textos_para_analisis.append(f"Post #{idx} (Likes: {post.get('likes', '0')}): {desc}")

print(f"Textos válidos extraídos para análisis: {len(textos_para_analisis)} elementos.")

if len(textos_para_analisis) < 3:
    print("⚠️ Advertencia: Hay muy pocos textos disponibles para un análisis de lenguaje significativo.")

contenido_consolidado = "\n".join(textos_para_analisis)

# ==========================================
# CONSTRUCCIÓN DEL PROMPT BIG FIVE
# ==========================================
prompt = f"""
Actúa como un analista de datos especializado en lingüística computacional y psicología exploratoria. 
A continuación, te proporcionaré una muestra de textos públicos extraídos de un perfil de Instagram (biografía y descripciones de publicaciones).

Tu tarea es realizar un ANÁLISIS EXPLORATORIO de los rasgos de personalidad basados estrictamente en el modelo de los Cinco Grandes (Big Five):
1. Apertura a la experiencia
2. Responsabilidad
3. Extraversión
4. Amabilidad
5. Neuroticismo

INSTRUCCIONES CRÍTICAS:
- Trata los resultados estrictamente como estimaciones exploratorias basadas en muestras de lenguaje público, NUNCA como un diagnóstico clínico o evaluación psicológica validada.
- Si los datos son insuficientes, ambiguos o escasos para evaluar alguna dimensión, indícalo claramente en lugar de inventar conclusiones.
- Fundamenta brevemente cada dimensión mencionando evidencias textuales de los datos proporcionados.

DATOS DEL PERFIL ({perfil_url}):
{contenido_consolidado}

Por favor, presenta tu análisis de forma estructurada y clara en formato Markdown y en castellano.
"""

# ==========================================
# LLAMADA A LA API DE GROQ
# ==========================================
print(f"\nEnviando datos a Groq ({MODELO}) para el análisis exploratorio Big Five...")

try:
    completion = client.chat.completions.create(
        model=MODELO,
        messages=[
            {"role": "system", "content": "Eres un analista experto en lingüística computacional y psicología exploratoria."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
    )

    resultado = completion.choices[0].message.content

    print("\n" + "="*50)
    print("🧠 RESULTADO DEL ANÁLISIS EXPLORATORIO (BIG FIVE - GROQ)")
    print("="*50 + "\n")
    print(resultado)
    print("\n" + "="*50)

    with open("resultado_big_five.md", "w", encoding="utf-8") as f:
        f.write(resultado)
    print("📁 Resultado guardado exitosamente en 'resultado_big_five.md'.")

except Exception as ex:
    print(f"❌ Ocurrió un error con la API de Groq: {ex}")