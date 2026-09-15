# Conceptos clave — Algoritmos Genéticos

## 1. ¿Qué es un algoritmo genético y por qué es una técnica de búsqueda/optimización de IA?

Un **algoritmo genético (AG)** es una técnica metaheurística de búsqueda y optimización
inspirada en la selección natural y la genética. Mantiene una **población** de
soluciones candidatas que evoluciona a lo largo de generaciones: los individuos más
aptos tienen mayor probabilidad de ser **seleccionados** para reproducirse, sus
cromosomas se combinan mediante **cruzamiento** y se alteran aleatoriamente mediante
**mutación**, generando nuevas soluciones que reemplazan (total o parcialmente) a la
población anterior.

Se considera una técnica de búsqueda/optimización dentro de la Inteligencia Artificial
porque no explora el espacio de soluciones de forma exhaustiva ni analítica (como lo
haría un método exacto), sino que usa una heurística guiada por la **función de
aptitud** para converger hacia soluciones de alta calidad en espacios de búsqueda
demasiado grandes para la fuerza bruta (por ejemplo, N! rutas posibles en el TSP, o
2^N combinaciones en la mochila). No garantiza el óptimo global, pero balancea
**exploración** (mutación, diversidad) y **explotación** (selección, elitismo) para
encontrar soluciones muy buenas en tiempos razonables.

## 2. Población, individuo, cromosoma, gen, selección, cruzamiento, mutación, elitismo y función de aptitud

| Concepto | Definición | Ejemplo en este taller |
|---|---|---|
| **Población** | Conjunto de soluciones candidatas que existen en una generación dada. | 100 vectores candidatos para N-Reinas. |
| **Individuo** | Una solución candidata completa al problema. | Una ruta completa del TSP. |
| **Cromosoma** | La codificación (representación) del individuo. | Vector de tamaño N, permutación, cadena binaria. |
| **Gen** | Cada componente/posición del cromosoma. | La fila asignada a la reina de la columna *i*. |
| **Selección** | Mecanismo que elige qué individuos se reproducen, favoreciendo a los más aptos. | Selección por torneo (N-Reinas, cursos, mochila) o ruleta (TSP). |
| **Cruzamiento** | Combina el material genético de dos padres para crear uno o más hijos. | OX en TSP, un punto en N-Reinas/mochila, uniforme en cursos. |
| **Mutación** | Altera aleatoriamente uno o más genes para mantener diversidad y explorar. | Reinicio aleatorio, swap, inversión, bit-flip. |
| **Elitismo** | Conserva sin cambios a los mejores individuos de una generación a la siguiente. | Se copian los 2 mejores individuos directamente. |
| **Función de aptitud** | Mide qué tan buena es una solución; guía toda la búsqueda. | Pares no atacantes, 1/distancia, -penalización, valor de la mochila. |

## 3. ¿Por qué es fundamental una función de aptitud adecuada? Maximización vs. minimización

La función de aptitud es la **única señal** que el algoritmo genético tiene para
distinguir buenas soluciones de malas. Si está mal definida (no discrimina lo
suficiente entre individuos, o premia algo irrelevante al objetivo real), la presión
de selección empuja a la población en la dirección equivocada y el AG no converge a
soluciones útiles, sin importar qué tan bien diseñados estén los demás operadores.

Muchos problemas reales son de **minimización** (distancia en el TSP, penalización en
horarios, conflictos en N-Reinas), mientras que los operadores clásicos de selección
(torneo, ruleta) suponen "mayor aptitud = mejor individuo". Por eso se transforma el
costo en una aptitud a **maximizar**, típicamente con:

- `aptitud = 1 / (costo + ε)` (usado en el TSP), o
- `aptitud = -penalización` (usado en horarios y, en la mochila, en su variante de
  penalización), o
- directamente una cantidad a maximizar cuando el problema ya es de **maximización**
  (por ejemplo, pares no atacantes en N-Reinas, o valor total en la mochila).

## 4. Operadores de cruzamiento y mutación para cromosomas de permutación vs. binarios

**Cromosomas de permutación** (TSP: cada ciudad aparece exactamente una vez):
- *Cruzamiento*: un cruzamiento de un punto clásico rompe la permutación (genera
  ciudades repetidas y otras ausentes). Se necesitan operadores que preserven el
  orden relativo y la unicidad: **OX (Order Crossover)**, **PMX (Partially Mapped
  Crossover)** o **Cycle Crossover**.
- *Mutación*: operadores que no rompen la propiedad de permutación: **intercambio
  (swap)** de dos posiciones, **inversión** de un segmento, o **inserción** de un gen
  en otra posición.

**Cromosomas binarios** (Mochila: cada gen es independiente, 0 o 1):
- *Cruzamiento*: al no existir restricción de unicidad entre genes, sirven los
  operadores clásicos: cruzamiento de **un punto**, **dos puntos** o **uniforme**.
- *Mutación*: **bit-flip** — invertir cada bit con una probabilidad dada.

## 5. Riesgos de una tasa de mutación demasiado baja o demasiado alta

- **Tasa muy baja**: la diversidad genética se pierde rápido; la población converge
  hacia un óptimo local y el algoritmo deja de explorar otras zonas del espacio de
  búsqueda (**convergencia prematura**). En los experimentos de TSP de este taller
  (15 ciudades), una tasa de 0.02 obtuvo peores resultados promedio que 0.1 porque el
  algoritmo no lograba escapar de rutas subóptimas encontradas temprano.
- **Tasa muy alta**: la búsqueda se vuelve casi aleatoria; la mutación destruye buenas
  soluciones que el cruzamiento y la selección ya habían construido, impidiendo que el
  algoritmo explote el progreso logrado. En el mismo experimento de TSP, una tasa de
  0.2 dio el peor promedio y la mayor dispersión entre corridas.

La tasa óptima depende del problema y debe ajustarse experimentalmente (ver
`informe_final.md`, sección de resultados del TSP).
