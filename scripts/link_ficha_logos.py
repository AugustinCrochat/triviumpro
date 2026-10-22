#!/usr/bin/env python3
"""Hace clicables los logos de una ficha PDF ya hecha: el logo Trivium Pro (arriba y abajo) lleva a la home;
las insignias del encabezado (marca, bandera de origen, marcado CE, sello ALI) y la caja "Origen" del pie
llevan a su página informativa.

Los logos y sellos se ubican con pdfplumber (imágenes) y con una detección de rectángulo oscuro (el logo
Trivium Pro es un vector negro). Las insignias se asignan por orden de izquierda a derecha.

Uso: python3 scripts/link_ficha_logos.py ficha.pdf [--chips URL1,URL2,...] [--origen URL] [--sin-pie]
"""
import os, shutil, subprocess, sys, tempfile
import numpy as np
import pdfplumber
from PIL import Image

HOME = "https://pro.trivium.ar/"

def logo_oscuro(pdf, n, w, h, region):
    """Bounding box (pt) del mayor bloque casi negro dentro de region=(x0,y0,x1,y1) desde arriba-izquierda."""
    tmp = tempfile.mkdtemp()
    subprocess.run(["pdftoppm", "-r", "144", "-f", str(n), "-l", str(n), "-png", pdf, os.path.join(tmp, "p")], capture_output=True)
    f = [x for x in os.listdir(tmp) if x.endswith(".png")][0]
    im = np.array(Image.open(os.path.join(tmp, f)).convert("RGB")).astype(int)
    k = im.shape[1] / w
    x0, y0, x1, y1 = [int(v * k) for v in region]
    sub = im[y0:y1, x0:x1]
    oscuro = (sub.sum(axis=2) < 150)
    cols = np.where(oscuro.sum(axis=0) > 6)[0]; rows = np.where(oscuro.sum(axis=1) > 6)[0]
    if len(cols) < 20 or len(rows) < 10: return None
    return ((x0 + cols.min()) / k, (y0 + rows.min()) / k, (x0 + cols.max()) / k, (y0 + rows.max()) / k)

def palabras_pie(pdf, n, h):
    import re
    html = subprocess.run(["pdftotext", "-f", str(n), "-l", str(n), "-bbox", pdf, "-"], capture_output=True, text=True).stdout
    return [(float(a), float(b), float(c), float(d), t) for a, b, c, d, t in
            re.findall(r'<word xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" yMax="([\d.]+)">(.*?)</word>', html) if float(b) > h - 80]

def procesar(pdf, chips, origen, pie=True):
    marks_pag = []
    with pdfplumber.open(pdf) as doc:
        for n, pg in enumerate(doc.pages, 1):
            w, h = float(pg.width), float(pg.height)
            rects = []   # (x0, top, x1, bottom, url)
            # logo Trivium Pro de arriba (imagen o bloque oscuro) -> home
            sup = [i for i in pg.images if i["top"] < 80 and ((i["x0"] < 150 and (i["x1"] - i["x0"]) > 40) or (i["x1"] - i["x0"]) > 180)]
            if sup:
                i = sup[0]; rects.append((i["x0"], i["top"], i["x1"], i["bottom"], HOME))
            else:
                b = logo_oscuro(pdf, n, w, h, (0, 0, 190, 90))
                if b: rects.append((*b, HOME))
            # insignias del encabezado (de izquierda a derecha)
            chips_pg = sorted([i for i in pg.images if i["top"] < 80 and i["x0"] >= 150 and 14 < (i["x1"] - i["x0"]) <= 180], key=lambda i: i["x0"])
            for i, url in zip(chips_pg, chips):
                if url: rects.append((i["x0"], i["top"], i["x1"], i["bottom"], url))
            if pie:
                inf = [i for i in pg.images if i["top"] > h - 80 and i["x0"] < 150 and (i["x1"] - i["x0"]) > 20]
                if inf:
                    i = inf[0]; rects.append((i["x0"], i["top"], i["x1"], i["bottom"], HOME))
                else:
                    b = logo_oscuro(pdf, n, w, h, (0, h - 70, 150, h))
                    if b: rects.append((*b, HOME))
                if origen:
                    for p in palabras_pie(pdf, n, h):
                        if p[4] == "Origen:":
                            fin = max((q[2] for q in palabras_pie(pdf, n, h) if abs(q[1] - p[1]) < 3 and q[0] >= p[0]), default=p[2])
                            rects.append((p[0] - 5, p[1] - 3, fin + 5, p[3] + 3, origen)); break
            marks_pag.append((n, h, rects))
    tmp = tempfile.mkdtemp(); partes = []
    for n, h, rects in marks_pag:
        part = os.path.join(tmp, f"p{n}.pdf")
        ps = "\n".join(f"[ /Rect [{x0 - 1:.1f} {h - bt - 1:.1f} {x1 + 1:.1f} {h - tp + 1:.1f}] /Border [0 0 0] /Subtype /Link /Action << /Subtype /URI /URI ({u}) >> /ANN pdfmark"
                       for x0, tp, x1, bt, u in rects) + "\n"
        psf = os.path.join(tmp, f"m{n}.ps"); open(psf, "w").write(ps)
        subprocess.run(["gs", "-q", "-dNOPAUSE", "-dBATCH", "-sDEVICE=pdfwrite", "-dPDFSETTINGS=/printer", f"-dFirstPage={n}", f"-dLastPage={n}",
                        f"-sOutputFile={part}", psf, pdf], check=True, capture_output=True)
        partes.append(part)
    final = os.path.join(tmp, "f.pdf")
    subprocess.run(["gs", "-q", "-dNOPAUSE", "-dBATCH", "-sDEVICE=pdfwrite", "-dPDFSETTINGS=/printer", f"-sOutputFile={final}"] + partes, check=True, capture_output=True)
    shutil.move(final, pdf)
    print(f"✔ {os.path.basename(pdf)}: {sum(len(r) for _, _, r in marks_pag)} áreas de logo/insignia enlazadas")

if __name__ == "__main__":
    a = sys.argv[1:]
    chips = a[a.index("--chips") + 1].split(",") if "--chips" in a else []
    origen = a[a.index("--origen") + 1] if "--origen" in a else None
    procesar(a[0], chips, origen, "--sin-pie" not in a)
