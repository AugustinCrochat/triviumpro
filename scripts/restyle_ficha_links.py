#!/usr/bin/env python3
"""Rehace, en una ficha PDF ya hecha, los enlaces "Ver ficha del producto en la web ↗" y
"Ver video del producto ↗" como bloques con ícono (globo / play), uno al lado del otro, debajo
de la descripción. Tapa con blanco los enlaces de texto previos (los dibujados con
add_ficha_link_descripcion.py) y dibuja los bloques con Ghostscript.

Uso: python3 scripts/restyle_ficha_links.py ficha.pdf URL_PRODUCTO [URL_VIDEO]
"""
import os, re, shutil, subprocess, sys, tempfile
from PIL import Image, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ICON = os.path.join(ROOT, "assets/img/iconos/contacto")
FONT = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", 100)
SZ = 7.4

def pagina1(pdf):
    html = subprocess.run(["pdftotext", "-f", "1", "-l", "1", "-bbox", pdf, "-"], capture_output=True, text=True, check=True).stdout
    pm = re.search(r'<page width="([\d.]+)" height="([\d.]+)">(.*?)</page>', html, re.S)
    words = [(float(a), float(b), float(c), float(d), t) for a, b, c, d, t in
             re.findall(r'<word xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" yMax="([\d.]+)">(.*?)</word>', pm.group(3))]
    return float(pm.group(1)), float(pm.group(2)), words

def icono_hex(svg, px, fondo):
    tmp = tempfile.mkdtemp(); png = os.path.join(tmp, "i.png")
    subprocess.run(["inkscape", os.path.join(ICON, svg), "-w", str(px * 2), "-o", png], check=True, capture_output=True)
    im = Image.open(png).convert("RGBA"); bg = Image.new("RGBA", im.size, fondo + (255,)); bg.alpha_composite(im)
    return bg.convert("RGB").resize((px, px), Image.LANCZOS).tobytes().hex() + ">"

RR = ("/rr { /rad exch def /hh exch def /ww exch def /yy exch def /xx exch def newpath "
      "xx rad add yy moveto xx ww add yy xx ww add yy hh add rad arcto 4 {pop} repeat "
      "xx ww add yy hh add xx yy hh add rad arcto 4 {pop} repeat xx yy hh add xx yy rad arcto 4 {pop} repeat "
      "xx yy xx ww add yy rad arcto 4 {pop} repeat closepath } def\n")

def procesar(pdf, url, video):
    w, h, words = pagina1(pdf)
    linea = next((x for i, x in enumerate(words[:-2]) if x[4] == "Ver" and words[i + 1][4] == "ficha" and words[i + 2][4] == "del"), None)
    if not linea:
        print(f"✘ {os.path.basename(pdf)}: no encontré 'Ver ficha del producto…'"); return
    x0 = linea[0]; y_top = linea[1]
    vid = next((x for i, x in enumerate(words[:-2]) if x[4] == "Ver" and words[i + 1][4] == "video" and abs(x[0] - x0) < 3), None)
    y_bot = (vid[3] if vid else linea[3]) + 1.5
    ancho_cubre = 175.0
    alto = SZ * 2.0; pad = 4.0; ic = SZ * 1.25; gi = 2.4; gap = 4.5
    cajas = [("web-rojo.svg", "Ver ficha del producto en la web", url)]
    if video: cajas.append(("video-rojo.svg", "Ver video del producto", video))
    yc = h - (y_top + y_bot) / 2.0 + (0 if not vid else 0)
    yc = h - (y_top - 1.0) - alto / 2.0 + 0.5   # centrado donde estaba la primera línea
    ops = [f"1 setgray {x0 - 3:.1f} {h - y_bot - 1:.1f} {ancho_cubre:.1f} {y_bot - y_top + 3:.1f} rectfill",
           f"/HelvB findfont {SZ} scalefont setfont"]
    marks = []; x = x0
    for svg, texto, u in cajas:
        wt = FONT.getlength(texto) * SZ / 100.0 + FONT.getlength(" ↗".replace("↗", "")) * 0
        flecha = SZ * 0.8
        cw = pad + ic + gi + wt + 3.0 + flecha + pad
        ops.append(f"gsave 1 0.969 0.973 setrgbcolor {x:.2f} {yc - alto / 2:.2f} {cw:.2f} {alto:.2f} 2.5 rr fill grestore")
        ops.append(f"gsave 0.89 0.71 0.74 setrgbcolor 0.5 setlinewidth {x:.2f} {yc - alto / 2:.2f} {cw:.2f} {alto:.2f} 2.5 rr stroke grestore")
        px = max(12, round(ic * 150 / 72))
        ops.append(f"gsave {x + pad:.2f} {yc - ic / 2:.2f} translate {ic:.2f} {ic:.2f} scale {px} {px} 8 [{px} 0 0 -{px} 0 {px}] ({icono_hex(svg, px, (255, 247, 248))}) /ASCIIHexDecode filter false 3 colorimage grestore")
        tx = x + pad + ic + gi
        ops.append(f"0.784 0.063 0.18 setrgbcolor {tx:.2f} {yc - SZ * 0.33:.2f} moveto ({texto}) show")
        ax = tx + wt + 3.0; ay = yc - flecha * 0.35
        ops.append(f"gsave 0.784 0.063 0.18 setrgbcolor 0.8 setlinewidth 1 setlinecap 1 setlinejoin {ax:.2f} {ay:.2f} moveto {ax + flecha * 0.8:.2f} {ay + flecha * 0.8:.2f} lineto stroke "
                   f"{ax + flecha * 0.15:.2f} {ay + flecha * 0.8:.2f} moveto {ax + flecha * 0.8:.2f} {ay + flecha * 0.8:.2f} lineto {ax + flecha * 0.8:.2f} {ay + flecha * 0.15:.2f} lineto stroke grestore")
        marks.append(f"[ /Rect [{x:.1f} {yc - alto / 2:.1f} {x + cw:.1f} {yc + alto / 2:.1f}] /Border [0 0 0] /Subtype /Link /Action << /Subtype /URI /URI ({u}) >> /ANN pdfmark")
        x += cw + gap
    ps = (RR + "/HelvB /Helvetica-Bold findfont dup length dict begin {1 index /FID ne {def} {pop pop} ifelse} forall "
          "/Encoding ISOLatin1Encoding def currentdict end definefont pop\n" + "\n".join(marks) + "\n"
          "<< /EndPage { exch dup 1 add /PGN exch def exch 0 eq { PGN 1 eq { gsave\n" + "\n".join(ops) + "\ngrestore } if true } { false } ifelse } >> setpagedevice\n")
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
    print(f"✔ {os.path.basename(pdf)}: bloques con ícono")

if __name__ == "__main__":
    procesar(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None)
