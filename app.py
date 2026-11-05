import io
import streamlit as st
from PIL import Image
from streamlit_drawable_canvas import st_canvas

st.set_page_config(page_title="Lienzo a tu medida", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Pacifico&display=swap');
.stApp {
    background-color: #fdf6ec;
}
[data-testid="stHeader"] {
    background: transparent;
}
section[data-testid="stSidebar"] {
    background-color: #f4e4d0;
}
.stApp p, .stApp label, .stApp li {
    color: #3d2b1f;
}
h1, h2, h3 {
    font-family: 'Pacifico', cursive;
    color: #e07a5f !important;
}
[data-testid="stMetricValue"], [data-testid="stMetricLabel"] {
    color: #3d2b1f !important;
}
div.stButton > button, div.stDownloadButton > button {
    background-color: #e07a5f;
    color: #ffffff !important;
    border: none;
    border-radius: 20px;
    font-weight: bold;
    padding: 8px 24px;
}
div.stButton > button:hover, div.stDownloadButton > button:hover {
    background-color: #3d2b1f;
}
</style>
""", unsafe_allow_html=True)

herramientas = {
    "Lápiz libre": "freedraw",
    "Línea": "line",
    "Rectángulo": "rect",
    "Círculo": "circle",
    "Mover y editar": "transform",
}


def hex_a_rgba(codigo, alfa):
    codigo = codigo.lstrip("#")
    r, g, b = int(codigo[0:2], 16), int(codigo[2:4], 16), int(codigo[4:6], 16)
    return f"rgba({r}, {g}, {b}, {alfa})"


with st.sidebar:
    st.subheader("Configura tu lienzo")
    herramienta = st.selectbox("Herramienta", list(herramientas.keys()))
    grosor = st.slider("Grosor del trazo", 1, 40, 8)
    color = st.color_picker("Color del trazo", "#e07a5f")
    fondo = st.color_picker("Color del fondo", "#ffffff")
    relleno = st.checkbox("Rellenar las figuras")
    ancho = st.slider("Ancho del lienzo", 300, 900, 600, 50)
    alto = st.slider("Alto del lienzo", 300, 700, 400, 50)
    st.caption("Al cambiar el tamaño o el fondo, el lienzo se reinicia.")

st.title("🎨 Lienzo a tu medida")
st.caption("Actividad: Tablero en Streamlit con propiedades configurables")
st.write("Elige tus herramientas en la barra lateral y dibuja lo que quieras.")

resultado = st_canvas(
    fill_color=hex_a_rgba(color, 0.35) if relleno else "rgba(0, 0, 0, 0)",
    stroke_width=grosor,
    stroke_color=color,
    background_color=fondo,
    height=alto,
    width=ancho,
    drawing_mode=herramientas[herramienta],
    key=f"lienzo_{ancho}_{alto}_{fondo}",
)

col1, col2 = st.columns(2)

with col1:
    if resultado.json_data is not None:
        objetos = resultado.json_data.get("objects", [])
        st.metric("Elementos dibujados", len(objetos))

with col2:
    if resultado.image_data is not None:
        imagen = Image.fromarray(resultado.image_data.astype("uint8"))
        buffer = io.BytesIO()
        imagen.save(buffer, format="PNG")
        st.download_button("Descargar dibujo", buffer.getvalue(), file_name="dibujo.png", mime="image/png")
