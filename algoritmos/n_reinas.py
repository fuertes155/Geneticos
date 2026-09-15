"""
PROBLEMA BASE - N-REINAS
Algoritmo Genetico para el problema de las N-Reinas.

Representacion: vector de tamano N. El indice representa la columna y el
valor (0..N-1) representa la fila donde se ubica la reina de esa columna.
Como cada columna tiene exactamente una reina, nunca hay conflictos de
columna; solo se cuentan conflictos de fila y de diagonal.

Este archivo esta escrito con bucles simples (sin numpy, sin funciones
lambda) para que sea facil de leer y explicar linea por linea. Puede
ejecutarse completo en Spyder (F5) o por celdas (Ctrl+Enter en cada bloque
separado por "# %%"). Las funciones tambien se importan desde la app web
(app_web/pages/1_N_Reinas.py) sin ejecutar los experimentos.
"""

import os
import random
import pandas as pd
import matplotlib.pyplot as plt

RESULTADOS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "resultados")
os.makedirs(RESULTADOS_DIR, exist_ok=True)

# %% Representacion y funcion de aptitud


def crear_individuo(n):
    """Vector de tamano n: para cada columna, sortea una fila al azar (0..n-1)."""
    individuo = []
    for columna in range(n):
        fila = random.randrange(n)
        individuo.append(fila)
    return individuo


def crear_poblacion(tam_poblacion, n):
    poblacion = []
    for _ in range(tam_poblacion):
        poblacion.append(crear_individuo(n))
    return poblacion


def contar_conflictos(individuo):
    """Numero de pares de reinas que se atacan (misma fila o misma diagonal)."""
    n = len(individuo)
    conflictos = 0
    for i in range(n):
        for j in range(i + 1, n):
            misma_fila = individuo[i] == individuo[j]
            misma_diagonal = abs(individuo[i] - individuo[j]) == abs(i - j)
            if misma_fila or misma_diagonal:
                conflictos += 1
    return conflictos


def aptitud(individuo):
    """Aptitud a maximizar: pares no atacantes = max posible - conflictos."""
    n = len(individuo)
    max_pares = n * (n - 1) // 2
    return max_pares - contar_conflictos(individuo)


# %% Operadores geneticos


def seleccion_torneo(poblacion, aptitudes, k=3):
    """Elige k individuos al azar y devuelve el de mayor aptitud entre ellos."""
    participantes = random.sample(range(len(poblacion)), k)
    mejor_idx = participantes[0]
    for idx in participantes:
        if aptitudes[idx] > aptitudes[mejor_idx]:
            mejor_idx = idx
    return poblacion[mejor_idx]


def cruzamiento_un_punto(padre1, padre2, prob_cruce=0.8):
    if random.random() > prob_cruce:
        return padre1[:], padre2[:]
    n = len(padre1)
    punto = random.randint(1, n - 1)
    hijo1 = padre1[:punto] + padre2[punto:]
    hijo2 = padre2[:punto] + padre1[punto:]
    return hijo1, hijo2


def mutacion(individuo, n, tasa_mutacion):
    """Reinicio aleatorio: cada gen cambia de fila con probabilidad tasa_mutacion."""
    nuevo = individuo[:]
    for i in range(len(nuevo)):
        if random.random() < tasa_mutacion:
            nuevo[i] = random.randrange(n)
    return nuevo


def obtener_mejores_indices(aptitudes, cantidad):
    """Indices de los 'cantidad' individuos con mayor aptitud (para el elitismo).

    Es una busqueda simple: encuentra el mejor, lo aparta, encuentra el
    siguiente mejor, y asi hasta juntar la cantidad pedida.
    """
    restantes = aptitudes[:]
    mejores = []
    for _ in range(cantidad):
        mejor_idx = 0
        for i in range(len(restantes)):
            if restantes[i] > restantes[mejor_idx]:
                mejor_idx = i
        mejores.append(mejor_idx)
        restantes[mejor_idx] = float("-inf")  # para no volver a elegirlo
    return mejores


# %% Ciclo evolutivo


