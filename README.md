# Proyecto final de Ciencia de Datos

**Alumno:** Jose Antonio Ortega Jacobo  
**Escuela:** CU UAEMEX Texcoco  
**Carrera:** Ingeniería en Computación

## ¿De qué trata?

Clasificamos tumores benignos y malignos usando el conjunto **Breast Cancer Wisconsin (Diagnostic)**. Es un proyecto para practicar Python y comparar modelos, no una herramienta de diagnóstico.

Usamos cuatro modelos: regresión logística (como referencia), Naive Bayes, SVM y una red neuronal pequeña. Los datos vienen con `scikit-learn`, así que **no necesitas descargarlos por separado**.

## Subir a GitHub automaticamente (Windows)

1. Descarga el ZIP y **extrae toda la carpeta** (no ejecutes archivos dentro del ZIP).
2. Abre la carpeta `Proyecto_Wisconsin_Sencillo_Jose_Antonio`.
3. Haz doble clic en **`SUBIR_TODO.cmd`**.
4. Si faltan Git o GitHub CLI, el programa tratara de instalarlos con `winget`.
5. Si GitHub abre el navegador, inicia sesion y autoriza el acceso.
6. Al terminar se abrira tu repositorio **publico** en GitHub.

El repositorio se llama `Proyecto-Final-Ciencia-de-Datos` de forma predeterminada. Si ya existe, cambia `$nombreRepo` al inicio de `SUBIR_A_GITHUB.ps1`. Si prefieres un repositorio privado, cambia `$visibilidad` a `--private`.

El script usa tu nombre y una direccion `noreply` para los commits, **sin incluir tu correo personal en el articulo**. No instala Python: el proyecto ya incluye los resultados y el reporte; para ejecutar el codigo usa las instrucciones de abajo.

## Cómo ejecutarlo en Windows

1. Descarga este repositorio y abre la carpeta del proyecto en VS Code.
2. Abre una terminal en esa misma carpeta.
3. Instala las librerías:

   ```powershell
   py -m pip install -r requirements.txt
   ```

4. Ejecuta el programa:

   ```powershell
   py proyecto.py
   ```

También puedes abrir **`Exploracion_y_modelos.ipynb`** en Jupyter o VS Code y ejecutar las celdas una por una.

## ¿Qué hace el código?

1. Carga los datos y revisa si faltan valores.
2. Divide los registros en entrenamiento, validación y prueba.
3. Hace las gráficas del análisis exploratorio (EDA).
4. Escala los datos y entrena los cuatro modelos.
5. Prueba distintos parámetros con validación cruzada de cinco partes.
6. Calcula accuracy, precision, recall, F1, AUC y matrices de confusión.
7. Guarda las gráficas y las tablas en la carpeta **`resultados/`**.

## Resultados del experimento

Se usaron 569 filas y 30 columnas, con semilla 42 y división 60/20/20. La clase positiva es **maligno = 1**.

| Modelo | Exactitud | F1 | Sensibilidad |
| --- | ---: | ---: | ---: |
| Regresión logística | 98.25 % | 0.9756 | 95.24 % |
| Naive Bayes | 92.11 % | 0.8889 | 85.71 % |
| SVM | 98.25 % | 0.9756 | 95.24 % |
| Red neuronal | 95.61 % | 0.9398 | 92.86 % |

Los resultados pueden variar ligeramente con otras versiones de las librerías. En este experimento la regresión logística fue elegida usando el conjunto de validación.

## Archivos principales

- `proyecto.py`: todo el ejercicio explicado en pasos.
- `Exploracion_y_modelos.ipynb`: los mismos pasos separados en celdas.
- `requirements.txt`: librerías necesarias.
- `resultados/`: 8 gráficas y archivos CSV con métricas y errores.
- `articulo/Articulo_IEEE_Ciencia_de_Datos.pdf`: reporte de 6 páginas con formato IEEE.
- `articulo/articulo_ieee.tex`: reporte editable en LaTeX.
- `SUBIR_TODO.cmd`: doble clic para publicar el proyecto en GitHub.
- `SUBIR_A_GITHUB.ps1`: script que instala herramientas si faltan y sube los archivos.

No se incluye una presentación, ya que el trabajo se entrega como repositorio y artículo.

## Datos y referencias

Conjunto de datos: [UCI, Breast Cancer Wisconsin (Diagnostic)](https://archive.ics.uci.edu/dataset/17/breast-cancer-wisconsin-diagnostic).

El artículo contiene solo cinco referencias académicas, una para cada tema importante (datos, Naive Bayes, SVM, red neuronal y curva ROC), como pide la consigna. Se recomienda leerlas y explicar el trabajo con palabras propias antes de entregarlo.
