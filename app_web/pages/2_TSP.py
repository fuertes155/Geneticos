import pathlib
import sys

import matplotlib.pyplot as plt
import streamlit as st

ROOT = pathlib.Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from algoritmos import tsp

st.set_page_config(page_title="TSP | Taller AG", page_icon="🗺️", layout="wide")
st.title("🗺️ Ejercicio 1: Problema del Agente Viajero (TSP)")
st.write(
    "Cromosoma = permutacion de ciudades. Aptitud = 1/(distancia+epsilon). "
    "Cruzamiento OX; mutacion por intercambio (swap) o inversion."
)

col_params, col_resultado = st.columns([1, 2])

with col_params:
    st.subheader("Parametros")
    n_ciudades = st.slider("Numero de ciudades", min_value=6, max_value=20, value=15, key="tsp_n_ciudades")
    semilla_ciudades = st.number_input("Semilla de las ciudades", min_value=0, value=1, step=1, key="tsp_semilla_ciudades")
    tam_poblacion = st.select_slider("Tamano de poblacion", options=[40, 80, 100, 150], value=80, key="tsp_pop")
    generaciones = st.slider("Generaciones", min_value=50, max_value=500, value=150, step=10, key="tsp_gens")
    tasa_mutacion = st.select_slider("Tasa de mutacion", options=[0.02, 0.05, 0.1, 0.2, 0.4], value=0.1, key="tsp_tasa")
    tipo_mutacion = st.radio("Tipo de mutacion", options=["swap", "inversion"], horizontal=True, key="tsp_tipo_mutacion")
    semilla_ga = st.number_input("Semilla del algoritmo", min_value=0, value=0, step=1, key="tsp_semilla_ga")
    ejecutar = st.button("▶ Ejecutar algoritmo genetico", type="primary", key="tsp_boton")

if ejecutar:
    ciudades = tsp.generar_ciudades(n_ciudades, semilla=int(semilla_ciudades))
    matriz = tsp.matriz_distancias(ciudades)
    resultado = tsp.ejecutar_ga(
        matriz, tam_poblacion=tam_poblacion, generaciones=generaciones,
        tasa_mutacion=tasa_mutacion, tipo_mutacion=tipo_mutacion, semilla=int(semilla_ga),
    )
    st.session_state["tsp_resultado"] = resultado
    st.session_state["tsp_ciudades"] = ciudades

if "tsp_resultado" in st.session_state:
    resultado = st.session_state["tsp_resultado"]
    ciudades = st.session_state["tsp_ciudades"]

    with col_resultado:
        st.subheader("Resultado")
        st.metric("Distancia de la mejor ruta", f"{resultado['mejor_distancia']:.2f}")

        ruta = resultado["mejor_individuo"] + [resultado["mejor_individuo"][0]]
        xs = [ciudades[i][0] for i in ruta]
        ys = [ciudades[i][1] for i in ruta]
        fig, ax = plt.subplots(figsize=(5, 5))
        ax.plot(xs, ys, "o-", color="steelblue")
        for idx, (x, y) in enumerate(ciudades):
            ax.annotate(str(idx), (x, y), textcoords="offset points", xytext=(4, 4))
        ax.set_title("Mejor ruta encontrada")
        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        st.pyplot(fig)

        st.subheader("Convergencia")
        st.line_chart({"Mejor distancia": resultado["historial"]})

st.divider()
st.subheader("Preguntas del taller")
st.markdown(
    """
- **¿Por que no puede usarse un cruzamiento binario simple sin controlar duplicados?**
  Porque el cromosoma es una *permutacion*: cada ciudad debe aparecer exactamente una vez.
  Un cruzamiento de un punto clasico (como el binario) combina segmentos sin verificar
  que ciudades ya fueron usadas, generando hijos invalidos (ciudades repetidas y otras
  ausentes). Por eso se usan operadores como OX o PMX, que reconstruyen una permutacion valida.
- **¿Que pasa si aumenta el numero de ciudades?** El espacio de busqueda crece
  factorialmente ((N-1)!/2 rutas posibles), por lo que se necesitan mas generaciones
  y/o poblacion para mantener la calidad de la solucion; con los mismos parametros,
  la distancia relativa al optimo tiende a empeorar.
- **¿Que estrategia de mutacion encuentra mejores rutas?** En las pruebas de este
  taller (15 ciudades, poblacion 80, 150 generaciones), el intercambio (swap) con
  tasa moderada (0.1) obtuvo en promedio mejores resultados y menor variabilidad que
  tasas muy bajas (subexploracion) o muy altas (destruyen buenas rutas encontradas).
"""
)
