"""
EJERCICIO 3 - PROBLEMA DE LA MOCHILA (KNAPSACK)
Algoritmo Genetico con representacion binaria.

Cromosoma binario de longitud = numero de objetos. gen=1 si el objeto se
selecciona, gen=0 si no. Se compara la estrategia de PENALIZACION (permite
individuos que exceden el peso pero castiga su aptitud) contra la de
REPARACION (arregla el cromosoma quitando objetos hasta cumplir la capacidad).

Este archivo esta escrito con bucles simples (sin numpy, sin funciones
lambda) para que sea facil de leer y explicar linea por linea. Ejecutable
completo en Spyder (F5) o por celdas "# %%". Las funciones se reutilizan
desde app_web/pages/4_Mochila.py sin correr los experimentos.
"""

import os
import random
import pandas as pd
import matplotlib.pyplot as plt

RESULTADOS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "resultados")
os.makedirs(RESULTADOS_DIR, exist_ok=True)

OBJETOS = pd.DataFrame([
    {"objeto": "Laptop",        "peso": 8,  "valor": 90},
    {"objeto": "Camara",        "peso": 3,  "valor": 45},
    {"objeto": "Libro",         "peso": 2,  "valor": 10},
    {"objeto": "Botella agua",  "peso": 1,  "valor": 5},
    {"objeto": "Tienda campana","peso": 10, "valor": 60},
    {"objeto": "Saco de dormir","peso": 6,  "valor": 40},
    {"objeto": "Botiquin",      "peso": 2,  "valor": 30},
    {"objeto": "Linterna",      "peso": 1,  "valor": 15},
    {"objeto": "Radio",         "peso": 4,  "valor": 20},
    {"objeto": "Comida",        "peso": 5,  "valor": 50},
    {"objeto": "Ropa",          "peso": 4,  "valor": 25},
    {"objeto": "Herramientas",  "peso": 7,  "valor": 35},
    {"objeto": "Cuerda",        "peso": 3,  "valor": 18},
    {"objeto": "GPS",           "peso": 2,  "valor": 55},
    {"objeto": "Bateria externa","peso": 1, "valor": 22},
])

N_OBJETOS = len(OBJETOS)
PESOS = OBJETOS["peso"].tolist()
VALORES = OBJETOS["valor"].tolist()
FACTOR_PENALIZACION = 10

# %% Representacion y funcion de aptitud


def crear_individuo():
    individuo = []
    for _ in range(N_OBJETOS):
        individuo.append(random.randint(0, 1))
    return individuo


def crear_poblacion(tam_poblacion):
    poblacion = []
    for _ in range(tam_poblacion):
        poblacion.append(crear_individuo())
    return poblacion


def peso_valor(individuo):
    """Suma el peso y el valor de los objetos marcados con un 1."""
    peso_total = 0
    valor_total = 0
    for i in range(N_OBJETOS):
        if individuo[i] == 1:
            peso_total += PESOS[i]
            valor_total += VALORES[i]
    return peso_total, valor_total


def reparar(individuo, capacidad):
    """Quita objetos con peor razon valor/peso hasta cumplir la capacidad."""
    nuevo = individuo[:]
    peso_total, _ = peso_valor(nuevo)
    if peso_total <= capacidad:
        return nuevo

    # Lista de (razon valor/peso, indice) solo de los objetos seleccionados
    seleccionados = []
    for i in range(N_OBJETOS):
        if nuevo[i] == 1:
            razon = VALORES[i] / PESOS[i]
            seleccionados.append((razon, i))
    seleccionados.sort()  # de menor a mayor razon: los peores objetos primero

    idx = 0
    while peso_total > capacidad and idx < len(seleccionados):
        _, item = seleccionados[idx]
        nuevo[item] = 0
        peso_total -= PESOS[item]
        idx += 1
    return nuevo


def aptitud(individuo, capacidad, modo="penalizacion"):
    peso_total, valor_total = peso_valor(individuo)
    if modo == "reparacion":
        return valor_total
    exceso = max(0, peso_total - capacidad)
    return valor_total - FACTOR_PENALIZACION * exceso


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
    punto = random.randint(1, N_OBJETOS - 1)
    hijo1 = padre1[:punto] + padre2[punto:]
    hijo2 = padre2[:punto] + padre1[punto:]
    return hijo1, hijo2


def mutacion(individuo, tasa_mutacion):
    """Bit-flip: cada gen (0 o 1) se invierte con probabilidad tasa_mutacion."""
    nuevo = individuo[:]
    for i in range(len(nuevo)):
        if random.random() < tasa_mutacion:
            nuevo[i] = 1 - nuevo[i]
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


