import os
import streamlit as st
import base64
from openai import OpenAI
from PIL import Image
import numpy as np
import pandas as pd
from streamlit_drawable_canvas import st_canvas

st.set_page_config(
    page_title='Tablero Inteligente',
    page_icon='🎨',
    layout='wide'
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .stApp { background-color: #F8FAFC; color: #0F172A; }
    [data-testid="stSidebar"] { background-color: #F1F5F9; border-right: 1px solid #E2E8F0; }
    .hero-box {
        background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%);
        color: #FFFFFF; padding: 25px 30px; border-radius: 14px; margin-bottom: 20px;
        box-shadow: 0 10px 25px -5px rgba(15, 23, 42, 0.15);
    }
    .card-box {
        background-color: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 12px; padding: 20px; margin-bottom: 15px;
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
            return base64.b64encode(image_file.read()).decode("utf-8")
    except FileNotFoundError:
        return "Error"

# Configuración de la barra lateral sin bloques 'with' para evitar excepciones de Streamlit
st.sidebar.markdown("### ⚙️ Configuración")
st.sidebar.markdown("**Acerca de:**")
st.sidebar.info("En esta aplicación veremos la capacidad que ahora tiene una máquina de interpretar un boceto mediante visión multimodal.")
st.sidebar.markdown("---")
stroke_width = st.sidebar.slider('Grosor del Pincel', 1, 30, 6)

st.markdown("""
<div class="hero-box">
    <h2 style="margin:0; font-size: 1.8rem;">Tablero Inteligente (CanvasAI)</h2>
    <p style="margin:6px 0 0 0; color: #94A3B8;">Dibuja un boceto y deja que la inteligencia artificial lo interprete.</p>
</div>
""", unsafe_allow_html=True)

api_key = ""
try:
    if "OPENAI_API_KEY" in st.secrets:
        api_key = st.secrets["OPENAI_API_KEY"]
except Exception:
    pass

if not api_key:
    with st.expander("🔑 Configuración Manual de API Key"):
        ke = st.text_input('Ingresa tu Clave OpenAI', type='password')
        if ke:
            api_key = ke

col_canvas, col_result = st.columns([1.1, 1.3], gap="large")

with col_canvas:
    st.markdown('<div class="card-box">', unsafe_allow_html=True)
    st.markdown("#### 🎨 Lienzo de Dibujo")
    
    canvas_result = st_canvas(
        fill_color="rgba(255, 165, 0, 0.3)",
        stroke_width=stroke_width,
        stroke_color="#000000",
        background_color="#FFFFFF",
        height=300,
        width=360,
        drawing_mode="freedraw",
        key="canvas_fixed",
    )
    
    st.write("")
    analyze_button = st.button("🔍 Analizar Boceto con IA", type="primary")
    st.markdown('</div>', unsafe_allow_html=True)

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
                        messages=[{
                            "role": "user",
                            "content": [
                                {"type": "text", "text": prompt_text},
                                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}"}}
                            ]
                        }],
                        max_tokens=500,
                    )
                    
                    if response.choices[0].message.content is not None:
                        full_response = response.choices[0].message.content
                        st.markdown("""
                        <div style="background: #EFF6FF; border: 1px solid #BFDBFE; border-radius: 10px; padding: 15px; color: #1E3A8A; margin-top: 10px;">
                            <strong>Resultado de la Interpretación:</strong><br><br>
                        """, unsafe_allow_html=True)
                        st.write(full_response)
                        st.markdown("</div>", unsafe_allow_html=True)
                        st.session_state.mi_respuesta = full_response
                except Exception as e:
                    st.error(f"❌ Ocurrió un error: {e}")
    else:
        st.info("👈 Dibuja cualquier forma en el tablero y haz clic en **Analizar Boceto con IA**.")
    st.markdown('</div>', unsafe_allow_html=True)
