#!/usr/bin/env python3
"""Vuelve clicables los datos del pie de una ficha técnica PDF (formato Trivium Pro).

Busca en cada página, con pdftotext -bbox, "pro.trivium.ar", "info@trivium.ar" y
"WhatsApp +54 9 11 2701-5294" y les agrega un enlace (sitio, mail y wa.me) con
Ghostscript. Es idempotente: si el PDF ya tiene los enlaces no hace falta correrlo,
y correrlo de nuevo solo duplica las anotaciones (por eso se aplica al PDF recién
generado, antes de publicarlo).

Con --producto URL, "pro.trivium.ar" del pie lleva a la ficha del producto en vez de la home.

Con --solo-etiqueta --producto URL, solo se enlaza la etiqueta "Ver ficha del producto en pro.trivium.ar"
(sirve cuando update_ficha_contacto.py descartó las anotaciones viejas de una ficha ya hecha).

Uso: python3 scripts/add_ficha_links.py ficha.pdf [salida.pdf] [--producto URL] [--solo-etiqueta]
"""
import re, shutil, subprocess, sys, tempfile, os

LINKS = [
    (["pro.trivium.ar"], "https://pro.trivium.ar/"),
    (["info@trivium.ar"], "mailto:info@trivium.ar"),
    (["+54", "9", "11", "2701-5294"], "https://wa.me/5491127015294"),
    (["+54", "9", "351", "399-4200"], "https://wa.me/5493513994200"),
]

def pages(pdf):
    html = subprocess.run(["pdftotext", "-bbox", pdf, "-"], capture_output=True, text=True, check=True).stdout
    for pm in re.finditer(r'<page width="([\d.]+)" height="([\d.]+)">(.*?)</page>', html, re.S):
        w, h = float(pm.group(1)), float(pm.group(2))
        words = [(float(a), float(b), float(c), float(d), t) for a, b, c, d, t in
                 re.findall(r'<word xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" yMax="([\d.]+)">(.*?)</word>', pm.group(3))]
        yield w, h, words

ETIQUETA = ["Ver", "ficha", "del", "producto", "en", "pro.trivium.ar"]

def marks(pdf, producto=None, solo_etiqueta=False):
    """Un grupo de marcas por página. Ghostscript solo aplica bien /Page 1: por eso
    main() procesa cada página como PDF de una hoja y después las vuelve a unir."""
    grupos = []
    for n, (w, h, words) in enumerate(pages(pdf), 1):
        out = []
        texts = [t for *_, t in words]
        todos = [(ETIQUETA, producto)] if (producto and solo_etiqueta) else \
                ([(ETIQUETA, producto)] if producto else []) + LINKS
        for seq, url in todos:
            if producto and seq == ["pro.trivium.ar"]:
                url = producto          # el sitio del pie lleva a la ficha del producto
            for i in range(len(texts) - len(seq) + 1):
                if texts[i:i + len(seq)] == seq:
                    ws = words[i:i + len(seq)]
                    x0 = min(a for a, *_ in ws) - 1; x1 = max(c for _, _, c, _, _ in ws) + 1
                    y0 = h - max(d for *_, d, _ in ws) - 1; y1 = h - min(b for _, b, *_ in ws) + 1
                    out.append(f"[ /Rect [{x0:.1f} {y0:.1f} {x1:.1f} {y1:.1f}] /Border [0 0 0] "
                               f"/Subtype /Link /Action << /Subtype /URI /URI ({url}) >> /ANN pdfmark")
        grupos.append(out)
    return grupos

def main():
    args = sys.argv[1:]
    producto = None
    solo = "--solo-etiqueta" in args
    if solo:
        args.remove("--solo-etiqueta")
    if "--producto" in args:
        i = args.index("--producto"); producto = args[i + 1]; del args[i:i + 2]
    src = args[0]; dst = args[1] if len(args) > 1 else src
    grupos = marks(src, producto, solo)
    if not any(grupos):
        sys.exit("no se encontró ningún dato de contacto para enlazar")
    tmpdir = tempfile.mkdtemp()
    partes = []
    for n, m in enumerate(grupos, 1):
        ps = os.path.join(tmpdir, f"m{n}.ps"); open(ps, "w").write("\n".join(m) + "\n")
        part = os.path.join(tmpdir, f"p{n}.pdf")
        subprocess.run(["gs", "-q", "-dNOPAUSE", "-dBATCH", "-sDEVICE=pdfwrite", "-dPDFSETTINGS=/printer",
                        f"-dFirstPage={n}", f"-dLastPage={n}", f"-sOutputFile={part}", ps, src], check=True)
        partes.append(part)
    tmp = os.path.join(tmpdir, "final.pdf")
    subprocess.run(["gs", "-q", "-dNOPAUSE", "-dBATCH", "-sDEVICE=pdfwrite", "-dPDFSETTINGS=/printer",
                    f"-sOutputFile={tmp}"] + partes, check=True)
    shutil.move(tmp, dst)
    print(f"✔ {os.path.basename(dst)}: {sum(len(m) for m in grupos)} enlaces en {len(grupos)} página(s)")

if __name__ == "__main__":
    main()
