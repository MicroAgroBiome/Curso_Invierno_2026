"""Figuras para las libretas de curso (09 y 10).

Todo el codigo de graficado vive aqui para que las libretas se puedan leer de corrido.
Cada funcion dibuja una figura y la devuelve; la libreta solo tiene que llamarla con sus
datos. No hace falta leer este archivo para seguir el curso.
"""

from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.metrics import confusion_matrix

AZUL = "#4C72B0"
ROJO = "#C44E52"
VERDE = "#55A868"
NARANJA = "#DD8452"
MORADO = "#8172B3"
COLORES_CLASE = {"Clase A": AZUL, "Clase B": NARANJA, "Clase C": VERDE}


def aplicar_estilo() -> None:
    """Estilo comun para todas las figuras del curso."""
    sns.set_theme(style="whitegrid", context="notebook")
    plt.rcParams["figure.dpi"] = 120


def preparar_libreta() -> None:
    """Deja el entorno listo: estilo de figuras y sin avisos tecnicos que distraigan.

    Son tres cosas de fontaneria que no aportan nada al tema del curso:
    - el estilo comun de las figuras,
    - silenciar los avisos de bibliotecas,
    - decirle a joblib cuantos nucleos usar, porque en Windows intenta averiguarlo
      llamando a un programa del sistema que no siempre existe y escupe un error feo.
    """
    import os
    import warnings

    warnings.filterwarnings("ignore")
    os.environ.setdefault("LOKY_MAX_CPU_COUNT", "4")
    aplicar_estilo()


# ----------------------------------------------------------------------------------
# Libreta 09: la cadena composicional
# ----------------------------------------------------------------------------------


def profundidad_por_muestra(lecturas_por_muestra: pd.Series):
    """Histograma de cuantas lecturas tiene cada muestra."""
    figura, eje = plt.subplots(figsize=(7, 3.5))
    eje.hist(lecturas_por_muestra, bins=40, color=MORADO)
    eje.set_xscale("log")
    eje.set_xlabel("lecturas por muestra (escala logaritmica)")
    eje.set_ylabel("numero de muestras")
    eje.set_title("Cada muestra se secuencio a una profundidad distinta")
    figura.tight_layout()
    return figura


def dos_muestras_lado_a_lado(conteos: pd.DataFrame, relativa: pd.DataFrame,
                             muestra_a: str, muestra_b: str, n_taxones: int = 12):
    """Compara dos muestras antes y despues de cerrar, con los taxones mas abundantes."""
    taxones = relativa.loc[[muestra_a, muestra_b]].sum(axis=0).nlargest(n_taxones).index
    posiciones = np.arange(len(taxones))
    ancho = 0.4

    figura, ejes = plt.subplots(1, 2, figsize=(12, 3.8))
    ejes[0].bar(posiciones - ancho / 2, conteos.loc[muestra_a, taxones], ancho,
                label=muestra_a, color=AZUL)
    ejes[0].bar(posiciones + ancho / 2, conteos.loc[muestra_b, taxones], ancho,
                label=muestra_b, color=NARANJA)
    ejes[0].set_title("Conteos: dependen de la profundidad")
    ejes[0].set_ylabel("lecturas")

    ejes[1].bar(posiciones - ancho / 2, relativa.loc[muestra_a, taxones], ancho,
                label=muestra_a, color=AZUL)
    ejes[1].bar(posiciones + ancho / 2, relativa.loc[muestra_b, taxones], ancho,
                label=muestra_b, color=NARANJA)
    ejes[1].set_title("Abundancia relativa: ya se pueden comparar")
    ejes[1].set_ylabel("fraccion de la muestra")

    for eje in ejes:
        eje.set_xticks(posiciones)
        eje.set_xticklabels([t.replace("Taxon-", "T") for t in taxones], rotation=45, fontsize=8)
        eje.legend(fontsize=8)
    figura.tight_layout()
    return figura


