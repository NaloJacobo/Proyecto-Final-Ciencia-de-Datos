"""Proyecto final de Ciencia de Datos: clasificación de cáncer de mama.
Autor: Jose Antonio Ortega Jacobo
Ejecutar desde esta carpeta: python proyecto.py
"""

# %% 1. Importar librerías
from pathlib import Path
import warnings

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.datasets import load_breast_cancer
from sklearn.exceptions import ConvergenceWarning
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, roc_auc_score, roc_curve,
    precision_recall_curve, average_precision_score,
)
from sklearn.model_selection import train_test_split, GridSearchCV, StratifiedKFold
from sklearn.naive_bayes import GaussianNB
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

# Usamos la misma semilla para poder repetir el experimento.
SEMILLA = 42
carpeta = Path("resultados")
figuras = carpeta / "figuras"
figuras.mkdir(parents=True, exist_ok=True)
warnings.filterwarnings("ignore", category=ConvergenceWarning)

# %% 2. Cargar y revisar los datos
# El conjunto viene incluido con scikit-learn; no hay que descargar archivos.
datos = load_breast_cancer(as_frame=True)
X = datos.data.copy()
# En el dataset original 0 = maligno, 1 = benigno.
# Lo cambiamos para que la clase positiva sea maligno (1).
y = pd.Series(1 - datos.target, name="maligno")

print("Filas:", len(X))
print("Columnas:", X.shape[1])
print("Datos faltantes:", X.isna().sum().sum())
print("Filas repetidas:", X.duplicated().sum())
print("0 = Benigno, 1 = Maligno")
print(y.value_counts().sort_index())

# %% 3. Separar entrenamiento, validación y prueba
# 60% entrenamiento, 20% validación y 20% prueba.
# stratify conserva aproximadamente la proporción de clases.
X_resto, X_test, y_resto, y_test = train_test_split(
    X, y, test_size=0.20, random_state=SEMILLA, stratify=y
)
X_train, X_val, y_train, y_val = train_test_split(
    X_resto, y_resto, test_size=0.25, random_state=SEMILLA, stratify=y_resto
)
print("Entrenamiento:", len(X_train))
print("Validación:", len(X_val))
print("Prueba:", len(X_test))

# %% 4. Análisis exploratorio (EDA)
# Por buena práctica, las gráficas para estudiar los datos usan solo entrenamiento.
conteos = y_train.value_counts().sort_index()
plt.figure(figsize=(6, 4))
plt.bar(["Benigno", "Maligno"], conteos.values)
plt.title("Cantidad de casos por diagnóstico")
plt.ylabel("Número de casos")
plt.tight_layout()
plt.savefig(figuras / "01_clases.png")
plt.close()

plt.figure(figsize=(6, 4))
plt.hist(X_train.loc[y_train == 0, "mean radius"], bins=17, alpha=0.7, label="Benigno")
plt.hist(X_train.loc[y_train == 1, "mean radius"], bins=17, alpha=0.7, label="Maligno")
plt.xlabel("Radio medio")
plt.ylabel("Frecuencia")
plt.title("Radio medio según el diagnóstico")
plt.legend()
plt.tight_layout()
plt.savefig(figuras / "02_radio_hist.png")
plt.close()

# Para que el mapa sea legible usamos 10 de las 30 columnas.
columnas = [
    "mean radius", "mean texture", "mean perimeter", "mean area",
    "mean concavity", "mean concave points", "worst radius",
    "worst perimeter", "worst area", "worst concave points",
]
correlacion = X_train[columnas].corr()
plt.figure(figsize=(8, 6))
plt.imshow(correlacion, cmap="coolwarm", vmin=-1, vmax=1)
plt.colorbar(label="Correlación")
plt.xticks(range(10), columnas, rotation=70, fontsize=7)
plt.yticks(range(10), columnas, fontsize=7)
plt.title("Correlación entre variables")
plt.tight_layout()
plt.savefig(figuras / "03_correlaciones.png")
plt.close()

plt.figure(figsize=(6, 4))
plt.boxplot([
    X_train.loc[y_train == 0, "worst concave points"],
    X_train.loc[y_train == 1, "worst concave points"],
], tick_labels=["Benigno", "Maligno"])
plt.title("Puntos cóncavos por diagnóstico")
plt.ylabel("worst concave points")
plt.tight_layout()
plt.savefig(figuras / "04_boxplot.png")
plt.close()

