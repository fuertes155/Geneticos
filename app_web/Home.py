import pathlib
import sys

import streamlit as st

ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

st.set_page_config(page_title="Taller 1 - Algoritmos Geneticos", page_icon="🧬", layout="wide")

st.title("🧬 Taller 1 - Inteligencia Artificial")
st.subheader("Algoritmos Evolutivos / Algoritmos Geneticos")

st.markdown(
    """
Esta aplicacion despliega los cuatro problemas del taller resueltos con
**Algoritmos Geneticos**. Usa el menu de la izquierda para navegar entre ellos:

- **N-Reinas**: problema base. Vector de tamano N, minimizar conflictos entre reinas.
- **TSP (Agente Viajero)**: cromosoma de permutacion, cruzamiento OX, minimizar la ruta.
- **Asignacion de cursos a salas**: representacion por penalizaciones y restricciones duras/blandas.
- **Mochila (Knapsack)**: cromosoma binario, comparando penalizacion vs. reparacion.

Cada pagina permite ajustar los parametros del algoritmo genetico (poblacion,
generaciones, tasa de mutacion, etc.) y ejecutar el algoritmo en vivo.
"""
)

st.divider()

with st.expander("Objetivo general del taller"):
    st.write(
        "Implementar, experimentar y analizar algoritmos geneticos como tecnica de "
        "Inteligencia Artificial para resolver problemas. Se compara representacion, "
        "funcion de aptitud, seleccion, cruzamiento, mutacion y criterios de parada "
        "en diferentes problemas."
    )

with st.expander("1. ¿Que es un algoritmo genetico y por que es una tecnica de busqueda/optimizacion de IA?"):
    st.write(
        "Un algoritmo genetico (AG) es una tecnica de busqueda metaheuristica inspirada "
        "en la seleccion natural: mantiene una poblacion de soluciones candidatas que "
        "compite, se combina (cruzamiento) y se altera aleatoriamente (mutacion) a lo "
        "largo de generaciones, favoreciendo a los individuos mas aptos (seleccion). "
        "Es una tecnica de IA de busqueda/optimizacion porque no explora el espacio de "
        "soluciones de forma exhaustiva ni exacta, sino que usa una heuristica guiada "
        "por la funcion de aptitud para converger hacia buenas soluciones en espacios "
        "de busqueda demasiado grandes para explorar por fuerza bruta (N-Reinas, TSP, "
        "horarios, mochila, etc.), sin garantizar el optimo global pero encontrando "
        "soluciones muy buenas en tiempo razonable."
    )

with st.expander("2. Poblacion, individuo, cromosoma, gen, seleccion, cruzamiento, mutacion, elitismo, aptitud"):
    st.markdown(
        """
- **Poblacion**: conjunto de soluciones candidatas (individuos) que existe en una generacion dada.
- **Individuo**: una solucion candidata completa al problema (p.ej. una ruta del TSP).
- **Cromosoma**: la codificacion del individuo (vector, permutacion, cadena binaria).
- **Gen**: cada componente/posicion del cromosoma (p.ej. la fila de la reina en la columna i).
- **Seleccion**: mecanismo que elige que individuos se reproducen, favoreciendo a los mas aptos (torneo, ruleta).
- **Cruzamiento (crossover)**: combina el material genetico de dos padres para crear uno o mas hijos.
- **Mutacion**: altera aleatoriamente uno o mas genes de un individuo para mantener diversidad y explorar nuevas zonas.
- **Elitismo**: conserva sin cambios a los mejores individuos de una generacion hacia la siguiente, evitando perder buenas soluciones.
- **Funcion de aptitud (fitness)**: mide que tan buena es una solucion; guia la seleccion y por tanto toda la busqueda.
"""
    )

with st.expander("3. ¿Por que es fundamental la funcion de aptitud? Maximizacion vs. minimizacion"):
    st.write(
        "La funcion de aptitud es la unica senal que el algoritmo tiene para distinguir "
        "buenas soluciones de malas; si esta mal definida (no discrimina, o premia algo "
        "irrelevante), la seleccion presiona a la poblacion en la direccion equivocada y "
        "el AG no converge a soluciones utiles, sin importar que tan buenos sean los "
        "demas operadores. En problemas de minimizacion (distancia en TSP, penalizacion "
        "en horarios, conflictos en N-Reinas) se suele transformar el costo en una "
        "aptitud a maximizar, por ejemplo aptitud = 1/(costo+epsilon) o aptitud = "
        "-costo/penalizacion, para poder reutilizar los mismos mecanismos de seleccion "
        "(torneo, ruleta) que asumen 'mayor aptitud = mejor individuo'."
    )

with st.expander("4. Operadores para cromosomas de permutacion vs. binarios"):
    st.markdown(
        """
- **Cromosomas de permutacion** (TSP): el cruzamiento clasico de un punto rompe la
  permutacion (puede repetir o perder ciudades), por eso se usan operadores que
  preservan el orden relativo, como **OX (Order Crossover)**, **PMX (Partially
  Mapped Crossover)** o **Cycle Crossover**. Para mutacion se usan operadores que
  no rompen la propiedad de permutacion: **intercambio (swap)**, **inversion** de
  un segmento, o **insercion** de un gen en otra posicion.
- **Cromosomas binarios** (Mochila): al no existir restriccion de unicidad, sirven
  los operadores clasicos: **cruzamiento de un punto, dos puntos o uniforme**, y
  **mutacion de bit-flip** (invertir un bit con cierta probabilidad).
"""
    )

with st.expander("5. Riesgos de una tasa de mutacion muy baja o muy alta"):
    st.write(
        "Una tasa de mutacion demasiado **baja** reduce la diversidad genetica: la "
        "poblacion converge rapido hacia un optimo local y pierde la capacidad de "
        "explorar otras zonas del espacio de busqueda (convergencia prematura). Una "
        "tasa demasiado **alta** convierte la busqueda en casi aleatoria: destruye "
        "buenas soluciones encontradas por el cruzamiento y la seleccion, impidiendo "
        "que el algoritmo explote el progreso ya logrado, por lo que la poblacion deja "
        "de mejorar de forma consistente generacion tras generacion."
    )

st.divider()
st.caption("Selecciona un problema en el menu de la izquierda para experimentar con el algoritmo genetico correspondiente.")
