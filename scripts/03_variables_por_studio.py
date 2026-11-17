# Qué variables del metadata cambian DENTRO de cada estudio grande
# (rizósfera, WGS); solo esas permiten comparar sin confusión con el estudio
import pandas as pd

meta = pd.read_csv("datos/agrobiomData/full_metadata.csv", low_memory=False)
meta = meta.drop_duplicates("sample")                      # una fila por muestra (el CSV trae una por BGC)
meta = meta[(meta["assay_type"] == "WGS") & (meta["plant_part"] == "Rhizosphere")]

per_bgc = {"sample", "bgc", "anchor", "bin", "completeness", "contamination",
           "closest_taxon", "closest_ani", "closest_reference"}   # columnas por BGC, no por muestra

for doi, study in meta.groupby("doi"):
    if len(study) >= 15:                                    # solo estudios con muestras suficientes
        varying = {c: study[c].nunique() for c in study.columns
                   if c not in per_bgc and study[c].nunique() > 1}
        print(f"\n{doi}  ({len(study)} muestras)\n  varían: {varying}")