#!/usr/bin/env python3
"""Rediseña la barra "Financiación disponible" de las fichas PDF hechas a mano (las generadas ya la
traen en la plantilla de generate_fichas.py): más contraste (texto blanco sobre negro, borde rojo) y
con enlace a https://pro.trivium.ar/contacto/.

Busca la palabra "Financiación" en cada página, detecta la barra oscura que la contiene (render +
componente conexa), la tapa y dibuja la barra nueva con Ghostscript (EndPage); el enlace va como
pdfmark. Idempotente: si la ficha ya tiene el enlace a /contacto/ no hace nada.

Uso: python3 scripts/ficha_barra_financiacion.py ficha.pdf [ficha2.pdf ...]
"""
import os, re, shutil, subprocess, sys, tempfile
from collections import deque
from PIL import Image, ImageFont

FUENTES = "/usr/share/fonts/opentype/urw-base35/NimbusSans-%s.otf"
CONTACTO = "https://pro.trivium.ar/contacto/"
DPI = 100

def palabras(pdf, pag):
    xml = subprocess.run(["pdftotext", "-f", str(pag), "-l", str(pag), "-bbox", pdf, "-"], capture_output=True, text=True, check=True).stdout
    alto = float(re.search(r'<page width="[\d.]+" height="([\d.]+)"', xml).group(1))
    return alto, [(w[4], *map(float, w[:4])) for w in re.findall(r'<word xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" yMax="([\d.]+)">([^<]*)</word>', xml)]

def barra(pdf, pag, x, y):
    """bbox (pt, desde arriba) de la barra oscura que rodea al punto (x, y)."""
    out = tempfile.mkdtemp(); base = os.path.join(out, "p")
    subprocess.run(["pdftoppm", "-r", str(DPI), "-f", str(pag), "-l", str(pag), "-png", pdf, base], check=True)
    im = Image.open([os.path.join(out, f) for f in os.listdir(out)][0]).convert("L")
    k = DPI / 72.0; W, H = im.size; px = im.load()
    sx, sy = int(x * k), int(y * k)
    if px[sx, sy] > 90:
        return None
    visto = {(sx, sy)}; cola = deque([(sx, sy)]); x0 = x1 = sx; y0 = y1 = sy
    while cola:
        cx, cy = cola.popleft()
        x0, x1, y0, y1 = min(x0, cx), max(x1, cx), min(y0, cy), max(y1, cy)
        for nx, ny in ((cx + 1, cy), (cx - 1, cy), (cx, cy + 1), (cx, cy - 1)):
            if 0 <= nx < W and 0 <= ny < H and (nx, ny) not in visto and px[nx, ny] <= 90:
                visto.add((nx, ny)); cola.append((nx, ny))
        if len(visto) > 400000: return None
    return x0 / k, y0 / k, (x1 + 1) / k, (y1 + 1) / k

def envolver(tokens, ancho, tam):
    """tokens [(palabra, estilo)] -> líneas [[(palabra, estilo)]] que caben en 'ancho' pt."""
    f = {"n": ImageFont.truetype(FUENTES % "Regular", 100), "b": ImageFont.truetype(FUENTES % "Bold", 100)}
    med = lambda t, e: f["b" if e in ("b", "l") else "n"].getlength(t) * tam / 100
    lineas, act, w = [], [], 0.0
    esp = med(" ", "n")
    for t, e in tokens:
        tw = med(t, e)
        if act and w + esp + tw > ancho:
            lineas.append(act); act, w = [], 0.0
        w += (esp if act else 0) + tw; act.append((t, e))
    lineas.append(act)
    return lineas, med, esp

def esc(s):
    return "".join("\\%03o" % b if b > 126 or chr(b) in "\\()" else chr(b) for b in s.encode("latin-1"))

