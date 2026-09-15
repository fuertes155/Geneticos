import pathlib
import sys

import streamlit as st

ROOT = pathlib.Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from algoritmos import mochila

st.set_page_config(page_title="Mochila | Taller AG", page_icon="🎒", layout="wide")
st.title("🎒 Ejercicio 3: Problema de la Mochila (Knapsack)")
st.write(
    "Cromosoma binario: gen=1 si el objeto se selecciona. Se compara la "
    "estrategia de **penalizacion** contra la de **reparacion** de individuos "
    "que exceden la capacidad."
)

st.subheader("Objetos disponibles (edita peso/valor si quieres)")
objetos_editados = st.data_editor(
    mochila.OBJETOS, num_rows="fixed", width="stretch", key="editor_objetos"
)

col_params, col_resultado = st.columns([1, 2])

with col_params:
    st.subheader("Parametros")
    capacidad = st.slider("Capacidad de la mochila", min_value=5, max_value=60, value=25, key="mochila_capacidad")
    modo = st.radio("Estrategia", options=["penalizacion", "reparacion"], horizontal=True, key="mochila_modo")
    tam_poblacion = st.select_slider("Tamano de poblacion", options=[30, 50, 100, 150], value=100, key="mochila_pop")
    generaciones = st.slider("Generaciones", min_value=20, max_value=400, value=200, step=20, key="mochila_gens")
    tasa_mutacion = st.select_slider("Tasa de mutacion", options=[0.02, 0.05, 0.1, 0.2], value=0.05, key="mochila_tasa")
    semilla = st.number_input("Semilla aleatoria", min_value=0, value=0, step=1, key="mochila_semilla")
    ejecutar = st.button("▶ Ejecutar algoritmo genetico", type="primary", key="mochila_boton")

if ejecutar:
    mochila.OBJETOS = objetos_editados.reset_index(drop=True)
    mochila.PESOS = mochila.OBJETOS["peso"].tolist()
    mochila.VALORES = mochila.OBJETOS["valor"].tolist()

    resultado = mochila.ejecutar_ga(
        capacidad=capacidad, tam_poblacion=tam_poblacion, generaciones=generaciones,
        tasa_mutacion=tasa_mutacion, modo=modo, semilla=int(semilla),
    )
    st.session_state["mochila_resultado"] = resultado
    st.session_state["mochila_capacidad_usada"] = capacidad

if "mochila_resultado" in st.session_state:
    resultado = st.session_state["mochila_resultado"]
    capacidad_usada = st.session_state["mochila_capacidad_usada"]

    with col_resultado:
        st.subheader("Resultado")
        m1, m2, m3 = st.columns(3)
        m1.metric("Valor total", resultado["mejor_valor"])
        m2.metric("Peso usado", f"{resultado['mejor_peso']} / {capacidad_usada}")
        m3.metric("Generacion de la mejor solucion", resultado["mejor_generacion"])

        st.progress(min(1.0, resultado["mejor_peso"] / capacidad_usada))

        st.markdown("**Objetos seleccionados:**")
        st.dataframe(mochila.seleccion_a_tabla(resultado["mejor_individuo"]), width="stretch", key="mochila_tabla_seleccion")

        st.subheader("Convergencia")
        st.line_chart({"Mejor valor factible": resultado["historial"]})

st.divider()
st.subheader("Preguntas del taller")
st.write(
    "**¿Por que este problema permite usar cromosomas binarios?** Porque cada "
    "objeto tiene exactamente dos estados posibles e independientes entre si "
    "(incluido o no incluido), sin restriccion de orden ni de unicidad entre "
    "genes; un bit por objeto representa esa decision de forma natural y "
    "permite usar los operadores geneticos binarios clasicos (cruzamiento de "
    "un punto, bit-flip) sin generar cromosomas invalidos por construccion."
)
