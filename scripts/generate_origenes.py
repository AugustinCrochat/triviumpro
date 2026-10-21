"""Genera las páginas /origen/<slug>/ (una por sello de origen y la de marcado CE)
y el índice /origen/.

Fuente del texto: scripts/origenes_content.py. Los equipos de cada página salen
del campo "badges" de data/catalog.json, así que si se carga un sello nuevo o
se cambia el de un producto, la página se regenera sola. Plantillas: origen.html
(página de sello, con grilla de productos) y guia.html (índice).

Uso:
    python3 scripts/generate_origenes.py
"""
import html as html_lib
import json
import os
from collections import OrderedDict

from generate_pretty_urls import (
    BASE_DIR, SITE_URL, ORG_NAME, ORIGIN_BADGES, breadcrumb_html, breadcrumb_jsonld,
    create_index_file, esc, faq_html, faq_jsonld, itemlist_jsonld, load_public_offers,
    make_seo_block, blog_links_html, product_card_html,
)
from origenes_content import ORIGENES, UPDATED

ROOT2 = '../../'
OG_IMAGE = f"{SITE_URL}/assets/img/og-trivium.png"
WA = "https://wa.me/5491127015294?text="


def load(name):
    with open(os.path.join(BASE_DIR, 'data', name), encoding='utf-8') as f:
        return json.load(f)


def n_equipos(n):
    return f"{n} equipo" + ("" if n == 1 else "s")


def que_hay_html(prods, brands, cats):
    """Resumen por categoría (con link y marcas) + lista de modelos con link."""
    por_cat = OrderedDict()
    for p in prods:
        por_cat.setdefault(p['category'], []).append(p)
    items = []
    for slug, lst in por_cat.items():
        c = cats.get(slug, {})
        nombre = c.get('seo_name') or c.get('name') or slug
        marcas = sorted({brands[p['brand']]['name'] for p in lst if p.get('brand') in brands})
        resto = f": {', '.join(marcas)}" if marcas else ""
        items.append(f'<li><a href="{ROOT2}categoria/{esc(slug)}/">{esc(nombre)}</a>'
                     f' — {n_equipos(len(lst))}{esc(resto)}</li>')
    modelos = ''.join(
        f'<li><a href="{ROOT2}producto/{esc(p["slug"])}/">{esc(html_lib.unescape(p["name"]))}</a></li>'
        for p in prods)
    return (f'<ul>{"".join(items)}</ul>'
            f'<h3>Todos los modelos</h3><ul class="origen-modelos">{modelos}</ul>')


def cta_html(o):
    msg = f"Hola, quiero consultar por equipos: {o['pais']}."
    return (f'<div class="cta"><p><strong>¿Buscás un equipo puntual?</strong> Contanos tu taller y te '
            f'recomendamos. Enviamos e instalamos en <a href="{ROOT2}zonas/">todo el país</a> '
            f'(la instalación se cotiza aparte).</p>'
            f'<a class="btn btn--primary" href="{WA}{esc(msg.replace(" ", "%20"))}">'
            f'Consultar por WhatsApp</a></div>')


def otros_html(actual):
    lis = ''.join(
        f'<li><a href="../{esc(o["slug"])}/">{esc(o["h1"])}</a></li>'
        for o in ORIGENES if o['slug'] != actual)
    return (f'<h2>Otros orígenes y sellos</h2><ul>{lis}</ul>'
            f'<p><a href="../">Ver el índice de origen y marcado CE</a>.</p>')


