"""Genera /marcas/ (página de marcas) como HTML estático.

Antes la página armaba la lista por JavaScript y el HTML publicado traía el
contenedor vacío: un crawler casi no veía contenido. Ahora todo sale prerenderizado.

Texto editorial: scripts/marcas_content.py. Equipos, categorías, sellos de origen
y logos salen de data/catalog.json y de assets/img/marcas/. Plantilla: marcas.html.

Uso:
    python3 scripts/generate_marcas.py
"""
import json
import os
from urllib.parse import quote

from generate_pretty_urls import (
    BASE_DIR, SITE_URL, ORG_NAME, ORIGIN_BADGES, brand_logo_rel, breadcrumb_html,
    breadcrumb_jsonld, create_index_file, esc, faq_html, faq_jsonld, make_seo_block,
)
from marcas_content import FAQS, MARCAS, PREMIUM, PROPIA, UPDATED

ROOT = '../'
OG_IMAGE = f"{SITE_URL}/assets/img/og-trivium.png"
WA = "https://wa.me/5491127015294?text="
TITLE = "Marcas de equipos para taller: Rotary Lift, Hofmann, Haweka"


def load(name):
    with open(os.path.join(BASE_DIR, 'data', name), encoding='utf-8') as f:
        return json.load(f)


def wa_link(text):
    return WA + quote(text, safe='')


def flag_chip(bid, label=None):
    b = ORIGIN_BADGES[bid]
    txt = label or ('Marcado CE' if b.get('plain') else b['name'])
    return (f'<a class="marca-chip" href="{ROOT}{esc(b["href"])}">'
            f'<img src="{ROOT}assets/img/iconos/origen/{b["file"]}" alt="">{esc(txt)}</a>')


def origen_chips(slug, prods, info):
    """Chips de origen: con bandera (y link a /origen/) cuando los productos llevan
    sello; texto plano si no."""
    ids = []
    for p in prods:
        for bid in p.get('badges') or []:
            if bid in ORIGIN_BADGES and bid not in ids:
                ids.append(bid)
    ids.sort(key=list(ORIGIN_BADGES).index)   # orden estable: EE. UU., Italia, Alemania, Suecia, Taiwán, CE
    paises = [i for i in ids if ORIGIN_BADGES[i].get('country')]
    chips = []
    if len(paises) == 1:
        chips.append(flag_chip(paises[0], info['origen_txt']))
    elif paises:
        chips.extend(flag_chip(i) for i in paises)
    else:
        chips.append(f'<span class="marca-chip marca-chip--plain">{esc(info["origen_txt"])}</span>')
    if 'ce-ue' in ids:
        chips.append(flag_chip('ce-ue'))
    return ''.join(chips)


def categorias(prods, cats):
    """Categorías raíz de los productos de la marca, en el orden del catálogo."""
    vistos = []
    for p in prods:
        c = cats.get(p['category'], {})
        raiz = c.get('parent') or p['category']
        if raiz not in vistos:
            vistos.append(raiz)
    orden = {c['slug']: i for i, c in enumerate(cats.values())}
    vistos.sort(key=lambda s: orden.get(s, 99))
    return [(s, cats[s].get('seo_name') or cats[s]['name']) for s in vistos if s in cats]


def card_html(brand, info, prods, cats, propia=False):
    slug = brand['slug']
    logo = brand_logo_rel(slug)
    logo_html = (f'<img src="{ROOT}{logo}" alt="Logo de {esc(brand["name"])}" loading="lazy">'
                 if logo else f'<span>{esc(brand["name"])}</span>')
    cat_links = ''.join(f'<a href="{ROOT}categoria/{esc(s)}/">{esc(n)}</a>' for s, n in categorias(prods, cats))
    n = len(prods)
    return (
        f'<article class="marca-card{" marca-propia" if propia else ""}">'
        f'<a class="marca-card__logo" href="{ROOT}marca/{esc(slug)}/" aria-label="{esc(brand["name"])}">{logo_html}</a>'
        f'<div class="marca-card__body">'
        f'<div class="marca-chips">{origen_chips(slug, prods, info)}</div>'
        f'<h3><a href="{ROOT}marca/{esc(slug)}/">{esc(info["nombre_seo"])}</a></h3>'
        f'<p class="resumen">{esc(info["resumen"])}</p>'
        f'<p class="desc">{esc(info["desc"])}</p>'
        f'<div class="marca-cats">{cat_links}</div>'
        f'<div class="marca-actions">'
        f'<a class="btn btn--primary" href="{ROOT}marca/{esc(slug)}/">Ver {n} equipo{"" if n == 1 else "s"}</a>'
        f'<a class="btn btn--ghost" href="{wa_link("Hola, quiero info sobre productos " + brand["name"])}">Consultar</a>'
        f'</div></div></article>'
    )


