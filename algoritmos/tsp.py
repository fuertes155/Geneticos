"""
EJERCICIO 1 - PROBLEMA DEL AGENTE VIAJERO (TSP)
Algoritmo Genetico con representacion de permutacion.

Cromosoma: permutacion de indices de ciudades, ej. [0, 3, 1, 5, 2, 4].
Aptitud: 1 / (distancia_total + epsilon) -> se maximiza aptitud = se minimiza distancia.
Cruzamiento: OX (Order Crossover). Mutacion: intercambio (swap) o inversion.

Este archivo esta escrito con bucles simples (sin numpy, sin funciones
lambda) para que sea facil de leer y explicar linea por linea. Ejecutable
completo en Spyder (F5) o por celdas "# %%". Las funciones se reutilizan
desde app_web/pages/2_TSP.py sin correr los experimentos.
"""

import os
import math
import random
import pandas as pd
import matplotlib.pyplot as plt

RESULTADOS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "resultados")
os.makedirs(RESULTADOS_DIR, exist_ok=True)

EPS = 1e-6

# %% Generacion del problema


def generar_ciudades(n_ciudades, semilla=None):
    """Coordenadas 2D aleatorias en un plano de 100x100."""
    rng = random.Random(semilla)
    ciudades = []
    for _ in range(n_ciudades):
        x = rng.uniform(0, 100)
        y = rng.uniform(0, 100)
        ciudades.append((x, y))
    return ciudades


def matriz_distancias(ciudades):
    """Tabla (lista de listas) con la distancia entre cada par de ciudades."""
    n = len(ciudades)
    matriz = []
    for i in range(n):
        fila = []
        for j in range(n):
            if i == j:
                fila.append(0.0)
            else:
                xi, yi = ciudades[i]
                xj, yj = ciudades[j]
                distancia = math.sqrt((xi - xj) ** 2 + (yi - yj) ** 2)
                fila.append(distancia)
        matriz.append(fila)
    return matriz


# %% Representacion y funcion de aptitud


def crear_individuo(n_ciudades):
    individuo = list(range(n_ciudades))
    random.shuffle(individuo)
    return individuo


def crear_poblacion(tam_poblacion, n_ciudades):
    poblacion = []
    for _ in range(tam_poblacion):
        poblacion.append(crear_individuo(n_ciudades))
    return poblacion


def distancia_ruta(individuo, matriz):
    """Distancia total de la ruta, incluyendo el regreso a la ciudad inicial."""
    total = 0.0
    n = len(individuo)
    for i in range(n):
        origen = individuo[i]
        destino = individuo[(i + 1) % n]  # la ultima ciudad regresa a la primera
        total += matriz[origen][destino]
    return total


def aptitud(individuo, matriz):
    return 1.0 / (distancia_ruta(individuo, matriz) + EPS)


# %% Operadores geneticos


def seleccion_ruleta(poblacion, aptitudes):
    """Selecciona un individuo al azar, con probabilidad proporcional a su aptitud."""
    total = sum(aptitudes)
    pivote = random.uniform(0, total)
    acumulado = 0.0
    for i in range(len(poblacion)):
        acumulado += aptitudes[i]
        if acumulado >= pivote:
            return poblacion[i]
    return poblacion[-1]


def cruzamiento_ox(padre1, padre2):
    """Order Crossover: conserva un segmento de un padre y completa con el orden del otro."""
    n = len(padre1)
    i, j = sorted(random.sample(range(n), 2))

    hijo = [None] * n
    for pos in range(i, j + 1):
        hijo[pos] = padre1[pos]
    genes_usados = set(hijo[i:j + 1])

    posiciones_vacias = []
    for pos in range(n):
        if hijo[pos] is None:
            posiciones_vacias.append(pos)

    genes_restantes = []
    for gen in padre2:
        if gen not in genes_usados:
            genes_restantes.append(gen)

    for k in range(len(posiciones_vacias)):
        hijo[posiciones_vacias[k]] = genes_restantes[k]

    return hijo


def mutacion_intercambio(individuo, tasa_mutacion):
    nuevo = individuo[:]
    if random.random() < tasa_mutacion:
        i, j = random.sample(range(len(nuevo)), 2)
        nuevo[i], nuevo[j] = nuevo[j], nuevo[i]
    return nuevo


def mutacion_inversion(individuo, tasa_mutacion):
    nuevo = individuo[:]
    if random.random() < tasa_mutacion:
        i, j = sorted(random.sample(range(len(nuevo)), 2))
        nuevo[i:j + 1] = reversed(nuevo[i:j + 1])
    return nuevo


def obtener_mejores_indices(aptitudes, cantidad):
    """Indices de los 'cantidad' individuos con mayor aptitud (para el elitismo)."""
    restantes = aptitudes[:]
    mejores = []
    for _ in range(cantidad):
        mejor_idx = 0
        for i in range(len(restantes)):
            if restantes[i] > restantes[mejor_idx]:
                mejor_idx = i
        mejores.append(mejor_idx)
        restantes[mejor_idx] = float("-inf")
    return mejores


# %% Ciclo evolutivo


