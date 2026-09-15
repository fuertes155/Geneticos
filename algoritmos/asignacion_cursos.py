"""
EJERCICIO 2 - ASIGNACION DE CURSOS A SALAS DE COMPUTO
Algoritmo Genetico con representacion basada en penalizaciones.

Cada gen representa la (sala, franja) asignada a un curso, codificada como un
unico entero: gen = sala_id * n_franjas + franja_id.

La funcion de aptitud penaliza restricciones duras (sobrecupo, recursos
faltantes, choque de sala/franja, franjas bloqueadas) y premia levemente una
distribucion equilibrada entre salas (restriccion blanda).

Este archivo esta escrito con bucles simples (sin numpy, sin funciones
lambda) para que sea facil de leer y explicar linea por linea. Ejecutable
completo en Spyder (F5) o por celdas "# %%". Las funciones se reutilizan
desde app_web/pages/3_Asignacion_Cursos.py sin correr los experimentos.
"""

import os
import random
import pandas as pd
import matplotlib.pyplot as plt

RESULTADOS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "resultados")
os.makedirs(RESULTADOS_DIR, exist_ok=True)

# %% Datos del problema

CURSOS = pd.DataFrame([
    {"curso": "Programacion I",        "estudiantes": 28, "necesita_pc": True,  "software": "IDE"},
    {"curso": "Bases de Datos",        "estudiantes": 22, "necesita_pc": True,  "software": "SQL"},
    {"curso": "Redes",                 "estudiantes": 30, "necesita_pc": True,  "software": ""},
    {"curso": "Ingenieria de Software","estudiantes": 25, "necesita_pc": False, "software": ""},
    {"curso": "Inteligencia Artificial","estudiantes": 20, "necesita_pc": True, "software": "Python"},
    {"curso": "Sistemas Operativos",   "estudiantes": 18, "necesita_pc": True,  "software": ""},
    {"curso": "Electiva I",            "estudiantes": 35, "necesita_pc": False, "software": ""},
    {"curso": "Electiva II",           "estudiantes": 15, "necesita_pc": True,  "software": "Python"},
])

SALAS = pd.DataFrame([
    {"sala": "Lab-1", "capacidad": 30, "tiene_pc": True,  "software": ["IDE", "SQL", "Python"]},
    {"sala": "Lab-2", "capacidad": 20, "tiene_pc": True,  "software": ["Python"]},
    {"sala": "Aula-A", "capacidad": 40, "tiene_pc": False, "software": []},
    {"sala": "Aula-B", "capacidad": 25, "tiene_pc": True,  "software": ["IDE"]},
])

FRANJAS = ["7-9", "9-11", "11-13", "14-16", "16-18"]

# (sala_idx, franja_idx) bloqueados, p.ej. mantenimiento o reserva institucional
FRANJAS_BLOQUEADAS = {(2, 0), (1, 4)}

N_CURSOS = len(CURSOS)
N_SALAS = len(SALAS)
N_FRANJAS = len(FRANJAS)
N_COMBOS = N_SALAS * N_FRANJAS

PESO_SOBRECUPO = 5
PESO_RECURSOS = 20
PESO_CHOQUE = 50
PESO_BLOQUEO = 30
PESO_BALANCE = 0.5

# Listas planas para acceso rapido dentro del ciclo evolutivo (evita el
# overhead de DataFrame.iloc, que resulta muy lento con miles de llamadas).
# El software vacio se guarda como "" (no como None) para que la comparacion
# "if software_requerido:" funcione igual para todos los cursos que no
# necesitan software especifico.
_CURSOS_ESTUDIANTES = CURSOS["estudiantes"].tolist()
_CURSOS_NECESITA_PC = CURSOS["necesita_pc"].tolist()
_CURSOS_SOFTWARE = CURSOS["software"].tolist()
_SALAS_CAPACIDAD = SALAS["capacidad"].tolist()
_SALAS_TIENE_PC = SALAS["tiene_pc"].tolist()
_SALAS_SOFTWARE = SALAS["software"].tolist()

