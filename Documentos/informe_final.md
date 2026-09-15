# Informe Final — Taller 1: Algoritmos Genéticos

## 1. Objetivo

Implementar, experimentar y analizar algoritmos genéticos (AG) como técnica de
Inteligencia Artificial para resolver cuatro problemas de búsqueda/optimización:
N-Reinas (problema base), el Agente Viajero (TSP), la asignación de cursos a salas
de cómputo, y el problema de la Mochila. Para cada uno se comparó representación,
función de aptitud, selección, cruzamiento, mutación y criterios de parada.

Las respuestas a las preguntas conceptuales del taller están en
[`conceptos_clave.md`](conceptos_clave.md). El código fuente completo está en la
carpeta [`algoritmos/`](algoritmos/) y la aplicación web de despliegue en
[`app_web/`](app_web/) (ver [`README.md`](README.md) para instrucciones de
ejecución en Anaconda/Spyder y en Streamlit).

## 2. Metodología general

Los cuatro problemas comparten el mismo ciclo evolutivo: se crea una población
inicial aleatoria, se evalúa con una función de aptitud específica del problema, se
seleccionan padres (torneo o ruleta según el caso), se generan hijos por
cruzamiento y mutación, se aplica elitismo, y se repite hasta cumplir un criterio de
parada (número de generaciones o aptitud óptima alcanzada).

| Problema | Representación | Aptitud | Selección | Cruzamiento | Mutación |
|---|---|---|---|---|---|
| N-Reinas | Vector de tamaño N (fila por columna) | Pares no atacantes (maximizar) | Torneo (k=3) | Un punto | Reinicio aleatorio por gen |
| TSP | Permutación de ciudades | 1/(distancia+ε) | Ruleta | OX (Order Crossover) | Swap o inversión |
| Asignación de cursos | Vector de códigos (sala, franja) por curso | −penalización (maximizar) | Torneo (k=3) | Uniforme | Reasignación aleatoria por gen |
| Mochila | Cadena binaria (objeto incluido/no) | Valor total, con penalización o reparación | Torneo (k=3) | Un punto | Bit-flip |

Todos los scripts (`algoritmos/*.py`) exponen funciones reutilizables y, al
ejecutarse directamente (`if __name__ == "__main__":`), corren la experimentación
descrita en el taller, guardando tablas (`.csv`) y gráficas (`.png`) en la carpeta
`resultados/`.

## 3. Resultados — N-Reinas

Se probó N=6 y N=8, poblaciones de 50 y 100, y tasas de mutación 0.05, 0.1 y 0.2
(5 corridas por combinación, máximo 500 generaciones):

| N | Población | Tasa mutación | % resuelto | Generaciones promedio | Gen. mínimo | Gen. máximo |
|---|---|---|---|---|---|---|
| 6 | 50  | 0.05 | 40%  | 327.6 | 7   | 500 |
| 6 | 50  | 0.10 | 40%  | 319.8 | 12  | 500 |
| 6 | 50  | 0.20 | 100% | 133.4 | 17  | 300 |
| 6 | 100 | 0.05 | 60%  | 266.6 | 7   | 500 |
| 6 | 100 | 0.10 | 80%  | 212.6 | 4   | 500 |
| 6 | 100 | 0.20 | 100% | 9.6   | 5   | 14  |
| 8 | 50  | 0.05 | 20%  | 408.0 | 40  | 500 |
| 8 | 50  | 0.10 | 60%  | 366.6 | 216 | 500 |
| 8 | 50  | 0.20 | 100% | 66.6  | 26  | 129 |
| 8 | 100 | 0.05 | 100% | 12.2  | 4   | 25  |
| 8 | 100 | 0.10 | 80%  | 232.0 | 9   | 500 |
| 8 | 100 | 0.20 | 80%  | 134.8 | 12  | 500 |

**Análisis:** con población pequeña (50), una tasa de mutación alta (0.2) es
claramente superior: resuelve el 100% de las corridas y en muchas menos
generaciones, porque compensa la poca diversidad inicial de la población.
Con población grande (100) el resultado depende más de la semilla — en este caso
la combinación N=8/población=100/mutación=0.05 llegó al 100% con muy pocas
generaciones (12.2 en promedio), lo que confirma que **no hay una tasa de mutación
universalmente óptima**: interactúa con el tamaño de población y debe ajustarse
experimentalmente. La gráfica de convergencia está en
`resultados/n_reinas_convergencia.png`.

## 4. Resultados — TSP (Ejercicio 1)

Instancia de 15 ciudades (coordenadas aleatorias), población de 80, 150
generaciones, 10 corridas por configuración.

**Comparación de tasas de mutación (mutación por swap):**

| Tasa mutación | Mejor  | Peor   | Promedio |
|---|---|---|---|
| 0.05 | 382.76 | 432.11 | 407.23 |
| 0.20 | 398.05 | 473.59 | 417.39 |

**Comparación de estrategia de mutación (tasa=0.1):**

| Mutación  | Mejor  | Peor   | Promedio |
|---|---|---|---|
| swap      | 382.76 | 413.77 | 397.72 |
| inversion | 382.76 | 432.17 | 398.53 |

