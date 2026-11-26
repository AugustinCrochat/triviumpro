#!/usr/bin/env python3
"""SEO de los artículos del blog: OG/Twitter, canonical, meta description,
JSON-LD (Article + BreadcrumbList) y contenido prerenderizado en el HTML.

Las páginas de producto, categoría y marca las resuelve
scripts/generate_pretty_urls.py, que ya inyecta lo mismo.
"""

import json
import re
import html
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
from site_config import SITE_URL, ORG_NAME, load_chrome


def strip_html(text):
    text = re.sub(r'<[^>]+>', ' ', text or '')
    text = html.unescape(text)
    return re.sub(r'\s+', ' ', text).strip()


def clamp(text, limit=158):
    """Recorta en el límite de palabra, sin cortar al medio."""
    text = re.sub(r'\s+', ' ', (text or '')).strip()
    if len(text) <= limit:
        return text
    return text[:limit].rsplit(' ', 1)[0].rstrip(' .,;:·-') + '…'


def esc(s):
    """Escapa para atributo HTML. Des-escapa primero: los títulos de WordPress
    ya traen entidades (&#8220;) y volver a escaparlas las rompe."""
    return html.escape(html.unescape(str(s or '')), quote=True)


def make_og_block(title, description, image_url, url, og_type="article"):
    t, d = esc(title), esc(description)
    img, u = esc(image_url), esc(url)
    return (
        f'<meta property="og:type" content="{og_type}">\n'
        f'<meta property="og:site_name" content="{ORG_NAME}">\n'
        f'<meta property="og:title" content="{t}">\n'
        f'<meta property="og:description" content="{d}">\n'
        f'<meta property="og:image" content="{img}">\n'
        f'<meta property="og:url" content="{u}">\n'
        f'<meta name="twitter:card" content="summary_large_image">\n'
        f'<meta name="twitter:title" content="{t}">\n'
        f'<meta name="twitter:description" content="{d}">\n'
        f'<meta name="twitter:image" content="{img}">'
    )


def make_seo_block(canonical, description, jsonld):
    out = [
        f'<link rel="canonical" href="{esc(canonical)}">',
        f'<meta name="description" content="{esc(description)}">',
        '<meta name="robots" content="index, follow, max-image-preview:large">',
    ]
    for block in jsonld:
        payload = json.dumps(block, ensure_ascii=False, separators=(',', ':'))
        payload = payload.replace('</', '<\\/')
        out.append(f'<script type="application/ld+json">{payload}</script>')
    return '\n'.join(out)


def replace_empty_el(content, el_id, inner):
    """Reemplaza el interior del contenedor con id=el_id.

    Busca la etiqueta de cierre que corresponde contando anidamiento: el
    contenido inyectado trae <div> adentro, y un regex no-greedy cortaría en
    el primer </div>, duplicando contenido en cada corrida.
    """
    open_re = re.compile(
        r'<(?P<tag>\w+)[^>]*\bid="' + re.escape(el_id) + r'"[^>]*?(?P<self>/?)>'
    )
    m = open_re.search(content)
    if not m or m.group('self') == '/':
        return content

    tag = m.group('tag')
    start = m.end()
    depth = 1
    scan = re.compile(rf'<(/?){tag}\b[^>]*?(/?)>', re.I)
    pos = start
    while depth:
        nxt = scan.search(content, pos)
        if not nxt:
            return content  # markup desbalanceado: no tocar
        if nxt.group(1) == '/':
            depth -= 1
        elif nxt.group(2) != '/':
            depth += 1
        pos = nxt.end()
        if depth == 0:
            return content[:start] + inner + content[nxt.start():]
    return content


def titulo_seo(t):
    """Título de pestaña/Google (~60 caracteres): se corta en el primer ':' o ' – ' si el título es largo."""
    if len(t) <= 62:
        return t
    for sep in (': ', ' – ', ' - ', '? '):
        if sep in t:
            a = t.split(sep)[0].strip()
            if 28 <= len(a) <= 62:
                return a + ('?' if sep == '? ' else '')
    palabras, out = t.split(), ''
    for w in palabras:
        if len(out) + len(w) + 1 > 60: break
        out = (out + ' ' + w).strip()
    while out.split()[-1].lower() in ('de', 'la', 'el', 'en', 'y', 'para', 'con', 'un', 'una', 'los', 'las', 'del', 'a', 'que'):
        out = ' '.join(out.split()[:-1])
    return out


