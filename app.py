import os
from pathlib import Path
import streamlit as st
import pandas as pd
import plotly.express as px  # <-- faltaba

st.set_page_config(page_title="HW - Checkboxes", page_icon="✅", layout="wide")
st.header("✅ Gráficos con casillas de verificación (Streamlit + Plotly)")

CSV_ENV = os.getenv("DATA_CSV_URL", "").strip()  # opcional: URL raw

def _candidate_paths():
    app_dir = Path(__file__).resolve().parent
    return [
        app_dir / "vehicles_us.csv",          # junto a app.py
        app_dir / "src" / "vehicles_us.csv",  # si el repo tiene src/
        app_dir.parent / "vehicles_us.csv",   # un nivel arriba
        Path.cwd() / "vehicles_us.csv",       # cwd
    ]

@st.cache_data(show_spinner=True)
def load_data():
    # 1) Si pasas URL por env var, usa eso primero
    if CSV_ENV:
        try:
            st.info("Cargando CSV desde URL (DATA_CSV_URL)…")
            return pd.read_csv(CSV_ENV)
        except Exception as e:
            st.warning(f"No pude cargar desde URL ({CSV_ENV}). Intento rutas locales. Detalle: {e}")

    # 2) Intenta rutas locales conocidas
    tried = []
    for p in _candidate_paths():
        try:
            if p.exists():
                df = pd.read_csv(p)
                st.success(f"CSV cargado desde: {p}")
                return df
            else:
                tried.append(str(p))
        except Exception as e:
            tried.append(f"{p} (error: {e})")

    # 3) Si nada funcionó, lanza un error explícito con diagnóstico
    raise FileNotFoundError(
        "No encontré 'vehicles_us.csv' en ninguna de estas rutas:\n"
        + "\n".join(f"- {t}" for t in tried)
        + f"\n\ncwd={Path.cwd()}\napp_dir={Path(__file__).resolve().parent}"
    )

# ---- Carga de datos
try:
    df = load_data()
except Exception as e:
    st.error(f"No pude cargar 'vehicles_us.csv'.\n\nDetalle: {e}")
    st.stop()

# Determinar columnas numéricas (antes de usarlas)
numeric_cols = df.select_dtypes(include="number").columns.tolist()
if not numeric_cols:
    st.warning("El dataset no tiene columnas numéricas para graficar.")
    st.stop()

# ---- Controles ----
st.subheader("Controles")

# Parámetros del histograma
st.markdown("**Parámetros del histograma**")
c_h1, c_h2 = st.columns([3,1])
with c_h1:
    col_hist = st.selectbox("Columna numérica (histograma)", numeric_cols, index=0, key="hist_col")
    bins = st.slider("Número de bins", 5, 100, 30, key="hist_bins")
with c_h2:
    build_hist = st.button("Construir histograma", key="btn_hist")

# Parámetros de la dispersión
st.markdown("**Parámetros del diagrama de dispersión**")
if len(numeric_cols) >= 2:
    c1, c2, c3, c4 = st.columns([1,1,1,1])
    with c1:
        x_col = st.selectbox("Eje X", numeric_cols, index=0, key="scatter_x")
    with c2:
        y_col = st.selectbox("Eje Y", numeric_cols, index=min(1, len(numeric_cols)-1), key="scatter_y")
    # Color opcional por categoría (si hay columnas no numéricas)
    cat_cols = df.select_dtypes(exclude="number").columns.tolist()
    with c3:
        color_opt = st.selectbox("Color por (opcional)", ["(Ninguno)"] + cat_cols, index=0, key="scatter_color")
        color_col = None if color_opt == "(Ninguno)" else color_opt
    with c4:
        build_scatter = st.button("Construir dispersión", key="btn_scatter")
else:
    st.info("Se necesitan al menos dos columnas numéricas para la dispersión.")
    build_scatter = False  # para evitar NameError

st.divider()

# ---- Render de gráficos activados por botones ----
if 'build_hist' in locals() and build_hist:
    st.subheader("📊 Histograma")
    st.write(f"Mostrando histograma de **{col_hist}** con **{bins}** bins.")
    fig_hist = px.histogram(df.dropna(subset=[col_hist]), x=col_hist, nbins=bins, title=f"Histograma de {col_hist}")
    st.plotly_chart(fig_hist, use_container_width=True)

if build_scatter:
    st.subheader("🟣 Dispersión")
    if len(numeric_cols) >= 2:
        st.write(
            f"Mostrando dispersión de **{y_col}** vs **{x_col}**"
            + (f" coloreado por **{color_col}**" if color_col else "")
        )
        df_sc = df.dropna(subset=[x_col, y_col])
        fig_scatter = px.scatter(df_sc, x=x_col, y=y_col, color=color_col, hover_data=df.columns)
        st.plotly_chart(fig_scatter, use_container_width=True)
    else:
        st.warning("No hay suficientes columnas numéricas para la dispersión.")
