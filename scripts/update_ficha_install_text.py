#!/usr/bin/env python3
"""Reemplaza el texto del bloque "Instalación en tu taller" de una ficha PDF ya hecha.

Las fichas viejas no tienen fuente editable, así que se tapa el párrafo con un
rectángulo blanco y se escribe el texto nuevo encima (Ghostscript, EndPage). El texto
viejo queda debajo, invisible. Para fichas nuevas, cambiar el texto en el HTML y no
usar este script.

Texto vigente (decisión de Etienne): no mencionar puesta en marcha ni prueba de
funcionamiento, no decir que la instalación se cobra ni que es gratis; solo que hay
un equipo de técnicos para la colocación y que se hace en todo el país.

Uso: python3 scripts/update_ficha_install_text.py ficha.pdf [...]
"""
import re, shutil, statistics, subprocess, sys, tempfile, os
from PIL import ImageFont

NUEVO = "Contamos con un equipo de técnicos para la colocación de tu equipo, en todo el país."
FONT = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf", 100)

def paginas(pdf):
    html = subprocess.run(["pdftotext", "-bbox", pdf, "-"], capture_output=True, text=True, check=True).stdout
    for pm in re.finditer(r'<page width="([\d.]+)" height="([\d.]+)">(.*?)</page>', html, re.S):
        h = float(pm.group(2))
        words = [(float(a), float(b), float(c), float(d), t) for a, b, c, d, t in
                 re.findall(r'<word xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" yMax="([\d.]+)">(.*?)</word>', pm.group(3))]
        yield h, words

def ancho(txt, size):
    return FONT.getlength(txt) * size / 100.0

def envolver(txt, size, limite):
    lineas, actual = [], ""
    for w in txt.split():
        prueba = (actual + " " + w).strip()
        if ancho(prueba, size) <= limite or not actual:
            actual = prueba
        else:
            lineas.append(actual); actual = w
    lineas.append(actual)
    return lineas

def ps_esc(s):
    return s.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")

def bloques(pdf):
    out = {}
    for n, (h, words) in enumerate(paginas(pdf)):
        for i, (x0, y0, x1, y1, t) in enumerate(words):
            if t == "Instalación" and i + 3 < len(words) and words[i + 1][4] == "en" and words[i + 2][4] == "tu":
                cuerpo = [w for w in words if x0 - 2 <= w[0] <= x0 + 160 and y1 + 0.5 < w[1] < y1 + 48 and w[2] < x0 + 175]
                if not cuerpo:
                    continue
                # Solo las líneas consecutivas del párrafo: en las fichas viejas el pie de
                # contacto queda a pocos puntos y no hay que taparlo.
                tops = sorted({round(w[1]) for w in cuerpo})
                limite = tops[0]
                for a, b in zip(tops, tops[1:]):
                    if b - a > 17:
                        break
                    limite = b
                cuerpo = [w for w in cuerpo if round(w[1]) <= limite + 1]
                pie = [w[1] for w in words if w[4] in ("pro.trivium.ar", "WhatsApp") and w[1] > y1]
                if pie:
                    cuerpo = [w for w in cuerpo if w[1] < min(pie) - 2]
                # El alto que informa pdftotext incluye interlineado: el cuerpo se mide por el ancho de las palabras.
                size = statistics.median((w[2] - w[0]) / (FONT.getlength(w[4]) / 100.0) for w in cuerpo if len(w[4]) > 3)
                bx0 = min(w[0] for w in cuerpo) - 1.5; bx1 = max(w[2] for w in cuerpo) + 1.5
                by0 = min(w[1] for w in cuerpo) - 2.5; by1 = max(w[3] for w in cuerpo) + 1.5
                lineas = envolver(NUEVO, size, max(bx1 - bx0, 150) - 3)
                lead = size * 1.55
                top = min(w[1] for w in cuerpo)
                ops = [f"1 setgray {bx0:.1f} {h - by1:.1f} {bx1 - bx0:.1f} {by1 - by0:.1f} rectfill",
                       f"0.27 setgray /HelvL findfont {size:.2f} scalefont setfont"]
                for k, l in enumerate(lineas):
                    y = h - (top + size * 0.86 + k * lead)
                    ops.append(f"{bx0 + 1.5:.1f} {y:.1f} moveto ({ps_esc(l)}) show")
                out.setdefault(n, []).extend(ops)
    return out

PROLOGO = """/HelvL /Helvetica findfont dup length dict begin
{1 index /FID ne {def} {pop pop} ifelse} forall
/Encoding ISOLatin1Encoding def currentdict end definefont pop
"""

def procesar(pdf):
    b = bloques(pdf)
    if not b:
        print(f"· {os.path.basename(pdf)}: no tiene el bloque, sin cambios"); return
    casos = "".join(f"dup {n} eq {{ pop gsave\n" + "\n".join(ops) + "\ngrestore }} {{\n" for n, ops in sorted(b.items())) + "pop " + "} ifelse " * len(b)
    ps = PROLOGO + "<< /EndPage { exch 1 index 0 eq { dup 0 ge } { false } ifelse pop pop dup pop 0 eq { true } { false } ifelse } >> pop\n"
    # EndPage: recibe (pagecount reason); reason 0 = showpage. Dibuja en la página pagecount+1.
    ps = PROLOGO + "<< /EndPage { exch dup 1 add /PGN exch def exch 0 eq {\n" \
         + "".join(f"PGN {n + 1} eq {{ gsave\n" + "\n".join(ops) + "\ngrestore } if\n" for n, ops in sorted(b.items())) \
         + "true } { false } ifelse } >> setpagedevice\n"
    tmp = tempfile.mkdtemp(); psf = os.path.join(tmp, "o.ps"); open(psf, "w", encoding="latin-1").write(ps)
    out = os.path.join(tmp, "o.pdf")
    subprocess.run(["gs", "-q", "-dNOPAUSE", "-dBATCH", "-sDEVICE=pdfwrite", "-dPDFSETTINGS=/printer",
                    f"-sOutputFile={out}", psf, pdf], check=True)
    shutil.move(out, pdf)
    print(f"✔ {os.path.basename(pdf)}: texto de instalación reemplazado en {len(b)} página(s)")

if __name__ == "__main__":
    for p in sys.argv[1:]:
        procesar(p)