def inject_head(content, title, og_block, seo_block):
    title = titulo_seo(title)
    # Limpia inyecciones previas para que el script sea idempotente
    content = re.sub(r'\n?<meta property="og:[^>]*>', '', content)
    content = re.sub(r'\n?<meta name="twitter:[^>]*>', '', content)
    content = re.sub(r'\n?<link rel="canonical"[^>]*>', '', content)
    content = re.sub(r'\n?<meta name="description"[^>]*>', '', content)
    content = re.sub(r'\n?<meta name="robots"[^>]*>', '', content)
    content = re.sub(
        r'\n?<script type="application/ld\+json">.*?</script>', '', content, flags=re.S
    )

    completo = f"{title} — {ORG_NAME}"
    if len(completo) > 62 and len(title) >= 40:
        completo = title      # ~60 caracteres es lo que muestra Google: mejor el título completo que uno cortado
    content = re.sub(
        r'<title>[^<]*</title>',
        lambda m: f'<title>{esc(completo)}</title>',
        content,
        count=1,
    )
    return content.replace('</head>', og_block + '\n' + seo_block + '\n</head>', 1)


# Inverso de scripts/generate_pretty_urls.py:CATEGORY_BLOG_POSTS — qué
# categoría linkear al pie de cada nota, para que el lector (o un crawler)
# pueda ir de la guía a los equipos reales sin buscar. Mantenido a mano acá
# porque este script no importa el otro (son independientes en el pipeline).
POST_CATEGORY = {}
for _cat_slug, _cat_name, _posts in [
    ('elevadores', 'Elevadores', [
        'cuanto-cuesta-un-elevador-para-taller-que-influye-en-el-precio',
        'rotary-lift-o-trivium-pro-que-linea-conviene-segun-tu-taller',
        'que-equipos-necesita-un-taller-mecanico-lista-completa-por-prioridad',
        'como-equipar-un-taller-para-autos-electricos-e-hibridos-elevador-y-herramientas',
        'como-montar-un-taller-de-motos-elevador-y-equipamiento-necesario',
        'elevador-tijera-tipos-capacidades-y-cual-elegir-para-tu-taller',
        'como-elegir-un-elevador-de-2-columnas-capacidad-brazos-y-altura',
        'elevador-de-4-columnas-para-que-sirve-capacidades-y-cuando-conviene',
        'elevador-tijera-movil-para-detailing-por-que-conviene-y-como-elegirlo',
        'elevador-tijera-de-sobrepiso-plancha-elevadora-para-gomeria-ventajas-y-modelos',
        'es-rentable-un-lubricentro-como-calcular-la-ganancia-y-el-punto-de-equilibrio',
        'es-rentable-un-taller-mecanico-como-calcular-ganancias-y-que-equipos-necesitas',
        'como-abrir-un-taller-de-frenos-equipamiento-servicios-y-rentabilidad',
        'como-montar-un-taller-de-detailing-equipamiento-y-servicios-que-mas-rinden',
        'mantenimiento-de-un-elevador-de-taller-checklist-diario-mensual-y-anual',
        'como-elegir-el-elevador-adecuado-para-hacer-alineacion',
        'diferencias-entre-elevadores-de-2-columnas-de-piso-libre-y-travesano-al-piso',
        'elevador-de-4-columnas-vs-elevador-de-tijera-largo-cual-elegir-para-alineacion',
        'que-tipo-de-elevador-elegir-para-cambio-de-aceite',
        'por-que-elegir-un-elevador-con-brazos-all-vehicle-de-rotary-lift',
        'especificaciones-del-piso-para-la-instalacion-de-un-elevador-de-dos-columnas',
    ]),
    ('alineadoras', 'Alineadoras', [
        'alineacion-de-camiones-con-eje-desplazado-referencia-linea-central-josam',
        'es-rentable-un-taller-de-alineacion-y-balanceo-inversion-y-retorno',
        'hofmann-geoliner-880-alineadora-3d-de-paso-directo-con-ia',
        'como-elegir-la-alineadora-de-autos-ideal-para-tu-taller',
        'como-funciona-una-alineadora-y-su-importancia-en-talleres-y-gomerias',
        'como-se-alinea-un-vehiculo-con-una-alineadora-3d',
        'alineadoras-5d-el-mito-de-las-dimensiones-en-equipos-de-alineacion',
        'los-beneficios-de-tener-una-alineadora-en-tu-taller-o-gomeria',
        'como-funciona-la-alineacion-3d-de-autos-tecnologia-y-beneficios',
    ]),
    ('balanceadoras', 'Balanceadoras', [
        'como-elegir-una-balanceadora-de-ruedas-capacidad-tecnologia-y-modelos',
        'como-montar-una-gomeria-para-camiones-y-vehiculos-pesados-equipos-necesarios',
        'es-rentable-una-gomeria-como-calcular-ganancias-y-punto-de-equilibrio',
        'servicios-para-sumar-ticket-en-una-gomeria-y-que-equipos-necesitas',
        'como-centrar-una-rueda-en-la-balanceadora-conos-tuercas-rapidas-y-adaptadores',
        'balanceadoras-de-ruedas-con-o-sin-monitor-cual-elegir',
        'autocalibracion-en-una-balanceadora-de-ruedas-que-es-y-por-que-es-importante',
        'errores-comunes-al-usar-una-balanceadora-y-como-evitarlos',
        'por-que-incorporar-una-balanceadora-de-ruedas-en-tu-gomeria-es-una-decision-inteligente',
        'la-importancia-de-balancear-ruedas-beneficios-clave-para-talleres-y-gomerias',
    ]),
    ('desarmadoras', 'Desarmadoras', [
        'como-montar-una-gomeria-para-camiones-y-vehiculos-pesados-equipos-necesarios',
        'como-elegir-una-desarmadora-de-neumaticos-tipos-tamanos-y-modelos',
        'es-rentable-una-gomeria-como-calcular-ganancias-y-punto-de-equilibrio',
        'para-que-sirve-el-brazo-auxiliar-en-una-desarmadora-de-neumaticos',
        'como-funcionan-las-desarmadoras-para-neumaticos-runflat-guia-para-talleres-y-gomerias',
        'como-mantener-tu-desarmadora-trivium-center-en-optimas-condiciones',
        'equipamiento-esencial-para-comenzar-tu-taller-de-neumaticos',
    ]),
]:
    for _slug in _posts:
        POST_CATEGORY[_slug] = (_cat_slug, _cat_name)


