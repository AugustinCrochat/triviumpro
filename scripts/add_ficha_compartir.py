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
    """(alto de página, x derecho, y inferior del texto "FICHA TÉCNICA" en pt desde arriba).

    Los botones van en el encabezado, apilados justo debajo de "FICHA TÉCNICA" y pegados a su
    borde derecho: ahí no pisan la marca ni las banderas (que terminan unos 45 pt más a la
    izquierda) ni el contenido. Devuelve None si la ficha no tiene ese encabezado."""
    xml = subprocess.run(["pdftotext", "-f", "1", "-l", "1", "-bbox", pdf, "-"], capture_output=True, text=True, check=True).stdout
    h = float(re.search(r'<page width="[\d.]+" height="([\d.]+)"', xml).group(1))
    palabras = [(w[4], *map(float, w[:4])) for w in re.findall(r'<word xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" yMax="([\d.]+)">([^<]*)</word>', xml)]
    ficha = next(((x0, y0, y1) for t, x0, y0, x1, y1 in palabras if t == "FICHA" and y0 < 100), None)
    if ficha is None:
        return None
    base = ficha[2]
    derecho = next((x1 for t, x0, y0, x1, y1 in palabras if t.startswith("T") and t.endswith("CNICA") and abs(y0 - ficha[1]) < 3), None)
    if derecho is None:   # "TÉCNICA" partida en letras: el margen derecho es el de las demás fichas
        derecho = 556.0
    return h, derecho, base, palabras

MARCA = "&a=descargar&p=h"   # el visor ignora "p": marca los botones ya puestos en el encabezado

def ya_tiene(pdf):
    """Botones ya puestos en el encabezado: la palabra "Descargar" está en lo alto de la página."""
    xml = subprocess.run(["pdftotext", "-f", "1", "-l", "1", "-bbox", pdf, "-"], capture_output=True, text=True).stdout
    return any(float(y) < 100 for y in re.findall(r'<word xMin="[\d.]+" yMin="([\d.]+)" xMax="[\d.]+" yMax="[\d.]+">Descargar</word>', xml))

