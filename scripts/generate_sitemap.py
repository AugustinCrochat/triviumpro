"""
Genera sitemap.xml y robots.txt a partir de data/catalog.json y data/blog.json.

Uso:
    python3 scripts/generate_sitemap.py

Salida: sitemap.xml y robots.txt en la raíz del sitio.

Se excluyen las secciones marcadas noindex en vercel.json (cotizacion,
lista de revendedores).
"""

import json
import os
from datetime import date
from xml.sax.saxutils import escape

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
from site_config import SITE_URL

# Páginas estáticas: (ruta, prioridad, frecuencia)
STATIC_PAGES = [
    ("/", "1.0", "weekly"),
    ("/catalogo/", "0.9", "weekly"),
    ("/lista-precios/", "0.8", "daily"),
    ("/marcas/", "0.7", "monthly"),
    ("/instalacion-posventa-y-servicios/", "0.7", "monthly"),
    ("/nosotros/", "0.5", "yearly"),
    ("/contacto/", "0.5", "yearly"),
    ("/blog/", "0.7", "weekly"),
]


def load(name):
    with open(os.path.join(BASE_DIR, "data", name), encoding="utf-8") as f:
        return json.load(f)


def url_entry(loc, lastmod=None, changefreq=None, priority=None):
    parts = [f"    <loc>{escape(loc)}</loc>"]
    if lastmod:
        parts.append(f"    <lastmod>{lastmod}</lastmod>")
    if changefreq:
        parts.append(f"    <changefreq>{changefreq}</changefreq>")
    if priority:
        parts.append(f"    <priority>{priority}</priority>")
    return "  <url>\n" + "\n".join(parts) + "\n  </url>"


def main():
    catalog = load("catalog.json")
    posts = load("blog.json")
    today = date.today().isoformat()

    entries = []

    for path, priority, freq in STATIC_PAGES:
        entries.append(url_entry(SITE_URL + path, today, freq, priority))

    # Páginas pilar /guias/: salen de scripts/guias_content.py
    from guias_content import GUIAS, UPDATED
    entries.append(url_entry(f"{SITE_URL}/guias/", UPDATED, "monthly", "0.8"))
    for g in GUIAS:
        entries.append(url_entry(f"{SITE_URL}/guias/{g['slug']}/", UPDATED, "monthly", "0.8"))

    for c in catalog["categories"]:
        entries.append(
            url_entry(f"{SITE_URL}/categoria/{c['slug']}/", today, "weekly", "0.8")
        )

    for b in catalog["brands"]:
        entries.append(
            url_entry(f"{SITE_URL}/marca/{b['slug']}/", today, "monthly", "0.7")
        )

    for p in catalog["products"]:
        entries.append(
            url_entry(f"{SITE_URL}/producto/{p['slug']}/", today, "monthly", "0.8")
        )

    for post in posts:
        # date viene como 2025-10-29T23:49:21
        lastmod = post.get("date", "")[:10] or today
        entries.append(
            url_entry(f"{SITE_URL}/blog/{post['slug']}/", lastmod, "yearly", "0.6")
        )

    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(entries)
        + "\n</urlset>\n"
    )

    sitemap_path = os.path.join(BASE_DIR, "sitemap.xml")
    with open(sitemap_path, "w", encoding="utf-8") as f:
        f.write(xml)

    # Sin Disallow a propósito. Las secciones privadas se sacan del índice con
    # X-Robots-Tag: noindex desde _headers, y para que Google lea ese header
    # necesita poder rastrear la página: un Disallow se lo impediría y la URL
    # quedaría indexada igual. Además robots.txt es público, así que listar
    # /lista-revendedores-<slug>/ acá publicaría el slug que se busca ocultar.
    robots = (
        "User-agent: *\n"
        "Allow: /\n"
        "\n"
        f"Sitemap: {SITE_URL}/sitemap.xml\n"
    )
    with open(os.path.join(BASE_DIR, "robots.txt"), "w", encoding="utf-8") as f:
        f.write(robots)

    print(f"✔ sitemap.xml — {len(entries)} URLs")
    print("✔ robots.txt")


if __name__ == "__main__":
    main()