def main():
    catalog = load('catalog.json')
    brands = {b['slug']: b for b in catalog['brands']}
    cats = {c['slug']: c for c in catalog['categories']}
    blog_by_slug = {p['slug']: p for p in load('blog.json')}
    offers, _rate = load_public_offers()
    template = os.path.join(BASE_DIR, 'origen.html')

    counts = {o['badge']: sum(1 for p in catalog['products'] if o['badge'] in (p.get('badges') or []))
              for o in ORIGENES}

    for o in ORIGENES:
        prods = [p for p in catalog['products'] if o['badge'] in (p.get('badges') or [])]
        n = len(prods)
        url = f"{SITE_URL}/origen/{o['slug']}/"
        ob = ORIGIN_BADGES[o['badge']]

        def fill(text):
            return text.replace('{{N}}', str(n))

        faqs = [(q, fill(a)) for q, a in o['faqs']]
        body = fill(o['secciones']).replace('{{QUE_HAY}}', que_hay_html(prods, brands, cats))
        body += cta_html(o) + otros_html(o['slug'])

        crumbs = [("Inicio", ""), ("Origen", "origen/"), (o['h1'], None)]
        jsonld = [
            breadcrumb_jsonld([("Inicio", SITE_URL + '/'), ("Origen", SITE_URL + '/origen/'),
                               (o['h1'], url)]),
            {
                "@context": "https://schema.org",
                "@type": "CollectionPage",
                "name": o['h1'],
                "description": o['description'],
                "url": url,
                "inLanguage": "es-AR",
                "dateModified": UPDATED,
                "isPartOf": {"@type": "WebSite", "name": ORG_NAME, "url": SITE_URL + '/'},
                **({"about": {"@type": "Country", "name": o['pais']}} if ob.get('country') else {}),
            },
            itemlist_jsonld(prods),
            faq_jsonld(faqs),
        ]
        marcas_presentes = []
        for b in catalog['brands']:
            k = sum(1 for p in prods if p.get('brand') == b['slug'])
            if k:
                marcas_presentes.append(
                    f'<li><a href="{ROOT2}marca/{esc(b["slug"])}/">{esc(b["name"])}<b>{k}</b></a></li>')
        org_list = ''.join(
            f'<li><a class="{"active" if oo["badge"] == o["badge"] else ""}" '
            f'href="{ROOT2}origen/{esc(oo["slug"])}/">{esc(ORIGIN_BADGES[oo["badge"]]["name"])}'
            f'<b>{counts[oo["badge"]]}</b></a></li>' for oo in ORIGENES)
        brands_by_slug = brands
        grid = ''.join(product_card_html(p, brands_by_slug, ROOT2, offers) for p in prods)
        seo = f'<meta name="tv-badge" content="{esc(o["badge"])}">\n' + make_seo_block(
            url, o['description'], jsonld)

        create_index_file(
            os.path.join(BASE_DIR, 'origen', o['slug']), template, 2,
            title=o['title'],
            og={'type': 'website', 'title': o['title'], 'description': o['description'],
                'image': OG_IMAGE, 'url': url},
            seo=seo,
            body={
                'crumbs': breadcrumb_html(crumbs, ROOT2),
                'org-title': esc(o['h1']),
                'org-tag': esc(o['chip']),
                'org-count': f"{n} productos",
                'count': f"{n} productos",
                'org-intro': f'<div class="respuesta"><p>{fill(o["resumen"])}</p></div>',
                'org-list': org_list,
                'brand-list': ''.join(marcas_presentes),
                'grid': grid,
                'org-body': body,
                'org-faq': faq_html(f"Preguntas frecuentes: {o['h1'].lower()}", faqs),
                'org-posts': blog_links_html("Notas relacionadas", o['posts'], blog_by_slug, ROOT2),
            },
        )
        print(f"  -> origen/{o['slug']}/ ({n} equipos)")

    # --- Índice /origen/ (plantilla de guía) ---
    url = f"{SITE_URL}/origen/"
    desc = ("Origen de fabricación y marcado CE de los equipos de taller de Trivium Pro: Estados "
            "Unidos, Italia, Alemania, Suecia, Taiwán. Qué significa cada sello y qué equipos lo llevan.")
    items = ''.join(
        f'<li><a href="{esc(o["slug"])}/"><strong>{esc(o["h1"])} ({n_equipos(counts[o["badge"]])})</strong>'
        f'<span>{esc(o["description"])}</span></a></li>' for o in ORIGENES)
    faqs = [
        ("¿Por qué Trivium Pro indica el origen de cada equipo?",
         "Porque el país de fabricación define de dónde vienen los repuestos, qué normas siguió el diseño y "
         "qué soporte técnico hay. Es un dato que los talleres y las gomerías suelen pedir al comparar equipos."),
        ("¿El sello es el de la marca o el del equipo?",
         "El del equipo. Una misma marca puede fabricar en más de un país: Hofmann, por ejemplo, tiene "
         "alineadoras y balanceadoras de Estados Unidos, desarmadoras de Italia y una alineadora de camiones de Suecia. Cada producto lleva el "
         "origen que declara su fabricante."),
        ("¿Qué diferencia hay entre un sello Made in y el marcado CE?",
         "Made in indica el país de fabricación. El marcado CE es una declaración de conformidad con la "
         "normativa europea de seguridad y no indica dónde se fabricó el equipo."),
    ]
    body = ('<p>Cada equipo del catálogo muestra sobre la foto un sello con su origen de fabricación o con '
            'el marcado CE. Tocá el sello para ver todos los equipos que lo llevan y qué significa.</p>'
            f'<ul class="guia-lista">{items}</ul>'
            '<h2>Cómo leer estos sellos</h2>'
            '<p>«Made in» indica el país de fabricación declarado por el fabricante de cada modelo, no el '
            'de la marca. El <a href="marcado-ce/">marcado CE</a> es otra cosa: una declaración de '
            'conformidad con la normativa europea que no dice nada sobre el lugar de fabricación.</p>'
            f'<div class="cta"><p><strong>¿Dudas con qué equipo elegir?</strong> Contanos tu taller y te '
            f'recomendamos. Mirá también el <a href="../catalogo/">catálogo completo</a>.</p>'
            f'<a class="btn btn--primary" href="{WA}Hola%2C%20quiero%20consultar%20por%20equipos.">'
            f'Consultar por WhatsApp</a></div>')
    jsonld = [
        breadcrumb_jsonld([("Inicio", SITE_URL + '/'), ("Origen", url)]),
        {"@context": "https://schema.org", "@type": "CollectionPage",
         "name": "Origen y marcado CE de los equipos de taller", "url": url, "description": desc,
         "inLanguage": "es-AR", "dateModified": UPDATED},
        faq_jsonld(faqs),
    ]
    create_index_file(
        os.path.join(BASE_DIR, 'origen'), os.path.join(BASE_DIR, 'guia.html'), 1,
        title="Origen y marcado CE de los equipos de taller",
        og={'type': 'website', 'title': "Origen y marcado CE de los equipos de taller",
            'description': desc, 'image': OG_IMAGE, 'url': url},
        seo=make_seo_block(url, desc, jsonld),
        body={
            'crumbs': breadcrumb_html([("Inicio", ""), ("Origen", None)], '../'),
            'guia-title': "Origen y marcado CE de los equipos de taller",
            'guia-updated': f"Actualizado: {UPDATED}",
            'guia-body': body,
            'guia-faq': faq_html("Preguntas frecuentes", faqs),
        },
    )
    print("  -> origen/")


if __name__ == '__main__':
    main()
