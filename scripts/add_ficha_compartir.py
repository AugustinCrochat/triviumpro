#!/usr/bin/env python3
"""Agrega "Descargar" y "Compartir" (dos botones con enlace) debajo del título, a la derecha de la
línea "Modelo · Código", en la primera página de una ficha PDF ya hecha.

- Descargar: /ficha/?f=assets/pdf/<archivo>&a=descargar (el visor baja el archivo al abrir).
- Compartir: https://wa.me/?text=<título + enlace al PDF>.

Se dibuja con Ghostscript (EndPage) y los enlaces con pdfmark. Es idempotente: si la ficha ya
tiene el enlace de descarga no hace nada. Fichas sin encabezado "FICHA TÉCNICA" (hojas viejas
de fabricante) se omiten.

Uso: python3 scripts/add_ficha_compartir.py ficha.pdf [ficha2.pdf ...]
"""
import os, re, shutil, subprocess, sys, tempfile
from urllib.parse import quote

SITIO = "https://pro.trivium.ar"
ROJO = "0.91 0.16 0.10"

def cabecera(pdf):
    """(alto de página, x derecho, y superior de los botones en pt desde arriba).

    Los botones van debajo del título, en la línea de "Modelo · Código", pegados al margen
    derecho (el borde derecho sale de "FICHA TÉCNICA"). Si la ficha no tiene esa línea, se
    ponen justo debajo del título."""
    xml = subprocess.run(["pdftotext", "-f", "1", "-l", "1", "-bbox", pdf, "-"], capture_output=True, text=True, check=True).stdout
    h = float(re.search(r'<page width="[\d.]+" height="([\d.]+)"', xml).group(1))
    palabras = [(w[4], *map(float, w[:4])) for w in re.findall(r'<word xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" yMax="([\d.]+)">([^<]*)</word>', xml)]
    derecho = next((x1 for t, x0, y0, x1, y1 in palabras if t.startswith("T") and t.endswith("CNICA") and y0 < 100), None)
    if derecho is None:   # "TÉCNICA" partida en letras: el margen derecho es el de las demás fichas
        if not any(t == "FICHA" and y0 < 100 for t, x0, y0, x1, y1 in palabras):
            return None
        derecho = 556.0
    # título = palabras altas (más de 15 pt de alto de caja) bajo el encabezado
    titulo = [(y0, y1) for t, x0, y0, x1, y1 in palabras if 75 < y0 < 260 and (y1 - y0) > 16]
    if not titulo:
        return None
    base = max(y1 for _, y1 in titulo)
    sub = [(y0, y1) for t, x0, y0, x1, y1 in palabras if base - 1 < y0 < base + 25 and (y1 - y0) < 13 and x0 < 400]
    alto = 11.0
    if sub:
        centro = (min(y0 for y0, _ in sub) + max(y1 for _, y1 in sub)) / 2
        return h, derecho, centro - alto / 2
    return h, derecho, base + 4.0

def ya_tiene(pdf):
    return b"a=descargar" in subprocess.run(["strings", "-a", pdf], capture_output=True).stdout

def titulo(pdf):
    t = subprocess.run(["pdfinfo", pdf], capture_output=True, text=True).stdout
    m = re.search(r"^Title:\s*(.+)$", t, re.M)
    t = m.group(1).strip() if m else os.path.basename(pdf)[:-4].replace("-", " ")
    return re.sub(r"\s*\|\s*Trivium Pro\s*$", "", t)

