#!/usr/bin/env python3
"""Agrega insignias (logo de marca, sello de origen, marcado CE) al encabezado de una
ficha PDF ya hecha, a la izquierda de "FICHA TÉCNICA". Se dibujan con Ghostscript
(EndPage) sobre el espacio libre del encabezado; las fichas nuevas las llevan en el HTML.

Las imágenes salen de scripts/make_ficha_chips.py. El alto sale del prefijo del nombre:
brand-* 24 pt, origin-* 34 pt, ce.png 28 pt, ali-* 30 pt.

Fichas viejas sin encabezado "FICHA TÉCNICA" (hojas heredadas de Trivium Center): con
--top o --bottom las insignias se anclan a la esquina superior o inferior derecha de cada
página, en la banda libre del encabezado/pie.

Uso: python3 scripts/add_ficha_badges.py ficha.pdf [--top | --bottom] chip1.png [chip2.png ...]
"""
import os, re, shutil, subprocess, sys, tempfile
from PIL import Image

ALTOS = {"brand": 24.0, "origin": 34.0, "ce": 28.0, "ali": 30.0}
GAP = 9.0
DPI = 150

def cabeceras(pdf):
    html = subprocess.run(["pdftotext", "-bbox", pdf, "-"], capture_output=True, text=True, check=True).stdout
    for pm in re.finditer(r'<page width="([\d.]+)" height="([\d.]+)">(.*?)</page>', html, re.S):
        h = float(pm.group(2))
        for m in re.finditer(r'<word xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" yMax="([\d.]+)">FICHA</word>', pm.group(3)):
            x0, y0, x1, y1 = map(float, m.groups())
            if y0 < 120:
                yield len(list(re.finditer("<page", html[:pm.start()]))), h, x0, (y0 + y1) / 2
                break
        else:
            yield len(list(re.finditer("<page", html[:pm.start()]))), h, None, None

def hex_rgb(path, alto_pt):
    im = Image.open(path).convert("RGBA")
    fondo = Image.new("RGBA", im.size, (255, 255, 255, 255)); fondo.alpha_composite(im); im = fondo.convert("RGB")
    hpx = max(8, round(alto_pt * DPI / 72)); wpx = max(8, round(im.width * hpx / im.height))
    im = im.resize((wpx, hpx), Image.LANCZOS)
    return wpx, hpx, im.tobytes().hex() + ">"

def paginas_ancla(pdf, donde):
    """Anclaje a la esquina derecha: (nro de página, alto, x de la derecha, y del centro en pt desde abajo)."""
    info = subprocess.run(["pdfinfo", "-f", "1", "-l", "99", "-box", pdf], capture_output=True, text=True, check=True).stdout
    for m in re.finditer(r"Page\s+(\d+)\s+size:\s+([\d.]+) x ([\d.]+)", info):
        n, w, h = int(m.group(1)) - 1, float(m.group(2)), float(m.group(3))
        yield n, h, w - 28.0, (h - 27.0 if donde == "top" else 24.0)

def main():
    args = sys.argv[1:]
    donde = None
    for flag in ("--top", "--bottom"):
        if flag in args:
            donde = flag[2:]; args.remove(flag)
    pdf, chips = args[0], args[1:]
    datos = []
    for c in chips:
        pref = os.path.basename(c).split("-")[0].split(".")[0]
        alto = ALTOS[pref]
        wpx, hpx, hx = hex_rgb(c, alto)
        datos.append((alto, alto * wpx / hpx, wpx, hpx, hx))
    ops = {}
    if donde:
        origen = [(n, h, xr, h - yc) for n, h, xr, yc in paginas_ancla(pdf, donde)]   # y_mid en pt desde arriba
        origen = [(n, h, xr + 14.0, ym) for n, h, xr, ym in origen]
    else:
        origen = list(cabeceras(pdf))
    for n, h, x_ficha, y_mid in origen:
        if x_ficha is None:
            continue
        x = x_ficha - 14.0
        piezas = []
        for alto, ancho, wpx, hpx, hx in reversed(datos):   # de derecha a izquierda
            x -= ancho
            piezas.append(f"gsave {x:.2f} {h - y_mid - alto / 2:.2f} translate {ancho:.2f} {alto:.2f} scale "
                          f"{wpx} {hpx} 8 [{wpx} 0 0 -{hpx} 0 {hpx}] ({hx}) /ASCIIHexDecode filter false 3 colorimage grestore")
            x -= GAP
        ops[n] = "\n".join(piezas)
    if not ops:
        sys.exit("no se encontró el encabezado FICHA TÉCNICA")
    ps = "<< /EndPage { exch dup 1 add /PGN exch def exch 0 eq {\n" + "".join(
        f"PGN {n + 1} eq {{\n{o}\n}} if\n" for n, o in sorted(ops.items())) + "true } { false } ifelse } >> setpagedevice\n"
    tmp = tempfile.mkdtemp(); psf = os.path.join(tmp, "o.ps"); open(psf, "w").write(ps)
    out = os.path.join(tmp, "o.pdf")
    subprocess.run(["gs", "-q", "-dNOPAUSE", "-dBATCH", "-sDEVICE=pdfwrite", "-dPDFSETTINGS=/printer",
                    f"-sOutputFile={out}", psf, pdf], check=True)
    shutil.move(out, pdf)
    print(f"✔ {os.path.basename(pdf)}: {len(datos)} insignia(s) en {len(ops)} página(s)")

if __name__ == "__main__":
    main()
