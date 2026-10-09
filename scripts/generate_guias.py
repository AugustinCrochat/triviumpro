"""Genera las páginas pilar /guias/<slug>/ y el índice /guias/.

Fuente del texto: scripts/guias_content.py. Los datos de cada equipo de la
tabla comparativa salen de data/catalog.json, así que no hay que mantenerlos
a mano. Plantilla: guia.html.

Uso:
    python3 scripts/generate_guias.py
"""
import html as html_lib
import json
import os

from generate_pretty_urls import (
    BASE_DIR, SITE_URL, ORG_NAME, breadcrumb_html, breadcrumb_jsonld, clamp,
    create_index_file, esc, faq_html, faq_jsonld, make_seo_block,
    make_og_block, blog_links_html, replace_empty_el,
)
from guias_content import GUIAS, UPDATED

ROOT2 = '../../'
OG_IMAGE = f"{SITE_URL}/assets/img/og-trivium.png"


def load(name):
    with open(os.path.join(BASE_DIR, 'data', name), encoding='utf-8') as f:
        return json.load(f)


def capacidad(prod):
    cap = (prod.get('capacity') or '').strip()
    return cap if cap and cap != '—' else '—'


def tabla_html(guia, products, brands):
    rows = []
    for slug, nota in guia['tabla']['slugs']:
        p = products[slug]
        marca = brands.get(p.get('brand'), {}).get('name', '—')
        rows.append(
            f'<tr><td><a href="{ROOT2}producto/{esc(slug)}/">{esc(html_lib.unescape(p["name"]))}</a></td>'
            f'<td>{esc(marca)}</td><td>{esc(capacidad(p))}</td><td>{esc(nota)}</td></tr>'
        )
    return ('<div class="tabla-wrap"><table><thead><tr><th>Modelo</th><th>Marca</th>'
            '<th>Capacidad</th><th>Para qué sirve</th></tr></thead><tbody>'
            + ''.join(rows) + '</tbody></table></div>')


def cta_html(guia, cats):
    cat = cats[guia['category']]
    return (f'<div class="cta"><p><strong>¿Dudas con qué modelo elegir?</strong> Contanos tu taller '
            f'y te recomendamos el equipo. Mirá también el catálogo completo de '
            f'<a href="{ROOT2}categoria/{esc(cat["slug"])}/">{esc(cat["seo_name"] if cat.get("seo_name") else cat["name"])}</a>.</p>'
            f'<a class="btn btn--primary" href="https://wa.me/5491127015294?text='
            f'Hola%2C%20quiero%20asesoramiento%20sobre%20{esc(guia["slug"])}.">'
            f'Consultar por WhatsApp</a></div>')


def main():
    catalog = load('catalog.json')
    products = {p['slug']: p for p in catalog['products']}
    brands = {b['slug']: b for b in catalog['brands']}
    cats = {c['slug']: c for c in catalog['categories']}
    blog_by_slug = {p['slug']: p for p in load('blog.json')}
    template = os.path.join(BASE_DIR, 'guia.html')

    for guia in GUIAS:
        url = f"{SITE_URL}/guias/{guia['slug']}/"
        body = guia['intro'] + guia['secciones'].replace('{{TABLA}}', tabla_html(guia, products, brands))
        if 'class="cta"' not in body:
            body += cta_html(guia, cats)

        crumbs = [("Inicio", ""), ("Guías", "guias/"), (guia['h1'], None)]
        jsonld = [
            breadcrumb_jsonld([("Inicio", SITE_URL + '/'), ("Guías", SITE_URL + '/guias/'),
                               (guia['h1'], url)]),
            {
                "@context": "https://schema.org",
                "@type": "Article",
                "headline": guia['title'],
                "description": guia['description'],
                "url": url,
                "mainEntityOfPage": url,
                "inLanguage": "es-AR",
                "dateModified": UPDATED,
                "image": OG_IMAGE,
                "author": {"@type": "Organization", "name": ORG_NAME, "url": SITE_URL + '/'},
                "publisher": {"@type": "Organization", "name": ORG_NAME,
                              "logo": {"@type": "ImageObject",
                                       "url": f"{SITE_URL}/assets/img/logo-trivium.svg"}},
            },
            faq_jsonld(guia['faqs']),
        ]
        create_index_file(
            os.path.join(BASE_DIR, 'guias', guia['slug']), template, 2,
            title=guia['title'],
            og={'type': 'article', 'title': guia['title'], 'description': guia['description'],
                'image': OG_IMAGE, 'url': url},
            seo=make_seo_block(url, guia['description'], jsonld),
            body={
                'crumbs': breadcrumb_html(crumbs, ROOT2),
                'guia-title': esc(guia['h1']),
                'guia-updated': f"Actualizado: {UPDATED}",
                'guia-body': body,
                'guia-faq': faq_html("Preguntas frecuentes", guia['faqs']),
                'guia-posts': blog_links_html("Notas relacionadas", guia['posts'], blog_by_slug, ROOT2),
            },
        )
        print(f"  -> guias/{guia['slug']}/")

    # Índice /guias/
    url = f"{SITE_URL}/guias/"
    desc = ("Guías de compra de equipamiento para taller y gomería: elevadores, alineadoras, "
            "balanceadoras y desarmadoras. Cómo elegir, qué comparar y qué modelos hay.")
    items = ''.join(
        f'<li><a href="{esc(g["slug"])}/"><strong>{esc(g["h1"])}</strong>'
        f'<span>{esc(g["description"])}</span></a></li>' for g in GUIAS)
    index_body = ('<p>Guías técnicas y de compra del equipo de Trivium Pro, escritas a partir de '
                  'las fichas de cada equipo y de las instalaciones que hacemos en todo el país.</p>'
                  f'<ul class="guia-lista">{items}</ul>')
    jsonld = [
        breadcrumb_jsonld([("Inicio", SITE_URL + '/'), ("Guías", url)]),
        {"@context": "https://schema.org", "@type": "CollectionPage", "name": "Guías de compra",
         "url": url, "description": desc},
    ]
    create_index_file(
        os.path.join(BASE_DIR, 'guias'), template, 1,
        title="Guías de compra de equipamiento para taller",
        og={'type': 'website', 'title': 'Guías de compra de equipamiento para taller',
            'description': desc, 'image': OG_IMAGE, 'url': url},
        seo=make_seo_block(url, desc, jsonld),
        body={'crumbs': breadcrumb_html([("Inicio", ""), ("Guías", None)], '../'),
              'guia-title': 'Guías de compra', 'guia-updated': '',
              'guia-body': index_body, 'guia-faq': '', 'guia-posts': ''},
    )
    print("  -> guias/")


if __name__ == '__main__':
    main()
