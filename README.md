# Diferencias estadísticas y topológicas en la comunidad microbiana de suelos

[![Libro del curso](https://img.shields.io/badge/📖_Libro-en_línea-1f6feb)](https://microagrobiome.github.io/Curso_Invierno_2026/)
[![Hecho con Quarto](https://img.shields.io/badge/Hecho_con-Quarto-75AADB)](https://quarto.org/)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB)](https://www.python.org/)
[![Licencia: CC BY-NC-SA 4.0](https://img.shields.io/badge/Licencia-CC_BY--NC--SA_4.0-lightgrey)](https://creativecommons.org/licenses/by-nc-sa/4.0/deed.es)

Curso del proyecto **MicroAgroBiome** en la [**Segunda Escuela Michoacana de Biología Matemática**](https://matmor.unam.mx/embm-2026/) (Centro de Ciencias Matemáticas, UNAM).

**📖 Todo el material está en el libro del curso:** [Curso de Invierno 2026](https://microagrobiome.github.io/Curso_Invierno_2026/)

## Información del curso

| | |
|---|---|
| 📆 **Fechas** | 30 de noviembre al 5 de diciembre de 2026 (sin sesión el miércoles 2) |
| 🕒 **Horario** | Lunes, martes, jueves y viernes, 15:00–18:30 h (receso 16:30–17:00 h) · Sábado 5, 9:00–12:30 h (presentaciones) · Hora de la Ciudad de México |
| ⏱️ **Duración** | 12 horas |
| 🏢 **Modalidad** | Híbrida · Centro de Ciencias Matemáticas, UNAM |
| 🗣️ **Idioma** | Español |
| 🐍 **Lenguaje** | Python, en Google Colab (sin instalación) o en tu computadora |

### Descripción

Los microorganismos que viven alrededor de las raíces de las plantas (la **rizósfera**) forman comunidades enormemente diversas que no se pueden cultivar en el laboratorio: se estudian secuenciando todo su ADN (**metagenómica**). El resultado es una tabla con miles de taxones por muestra, y la pregunta central es cómo comparar esas comunidades: ¿cuándo dos comunidades son realmente distintas y qué explica esa diferencia?

En este curso respondemos esa pregunta con **datos reales** de la base de datos [MicroAgroBiome](https://agrobiom.matmor.unam.mx/), combinando dos enfoques:

- **Estadístico:** diversidad, pruebas de hipótesis, distancias entre comunidades, ordenación, clustering y transformaciones composicionales.
- **Topológico:** redes de coocurrencia y análisis topológico de datos (TDA).

### Objetivo

Desarrollar habilidades para identificar y cuantificar diferencias estadísticas y topológicas entre comunidades microbianas usando herramientas de análisis de datos y topología aplicada.

### ¿A quién va dirigido?

A estudiantes y profesionales de biología, matemáticas, ciencias de datos y áreas afines que quieran analizar datos de microbiomas. **No se requiere experiencia previa con microbiomas**: cada concepto (tabla de abundancia, diversidad, distancia entre comunidades) se introduce antes de usarlo.

### Requisitos previos

- Estadística básica: media, varianza, pruebas de hipótesis.
- Python básico: ejecutar celdas, usar variables y listas. **No** hace falta saber escribir funciones.
- Una cuenta de Google para trabajar en Google Colab, o Python ≥ 3.10 instalado localmente.
- Antes de la primera sesión: leer la [Dinámica de trabajo](https://microagrobiome.github.io/Curso_Invierno_2026/dinamica_trabajo.html) y verificar que el notebook del capítulo *Introducción a los datos* abre y su celda de Setup se ejecuta.

## Instructores

| Instructor | Institución | Sesiones |
|---|---|---|
| Dra. Nelly Sélem Mojica | - | Introducción · Transformación composicional |
| MC. Rafael Pérez-Estrada | ENES-Morelia, UNAM | Introducción · Transformación composicional |
| MC. David Alberto García Estrada | Centro de Investigación en Materiales Avanzados (CIMAV) | Introducción a los datos · Clustering |
| Dra. Haydeé Peruyero | ENES-Juriquilla, UNAM | Redes y TDA |
| Dr. Manuel Alejandro Ucan Puc | Escuela de Ingeniería y Ciencias, Tecnológico de Monterrey | Redes y TDA |

## Programa

| Día | Tema |
|---|---|
| **Lunes 30** | Bienvenida · Mapa del tesoro · Pruebas de hipótesis · Introducción a los datos · Inicio del proyecto |
| **Martes 1** | Transformación composicional · Proyecto |
| **Jueves 3** | Técnicas de clustering · Proyecto |
| **Viernes 4** | Redes de coocurrencia y TDA · Integración del proyecto |
| **Sábado 5** | Presentaciones de los proyectos por equipo |

La agenda por horas está en el libro: [Información general → Agenda](https://microagrobiome.github.io/Curso_Invierno_2026/index.html#agenda).

## Materiales

| Capítulo | Tipo | Notebook |
|---|---|---|
| 1 · [Mapa del tesoro: la ruta de la rizósfera](https://microagrobiome.github.io/Curso_Invierno_2026/mapa_del_tesoro.html) | Actividad interactiva | — |
| 2 · [Introducción a los datos](https://microagrobiome.github.io/Curso_Invierno_2026/intro_datos.html) | Lección con notebook | [![Abrir en Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/MicroAgroBiome/Curso_Invierno_2026/blob/main/notebooks/participante/intro_datos.ipynb) |
| 3 · [Pruebas de hipótesis en microbiomas](https://microagrobiome.github.io/Curso_Invierno_2026/pruebas_hipotesis.html) | Actividad interactiva (datos simulados) | — |
| 4 · [Transformación composicional](https://microagrobiome.github.io/Curso_Invierno_2026/composicional.html) | Lección con notebook | [![Abrir en Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/MicroAgroBiome/Curso_Invierno_2026/blob/main/notebooks/composicional_transformacion.ipynb) |
| 5 · [Técnicas de clustering](https://microagrobiome.github.io/Curso_Invierno_2026/clustering.html) | Lección con notebook | [![Abrir en Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/MicroAgroBiome/Curso_Invierno_2026/blob/main/notebooks/participante/clustering.ipynb) |
| [Proyecto del curso](https://microagrobiome.github.io/Curso_Invierno_2026/proyecto.html) | Trabajo en equipo | [![Abrir en Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/MicroAgroBiome/Curso_Invierno_2026/blob/main/notebooks/proyecto_maiz.ipynb) |

⚐ Falta el capítulo de redes y TDA (viernes).

### Cómo se enseña

Las lecciones con notebook siguen la **codificación en vivo participativa** de [The Carpentries](https://carpentries.org/): el instructor escribe el código en pantalla y los participantes lo escriben al mismo tiempo. Por eso hay dos versiones de cada notebook:

- **Notebook del participante** (`notebooks/participante/`): las celdas que se escriben en clase vienen vacías, con un comentario guía `# ⌨️`. Hay celdas de rescate **🛟** para ponerse al día si alguien se atrasa. **Es el que se abre en clase.**
- **Notebook completo** (`notebooks/`): todo el código ejecutado, con sus figuras. Es la fuente del libro y sirve de referencia.

Los ejercicios no piden escribir código desde cero: se completa una línea, se cambia un parámetro o se interpreta un resultado. Las soluciones están en el libro.

### Proyecto

En equipos (parejas), los participantes responden: **¿qué tan parecido es el microbioma de la rizósfera del maíz entre estudios distintos?** Cada día, la última media hora a una hora se dedica al proyecto. Cada equipo entrega un reporte y da una presentación de 10 minutos el sábado. Detalles: [Proyecto del curso](https://microagrobiome.github.io/Curso_Invierno_2026/proyecto.html).

## Datos

Todos los datos son subconjuntos de la base de datos [MicroAgroBiome](https://agrobiom.matmor.unam.mx/): metagenomas de rizósfera de cultivos, con conteos de lecturas por género.

| Archivo | Uso | Contenido |
|---|---|---|
| `datos/subset.zip` | Lecciones en clase | 75 metagenomas · 3330 géneros · 21 columnas de metadatos |
| `datos/subset_proyecto.zip` | Proyecto | 41 metagenomas de rizósfera de maíz (*Zea mays*) de 6 estudios (Sudáfrica y Estados Unidos) |
| `datos/composicional.zip` | Transformación composicional (caso real) | 550 metagenomas · 4611 géneros: conteos, metadatos, calidad y linaje; el caso real usa 15 muestras de agaves y cactus (rizósfera y filósfera) |

`subset.zip` y `subset_proyecto.zip` incluyen la lista de muestras y el registro de cómo se generó (`taller_samples.csv`, `subset_log.txt`), para que el subconjunto sea reproducible con `scripts/02_make_subset.py`. **No hace falta descargarlos a mano**: la celda de Setup de cada notebook los descarga y descomprime.

## Ejecutar los notebooks

### En Google Colab (recomendado)

Usa los botones **Open in Colab** de la tabla de materiales o del libro. Guarda una copia en tu Drive (*Archivo → Guardar una copia en Drive*) y ejecuta la celda de Setup.

### En tu computadora

```bash
git clone https://github.com/MicroAgroBiome/Curso_Invierno_2026.git
cd Curso_Invierno_2026
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Abre `notebooks/participante/intro_datos.ipynb` en VSCode o Jupyter y ejecuta la celda de Setup: debe mostrar `Entorno: Local (VSCode)`.

Librerías principales: `pandas`, `numpy`, `scikit-bio`, `biom-format`, `scikit-learn`, `scipy`, `matplotlib`, `seaborn` (versiones en `requirements.txt`).

## Estructura del repositorio

```
├── _quarto.yml              # Configuración del libro (capítulos, autores, formato)
├── _variables.yml           # URL del repositorio para los botones de Colab (un solo lugar)
├── index.qmd                # Información general, agenda, requisitos, citar
├── dinamica_trabajo.qmd     # Dinámica de clase; guía para instructores
├── proyecto.qmd             # Proyecto del curso
├── mapa_del_tesoro.qmd      # Actividad interactiva
├── intro_datos.qmd          # Introducción a los datos
├── pruebas_hipotesis.qmd    # Actividad interactiva
├── clustering.qmd           # Clustering
├── interactivos/            # Páginas HTML de las actividades interactivas
├── notebooks/
│   ├── intro_datos.ipynb   # Notebook completo (fuente; ejecutado)
│   ├── clustering.ipynb
│   ├── proyecto_maiz.ipynb                  # Notebook inicial del proyecto
│   └── participante/                        # Notebooks del participante (GENERADOS)
├── datos/                   # subset.zip, subset_proyecto.zip
├── scripts/
│   ├── 02_make_subset.py                 # Genera los subconjuntos de datos
│   ├── 03_variables_por_studio.py        # Explora las variables de metadatos por estudio
│   └── generar_notebook_participante.py  # Genera notebooks/participante/
├── logos/, styles.css, references.bib
├── requirements.txt
└── docs/                    # Libro renderizado (GitHub Pages) — NO editar a mano
```

## Contribuir (instructores)

El flujo completo está en el libro: [Dinámica de trabajo → Para instructores](https://microagrobiome.github.io/Curso_Invierno_2026/dinamica_trabajo.html#para-instructores-cómo-se-produce-el-material). Resumen:

1. Trabaja en **tu propia rama**; los cambios llegan a `main` por *pull request*.
2. El **notebook completo** es la única fuente. Edítalo, **ejecútalo completo** y genera la versión del participante:

   ```bash
   jupyter nbconvert --to notebook --execute --inplace --allow-errors notebooks/intro_datos.ipynb
   python scripts/generar_notebook_participante.py notebooks/intro_datos.ipynb
   ```

   Las celdas de ejercicio fallan a propósito (`TU_CODIGO_AQUI`); por eso se usa `--allow-errors`.
3. Nunca edites `notebooks/participante/` a mano.
4. Revisa con `quarto preview`. El libro **no ejecuta código**: usa `{{< embed >}}` con las salidas guardadas, así que renderizar no requiere Python ni los datos.
5. **No hagas commit de `docs/`** en tu rama. Antes de cada commit:

   ```bash
   git restore docs/ && git clean -fd docs/
   ```

   El render que se publica se hace solo en `main`, después del merge.
6. Para probar los botones de Colab antes del merge, cambia `blob/main/` por `blob/<tu-rama>/` en la URL (sin modificar `_variables.yml`).
7. Para generar otro subconjunto de datos usa `scripts/02_make_subset.py` con su propio `--out-dir`, para no sobrescribir `datos/subset/`.

## Cómo citar

**Los datos:** si usas los datos, cita el artículo de MicroAgroBiome:

> Aguilar C, Fontove-Herrera F, Pashkov A, García-Estrada DA, Contreras-Peruyero H, Guerrero-Flores S, Ramírez-Sánchez O, Sélem-Mojica N. *MicroAgroBiome: a toolkit for exploring specialized metabolism and ecological interactions in rhizosphere microbiomes of cultivated crops.* **Nucleic Acids Research** 54(D1): D1743–D1752 (2026). [doi:10.1093/nar/gkaf1083](https://doi.org/10.1093/nar/gkaf1083)

**El material del curso:**

> Sélem-Mojica N, Pérez-Estrada R, Peruyero H, García-Estrada DA, Ucan-Puc MA. *Diferencias estadísticas y topológicas en comunidades microbianas.* Segunda Escuela Michoacana de Biología Matemática, Centro de Ciencias Matemáticas, UNAM (2026). <https://microagrobiome.github.io/Curso_Invierno_2026/>

## Financiamiento

Este curso forma parte del proyecto de Ciencia de Frontera **CBF-2026-992 "MicroAgroBiome 2.0: un atlas evolutivo del metabolismo especializado en microbiomas de cultivos"**, financiado por SECIHTI.

## Licencia

El material del curso se puede reutilizar y adaptar con la debida atribución, bajo la licencia [Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0)](https://creativecommons.org/licenses/by-nc-sa/4.0/deed.es).