def ceros_y_prevalencia(conteos: pd.DataFrame, umbral: float):
    """Dos paneles: ceros por muestra y prevalencia por taxon con el umbral marcado."""
    ceros_por_muestra = (conteos == 0).mean(axis=1)
    prevalencia = (conteos > 0).mean(axis=0)

    figura, ejes = plt.subplots(1, 2, figsize=(11, 3.5))
    ejes[0].hist(ceros_por_muestra, bins=35, color=VERDE)
    ejes[0].set_xlabel("fraccion de taxones ausentes")
    ejes[0].set_ylabel("numero de muestras")
    ejes[0].set_title("Cuantos ceros tiene cada muestra")

    ejes[1].hist(prevalencia, bins=40, color=AZUL)
    ejes[1].axvline(umbral, color=ROJO, linestyle="--", linewidth=1.6,
                    label=f"umbral = {umbral:.0%}")
    ejes[1].set_xlabel("en que fraccion de muestras aparece el taxon")
    ejes[1].set_ylabel("numero de taxones")
    ejes[1].set_title("Prevalencia de cada taxon")
    ejes[1].legend(fontsize=8)
    figura.tight_layout()
    return figura


def antes_y_despues_de_amalgamar(antes: pd.DataFrame, despues: pd.DataFrame):
    """Cuantos ceros quedan antes y despues de agrupar los taxones raros."""
    ceros_antes = (antes == 0).mean(axis=1)
    ceros_despues = (despues == 0).mean(axis=1)

    figura, eje = plt.subplots(figsize=(7, 3.5))
    eje.hist([ceros_antes, ceros_despues], bins=30,
             label=[f"antes ({antes.shape[1]} columnas)",
                    f"despues ({despues.shape[1]} columnas)"],
             color=[ROJO, VERDE])
    eje.set_xlabel("fraccion de ceros por muestra")
    eje.set_ylabel("numero de muestras")
    eje.set_title("La amalgamacion quita la mayor parte de los ceros")
    eje.legend(fontsize=8)
    figura.tight_layout()
    return figura


def efecto_del_tratamiento_de_ceros(antes: pd.DataFrame, despues: pd.DataFrame,
                                    pseudoconteo: float):
    """Distribucion de los valores antes y despues de sustituir los ceros."""
    valores_antes = antes.to_numpy()
    positivos_antes = valores_antes[valores_antes > 0]
    valores_despues = despues.to_numpy().ravel()

    figura, eje = plt.subplots(figsize=(7.5, 3.8))
    eje.hist(np.log10(positivos_antes), bins=55, alpha=0.6,
             label="valores positivos antes", color=AZUL)
    eje.hist(np.log10(valores_despues), bins=55, alpha=0.6,
             label="todos los valores despues", color=NARANJA)
    eje.axvline(np.log10(pseudoconteo), color=ROJO, linestyle="--", linewidth=1.6,
                label="pseudoconteo c")
    eje.set_xlabel("logaritmo base 10 de la abundancia")
    eje.set_ylabel("numero de valores")
    eje.set_title("Los ceros pasan a valer c; el resto baja un poco")
    eje.legend(fontsize=8)
    figura.tight_layout()
    return figura


def antes_y_despues_del_clr(antes: pd.DataFrame, despues: pd.DataFrame, muestra: str):
    """La misma muestra antes y despues del CLR."""
    figura, ejes = plt.subplots(1, 2, figsize=(11, 3.5))
    ejes[0].hist(antes.loc[muestra], bins=45, color=AZUL)
    ejes[0].set_xlabel("abundancia")
    ejes[0].set_title(f"Antes del CLR: {muestra}")

    ejes[1].hist(despues.loc[muestra], bins=45, color=VERDE)
    ejes[1].axvline(0, color=ROJO, linestyle="--", linewidth=1.5)
    ejes[1].set_xlabel("coordenada CLR")
    ejes[1].set_title("Despues del CLR: centrada en cero")

    for eje in ejes:
        eje.set_ylabel("numero de taxones")
    figura.tight_layout()
    return figura


# ----------------------------------------------------------------------------------
# Libreta 10: ACP y clasificacion
# ----------------------------------------------------------------------------------


