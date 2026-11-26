"""Cuantificacion del efecto de estudio y estrategias para mitigarlo.

Las correcciones se escriben como transformaciones de pliegue: reciben el entrenamiento y
la prueba por separado y devuelven ambos transformados. Ninguna usa la etiqueta de la
muestra de prueba, y las que estiman algo del estudio retenido lo hacen solo con sus
propias abundancias, que es la informacion que se tendria ante un estudio nuevo.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


# --------------------------------------------------------------------------------------
# Cuantificacion
# --------------------------------------------------------------------------------------


def eta_squared_by_feature(matrix: pd.DataFrame, groups: pd.Series) -> pd.Series:
    """Fraccion de la varianza de cada columna que queda entre grupos."""
    aligned = groups.reindex(matrix.index)
    overall = matrix.mean(axis=0)
    sizes = aligned.value_counts()
    group_means = matrix.groupby(aligned, observed=True).mean()

    between = ((group_means - overall) ** 2).mul(sizes, axis=0).sum(axis=0)
    total = ((matrix - overall) ** 2).sum(axis=0)
    return (between / total.replace(0, np.nan)).rename("eta2")


def _squared_distances(matrix: pd.DataFrame) -> np.ndarray:
    """Distancias euclidianas al cuadrado; sobre CLR son distancias de Aitchison."""
    values = matrix.to_numpy(dtype=float)
    norms = (values ** 2).sum(axis=1)
    squared = norms[:, None] + norms[None, :] - 2 * (values @ values.T)
    return np.clip(squared, 0.0, None)


def distance_r2(
    matrix: pd.DataFrame,
    groups: pd.Series,
    *,
    n_permutations: int = 999,
    random_state: int = 42,
) -> dict:
    """R2 y p de una PERMANOVA de un factor sobre la distancia de Aitchison.

    Descompone la suma de cuadrados de las distancias en la parte dentro de grupo y la
    parte entre grupos, igual que `adonis`. El valor p sale de permutar las etiquetas.
    """
    aligned = groups.reindex(matrix.index).to_numpy()
    squared = _squared_distances(matrix)
    n = len(aligned)

    def statistic(labels: np.ndarray) -> tuple[float, float]:
        total = squared.sum() / (2 * n)
        within = 0.0
        for level in pd.unique(labels):
            mask = labels == level
            size = int(mask.sum())
            if size > 1:
                within += squared[np.ix_(mask, mask)].sum() / (2 * size)
        between = total - within
        k = len(pd.unique(labels))
        f = (between / (k - 1)) / (within / (n - k)) if within > 0 and n > k else np.nan
        return between / total, f

    observed_r2, observed_f = statistic(aligned)

    rng = np.random.default_rng(random_state)
    permuted = np.empty(n_permutations)
    for index in range(n_permutations):
        permuted[index] = statistic(rng.permutation(aligned))[1]

    p_value = (1 + np.sum(permuted >= observed_f)) / (1 + n_permutations)
    return {
        "r2": float(observed_r2),
        "pseudo_f": float(observed_f),
        "p_value": float(p_value),
        "n_groups": int(len(pd.unique(aligned))),
        "n_permutations": n_permutations,
    }


def design_summary(metadata: pd.DataFrame, *, label: str = "label", study: str = "study") -> dict:
    """Describe hasta que punto el diseno permite separar la etiqueta del estudio."""
    classes_per_study = metadata.groupby(study)[label].nunique()
    studies_per_class = metadata.groupby(label)[study].nunique()
    bridging = classes_per_study[classes_per_study > 1]
    return {
        "n_studies": int(len(classes_per_study)),
        "studies_with_one_class": int((classes_per_study == 1).sum()),
        "bridging_studies": bridging.index.tolist(),
        "samples_in_bridging_studies": int(metadata[study].isin(bridging.index).sum()),
        "min_studies_per_class": int(studies_per_class.min()),
        "fraction_samples_in_single_class_studies": float(
            metadata[study].isin(classes_per_study[classes_per_study == 1].index).mean()
        ),
    }


def aggregate_to_rank(
    counts: pd.DataFrame, lineage: pd.DataFrame, rank: str
) -> pd.DataFrame:
    """Suma los conteos de genero dentro de cada nivel del rango indicado.

    Subir de rango es una estrategia frente al efecto de lote: los niveles altos dependen
    menos de la version de la base de datos y de la profundidad con que se resuelven los
    generos raros.
    """
    if rank == "genus":
        return counts.copy()
    mapping = lineage.reindex(counts.columns)[rank]
    usable = mapping.dropna()
    # Se agrupa sobre la transpuesta: `groupby(axis=1)` esta deprecado en pandas 2.
    aggregated = counts[usable.index].T.groupby(usable).sum().T
    aggregated.index.name = counts.index.name
    aggregated.columns.name = rank
    return aggregated


# --------------------------------------------------------------------------------------
# Transformaciones de pliegue
# --------------------------------------------------------------------------------------


def no_correction(X_train, X_test, y_train, groups_train, groups_test):
    """Sin correccion: la referencia contra la que se comparan las demas."""
    return X_train, X_test


def _center_by_group(matrix: pd.DataFrame, groups: pd.Series, *, scale: bool = False) -> pd.DataFrame:
    aligned = groups.reindex(matrix.index)
    centered = matrix.sub(matrix.groupby(aligned, observed=True).transform("mean"))
    if scale:
        spread = matrix.groupby(aligned, observed=True).transform("std").replace(0, np.nan)
        centered = centered.div(spread).fillna(0.0)
    return centered


def study_center(X_train, X_test, y_train, groups_train, groups_test):
    """Centra cada estudio por su propia media en coordenadas CLR.

    En la geometria de Aitchison restar un vector en CLR equivale a perturbar la
    composicion por la inversa de la composicion media del estudio, asi que esto es el
    analogo composicional de quitar el desplazamiento de lote. No usa etiquetas.
    """
    return _center_by_group(X_train, groups_train), _center_by_group(X_test, groups_test)


def study_standardize(X_train, X_test, y_train, groups_train, groups_test):
    """Centra y escala cada estudio por su propia media y desviacion."""
    return (
        _center_by_group(X_train, groups_train, scale=True),
        _center_by_group(X_test, groups_test, scale=True),
    )


def drop_study_driven_features(ratio: float = 1.0, min_features: int = 50):
    """Descarta los taxones en que el estudio explica mas varianza que la etiqueta.

    El filtro se calcula **solo con el entrenamiento**, asi que el estudio retenido no
    interviene en la seleccion.
    """

    def transform(X_train, X_test, y_train, groups_train, groups_test):
        study_eta = eta_squared_by_feature(X_train, groups_train)
        label_eta = eta_squared_by_feature(X_train, y_train)
        keep = label_eta.index[(label_eta * ratio) >= study_eta]
        if len(keep) < min_features:
            keep = (label_eta - study_eta).nlargest(min_features).index
        return X_train[keep], X_test[keep]

    transform.__name__ = f"drop-study-driven(ratio={ratio})"
    return transform


STRATEGIES = {
    "sin-correccion": no_correction,
    "centrado-por-estudio": study_center,
    "estandarizado-por-estudio": study_standardize,
    "filtrar-taxones-de-lote": drop_study_driven_features(ratio=1.0),
}


def top_features_by_label(n: int = 50):
    """Conserva los n taxones que mas varianza de la etiqueta explican, ignorando el estudio.

    Es el control que distingue dos explicaciones de una mejora: corregir el lote, o
    simplemente reducir la dimension con seleccion supervisada.
    """

    def transform(X_train, X_test, y_train, groups_train, groups_test):
        keep = eta_squared_by_feature(X_train, y_train).nlargest(n).index
        return X_train[keep], X_test[keep]

    transform.__name__ = f"top-by-label(n={n})"
    return transform


def random_features(n: int = 50, random_state: int = 42):
    """Conserva n taxones al azar: la linea base de cualquier reduccion de dimension."""

    def transform(X_train, X_test, y_train, groups_train, groups_test):
        rng = np.random.default_rng(random_state)
        keep = rng.choice(X_train.columns.to_numpy(), size=min(n, X_train.shape[1]), replace=False)
        return X_train[keep], X_test[keep]

    transform.__name__ = f"random({n})"
    return transform


def count_surviving_features(
    X: pd.DataFrame, y: pd.Series, groups: pd.Series, *, ratio: float = 1.0
) -> dict:
    """Cuantos taxones pasan el filtro por criterio, antes de recurrir al respaldo."""
    study_eta = eta_squared_by_feature(X, groups)
    label_eta = eta_squared_by_feature(X, y)
    passing = int(((label_eta * ratio) >= study_eta).sum())
    return {
        "n_features": int(X.shape[1]),
        "pasan_el_criterio": passing,
        "fraccion": round(passing / X.shape[1], 4),
    }


CONTROL_STRATEGIES = {
    "filtrar-taxones-de-lote": drop_study_driven_features(ratio=1.0),
    "top-50-por-etiqueta": top_features_by_label(50),
    "50-taxones-al-azar": random_features(50),
}
