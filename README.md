# Taller 1 — Algoritmos Genéticos

Implementación de los 4 problemas del taller (N-Reinas, TSP, Asignación de cursos,
Mochila) con Algoritmos Genéticos en Python, pensada para trabajarse en
**Anaconda / Spyder**, más una aplicación web de despliegue hecha con **Streamlit**.

## Estructura del proyecto

```
Taller_Geneticos/
├── algoritmos/                 # Los 4 algoritmos geneticos (reutilizables)
│   ├── n_reinas.py              # Problema base: N-Reinas
│   ├── tsp.py                   # Ejercicio 1: Agente Viajero (TSP)
│   ├── asignacion_cursos.py     # Ejercicio 2: cursos a salas de computo
│   └── mochila.py               # Ejercicio 3: Mochila (Knapsack)
├── app_web/                    # Aplicacion web (Streamlit)
│   ├── Home.py                  # Pagina de inicio + conceptos clave
│   └── pages/
│       ├── 1_N_Reinas.py
│       ├── 2_TSP.py
│       ├── 3_Asignacion_Cursos.py
│       └── 4_Mochila.py
├── resultados/                 # CSV y PNG generados por la experimentacion
├── conceptos_clave.md          # Respuestas a las 5 preguntas conceptuales
├── informe_final.md            # Informe con metodologia, resultados y conclusiones
├── requirements.txt
└── taller_ia_geneticos.pdf     # Enunciado original del taller
```

## 1. Ejecutar los algoritmos en Spyder (Anaconda)

1. Abre Anaconda Navigator y lanza **Spyder** (o desde la Anaconda Prompt: `spyder`).
2. Instala las librerías si tu entorno de Anaconda no las tiene:
   ```
   conda install numpy pandas matplotlib
   ```
3. Abre cualquiera de los archivos en `algoritmos/` (por ejemplo `n_reinas.py`) y
   ejecútalo completo con **F5**. Cada script:
   - Define las funciones del algoritmo genético (representación, aptitud,
     selección, cruzamiento, mutación).
   - Al ejecutarse directamente, corre la experimentación pedida por el taller
     (barrido de parámetros, comparaciones, tablas y gráficas) e imprime los
     resultados en la consola de Spyder.
   - Guarda tablas `.csv` y gráficas `.png` en la carpeta `resultados/`.
   - Muestra las gráficas en el panel *Plots* de Spyder.
4. Los archivos están divididos en celdas (separadas por `# %%`), así que también
   puedes ejecutarlos bloque por bloque con `Ctrl+Enter` para explorar cada parte
   del algoritmo por separado (representación, operadores, ciclo evolutivo,
   experimentación).

## 2. Ejecutar la aplicación web (Streamlit)

1. Instala Streamlit si no lo tienes (en la Anaconda Prompt, con el entorno activado):
   ```
   pip install streamlit
   ```
   o
   ```
   conda install -c conda-forge streamlit
   ```
2. Desde la carpeta raíz del proyecto (`Taller_Geneticos`), ejecuta:
   ```
   streamlit run app_web/Home.py
   ```
3. Se abrirá el navegador en `http://localhost:8501`. En el menú lateral izquierdo
   puedes navegar entre las 4 páginas, una por cada problema, cada una con:
   - **N-Reinas**: tablero visual con las reinas, sliders de N/población/mutación.
   - **TSP**: mapa con la ruta encontrada, selector de tipo de mutación.
   - **Asignación de cursos**: tablas de cursos/salas (pestaña "Datos del problema") y horario resultante.
   - **Mochila**: tabla de objetos editable en vivo y barra de capacidad usada.

## 3. Documentos del taller

- [`conceptos_clave.md`](conceptos_clave.md): respuestas a las 5 preguntas de la
  sección "CONCEPTOS CLAVE" del enunciado.
- [`informe_final.md`](informe_final.md): metodología, resultados (tablas con datos
  reales de la experimentación), análisis por problema y conclusión comparativa,
  tal como pide la sección "ENTREGA FINAL" del taller.
- [`resultados/`](resultados/): evidencia de experimentación (CSV con las tablas y
  PNG con las gráficas de convergencia usadas en el informe).
