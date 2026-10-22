#!/usr/bin/env python3
"""Rehace el pie de contacto de una ficha PDF ya hecha con cajas delimitadas e íconos:

    [🌐 pro.trivium.ar] [✉ info@trivium.ar] [WA +54 9 11 2701-5294]   [bandera Origen: País]
                                                                       Página n de N

Cada caja es un enlace (pro.trivium.ar → ficha del producto si se pasa --producto, si no la
home; mail; wa.me; la de origen, a su página). Tapa la línea vieja (contacto y texto de origen/página
a su derecha) con un rectángulo del color del fondo y dibuja la nueva con Ghostscript. Las
anotaciones (enlaces) viejas que no tocan esa línea se conservan; las de la línea se rehacen.
El "Página n de N" queda en una línea propia, debajo de la caja de origen.

Fichas nuevas: escribir el pie en el HTML (ver las clases .pie / .caja de las fichas SPOA10 y PL-4.0-2D).

Uso: python3 scripts/update_ficha_contacto.py ficha.pdf [--producto URL] [--origen US|CN|IT|DE|none]
"""
import os, re, shutil, statistics, subprocess, sys, tempfile
import numpy as np
from PIL import Image, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ICONOS = os.path.join(ROOT, "assets/img/iconos/contacto")
FONT = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf", 100)
FONT_B = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", 100)
HOME, MAIL = "https://pro.trivium.ar/", "mailto:info@trivium.ar"
WA1, WA2 = "https://wa.me/5491127015294", "https://wa.me/5493513994200"   # WA2 (Ventas) ya no se dibuja; sirve para reconocer cajas viejas
N1 = "+54 9 11 2701-5294"
SITE = "https://pro.trivium.ar/origen/"
ORIGENES = {"US": ("usa.svg", "Estados Unidos"), "CN": ("china.svg", "China"),
            "IT": ("italia.svg", "Italia"), "DE": ("alemania.svg", "Alemania"),
            "SE": ("suecia.svg", "Suecia"), "TW": ("taiwan.svg", "Taiwán")}
ORI_URL = {"US": "estados-unidos", "CN": "marcado-ce", "IT": "italia", "DE": "alemania", "SE": "suecia", "TW": "taiwan"}
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

def ancho(t, size): return FONT_B.getlength(t) * size / 100.0
def psesc(s): return s.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")

def rasterizar_svg(svg_path, destino, w=300):
    subprocess.run(["inkscape", svg_path, "-w", str(w), "-o", destino], check=True, capture_output=True)

def links_viejos(pdf, n):
    import pdfplumber
    with pdfplumber.open(pdf) as doc:
        return [dict(x0=l["x0"], x1=l["x1"], top=l["top"], bottom=l["bottom"], uri=l["uri"])
                for l in doc.pages[n - 1].hyperlinks if l.get("uri")]

def paginas(pdf):
    html = subprocess.run(["pdftotext", "-bbox", pdf, "-"], capture_output=True, text=True, check=True).stdout
    for pm in re.finditer(r'<page width="([\d.]+)" height="([\d.]+)">(.*?)</page>', html, re.S):
        words = [(float(a), float(b), float(c), float(d), t) for a, b, c, d, t in
                 re.findall(r'<word xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" yMax="([\d.]+)">(.*?)</word>', pm.group(3))]
        yield float(pm.group(1)), float(pm.group(2)), words

def muestrear(pdf, n, w, bb):
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

def img_hex(png, px_w, px_h, bg):
    im = Image.open(png).convert("RGBA")
    fondo = Image.new("RGBA", im.size, tuple(int(c * 255) for c in bg) + (255,)); fondo.alpha_composite(im)
    im = fondo.convert("RGB").resize((px_w, px_h), Image.LANCZOS)
    return im.tobytes().hex() + ">"

ESTILO = {"rojo": ("1 0.961 0.965", "0.89 0.71 0.74"), "wa": ("0.937 0.984 0.953", "0.608 0.863 0.698"),
          "gris": ("0.957 0.957 0.957", "0.81 0.81 0.81")}   # (relleno, borde) en rgb