# %% Representacion y funcion de aptitud


def decodificar(gen):
    """Convierte el entero del gen en (sala_idx, franja_idx)."""
    sala_idx = gen // N_FRANJAS
    franja_idx = gen % N_FRANJAS
    return sala_idx, franja_idx


def crear_individuo():
    individuo = []
    for _ in range(N_CURSOS):
        individuo.append(random.randrange(N_COMBOS))
    return individuo


def crear_poblacion(tam_poblacion):
    poblacion = []
    for _ in range(tam_poblacion):
        poblacion.append(crear_individuo())
    return poblacion


def calcular_penalizacion(individuo):
    """Suma una penalizacion por cada restriccion violada. 0 = horario perfecto."""
    penalizacion = 0.0
    ocupacion = {}
    uso_por_sala = [0] * N_SALAS

    for curso_idx in range(N_CURSOS):
        gen = individuo[curso_idx]
        sala_idx, franja_idx = decodificar(gen)
        uso_por_sala[sala_idx] += 1

        # Restriccion dura: el curso no debe superar la capacidad de la sala
        exceso = _CURSOS_ESTUDIANTES[curso_idx] - _SALAS_CAPACIDAD[sala_idx]
        if exceso > 0:
            penalizacion += PESO_SOBRECUPO * exceso

        # Restriccion dura: la sala debe tener computadores si el curso los necesita
        if _CURSOS_NECESITA_PC[curso_idx] and not _SALAS_TIENE_PC[sala_idx]:
            penalizacion += PESO_RECURSOS

        # Restriccion dura: la sala debe tener el software que el curso requiere
        software_requerido = _CURSOS_SOFTWARE[curso_idx]
        if software_requerido and software_requerido not in _SALAS_SOFTWARE[sala_idx]:
            penalizacion += PESO_RECURSOS

        # Restriccion dura: la franja no debe estar bloqueada para esa sala
        if (sala_idx, franja_idx) in FRANJAS_BLOQUEADAS:
            penalizacion += PESO_BLOQUEO

        # Se registra que (sala, franja) quedo ocupada por este curso
        slot = (sala_idx, franja_idx)
        ocupacion[slot] = ocupacion.get(slot, 0) + 1

    # Restriccion dura: no puede haber dos cursos en la misma sala y franja
    for cantidad in ocupacion.values():
        if cantidad > 1:
            penalizacion += PESO_CHOQUE * (cantidad - 1)

    # Restriccion blanda: repartir los cursos parejo entre las salas.
    # La varianza mide que tan dispersos estan los valores de uso_por_sala
    # respecto a su promedio (0 = perfectamente parejo).
    media_uso = sum(uso_por_sala) / N_SALAS
    varianza_uso = 0.0
    for cantidad in uso_por_sala:
        varianza_uso += (cantidad - media_uso) ** 2
    varianza_uso = varianza_uso / N_SALAS
    penalizacion += PESO_BALANCE * varianza_uso

    return penalizacion


def aptitud(individuo):
    """Se maximiza; 0 es el optimo (sin penalizacion)."""
    return -calcular_penalizacion(individuo)