# --- enlaces de cada nota a las guías de compra y a las páginas de zona ---
# Reglas por palabra clave del slug, en orden: la primera que coincide gana.
# Las notas de casos (instalaciones, capacitaciones) llevan además su zona.
POST_GUIDE_RULES = [
    (('elevador', 'piso', 'lubricentro', 'monofasicos', 'certificacion-ali'), 'elevadores-para-taller'),
    (('alineador', 'alineacion', 'geoliner', 'geometria', 'hofmann', 'josam', 'ventajas-de-la-alineacion'), 'alineadoras-3d'),
    (('balance', 'autocalibracion'), 'balanceadoras-de-ruedas'),
    (('desarmadora',), 'desarmadoras-de-neumaticos'),
    (('gomeria', 'taller', 'neumaticos', 'rotacion', 'repuestera'), 'equipar-una-gomeria'),
]
POST_GUIDE_OVERRIDE = {
    'equipamiento-esencial-para-comenzar-tu-taller-de-neumaticos': 'equipar-una-gomeria',
    'instalamos-tres-elevadores-de-dos-columnas-para-punto-flash': 'elevadores-para-taller',
    'como-mantener-tu-desarmadora-trivium-center-en-optimas-condiciones': 'desarmadoras-de-neumaticos',
    # "alineacion" en el slug no la hace una nota de alineadoras:
    'como-abrir-un-taller-de-alineacion-y-balanceo': 'equipar-una-gomeria',
    'cuanto-espacio-dejar-entre-la-alineadora-y-el-elevador-recomendaciones-para-una-instalacion-optima': 'alineadoras-3d',
    # Caso de mantenimiento preventivo: la guía no aporta, la zona sí.
    'la-importancia-del-mantenimiento-preventivo-en-equipos-de-taller-caso-exitoso-lions-group': '',
}
POST_ZONE = {
    'formacion-tecnica-en-alineadora-3d-geoliner-630-en-neumaticos-pons-cordoba': 'cordoba',
    'instalamos-una-josam-cv-aligner-en-mendoza-tecnologia-snap-on-para-el-alineado-de-vehiculos-pesados': 'mendoza',
    'equipamiento-completo-para-repuestera-del-milagro': 'salta',
    'la-importancia-del-mantenimiento-preventivo-en-equipos-de-taller-caso-exitoso-lions-group': 'buenos-aires',
}


