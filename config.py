from pathlib import Path

OLLAMA_MODEL = "qwen2.5vl:7b"
OLLAMA_HOST = "http://localhost:11434"

WATCH_FOLDER = Path("/lab_inputs")
OUTPUT_FOLDER = Path("./output")
SCHEMAS_FOLDER = Path("./schemas")

CONFIDENCE_THRESHOLD = 0.80  # bajo esto → va a revisión humana

# Todos los tipos de ensayo que el sistema conoce
ENSAYO_TYPES = {
    "traccion_barras": "Registro para el ensayo de tracción a barras helicoidales",
    "shotcrete": "Ensayo de absorción de energía en paneles de shotcrete",
    # "compresion_hormigon": "...",
    # "flexion_vigas": "...",
}