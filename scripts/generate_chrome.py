"""Cachea el header y el footer renderizados en data/chrome.json.

site.js los inyecta en el cliente con mountChrome(), así que un crawler ve la
home con un solo enlace interno: toda la navegación vive en la capa de
JavaScript, que Google resuelve recién en una segunda pasada y con menos
garantías. Los demás generadores hornean este HTML en cada página.

En vez de portar renderHeader() y renderFooter() a Python — que duplicaría los
SVG, CAT_ICONS y el menú mobile, y se desincronizaría al primer cambio — se
ejecuta el JS real en Chromium y se guarda el resultado.

rootPath() lee <meta name="tv-root">, así que se renderiza con un centinela y
queda un HTML reusable en cualquier profundidad: cada generador reemplaza
%%ROOT%% por los "../" que le correspondan.

Hay que correrlo sólo cuando cambian la navegación o el footer en site.js.

Uso:
    python3 scripts/generate_chrome.py
"""

import json
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SENTINEL = '%%ROOT%%'
TARGET = os.path.join(BASE_DIR, 'data', 'chrome.json')

PAGE = f"""<!doctype html>
<html lang="es"><head><meta charset="utf-8">
<meta name="tv-root" content="{SENTINEL}">
</head><body>
<div id="site-header"></div>
<div id="site-footer"></div>
<script src="{SENTINEL}assets/js/site.js"></script>
<script>mountChrome('');</script>
</body></html>
"""


def main():
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        sys.exit("Falta playwright: pip install playwright && playwright install chromium")

    scratch = os.path.join(BASE_DIR, '.chrome-scratch.html')
    # El <script src> tiene que resolver de verdad, así que para cargar la
    # página se apunta a la raíz del repo; el centinela queda igual en la salida.
    with open(scratch, 'w', encoding='utf-8') as f:
        f.write(PAGE.replace(f'src="{SENTINEL}assets', 'src="assets'))

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            errores = []
            page.on('pageerror', lambda e: errores.append(str(e)))
            page.goto('file://' + scratch)
            page.wait_for_timeout(500)
            if errores:
                sys.exit(f"El JS falló al renderizar: {errores[0][:200]}")
            header = page.inner_html('#site-header')
            footer = page.inner_html('#site-footer')
            browser.close()
    finally:
        if os.path.exists(scratch):
            os.remove(scratch)

    if not header.strip() or not footer.strip():
        sys.exit("mountChrome() no devolvió contenido")
    if SENTINEL not in header:
        sys.exit(f"No aparece el centinela {SENTINEL} en el header: rootPath() no se aplicó")

    with open(TARGET, 'w', encoding='utf-8') as f:
        json.dump({'root_token': SENTINEL, 'header': header, 'footer': footer},
                  f, ensure_ascii=False, indent=1)

    links = header.count('href=') + footer.count('href=')
    print(f"✔ data/chrome.json — header {len(header)} B, footer {len(footer)} B, {links} enlaces")


if __name__ == '__main__':
    main()
