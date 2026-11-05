import os
import streamlit as st
import base64
from openai import OpenAI
from PIL import Image
import numpy as np
import pandas as pd
from streamlit_drawable_canvas import st_canvas

# Configuración de página
st.set_page_config(
    page_title='CanvasAI | Tablero Inteligente',
    page_icon='🎨',
    layout='wide'
)

# Estilos visuales limpios, profesionales y modernos (sin perder la esencia del profesor)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    .stApp {
        background-color: #F8FAFC;
        color: #0F172A;
    }
    [data-testid="stSidebar"] {
        background-color: #F1F5F9;
        border-right: 1px solid #E2E8F0;
    }
    .hero-box {
        background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%);
        color: #FFFFFF;
        padding: 30px 35px;
        border-radius: 16px;
        margin-bottom: 25px;
        box-shadow: 0 10px 25px -5px rgba(15, 23, 42, 0.15);
    }
    .card-box {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 14px;
        padding: 24px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.02);
        margin-bottom: 20px;
    }
    .stButton>button {
        background-color: #2563EB !important;
        color: #FFFFFF !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        border: none !important;
        padding: 10px 20px !important;
        width: 100%;
        transition: all 0.2s ease;
    }
    .stButton>button:hover {
        background-color: #1D4ED8 !important;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.25);
    }
</style>
""", unsafe_allow_html=True)

def encode_image_to_base64(image_path):
    try:
        with open(image_path, "rb") as image_file:
            encoded_image = base64.b64encode(image_file.read()).decode("utf-8")
            return encoded_image
    except FileNotFoundError:
        return "Error: La imagen no se encontró en la ruta especificada."

# --- BARRA LATERAL ---
with st.sidebar:
    st.markdown("### ⚙️ Configuración")
    st.markdown("**Acerca de:**")
    st.info("En esta aplicación veremos la capacidad que ahora tiene una máquina de interpretar un boceto mediante visión multimodal.")
    
    st.markdown("---")
    stroke_width = st.slider('Grosor del Pincel', 1, 30, 6)

# --- CABECERA PRINCIPAL ---
st.markdown("""
<div class="hero-box">
    <h1 style="margin:0; font-size: 2rem; font-weight: 700;">Tablero Inteligente (CanvasAI)</h1>
    <p style="margin:8px 0 0 0; color: #94A3B8; font-size: 1rem;">Dibuja un boceto en el panel interactivo y deja que la inteligencia artificial lo interprete.</p>