def main():
    catalog = load('catalog.json')
    brands = {b['slug']: b for b in catalog['brands']}
    cats = {c['slug']: c for c in catalog['categories']}
    por_marca = {s: [p for p in catalog['products'] if p.get('brand') == s] for s in brands}
    n_equipos = len(catalog['products'])
    n_marcas = len(brands)
    paises = {b for p in catalog['products'] for b in (p.get('badges') or [])
              if ORIGIN_BADGES.get(b, {}).get('country')}
    orden = [s for s in PREMIUM if s in brands] + ([PROPIA] if PROPIA in brands else [])
    url = f"{SITE_URL}/marcas/"
    premium_nombres = [brands[s]['name'] for s in PREMIUM if s in brands]
    lista_premium = ', '.join(premium_nombres[:-1]) + ' y ' + premium_nombres[-1]

    desc = (f"Marcas que representamos en Argentina: {lista_premium}, más la línea propia Trivium Pro. "
            f"Origen, equipos de cada marca y servicio técnico oficial en todo el país.")

    # --- hero ---
    strip = ''.join(
        f'<a href="{ROOT}marca/{esc(s)}/" aria-label="{esc(brands[s]["name"])}">'
        + (f'<img src="{ROOT}{brand_logo_rel(s)}" alt="{esc(brands[s]["name"])}">' if brand_logo_rel(s)
           else f'<b>{esc(brands[s]["name"])}</b>')
        + '</a>' for s in orden)
    hero = (
        '<section class="marcas-hero"><div class="container">'
        f'<div class="breadcrumbs">{breadcrumb_html([("Inicio", ""), ("Marcas", None)], ROOT)}</div>'
        '<h1>Marcas de equipamiento para taller<em>que representamos en Argentina.</em></h1>'
        '<p class="lead">Elevadores, alineadoras, balanceadoras, desarmadoras, accesorios de balanceo y '
        'aire comprimido de marcas líderes, y la línea propia Trivium Pro. Cada marca fue elegida por su '
        'calidad, respaldo técnico y disponibilidad de repuestos originales.</p>'
        '<div class="marcas-stats">'
        f'<div><b>{n_marcas}</b><span>marcas</span></div>'
        f'<div><b>{n_equipos}</b><span>equipos en catálogo</span></div>'
        f'<div><b>{len(paises)}</b><span>países de origen</span></div>'
        '<div><b>Todo el país</b><span>envíos y servicio técnico</span></div>'
        '</div>'
        f'<div class="marcas-strip">{strip}</div>'
        '</div></section>'
    )

    # --- respuesta + tarjetas ---
    respuesta = (
        f'<p class="marcas-respuesta"><strong>En resumen:</strong> Trivium Pro representa en Argentina a '
        f'{esc(lista_premium)}, y tiene su línea propia Trivium Pro. Ofrece {n_equipos} equipos '
        f'(elevadores, alineadoras, balanceadoras, desarmadoras, accesorios de balanceo y aire comprimido) '
        f'con garantía y servicio técnico oficial en todo el país. La instalación se cotiza aparte.</p>')
    premium_cards = ''.join(card_html(brands[s], MARCAS[s], por_marca[s], cats) for s in PREMIUM if s in brands)
    # Octavo lugar de la grilla (4 columnas): invitación a consultar por una marca o equipo puntual.
    premium_cards += (
        '<article class="marca-card marca-card--cta"><h3>¿Buscás otra marca o un equipo puntual?</h3>'
        '<p>Contanos qué necesitás y te asesoramos.</p>'
        f'<a class="btn btn--primary" href="{wa_link("Hola, busco una marca o equipo puntual.")}">Consultar por WhatsApp</a>'
        '</article>')
    propia_html = (card_html(brands[PROPIA], MARCAS[PROPIA], por_marca[PROPIA], cats, propia=True)
                   if PROPIA in brands else '')

    # --- comparativa ---
    filas = []
    for s in orden:
        i = MARCAS[s]
        cs = ', '.join(n for _, n in categorias(por_marca[s], cats))
        filas.append(
            f'<tr><td><a href="{ROOT}marca/{esc(s)}/">{esc(brands[s]["name"])}</a></td>'
            f'<td>{esc(i["origen_txt"])}</td><td>{esc(cs)}</td><td>{len(por_marca[s])}</td>'
            f'<td>{esc(i["ideal"])}</td></tr>')
    tabla = ('<div class="marcas-tabla"><table><thead><tr><th>Marca</th><th>Origen</th><th>Qué ofrece</th>'
             '<th>Equipos</th><th>Ideal para</th></tr></thead><tbody>' + ''.join(filas) + '</tbody></table></div>')

    # --- cómo elegir / origen ---
    origen_links = ''.join(
        f'<li><a href="{ROOT}{esc(b["href"])}">{esc(b["text"] if not b.get("plain") else "Marcado CE")}</a></li>'
        for b in ORIGIN_BADGES.values())
    texto = (
        '<div class="marcas-texto">'
        '<h2>Cómo elegir entre marcas</h2>'
        '<p>Las marcas premium importadas son la opción para un uso intensivo: talleres de alto volumen, '
        'concesionarias y flotas. La línea propia Trivium Pro apunta a talleres y gomerías que arrancan o amplían '
        'capacidad, con equipos de precio más accesible, marcado CE y respaldo local de posventa y repuestos. '
        'Estas guías ayudan a decidir:</p>'
        '<ul>'
        f'<li><a href="{ROOT}guias/elevadores-para-taller/">Elevador para taller: guía de compra</a></li>'
        f'<li><a href="{ROOT}guias/alineadoras-3d/">Alineadora 3D: guía de compra</a></li>'
        f'<li><a href="{ROOT}guias/balanceadoras-de-ruedas/">Balanceadora de ruedas: guía de compra</a></li>'
        f'<li><a href="{ROOT}guias/desarmadoras-de-neumaticos/">Desarmadora de neumáticos: guía de compra</a></li>'
        f'<li><a href="{ROOT}guias/equipos-de-taller-economicos/">Equipos de taller económicos: la línea Trivium Pro</a></li>'
        '</ul>'
        '<h2>Origen de fabricación</h2>'
        '<p>El país de fabricación lo declara el fabricante de cada modelo y se muestra con un sello sobre la '
        'foto: una misma marca puede fabricar en más de un país. Podés ver los equipos por origen:</p>'
        f'<ul>{origen_links}</ul>'
        f'<p><a href="{ROOT}origen/">Ver el índice de origen y marcado CE</a>.</p>'
        '</div>')
    cta = (f'<div class="marcas-texto"><p><strong>¿No sabés qué marca conviene a tu taller?</strong> Contanos '
           f'qué servicios hacés y te recomendamos. Enviamos e instalamos en <a href="{ROOT}zonas/">todo el '
           f'país</a> (la instalación se cotiza aparte).</p>'
           f'<a class="btn btn--primary" href="{wa_link("Hola, quiero asesoramiento para elegir una marca.")}">'
           f'Consultar por WhatsApp</a></div>')

    pagina = (
        hero
        + '<main class="marcas-main"><div class="container">'
        + respuesta
        + '<h2>Marcas premium importadas</h2>'
        + '<p class="sub">Equipos de las marcas líderes en cada categoría.</p>'
        + f'<div class="marca-grid">{premium_cards}</div>'
        + '<h2>Marca propia</h2>'
        + '<p class="sub">La línea económica de Trivium, con marcado CE.</p>'
        + propia_html
        + '<h2>Comparativa de marcas</h2>'
        + '<p class="sub">Origen, qué ofrece cada marca y para quién conviene.</p>'
        + tabla
        + texto
        + cta
        + '</div></main>'
        + '<section class="cat-faq">' + faq_html("Preguntas frecuentes sobre las marcas", FAQS) + '</section>'
    )

    # --- datos estructurados ---
    items = []
    for pos, s in enumerate(orden, 1):
        i = MARCAS[s]; logo = brand_logo_rel(s)
        brand_ld = {
            "@type": "Brand",
            "@id": f"{SITE_URL}/marca/{s}/#brand",
            "name": brands[s]['name'],
            "alternateName": i['nombre_seo'],
            "url": f"{SITE_URL}/marca/{s}/",
            "description": f"{i['resumen']} {i['desc']}",
        }
        if logo:
            brand_ld["logo"] = f"{SITE_URL}/{logo}"
        items.append({"@type": "ListItem", "position": pos, "item": brand_ld})
    jsonld = [
        breadcrumb_jsonld([("Inicio", SITE_URL + '/'), ("Marcas", url)]),
        {
            "@context": "https://schema.org",
            "@type": "CollectionPage",
            "name": "Marcas de equipamiento para taller que representamos en Argentina",
            "url": url,
            "description": desc,
            "inLanguage": "es-AR",
            "dateModified": UPDATED,
            "isPartOf": {"@type": "WebSite", "name": ORG_NAME, "url": SITE_URL + '/'},
            "mainEntity": {"@type": "ItemList", "numberOfItems": len(items), "itemListElement": items},
        },
        faq_jsonld(FAQS),
    ]
    create_index_file(
        os.path.join(BASE_DIR, 'marcas'), os.path.join(BASE_DIR, 'marcas.html'), 1,
        title=TITLE,
        og={'type': 'website', 'title': TITLE, 'description': desc, 'image': OG_IMAGE, 'url': url},
        seo=make_seo_block(url, desc, jsonld),
        body={'marcas-page': pagina},
    )
    print(f"  -> marcas/ ({n_marcas} marcas, {n_equipos} equipos)")


if __name__ == '__main__':
    main()
