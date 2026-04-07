import base64
import json
from pathlib import Path
import ollama
from config import OLLAMA_MODEL, SCHEMAS_FOLDER, CONFIDENCE_THRESHOLD


def encode_image(image_path: Path) -> str:
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def load_schema(tipo: str) -> dict:
    schema_path = SCHEMAS_FOLDER / f"{tipo}.json"
    if not schema_path.exists():
        raise FileNotFoundError(f"No existe schema para el tipo: {tipo}")
    with open(schema_path, "r", encoding="utf-8") as f:
        return json.load(f)


def build_prompt(schema: dict) -> str:
    columnas = schema["tabla_probetas"]["columnas"]
    col_desc = "\n".join(
        f'  - "{c["nombre"]}" ({c["tipo"]})'
        + (f' — valores válidos: {c["valores_validos"]}' if "valores_validos" in c else "")
        + (' — puede ser null' if c.get("puede_ser_null") else "")
        for c in columnas
    )

    campos_header = "\n".join(
        f'  - "{k}" ({v["tipo"]})'
        for k, v in schema["campos_header"].items()
    )

    return f"""Eres un sistema de extracción de datos de formularios de laboratorio.

Analiza la imagen de este formulario de ensayo y extrae TODOS los datos visibles.

CAMPOS DEL ENCABEZADO a extraer:
{campos_header}

TABLA DE PROBETAS — extrae cada fila con estas columnas:
{col_desc}

INSTRUCCIONES IMPORTANTES:
- Los datos están escritos a mano sobre un formulario impreso
- Si un campo está en blanco o ilegible, usa null
- Para cada valor numérico manuscrito, interpreta con cuidado (ej: "125" no "12S")
- La tabla puede tener filas vacías al final, ignóralas
- Para "tipo_rotura" busca letras como A, B, C, D, E en la columna correspondiente
- Asigna un confidence general entre 0 y 1 según qué tan legible está el formulario

Responde ÚNICAMENTE con JSON válido, sin markdown, sin texto adicional:
{{
  "header": {{
    "cliente": null,
    "fecha_ensayo": null,
    "temperatura_ambiente": null,
    "nro_rec": null,
    "escala_maquina_kN": null
  }},
  "probetas": [
    {{
      "id_probeta": 1,
      "calidad_barra": null,
      "carga_fluencia_kgf": null,
      "carga_max_kgf": null,
      "tension_fluencia_kgf_mm2": null,
      "tension_max_kgf_mm3": null,
      "alargamiento_pct": null,
      "tipo_rotura": null
    }}
  ],
  "confidence": 0.0,
  "campos_dudosos": []
}}"""


def extract(image_path: Path, tipo: str) -> dict:
    """
    Nodo 2: Recibe la foto y el tipo de ensayo, devuelve datos estructurados.

    Returns:
        {
            "header": {...},
            "probetas": [...],
            "confidence": 0.87,
            "campos_dudosos": ["alargamiento_pct fila 3"],
            "needs_review": False,
            "tipo": "traccion_barras",
            "image_path": "..."
        }
    """
    schema = load_schema(tipo)
    prompt = build_prompt(schema)
    image_b64 = encode_image(image_path)

    response = ollama.chat(
        model=OLLAMA_MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt,
                "images": [image_b64],
            }
        ],
        options={
            "temperature": 0,
            "num_ctx": 4096,  # contexto suficiente para tablas largas
        },
    )

    raw = response["message"]["content"].strip()

    # Limpiar markdown si el modelo lo agrega igual
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()

    result = json.loads(raw)
    result["tipo"] = tipo
    result["image_path"] = str(image_path)
    result["needs_review"] = result.get("confidence", 0) < CONFIDENCE_THRESHOLD

    return result