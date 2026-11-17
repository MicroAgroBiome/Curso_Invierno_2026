"""
Genera el notebook del PARTICIPANTE a partir del notebook COMPLETO (la fuente única).

Uso (desde la raíz del repo):
    python scripts/generar_notebook_participante.py notebooks/leccion_1_introduccion_datos.ipynb

Escribe:  notebooks/participante/<mismo nombre>.ipynb

Qué hace, según las etiquetas de celda (metadata.tags) del notebook completo:
    teclear    -> la celda queda vacía; solo conserva su comentario guía '# ⌨️ ...'
    rescate    -> se llena con el código de TODAS las celdas 'estado' anteriores,
                  para recrear las variables de quien se atrasó (🛟 Ponerse al día)
    solucion   -> se elimina (las soluciones están en el libro)
    instructor -> se elimina (notas solo para instructores)
Además, en todas las celdas de código: quita las líneas '#|' de Quarto y borra las salidas.

El notebook completo NO se modifica.
"""
import argparse
import ast
import sys
import textwrap
from pathlib import Path

import nbformat

GUIDE_PREFIX = "# ⌨️"          # comentario guía de las celdas 'teclear'
DROP_TAGS = {"solucion", "instructor"}


def tags_of(cell):
    return set(cell.get("metadata", {}).get("tags", []))


def strip_quarto_options(source):
    """Quita las líneas '#| opción: valor' (solo sirven para el libro)."""
    return "\n".join(l for l in source.splitlines() if not l.lstrip().startswith("#|")).strip("\n")


def guide_only(source, where):
    """Para celdas 'teclear': conserva solo el comentario guía y deja espacio para escribir."""
    guide = [l for l in source.splitlines() if l.startswith(GUIDE_PREFIX)]
    if not guide:
        sys.exit(f"ERROR en {where}: celda 'teclear' sin comentario guía '{GUIDE_PREFIX} ...'")
    return "\n".join(guide) + "\n"


def rescue_source(state_blocks):
    """Celda 🛟: ejecuta en silencio el código de las celdas 'estado' anteriores."""
    body = "\n\n".join(state_blocks)
    return (
        "#@title 🛟 Ponerse al día: ejecútala SOLO si te atrasaste o algo falló arriba\n"
        "# Recrea las variables de las celdas anteriores. Si reiniciaste el entorno,\n"
        "# ejecuta primero las celdas de Setup.\n"
        "import contextlib, io\n"
        "with contextlib.redirect_stdout(io.StringIO()):   # silencia los print intermedios\n"
        + textwrap.indent(body, "    ") + "\n"
        'print("✅ Listo: ya puedes continuar desde aquí.")\n'
    )


def build(complete_path, out_path):
    nb = nbformat.read(complete_path, as_version=4)
    state_blocks, new_cells, counts = [], [], {"teclear": 0, "rescate": 0, "eliminadas": 0}

    for i, cell in enumerate(nb.cells):
        tags = tags_of(cell)
        where = f"{complete_path} celda {i}"

        if tags & DROP_TAGS:
            counts["eliminadas"] += 1
            continue

        if cell.cell_type != "code":
            new_cells.append(cell)
            continue

        code = strip_quarto_options(cell.source)

        # Guardar el código de estado ANTES de vaciar la celda (las 'teclear' también pueden ser 'estado')
        if "estado" in tags:
            bad = [l for l in code.splitlines() if l.lstrip().startswith(("%", "!"))]
            if bad:
                sys.exit(f"ERROR en {where}: una celda 'estado' no puede tener comandos mágicos: {bad[0]}")
            state_blocks.append(code)

        if "rescate" in tags:
            if not state_blocks:
                sys.exit(f"ERROR en {where}: celda 'rescate' sin celdas 'estado' anteriores")
            cell.source = rescue_source(state_blocks)
            try:                                                    # el rescate debe ser Python válido
                ast.parse(cell.source)
            except SyntaxError as err:
                sys.exit(f"ERROR en {where}: la celda de rescate generada no es Python válido "
                         f"(línea {err.lineno}: {err.msg}). Revisa las celdas 'estado' anteriores.")
            cell.metadata["cellView"] = "form"                      # Colab: oculta el código
            cell.metadata.setdefault("jupyter", {})["source_hidden"] = True   # JupyterLab
            counts["rescate"] += 1
        elif "teclear" in tags:
            cell.source = guide_only(code, where)
            counts["teclear"] += 1
        else:
            cell.source = code

        cell.outputs, cell.execution_count = [], None
        new_cells.append(cell)

    nb.cells = new_cells
    nbformat.validate(nb)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    nbformat.write(nb, out_path)
    print(f"{out_path}: {len(new_cells)} celdas | ⌨️ {counts['teclear']} para teclear | "
          f"🛟 {counts['rescate']} de rescate | {counts['eliminadas']} eliminadas (soluciones/instructor)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("notebooks", nargs="+", type=Path, help="Notebook(s) completo(s)")
    parser.add_argument("--out-dir", type=Path, default=None,
                        help="Carpeta de salida (por defecto: <carpeta del notebook>/participante)")
    args = parser.parse_args()
    for path in args.notebooks:
        out_dir = args.out_dir or path.parent / "participante"
        build(path, out_dir / path.name)
