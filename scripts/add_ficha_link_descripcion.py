#!/usr/bin/env python3
"""Agrega, debajo del párrafo destacado de una ficha PDF ya hecha, el enlace
"Ver ficha del producto en la web ↗" (rojo, con flecha) hacia la página del producto.

Ubica el párrafo por tamaño de letra (el texto grande a la derecha de la foto, entre el
subtítulo "Modelo:" y la tabla). Se dibuja con Ghostscript y se enlaza con pdfmark en la página 1.
Si algo no coincide con esa estructura, informa y no toca el PDF.

Uso: python3 scripts/add_ficha_link_descripcion.py ficha.pdf URL [palabra-del-párrafo]
"""
import os, re, shutil, statistics, subprocess, sys, tempfile
from PIL import ImageFont

FONT = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf", 100)
TEXTO = "Ver ficha del producto en la web"
TEXTO_VIDEO = "Ver video del producto"
SEGUNDA = False   # --segunda: va una línea más abajo (debajo de "Ver ficha…")
SIZE = 8.6
ROJO = (0.78, 0.063, 0.18)   # #c8102e, el rojo de las fichas

def pagina1(pdf):
    html = subprocess.run(["pdftotext", "-f", "1", "-l", "1", "-bbox", pdf, "-"], capture_output=True, text=True, check=True).stdout
    pm = re.search(r'<page width="([\d.]+)" height="([\d.]+)">(.*?)</page>', html, re.S)
    w, h = float(pm.group(1)), float(pm.group(2))
    words = [(float(a), float(b), float(c), float(d), t) for a, b, c, d, t in
             re.findall(r'<word xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" yMax="([\d.]+)">(.*?)</word>', pm.group(3))]
    return w, h, words

def tam(x):
    return (x[2] - x[0]) / (FONT.getlength(x[4]) / 100.0) if len(x[4]) > 3 else 0

def parrafo_por_palabra(words, palabra):
    """Párrafo que contiene `palabra`: líneas consecutivas (hacia abajo) con el mismo margen izquierdo."""
    ini = [x for x in words if x[4] == palabra]
    if not ini:
        return None
    a0 = ini[0]
    # arranque real del párrafo: el margen izquierdo de la línea donde está la palabra
    a = (min(x[0] for x in words if abs(x[1] - a0[1]) < 3), a0[1], 0, 0, a0[4])
    lineas = {}
    for x in sorted((x for x in words if x[0] >= a[0] - 4 and x[1] >= a[1] - 2), key=lambda v: v[1]):
        # una palabra en negrita puede quedar 1-2 pt más arriba o abajo: misma línea si está a menos de 3 pt
        clave = next((k for k in lineas if abs(k - x[1]) < 3), None)
        lineas.setdefault(x[1] if clave is None else clave, []).append(x)
    tops = sorted(lineas); sel = [tops[0]]
    for t in tops[1:]:
        if t - sel[-1] > 17:
            break
        # la línea debe arrancar cerca del margen izquierdo del párrafo
        if min(v[0] for v in lineas[t]) > a[0] + 6:
            break
        sel.append(t)
    ws = [v for t in sel for v in lineas[t]]
    return min(v[0] for v in ws), max(v[3] for v in ws)

