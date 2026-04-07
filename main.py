from pathlib import Path
from nodes.classifier import classify
from nodes.extractor import extract
import json

image_path = Path("foto_formulario.jpg")

# Nodo 1: clasificar
print("Clasificando...")
classification = classify(image_path)
print(f"Tipo: {classification['tipo']} (confidence: {classification['confidence']})")

# Nodo 2: extraer
if classification["tipo"] != "desconocido":
    print("\nExtrayendo datos...")
    data = extract(image_path, classification["tipo"])
    print(json.dumps(data, indent=2, ensure_ascii=False))
    
    if data["needs_review"]:
        print("\n⚠️  Confidence bajo — requiere revisión humana")
else:
    print("Formulario no reconocido")