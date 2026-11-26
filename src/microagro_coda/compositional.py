"""Diagnostico de composicionalidad y cadena de correccion de la tesis.

La cadena reproduce el orden documentado en `tesis_maestria/escrito/metodologia.tex`
(seccion `sec:transformaciones`): amalgamacion de generos poco frecuentes, reclausura
modificada, correccion de ceros con pseudoconteo minimo, y transformacion CLR.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

OTHER_NAME = "other-genera"


# --------------------------------------------------------------------------------------
# Diagnostico: mostrar que los datos son composicionales ANTES de procesarlos
# --------------------------------------------------------------------------------------


def genus_mass_summary(relative_to_total: pd.Series) -> pd.Series:
    """Resume la masa de genero por muestra sobre el total de lecturas.

    Es el punto de partida del argumento composicional: cada muestra es una parte de
    un total fijo, y ese total observado no es el mismo entre muestras.
    """
    description = relative_to_total.describe()
    description["iqr"] = description["75%"] - description["25%"]
    description["max_over_min"] = description["max"] / description["min"]
    return description.rename("genus_mass")


def library_size_summary(sizes: pd.Series) -> pd.Series:
    """Resume la profundidad por muestra y su rango en ordenes de magnitud."""
    description = sizes.describe()
    description["max_over_min"] = description["max"] / description["min"]
    description["log10_range"] = np.log10(description["max"] / description["min"])
    return description.rename("library_size")


def closure_check(relative: pd.DataFrame, *, n_parts: int = 50) -> dict:
    """Comprueba la restriccion de suma constante y la singularidad que induce.

    Se arma una composicion cerrada de `n_parts` generos mas una categoria resto, de
    modo que el numero de partes sea mucho menor que el numero de muestras: asi la
    deficiencia de rango que se observa viene del cierre y no de que falten muestras.
    """
    top = relative.sum(axis=0).nlargest(n_parts).index
    composition = relative[top].copy()
    composition[OTHER_NAME] = 1.0 - composition.sum(axis=1)

    row_sums = composition.sum(axis=1)
    eigenvalues = np.linalg.eigvalsh(np.cov(composition.to_numpy(), rowvar=False))
    eigenvalues = np.sort(eigenvalues)[::-1]
    tolerance = eigenvalues[0] * composition.shape[1] * np.finfo(float).eps

    return {
        "n_parts": composition.shape[1],
        "n_samples": composition.shape[0],
        "row_sum_min": float(row_sums.min()),
        "row_sum_max": float(row_sums.max()),
        "rows_sum_to_one": bool(np.allclose(row_sums, 1.0)),
        "covariance_rank": int((eigenvalues > tolerance).sum()),
        "smallest_eigenvalue": float(eigenvalues[-1]),
        "largest_eigenvalue": float(eigenvalues[0]),
    }


def spurious_correlation_demo(
    relative: pd.DataFrame,
    clr: pd.DataFrame,
    *,
    max_genera: int = 300,
    random_state: int = 42,
) -> pd.DataFrame:
    """Compara las correlaciones de Pearson entre generos: cerradas frente a CLR.

    Sobre datos cerrados aparece el sesgo negativo que fuerza la suma constante (el
    argumento de Pearson 1897): si un genero sube, los demas tienen que bajar aunque
    no exista ninguna relacion biologica.
    """
    shared = relative.columns.intersection(clr.columns)
    rng = np.random.default_rng(random_state)
    if len(shared) > max_genera:
        shared = pd.Index(rng.choice(shared.to_numpy(), size=max_genera, replace=False))

    records = []
    for name, matrix in (("closed", relative[shared]), ("clr", clr[shared])):
        values = matrix.to_numpy(dtype=float)
        values = values[:, values.std(axis=0) > 0]
        correlation = np.corrcoef(values, rowvar=False)
        upper = correlation[np.triu_indices_from(correlation, k=1)]
        records.append(
            {
                "representation": name,
                "n_genera": values.shape[1],
                "n_pairs": upper.size,
                "mean_correlation": float(upper.mean()),
                "median_correlation": float(np.median(upper)),
                "fraction_negative": float((upper < 0).mean()),
            }
        )
    return pd.DataFrame(records).set_index("representation")


def spurious_correlation_values(
    relative: pd.DataFrame,
    clr: pd.DataFrame,
    *,
    max_genera: int = 300,
    random_state: int = 42,
) -> dict[str, np.ndarray]:
    """Devuelve las correlaciones por par para graficarlas como histograma."""
    shared = relative.columns.intersection(clr.columns)
    rng = np.random.default_rng(random_state)
    if len(shared) > max_genera:
        shared = pd.Index(rng.choice(shared.to_numpy(), size=max_genera, replace=False))

    output = {}
    for name, matrix in (("closed", relative[shared]), ("clr", clr[shared])):
        values = matrix.to_numpy(dtype=float)
        values = values[:, values.std(axis=0) > 0]
        correlation = np.corrcoef(values, rowvar=False)
        output[name] = correlation[np.triu_indices_from(correlation, k=1)]
    return output


def subcompositional_incoherence_demo(
    relative: pd.DataFrame,
    *,
    pair: tuple[str, str] | None = None,
    subset_sizes: tuple[int, ...] = (5, 10, 25, 50, 100, 250),
    n_draws: int = 30,
    random_state: int = 42,
) -> pd.DataFrame:
    """Muestra que la correlacion entre dos generos depende de quien mas este en la tabla.

    Para cada tamano de subcomposicion se extraen `n_draws` subconjuntos al azar que
    contienen al par, se recierran, y se mide la correlacion de Pearson de las
    abundancias relativas y la varianza de la log-razon del par. La correlacion se
    mueve con el subconjunto; la log-razon es exactamente invariante, que es justo la
    propiedad de coherencia subcomposicional que motiva trabajar en log-razones.
    """
    positive = relative.loc[:, (relative > 0).all(axis=0)]
    if positive.shape[1] < max(subset_sizes):
        raise ValueError("No hay suficientes generos presentes en todas las muestras.")

    if pair is None:
        pair = tuple(positive.sum(axis=0).nlargest(2).index)
    first, second = pair
    others = positive.columns.difference(list(pair))

    rng = np.random.default_rng(random_state)
    records = []
    for size in subset_sizes:
        for draw in range(n_draws):
            chosen = rng.choice(others.to_numpy(), size=size - 2, replace=False)
            block = positive[[first, second, *chosen]]
            closed = block.div(block.sum(axis=1), axis=0)
            log_ratio = np.log(closed[first] / closed[second])
            records.append(
                {
                    "subset_size": size,
                    "draw": draw,
                    "pearson_closed": float(closed[first].corr(closed[second])),
                    "log_ratio_variance": float(log_ratio.var(ddof=1)),
                }
            )
    frame = pd.DataFrame(records)
    frame.attrs["pair"] = pair
    return frame


def compositionality_report(
    counts: pd.DataFrame,
    relative: pd.DataFrame,
    genus_mass: pd.Series,
    clr: pd.DataFrame,
) -> pd.DataFrame:
    """Reune los diagnosticos en una tabla unica para el reporte y el documento."""
    sizes = counts.sum(axis=1)
    closure = closure_check(relative)
    correlations = spurious_correlation_demo(relative, clr)
    incoherence = subcompositional_incoherence_demo(relative)

    records = {
        "n_samples": counts.shape[0],
        "n_genera": counts.shape[1],
        "genus_mass_min": float(genus_mass.min()),
        "genus_mass_median": float(genus_mass.median()),
        "genus_mass_max": float(genus_mass.max()),
        "library_size_min": float(sizes.min()),
        "library_size_median": float(sizes.median()),
        "library_size_max": float(sizes.max()),
        "library_size_log10_range": float(np.log10(sizes.max() / sizes.min())),
        "closure_parts": closure["n_parts"],
        "closure_rows_sum_to_one": closure["rows_sum_to_one"],
        "closure_covariance_rank": closure["covariance_rank"],
        "mean_correlation_closed": float(correlations.loc["closed", "mean_correlation"]),
        "mean_correlation_clr": float(correlations.loc["clr", "mean_correlation"]),
        "fraction_negative_closed": float(correlations.loc["closed", "fraction_negative"]),
        "fraction_negative_clr": float(correlations.loc["clr", "fraction_negative"]),
        "incoherence_pair": " / ".join(incoherence.attrs["pair"]),
        "pearson_closed_spread": float(
            incoherence.groupby("subset_size")["pearson_closed"].mean().max()
            - incoherence.groupby("subset_size")["pearson_closed"].mean().min()
        ),
        "log_ratio_variance_spread": float(
            incoherence["log_ratio_variance"].max() - incoherence["log_ratio_variance"].min()
        ),
    }
    return pd.Series(records, name="value").to_frame()


# --------------------------------------------------------------------------------------
# Cadena de correccion composicional de la tesis
# --------------------------------------------------------------------------------------


def amalgamate_rare_genera(
    matrix: pd.DataFrame,
    *,
    min_prevalence: float = 0.30,
    other_name: str = OTHER_NAME,
) -> pd.DataFrame:
    """Paso 1: amalgama en una sola columna los generos poco prevalentes.

    El escrito define el conjunto a amalgamar como los generos presentes en menos del
    30 % de las muestras (`metodologia.tex`, ec. de `sec:transformaciones`).
    """
    if not 0.0 <= min_prevalence <= 1.0:
        raise ValueError("min_prevalence debe estar entre 0 y 1.")
    prevalence = (matrix > 0).mean(axis=0)
    rare = prevalence.index[prevalence < min_prevalence]

    result = matrix.drop(columns=rare)
    result[other_name] = matrix[rare].sum(axis=1) if len(rare) else 0.0
    return result


def reclose_modified(
    matrix: pd.DataFrame,
    *,
    total: float = 1.0,
    other_name: str = OTHER_NAME,
    tolerance: float = 1e-9,
) -> pd.DataFrame:
    """Paso 2: la masa faltante va exclusivamente a la categoria resto, sin repartir.

    Cuando no se amalgama ningun taxon la categoria resto vale cero, y el residuo de punto
    flotante del cierre puede dejarla en -1e-16. Eso se recorta a cero; solo se considera
    un error si el deficit supera `tolerance`, que si indicaria que la matriz no estaba
    cerrada al total que se declara.
    """
    result = matrix.copy()
    if other_name not in result.columns:
        result[other_name] = 0.0
    missing = total - result.sum(axis=1)
    result[other_name] = result[other_name] + missing

    negative = result[other_name] < 0
    if negative.any():
        worst = float(result.loc[negative, other_name].min())
        if worst < -tolerance * total:
            raise ValueError(
                f"La categoria resto quedo negativa en {int(negative.sum())} muestras "
                f"(minimo {worst:.3g}): la matriz excede el total."
            )
        result.loc[negative, other_name] = 0.0
    return result


def replace_zeros_preserving_total(
    matrix: pd.DataFrame,
    *,
    variant: str = "escrito",
) -> pd.DataFrame:
    """Paso 3: sustituye ceros por un pseudoconteo minimo conservando la suma.

    `escrito` usa c = min{x > 0} sobre toda la matriz y descuenta delta_i = n_i*c/p_i
    de cada entrada originalmente no cero de la muestra i, tal como se define en
    `metodologia.tex`. `notebook` reproduce la variante del codigo de la tesis, con
    c = min/2 y la correccion repartida entre todas las columnas.
    """
    values = matrix.to_numpy(dtype=float)
    if (values < 0).any():
        raise ValueError("La matriz trae valores negativos.")

    positive = values[values > 0]
    if positive.size == 0:
        raise ValueError("La matriz no tiene ningun valor positivo.")
    minimum = positive.min()

    zero_mask = values == 0
    zeros_per_sample = zero_mask.sum(axis=1)
    nonzeros_per_sample = values.shape[1] - zeros_per_sample

    if variant == "escrito":
        pseudocount = minimum
        with np.errstate(divide="ignore", invalid="ignore"):
            delta = np.where(nonzeros_per_sample > 0, zeros_per_sample * pseudocount / nonzeros_per_sample, 0.0)
        adjusted = np.where(zero_mask, pseudocount, values - delta[:, None])
    elif variant == "notebook":
        pseudocount = minimum / 2
        delta = zeros_per_sample * pseudocount / values.shape[1]
        adjusted = np.where(zero_mask, pseudocount, values) - delta[:, None]
    else:
        raise ValueError(f"Variante desconocida: {variant}")

    result = pd.DataFrame(adjusted, index=matrix.index, columns=matrix.columns)
    if (result <= 0).any().any():
        raise ValueError(
            "Quedaron valores no positivos tras tratar los ceros; "
            "revisa la amalgamacion o usa variant='notebook'."
        )
    result.attrs["pseudocount"] = float(pseudocount)
    return result


def clr_transform(data: pd.DataFrame) -> pd.DataFrame:
    """Paso 4: CLR por filas. Los ceros ya fueron tratados, no se anade pseudoconteo."""
    if (data <= 0).any().any():
        raise ValueError("CLR requiere valores positivos despues de corregir los ceros.")
    log_values = np.log(data.astype(float))
    return log_values.sub(log_values.mean(axis=1), axis=0)


def compositional_chain(
    relative: pd.DataFrame,
    *,
    min_prevalence: float = 0.30,
    total: float = 1.0,
    variant: str = "escrito",
) -> dict[str, pd.DataFrame]:
    """Corre los cuatro pasos y devuelve cada etapa intermedia.

    `amalgamated` es la representacion sin CLR que se usa como comparacion en la
    clasificacion: mismas columnas y mismas muestras, sin transformar.
    """
    amalgamated = amalgamate_rare_genera(relative, min_prevalence=min_prevalence)
    reclosed = reclose_modified(amalgamated, total=total)
    treated = replace_zeros_preserving_total(reclosed, variant=variant)
    clr = clr_transform(treated)
    return {
        "amalgamated": reclosed,
        "treated": treated,
        "clr": clr,
    }