# Guardamos una copia para revisar los valores en Excel.
X.assign(maligno=y).to_csv(carpeta / "datos.csv", index=False)
print("\nEDA: clase benigna más frecuente; no hay valores faltantes.")
print("El radio suele ser mayor en casos malignos, pero hay valores que se mezclan.")
print("Radio y perímetro están muy correlacionados.")

# %% 5. Crear los cuatro modelos
# Pipeline = primero escala los datos y después entrena el clasificador.
# Esto evita que se calcule la media usando datos de validación o prueba.
# GridSearchCV prueba varios parámetros con 5 divisiones de entrenamiento.
modelos = {
    "Regresión logística": LogisticRegression(max_iter=3000, random_state=SEMILLA),
    "Naive Bayes": GaussianNB(),
    "SVM": SVC(random_state=SEMILLA),
    "Red neuronal": MLPClassifier(solver="lbfgs", max_iter=800, random_state=SEMILLA),
}

# Listas pequeñas de parámetros para practicar la búsqueda.
parametros = {
    "Regresión logística": {"modelo__C": [0.1, 1, 10]},
    "Naive Bayes": {"modelo__var_smoothing": [1e-10, 1e-9, 1e-8, 1e-7]},
    "SVM": [
        {"modelo__kernel": ["linear"], "modelo__C": [0.1, 1, 10], "modelo__gamma": ["scale"]},
        {"modelo__kernel": ["rbf"], "modelo__C": [0.1, 1, 10], "modelo__gamma": [0.01, 0.1, 1, "scale"]},
    ],
    "Red neuronal": {
        "modelo__hidden_layer_sizes": [(16,), (32,), (32, 16)],
        "modelo__alpha": [0.001, 0.01, 0.1],  # Regularización L2
    },
}

cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=SEMILLA)
modelos_entrenados = {}
resultados_val = []
resultados_test = []
errores = []
parametros_elegidos = []

# %% 6. Entrenar, comparar y guardar métricas
for nombre, clasificador in modelos.items():
    print("\nEntrenando:", nombre)
    pasos = Pipeline([
        ("escalar", StandardScaler()),
        ("modelo", clasificador),
    ])
    busqueda = GridSearchCV(pasos, parametros[nombre], cv=cv, scoring="f1", n_jobs=1)
    busqueda.fit(X_train, y_train)
    mejor = busqueda.best_estimator_
    modelos_entrenados[nombre] = mejor

    parametros_elegidos.append({
        "modelo": nombre,
        "mejores_parametros": str(busqueda.best_params_),
        "f1_cv": round(busqueda.best_score_, 4),
        "desviacion_cv": round(busqueda.cv_results_["std_test_score"][busqueda.best_index_], 4),
    })

    # Evaluamos validación y prueba POR SEPARADO.
    for conjunto, X_actual, y_actual in [
        ("validacion", X_val, y_val),
        ("prueba", X_test, y_test),
    ]:
        pred = mejor.predict(X_actual)
        if hasattr(mejor, "decision_function"):
            puntos = mejor.decision_function(X_actual)
        else:
            puntos = mejor.predict_proba(X_actual)[:, 1]

        matriz = confusion_matrix(y_actual, pred, labels=[0, 1])
        fila = {
            "modelo": nombre,
            "accuracy": round(accuracy_score(y_actual, pred), 6),
            "precision": round(precision_score(y_actual, pred), 6),
            "recall": round(recall_score(y_actual, pred), 6),
            "f1": round(f1_score(y_actual, pred), 6),
            "roc_auc": round(roc_auc_score(y_actual, puntos), 6),
            "average_precision": round(average_precision_score(y_actual, puntos), 6),
            "tn": int(matriz[0, 0]), "fp": int(matriz[0, 1]),
            "fn": int(matriz[1, 0]), "tp": int(matriz[1, 1]),
        }
        if conjunto == "validacion":
            resultados_val.append(fila)
        else:
            resultados_test.append(fila)
            for indice, real, calculado in zip(X_test.index, y_test, pred):
                if real != calculado:
                    errores.append({
                        "modelo": nombre, "id": indice,
                        "real": int(real), "predicho": int(calculado),
                        "tipo": "Falso negativo" if real == 1 else "Falso positivo",
                        "mean_radius": X.loc[indice, "mean radius"],
                        "worst_concave_points": X.loc[indice, "worst concave points"],
                    })

