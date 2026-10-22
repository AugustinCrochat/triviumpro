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
            if f in CATALOGOS: continue
            m.setdefault(f, (p, brands.get(p.get("brand"), ""), cats.get(p.get("category"), "")))
    return m

# Fichas de varios ítems (scripts/generate_haweka_catalogos.py): título y asunto propios.
CATALOGOS = {
    "web-ficha-accesorios-de-alineacion-y-balanceo.pdf": "Accesorios Haweka para alineación y balanceo",
    "web-ficha-conos-y-mangas.pdf": "Conos y mangas de centrado Haweka",
    "39-ficha-805-818-000-805-995-000-probike-haweka.pdf": "Dispositivo de fijación ProBike Haweka: Standard y Power Clamp",
    "ficha-haweka-210-400-001-4-conos-expandibles-exhibidor.pdf": "Conos expandibles y QuickPlate IV Haweka con exhibidor",
}

def aplicar_catalogo(ruta, nombre):
    titulo = f"Ficha técnica {nombre} | Trivium Pro"
    ps = (f"[ /Title {ps_str(titulo)} /Author (Trivium Pro) /Subject {ps_str(nombre + ': códigos, medidas y usos')} "
          f"/Keywords {ps_str('Haweka, accesorios de balanceo, Trivium Pro, Argentina')} /Creator (Trivium Pro) /DOCINFO pdfmark\n")
    tmp = tempfile.mkdtemp(); psf = os.path.join(tmp, "m.ps"); open(psf, "w", encoding="latin-1").write(ps)
    out = os.path.join(tmp, "o.pdf")
    subprocess.run(["gs", "-q", "-dNOPAUSE", "-dBATCH", "-sDEVICE=pdfwrite", "-dPDFSETTINGS=/printer",
                    f"-sOutputFile={out}", ruta, psf], check=True, capture_output=True)
    shutil.move(out, ruta)
    return titulo

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
    objetivos = [os.path.basename(a) for a in sys.argv[1:]] or list(m) + list(CATALOGOS)
    n = 0
    for f in objetivos:
        ruta = os.path.join(ROOT, "assets/pdf", f)
        if f in CATALOGOS and os.path.exists(ruta):
            t = aplicar_catalogo(ruta, CATALOGOS[f]); n += 1
            print("✔", t)
        elif f in m and os.path.exists(ruta):
            t = aplicar(ruta, *m[f]); n += 1
            if n <= 3 or len(objetivos) == 1:
                print("✔", t)
    print(f"{n} fichas con título y metadatos")
