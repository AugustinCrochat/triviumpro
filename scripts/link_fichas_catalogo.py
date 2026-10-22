#!/usr/bin/env python3
"""Apunta cada producto a su ficha técnica generada (assets/pdf/ficha-tecnica-<slug>.pdf):
reemplaza el href del botón "Ficha Técnica" en html_description, o crea el botón si el
producto no tenía ficha. Después regenera data/catalog.js. Los PDF viejos quedan en
assets/pdf/ (las URLs ya indexadas siguen funcionando).

Uso: python3 scripts/link_fichas_catalogo.py
"""
import json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import generate_fichas as gf

ROOT = gf.ROOT
BTN = ('<div class="product-page-description"><div class="product-page-button-container">'
       '<a class="product-page-btn product-page-btn-pdf" href="{href}" target="_blank" rel="noopener">Ficha Técnica</a></div></div>')

def main():
    p = os.path.join(ROOT, "data/catalog.json")
    d = json.load(open(p, encoding="utf-8"))
    cambiados = creados = 0
    for prod in d["products"]:
        if prod["slug"] in gf.YA_NUEVAS: continue
        nuevo = f"assets/pdf/ficha-tecnica-{prod['slug']}.pdf"
        if not os.path.exists(os.path.join(ROOT, nuevo)): continue
        t = prod.get("html_description", "") or ""
        if f'href="{nuevo}"' in t: continue
        pdfs = re.findall(r'(<a[^>]*product-page-btn-pdf[^>]*href=")([^"]+\.pdf)(")', t)
        if pdfs:
            t = re.sub(r'(<a[^>]*product-page-btn-pdf[^>]*href=")[^"]+\.pdf(")', r'\g<1>' + nuevo + r'\g<2>', t, count=1)
            cambiados += 1
        elif re.search(r'href="assets/pdf/[^"]+\.pdf"', t):
            t = re.sub(r'href="assets/pdf/[^"]+\.pdf"', f'href="{nuevo}"', t, count=1); cambiados += 1
        elif "product-page-button-container" in t:
            t = t.replace('</div>', f'<a class="product-page-btn product-page-btn-pdf" href="{nuevo}" target="_blank" rel="noopener">Ficha Técnica</a></div>', 1); creados += 1
        else:
            t = BTN.format(href=nuevo) + t; creados += 1
        prod["html_description"] = t
    json.dump(d, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    with open(os.path.join(ROOT, "data/catalog.js"), "w", encoding="utf-8") as f:
        f.write("window.CATALOG_DATA = "); json.dump(d, f, ensure_ascii=False); f.write(";")
    print(f"✔ {cambiados} botones repuntados, {creados} creados")

if __name__ == "__main__":
    main()
