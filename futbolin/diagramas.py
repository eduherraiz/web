"""Copia los diagramas del repo del futbolín con los colores oscuros de esta página.

Uso: python3 futbolin/diagramas.py <carpeta docs/img del repo del futbolín>

Los SVG los genera docs/img/diagramas.py en ese repo y sus colores son variables CSS
con valor por defecto. Aquí solo se les añade un <style> que las redefine.
"""
import re
import sys
from pathlib import Path

DIAGRAMAS = ["barrera-ir", "cableado-general", "placa-interfaz", "alimentacion-cableado", "tiras-conexion"]
OSCURO = ("<style>svg{--tinta:#efe6d2;--suave:#9aa0b2;--papel:#0f1118;--linea:#262b3b;--chip:#1c2030;"
          "--bola:#2a2e3d;--rojo:#e0604a;--madera:#8a6a44;--madera-borde:#a8865c}</style>")

origen = Path(sys.argv[1])
destino = Path(__file__).resolve().parent / "diagramas"
destino.mkdir(exist_ok=True)
for nombre in DIAGRAMAS:
    svg = (origen / f"{nombre}.svg").read_text()
    # justo después de la etiqueta <svg ...>
    svg = re.sub(r"(<svg[^>]*>)", r"\1" + OSCURO, svg, count=1)
    (destino / f"{nombre}.svg").write_text(svg)
print(", ".join(DIAGRAMAS))
