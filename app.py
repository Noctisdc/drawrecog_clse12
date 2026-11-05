import os
import streamlit as st
import base64
from openai import OpenAI
import tensorflow as tf
from PIL import Image
import numpy as np
import pandas as pd
from streamlit_drawable_canvas import st_canvas

st.set_page_config(page_title='Tablero Inteligente', page_icon='🎨', layout='wide')

def encode_image_to_base64(image_path):
    try:
        with open(image_path, "rb") as image_file:
            encoded_image = base64.b64encode(image_file.read()).decode("utf-8")
            return encoded_image
    except FileNotFoundError:
        return "Error: La imagen no se encontró en la ruta especificada."

# Sidebar
with st.sidebar:
    st.subheader("Acerca de:")
    st.subheader("En esta aplicación veremos la capacidad que ahora tiene una máquina de interpretar un boceto")
    stroke_width = st.slider('Selecciona el ancho de línea', 1, 30, 5)

st.title('Tablero Inteligente')
st.subheader("Dibuja el boceto en el panel y presiona el botón para analizarla")

col1, col2 = st.columns([2, 1])

with col1:
    drawing_mode = "freedraw"
    stroke_color = "#000000" 
    bg_color = '#FFFFFF'

    canvas_result = st_canvas(
        fill_color="rgba(255, 165, 0, 0.3)",
        stroke_width=stroke_width,
        stroke_color=stroke_color,
        background_color=bg_color,
        height=300,
        width=400,
        drawing_mode=drawing_mode,
        key="canvas",
    )
    
    # Guardar en sesión de forma segura para evitar pérdida de datos al recargar
    if canvas_result is not None and isinstance(canvas_result, dict):
        img_raw = canvas_result.get("image_data")
        if img_raw is not None:
            st.session_state.canvas_cache = img_raw

with col2:
    ke = st.text_input('Ingresa tu Clave', type='password')
    if ke:
        os.environ['OPENAI_API_KEY'] = ke

    api_key = os.environ.get('OPENAI_API_KEY', '')
    analyze_button = st.button("Analiza la imagen", type="secondary")

# Recuperar datos cacheados
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
                                    "image_url": {
                                        "url": f"data:image/png;base64,{base64_image}"
                                    },
                                    "type": "image_url",
                                },
                            ],
                        }
                    ],
                    max_tokens=500,
                )
                
                if response.choices[0].message.content is not None:
                    full_response = response.choices[0].message.content
                    st.markdown("### Resultado:")
                    st.write(full_response)
                    st.session_state.mi_respuesta = full_response
                    
            except Exception as e:
                st.error(f"An error occurred: {e}")
