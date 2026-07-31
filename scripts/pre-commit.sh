#!/bin/sh
# Regenerate pages, SEO metadata and sitemap if catalog or blog data changed
if git diff --cached --name-only | grep -qE '^data/(catalog|blog)\.json$'; then
  echo "▶ Datos cambiados — regenerando páginas, SEO y sitemap..."
  python3 scripts/generate_pretty_urls.py \
    && python3 scripts/generate_og_tags.py \
    && python3 scripts/generate_sitemap.py || exit 1
  git add producto/ blog/ categoria/ marca/ nosotros/ catalogo/ instalacion-posventa-y-servicios/ contacto/ marcas/ sitemap.xml robots.txt 2>/dev/null
  echo "✔ Listo."
fi
