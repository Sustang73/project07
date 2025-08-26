import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

st.set_page_config(page_title="HW - Checkboxes", page_icon="✅", layout="wide")

st.header("✅ Gráficos con casillas de verificación (Streamlit + Plotly)")

@st.cache_data(show_spinner=True)
def load_data():
    csv_path = (Path(__file__).resolve().parent / ".." / "vehicles_us.csv").resolve()
    return pd.read_csv(csv_path)

# Carga de datos
try:
    df = load_data()
except Exception as e:
    st.error(f"No pude cargar ../vehicles_us.csv\n\nDetalle: {e}")
    st.stop()

numeric_cols = df.select_dtypes(include="number").columns.tolist()
if not numeric_cols:
    st.warning("El dataset no tiene columnas numéricas para graficar.")
    st.stop()

# ---- Controles ----
st.subheader("Controles")
show_hist = st.checkbox("Mostrar histograma")
show_scatter = st.checkbox("Mostrar diagrama de dispersión")

# Parámetros del histograma
st.subheader("Parámetros del histograma")
col_hist = st.selectbox("Columna numérica (histograma)", numeric_cols, index=0)
bins = st.slider("Número de bins", 5, 100, 30)

# Parámetros de la dispersión
st.subheader("Parámetros de la dispersión")
if len(numeric_cols) >= 2:
    c1, c2, c3 = st.columns([1,1,1])
    with c1:
        x_col = st.selectbox("Eje X", numeric_cols, index=0, key="scatter_x")
    with c2:
        y_col = st.selectbox("Eje Y", numeric_cols, index=min(1, len(numeric_cols)-1), key="scatter_y")
    # Color opcional por categoría (si hay columnas no numéricas)
    cat_cols = df.select_dtypes(exclude="number").columns.tolist()
    with c3:
        color_opt = st.selectbox("Color por (opcional)", ["(Ninguno)"] + cat_cols, index=0)
        color_col = None if color_opt == "(Ninguno)" else color_opt
else:
    st.info("Se necesitan al menos dos columnas numéricas para la dispersión.")

st.divider()

# ---- Render de gráficos según checkboxes ----
if show_hist:
    st.subheader("📊 Histograma")
    st.write(f"Mostrando histograma de **{col_hist}** con **{bins}** bins.")
    fig_hist = px.histogram(df, x=col_hist, nbins=bins, title=f"Histograma de {col_hist}")
    st.plotly_chart(fig_hist, use_container_width=True)

if show_scatter:
    st.subheader("🟣 Dispersión")
    if len(numeric_cols) >= 2:
        st.write(f"Mostrando dispersión de **{y_col}** vs **{x_col}**" + (f" coloreado por **{color_col}**" if color_col else ""))
        fig_scatter = px.scatter(df, x=x_col, y=y_col, color=color_col, hover_data=df.columns)
        st.plotly_chart(fig_scatter, use_container_width=True)
    else:
        st.warning("No hay suficientes columnas numéricas para la dispersión.")