def botones_viejos(pdf):
    """Botones de versiones anteriores (debajo del título): se tapan con blanco y sus enlaces
    se anulan. Para leer los enlaces hay que reescribir sin object streams (gs -dWriteObjStms=false).
    Devuelve (pdf a usar, [rects (x0 y0 x1 y1) de los botones viejos])."""
    tmp = tempfile.mkdtemp(); a = os.path.join(tmp, "a.pdf")
    subprocess.run(["gs", "-q", "-dNOPAUSE", "-dBATCH", "-sDEVICE=pdfwrite", "-dPDFSETTINGS=/printer",
                    "-dWriteObjStms=false", "-dWriteXRefStm=false", f"-sOutputFile={a}", pdf], check=True)
    b = bytearray(open(a, "rb").read())
    rects = []
    for m in re.finditer(rb"/Subtype\s*/Link", bytes(b)):
        ini = bytes(b).rfind(b" 0 obj", 0, m.start()); fin = bytes(b).find(b"endobj", m.start())
        obj = bytes(b[ini:fin])
        if b"a=descargar" in obj or b"wa.me/?text" in obj:
            r = re.search(rb"/Rect\s*\[([^\]]*)\]", obj)
            vals = [float(x) for x in r.group(1).split()]
            rects.append(tuple(vals))
            nuevo = b"/Rect [0 0 0 0]".ljust(len(r.group(0)))
            pos = ini + r.start()
            b[pos:pos + len(r.group(0))] = nuevo
    open(a, "wb").write(bytes(b))
    return a, rects

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
    h, xr, base, palabras = cab
    nombre = os.path.basename(pdf)
    url_pdf = f"{SITIO}/assets/pdf/{nombre}"
    desc = f"{SITIO}/ficha/?f=assets/pdf/{quote(nombre)}{MARCA}"
    comp = "https://wa.me/?text=" + quote(f"{titulo(pdf)} — Trivium Pro\n{url_pdf}")
    # medidas (pt): dos botones apilados bajo "FICHA TÉCNICA", alineados a su borde derecho
    alto, sep, fs, ancho = 8.6, 1.4, 5.6, 42.0
    xr = xr + 1.0
    x = xr - ancho
    top1 = base + 2.2; top2 = top1 + alto + sep
    # el hueco tiene que estar libre de texto
    for t, x0, y0, x1, y1 in palabras:
        if x1 > x - 1 and x0 < xr + 1 and y1 > top1 - 0.5 and y0 < top2 + alto + 0.5 and not (t == "FICHA" or t.endswith("CNICA")):
            print("⚠ hay texto bajo los botones nuevos:", nombre, t); break
    origen, viejos = pdf, []
    origen, viejos = botones_viejos(pdf)
    for r in viejos:   # texto que quedaría tapado por la cubierta blanca de los botones viejos
        for t, x0, y0, x1, y1 in palabras:
            if t in ("Descargar", "Compartir"): continue
            if x1 > r[0] and x0 < r[2] and (h - y1) < r[3] and (h - y0) > r[1]:
                print("⚠ los botones viejos tapaban texto:", nombre, t); break
    cubrir = "".join(f"1 setgray {r[0] - 0.8:.2f} {r[1] - 0.8:.2f} {r[2] - r[0] + 1.6:.2f} {r[3] - r[1] + 1.6:.2f} rectfill " for r in viejos if r[2] > 0)

    def pill(top, texto, icono):
        y0 = h - (top + alto)
        cx = x + 5.2; cy = y0 + alto / 2
        ic = {"bajar": f"{cx:.2f} {cy + 2.0:.2f} moveto {cx:.2f} {cy - 1.4:.2f} lineto {cx - 1.6:.2f} {cy - 0.1:.2f} moveto {cx:.2f} {cy - 1.4:.2f} lineto {cx + 1.6:.2f} {cy - 0.1:.2f} lineto "
                      f"{cx - 2.1:.2f} {cy - 2.6:.2f} moveto {cx + 2.1:.2f} {cy - 2.6:.2f} lineto",
              "subir": f"{cx - 1.8:.2f} {cy - 1.8:.2f} moveto {cx + 1.8:.2f} {cy + 1.8:.2f} lineto {cx - 0.3:.2f} {cy + 1.8:.2f} moveto {cx + 1.8:.2f} {cy + 1.8:.2f} lineto {cx + 1.8:.2f} {cy - 0.3:.2f} lineto"}[icono]
        return (f"gsave 0.97 0.97 0.97 setrgbcolor {x:.2f} {y0:.2f} {ancho:.2f} {alto:.2f} rectfill "
                f"0.85 0.85 0.87 setrgbcolor 0.5 setlinewidth {x:.2f} {y0:.2f} {ancho:.2f} {alto:.2f} rectstroke "
                f"{ROJO} setrgbcolor 0.8 setlinewidth 1 setlinecap 1 setlinejoin newpath {ic} stroke "
                f"0.13 setgray /Helvetica-Bold findfont {fs} scalefont setfont {x + 9.4:.2f} {y0 + 2.7:.2f} moveto ({texto}) show grestore")

    dib = cubrir + pill(top1, "Descargar", "bajar") + "\n" + pill(top2, "Compartir", "subir")
    marcas = "\n".join(
        f"[ /Rect [{x:.1f} {h - (t + alto):.1f} {x + ancho:.1f} {h - t:.1f}] /Border [0 0 0] /Subtype /Link /Action << /Subtype /URI /URI ({u}) >> /ANN pdfmark"
        for t, u in ((top1, desc), (top2, comp)))
    tmp = tempfile.mkdtemp()
    ps = os.path.join(tmp, "o.ps")
    open(ps, "w").write(marcas + "\n<< /EndPage { exch pop 0 eq { " + dib + " true } { false } ifelse } >> setpagedevice\n")
    gs = ["gs", "-q", "-dNOPAUSE", "-dBATCH", "-sDEVICE=pdfwrite", "-dPDFSETTINGS=/printer"]
    n = int(re.search(r"^Pages:\s+(\d+)", subprocess.run(["pdfinfo", origen], capture_output=True, text=True).stdout, re.M).group(1))
    p1 = os.path.join(tmp, "p1.pdf")
    subprocess.run(gs + ["-dFirstPage=1", "-dLastPage=1", f"-sOutputFile={p1}", ps, origen], check=True)
    partes = [p1]
    if n > 1:
        rest = os.path.join(tmp, "rest.pdf")
        subprocess.run(gs + ["-dFirstPage=2", f"-sOutputFile={rest}", origen], check=True)
        partes.append(rest)
    out = os.path.join(tmp, "final.pdf")
    subprocess.run(gs + [f"-sOutputFile={out}"] + partes, check=True)
    shutil.move(out, pdf)
    print("✔", nombre)
    return True

if __name__ == "__main__":
    for f in sys.argv[1:]:
        procesar(f)
