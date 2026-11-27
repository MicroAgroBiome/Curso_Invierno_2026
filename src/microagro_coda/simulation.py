"""Generador de datos sinteticos con la estructura de una tabla de microbioma.

El objetivo es construir un conjunto donde la diferencia entre clases viva **solo en
las log-razones** entre taxones, y donde ademas exista un factor tecnico multiplicativo
que arruine la geometria de las abundancias relativas. Asi se puede comprobar, con la
verdad conocida, que la correccion composicional no es un adorno: es lo que recupera la
senal.

Modelo generador, para la muestra i de la clase k y el taxon j:

    log a_ij = mu_j + delta_kj + eps_ij,        eps_ij ~ N(0, sigma^2)

donde `mu_j` da la curva rango-abundancia (log-normal, como en comunidades reales) y
`delta_kj` solo es distinto de cero en un subconjunto de taxones firma. Como la clase
entra de forma aditiva en el logaritmo, es una **perturbacion en el simplex**: cambia
las razones entre taxones, no su escala.

Encima se anade un taxon dominante cuyo logaritmo varia muchisimo y es independiente de
la clase:

    log a_i0 = nu_i,        nu_i ~ N(mu_nu, sigma_nu^2),   sigma_nu >> sigma

Imita lo que en los datos reales hace la fraccion sin clasificar o el ADN del hospedero,
que va del 4 % al 95 % entre muestras. Por ultimo se cierra y se muestrea:

    x_i = C(a_i) = a_i / sum_j a_ij
    c_i ~ Multinomial(N_i, x_i)

con `N_i` log-uniforme en varios ordenes de magnitud. El muestreo multinomial a
profundidad finita es lo que produce los ceros, igual que en los datos reales: un taxon
raro no se observa porque no le tocaron lecturas, no porque este ausente.

Por que el CLR lo arregla. El CLR de la composicion no depende del total:

    clr(x)_j = log a_ij - (1/D) sum_l log a_il

asi que el taxon dominante entra con peso 1/D, despreciable cuando D es grande. En
cambio en abundancia relativa, si a_i0 domina el total, x_ij ~= a_ij / exp(nu_i): el
ruido tecnico se vuelve un **factor multiplicativo** que infla la varianza de cada taxon
en escala lineal y entierra la diferencia entre clases.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd


@dataclass
class SimulationConfig:
    """Parametros del generador. Los valores por omision imitan el subconjunto real."""

    n_per_class: int = 300
    classes: tuple[str, ...] = ("Clase A", "Clase B", "Clase C")
    n_taxa: int = 500
    n_signature: int = 30
    effect_size: float = 1.6          # magnitud de delta_kj, en logaritmo natural
    biological_sd: float = 2.0        # sigma: variabilidad entre muestras de una clase
    abundance_sd: float = 3.5         # dispersion de la curva rango-abundancia
    nuisance_sd: float = 3.0          # sigma_nu: variabilidad del taxon dominante
    nuisance_mean: float = 4.0        # mu_nu, relativo a la media de mu_j
    depth_log10_range: tuple[float, float] = (5.0, 7.0)
    random_state: int = 42
    metadata: dict = field(default_factory=dict)


@dataclass
class SimulatedDataset:
    """Lo observable mas la verdad subyacente, que en datos reales no se tiene."""

    counts: pd.DataFrame            # muestras x taxones, conteos enteros
    labels: pd.Series               # clase de cada muestra
    absolute: pd.DataFrame          # abundancias absolutas latentes
    signature_taxa: list[str]       # taxones en que las clases difieren de verdad
    nuisance_taxon: str             # taxon dominante, independiente de la clase
    nuisance_value: pd.Series       # nu_i, el factor tecnico latente
    library_size: pd.Series         # N_i, profundidad de cada muestra
    config: SimulationConfig

    def summary(self) -> pd.Series:
        """Cifras que describen la tabla generada, para compararlas con las reales."""
        counts = self.counts
        present = counts > 0
        return pd.Series({
            "muestras": counts.shape[0],
            "taxones": counts.shape[1],
            "clases": int(self.labels.nunique()),
            "taxones firma": len(self.signature_taxa),
            "fraccion de ceros": round(float(1 - present.to_numpy().mean()), 4),
            "prevalencia mediana": round(float(present.mean(axis=0).median()), 4),
            "taxones en <30% de las muestras": int((present.mean(axis=0) < 0.30).sum()),
            "profundidad minima": int(self.library_size.min()),
            "profundidad mediana": int(self.library_size.median()),
            "profundidad maxima": int(self.library_size.max()),
            "ordenes de magnitud de profundidad": round(
                float(np.log10(self.library_size.max() / self.library_size.min())), 2
            ),
            "peso maximo del taxon dominante": round(
                float((counts[self.nuisance_taxon] / counts.sum(axis=1)).max()), 4
            ),
            "peso minimo del taxon dominante": round(
                float((counts[self.nuisance_taxon] / counts.sum(axis=1)).min()), 4
            ),
        })


def simulate_microbiome(config: SimulationConfig | None = None) -> SimulatedDataset:
    """Genera la tabla sintetica descrita en el encabezado del modulo."""
    config = config or SimulationConfig()
    rng = np.random.default_rng(config.random_state)

    n_classes = len(config.classes)
    n_samples = config.n_per_class * n_classes
    taxa = [f"Taxon-{index:03d}" for index in range(config.n_taxa)]
    samples = pd.Index([f"S{index:04d}" for index in range(n_samples)], name="sample")
    labels = pd.Series(
        np.repeat(list(config.classes), config.n_per_class), index=samples, name="label"
    )

    # 1. Curva rango-abundancia: unos pocos taxones abundantes y una cola larga de raros.
    mu = rng.normal(0.0, config.abundance_sd, size=config.n_taxa)
    mu = np.sort(mu)[::-1]

    # 2. Firma de clase: delta_kj distinto de cero solo en `n_signature` taxones.
    #    Se eligen de la zona media del ranking: ni dominantes ni practicamente ausentes.
    middle = np.arange(config.n_taxa // 6, config.n_taxa // 6 + config.n_taxa // 2)
    signature_index = rng.choice(middle, size=config.n_signature, replace=False)
    delta = np.zeros((n_classes, config.n_taxa))
    for position, taxon in enumerate(signature_index):
        # Cada taxon firma sube en una clase y baja en las demas: es una perturbacion.
        favoured = position % n_classes
        delta[:, taxon] = -config.effect_size / (n_classes - 1)
        delta[favoured, taxon] = config.effect_size

    # 3. Taxon dominante con variabilidad tecnica, independiente de la clase.
    nuisance_position = 0
    mu[nuisance_position] = mu.mean() + config.nuisance_mean
    delta[:, nuisance_position] = 0.0

    class_index = np.repeat(np.arange(n_classes), config.n_per_class)
    log_absolute = (
        mu[None, :]
        + delta[class_index]
        + rng.normal(0.0, config.biological_sd, size=(n_samples, config.n_taxa))
    )
    nuisance_value = rng.normal(0.0, config.nuisance_sd, size=n_samples)
    log_absolute[:, nuisance_position] += nuisance_value

    absolute = np.exp(log_absolute)
    composition = absolute / absolute.sum(axis=1, keepdims=True)

    # 4. Profundidad log-uniforme y muestreo multinomial: de ahi salen los ceros.
    low, high = config.depth_log10_range
    library_size = np.power(10, rng.uniform(low, high, size=n_samples)).astype(int)
    counts = np.vstack([
        rng.multinomial(size, probabilities)
        for size, probabilities in zip(library_size, composition)
    ])

    return SimulatedDataset(
        counts=pd.DataFrame(counts, index=samples, columns=taxa).rename_axis("sample"),
        labels=labels,
        absolute=pd.DataFrame(absolute, index=samples, columns=taxa).rename_axis("sample"),
        signature_taxa=[taxa[index] for index in sorted(signature_index)],
        nuisance_taxon=taxa[nuisance_position],
        nuisance_value=pd.Series(nuisance_value, index=samples, name="nuisance"),
        library_size=pd.Series(library_size, index=samples, name="library_size"),
        config=config,
    )


def log_pseudocount(relative: pd.DataFrame, pseudocount: float | None = None) -> pd.DataFrame:
    """log(x + c) sin centrar: el paso intermedio entre la abundancia relativa y el CLR.

    Sirve para separar dos efectos que suelen confundirse: tomar logaritmo (que convierte
    el ruido multiplicativo en aditivo) y **centrar por la media geometrica** (que es lo
    que elimina ese ruido aditivo comun y da la geometria de Aitchison).
    """
    if pseudocount is None:
        positive = relative.to_numpy()[relative.to_numpy() > 0]
        pseudocount = positive.min() / 2 if positive.size else 1e-9
    return np.log(relative + pseudocount)