def ejecutar_ga(capacidad, tam_poblacion=100, generaciones=200, tasa_mutacion=0.05,
                 prob_cruce=0.8, elitismo=2, modo="penalizacion", semilla=None):
    if semilla is not None:
        random.seed(semilla)

    poblacion = crear_poblacion(tam_poblacion)
    poblacion[0] = [0] * N_OBJETOS  # mochila vacia: siempre factible, garantiza que exista un mejor_individuo
    if modo == "reparacion":
        for i in range(len(poblacion)):
            poblacion[i] = reparar(poblacion[i], capacidad)

    historial_mejor_valor = []
    mejor_individuo = None
    mejor_valor = -1
    mejor_peso = None
    mejor_generacion = None

    for generacion in range(1, generaciones + 1):
        aptitudes = []
        for individuo in poblacion:
            aptitudes.append(aptitud(individuo, capacidad, modo))

        # Se guarda la mejor solucion FACTIBLE vista hasta ahora (aunque el
        # modo penalizacion permita explorar temporalmente mochilas invalidas)
        for individuo in poblacion:
            peso_total, valor_total = peso_valor(individuo)
            if peso_total <= capacidad and valor_total > mejor_valor:
                mejor_valor = valor_total
                mejor_peso = peso_total
                mejor_individuo = individuo[:]
                mejor_generacion = generacion

        historial_mejor_valor.append(mejor_valor if mejor_valor >= 0 else 0)

        # Elitismo
        indices_elite = obtener_mejores_indices(aptitudes, elitismo)
        nueva_poblacion = []
        for i in indices_elite:
            nueva_poblacion.append(poblacion[i][:])

        # El resto se completa con seleccion + cruce + mutacion (y reparacion, si aplica)
        while len(nueva_poblacion) < tam_poblacion:
            padre1 = seleccion_torneo(poblacion, aptitudes)
            padre2 = seleccion_torneo(poblacion, aptitudes)
            hijo1, hijo2 = cruzamiento_un_punto(padre1, padre2, prob_cruce)
            hijo1 = mutacion(hijo1, tasa_mutacion)
            hijo2 = mutacion(hijo2, tasa_mutacion)
            if modo == "reparacion":
                hijo1 = reparar(hijo1, capacidad)
                hijo2 = reparar(hijo2, capacidad)
            nueva_poblacion.append(hijo1)
            if len(nueva_poblacion) < tam_poblacion:
                nueva_poblacion.append(hijo2)

        poblacion = nueva_poblacion

    return {
        "mejor_individuo": mejor_individuo,
        "mejor_valor": mejor_valor,
        "mejor_peso": mejor_peso,
        "mejor_generacion": mejor_generacion,
        "historial": historial_mejor_valor,
    }


def seleccion_a_tabla(individuo):
    """Devuelve la tabla (con nombre, peso y valor) de los objetos seleccionados."""
    seleccionados = []
    for i in range(len(individuo)):
        if individuo[i] == 1:
            seleccionados.append(i)
    return OBJETOS.iloc[seleccionados].reset_index(drop=True)


# %% Funcion simple para promedio (en vez de usar numpy)


def promedio(lista):
    return sum(lista) / len(lista)


# %% Experimentacion (solo corre si se ejecuta este script directamente)

if __name__ == "__main__":
    capacidades = [15, 25]
    modos = ["penalizacion", "reparacion"]
    repeticiones = 10

    filas = []
    historiales = {}
    for capacidad in capacidades:
        for modo in modos:
            valores_finales = []
            pesos_finales = []
            generaciones_finales = []
            for rep in range(repeticiones):
                resultado = ejecutar_ga(capacidad=capacidad, modo=modo, semilla=rep)
                valores_finales.append(resultado["mejor_valor"])
                pesos_finales.append(resultado["mejor_peso"])
                generaciones_finales.append(resultado["mejor_generacion"])
                if rep == 0:
                    historiales[(capacidad, modo)] = resultado["historial"]
            filas.append({
                "Capacidad": capacidad,
                "Modo": modo,
                "Valor promedio": promedio(valores_finales),
                "Valor mejor": max(valores_finales),
                "Peso promedio": promedio(pesos_finales),
                "Generacion promedio mejor": promedio(generaciones_finales),
            })

    tabla = pd.DataFrame(filas)
    print("=== RESULTADOS MOCHILA (promedio de %d corridas) ===" % repeticiones)
    print(tabla.to_string(index=False))
    tabla.to_csv(os.path.join(RESULTADOS_DIR, "mochila_resultados.csv"), index=False)

    plt.figure(figsize=(9, 5))
    for (capacidad, modo), historial in historiales.items():
        plt.plot(historial, label=f"cap={capacidad}, {modo}")
    plt.xlabel("Generacion")
    plt.ylabel("Mejor valor factible")
    plt.title("Convergencia Mochila")
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(RESULTADOS_DIR, "mochila_convergencia.png"), dpi=150)
    plt.show()

    mejor = ejecutar_ga(capacidad=25, modo="reparacion", semilla=0)
    print("\nMejor solucion (capacidad=25, reparacion):")
    print("Valor:", mejor["mejor_valor"], "| Peso:", mejor["mejor_peso"],
          "| Generacion:", mejor["mejor_generacion"])
    print(seleccion_a_tabla(mejor["mejor_individuo"]))
