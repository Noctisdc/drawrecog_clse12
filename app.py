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
    page_title='Tablero Inteligente',
    page_icon='🎨',
    layout='wide'
)

# Estilos profesionales limpios para evitar el aspecto básico y plano
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .stApp { background-color: #F8FAFC; color: #0F172A; }
    [data-testid="stSidebar"] { background-color: #F1F5F9; border-right: 1px solid #E2E8F0; }
    .main-header {
        background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%);
        color: #FFFFFF; padding: 28px 32px; border-radius: 14px; margin-bottom: 24px;
        box-shadow: 0 10px 25px -5px rgba(15, 23, 42, 0.15);
    }
    .content-card {
        background-color: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 12px; padding: 22px; margin-bottom: 16px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.02);
    }
    .stButton>button {
        background-color: #2563EB !important; color: #FFFFFF !important; border-radius: 8px !important; font-weight: 600 !important; width: 100%;
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

# Sidebar clásico del profesor con mejor diseño
with st.sidebar:
    st.markdown("### ⚙️ Panel de Control")
    st.subheader("Acerca de:")
    st.info("En esta aplicación veremos la capacidad que ahora tiene una máquina de interpretar un boceto.")
    st.markdown("---")
    stroke_width = st.slider('Selecciona el ancho de línea', 1, 30, 5)

# Cabecera moderna pero respetando la estructura del profesor
st.markdown("""
<div class="main-header">
    <h1 style="margin:0; font-size: 1.8rem; font-weight: 700;">Tablero Inteligente</h1>
    <p style="margin:6px 0 0 0; color: #94A3B8; font-size: 0.95rem;">Interpretación multimodal de bocetos mediante inteligencia artificial.</p>
</div>
""", unsafe_allow_html=True)

st.subheader("Dibuja el boceto en el panel y presiona el botón para analizarla")

col1, col2 = st.columns([1.1, 1.3], gap="large")

with col1:
    st.markdown('<div class="content-card">', unsafe_allow_html=True)
    st.markdown("#### 🎨 Lienzo de Dibujo")
    
    drawing_mode = "freedraw"
    stroke_color = "#000000" 
    bg_color = '#FFFFFF'

    canvas_result = st_canvas(
        fill_color="rgba(255, 165, 0, 0.3)",
        stroke_width=stroke_width,
        stroke_color=stroke_color,
        background_color=bg_color,
        height=300,
        width=380,
        drawing_mode=drawing_mode,
        key="canvas_profesor_estilo",
    )
    st.markdown('</div>', unsafe_allow_html=True)
    
    if canvas_result is not None and isinstance(canvas_result, dict):
        img_raw = canvas_result.get("image_data")
        if img_raw is not None:
            st.session_state.canvas_cache = img_raw

with col2:
    st.markdown('<div class="content-card">', unsafe_allow_html=True)
    st.markdown("#### 🔑 Credenciales y Análisis")
    
    ke = st.text_input('Ingresa tu Clave', type='password')
    if ke:
        os.environ['OPENAI_API_KEY'] = ke

    api_key = os.environ.get('OPENAI_API_KEY', '')
    
    st.write("")
    analyze_button = st.button("Analiza la imagen", type="primary")
    st.markdown('</div>', unsafe_allow_html=True)

img_data = st.session_state.get("canvas_cache", None)

if analyze_button:
    if not api_key:
        st.warning("Por favor ingresa tu API key.")
    elif img_data is None or not isinstance(img_data, np.ndarray) or img_data.size == 0:
        st.warning("Por favor, dibuja algo en el lienzo.")
    else:
        with st.spinner("Analizando ..."):
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
                    <div style="background: #EFF6FF; border: 1px solid #BFDBFE; border-radius: 12px; padding: 20px; color: #1E3A8A; margin-top: 15px;">
                        <strong>Resultado de la Interpretación:</strong><br><br>
                    """, unsafe_allow_html=True)
                    st.write(full_response)
                    st.markdown("</div>", unsafe_allow_html=True)
                    st.session_state.mi_respuesta = full_response
                    
            except Exception as e:
                st.error(f"An error occurred: {e}")
