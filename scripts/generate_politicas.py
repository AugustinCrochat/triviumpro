#!/usr/bin/env python3
"""Genera las páginas legales (/terminos-y-condiciones/, /cambios-devoluciones-y-arrepentimiento/,
/envios-y-entregas/, /politica-de-privacidad/) usando de molde el encabezado y el pie de /nosotros/.
El contenido está en scripts/politicas_content.py. Después correr generate_pretty_urls.py para que
les ponga canonical, meta y JSON-LD (están en su lista de páginas sueltas).

Uso: python3 scripts/generate_politicas.py
"""
import html, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from politicas_content import PAGINAS

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def main():
    molde = open(os.path.join(ROOT, "nosotros/index.html"), encoding="utf-8").read()
    i = molde.index('<section class="cat-hero">'); j = molde.index('<div id="site-footer">')
    cabeza, pie = molde[:i], molde[j:]
    pie = pie.replace("mountChrome('nosotros')", "mountChrome('')")
    for p in PAGINAS:
        c = cabeza
        c = re.sub(r"<title>.*?</title>", f"<title>{html.escape(p['title'])} — Trivium Pro</title>", c, count=1, flags=re.S)
        cuerpo = f'''<section class="cat-hero">
  <div class="container">
    <div class="breadcrumbs"><a href="../">Inicio</a><span>/</span> {html.escape(p['crumb'])}</div>
    <h1>{html.escape(p['h1'])}</h1>
  </div>
</section>

<section class="section">
  <div class="container legal">
{p['html']}
  </div>
</section>

'''
        d = os.path.join(ROOT, p["slug"]); os.makedirs(d, exist_ok=True)
        open(os.path.join(d, "index.html"), "w", encoding="utf-8").write(c + cuerpo + pie)
        print("✔", p["slug"])

if __name__ == "__main__":
    main()