def desglosar_penalizacion(individuo):
    """Detalle por tipo de restriccion, util para mostrar en el informe/app."""
    detalle = {"sobrecupo": 0.0, "recursos": 0.0, "choques": 0.0, "bloqueos": 0.0, "balance": 0.0}
    ocupacion = {}
    uso_por_sala = [0] * N_SALAS

    for curso_idx in range(N_CURSOS):
        gen = individuo[curso_idx]
        sala_idx, franja_idx = decodificar(gen)
        uso_por_sala[sala_idx] += 1

        exceso = _CURSOS_ESTUDIANTES[curso_idx] - _SALAS_CAPACIDAD[sala_idx]
        if exceso > 0:
            detalle["sobrecupo"] += PESO_SOBRECUPO * exceso

        if _CURSOS_NECESITA_PC[curso_idx] and not _SALAS_TIENE_PC[sala_idx]:
            detalle["recursos"] += PESO_RECURSOS

        software_requerido = _CURSOS_SOFTWARE[curso_idx]
        if software_requerido and software_requerido not in _SALAS_SOFTWARE[sala_idx]:
            detalle["recursos"] += PESO_RECURSOS

        if (sala_idx, franja_idx) in FRANJAS_BLOQUEADAS:
            detalle["bloqueos"] += PESO_BLOQUEO

        slot = (sala_idx, franja_idx)
        ocupacion[slot] = ocupacion.get(slot, 0) + 1

    for cantidad in ocupacion.values():
        if cantidad > 1:
            detalle["choques"] += PESO_CHOQUE * (cantidad - 1)

    media_uso = sum(uso_por_sala) / N_SALAS
    varianza_uso = 0.0
    for cantidad in uso_por_sala:
        varianza_uso += (cantidad - media_uso) ** 2
    varianza_uso = varianza_uso / N_SALAS
    detalle["balance"] = PESO_BALANCE * varianza_uso

    return detalle


# %% Operadores geneticos


def seleccion_torneo(poblacion, aptitudes, k=3):
    """Elige k individuos al azar y devuelve el de mayor aptitud entre ellos."""
    participantes = random.sample(range(len(poblacion)), k)
    mejor_idx = participantes[0]
    for idx in participantes:
        if aptitudes[idx] > aptitudes[mejor_idx]:
            mejor_idx = idx
    return poblacion[mejor_idx]


def cruzamiento_uniforme(padre1, padre2, prob_cruce=0.8):
    """Para cada gen, se sortea de cual de los dos padres lo hereda el hijo 1."""
    if random.random() > prob_cruce:
        return padre1[:], padre2[:]
    hijo1 = []
    hijo2 = []
    for i in range(len(padre1)):
        if random.random() < 0.5:
            hijo1.append(padre1[i])
            hijo2.append(padre2[i])
        else:
            hijo1.append(padre2[i])
            hijo2.append(padre1[i])
    return hijo1, hijo2


def mutacion(individuo, tasa_mutacion):
    nuevo = individuo[:]
    for i in range(len(nuevo)):
        if random.random() < tasa_mutacion:
            nuevo[i] = random.randrange(N_COMBOS)
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


def ejecutar_ga(tam_poblacion=100, generaciones=300, tasa_mutacion=0.1,
                 prob_cruce=0.8, elitismo=2, semilla=None):
    if semilla is not None:
        random.seed(semilla)

    poblacion = crear_poblacion(tam_poblacion)
    historial_mejor = []
    mejor_individuo = None
    mejor_penalizacion = float("inf")

    for _ in range(generaciones):
        # 1) Evaluar penalizacion y aptitud de toda la poblacion
        penalizaciones = []
        aptitudes = []
        for individuo in poblacion:
            p = calcular_penalizacion(individuo)
            penalizaciones.append(p)
            aptitudes.append(-p)

        # 2) Buscar el mejor horario de esta generacion (menor penalizacion)
        idx_mejor_gen = 0
        for i in range(len(penalizaciones)):
            if penalizaciones[i] < penalizaciones[idx_mejor_gen]:
                idx_mejor_gen = i

        if penalizaciones[idx_mejor_gen] < mejor_penalizacion:
            mejor_penalizacion = penalizaciones[idx_mejor_gen]
            mejor_individuo = poblacion[idx_mejor_gen][:]
        historial_mejor.append(mejor_penalizacion)

        # 3) Elitismo (se puede desactivar poniendo elitismo=0)
        nueva_poblacion = []
        if elitismo > 0:
            indices_elite = obtener_mejores_indices(aptitudes, elitismo)
            for i in indices_elite:
                nueva_poblacion.append(poblacion[i][:])

        # 4) El resto se completa con seleccion + cruce uniforme + mutacion
        while len(nueva_poblacion) < tam_poblacion:
            padre1 = seleccion_torneo(poblacion, aptitudes)
            padre2 = seleccion_torneo(poblacion, aptitudes)
            hijo1, hijo2 = cruzamiento_uniforme(padre1, padre2, prob_cruce)
            hijo1 = mutacion(hijo1, tasa_mutacion)
            hijo2 = mutacion(hijo2, tasa_mutacion)
            nueva_poblacion.append(hijo1)
            if len(nueva_poblacion) < tam_poblacion:
                nueva_poblacion.append(hijo2)

        poblacion = nueva_poblacion

    return {
        "mejor_individuo": mejor_individuo,
        "mejor_penalizacion": mejor_penalizacion,
        "historial": historial_mejor,
    }


