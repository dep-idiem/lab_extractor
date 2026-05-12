"""
Mockup demo de lab_extractor.

Simula la entrega de una imagen de formulario y muestra el resultado
de la clasificación + extracción sin necesidad de tener Ollama corriendo.

Run:
    streamlit run review/app.py
"""
from pathlib import Path
import json
import streamlit as st
from PIL import Image

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_IMAGE = REPO_ROOT / "image.png"
CONFIDENCE_THRESHOLD = 0.80


MOCK_CLASSIFICATION = {
    "tipo": "traccion_barras",
    "confidence": 0.96,
    "razon": "El título dice 'Registro para el ensayo de tracción a barras helicoidales'.",
}

MOCK_EXTRACTION = {
    "tipo": "traccion_barras",
    "header": {
        "cliente": "Minera Los Pelambres",
        "fecha_ensayo": "2026-04-22",
        "temperatura_ambiente": 19.5,
        "nro_rec": "REC-2814",
        "escala_maquina_kN": 600.0,
    },
    "probetas": [
        {
            "id_probeta": 1,
            "calidad_barra": "A630-420H",
            "carga_fluencia_kgf": 12450.0,
            "carga_max_kgf": 17820.0,
            "tension_fluencia_kgf_mm2": 44.1,
            "tension_max_kgf_mm3": 63.2,
            "alargamiento_pct": 14.8,
            "tipo_rotura": "B",
        },
        {
            "id_probeta": 2,
            "calidad_barra": "A630-420H",
            "carga_fluencia_kgf": 12380.0,
            "carga_max_kgf": 17640.0,
            "tension_fluencia_kgf_mm2": 43.9,
            "tension_max_kgf_mm3": 62.6,
            "alargamiento_pct": 15.1,
            "tipo_rotura": "B",
        },
        {
            "id_probeta": 3,
            "calidad_barra": "A630-420H",
            "carga_fluencia_kgf": 12510.0,
            "carga_max_kgf": 17905.0,
            "tension_fluencia_kgf_mm2": 44.3,
            "tension_max_kgf_mm3": 63.5,
            "alargamiento_pct": None,
            "tipo_rotura": "A",
        },
        {
            "id_probeta": 4,
            "calidad_barra": "A630-420H",
            "carga_fluencia_kgf": 12290.0,
            "carga_max_kgf": 17580.0,
            "tension_fluencia_kgf_mm2": 43.6,
            "tension_max_kgf_mm3": 62.4,
            "alargamiento_pct": 14.5,
            "tipo_rotura": "B",
        },
    ],
    "confidence": 0.87,
    "campos_dudosos": ["alargamiento_pct fila 3 (ilegible)"],
}
MOCK_EXTRACTION["needs_review"] = MOCK_EXTRACTION["confidence"] < CONFIDENCE_THRESHOLD


def confidence_badge(value: float) -> str:
    if value >= 0.90:
        color, label = "#16a34a", "alta"
    elif value >= CONFIDENCE_THRESHOLD:
        color, label = "#ca8a04", "media"
    else:
        color, label = "#dc2626", "baja"
    return (
        f'<span style="background:{color};color:white;padding:2px 10px;'
        f'border-radius:12px;font-size:0.85rem;font-weight:600">'
        f"{value:.0%} · {label}</span>"
    )


def render_header(header: dict) -> None:
    cols = st.columns(len(header))
    pretty = {
        "cliente": "Cliente",
        "fecha_ensayo": "Fecha ensayo",
        "temperatura_ambiente": "Temp. ambiente (°C)",
        "nro_rec": "N° REC",
        "escala_maquina_kN": "Escala máquina (kN)",
    }
    for col, (k, v) in zip(cols, header.items()):
        col.metric(pretty.get(k, k), "—" if v is None else v)


st.set_page_config(
    page_title="lab_extractor · demo",
    page_icon="🧪",
    layout="wide",
)

st.title("🧪 lab_extractor — demo")
st.caption(
    "Subí una foto de un formulario de ensayo y mirá cómo el pipeline lo clasifica "
    "y extrae los datos estructurados. *(Esta vista es un mockup con datos simulados.)*"
)

with st.sidebar:
    st.header("Entrada")
    uploaded = st.file_uploader(
        "Subir formulario", type=["png", "jpg", "jpeg", "pdf"]
    )
    use_default = st.toggle(
        "Usar imagen de ejemplo", value=uploaded is None, disabled=uploaded is not None
    )
    st.divider()
    st.subheader("Pipeline")
    st.markdown(
        "1. **Clasificador** (qwen2.5vl) → tipo de ensayo\n"
        "2. **Extractor** (qwen2.5vl + schema) → JSON estructurado\n"
        "3. **Validador** → flag de revisión humana\n"
        "4. **Exporter** → Excel / DB"
    )
    st.divider()
    st.caption(f"Threshold actual: **{CONFIDENCE_THRESHOLD:.0%}**")

image_source = None
if uploaded is not None:
    image_source = uploaded
elif use_default and DEFAULT_IMAGE.exists():
    image_source = DEFAULT_IMAGE

if image_source is None:
    st.info("Subí una imagen o activá *Usar imagen de ejemplo* en la barra lateral.")
    st.stop()

left, right = st.columns([1, 1.3], gap="large")

with left:
    st.subheader("Formulario recibido")
    st.image(Image.open(image_source), use_container_width=True)

with right:
    st.subheader("Resultado")

    with st.container(border=True):
        st.markdown("**Paso 1 · Clasificación**")
        c1, c2 = st.columns([1, 1])
        c1.markdown(
            f"Tipo detectado: `{MOCK_CLASSIFICATION['tipo']}`<br>"
            f"Confidence: {confidence_badge(MOCK_CLASSIFICATION['confidence'])}",
            unsafe_allow_html=True,
        )
        c2.markdown(f"*{MOCK_CLASSIFICATION['razon']}*")

    extraction = MOCK_EXTRACTION

    with st.container(border=True):
        top = st.columns([2, 1])
        top[0].markdown("**Paso 2 · Extracción**")
        top[1].markdown(
            f"Confidence global: {confidence_badge(extraction['confidence'])}",
            unsafe_allow_html=True,
        )

        st.markdown("##### Encabezado")
        render_header(extraction["header"])

        st.markdown("##### Probetas")
        st.dataframe(
            extraction["probetas"],
            hide_index=True,
            use_container_width=True,
        )

        if extraction["campos_dudosos"]:
            st.markdown("##### Campos dudosos")
            for campo in extraction["campos_dudosos"]:
                st.markdown(f"- ⚠️ {campo}")

    if extraction["needs_review"]:
        st.warning(
            "⚠️ La confidence está por debajo del threshold "
            f"({CONFIDENCE_THRESHOLD:.0%}) — este formulario va a revisión humana."
        )
    else:
        st.success("✅ Extracción aprobada automáticamente.")

    with st.expander("Ver JSON crudo (lo que recibe el exporter)"):
        st.code(json.dumps(extraction, indent=2, ensure_ascii=False), language="json")
