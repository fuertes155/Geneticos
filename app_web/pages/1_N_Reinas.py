import pathlib
import sys

import matplotlib.pyplot as plt
import streamlit as st

ROOT = pathlib.Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from algoritmos import n_reinas as nr

st.set_page_config(page_title="N-Reinas | Taller AG", page_icon="♛", layout="wide")
st.title("♛ Problema base: N-Reinas")
st.write(
    "Cada individuo es un vector de tamano N; el indice representa la columna y "
    "el valor la fila de la reina. El objetivo es llegar a 0 conflictos (ninguna "
    "reina ataca a otra)."
)

col_params, col_resultado = st.columns([1, 2])

with col_params:
    st.subheader("Parametros")
    n = st.slider("Numero de reinas (N)", min_value=4, max_value=12, value=8, key="nreinas_slider_n")
    tam_poblacion = st.select_slider("Tamano de poblacion", options=[20, 50, 100, 200], value=100, key="nreinas_pop")
    generaciones = st.slider("Generaciones maximas", min_value=50, max_value=1000, value=500, step=50, key="nreinas_gens")
    tasa_mutacion = st.select_slider("Tasa de mutacion", options=[0.05, 0.1, 0.2], value=0.1, key="nreinas_tasa")
    elitismo = st.slider("Individuos con elitismo", min_value=0, max_value=5, value=2, key="nreinas_elitismo")
    semilla = st.number_input("Semilla aleatoria", min_value=0, value=42, step=1, key="nreinas_semilla")
    ejecutar = st.button("▶ Ejecutar algoritmo genetico", type="primary", key="nreinas_boton")

if ejecutar:
    resultado = nr.ejecutar_ga(
        n=n, tam_poblacion=tam_poblacion, generaciones=generaciones,
        tasa_mutacion=tasa_mutacion, elitismo=elitismo, semilla=int(semilla),
    )
    st.session_state["nreinas_resultado"] = resultado
    st.session_state["nreinas_n"] = n

if "nreinas_resultado" in st.session_state:
    resultado = st.session_state["nreinas_resultado"]
    n_actual = st.session_state["nreinas_n"]

    with col_resultado:
        st.subheader("Resultado")
        m1, m2, m3 = st.columns(3)
        m1.metric("Resuelto", "Si" if resultado["resuelto"] else "No")
        m2.metric("Conflictos restantes", resultado["conflictos"])
        m3.metric("Generaciones usadas", resultado["generaciones_usadas"])

        individuo = resultado["mejor_individuo"]
        fig, ax = plt.subplots(figsize=(4.5, 4.5))
        tablero = [[(f + c) % 2 for c in range(n_actual)] for f in range(n_actual)]
        ax.imshow(tablero, cmap="Greys", vmin=0, vmax=1.6)
        for col, fila in enumerate(individuo):
            ax.text(col, fila, "♛", ha="center", va="center", fontsize=22, color="crimson")
        ax.set_xticks(range(n_actual))
        ax.set_yticks(range(n_actual))
        ax.set_xlabel("Columna")
        ax.set_ylabel("Fila")
        ax.set_title(f"Mejor tablero encontrado (N={n_actual})")
        st.pyplot(fig)

        st.subheader("Convergencia")
        st.line_chart({"Mejor aptitud (pares no atacantes)": resultado["historial"]})

st.divider()
st.subheader("Experimentacion sugerida por el taller")
st.write(
    "Prueba N=6 y N=8, distintos tamanos de poblacion y tasas de mutacion "
    "0.05, 0.1 y 0.2, y observa como cambia el numero de generaciones "
    "necesarias para resolver el problema (columna 'Generaciones usadas')."
)
