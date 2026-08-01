#!/bin/sh
# Regenera páginas, SEO y sitemap si cambiaron los datos
if git diff --cached --name-only | grep -qE '^data/(catalog|blog)\.json$'; then
  echo "▶ Datos cambiados — regenerando páginas, SEO y sitemap..."
  python3 scripts/generate_pretty_urls.py \
    && python3 scripts/generate_og_tags.py \
    && python3 scripts/generate_sitemap.py || exit 1
  git add producto/ blog/ categoria/ marca/ nosotros/ catalogo/ instalacion-posventa-y-servicios/ contacto/ marcas/ sitemap.xml robots.txt 2>/dev/null
fi
# worker.js se genera desde redirects.map: si no, quedan desincronizados
if git diff --cached --name-only | grep -q '^redirects\.map$'; then
  echo "▶ redirects.map cambió — regenerando worker.js..."
  python3 scripts/generate_worker.py || exit 1
  git add worker.js
fi