def post_guide_html(slug, root):
    """Bloque estático 'Guías relacionadas' al pie de la nota.

    Va en #post-guide, fuera de #post-content: el script de la página
    reescribe #post-content con post.content al hidratar, así que cualquier
    enlace prerenderizado adentro se pierde en el navegador.
    """
    from guias_content import GUIAS
    from zonas_content import ZONAS
    guia_slug = POST_GUIDE_OVERRIDE.get(slug)
    if guia_slug is None:
        for words, g in POST_GUIDE_RULES:
            if any(w in slug for w in words):
                guia_slug = g
                break
    items = []
    guide = next((g for g in GUIAS if g['slug'] == guia_slug), None)
    if guide:
        items.append(f'<li><a href="{esc(root)}guias/{esc(guide["slug"])}/"><strong>{esc(guide["h1"])}</strong>'
                     f'<span>{esc(guide["description"])}</span></a></li>')
    zone = next((z for z in ZONAS if z['slug'] == POST_ZONE.get(slug)), None)
    if zone:
        items.append(f'<li><a href="{esc(root)}zonas/{esc(zone["slug"])}/"><strong>{esc(zone["h1"])}</strong>'
                     f'<span>{esc(zone["description"])}</span></a></li>')
    out = ''
    if items:
        out += (f'<div class="container"><h2>Guías relacionadas</h2>'
                f'<ul class="guia-lista">{"".join(items)}</ul></div>')
    out += related_html(slug, root)
    return out


_RELATED = None


def related_html(slug, root):
    """Equipos y notas afines a esta nota (scripts/related.py), como grillas de tarjetas."""
    global _RELATED
    if _RELATED is None:
        import related
        from generate_pretty_urls import product_card_html
        with open(BASE_DIR / 'data' / 'catalog.json', encoding='utf-8') as f:
            cat = json.load(f)
        with open(BASE_DIR / 'data' / 'blog.json', encoding='utf-8') as f:
            blog = json.load(f)
        _RELATED = (related.build(), {p['slug']: p for p in cat['products']},
                    {b['slug']: b for b in cat['brands']}, {p['slug']: p for p in blog},
                    product_card_html)
    rel, prods, brands, blog, card = _RELATED
    out = ''
    equipos = [prods[s] for s in rel['post_products'].get(slug, []) if s in prods]
    if equipos:
        out += ('<div class="container"><h2>Equipos relacionados</h2><div class="prod-grid">'
                + ''.join(card(p, brands, root) for p in equipos) + '</div></div>')
    notas = [blog[s] for s in rel['post_posts'].get(slug, []) if s in blog]
    if notas:
        from blog_layout import tarjeta
        out += f'<div class="container"><h2>Notas relacionadas</h2><div class="nota-grid">{"".join(tarjeta(n, root) for n in notas)}</div></div>'
    return out


def update_blog():
    """La plantilla del blog vive en scripts/blog_layout.py."""
    import blog_layout
    blog_layout.build_all()


if __name__ == "__main__":
    update_blog()