**Análisis:** la tasa de mutación baja (0.05) obtuvo mejor promedio y menor
dispersión que la alta (0.2): con 150 generaciones, una mutación excesiva destruye
rutas buenas antes de que la selección/cruzamiento las consolide. Entre
estrategias, **swap** fue ligeramente mejor y más consistente que **inversión**
(menor peor caso). La mejor ruta encontrada y su gráfica de convergencia están en
`resultados/tsp_mejor_ruta.png` y `resultados/tsp_convergencia.png`.

**Respuestas a las preguntas del ejercicio** están desarrolladas en la página TSP
de la aplicación web y resumidas aquí:
- Un cruzamiento binario simple no controla duplicados porque el cromosoma es una
  permutación (cada ciudad debe aparecer una sola vez); por eso se requieren
  operadores como OX o PMX.
- Al aumentar el número de ciudades, el espacio de búsqueda crece factorialmente,
  por lo que se necesita más población y/o generaciones para mantener la calidad
  de la solución.
- La estrategia de mutación por **swap** con tasa moderada-baja encontró las
  mejores rutas en estas pruebas.

## 5. Resultados — Asignación de cursos a salas (Ejercicio 2)

8 cursos, 4 salas, 5 franjas horarias, con restricciones duras (sobrecupo, recursos
faltantes, choques de sala/franja, franjas bloqueadas) y una restricción blanda
(equilibrio de carga entre salas). Con parámetros holgados (población 100, 300
generaciones) el algoritmo siempre llega a una solución con penalización ≈0 (solo
el término de balance), por lo que para visibilizar el efecto del elitismo se usó
una configuración más exigente: población 20, 15 generaciones, mutación 0.2, 15
corridas.

| Configuración | Mejor | Peor  | Promedio |
|---|---|---|---|
| Con elitismo (2) | 0.25 | 40.25 | 10.75 |
| Sin elitismo     | 0.75 | 40.25 | 16.30 |

**Análisis:** con recursos computacionales limitados (pocas generaciones/población),
el elitismo mejora el promedio en un 34% (10.75 vs. 16.30), porque evita perder las
mejores soluciones encontradas de una generación a otra. Con más generaciones,
ambas variantes convergen igual, ya que el problema (8 cursos en 20 combinaciones
posibles de sala/franja) es lo bastante pequeño para resolverse sin dificultad.
La gráfica de convergencia está en `resultados/cursos_convergencia.png`.

Restricciones duras vs. blandas, y la disyuntiva penalización/reparación, se
discuten en `conceptos_clave.md` y en la página correspondiente de la app web.

## 6. Resultados — Mochila (Ejercicio 3)

15 objetos con peso y valor distintos, dos capacidades (15 y 25), comparando
penalización frente a reparación, 10 corridas por configuración:

| Capacidad | Modo | Valor promedio | Valor mejor | Peso promedio | Generación promedio del mejor |
|---|---|---|---|---|---|
| 15 | penalización | 227.0 | 227 | 15.0 | 8.1 |
| 15 | reparación   | 227.0 | 227 | 15.0 | 1.5 |
| 25 | penalización | 325.0 | 325 | 25.0 | 8.7 |
| 25 | reparación   | 325.0 | 325 | 25.0 | 3.2 |

**Análisis:** ambas estrategias encuentran el mismo valor óptimo de forma
consistente en las 10 corridas (el problema es pequeño: 2^15 combinaciones), pero
la **reparación converge notablemente más rápido** (generación promedio 1.5–3.2
frente a 8.1–8.7 con penalización), porque todos los individuos son siempre
factibles y el algoritmo no "desperdicia" evaluaciones en soluciones inválidas. La
penalización, en cambio, permite explorar temporalmente el espacio de soluciones
inválidas antes de converger. El cromosoma binario es adecuado porque cada objeto
tiene exactamente dos estados independientes (incluido/no incluido), sin
restricciones de orden ni unicidad entre genes.

## 7. Conclusión comparativa

Los cuatro problemas muestran que un mismo esquema evolutivo (población → selección
→ cruzamiento → mutación → elitismo) se adapta a problemas muy distintos con solo
cambiar la **representación** y la **función de aptitud**:

- La **representación** debe ajustarse a las restricciones estructurales del
  problema: vectores libres para N-Reinas, permutaciones para el TSP (que exigen
  operadores especializados como OX), vectores categóricos para la asignación de
  cursos, y cadenas binarias para la mochila.
- La **función de aptitud** es el componente más determinante: cuando el problema
  es de minimización o tiene restricciones, transformarla correctamente
  (1/costo, −penalización) es indispensable para que la selección funcione.
- El **elitismo** ayuda especialmente cuando los recursos computacionales
  (población/generaciones) son limitados; con suficiente presupuesto, su efecto se
  diluye.
- La **tasa y el tipo de mutación** no tienen un valor óptimo universal: dependen
  del tamaño de población, del número de generaciones y de la dificultad de la
  instancia — deben calibrarse experimentalmente para cada problema.
- Comparado con reparar individuos inválidos, **penalizar** es más simple de
  implementar pero converge más lento; **reparar** exige más lógica específica del
  dominio pero acelera la convergencia al garantizar siempre soluciones factibles.

En conjunto, los algoritmos genéticos demuestran ser una técnica de IA flexible y
efectiva para problemas de búsqueda y optimización combinatoria donde los métodos
exactos son computacionalmente inviables, a costa de no garantizar el óptimo global
y de requerir ajuste experimental de sus parámetros.