def horario_a_tabla(individuo):
    """Convierte el individuo en una tabla salas x franjas con el curso asignado."""
    tabla = pd.DataFrame("-", index=SALAS["sala"], columns=FRANJAS)
    for curso_idx in range(N_CURSOS):
        gen = individuo[curso_idx]
        sala_idx, franja_idx = decodificar(gen)
        nombre_curso = CURSOS.iloc[curso_idx]["curso"]
        celda_actual = tabla.iloc[sala_idx, franja_idx]
        if celda_actual == "-":
            tabla.iloc[sala_idx, franja_idx] = nombre_curso
        else:
            tabla.iloc[sala_idx, franja_idx] = celda_actual + " / " + nombre_curso
    return tabla


# %% Funcion simple para promedio (en vez de usar numpy)


def promedio(lista):
    return sum(lista) / len(lista)


# %% Experimentacion (solo corre si se ejecuta este script directamente)

if __name__ == "__main__":
    # Poblacion pequena y pocas generaciones para que el efecto del elitismo
    # sea visible; con parametros holgados (100/300) el problema es tan
    # sencillo que ambas variantes llegan igual al optimo.
    TAM_POBLACION = 20
    GENERACIONES = 15
    TASA_MUTACION = 0.2

    print("=== Comparacion CON y SIN elitismo (15 corridas) ===")
    filas = []
    historiales = {}
    for etiqueta, elitismo in [("Con elitismo", 2), ("Sin elitismo", 0)]:
        finales = []
        for rep in range(15):
            resultado = ejecutar_ga(tam_poblacion=TAM_POBLACION, generaciones=GENERACIONES,
                                     tasa_mutacion=TASA_MUTACION, elitismo=elitismo, semilla=rep)
            finales.append(resultado["mejor_penalizacion"])
            if rep == 0:
                historiales[etiqueta] = resultado["historial"]
        filas.append({
            "Configuracion": etiqueta,
            "Mejor": min(finales),
            "Peor": max(finales),
            "Promedio": promedio(finales),
        })
    tabla_comparacion = pd.DataFrame(filas)
    print(tabla_comparacion.to_string(index=False))
    tabla_comparacion.to_csv(os.path.join(RESULTADOS_DIR, "cursos_elitismo.csv"), index=False)

    plt.figure(figsize=(9, 5))
    for etiqueta, historial in historiales.items():
        plt.plot(historial, label=etiqueta)
    plt.xlabel("Generacion")
    plt.ylabel("Mejor penalizacion (menor es mejor)")
    plt.title("Convergencia asignacion de cursos")
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(RESULTADOS_DIR, "cursos_convergencia.png"), dpi=150)
    plt.show()

    mejor = ejecutar_ga(elitismo=2, generaciones=400, semilla=0)
    print("\nMejor penalizacion encontrada:", mejor["mejor_penalizacion"])
    print("\nHorario final:")
    print(horario_a_tabla(mejor["mejor_individuo"]))
