import os
from pathlib import Path
import streamlit as st
import pandas as pd

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
            st.info(f"Cargando CSV desde URL (DATA_CSV_URL)…")
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
