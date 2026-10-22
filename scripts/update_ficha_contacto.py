#!/usr/bin/env python3
"""Reemplaza la línea de contacto del pie de una ficha PDF ya hecha por la versión vigente:

    pro.trivium.ar · info@trivium.ar · [WA] +54 9 11 2701-5294 · [WA] +54 9 351 399-4200 (Ventas)

con el ícono de WhatsApp y cada dato como enlace (pro.trivium.ar → ficha del producto si se
pasa --producto, si no la home; mail; wa.me de cada número). Tapa la línea vieja con un
rectángulo del color del fondo y escribe la nueva encima (Ghostscript). Las anotaciones
viejas de la ficha se descartan (por eso después conviene correr add_ficha_producto_link.py,
que vuelve a poner el enlace de la etiqueta "Ver ficha del producto").

Para fichas nuevas, escribir la línea directamente en el HTML (ver scripts/add_ficha_links.py).

Uso: python3 scripts/update_ficha_contacto.py ficha.pdf [--producto URL]
"""
import os, re, shutil, statistics, subprocess, sys, tempfile
import numpy as np
from PIL import Image, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf", 100)
HOME = "https://pro.trivium.ar/"
MAIL = "mailto:info@trivium.ar"
WA1, WA2 = "https://wa.me/5491127015294", "https://wa.me/5493513994200"
N1, N2 = "+54 9 11 2701-5294", "+54 9 351 399-4200 (Ventas)"
WA_PATH = ("M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164"
           "-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458"
           ".13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612"
           "-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016"
           "-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227"
           " 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347"
           "m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26"
           "c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884"
           "-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945"
           "L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413Z")

def ancho(t, size): return FONT.getlength(t) * size / 100.0

def icono_png(destino):
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="240" height="240">'
           f'<path d="{WA_PATH}" fill="#25D366"/></svg>')
    tmp = tempfile.mkdtemp(); f = os.path.join(tmp, "wa.svg"); open(f, "w").write(svg)
    subprocess.run(["inkscape", f, "-w", "240", "-h", "240", "-o", destino], check=True, capture_output=True)

def paginas(pdf):
    html = subprocess.run(["pdftotext", "-bbox", pdf, "-"], capture_output=True, text=True, check=True).stdout
    for pm in re.finditer(r'<page width="([\d.]+)" height="([\d.]+)">(.*?)</page>', html, re.S):
        words = [(float(a), float(b), float(c), float(d), t) for a, b, c, d, t in
                 re.findall(r'<word xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" yMax="([\d.]+)">(.*?)</word>', pm.group(3))]
        yield float(pm.group(1)), float(pm.group(2)), words

