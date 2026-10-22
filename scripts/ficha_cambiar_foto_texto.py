#!/usr/bin/env python3
"""Reemplaza una foto y el texto de una ficha PDF ya hecha (sin rehacer la página).

Se dibuja con Ghostscript (EndPage) sobre el original: un rectángulo blanco que tapa la
foto y el párrafo viejos, la foto nueva con borde redondeado y el párrafo nuevo en
Helvetica. Los enlaces de la página se conservan.

Uso: ficha_cambiar_foto_texto.py ficha.pdf pagina foto.png x0 top x1 bottom "texto" texto_x texto_top ancho texto_bottom [tamaño] [interlineado]
(coordenadas en pt desde arriba a la izquierda; la foto se ajusta al rectángulo x0,top,x1,bottom)
"""
import os, shutil, subprocess, sys, tempfile
from PIL import Image, ImageFont

def main():
    (pdf, pagina, foto, x0, top, x1, bottom, texto, tx, ttop, tw, tbottom) = sys.argv[1:13]
    size = float(sys.argv[13]) if len(sys.argv) > 13 else 8.295
    lead = float(sys.argv[14]) if len(sys.argv) > 14 else 11.25
    pagina = int(pagina); x0, top, x1, bottom, tx, ttop, tw, tbottom = map(float, (x0, top, x1, bottom, tx, ttop, tw, tbottom))
    alto_pag = float(subprocess.run(["pdfinfo", "-f", str(pagina), "-l", str(pagina), pdf], capture_output=True, text=True, check=True)
                     .stdout.split("size:")[1].split("x")[1].split()[0])
    im = Image.open(foto).convert("RGB"); w, h = im.size
    hx = im.tobytes().hex() + ">"
    # envoltura del texto con las métricas de Nimbus Sans (Helvetica)
    fuente = ImageFont.truetype("/usr/share/fonts/opentype/urw-base35/NimbusSans-Regular.otf", 100)
    medir = lambda s: fuente.getlength(s) * size / 100
    lineas, actual = [], ""
    for pal in texto.split():
        prueba = (actual + " " + pal).strip()
        if medir(prueba) <= tw or not actual: actual = prueba
        else: lineas.append(actual); actual = pal
    lineas.append(actual)
    if ttop + (len(lineas) - 1) * lead + size > tbottom + 0.5:
        sys.exit(f"el texto no entra: {len(lineas)} líneas")
    esc = lambda s: "".join("\\%03o" % b if b > 126 or chr(b) in "\\()" else chr(b) for b in s.encode("latin-1"))
    y = lambda t: alto_pag - t
    r = 5.0   # radio del borde
    ops = [
        # tapa foto y párrafo viejos
        f"gsave 1 setgray {x0 - 1.5:.2f} {y(bottom + 1.5):.2f} {x1 - x0 + 3:.2f} {bottom - top + 3:.2f} rectfill "
        f"{tx - 2:.2f} {y(tbottom):.2f} {tw + 6:.2f} {tbottom - ttop + 2.5:.2f} rectfill grestore",
        # foto recortada con esquinas redondeadas
        f"gsave newpath {x0 + r:.2f} {y(bottom):.2f} moveto {x1:.2f} {y(bottom):.2f} {x1:.2f} {y(top):.2f} {r} arcto 4 {{pop}} repeat "
        f"{x1:.2f} {y(top):.2f} {x0:.2f} {y(top):.2f} {r} arcto 4 {{pop}} repeat {x0:.2f} {y(top):.2f} {x0:.2f} {y(bottom):.2f} {r} arcto 4 {{pop}} repeat "
        f"{x0:.2f} {y(bottom):.2f} {x1:.2f} {y(bottom):.2f} {r} arcto 4 {{pop}} repeat closepath clip "
        f"{x0:.2f} {y(bottom):.2f} translate {x1 - x0:.2f} {bottom - top:.2f} scale {w} {h} 8 [{w} 0 0 -{h} 0 {h}] ({hx}) /ASCIIHexDecode filter false 3 colorimage grestore",
        # borde
        f"gsave 0.84 0.84 0.86 setrgbcolor 1.1 setlinewidth newpath {x0 + r:.2f} {y(bottom):.2f} moveto {x1:.2f} {y(bottom):.2f} {x1:.2f} {y(top):.2f} {r} arcto 4 {{pop}} repeat "
        f"{x1:.2f} {y(top):.2f} {x0:.2f} {y(top):.2f} {r} arcto 4 {{pop}} repeat {x0:.2f} {y(top):.2f} {x0:.2f} {y(bottom):.2f} {r} arcto 4 {{pop}} repeat "
        f"{x0:.2f} {y(bottom):.2f} {x1:.2f} {y(bottom):.2f} {r} arcto 4 {{pop}} repeat closepath stroke grestore",
        "gsave 0.2 setgray /Helvetica findfont dup length dict begin {1 index /FID ne {def} {pop pop} ifelse} forall /Encoding ISOLatin1Encoding def currentdict end /HelvL exch definefont pop /HelvL findfont %.3f scalefont setfont" % size,
    ]
    for i, l in enumerate(lineas):
        ops.append(f"{tx:.2f} {y(ttop + i * lead + size * 0.93):.2f} moveto ({esc(l)}) show")
    ops.append("grestore")
    ps = ("<< /EndPage { exch dup 1 add /PGN exch def exch 0 eq {\nPGN %d eq {\n" % (pagina) + "\n".join(ops) +
          "\n} if\ntrue } { false } ifelse } >> setpagedevice\n")
    tmp = tempfile.mkdtemp(); psf = os.path.join(tmp, "o.ps"); open(psf, "w").write(ps)
    out = os.path.join(tmp, "o.pdf")
    subprocess.run(["gs", "-q", "-dNOPAUSE", "-dBATCH", "-sDEVICE=pdfwrite", "-dPDFSETTINGS=/printer", f"-sOutputFile={out}", psf, pdf], check=True)
    shutil.move(out, pdf)
    print(f"✔ {os.path.basename(pdf)}: foto y {len(lineas)} líneas de texto en la página {pagina}")

if __name__ == "__main__":
    main()
