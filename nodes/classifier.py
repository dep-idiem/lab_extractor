import base64
import json
from pathlib import Path
import ollama
from config import OLLAMA_MODEL, ENSAYO_TYPES


def encode_image(image_path: Path) -> str:
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def classify(image_path: Path) -> dict:
    """
    Nodo 1: Recibe una foto de formulario y devuelve el tipo de ensayo.
    
    Returns:
        {
            "tipo": "traccion_barras",
            "confidence": 0.95,
            "razon": "El título del formulario dice 'Ensayo de tracción a barras helicoidales'"
        }
    """
    tipos_conocidos = "\n".join(
        f'- "{key}": {descripcion}'
        for key, descripcion in ENSAYO_TYPES.items()
    )

    prompt = f"""Eres un clasificador de formularios de laboratorio de estructuras.

Analiza la imagen y determina qué tipo de formulario es.

Los tipos conocidos son:
{tipos_conocidos}

Responde ÚNICAMENTE con un JSON válido, sin texto adicional, sin markdown:
{{
    "tipo": "<clave del tipo, o 'desconocido' si no coincide con ninguno>",
    "confidence": <float entre 0 y 1>,
    "razon": "<una frase corta explicando por qué>"
}}"""

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
        options={"temperature": 0},  # determinismo máximo para clasificación
    )

    raw = response["message"]["content"].strip()

    # Limpiar posibles ```json ... ``` que el modelo a veces agrega igual
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()

    result = json.loads(raw)
    result["image_path"] = str(image_path)
    return result