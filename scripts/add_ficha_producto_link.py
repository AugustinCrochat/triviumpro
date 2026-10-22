#!/usr/bin/env python3
"""Agrega a la primera página de una ficha PDF una etiqueta clicable que lleva a la ficha
del producto en pro.trivium.ar ("Ver ficha del producto en pro.trivium.ar").

Busca en las cuatro esquinas el primer rincón libre (fondo liso) para no tapar contenido,
dibuja la etiqueta (rectángulo blanco con borde fino y texto) con Ghostscript y le pone el
enlace con pdfmark. Si el PDF ya tiene ese enlace, no hace nada.

Uso: python3 scripts/add_ficha_producto_link.py ficha.pdf https://pro.trivium.ar/producto/<slug>/
     python3 scripts/add_ficha_producto_link.py --todas      (todas las fichas enlazadas desde catalog.json)
     python3 scripts/add_ficha_producto_link.py ficha.pdf URL --pos X,Y   (posición manual en pt desde arriba-izquierda)
"""
import json, os, re, shutil, subprocess, sys, tempfile
from PIL import Image, ImageFont
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://pro.trivium.ar"
LABEL = "Ver ficha del producto en pro.trivium.ar"
FONT = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf", 100)
SIZE = 6.8
PADX, PADY, MARGIN = 5.0, 3.0, 12.0

def pagina1(pdf):
    out = subprocess.run(["pdfinfo", "-f", "1", "-l", "1", pdf], capture_output=True, text=True).stdout
    m = re.search(r"Page\s+1 size:\s+([\d.]+) x ([\d.]+)", out) or re.search(r"Page size:\s+([\d.]+) x ([\d.]+)", out)
    return float(m.group(1)), float(m.group(2))

def esquina_libre(pdf, w, h, ancho, alto):
    tmp = tempfile.mkdtemp()
    subprocess.run(["pdftoppm", "-r", "72", "-f", "1", "-l", "1", "-gray", "-png", pdf, os.path.join(tmp, "p")],
                   capture_output=True)
    f = [x for x in os.listdir(tmp) if x.endswith(".png")][0]
    im = np.array(Image.open(os.path.join(tmp, f)).convert("L"), dtype=float)
    H, W = im.shape
    cand = {
        "abajo-derecha": (W - MARGIN - ancho, H - MARGIN - alto),
        "abajo-izquierda": (MARGIN, H - MARGIN - alto),
        "arriba-derecha": (W - MARGIN - ancho, MARGIN),
        "arriba-izquierda": (MARGIN, MARGIN),
    }
    mejor = None
    for nombre, (x, y) in cand.items():
        x0, y0 = int(max(0, x - 2)), int(max(0, y - 2))
        reg = im[y0:int(y + alto + 2), x0:int(x + ancho + 2)]
        if not reg.size:
            continue
        sd = reg.std()
        if sd < 6:                               # fondo liso (blanco, gris de banda, etc.)
            return nombre, x, y
        if mejor is None or sd < mejor[0]:
            mejor = (sd, nombre, x, y)
    # sin rincón liso: el menos cargado, si no tapa casi nada (la etiqueta es chica)
    if mejor and mejor[0] < 40:
        return mejor[1], mejor[2], mejor[3]
    return None, None, None

def ya_tiene(pdf, url):
    out = subprocess.run(["pdfinfo", "-url", pdf], capture_output=True, text=True).stdout
    return url in out

def procesar(pdf, url, forzar=None):
    if ya_tiene(pdf, url):
        print(f"· {os.path.basename(pdf)}: ya tiene el enlace"); return "ya"
    w, h = pagina1(pdf)
    ancho = FONT.getlength(LABEL) * SIZE / 100 + 2 * PADX
    alto = SIZE + 2 * PADY + 1
    nombre, x, y = ("manual", forzar[0], forzar[1]) if forzar else esquina_libre(pdf, w, h, ancho, alto)
    if nombre is None:
        print(f"✘ {os.path.basename(pdf)}: ninguna esquina libre, sin cambios"); return "sin_lugar"
    ybase = h - y - alto               # a coordenadas PostScript (origen abajo)
    esc = LABEL.replace("(", "\\(").replace(")", "\\)")
    ps = (f"[ /Rect [{x:.1f} {ybase:.1f} {x + ancho:.1f} {ybase + alto:.1f}] /Border [0 0 0] /Subtype /Link "
          f"/Action << /Subtype /URI /URI ({url}) >> /ANN pdfmark\n"
          "/HelvL /Helvetica findfont dup length dict begin {1 index /FID ne {def} {pop pop} ifelse} forall "
          "/Encoding ISOLatin1Encoding def currentdict end definefont pop\n"
          "<< /EndPage { exch dup 1 add /PGN exch def exch 0 eq { PGN 1 eq { gsave\n"
          f"1 setgray {x:.1f} {ybase:.1f} {ancho:.1f} {alto:.1f} rectfill\n"
          f"0.78 setgray 0.5 setlinewidth {x + .25:.1f} {ybase + .25:.1f} {ancho - .5:.1f} {alto - .5:.1f} rectstroke\n"
          f"0.18 0.35 0.72 setrgbcolor /HelvL findfont {SIZE} scalefont setfont "
          f"{x + PADX:.1f} {ybase + PADY + 1:.1f} moveto ({esc}) show\n"
          "grestore } if true } { false } ifelse } >> setpagedevice\n")
    tmp = tempfile.mkdtemp(); psf = os.path.join(tmp, "o.ps"); open(psf, "w", encoding="latin-1").write(ps)
    out = os.path.join(tmp, "o.pdf")
    subprocess.run(["gs", "-q", "-dNOPAUSE", "-dBATCH", "-sDEVICE=pdfwrite", "-dPDFSETTINGS=/printer",
                    f"-sOutputFile={out}", psf, pdf], check=True, capture_output=True)
    shutil.move(out, pdf)
    print(f"✔ {os.path.basename(pdf)}: etiqueta en {nombre}"); return "ok"

def todas():
    d = json.load(open(os.path.join(ROOT, "data/catalog.json"), encoding="utf-8"))
    mapa = {}
    for p in d["products"]:
        for f in re.findall(r'href="(assets/pdf/[^"]+\.pdf)"', p.get("html_description", "")):
            mapa.setdefault(f, p["slug"])
    res = {}
    for f, slug in mapa.items():
        ruta = os.path.join(ROOT, f)
        if os.path.exists(ruta):
            res[f] = procesar(ruta, f"{SITE}/producto/{slug}/")
    print({k: sum(1 for v in res.values() if v == k) for k in set(res.values())})

if __name__ == "__main__":
    if sys.argv[1] == "--todas":
        todas()
    else:
        pos = None
        if "--pos" in sys.argv:
            pos = tuple(float(v) for v in sys.argv[sys.argv.index("--pos") + 1].split(","))
        procesar(sys.argv[1], sys.argv[2], pos)
