#!/usr/bin/env python3
"""Alinea los puntos rojos de los tres bloques del pie ("Instalación en tu taller", "Servicio técnico
oficial", "Repuestos originales") de las fichas ya hechas: en esas fichas el punto quedaba flotando
arriba del título. Se borra y se vuelve a dibujar a la izquierda del título, centrado en su línea.

Uso: python3 scripts/fix_ficha_bullets.py ficha.pdf [...]
"""
import os, re, shutil, subprocess, sys, tempfile
import numpy as np
from PIL import Image

TIT = [("Instalación", "en"), ("Servicio", "técnico"), ("Repuestos", "originales")]

def paginas(pdf):
    html = subprocess.run(["pdftotext", "-bbox", pdf, "-"], capture_output=True, text=True, check=True).stdout
    for pm in re.finditer(r'<page width="([\d.]+)" height="([\d.]+)">(.*?)</page>', html, re.S):
        words = [(float(a), float(b), float(c), float(d), t) for a, b, c, d, t in
                 re.findall(r'<word xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" yMax="([\d.]+)">(.*?)</word>', pm.group(3))]
        yield float(pm.group(1)), float(pm.group(2)), words

def procesar(pdf):
    tmp = tempfile.mkdtemp(); partes = []; cambios = 0
    pag = list(paginas(pdf))
    for n, (w, h, words) in enumerate(pag, 1):
        part = os.path.join(tmp, f"p{n}.pdf"); ops = []
        titulos = []
        for i, x in enumerate(words[:-1]):
            for a, b in TIT:
                if x[4] == a and words[i + 1][4] == b and abs(words[i + 1][1] - x[1]) < 3 and x[1] > h * 0.6:
                    titulos.append(x)
        if titulos:
            subprocess.run(["pdftoppm", "-r", "288", "-f", str(n), "-l", str(n), "-png", pdf, os.path.join(tmp, "r")], capture_output=True)
            f = [q for q in os.listdir(tmp) if q.startswith("r") and q.endswith(".png")][0]
            im = np.array(Image.open(os.path.join(tmp, f)).convert("RGB")).astype(int); os.remove(os.path.join(tmp, f))
            k = im.shape[1] / w
            for t in titulos:
                x0, y0 = t[0], t[1]
                X0, X1, Y0, Y1 = int((x0 - 6) * k), int((x0 + 10) * k), int((y0 - 16) * k), int((y0 + 1) * k)
                reg = im[Y0:Y1, X0:X1]
                rojo = (reg[:, :, 0] > 190) & (reg[:, :, 1] < 90) & (reg[:, :, 2] < 90)
                ys, xs = np.nonzero(rojo)
                if len(xs) < 6 or (ys.max() / k + (y0 - 16)) > y0 - 1.0:
                    continue          # sin punto flotante (ya está alineado o no hay)
                bx0, bx1 = (xs.min() + X0) / k - 1.2, (xs.max() + X0) / k + 1.2
                by0, by1 = (ys.min() + Y0) / k - 1.2, (ys.max() + Y0) / k + 1.2
                bg = im[max(0, Y0 - 2), X0].astype(float) / 255.0
                ym = h - (t[1] + t[3]) / 2.0
                ops.append(f"{bg[0]:.3f} {bg[1]:.3f} {bg[2]:.3f} setrgbcolor {bx0:.1f} {h - by1:.1f} {bx1 - bx0:.1f} {by1 - by0:.1f} rectfill")
                ops.append(f"0.89 0.07 0.07 setrgbcolor {x0 - 4.4:.2f} {ym:.2f} 1.7 0 360 arc fill")
                cambios += 1
        if ops:
            ps = ("<< /EndPage { exch dup 1 add /PGN exch def exch 0 eq { PGN 1 eq { gsave\n" + "\n".join(ops) + "\ngrestore } if true } { false } ifelse } >> setpagedevice\n")
            psf = os.path.join(tmp, f"o{n}.ps"); open(psf, "w").write(ps)
            subprocess.run(["gs", "-q", "-dNOPAUSE", "-dBATCH", "-sDEVICE=pdfwrite", "-dPDFSETTINGS=/printer", "-dPreserveAnnots=true",
                            f"-dFirstPage={n}", f"-dLastPage={n}", f"-sOutputFile={part}", psf, pdf], check=True, capture_output=True)
        else:
            subprocess.run(["gs", "-q", "-dNOPAUSE", "-dBATCH", "-sDEVICE=pdfwrite", "-dPDFSETTINGS=/printer", f"-dFirstPage={n}", f"-dLastPage={n}",
                            f"-sOutputFile={part}", pdf], check=True, capture_output=True)
        partes.append(part)
    if not cambios:
        print(f"· {os.path.basename(pdf)}: sin puntos flotantes"); return
    final = os.path.join(tmp, "f.pdf")
    subprocess.run(["gs", "-q", "-dNOPAUSE", "-dBATCH", "-sDEVICE=pdfwrite", "-dPDFSETTINGS=/printer", f"-sOutputFile={final}"] + partes, check=True, capture_output=True)
    shutil.move(final, pdf)
    print(f"✔ {os.path.basename(pdf)}: {cambios} puntos alineados")

if __name__ == "__main__":
    for p in sys.argv[1:]:
        procesar(p)