def muestrear(pdf, n, w, h, bb):
    """(color de fondo, color de texto) del rectángulo bb=(x0,y0,x1,y1) en pt desde arriba."""
    tmp = tempfile.mkdtemp()
    subprocess.run(["pdftoppm", "-r", "144", "-f", str(n), "-l", str(n), "-png", pdf, os.path.join(tmp, "p")], capture_output=True)
    f = [x for x in os.listdir(tmp) if x.endswith(".png")][0]
    im = np.array(Image.open(os.path.join(tmp, f)).convert("RGB"), dtype=float)
    k = im.shape[1] / w
    x0, y0, x1, y1 = [int(v * k) for v in bb]
    reg = im[max(0, y0):y1, max(0, x0):x1].reshape(-1, 3)
    vals, cnt = np.unique(reg.astype(int), axis=0, return_counts=True)
    bg = vals[cnt.argmax()].astype(float)
    dist = np.abs(reg - bg).sum(axis=1)
    lejos = reg[np.argsort(dist)[-max(5, len(reg) // 40):]]
    return bg / 255.0, lejos.mean(axis=0) / 255.0

def procesar(pdf, producto):
    sitio = producto or HOME
    datos = {}
    for n, (w, h, words) in enumerate(paginas(pdf), 1):
        pri = [i for i, x in enumerate(words) if x[4] == "pro.trivium.ar"]
        if not pri:
            continue
        for i in pri:
            y0 = words[i][1]
            linea = [x for x in words if abs(x[1] - y0) < 3]
            textos = [x[4] for x in linea]
            if "info@trivium.ar" in textos and "2701-5294" in textos:
                break
        else:
            continue
        # extensión del grupo: de pro.trivium.ar / info / número (lo que quede más a la izquierda y a la derecha)
        claves = [x for x in linea if x[4] in ("pro.trivium.ar", "info@trivium.ar", "2701-5294", "WhatsApp", "+54", "9", "11", "·", "|")
                  or x[4] in ("·WhatsApp", "·info@trivium.ar")]
        x_ini = min(x[0] for x in claves); x_fin = max(x[2] for x in claves)
        grupo = [x for x in linea if x_ini - 1 <= x[0] and x[2] <= x_fin + 1]
        yt = min(x[1] for x in grupo); yb = max(x[3] for x in grupo)
        size = statistics.median((x[2] - x[0]) / (FONT.getlength(x[4]) / 100.0) for x in grupo if len(x[4]) > 3 and "@" not in x[4]) if True else 7
        otros = [x for x in linea if x not in grupo]
        datos[n] = dict(w=w, h=h, x_ini=x_ini, x_fin=x_fin, yt=yt, yb=yb, size=size, otros=otros)
    if not datos:
        print(f"· {os.path.basename(pdf)}: no tiene la línea de contacto, sin cambios"); return
    icon = os.path.join(tempfile.mkdtemp(), "wa.png"); icono_png(icon)
    tmp = tempfile.mkdtemp(); partes = []
    npag = len(list(paginas(pdf)))
    for n in range(1, npag + 1):
        part = os.path.join(tmp, f"p{n}.pdf")
        if n not in datos:
            subprocess.run(["gs", "-q", "-dNOPAUSE", "-dBATCH", "-sDEVICE=pdfwrite", "-dPDFSETTINGS=/printer", f"-dFirstPage={n}", f"-dLastPage={n}",
                            f"-sOutputFile={part}", pdf], check=True, capture_output=True)
            partes.append(part); continue
        d = datos[n]; w, h, size = d["w"], d["h"], d["size"]
        bg, fg = muestrear(pdf, n, w, h, (d["x_ini"], d["yt"], d["x_fin"], d["yb"]))
        isz = size * 1.25
        def construir(sz):
            isz = sz * 1.25
            seg = [("t", "pro.trivium.ar", sitio), ("p", " · ", None), ("t", "info@trivium.ar", MAIL), ("p", " · ", None),
                   ("i", None, WA1), ("t", N1, WA1), ("p", " · ", None), ("i", None, WA2), ("t", N2, WA2)]
            x = 0.0; out = []
            for tipo, txt, url in seg:
                if tipo == "i":
                    ww = isz; out.append((tipo, x, ww, txt, url)); x += ww + sz * 0.3
                else:
                    ww = ancho(txt, sz) + (sz * 0.12 if tipo == "t" else 0); out.append((tipo, x, ww, txt, url)); x += ww
            return out, x
        sz = size
        out, total = construir(sz)
        derecha = d["x_fin"] > w - 80
        x0 = (d["x_fin"] - total) if derecha else d["x_ini"]
        # colisión con otros textos de la misma línea
        for _ in range(4):
            if any(not (o[2] < x0 - 3 or o[0] > x0 + total + 3) for o in d["otros"]):
                sz *= 0.93; out, total = construir(sz); x0 = (d["x_fin"] - total) if derecha else d["x_ini"]
            else:
                break
        cover_x0 = min(d["x_ini"], x0) - 1.5; cover_x1 = max(d["x_fin"], x0 + total) + 1.5
        ytop = d["yt"] - 1.5; ybot = d["yb"] + 1.5
        base = h - (d["yb"] - (d["yb"] - d["yt"]) * 0.22)          # línea de base aproximada
        ops = [f"{bg[0]:.3f} {bg[1]:.3f} {bg[2]:.3f} setrgbcolor {cover_x0:.1f} {h - ybot:.1f} {cover_x1 - cover_x0:.1f} {ybot - ytop:.1f} rectfill",
               f"{fg[0]:.3f} {fg[1]:.3f} {fg[2]:.3f} setrgbcolor /HelvL findfont {sz:.2f} scalefont setfont"]
        marks = []
        # icono compuesto sobre el fondo
        im = Image.open(icon).convert("RGBA"); fondo = Image.new("RGBA", im.size, tuple(int(c * 255) for c in bg) + (255,)); fondo.alpha_composite(im)
        px = max(10, round(sz * 1.25 * 150 / 72)); ic = fondo.convert("RGB").resize((px, px), Image.LANCZOS)
        hexic = ic.tobytes().hex() + ">"
        for tipo, x, ww, txt, url in out:
            X = x0 + x
            if tipo == "t":
                ops.append(f"{X:.2f} {base:.2f} moveto ({txt.replace('(', chr(92) + '(').replace(')', chr(92) + ')')}) show")
            elif tipo == "p":
                ops.append(f"{X:.2f} {base:.2f} moveto ({txt}) show")
            else:
                iy = base - sz * 0.22
                ops.append(f"gsave {X:.2f} {iy:.2f} translate {ww:.2f} {ww:.2f} scale {px} {px} 8 [{px} 0 0 -{px} 0 {px}] ({hexic}) /ASCIIHexDecode filter false 3 colorimage grestore")
                ops.append(f"{fg[0]:.3f} {fg[1]:.3f} {fg[2]:.3f} setrgbcolor")
            if url:
                x1 = X + ww + (sz * 0.2 if tipo == 'i' else 0)
                marks.append(f"[ /Rect [{X - 1:.1f} {h - ybot:.1f} {x1 + 1:.1f} {h - ytop:.1f}] /Border [0 0 0] /Subtype /Link /Action << /Subtype /URI /URI ({url}) >> /ANN pdfmark")
        ps = ("/HelvL /Helvetica findfont dup length dict begin {1 index /FID ne {def} {pop pop} ifelse} forall "
              "/Encoding ISOLatin1Encoding def currentdict end definefont pop\n" + "\n".join(marks) + "\n"
              "<< /EndPage { exch dup 1 add /PGN exch def exch 0 eq { PGN 1 eq { gsave\n" + "\n".join(ops) + "\ngrestore } if true } { false } ifelse } >> setpagedevice\n")
        psf = os.path.join(tmp, f"o{n}.ps"); open(psf, "w", encoding="latin-1").write(ps)
        subprocess.run(["gs", "-q", "-dNOPAUSE", "-dBATCH", "-sDEVICE=pdfwrite", "-dPDFSETTINGS=/printer", "-dPreserveAnnots=false",
                        f"-dFirstPage={n}", f"-dLastPage={n}", f"-sOutputFile={part}", psf, pdf], check=True, capture_output=True)
        partes.append(part)
    final = os.path.join(tmp, "final.pdf")
    subprocess.run(["gs", "-q", "-dNOPAUSE", "-dBATCH", "-sDEVICE=pdfwrite", "-dPDFSETTINGS=/printer", f"-sOutputFile={final}"] + partes,
                   check=True, capture_output=True)
    shutil.move(final, pdf)
    print(f"✔ {os.path.basename(pdf)}: contacto actualizado en {len(datos)} página(s)")

if __name__ == "__main__":
    prod = None
    if "--producto" in sys.argv:
        prod = sys.argv[sys.argv.index("--producto") + 1]
    procesar(sys.argv[1], prod)
