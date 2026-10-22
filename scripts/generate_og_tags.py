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
    if not items:
        return ''
    return (f'<div class="container"><h2>Guías relacionadas</h2>'
            f'<ul class="guia-lista">{"".join(items)}</ul></div>')


def update_blog():
    with open(BASE_DIR / 'data' / 'blog.json', encoding='utf-8') as f:
        posts = json.load(f)

    root = '../../'
    by_date = sorted(posts, key=lambda p: p.get('date', ''), reverse=True)

    count = 0
    for post in posts:
        slug = post['slug']
        page_path = BASE_DIR / 'blog' / slug / 'index.html'
        if not page_path.exists():
            continue

        title = html.unescape(post['title'])
        url = f"{SITE_URL}/blog/{slug}/"
        description = (post.get('meta_description')
                       or clamp(strip_html(post.get('excerpt', ''))) or title)
        image_path = post.get('image', '')
        image_url = f"{SITE_URL}/{image_path}" if image_path else ''
        published = post.get('date', '')

        article_ld = {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": title[:110],
            "description": post.get('meta_description') or strip_html(post.get('excerpt', '')),
            "url": url,
            "mainEntityOfPage": {"@type": "WebPage", "@id": url},
            "author": {"@type": "Organization", "name": ORG_NAME},
            "publisher": {
                "@type": "Organization",
                "name": ORG_NAME,
                "logo": {"@type": "ImageObject",
                         "url": f"{SITE_URL}/assets/img/logo-trivium.svg"},
            },
        }
        if published:
            article_ld["datePublished"] = published
            article_ld["dateModified"] = published
        if image_url:
            article_ld["image"] = [image_url]

        # Preguntas frecuentes: salen de los <details> del propio contenido, así el
        # schema nunca queda desfasado del texto visible.
        faq_items = re.findall(
            r'<details><summary>(.*?)</summary><p>(.*?)</p></details>',
            post.get('content') or '', re.S)
        faq_ld = None
        if faq_items:
            faq_ld = {
                "@context": "https://schema.org",
                "@type": "FAQPage",
                "mainEntity": [
                    {"@type": "Question", "name": strip_html(q),
                     "acceptedAnswer": {"@type": "Answer", "text": strip_html(a)}}
                    for q, a in faq_items
                ],
            }

        crumbs_ld = {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Inicio",
                 "item": f"{SITE_URL}/"},
                {"@type": "ListItem", "position": 2, "name": "Blog",
                 "item": f"{SITE_URL}/blog/"},
                {"@type": "ListItem", "position": 3, "name": title, "item": url},
            ],
        }

        # --- contenido prerenderizado ---
        pretty_date = published[:10]
        hero = ''
        if image_path:
            hero = (f'<p><img src="{esc(root + image_path)}" alt="{esc(title)}" '
                    f'width="1200" height="630"></p>')
        body_html = hero + (post.get('content') or post.get('excerpt') or '')
        cat = POST_CATEGORY.get(slug)
        if cat:
            cat_slug, cat_name = cat
            body_html += (
                f'<p class="post-cat-cta"><a href="{esc(root)}categoria/{esc(cat_slug)}/">'
                f'Ver equipos de {esc(cat_name.lower())} en Trivium Pro →</a></p>'
            )

        more = [p for p in by_date if p['slug'] != slug][:6]
        more_html = ''.join(
            f'<a class="prod-card" href="{esc(root)}blog/{esc(p["slug"])}/">'
            f'<div class="body"><h3>{esc(html.unescape(p["title"]))}</h3></div></a>'
            for p in more
        )
        crumbs_html = (
            f'<a href="{esc(root)}">Inicio</a> <span class="sep">/</span> '
            f'<a href="{esc(root)}blog/">Blog</a> <span class="sep">/</span> '
            f'<span>{esc(title)}</span>'
        )

        content = page_path.read_text(encoding='utf-8')
        content = inject_head(
            content, title,
            make_og_block(title, description, image_url, url, 'article'),
            make_seo_block(url, description, [article_ld, crumbs_ld] + ([faq_ld] if faq_ld else [])),
        )
        # Header y footer: sin esto el crawler ve el artículo sin navegación.
        chrome_h, chrome_f = load_chrome(root)
        if chrome_h:
            content = replace_empty_el(content, 'site-header', chrome_h)
            content = replace_empty_el(content, 'site-footer', chrome_f)
        content = replace_empty_el(content, 'crumbs', crumbs_html)
        content = replace_empty_el(content, 'post-title', esc(title))
        content = replace_empty_el(content, 'post-date', esc(pretty_date))
        content = replace_empty_el(content, 'post-content', body_html)
        content = replace_empty_el(content, 'more-posts', more_html)
        # Contenedor estático de guías (idempotente: se crea una sola vez).
        if 'id="post-guide"' not in content:
            content = content.replace(
                '</article>', '</article>\n<section class="cat-blog-links" id="post-guide"></section>', 1)
        if 'assets/css/guia.css' not in content:
            content = content.replace(
                '<link rel="stylesheet" href="../../assets/css/styles.css">',
                '<link rel="stylesheet" href="../../assets/css/styles.css">\n'
                '<link rel="stylesheet" href="../../assets/css/guia.css">', 1)
        content = replace_empty_el(content, 'post-guide', post_guide_html(slug, root))
        # El script inline usa ${root} sin declararlo: lanzaba ReferenceError
        # al armar las migas y abortaba antes de renderizar "Más noticias".
        content = content.replace('${root}', '${rootPath()}')
        page_path.write_text(content, encoding='utf-8')
        count += 1

    print(f"✔ {count} artículos del blog con OG, canonical, description y JSON-LD")


if __name__ == "__main__":
    update_blog()