def procesar(pdf):
    if ya_tiene(pdf):
        print("· ya tiene botones:", os.path.basename(pdf)); return False
    cab = cabecera(pdf)
    if not cab:
        print("· sin encabezado FICHA TÉCNICA:", os.path.basename(pdf)); return False
    h, xr, ysup = cab
    nombre = os.path.basename(pdf)
    url_pdf = f"{SITIO}/assets/pdf/{nombre}"
    desc = f"{SITIO}/ficha/?f=assets/pdf/{quote(nombre)}&a=descargar"
    comp = "https://wa.me/?text=" + quote(f"{titulo(pdf)} — Trivium Pro\n{url_pdf}")
    # medidas (pt): botones de 11 de alto, bajo el texto, alineados a la derecha
    alto, gap, fs = 11.0, 4.0, 6.3
    ancho_c, ancho_d = 45.0, 47.0
    y0 = h - (ysup + alto)                # base de los botones (desde abajo)
    xr = xr + 1.0
    xc = xr - ancho_c; xd = xc - gap - ancho_d

    def pill(x, ancho, texto, icono):
        cx = x + 6.5; cy = y0 + alto / 2
        ic = {"bajar": f"{cx:.2f} {cy + 2.4:.2f} moveto {cx:.2f} {cy - 1.8:.2f} lineto {cx - 2:.2f} {cy - 0.2:.2f} moveto {cx:.2f} {cy - 1.8:.2f} lineto {cx + 2:.2f} {cy - 0.2:.2f} lineto "
                      f"{cx - 2.6:.2f} {cy - 3.2:.2f} moveto {cx + 2.6:.2f} {cy - 3.2:.2f} lineto",
              "subir": f"{cx - 2.2:.2f} {cy - 2.2:.2f} moveto {cx + 2.2:.2f} {cy + 2.2:.2f} lineto {cx - 0.4:.2f} {cy + 2.2:.2f} moveto {cx + 2.2:.2f} {cy + 2.2:.2f} lineto {cx + 2.2:.2f} {cy - 0.4:.2f} lineto"}[icono]
        return (f"gsave 0.97 0.97 0.97 setrgbcolor {x:.2f} {y0:.2f} {ancho:.2f} {alto:.2f} rectfill "
                f"0.85 0.85 0.87 setrgbcolor 0.6 setlinewidth {x:.2f} {y0:.2f} {ancho:.2f} {alto:.2f} rectstroke "
                f"{ROJO} setrgbcolor 0.9 setlinewidth 1 setlinecap 1 setlinejoin newpath {ic} stroke "
                f"0.13 setgray /Helvetica-Bold findfont {fs} scalefont setfont {x + 11:.2f} {y0 + 3.4:.2f} moveto ({texto}) show grestore")

    dib = pill(xd, ancho_d, "Descargar", "bajar") + "\n" + pill(xc, ancho_c, "Compartir", "subir")
    marcas = "\n".join(
        f"[ /Rect [{x:.1f} {y0:.1f} {x + a:.1f} {y0 + alto:.1f}] /Border [0 0 0] /Subtype /Link /Action << /Subtype /URI /URI ({u}) >> /ANN pdfmark"
        for x, a, u in ((xd, ancho_d, desc), (xc, ancho_c, comp)))
    tmp = tempfile.mkdtemp()
    ps = os.path.join(tmp, "o.ps")
    open(ps, "w").write(marcas + "\n<< /EndPage { exch pop 0 eq { " + dib + " true } { false } ifelse } >> setpagedevice\n")
    gs = ["gs", "-q", "-dNOPAUSE", "-dBATCH", "-sDEVICE=pdfwrite", "-dPDFSETTINGS=/printer"]
    n = int(re.search(r"^Pages:\s+(\d+)", subprocess.run(["pdfinfo", pdf], capture_output=True, text=True).stdout, re.M).group(1))
    p1 = os.path.join(tmp, "p1.pdf")
    subprocess.run(gs + ["-dFirstPage=1", "-dLastPage=1", f"-sOutputFile={p1}", ps, pdf], check=True)
    partes = [p1]
    if n > 1:
        rest = os.path.join(tmp, "rest.pdf")
        subprocess.run(gs + ["-dFirstPage=2", f"-sOutputFile={rest}", pdf], check=True)
        partes.append(rest)
    out = os.path.join(tmp, "final.pdf")
    subprocess.run(gs + [f"-sOutputFile={out}"] + partes, check=True)
    shutil.move(out, pdf)
    print("✔", nombre)
    return True

if __name__ == "__main__":
    for f in sys.argv[1:]:
        procesar(f)