RR = ("/rr { /rad exch def /hh exch def /ww exch def /yy exch def /xx exch def newpath "
      "xx rad add yy moveto xx ww add yy xx ww add yy hh add rad arcto 4 {pop} repeat "
      "xx ww add yy hh add xx yy hh add rad arcto 4 {pop} repeat xx yy hh add xx yy rad arcto 4 {pop} repeat "
      "xx yy xx ww add yy rad arcto 4 {pop} repeat closepath } def\n")

def procesar(pdf, producto, origen):
    sitio = producto or HOME
    datos = {}
    total_pag = len(list(paginas(pdf)))
    for n, (w, h, words) in enumerate(paginas(pdf), 1):
        pri = [i for i, x in enumerate(words) if x[4] == "pro.trivium.ar"]
        linea = None
        for i in pri:
            y0 = words[i][1]
            l = [x for x in words if abs(x[1] - y0) < 3]
            tx = [x[4] for x in l]
            if "info@trivium.ar" in tx and "2701-5294" in tx:
                linea = l; break
        if not linea:
            continue
        claves = [x for x in linea if x[4] in ("pro.trivium.ar", "info@trivium.ar", "2701-5294", "399-4200", "(Ventas)")
                  or x[4] in ("·info@trivium.ar", "·WhatsApp")]
        # (los "·" y números sueltos no cuentan: en algunas fichas el "Página 1 de 2" está en la misma línea)
        x_ini = min(x[0] for x in claves); x_fin = max(x[2] for x in claves)
        grupo = [x for x in linea if x_ini - 1 <= x[0] and x[2] <= x_fin + 1]
        derecho = [x for x in linea if x[0] > x_fin + 2]                     # origen / página a la derecha
        pagina = " ".join(x[4] for x in derecho)
        mp = "Página" in pagina   # (el texto viejo tapado sigue en el PDF y se mezcla al extraerlo: el número se rearma abajo)
        yt = min(x[1] for x in grupo + derecho); yb = max(x[3] for x in grupo + derecho)
        size = statistics.median((x[2] - x[0]) / (FONT.getlength(x[4]) / 100.0) for x in grupo if len(x[4]) > 3 and "@" not in x[4])
        r_fin = max([x[2] for x in derecho] or [x_fin])
        datos[n] = dict(w=w, h=h, x_ini=x_ini, x_fin=x_fin, r_fin=r_fin, yt=yt, yb=yb, size=size,
                        pagina=f"Página {n} de {total_pag}" if mp else "", hay_derecha=bool(derecho))
    if not datos:
        print(f"· {os.path.basename(pdf)}: no tiene la línea de contacto, sin cambios"); return
    tmp = tempfile.mkdtemp()
    ic = {}
    iconos = [("web", "globo.svg"), ("mail", "mail.svg")] + ([("flag", ORIGENES[origen][0])] if origen in ORIGENES else [])
    for nombre, svg in iconos:
        d = os.path.join(tmp, nombre + ".png"); rasterizar_svg(os.path.join(ICONOS, svg), d); ic[nombre] = d
    svgwa = os.path.join(tmp, "wa.svg")
    open(svgwa, "w").write(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="{WA_PATH}" fill="#25D366"/></svg>')
    d = os.path.join(tmp, "wa.png"); rasterizar_svg(svgwa, d); ic["wa"] = d
    npag = len(list(paginas(pdf))); partes = []
    for n in range(1, npag + 1):
        part = os.path.join(tmp, f"p{n}.pdf")
        if n not in datos:
            subprocess.run(["gs", "-q", "-dNOPAUSE", "-dBATCH", "-sDEVICE=pdfwrite", "-dPDFSETTINGS=/printer", f"-dFirstPage={n}", f"-dLastPage={n}",
                            f"-sOutputFile={part}", pdf], check=True, capture_output=True)
            partes.append(part); continue
        D = datos[n]; w, h = D["w"], D["h"]
        bg, fg = muestrear(pdf, n, w, (D["x_ini"], D["yt"], max(D["x_fin"], D["r_fin"]), D["yb"]))
        sz = 8.2
        alto = sz * 1.62; pad = 4.2; gi = 3.0; isz = sz * 1.15
        def caja(tipo, txt, url):
            wt = ancho(txt, sz) + sz * 0.12
            return dict(tipo=tipo, txt=txt, url=url, w=pad + isz + gi + wt + pad)
        cajas = [caja("web", "pro.trivium.ar", sitio), caja("mail", "info@trivium.ar", MAIL), caja("wa", N1, WA1)]
        gap = 4.0
        total = sum(c["w"] for c in cajas) + gap * (len(cajas) - 1)
        derecha_contacto = (not D["hay_derecha"]) and D["x_fin"] > w - 80      # contacto pegado a la derecha (sin origen)
        x0 = (D["x_fin"] - total) if derecha_contacto else D["x_ini"]
        yc = h - (D["yt"] + D["yb"]) / 2.0                                       # centro vertical de la línea (PostScript)
        # los bordes de las cajas viejas salen de sus enlaces (el texto queda adentro de la caja, con ícono a la izquierda)
        viejos = [hl for hl in links_viejos(pdf, n) if hl["uri"] in (HOME, sitio, MAIL, WA1, WA2)
                  and (h - hl["bottom"]) < yc < (h - hl["top"]) and D["x_ini"] - 22 < hl["x0"] and hl["x1"] < D["x_fin"] + 22]
        if viejos:
            D["x_ini"] = min(D["x_ini"], min(hl["x0"] for hl in viejos)); D["x_fin"] = max(D["x_fin"], max(hl["x1"] for hl in viejos))
            x0 = (D["x_fin"] - total) if derecha_contacto else D["x_ini"]
        cover = [min(D["x_ini"], x0) - 2, max(D["x_fin"], D["r_fin"], x0 + total) + 2]
        # enlaces viejos que no tocan la línea: se conservan (el resto se rehace)
        preservados = []
        origen_url = SITE + ORI_URL[origen] + "/" if origen in ORI_URL else None
        for hl in links_viejos(pdf, n):
            ly0, ly1 = h - hl["bottom"], h - hl["top"]
            toca = hl["x1"] > cover[0] and hl["x0"] < cover[1] and ly1 > yc - alto / 2 - 4 and ly0 < yc + alto / 2 + 4
            if toca:
                if "/origen/" in hl["uri"]: origen_url = hl["uri"]
                continue
            preservados.append(f"[ /Rect [{hl['x0']:.1f} {ly0:.1f} {hl['x1']:.1f} {ly1:.1f}] /Border [0 0 0] /Subtype /Link /Action << /Subtype /URI /URI ({hl['uri']}) >> /ANN pdfmark")
        cy0 = min([yc - alto / 2 - 2.5] + [h - hl["bottom"] - 2 for hl in viejos]); cy1 = max([yc + alto / 2 + 2.5] + [h - hl["top"] + 2 for hl in viejos])
        ops = [f"{bg[0]:.3f} {bg[1]:.3f} {bg[2]:.3f} setrgbcolor {cover[0]:.1f} {cy0:.1f} {cover[1] - cover[0]:.1f} {cy1 - cy0:.1f} rectfill",
               "/HelvL findfont {:.2f} scalefont setfont".format(sz)]
        marks = preservados
        def dibuja_caja(x, c):
            fill, line = ESTILO["wa" if c["tipo"] == "wa" else "rojo"]
            ops.append(f"gsave {fill} setrgbcolor {x:.2f} {yc - alto / 2:.2f} {c['w']:.2f} {alto:.2f} 3.5 rr fill grestore")
            ops.append(f"gsave {line} setrgbcolor 0.8 setlinewidth {x:.2f} {yc - alto / 2:.2f} {c['w']:.2f} {alto:.2f} 3.5 rr stroke grestore")
            px = max(10, round(isz * 150 / 72))
            ops.append(f"gsave {x + pad:.2f} {yc - isz / 2:.2f} translate {isz:.2f} {isz:.2f} scale {px} {px} 8 [{px} 0 0 -{px} 0 {px}] ({img_hex(ic[c['tipo']], px, px, tuple(map(float, fill.split())))}) /ASCIIHexDecode filter false 3 colorimage grestore")
            ops.append(f"0.1 setgray {x + pad + isz + gi:.2f} {yc - sz * 0.33:.2f} moveto ({psesc(c['txt'])}) show")
            if c.get("url"):
                marks.append(f"[ /Rect [{x:.1f} {yc - alto / 2:.1f} {x + c['w']:.1f} {yc + alto / 2:.1f}] /Border [0 0 0] /Subtype /Link /Action << /Subtype /URI /URI ({c['url']}) >> /ANN pdfmark")
        x = x0
        for c in cajas:
            dibuja_caja(x, c); x += c["w"] + gap
        # origen (bandera + país) a la derecha, y el "Página n de N" si lo había
        if origen in ORIGENES and D["hay_derecha"]:
            txt = f"Origen: {ORIGENES[origen][1]}"
            fw, fh = sz * 1.5, sz * 1.0
            cw = pad + fw + gi + ancho(txt, sz) + pad
            xr = D["r_fin"] - cw
            fill, line = ESTILO["gris"]
            ops.append(f"gsave {fill} setrgbcolor {xr:.2f} {yc - alto / 2:.2f} {cw:.2f} {alto:.2f} 3.5 rr fill grestore")
            ops.append(f"gsave {line} setrgbcolor 0.8 setlinewidth {xr:.2f} {yc - alto / 2:.2f} {cw:.2f} {alto:.2f} 3.5 rr stroke grestore")
            if origen_url:
                marks.append(f"[ /Rect [{xr:.1f} {yc - alto / 2:.1f} {xr + cw:.1f} {yc + alto / 2:.1f}] /Border [0 0 0] /Subtype /Link /Action << /Subtype /URI /URI ({origen_url}) >> /ANN pdfmark")
            pxw, pxh = round(fw * 150 / 72), round(fh * 150 / 72)
            ops.append(f"gsave {xr + pad:.2f} {yc - fh / 2:.2f} translate {fw:.2f} {fh:.2f} scale {pxw} {pxh} 8 [{pxw} 0 0 -{pxh} 0 {pxh}] ({img_hex(ic['flag'], pxw, pxh, tuple(map(float, fill.split())))}) /ASCIIHexDecode filter false 3 colorimage grestore")
            ops.append(f"0.5 setlinewidth 0.7 setgray {xr + pad:.2f} {yc - fh / 2:.2f} {fw:.2f} {fh:.2f} rectstroke")
            ops.append(f"0.1 setgray {xr + pad + fw + gi:.2f} {yc - sz * 0.33:.2f} moveto ({psesc(txt)}) show")
            if D["pagina"]:   # en una línea propia, abajo de la caja de origen y alineado a su derecha
                psz = 7.4
                ops.append(f"/HelvR findfont {psz} scalefont setfont 0.25 setgray {D['r_fin'] - FONT.getlength(D['pagina']) * psz / 100.0:.2f} {yc - alto / 2 - 3 - psz:.2f} moveto ({psesc(D['pagina'])}) show")
        ps = (RR + "/HelvL /Helvetica-Bold findfont dup length dict begin {1 index /FID ne {def} {pop pop} ifelse} forall "
              "/Encoding ISOLatin1Encoding def currentdict end definefont pop\n"
              "/HelvR /Helvetica findfont dup length dict begin {1 index /FID ne {def} {pop pop} ifelse} forall "
              "/Encoding ISOLatin1Encoding def currentdict end definefont pop\n" + "\n".join(marks) + "\n"
              "<< /EndPage { exch dup 1 add /PGN exch def exch 0 eq { PGN 1 eq { gsave\n" + "\n".join(ops) + "\ngrestore } if true } { false } ifelse } >> setpagedevice\n")
        psf = os.path.join(tmp, f"o{n}.ps"); open(psf, "w", encoding="latin-1").write(ps)
        subprocess.run(["gs", "-q", "-dNOPAUSE", "-dBATCH", "-sDEVICE=pdfwrite", "-dPDFSETTINGS=/printer", "-dPreserveAnnots=false",
                        f"-dFirstPage={n}", f"-dLastPage={n}", f"-sOutputFile={part}", psf, pdf], check=True, capture_output=True)
        partes.append(part)
    final = os.path.join(tmp, "final.pdf")
    subprocess.run(["gs", "-q", "-dNOPAUSE", "-dBATCH", "-sDEVICE=pdfwrite", "-dPDFSETTINGS=/printer", f"-sOutputFile={final}"] + partes, check=True, capture_output=True)
    shutil.move(final, pdf)
    print(f"✔ {os.path.basename(pdf)}: pie rehecho en {len(datos)} página(s)")

if __name__ == "__main__":
    prod = sys.argv[sys.argv.index("--producto") + 1] if "--producto" in sys.argv else None
    ori = sys.argv[sys.argv.index("--origen") + 1] if "--origen" in sys.argv else "none"
    procesar(sys.argv[1], prod, ori)
