"""Genera la página /mapa-del-sitio/: todo el contenido de Trivium Pro en una sola página.

Todo sale de los datos (catalog.json, blog.json) y de los textos de las guías, los
orígenes y las zonas, así que se regenera sola al sumar un equipo, una guía o una nota.
Plantilla: guia.html. Los estilos (.mapa*) están en assets/css/guia.css.

Uso:
    python3 scripts/generate_mapa.py
"""
import html as html_lib
import os
from collections import OrderedDict

from generate_pretty_urls import (
    BASE_DIR, SITE_URL, breadcrumb_html, breadcrumb_jsonld, create_index_file, esc,
    make_seo_block,
)
from generate_guias import load
from guias_content import GUIAS
from origenes_content import ORIGENES
from zonas_content import ZONAS

ROOT = '../'
OG_IMAGE = f"{SITE_URL}/assets/img/og-trivium.png"
MESES = ['ene', 'feb', 'mar', 'abr', 'may', 'jun', 'jul', 'ago', 'sep', 'oct', 'nov', 'dic']
POSTS_A_LA_VISTA = 12

# (ruta, título, descripción corta)
EMPRESA = [
    ('nosotros/', 'Nosotros', 'Quiénes somos y cómo trabajamos.'),
    ('instalacion-posventa-y-servicios/', 'Instalación, posventa y servicios',
     'Instalación (se cotiza aparte), capacitación y servicio técnico.'),
    ('contacto/', 'Contacto', 'WhatsApp, teléfono, mail y dirección.'),
    ('marcas/', 'Marcas', 'Las marcas que representamos y el origen de cada equipo.'),
]
POLITICAS = [
    ('envios-y-entregas/', 'Envíos y entregas', 'Cómo se envía y entrega a todo el país.'),
    ('cambios-devoluciones-y-arrepentimiento/', 'Cambios, devoluciones y arrepentimiento',
     'Plazos y pasos, incluido el botón de arrepentimiento.'),
    ('terminos-y-condiciones/', 'Términos y condiciones', 'Condiciones de uso y de compra.'),
    ('politica-de-privacidad/', 'Política de privacidad', 'Qué datos se guardan y para qué.'),
]


def txt(s):
    return esc(html_lib.unescape(s or ''))


def n_eq(n):
    return f'{n} equipo' + ('' if n == 1 else 's')


def lista(items):
    """items: [(href, título, descripción)] → <ul class="mapa-lista"> con descripción corta."""
    lis = ''.join(
        f'<li><a href="{ROOT}{esc(h)}"><strong>{txt(t)}</strong>'
        + (f'<span>{txt(d)}</span>' if d else '') + '</a></li>' for h, t, d in items)
    return f'<ul class="mapa-lista">{lis}</ul>'


def plegable(titulo, lis, abierto=False):
    return (f'<details class="mapa-det"{" open" if abierto else ""}><summary>{titulo}</summary>'
            f'<ul class="mapa-cols">{lis}</ul></details>')


def seccion(id_, titulo, intro, cuerpo):
    return f'<section id="{id_}" class="mapa-sec"><h2>{esc(titulo)}</h2><p>{intro}</p>{cuerpo}</section>'


