#!/usr/bin/env python3
"""Pone título, autor, asunto y palabras clave a las fichas PDF (lo que muestran el navegador,
Google y los LLM; antes salían como "f3.html" o "Microsoft Word - ...").

Título:  "Ficha técnica <producto> | Trivium Pro"
Asunto:  el resumen del producto; palabras clave: marca, categoría, capacidad, modelo, SKU.
Sale de data/catalog.json (el primer producto que enlaza ese PDF).

Uso: python3 scripts/set_ficha_metadata.py            (todas las fichas del catálogo)
     python3 scripts/set_ficha_metadata.py ficha.pdf  (una)
"""
import json, os, re, shutil, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def esc(s):
    s = s.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
    return s

def ps_str(s):
    # PDFDocEncoding ≈ Latin-1 para el español; fuera de eso se reemplaza
    return "(" + esc(s.encode("latin-1", "replace").decode("latin-1")) + ")"

def mapa():
    d = json.load(open(os.path.join(ROOT, "data/catalog.json"), encoding="utf-8"))
    brands = {b["slug"]: b["name"] for b in d["brands"]}
    cats = {c["slug"]: c["name"] for c in d["categories"]}
    m = {}
    for p in d["products"]:
        for f in re.findall(r'href="assets/pdf/([^"]+\.pdf)"', p.get("html_description", "")):
            m.setdefault(f, (p, brands.get(p.get("brand"), ""), cats.get(p.get("category"), "")))
    return m

def aplicar(ruta, p, marca, cat):
    titulo = f"Ficha técnica {p['name']}" + ("" if "Trivium Pro" in p["name"] else " | Trivium Pro")
    asunto = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", p.get("summary", ""))).strip() or p["name"]
    claves = ", ".join(x for x in (marca, cat, p.get("capacity") if p.get("capacity") not in (None, "—") else "", p.get("sku", ""),
                                   "Trivium Pro", "Argentina") if x)
    ps = (f"[ /Title {ps_str(titulo)} /Author (Trivium Pro) /Subject {ps_str(asunto)} /Keywords {ps_str(claves)} "
          "/Creator (Trivium Pro) /DOCINFO pdfmark\n")
    tmp = tempfile.mkdtemp(); psf = os.path.join(tmp, "m.ps"); open(psf, "w", encoding="latin-1").write(ps)
    out = os.path.join(tmp, "o.pdf")
    subprocess.run(["gs", "-q", "-dNOPAUSE", "-dBATCH", "-sDEVICE=pdfwrite", "-dPDFSETTINGS=/printer",
                    f"-sOutputFile={out}", ruta, psf], check=True, capture_output=True)
    shutil.move(out, ruta)
    return titulo

if __name__ == "__main__":
    m = mapa()
    objetivos = [os.path.basename(a) for a in sys.argv[1:]] or list(m)
    n = 0
    for f in objetivos:
        ruta = os.path.join(ROOT, "assets/pdf", f)
        if f in m and os.path.exists(ruta):
            t = aplicar(ruta, *m[f]); n += 1
            if n <= 3 or len(objetivos) == 1:
                print("✔", t)
    print(f"{n} fichas con título y metadatos")
