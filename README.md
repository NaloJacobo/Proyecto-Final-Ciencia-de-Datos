# Proyecto final de Ciencia de Datos

**Alumno:** Jose Antonio Ortega Jacobo  
**Escuela:** CU UAEMEX Texcoco  
**Carrera:** Ingeniería en Computación

## Descripción

En este proyecto clasificamos tumores como benignos o malignos usando el conjunto de datos **Breast Cancer Wisconsin (Diagnostic)**. La idea es practicar el análisis de datos en Python y comparar varios métodos de clasificación. Este ejercicio es académico y no sustituye un diagnóstico médico.

Se comparan cuatro modelos: **regresión logística** (referencia), **Naive Bayes**, **SVM** y una **red neuronal pequeña**. Los datos están incluidos en `scikit-learn`, así que no hay que descargarlos por separado.

## Requisitos

- Python 3
- Las librerías indicadas en `requirements.txt`

## Cómo ejecutar el proyecto

1. Abre la carpeta en VS Code o en una terminal.
2. Instala las librerías:

   ```powershell
   py -m pip install -r requirements.txt
   ```

3. Ejecuta el archivo principal:

   ```powershell
   py proyecto.py
   ```

También puedes abrir **`Exploracion_y_modelos.ipynb`** en Jupyter o VS Code para ejecutar el trabajo paso a paso.

## Pasos del ejercicio

1. Cargar los datos y comprobar si hay valores faltantes.
2. Separar los datos en entrenamiento, validación y prueba.
3. Explorar la información con gráficas (EDA).
4. Escalar los datos y entrenar los cuatro modelos.
5. Comparar parámetros mediante validación cruzada de cinco partes.
6. Calcular exactitud, precisión, sensibilidad, F1, AUC y matrices de confusión.
7. Guardar las tablas y gráficas en `resultados/`.

## Resultados

El conjunto tiene **569 registros** y **30 características**. Se utilizó la semilla **42** y una separación de **60 % entrenamiento, 20 % validación y 20 % prueba**. La clase positiva corresponde a los tumores malignos.

| Modelo | Exactitud | F1 | Sensibilidad |
| --- | ---: | ---: | ---: |
| Regresión logística | 98.25 % | 0.9756 | 95.24 % |
| Naive Bayes | 92.11 % | 0.8889 | 85.71 % |
| SVM | 98.25 % | 0.9756 | 95.24 % |
| Red neuronal | 95.61 % | 0.9398 | 92.86 % |

En este experimento la regresión logística fue seleccionada con el conjunto de validación. Los resultados pueden variar ligeramente según la versión de las librerías.

## Archivos del proyecto

- `proyecto.py`: código principal, explicado por pasos.
- `Exploracion_y_modelos.ipynb`: el ejercicio dividido en celdas.
- `requirements.txt`: librerías necesarias.
- `resultados/`: gráficas, tablas de métricas, parámetros y análisis de errores.
- `articulo/Articulo_IEEE_Ciencia_de_Datos.pdf`: artículo de seis páginas en formato IEEE.
- `articulo/articulo_ieee.tex`: archivo editable del artículo.

## Datos y referencias

Conjunto utilizado: [Breast Cancer Wisconsin (Diagnostic), UCI](https://archive.ics.uci.edu/dataset/17/breast-cancer-wisconsin-diagnostic).

Las cinco referencias académicas relacionadas con los métodos y la evaluación están al final del artículo IEEE.