def ejecutar_ga(matriz, tam_poblacion=100, generaciones=300, tasa_mutacion=0.1,
                 tipo_mutacion="swap", elitismo=2, semilla=None):
    if semilla is not None:
        random.seed(semilla)

    n_ciudades = len(matriz)
    if tipo_mutacion == "swap":
        mutar = mutacion_intercambio
    else:
        mutar = mutacion_inversion

    poblacion = crear_poblacion(tam_poblacion, n_ciudades)
    historial_mejor = []
    mejor_individuo = None
    mejor_distancia = float("inf")

    for _ in range(generaciones):
        # 1) Evaluar distancia y aptitud de toda la poblacion
        distancias = []
        aptitudes = []
        for individuo in poblacion:
            d = distancia_ruta(individuo, matriz)
            distancias.append(d)
            aptitudes.append(1.0 / (d + EPS))

        # 2) Buscar la mejor ruta de esta generacion
        idx_mejor_gen = 0
        for i in range(len(distancias)):
            if distancias[i] < distancias[idx_mejor_gen]:
                idx_mejor_gen = i

        if distancias[idx_mejor_gen] < mejor_distancia:
            mejor_distancia = distancias[idx_mejor_gen]
            mejor_individuo = poblacion[idx_mejor_gen][:]
        historial_mejor.append(mejor_distancia)

        # 3) Elitismo: las mejores rutas pasan intactas a la siguiente generacion
        indices_elite = obtener_mejores_indices(aptitudes, elitismo)
        nueva_poblacion = []
        for i in indices_elite:
            nueva_poblacion.append(poblacion[i][:])

        # 4) El resto se completa con seleccion + cruce OX + mutacion
        while len(nueva_poblacion) < tam_poblacion:
            padre1 = seleccion_ruleta(poblacion, aptitudes)
            padre2 = seleccion_ruleta(poblacion, aptitudes)
            hijo = cruzamiento_ox(padre1, padre2)
            hijo = mutar(hijo, tasa_mutacion)
            nueva_poblacion.append(hijo)

        poblacion = nueva_poblacion

    return {
        "mejor_individuo": mejor_individuo,
        "mejor_distancia": mejor_distancia,
        "historial": historial_mejor,
    }


# %% Funcion simple para promedio (en vez de usar numpy)


def promedio(lista):
    return sum(lista) / len(lista)


# %% Experimentacion (solo corre si se ejecuta este script directamente)

if __name__ == "__main__":
    N_CIUDADES = 15
    TAM_POBLACION = 80
    GENERACIONES = 150
    ciudades = generar_ciudades(N_CIUDADES, semilla=1)
    matriz = matriz_distancias(ciudades)

    print("=== Comparacion de tasas de mutacion (swap, 10 corridas) ===")
    filas = []
    for tasa in [0.05, 0.2]:
        distancias_finales = []
        for rep in range(10):
            resultado = ejecutar_ga(matriz, tam_poblacion=TAM_POBLACION, generaciones=GENERACIONES,
                                     tasa_mutacion=tasa, tipo_mutacion="swap", semilla=rep)
            distancias_finales.append(resultado["mejor_distancia"])
        filas.append({
            "Tasa mutacion": tasa,
            "Mejor": min(distancias_finales),
            "Peor": max(distancias_finales),
            "Promedio": promedio(distancias_finales),
        })
    tabla_mutacion = pd.DataFrame(filas)
    print(tabla_mutacion.to_string(index=False))

    print("\n=== Comparacion de estrategia de mutacion (tasa=0.1, 10 corridas) ===")
    filas_estrategia = []
    historiales = {}
    for tipo in ["swap", "inversion"]:
        distancias_finales = []
        for rep in range(10):
            resultado = ejecutar_ga(matriz, tam_poblacion=TAM_POBLACION, generaciones=GENERACIONES,
                                     tasa_mutacion=0.1, tipo_mutacion=tipo, semilla=rep)
            distancias_finales.append(resultado["mejor_distancia"])
            if rep == 0:
                historiales[tipo] = resultado["historial"]
        filas_estrategia.append({
            "Mutacion": tipo,
            "Mejor": min(distancias_finales),
            "Peor": max(distancias_finales),
            "Promedio": promedio(distancias_finales),
        })
    tabla_estrategia = pd.DataFrame(filas_estrategia)
    print(tabla_estrategia.to_string(index=False))

    tabla_mutacion.to_csv(os.path.join(RESULTADOS_DIR, "tsp_tasas_mutacion.csv"), index=False)
    tabla_estrategia.to_csv(os.path.join(RESULTADOS_DIR, "tsp_estrategias_mutacion.csv"), index=False)

    plt.figure(figsize=(9, 5))
    for tipo, historial in historiales.items():
        plt.plot(historial, label=f"mutacion={tipo}")
    plt.xlabel("Generacion")
    plt.ylabel("Mejor distancia")
    plt.title(f"Convergencia TSP ({N_CIUDADES} ciudades)")
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(RESULTADOS_DIR, "tsp_convergencia.png"), dpi=150)
    plt.show()

    mejor_general = ejecutar_ga(matriz, tam_poblacion=TAM_POBLACION, generaciones=GENERACIONES,
                                 tasa_mutacion=0.1, tipo_mutacion="swap", semilla=0)
    ruta = mejor_general["mejor_individuo"] + [mejor_general["mejor_individuo"][0]]
    xs = []
    ys = []
    for i in ruta:
        xs.append(ciudades[i][0])
        ys.append(ciudades[i][1])
    plt.figure(figsize=(6, 6))
    plt.plot(xs, ys, "o-")
    for idx, (x, y) in enumerate(ciudades):
        plt.annotate(str(idx), (x, y))
    plt.title(f"Mejor ruta encontrada (distancia={mejor_general['mejor_distancia']:.2f})")
    plt.tight_layout()
    plt.savefig(os.path.join(RESULTADOS_DIR, "tsp_mejor_ruta.png"), dpi=150)
    plt.show()