def comparar_acp(puntos_sin_clr: pd.DataFrame, puntos_con_clr: pd.DataFrame,
                 etiquetas: pd.Series, varianza_sin_clr, varianza_con_clr):
    """Dos diagramas de dispersion de PC1 frente a PC2, coloreados por clase."""
    figura, ejes = plt.subplots(1, 2, figsize=(12, 4.6))
    datos = [("Sin CLR", puntos_sin_clr, varianza_sin_clr),
             ("Con CLR", puntos_con_clr, varianza_con_clr)]

    for eje, (titulo, puntos, varianza) in zip(ejes, datos):
        for clase in sorted(etiquetas.unique()):
            esta_clase = etiquetas == clase
            eje.scatter(puntos.loc[esta_clase, "PC1"], puntos.loc[esta_clase, "PC2"],
                        s=14, alpha=0.7, color=COLORES_CLASE[clase], label=clase)
        eje.set_title(titulo)
        eje.set_xlabel(f"PC1 ({100 * varianza[0]:.1f} %)")
        eje.set_ylabel(f"PC2 ({100 * varianza[1]:.1f} %)")
    ejes[0].legend(fontsize=8)
    figura.suptitle("Las mismas muestras, antes y despues de la correccion", y=1.02)
    figura.tight_layout()
    return figura


def comparar_aciertos(resultados: pd.DataFrame, azar: float):
    """Barras de aciertos por modelo, sin CLR frente a con CLR.

    `resultados` necesita las columnas: modelo, representacion, aciertos.
    """
    modelos = list(resultados["modelo"].unique())
    posiciones = np.arange(len(modelos))
    ancho = 0.36
    colores = {"Sin CLR": ROJO, "Con CLR": AZUL}

    figura, eje = plt.subplots(figsize=(8.5, 4))
    for desplazamiento, representacion in enumerate(["Sin CLR", "Con CLR"]):
        filas = resultados[resultados["representacion"] == representacion]
        filas = filas.set_index("modelo").loc[modelos]
        barras = eje.bar(posiciones + (desplazamiento - 0.5) * ancho, filas["aciertos"],
                         ancho, label=representacion, color=colores[representacion])
        eje.bar_label(barras, fmt="%.2f", fontsize=8, padding=2)

    eje.axhline(azar, color="grey", linestyle="--", linewidth=1.3,
                label=f"azar ({azar:.2f})")
    eje.set_xticks(posiciones)
    eje.set_xticklabels(modelos)
    eje.set_ylabel("aciertos (exactitud balanceada)")
    eje.set_ylim(0, 1.1)
    eje.set_title("Aciertos con y sin correccion composicional")
    eje.legend(fontsize=8, ncol=3)
    figura.tight_layout()
    return figura


def comparar_matrices_de_confusion(verdadero: pd.Series, predicho_sin_clr,
                                   predicho_con_clr, clases: list):
    """Dos matrices de confusion lado a lado."""
    figura, ejes = plt.subplots(1, 2, figsize=(11, 4.2))
    datos = [("Sin CLR", predicho_sin_clr), ("Con CLR", predicho_con_clr)]

    for eje, (titulo, predicho) in zip(ejes, datos):
        matriz = confusion_matrix(verdadero, predicho, labels=clases)
        sns.heatmap(matriz, annot=True, fmt="d", cmap="Blues", cbar=False,
                    xticklabels=clases, yticklabels=clases, ax=eje)
        eje.set_title(titulo)
        eje.set_xlabel("lo que predijo el modelo")
        eje.set_ylabel("lo que era en realidad")
    figura.tight_layout()
    return figura


def taxones_mas_importantes(importancias: pd.Series, taxones_firma: list,
                            cuantos: int = 15, titulo: str = ""):
    """Barras horizontales de los taxones con mayor peso, marcando los verdaderos."""
    mejores = importancias.nlargest(cuantos).sort_values()
    colores = []
    for taxon in mejores.index:
        if taxon in taxones_firma:
            colores.append(VERDE)
        else:
            colores.append("#BBBBBB")

    figura, eje = plt.subplots(figsize=(7.5, 5))
    eje.barh(range(len(mejores)), mejores.to_numpy(), color=colores)
    eje.set_yticks(range(len(mejores)))
    eje.set_yticklabels([t.replace("Taxon-", "T") for t in mejores.index], fontsize=8)
    eje.set_xlabel("peso en el modelo")
    eje.set_title(titulo)

    parches = [plt.Rectangle((0, 0), 1, 1, color=VERDE),
               plt.Rectangle((0, 0), 1, 1, color="#BBBBBB")]
    eje.legend(parches, ["taxon que separa de verdad", "los demas"], fontsize=8, loc="lower right")
    figura.tight_layout()
    return figura