def main():
    catalog = load('catalog.json')
    posts = sorted(load('blog.json'), key=lambda p: p.get('date', ''), reverse=True)
    prods, cats, brands = catalog['products'], catalog['categories'], catalog['brands']
    n_cat = {c['slug']: sum(1 for p in prods if p['category'] == c['slug']) for c in cats}
    hijas = {}
    for c in cats:
        if c.get('parent'):
            hijas.setdefault(c['parent'], []).append(c)
    # una categoría padre cuenta también los equipos de sus hijas
    total = lambda c: n_cat[c['slug']] + sum(n_cat[h['slug']] for h in hijas.get(c['slug'], []))
    nombre = lambda c: c.get('seo_name') or c['name']

    # --- Catálogo: árbol de categorías ---
    arbol = []
    for c in cats:
        if c.get('parent') or total(c) == 0:
            continue
        sub = ''.join(
            f'<li><a href="{ROOT}categoria/{esc(h["slug"])}/">{txt(nombre(h))}</a> '
            f'<b>{n_cat[h["slug"]]}</b></li>'
            for h in hijas.get(c['slug'], []) if n_cat[h['slug']])
        arbol.append(
            f'<li><a href="{ROOT}categoria/{esc(c["slug"])}/">{txt(nombre(c))}</a> <b>{total(c)}</b>'
            + (f'<ul>{sub}</ul>' if sub else '') + '</li>')
    catalogo = (f'<p><a href="{ROOT}catalogo/">Ver el catálogo completo</a> con filtros por categoría y marca.</p>'
                f'<ul class="mapa-arbol">{"".join(arbol)}</ul>')

    # --- Marcas ---
    marcas = lista([(f'marca/{b["slug"]}/', b['name'],
                     n_eq(sum(1 for p in prods if p.get("brand") == b["slug"]))
                     + (f' · {b["note"]}' if b.get('note') else '')) for b in brands])

    # --- Todos los equipos, por categoría ---
    por_cat = OrderedDict()
    for p in prods:
        por_cat.setdefault(p['category'], []).append(p)
    cat_by = {c['slug']: c for c in cats}
    equipos = ''.join(
        plegable(f'{txt(nombre(cat_by[s]))} <b>{len(lst)}</b>',
                 ''.join(f'<li><a href="{ROOT}producto/{esc(p["slug"])}/">{txt(p["name"])}</a></li>'
                         for p in lst))
        for s, lst in por_cat.items() if s in cat_by)

    # --- Guías, origen, zonas ---
    guias = lista([('guias/', 'Todas las guías de compra', 'Índice de guías por tipo de equipo y de negocio.')]
                  + [(f'guias/{g["slug"]}/', g['h1'], g['description']) for g in GUIAS])
    origen = lista([('origen/', 'Origen y marcado CE', 'Qué significa cada sello y qué equipos lo llevan.')]
                   + [(f'origen/{o["slug"]}/', o['h1'], o['description']) for o in ORIGENES])
    zonas = lista([('zonas/', 'Zonas de envío e instalación', 'Cobertura en todo el país y cómo se cotiza.')]
                  + [(f'zonas/{z["slug"]}/', z['h1'], z['description']) for z in ZONAS])

    # --- Blog: por año, con lo último a la vista y el resto plegado ---
    def item(p):
        d = p.get('date', '')[:10]
        fecha = f'{MESES[int(d[5:7]) - 1]} {d[:4]}' if len(d) >= 7 else ''
        return (f'<li><a href="{ROOT}blog/{esc(p["slug"])}/">{txt(p["title"])}</a>'
                + (f' <time datetime="{esc(d)}">{fecha}</time>' if fecha else '') + '</li>')
    recientes = ''.join(item(p) for p in posts[:POSTS_A_LA_VISTA])
    resto = posts[POSTS_A_LA_VISTA:]
    blog = (f'<p><a href="{ROOT}blog/">Ir al blog</a></p><ul class="mapa-cols mapa-cols--1">{recientes}</ul>'
            + (plegable(f'Ver las {len(resto)} notas restantes', ''.join(item(p) for p in resto))
               if resto else ''))

    secciones = [
        ('catalogo', 'Catálogo de equipos',
         'Elevadores, alineadoras, balanceadoras, desarmadoras, herramientas y equipamiento de taller.', catalogo),
        ('equipos', 'Todos los equipos',
         'Cada equipo con su ficha: especificaciones, fotos, ficha técnica en PDF y consulta por WhatsApp.', equipos),
        ('marcas', 'Marcas',
         'Hofmann, Rotary Lift, Forward Lift, Direct Lift, Challenger Lifts, Haweka, Prevost y Trivium Pro.', marcas),
        ('guias', 'Guías de compra',
         'Cómo elegir equipos según el tipo de taller y de negocio, con modelos y comparativas.', guias),
        ('origen', 'Origen y marcado CE',
         'De dónde viene cada equipo y qué significa cada sello.', origen),
        ('zonas', 'Zonas',
         'Enviamos e instalamos en todo el país; la instalación se cotiza aparte.', zonas),
        ('empresa', 'Empresa y servicios', 'Quiénes somos, servicios y cómo contactarnos.', lista(EMPRESA)),
        ('politicas', 'Compra y políticas', 'Envíos, cambios, devoluciones y datos personales.', lista(POLITICAS)),
        ('blog', 'Blog',
         f'{len(posts)} notas técnicas y comparativas, de la más nueva a la más vieja.', blog),
    ]
    indice = ''.join(f'<a href="#{i}">{esc(t)}</a>' for i, t, _, _ in secciones)
    stats = ''.join(f'<div><strong>{n}</strong><span>{esc(e)}</span></div>' for n, e in [
        (len(prods), 'equipos'), (sum(1 for c in cats if total(c) and not c.get('parent')), 'categorías'),
        (len(brands), 'marcas'), (len(GUIAS), 'guías de compra'), (len(posts), 'notas del blog')])
    cuerpo = (f'<div class="mapa"><p class="mapa-intro">Todo el contenido de Trivium Pro en un solo lugar: '
              'el catálogo, las guías, el origen de los equipos, las zonas de envío y las notas del blog. '
              'Para ver precios y pedir cotización, entrá a la ficha del equipo o escribinos por WhatsApp.</p>'
              f'<div class="mapa-stats">{stats}</div><nav class="mapa-indice" aria-label="Secciones">{indice}</nav>'
              + ''.join(seccion(*s) for s in secciones) + '</div>')

    url = f"{SITE_URL}/mapa-del-sitio/"
    desc = (f"Mapa del sitio de Trivium Pro: {len(prods)} equipos de taller, {len(GUIAS)} guías de compra, "
            f"origen y marcado CE, zonas de envío y {len(posts)} notas del blog, en una sola página.")
    jsonld = [
        breadcrumb_jsonld([("Inicio", SITE_URL + '/'), ("Mapa del sitio", url)]),
        {"@context": "https://schema.org", "@type": "CollectionPage", "name": "Mapa del sitio",
         "url": url, "description": desc, "inLanguage": "es-AR",
         "isPartOf": {"@type": "WebSite", "name": "Trivium Pro", "url": SITE_URL + '/'}},
    ]
    create_index_file(
        os.path.join(BASE_DIR, 'mapa-del-sitio'), os.path.join(BASE_DIR, 'guia.html'), 1,
        title="Mapa del sitio: equipos, guías, zonas y blog",
        og={'type': 'website', 'title': 'Mapa del sitio de Trivium Pro', 'description': desc,
            'image': OG_IMAGE, 'url': url},
        seo=make_seo_block(url, desc, jsonld),
        body={'crumbs': breadcrumb_html([("Inicio", ""), ("Mapa del sitio", None)], ROOT),
              'guia-title': 'Todo Trivium Pro, en un solo lugar', 'guia-tag': 'Mapa del sitio',
              'guia-updated': '', 'guia-body': cuerpo, 'guia-faq': '', 'guia-posts': ''},
    )
    print(f"  -> mapa-del-sitio/ ({len(prods)} equipos, {len(posts)} notas)")


if __name__ == '__main__':
    main()
