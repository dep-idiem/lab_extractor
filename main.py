# test_classifier.py
from pathlib import Path
from nodes.classifier import classify

result = classify(Path("foto_formulario.jpg"))
print(result)
# → {'tipo': 'traccion_barras', 'confidence': 0.93, 'razon': '...', 'image_path': '...'}