def procesar(pdf, url, palabra=None):
    w, h, words = pagina1(pdf)
    if SEGUNDA:
        # el video va justo debajo de la línea "Ver ficha del producto en la web"
        for i, x in enumerate(words[:-2]):
            if x[4] == "Ver" and words[i + 1][4] == "ficha" and words[i + 2][4] == "del":
                return dibujar(pdf, url, w, h, x[0], x[3] - 5.0 + 0.0)
        print(f"✘ {os.path.basename(pdf)}: no encontré la línea 'Ver ficha…'"); return
    if palabra:
        r = parrafo_por_palabra(words, palabra)
        if not r:
            print(f"✘ {os.path.basename(pdf)}: no encontré la palabra '{palabra}'"); return
        x0, ult = r
        return dibujar(pdf, url, w, h, x0, ult)
    modelo = [x for x in words if x[4].startswith("Modelo:")]
    if not modelo:
        print(f"✘ {os.path.basename(pdf)}: no encontré el subtítulo 'Modelo:'"); return
    ym = modelo[0][3]
    grandes = [x for x in words if x[0] > w * 0.33 and ym < x[1] < ym + 200 and tam(x) >= 9.8]
    if len(grandes) < 8:
        print(f"✘ {os.path.basename(pdf)}: no encontré el párrafo destacado"); return
    # solo las líneas consecutivas (los títulos con letras espaciadas de más abajo también salen "grandes")
    tops = sorted({round(x[1]) for x in grandes}); fin = tops[0]
    for a_, b_ in zip(tops, tops[1:]):
        if b_ - a_ > 22:
            break
        fin = b_
    grandes = [x for x in grandes if round(x[1]) <= fin + 1]
    x0 = min(x[0] for x in grandes); y_ini = min(x[1] for x in grandes); y_fin = max(x[3] for x in grandes)
    parrafo = [x for x in words if x[0] >= x0 - 2 and y_ini - 1 <= x[1] and x[3] <= y_fin + 1]   # incluye negritas
    ult = max(x[3] for x in parrafo)
    # que no haya otro texto pegado justo debajo
    debajo = [x for x in words if x[0] >= x0 - 2 and ult < x[1] < ult + 18]
    if debajo:
        print(f"✘ {os.path.basename(pdf)}: poco espacio debajo del párrafo ({debajo[0][4]})"); return
    return dibujar(pdf, url, w, h, x0, ult)

def dibujar(pdf, url, w, h, x0, ult):
    global TEXTO
    y_top = ult + 5.0 + (9.0 if SEGUNDA else 0.0)
    base = h - (y_top + SIZE * 0.86)
    ancho = FONT.getlength(TEXTO) * SIZE / 100.0
    ax = x0 + ancho + 4.0                     # flecha ↗ a continuación del texto
    s = SIZE * 0.55
    ps = (f"[ /Rect [{x0 - 1:.1f} {base - 2.5:.1f} {ax + s + 2:.1f} {base + SIZE:.1f}] /Border [0 0 0] /Subtype /Link "
          f"/Action << /Subtype /URI /URI ({url}) >> /ANN pdfmark\n"
          "/HelvL /Helvetica findfont dup length dict begin {1 index /FID ne {def} {pop pop} ifelse} forall "
          "/Encoding ISOLatin1Encoding def currentdict end definefont pop\n"
          "<< /EndPage { exch dup 1 add /PGN exch def exch 0 eq { PGN 1 eq { gsave\n"
          f"{ROJO[0]} {ROJO[1]} {ROJO[2]} setrgbcolor /HelvL findfont {SIZE} scalefont setfont {x0:.2f} {base:.2f} moveto ({TEXTO}) show\n"
          f"0.9 setlinewidth 1 setlinecap 1 setlinejoin {ax:.2f} {base:.2f} moveto {ax + s:.2f} {base + s:.2f} lineto stroke\n"
          f"{ax + s * 0.15:.2f} {base + s:.2f} moveto {ax + s:.2f} {base + s:.2f} lineto {ax + s:.2f} {base + s * 0.15:.2f} lineto stroke\n"
          "grestore } if true } { false } ifelse } >> setpagedevice\n")
    tmp = tempfile.mkdtemp(); psf = os.path.join(tmp, "o.ps"); open(psf, "w", encoding="latin-1").write(ps)
    n = int(re.search(r"Pages:\s+(\d+)", subprocess.run(["pdfinfo", pdf], capture_output=True, text=True).stdout).group(1))
    partes = []
    for i in range(1, n + 1):
        part = os.path.join(tmp, f"p{i}.pdf")
        cmd = ["gs", "-q", "-dNOPAUSE", "-dBATCH", "-sDEVICE=pdfwrite", "-dPDFSETTINGS=/printer", f"-dFirstPage={i}", f"-dLastPage={i}", f"-sOutputFile={part}"]
        subprocess.run(cmd + ([psf] if i == 1 else []) + [pdf], check=True, capture_output=True)
        partes.append(part)
    final = os.path.join(tmp, "f.pdf")
    subprocess.run(["gs", "-q", "-dNOPAUSE", "-dBATCH", "-sDEVICE=pdfwrite", "-dPDFSETTINGS=/printer", f"-sOutputFile={final}"] + partes, check=True, capture_output=True)
    shutil.move(final, pdf)
    print(f"✔ {os.path.basename(pdf)}: enlace debajo de la descripción")

if __name__ == "__main__":
    if "--video" in sys.argv:
        sys.argv.remove("--video"); TEXTO = TEXTO_VIDEO; SEGUNDA = True
    procesar(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None)
