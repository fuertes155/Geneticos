import pathlib
import sys

import streamlit as st

ROOT = pathlib.Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from algoritmos import asignacion_cursos as ac

st.set_page_config(page_title="Asignacion de cursos | Taller AG", page_icon="🗓️", layout="wide")
st.title("🗓️ Ejercicio 2: Asignacion de cursos a salas de computo")
st.write(
    "Cada gen codifica la (sala, franja) asignada a un curso. La aptitud "
    "penaliza sobrecupo, falta de recursos, choques de sala/franja y franjas "
    "bloqueadas; premia una distribucion equilibrada entre salas."
)

tab_datos, tab_ga = st.tabs(["📋 Datos del problema", "🧬 Ejecutar algoritmo genetico"])

with tab_datos:
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Cursos**")
        st.dataframe(ac.CURSOS, width="stretch", key="cursos_tabla_cursos")
    with col2:
        st.markdown("**Salas**")
        st.dataframe(ac.SALAS, width="stretch", key="cursos_tabla_salas")
    st.markdown(
        f"**Franjas horarias:** {', '.join(ac.FRANJAS)}  \n"
        f"**Franjas bloqueadas (sala, franja):** {sorted(ac.FRANJAS_BLOQUEADAS)}"
    )

with tab_ga:
    col_params, col_resultado = st.columns([1, 2])

    with col_params:
        st.subheader("Parametros")
        tam_poblacion = st.select_slider("Tamano de poblacion", options=[20, 50, 100, 150], value=100, key="cursos_pop")
        generaciones = st.slider("Generaciones", min_value=10, max_value=500, value=200, step=10, key="cursos_gens")
        tasa_mutacion = st.select_slider("Tasa de mutacion", options=[0.05, 0.1, 0.15, 0.2], value=0.1, key="cursos_tasa")
        usar_elitismo = st.checkbox("Usar elitismo", value=True, key="cursos_elitismo_check")
        elitismo = 2 if usar_elitismo else 0
        semilla = st.number_input("Semilla aleatoria", min_value=0, value=0, step=1, key="cursos_semilla")
        ejecutar = st.button("▶ Ejecutar algoritmo genetico", type="primary", key="cursos_boton")

    if ejecutar:
        resultado = ac.ejecutar_ga(
            tam_poblacion=tam_poblacion, generaciones=generaciones,
            tasa_mutacion=tasa_mutacion, elitismo=elitismo, semilla=int(semilla),
        )
        st.session_state["cursos_resultado"] = resultado

    if "cursos_resultado" in st.session_state:
        resultado = st.session_state["cursos_resultado"]
        individuo = resultado["mejor_individuo"]

        with col_resultado:
            st.subheader("Resultado")
            st.metric("Penalizacion final (0 = sin conflictos)", round(resultado["mejor_penalizacion"], 2))

            desglose = ac.desglosar_penalizacion(individuo)
            st.markdown("**Desglose de penalizacion:**")
            st.table({k: [round(v, 2)] for k, v in desglose.items()})

            st.subheader("Horario resultante")
            tabla_horario = ac.horario_a_tabla(individuo)

            def resaltar_vacios(valor):
                return "color: #999" if valor == "-" else ""

            st.dataframe(tabla_horario.style.map(resaltar_vacios), width="stretch", key="cursos_tabla_horario")

            st.subheader("Convergencia")
            st.line_chart({"Mejor penalizacion": resultado["historial"]})

st.divider()
st.subheader("Preguntas del taller")
st.markdown(
    """
- **¿Que restricciones son duras y cuales blandas?** Duras: sobrecupo, sala sin
  recursos requeridos, dos cursos en la misma sala/franja y franjas bloqueadas
  (una solucion con estas violaciones no es utilizable). Blanda: la distribucion
  equilibrada de cursos entre salas (deseable, pero no invalida el horario).
- **¿Es mejor penalizar o reparar individuos invalidos?** Penalizar es mas simple
  de implementar y deja que el propio algoritmo aprenda a evitarlas; reparar
  garantiza soluciones siempre validas pero requiere logica adicional y puede
  sesgar la busqueda hacia el criterio de reparacion elegido. En este taller se
  penaliza, lo que permite explorar el espacio completo (incluyendo horarios
  invalidos) antes de converger a uno valido.
- **¿Como cambia el resultado al aumentar el numero de cursos?** El espacio de
  combinaciones (sala, franja) por curso se mantiene, pero la probabilidad de
  choques aumenta al haber mas cursos compitiendo por las mismas franjas, por lo
  que se necesitan mas generaciones (o mayor poblacion/elitismo) para llegar a
  penalizacion cero.
"""
)