validacion = pd.DataFrame(resultados_val)
prueba = pd.DataFrame(resultados_test)
validacion.to_csv(carpeta / "metricas_validacion.csv", index=False)
prueba.to_csv(carpeta / "metricas_prueba.csv", index=False)
pd.DataFrame(errores).to_csv(carpeta / "errores_prueba.csv", index=False)
resumen_cv = pd.DataFrame(parametros_elegidos)
resumen_cv.to_csv(carpeta / "hiperparametros.csv", index=False)

# Elegimos usando VALIDACIÓN; la prueba solo muestra el resultado final.
validacion_ordenada = validacion.sort_values(["f1", "recall", "roc_auc"], ascending=False)
mejor_nombre = validacion_ordenada.iloc[0]["modelo"]
print("\nTabla de resultados en prueba:")
print(prueba[["modelo", "accuracy", "precision", "recall", "f1", "roc_auc"]].to_string(index=False))
print("\nModelo elegido con validación:", mejor_nombre)

# %% 7. Gráficas para comparar modelos
fig, ejes = plt.subplots(2, 2, figsize=(9, 7))
for eje, (nombre, modelo) in zip(ejes.flat, modelos_entrenados.items()):
    matriz = confusion_matrix(y_test, modelo.predict(X_test), labels=[0, 1])
    eje.imshow(matriz, cmap="Blues")
    for fila in range(2):
        for columna in range(2):
            eje.text(columna, fila, str(matriz[fila, columna]), ha="center", va="center")
    eje.set_xticks([0, 1], ["Benigno", "Maligno"])
    eje.set_yticks([0, 1], ["Benigno", "Maligno"])
    eje.set_title(nombre)
    eje.set_xlabel("Predicción")
    eje.set_ylabel("Real")
fig.tight_layout()
fig.savefig(figuras / "05_matrices_confusion.png")
plt.close(fig)

plt.figure(figsize=(7, 5))
for nombre, modelo in modelos_entrenados.items():
    if hasattr(modelo, "decision_function"):
        puntos = modelo.decision_function(X_test)
    else:
        puntos = modelo.predict_proba(X_test)[:, 1]
    tasa_fp, tasa_tp, _ = roc_curve(y_test, puntos)
    auc = roc_auc_score(y_test, puntos)
    plt.plot(tasa_fp, tasa_tp, label=f"{nombre} (AUC={auc:.3f})")
plt.plot([0, 1], [0, 1], "--", label="Azar")
plt.title("Curvas ROC en prueba")
plt.xlabel("Falsos positivos")
plt.ylabel("Sensibilidad")
plt.legend(fontsize=8)
plt.tight_layout()
plt.savefig(figuras / "06_roc.png")
plt.close()

plt.figure(figsize=(7, 5))
for nombre, modelo in modelos_entrenados.items():
    if hasattr(modelo, "decision_function"):
        puntos = modelo.decision_function(X_test)
    else:
        puntos = modelo.predict_proba(X_test)[:, 1]
    precision, recall, _ = precision_recall_curve(y_test, puntos)
    plt.plot(recall, precision, label=nombre)
plt.title("Curvas precisión-recall en prueba")
plt.xlabel("Sensibilidad")
plt.ylabel("Precisión")
plt.legend(fontsize=8)
plt.tight_layout()
plt.savefig(figuras / "07_precision_recall.png")
plt.close()

plt.figure(figsize=(7, 4))
plt.barh(resumen_cv["modelo"], resumen_cv["f1_cv"], xerr=resumen_cv["desviacion_cv"], capsize=3)
plt.xlim(0.75, 1.02)
plt.xlabel("F1 promedio y desviación estándar (5 folds)")
plt.title("Resultados de validación cruzada")
plt.tight_layout()
plt.savefig(figuras / "08_cv_variabilidad.png")
plt.close()

print("\nListo: archivos CSV y 8 gráficas guardados en la carpeta resultados.")