def dibujo(alto_pag, bb):
    x0, t0, x1, t1 = bb
    tokens = ([("Financiación", "b"), ("disponible:", "b")] + [(p, "n") for p in "consultá planes de pago. Pedí tu cotización en".split()]
              + [("pro.trivium.ar/contacto", "l")] + [(p, "n") for p in "para empezar.".split()])
    pad_i, pad_d = 6.0, 4.0
    ancho = (x1 - x0) - pad_i - pad_d; alto = t1 - t0
    elegido = None
    for tam in (7.4, 7.0, 6.6, 6.2, 5.8, 5.4):
        lineas, med, esp = envolver(tokens, ancho, tam)
        lead = tam * 1.28
        if len(lineas) * lead + 3.2 <= alto: elegido = (tam, lineas, med, esp, lead); break
    if not elegido: return None
    tam, lineas, med, esp, lead = elegido
    Y = lambda t: alto_pag - t
    ops = [f"gsave 1 setgray {x0 - 0.8:.2f} {Y(t1 + 0.8):.2f} {x1 - x0 + 1.6:.2f} {alto + 1.6:.2f} rectfill "
           f"0.067 setgray {x0:.2f} {Y(t1):.2f} {x1 - x0:.2f} {alto:.2f} rectfill 0.784 0.063 0.18 setrgbcolor {x0:.2f} {Y(t1):.2f} 2.6 {alto:.2f} rectfill grestore",
           "gsave /Helvetica findfont dup length dict begin {1 index /FID ne {def} {pop pop} ifelse} forall /Encoding ISOLatin1Encoding def currentdict end /HelvL exch definefont pop "
           "/Helvetica-Bold findfont dup length dict begin {1 index /FID ne {def} {pop pop} ifelse} forall /Encoding ISOLatin1Encoding def currentdict end /HelvB exch definefont pop"]
    total = len(lineas) * lead
    y_ini = t0 + (alto - total) / 2 + tam * 0.86
    link = None
    for i, linea in enumerate(lineas):
        cx = x0 + pad_i; ybase = y_ini + i * lead
        for j, (t, e) in enumerate(linea):
            if j: cx += esp
            fuente = "HelvL" if e == "n" else "HelvB"
            color = "0.9 setgray" if e == "n" else "1 setgray"
            ops.append(f"{color} /{fuente} findfont {tam:.2f} scalefont setfont {cx:.2f} {Y(ybase):.2f} moveto ({esc(t)}) show")
            if e == "l":
                w = med(t, e)
                ops.append(f"1 setgray 0.5 setlinewidth {cx:.2f} {Y(ybase + 1.1):.2f} moveto {cx + w:.2f} {Y(ybase + 1.1):.2f} lineto stroke")
                link = (cx, Y(ybase + tam * 0.25), cx + w, Y(ybase - tam * 0.8))
            cx += med(t, e)
    ops.append("grestore")
    return "\n".join(ops), link

def procesar(pdf):
    crudo = subprocess.run(["gs", "-q", "-dNOPAUSE", "-dBATCH", "-sDEVICE=pdfwrite", "-dWriteObjStms=false", "-dWriteXRefStm=false", "-sOutputFile=-", pdf], capture_output=True).stdout
    if b"pro.trivium.ar/contacto" in crudo:
        print("· ya tiene el enlace:", os.path.basename(pdf)); return False
    n = int(re.search(r"^Pages:\s+(\d+)", subprocess.run(["pdfinfo", pdf], capture_output=True, text=True).stdout, re.M).group(1))
    trabajos = []
    for pag in range(1, n + 1):
        alto, ws = palabras(pdf, pag)
        for t, x0, y0, x1, y1 in ws:
            if t.startswith("Financiaci"):
                bb = barra(pdf, pag, max(x0 - 3.0, 1), (y0 + y1) / 2)
                if bb and 10 < bb[2] - bb[0] < 560 and 8 < bb[3] - bb[1] < 80:
                    trabajos.append((pag, alto, bb))
                break
    if not trabajos:
        print("· sin barra de financiación:", os.path.basename(pdf)); return False
    tmp = tempfile.mkdtemp()
    pdf_actual = pdf
    for pag, alto, bb in trabajos:
        d = dibujo(alto, bb)
        if not d:
            print("⚠ la barra es muy chica:", os.path.basename(pdf), pag); continue
        ops, link = d
        ps = ("<< /EndPage { exch dup 1 add /PGN exch def exch 0 eq {\nPGN %d eq {\n" % pag + ops + "\n} if\ntrue } { false } ifelse } >> setpagedevice\n")
        if link:
            ps = (f"[ /Page {pag} /Rect [{link[0]:.1f} {link[3]:.1f} {link[2]:.1f} {link[1]:.1f}] /Border [0 0 0] /Subtype /Link /Action << /Subtype /URI /URI ({CONTACTO}) >> /ANN pdfmark\n") + ps
        psf = os.path.join(tmp, "o.ps"); open(psf, "w").write(ps)
        out = os.path.join(tmp, f"o{pag}.pdf")
        subprocess.run(["gs", "-q", "-dNOPAUSE", "-dBATCH", "-sDEVICE=pdfwrite", "-dPDFSETTINGS=/printer", f"-sOutputFile={out}", psf, pdf_actual], check=True)
        pdf_actual = out
    shutil.copy(pdf_actual, pdf)
    print("✔", os.path.basename(pdf), f"({len(trabajos)} barra/s)")
    return True

if __name__ == "__main__":
    for f in sys.argv[1:]:
        procesar(f)