def ejecutar_ga(n, tam_poblacion=100, generaciones=500, tasa_mutacion=0.1,
                 prob_cruce=0.8, elitismo=2, semilla=None):
    """Corre el AG para N-Reinas y devuelve el historial y la mejor solucion."""
    if semilla is not None:
        random.seed(semilla)

    max_pares = n * (n - 1) // 2
    poblacion = crear_poblacion(tam_poblacion, n)
    historial_mejor = []
    mejor_individuo = None
    mejor_aptitud = -1

    for generacion in range(1, generaciones + 1):
        # 1) Evaluar la aptitud de toda la poblacion
        aptitudes = []
        for individuo in poblacion:
            aptitudes.append(aptitud(individuo))

        # 2) Buscar el mejor individuo de esta generacion
        idx_mejor_gen = 0
        for i in range(len(aptitudes)):
            if aptitudes[i] > aptitudes[idx_mejor_gen]:
                idx_mejor_gen = i

        if aptitudes[idx_mejor_gen] > mejor_aptitud:
            mejor_aptitud = aptitudes[idx_mejor_gen]
            mejor_individuo = poblacion[idx_mejor_gen][:]
        historial_mejor.append(mejor_aptitud)

        # 3) Si ya no hay conflictos, terminar antes de tiempo
        if mejor_aptitud == max_pares:
            return {
                "mejor_individuo": mejor_individuo,
                "mejor_aptitud": mejor_aptitud,
                "conflictos": max_pares - mejor_aptitud,
                "generaciones_usadas": generacion,
                "resuelto": True,
                "historial": historial_mejor,
            }

        # 4) Elitismo: los mejores pasan intactos a la siguiente generacion
        indices_elite = obtener_mejores_indices(aptitudes, elitismo)
        nueva_poblacion = []
        for i in indices_elite:
            nueva_poblacion.append(poblacion[i][:])

        # 5) El resto de la poblacion se completa con seleccion + cruce + mutacion
        while len(nueva_poblacion) < tam_poblacion:
            padre1 = seleccion_torneo(poblacion, aptitudes)
            padre2 = seleccion_torneo(poblacion, aptitudes)
            hijo1, hijo2 = cruzamiento_un_punto(padre1, padre2, prob_cruce)
            hijo1 = mutacion(hijo1, n, tasa_mutacion)
            hijo2 = mutacion(hijo2, n, tasa_mutacion)
            nueva_poblacion.append(hijo1)
            if len(nueva_poblacion) < tam_poblacion:
                nueva_poblacion.append(hijo2)

        poblacion = nueva_poblacion

    return {
        "mejor_individuo": mejor_individuo,
        "mejor_aptitud": mejor_aptitud,
        "conflictos": max_pares - mejor_aptitud,
        "generaciones_usadas": generaciones,
        "resuelto": mejor_aptitud == max_pares,
        "historial": historial_mejor,
    }


def tablero_a_texto(individuo):
    n = len(individuo)
    filas = []
    for fila in range(n):
        linea = ""
        for columna in range(n):
            if individuo[columna] == fila:
                linea += "Q "
            else:
                linea += ". "
        filas.append(linea)
    return "\n".join(filas)


# %% Funciones simples para promedio/minimo/maximo (en vez de usar numpy)


def promedio(lista):
    return sum(lista) / len(lista)


# %% Experimentacion (solo corre si se ejecuta este script directamente)

if __name__ == "__main__":
    valores_n = [6, 8]
    tamanos_poblacion = [50, 100]
    tasas_mutacion = [0.05, 0.1, 0.2]
    repeticiones = 5
    generaciones_max = 500

    filas_resultado = []
    historiales_ejemplo = {}

    for n in valores_n:
        for tam_pob in tamanos_poblacion:
            for tasa in tasas_mutacion:
                generaciones_lista = []
                resueltos = 0
                mejor_historial = None
                for rep in range(repeticiones):
                    resultado = ejecutar_ga(
                        n=n, tam_poblacion=tam_pob, generaciones=generaciones_max,
                        tasa_mutacion=tasa, semilla=rep,
                    )
                    generaciones_lista.append(resultado["generaciones_usadas"])
                    resueltos += int(resultado["resuelto"])
                    if rep == 0:
                        mejor_historial = resultado["historial"]

                historiales_ejemplo[(n, tam_pob, tasa)] = mejor_historial
                filas_resultado.append({
                    "N": n,
                    "Poblacion": tam_pob,
                    "Tasa mutacion": tasa,
                    "% resuelto": 100 * resueltos / repeticiones,
                    "Generaciones promedio": promedio(generaciones_lista),
                    "Generaciones min": min(generaciones_lista),
                    "Generaciones max": max(generaciones_lista),
                })

    tabla = pd.DataFrame(filas_resultado)
    print("\n=== RESULTADOS N-REINAS (promedio de %d corridas) ===" % repeticiones)
    print(tabla.to_string(index=False))
    tabla.to_csv(os.path.join(RESULTADOS_DIR, "n_reinas_resultados.csv"), index=False)

    plt.figure(figsize=(9, 5))
    for (n, tam_pob, tasa), historial in historiales_ejemplo.items():
        if tam_pob == 100:
            plt.plot(historial, label=f"N={n}, mut={tasa}")
    plt.xlabel("Generacion")
    plt.ylabel("Mejor aptitud (pares no atacantes)")
    plt.title("Convergencia N-Reinas (poblacion=100)")
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(RESULTADOS_DIR, "n_reinas_convergencia.png"), dpi=150)
    plt.show()

    print("\nEjemplo de tablero resuelto (N=8):")
    ejemplo = ejecutar_ga(n=8, tam_poblacion=100, tasa_mutacion=0.1, semilla=42)
    print("Resuelto:", ejemplo["resuelto"], "| Generaciones:", ejemplo["generaciones_usadas"])
    print(tablero_a_texto(ejemplo["mejor_individuo"]))