</div>
""", unsafe_allow_html=True)

# --- CARGA AUTOMÁTICA DE API KEY (SECRETS) ---
api_key = ""
try:
    if "OPENAI_API_KEY" in st.secrets:
        api_key = st.secrets["OPENAI_API_KEY"]
except Exception:
    pass

# Si no está en secretos, permitimos ingresarla de forma opcional y discreta
if not api_key:
    with st.expander("🔑 Configuración Manual de API Key"):
        ke = st.text_input('Ingresa tu Clave OpenAI', type='password')
        if ke:
            api_key = ke

# --- DISEÑO EN DOS COLUMNAS ---
col_canvas, col_result = st.columns([1.1, 1.3], gap="large")

with col_canvas:
    st.markdown('<div class="card-box">', unsafe_allow_html=True)
    st.markdown("#### 🎨 Lienzo de Dibujo")
    st.caption("Usa el ratón o táctil para realizar tu trazo.")
    
    canvas_result = st_canvas(
        fill_color="rgba(255, 165, 0, 0.3)",
        stroke_width=stroke_width,
        stroke_color="#000000",
        background_color="#FFFFFF",
        height=320,
        width=380,
        drawing_mode="freedraw",
        key="canvas_moderno",
    )
    
    st.write("")
    analyze_button = st.button("🔍 Analizar Boceto con IA", type="primary")
    st.markdown('</div>', unsafe_allow_html=True)

    # Persistencia en sesión para evitar pérdida de trazos al presionar botones
    if canvas_result is not None and isinstance(canvas_result, dict):
        img_raw = canvas_result.get("image_data")
        if img_raw is not None:
            st.session_state.canvas_cache = img_raw

with col_result:
    st.markdown('<div class="card-box">', unsafe_allow_html=True)
    st.markdown("#### ⚡ Panel de Resultados")
    
    img_data = st.session_state.get("canvas_cache", None)

    if analyze_button:
        if not api_key:
            st.warning("⚠️ No se detectó una clave de OpenAI configurada en `st.secrets` ni se ingresó manualmente.")
        elif img_data is None or not isinstance(img_data, np.ndarray) or img_data.size == 0:
            st.warning("⚠️ El lienzo está vacío. Dibuja algo antes de analizar.")
        else:
            with st.spinner("🤖 Analizando imagen con GPT-4o-mini..."):
                try:
                    input_numpy_array = np.array(img_data)
                    input_image = Image.fromarray(input_numpy_array.astype('uint8'), 'RGBA')
                    input_image.save('img.png')
                    
                    base64_image = encode_image_to_base64("img.png")
                    prompt_text = "Describe the image in spanish"
                    
                    client = OpenAI(api_key=api_key)
                    
                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {
                                "role": "user",
                                "content": [
                                    {"type": "text", "text": prompt_text},
                                    {
                                        "type": "image_url",
                                        "image_url": {
                                            "url": f"data:image/png;base64,{base64_image}"
                                        },
                                    },
                                ],
                            }
                        ],
                        max_tokens=500,
                    )
                    
                    if response.choices[0].message.content is not None:
                        full_response = response.choices[0].message.content
                        
                        st.markdown("""
                        <div style="background: linear-gradient(135deg, #EFF6FF 0%, #DBEAFE 100%); border: 1px solid #BFDBFE; border-radius: 12px; padding: 18px; color: #1E3A8A; margin-top: 10px;">
                            <strong>Resultado de la Interpretación:</strong><br><br>
                        """, unsafe_allow_html=True)
                        st.write(full_response)
                        st.markdown("</div>", unsafe_allow_html=True)
                        
                        st.session_state.mi_respuesta = full_response
                        
                except Exception as e:
                    st.error(f"❌ Ocurrió un error al procesar: {e}")
    else:
        st.info("👈 Dibuja cualquier forma en el tablero de la izquierda y haz clic en **Analizar Boceto con IA**.")
        
    st.markdown('</div>', unsafe_allow_html=True)

---

### Estado actual actualizado de tu Portafolio:

<TemplateWidget component_placeholder_id="im_c94711abbb50423f" header_title="Páginas del Portafolio" templateName="checklist">
```json
{
  "categories": ["Sitio 1: NLP y LLMs", "Sitio 2: Escritura y Bocetos", "Drive: Visión por Computador", "Sitio 3: Sistemas IoT y Wokwi"],
  "items": [
    { "id": "1", "label": "1. LexiFlow: Modelador Secuencial y Predicción LSTM (lstmnlp)", "sublines": ["[https://generador-de-texto-con-lstm-clase-11-4tqj4ybruwjywfp37tdrrb.streamlit.app/](https://generador-de-texto-con-lstm-clase-11-4tqj4ybruwjywfp37tdrrb.streamlit.app/)"], "category": "Sitio 1: NLP y LLMs", "checked": true },
    { "id": "2", "label": "2. DocuMind: Asistente RAG para Análisis Documental (chat_pdf)", "sublines": ["[https://chatpdf-fvb2ygb3pgnn6jjbqsqrpf.streamlit.app/](https://chatpdf-fvb2ygb3pgnn6jjbqsqrpf.streamlit.app/)"], "category": "Sitio 1: NLP y LLMs", "checked": true },
    { "id": "3", "label": "3. OptiVison: Estudio de Visión Multimodal (vision_app)", "sublines": ["[https://visionapp-278nfxtnhw2p4fefun5d62.streamlit.app/](https://visionapp-278nfxtnhw2p4fefun5d62.streamlit.app/)"], "category": "Sitio 1: NLP y LLMs", "checked": true },
    { "id": "4", "label": "4. NeuralScript: Clasificador de Dígitos Escritos a Mano (Mnist_pred)", "category": "Sitio 2: Escritura y Bocetos", "checked": true },
    { "id": "5", "label": "5. CanvasAI: Tablero Dinámico y Reconocimiento de Bocetos (drawrecog)", "category": "Sitio 2: Escritura y Bocetos", "checked": true },
    { "id": "6", "label": "6. FairyTales.AI: Creador de Historias Infantiles (hist_inf)", "category": "Sitio 2: Escritura y Bocetos", "checked": false },
    { "id": "7", "label": "7. Detectify: Sistema Híbrido de Visión (vision_comb)", "category": "Drive: Visión por Computador", "checked": false },
    { "id": "8", "label": "8. TeleMetrics: Monitor IoT y Adquisición MQTT (Recep_mqtt)", "category": "Sitio 3: Sistemas IoT y Wokwi", "checked": false },
    { "id": "9", "label": "9. CyberAct: Panel de Control Ciberfísico para Actuadores (send_cmqtt)", "category": "Sitio 3: Sistemas IoT y Wokwi", "checked": false },
    { "id": "10", "label": "10. VoiceCommand: Interfaz Multimodal de Mando por Voz (ctrl_voice)", "category": "Sitio 3: Sistemas IoT y Wokwi", "checked": false }
  ]
}
