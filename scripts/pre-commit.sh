#!/bin/sh
# Regenera páginas, SEO y sitemap si cambiaron los datos
if git diff --cached --name-only | grep -qE '^(data/(catalog|blog)\.json|scripts/guias_content\.py|scripts/related\.py|scripts/origenes_content\.py|scripts/marcas_content\.py|scripts/zonas_content\.py|marcas\.html|guia\.html|origen\.html)$'; then
  echo "▶ Datos cambiados — regenerando páginas, SEO y sitemap..."
  python3 scripts/generate_pretty_urls.py \
    && python3 scripts/generate_og_tags.py \
    && python3 scripts/generate_guias.py \
    && python3 scripts/generate_origenes.py \
    && python3 scripts/generate_marcas.py \
    && python3 scripts/generate_zonas.py \
    && python3 scripts/generate_mapa.py \
    && python3 scripts/generate_sitemap.py \
    && python3 scripts/generate_llms_txt.py \
    && python3 scripts/generate_llms_full.py || exit 1
  git add guias/ origen/ marcas/ zonas/ mapa-del-sitio/ producto/ blog/ categoria/ marca/ nosotros/ catalogo/ instalacion-posventa-y-servicios/ contacto/ marcas/ index.html sitemap.xml robots.txt llms.txt llms-full.txt llms-blog.txt feed.xml data/blog.js 2>/dev/null
fi
# worker.js se genera desde redirects.map: si no, quedan desincronizados
if git diff --cached --name-only | grep -q '^redirects\.map$'; then
  echo "▶ redirects.map cambió — regenerando worker.js..."
  python3 scripts/generate_worker.py || exit 1
  git add worker.js
fi
# El header y el footer horneados salen de site.js: si cambia la navegación,
# data/chrome.json queda viejo y el HTML servido difiere de lo que renderiza el JS.
if git diff --cached --name-only | grep -q '^assets/js/site\.js$'; then
  echo "⚠  site.js cambió. Si tocaste la navegación o el footer, corré:"
  echo "     python3 scripts/generate_chrome.py && python3 scripts/generate_pretty_urls.py && python3 scripts/generate_og_tags.py"
fi
