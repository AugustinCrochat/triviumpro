"""Plantilla única del blog. Todo sale de data/blog.json: no hay que copiar páginas a mano.

Genera:
  blog/<slug>/index.html  nota completa (se reescribe entera)
  blog/index.html         listado prerenderizado (el <head> lo mantiene generate_pretty_urls.py)
  data/blog.js            copia de blog.json para el navegador
  feed.xml                RSS de las últimas 30 notas
  llms-blog.txt           texto de todas las notas para asistentes de IA

Se ejecuta con `python3 scripts/generate_og_tags.py` (lo llama el pre-commit).
Campos opcionales de cada nota en blog.json: meta_description, updated (AAAA-MM-DD, sólo si cambió el contenido).
"""
import html
import json
import re
import unicodedata
from email.utils import format_datetime
from datetime import datetime, timedelta, timezone
from urllib.parse import quote

from site_config import SITE_URL, ORG_NAME, load_chrome
import blog_productos
from generate_og_tags import (
    BASE_DIR, POST_CATEGORY, POST_ZONE, clamp, esc, make_og_block, make_seo_block,
    post_guide_html, replace_empty_el, strip_html, titulo_seo,
)

CSS_V = '20261126c'
JS_V = '20261126a'
WHATSAPP = '5491127015294'
MESES = ('enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto',
         'septiembre', 'octubre', 'noviembre', 'diciembre')

try:
    from PIL import Image
except ImportError:  # sin Pillow sólo se pierden las medidas de las imágenes
    Image = None


def fecha_larga(iso):
    try:
        a, m, d = iso[:10].split('-')
        return f'{int(d)} de {MESES[int(m) - 1]} de {a}'
    except (ValueError, IndexError):
        return ''


def slugify(t):
    t = unicodedata.normalize('NFKD', strip_html(t)).encode('ascii', 'ignore').decode().lower()
    return re.sub(r'[^a-z0-9]+', '-', t).strip('-')[:60] or 'seccion'


# --- sección editorial de cada nota (sale del slug) ---
CASOS = ('instalamos', 'formacion-tecnica', 'capacitacion-y-puesta', 'equipamiento-completo-para', 'caso-exitoso')
NOVEDADES = ('trivium-center-ahora-es',)
SECCIONES = ('Alineación', 'Balanceo', 'Desarmadoras y neumáticos', 'Elevadores', 'Gestión del taller', 'Casos e instalaciones', 'Marcas y novedades')


def seccion(slug):
    if any(w in slug for w in CASOS):
        return 'Casos e instalaciones'
    if any(w in slug for w in NOVEDADES):
        return 'Marcas y novedades'
    if any(w in slug for w in ('rentable', 'cuanto-cuesta-equipar', 'en-cuanto-tiempo-se-paga', 'como-abrir', 'como-empezar', 'como-montar', 'como-instalar')):
        return 'Gestión del taller'
    if slug in POST_CATEGORY:
        return {'elevadores': 'Elevadores', 'alineadoras': 'Alineación', 'balanceadoras': 'Balanceo',
                'desarmadoras': 'Desarmadoras y neumáticos'}[POST_CATEGORY[slug][0]]
    for palabras, nombre in (
        (('elevador', 'certificacion-ali'), 'Elevadores'),
        (('balance', 'centrar-una-rueda'), 'Balanceo'),
        (('alinea', 'geoliner', 'geometria', 'josam', 'adas', 'desalineado'), 'Alineación'),
        (('desarmadora', 'neumatico', 'gomeria', 'valvula', 'pinchadura', 'tpms', 'nitrogeno', 'rotacion'), 'Desarmadoras y neumáticos'),
        (('hofmann', 'rotary', 'challenger', 'trivium-pro', 'direct-lift', 'john-bean'), 'Marcas y novedades'),
    ):
        if any(w in slug for w in palabras):
            return nombre
    return 'Gestión del taller'


CATEGORIA_DE_SECCION = {'Alineación': ('alineadoras', 'alineadoras'), 'Balanceo': ('balanceadoras', 'balanceadoras'),
                        'Desarmadoras y neumáticos': ('desarmadoras', 'desarmadoras'), 'Elevadores': ('elevadores', 'elevadores')}


# --- imágenes ---
_MEDIDAS = {}


def medidas(rel):
    if rel not in _MEDIDAS:
        ruta = BASE_DIR / rel
        try:
            with Image.open(ruta) as im:
                _MEDIDAS[rel] = im.size
        except Exception:
            _MEDIDAS[rel] = None
    return _MEDIDAS[rel]


def miniatura(rel):
    t = re.sub(r'^(assets/img/(?:productos|blog)/)([^/]+)$', r'\1t/\2', rel or '')
    return t if t and (BASE_DIR / t).exists() else rel


def tarjeta(p, root, h='h3', prioridad=False):
    sec = seccion(p['slug'])
    titulo = html.unescape(p['title'])
    resumen = clamp(strip_html(p.get('excerpt', '')) or p.get('meta_description', ''), 130)
    img = miniatura(p.get('image', ''))
    pic = (f'<img src="{esc(root + img)}" alt="" width="640" height="360" '
           f'{"fetchpriority=\"high\"" if prioridad else "loading=\"lazy\""} decoding="async">') if img else ''
    return (f'<a class="nota-card" href="{esc(root)}blog/{esc(p["slug"])}/" data-sec="{esc(sec)}">'
            f'<span class="nota-card__img">{pic}</span><span class="nota-card__txt">'
            f'<span class="nota-card__meta"><b>{esc(sec)}</b> · <time datetime="{p.get("date", "")[:10]}">{fecha_larga(p.get("date", ""))}</time></span>'
            f'<{h}>{esc(titulo)}</{h}><span class="nota-card__res">{esc(resumen)}</span></span></a>')


# --- cuerpo de la nota ---
def preparar_cuerpo(c):
    """Limpieza y mejoras de lectura sin cambiar el texto. Devuelve (html, índice)."""
    c = re.sub(r'<hr class="wp-block-separator[^>]*>', '', c)
    c = re.sub(r'<p>(?:\s|&nbsp;)*</p>', '', c)
    # el rótulo «En resumen» queda en su renglón, así que la frase que sigue arranca con mayúscula
    c = re.sub(r'<p>\s*<strong>\s*En resumen:?\s*</strong>\s*([a-záéíóúñ])?',
               lambda m: '<p class="nota-resumen"><strong>En resumen</strong> ' + (m.group(1) or '').upper(), c, count=1)

    usados, indice = set(), []

    def h2(m):
        attrs, inner = m.group(1), m.group(2)
        ya = re.search(r'\bid="([^"]+)"', attrs)
        base = ya.group(1) if ya else slugify(inner)
        ident, n = base, 2
        while ident in usados:
            ident, n = f'{base}-{n}', n + 1
        usados.add(ident)
        texto = strip_html(inner)
        if texto:
            indice.append((ident, texto))
        return m.group(0) if ya else f'<h2 id="{ident}"{attrs}>{inner}</h2>'
    c = re.sub(r'<h2([^>]*)>(.*?)</h2>', h2, c, flags=re.S)

    # tablas sin contenedor: que se desplacen solas en el celular
    partes = re.split(r'(<div class="tabla-wrap">.*?</div>)', c, flags=re.S)
    c = ''.join(x if x.startswith('<div class="tabla-wrap">') else
                re.sub(r'(<table\b.*?</table>)', r'<div class="tabla-wrap">\1</div>', x, flags=re.S) for x in partes)

    def img(m):
        tag = m.group(0)
        if 'loading=' not in tag:
            tag = tag.replace('<img', '<img loading="lazy"', 1)
        if ' width=' not in tag:
            src = re.search(r'src="(?:\.\./\.\./|/)?(assets/[^"?]+)"', tag)
            wh = src and medidas(src.group(1))
            if wh:
                tag = tag.replace('<img', f'<img width="{wh[0]}" height="{wh[1]}"', 1)
        return tag
    return re.sub(r'<img\b[^>]*>', img, c), indice


def preguntas(contenido):
    pares = re.findall(r'<details[^>]*>\s*<summary>(.*?)</summary>\s*<p>(.*?)</p>\s*</details>', contenido, re.S)
    return [(strip_html(q), strip_html(a)) for q, a in pares]


def palabras(contenido):
    return len(strip_html(re.sub(r'<(script|style)\b.*?</\1>', ' ', contenido, flags=re.S)).split())


def cabeza(root, titulo_tab, extra):
    fuente = 'https://fonts.googleapis.com/css2?family=Archivo:wght@400;500;600;700;800&display=swap'
    return f'''<!doctype html>
<html lang="es-AR">
<head>
<meta charset="utf-8">
<link rel="icon" href="/favicon.ico" sizes="48x48">
<link rel="icon" type="image/png" href="/favicon-96x96.png" sizes="96x96">
<link rel="icon" type="image/png" href="/favicon-192x192.png" sizes="192x192">
<link rel="icon" type="image/svg+xml" href="/assets/img/icono-trivium.svg">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="tv-root" content="{root}">
<title>{esc(titulo_tab)}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="{fuente}" rel="stylesheet" media="print" onload="this.media='all'"><noscript><link href="{fuente}" rel="stylesheet"></noscript>
<link rel="stylesheet" href="{root}assets/css/styles.css?v={JS_V}">
<link rel="stylesheet" href="{root}assets/css/guia.css?v={JS_V}">
<link rel="stylesheet" href="{root}assets/css/blog.css?v={CSS_V}">
<link rel="alternate" type="application/rss+xml" title="Blog de {ORG_NAME}" href="/feed.xml">
{extra}
</head>'''


def bajada(post):
    """El resumen de la nota o su descripción propia. Si no hay ninguno completo (notas importadas de WordPress), nada."""
    for r in (strip_html(post.get('excerpt', '')).strip(), (post.get('meta_description') or '').strip()):
        if r.endswith(('.', '?', '!')) and '[' not in r[-6:] and not r.endswith('...'):
            return r
    return ''


def pagina_nota(post, posts, productos):
    root = '../../'
    slug = post['slug']
    titulo = html.unescape(post['title'])
    url = f'{SITE_URL}/blog/{slug}/'
    contenido = post.get('content') or post.get('excerpt') or ''
    desc = post.get('meta_description') or clamp(strip_html(post.get('excerpt', ''))) or titulo
    imagen = post.get('image', '')
    img_url = f'{SITE_URL}/{imagen}' if imagen else ''
    wh = (imagen and medidas(imagen)) or (1100, 600)
    publicada = post.get('date', '')
    cambiada = post.get('updated') or publicada
    sec = seccion(slug)
    n_palabras = palabras(contenido)
    minutos = max(1, round(n_palabras / 200))
    cuerpo, indice = preparar_cuerpo(contenido)
    equipos = blog_productos.elegidos(slug)
    cuerpo = blog_productos.insertar(cuerpo, equipos, root)

    # fechas con zona horaria de Argentina
    zona = lambda f: (f if 'T' in f else f + 'T09:00:00') + '-03:00'
    nota_ld = {
        '@context': 'https://schema.org', '@type': 'BlogPosting', 'headline': titulo[:110], 'description': desc,
        'url': url, 'mainEntityOfPage': {'@type': 'WebPage', '@id': url}, 'inLanguage': 'es-AR',
        'articleSection': sec, 'wordCount': n_palabras,
        'isPartOf': {'@type': 'Blog', 'name': f'Blog de {ORG_NAME}', 'url': f'{SITE_URL}/blog/'},
        'author': {'@type': 'Organization', 'name': ORG_NAME, 'url': f'{SITE_URL}/nosotros/'},
        'publisher': {'@type': 'Organization', 'name': ORG_NAME, 'url': f'{SITE_URL}/',
                      'logo': {'@type': 'ImageObject', 'url': f'{SITE_URL}/favicon-192x192.png', 'width': 192, 'height': 192}},
    }
    if publicada:
        nota_ld['datePublished'], nota_ld['dateModified'] = zona(publicada), zona(cambiada)
    if img_url:
        nota_ld['image'] = [{'@type': 'ImageObject', 'url': img_url, 'width': wh[0], 'height': wh[1]}]
    citados = [productos[s] for s in dict.fromkeys(re.findall(r'/producto/([a-z0-9.\-]+)/', contenido)) if s in productos]
    if citados:
        nota_ld['mentions'] = [{'@type': 'Thing', 'name': html.unescape(p['name']), 'url': f'{SITE_URL}/producto/{p["slug"]}/'} for p in citados[:10]]
    bloques = [nota_ld, {'@context': 'https://schema.org', '@type': 'BreadcrumbList', 'itemListElement': [
        {'@type': 'ListItem', 'position': 1, 'name': 'Inicio', 'item': f'{SITE_URL}/'},
        {'@type': 'ListItem', 'position': 2, 'name': 'Blog', 'item': f'{SITE_URL}/blog/'},
        {'@type': 'ListItem', 'position': 3, 'name': titulo, 'item': url}]}]
    faq = preguntas(contenido)
    if faq:
        bloques.append({'@context': 'https://schema.org', '@type': 'FAQPage', 'mainEntity': [
            {'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': a}} for q, a in faq]})

    tab = titulo_seo(titulo)
    if len(f'{tab} — {ORG_NAME}') <= 62 or len(tab) < 40:
        tab = f'{tab} — {ORG_NAME}'
    extra = [make_og_block(titulo, desc, img_url, url, 'article'),
             f'<meta property="og:locale" content="es_AR">\n<meta property="og:image:width" content="{wh[0]}">\n<meta property="og:image:height" content="{wh[1]}">',
             f'<meta property="article:published_time" content="{zona(publicada)}">\n<meta property="article:modified_time" content="{zona(cambiada)}">\n<meta property="article:section" content="{esc(sec)}">' if publicada else '',
             make_seo_block(url, desc, bloques)]

    header, footer = load_chrome(root)
    fechas = f'<time datetime="{publicada[:10]}">{fecha_larga(publicada)}</time>'
    if cambiada[:10] != publicada[:10]:
        fechas += f' · actualizada el <time datetime="{cambiada[:10]}">{fecha_larga(cambiada)}</time>'
    portada = (f'<figure class="nota-portada"><img src="{esc(root + imagen)}" alt="{esc(titulo)}" width="{wh[0]}" height="{wh[1]}" fetchpriority="high"></figure>') if imagen else ''

    aside = ''
    if len(indice) >= 3:
        items = ''.join(f'<li><a href="#{i}">{esc(t)}</a></li>' for i, t in indice)
        aside = f'<details class="nota-indice" open><summary>En esta nota</summary><nav aria-label="Índice de la nota"><ol>{items}</ol></nav></details>'
    if aside or equipos:
        aside = f'<aside class="nota-lado"><div class="nota-fijo">{aside}{blog_productos.lateral(equipos[0], root) if equipos else ""}</div></aside>'

    cat = POST_CATEGORY.get(slug)
    cat = (cat[0], cat[1].lower()) if cat else CATEGORIA_DE_SECCION.get(sec)
    ver = f'<a class="nota-cta__link" href="{root}categoria/{cat[0]}/">Ver equipos de {cat[1]} →</a>' if cat else f'<a class="nota-cta__link" href="{root}catalogo/">Ver el catálogo →</a>'
    wa = f'https://wa.me/{WHATSAPP}?text={quote("Hola, leí la nota «" + titulo + "» y quiero hacer una consulta.")}'
    cta = (f'<aside class="nota-cta"><div><strong>¿Estás evaluando equipar tu taller?</strong><p>Contanos qué trabajos hacés y te asesoramos.</p>{ver}</div>'
           f'<div class="nota-cta__botones"><a class="btn btn--primary" href="{wa}" rel="noopener">Consultar por WhatsApp</a>'
           f'<a class="btn btn--ghost" href="{root}contacto/">Pedir cotización</a></div></aside>')

    relacionados = post_guide_html(slug, root)
    ya = set(re.findall(r'blog/([a-z0-9\-]+)/', relacionados + contenido))
    otras = sorted((p for p in posts if p['slug'] != slug and p['slug'] not in ya),
                   key=lambda p: (seccion(p['slug']) == sec, p.get('date', '')), reverse=True)[:3]
    mas = ''.join(tarjeta(p, root) for p in otras)

    texto_bajada = bajada(post)
    resumen_visible = f'<p class="nota-bajada">{esc(texto_bajada)}</p>' if texto_bajada else ''
    return cabeza(root, tab, '\n'.join(x for x in extra if x)) + f'''
<body class="pagina-nota">
<div id="site-header">{header or ''}</div>
<main>
<article id="post-view">
<header class="nota-cabecera"><div class="nota-ancho">
<nav class="breadcrumbs" aria-label="Ruta"><a href="{root}">Inicio</a> <span class="sep">/</span> <a href="{root}blog/">Blog</a> <span class="sep">/</span> <span>{esc(sec)}</span></nav>
<a class="nota-seccion" href="{root}blog/?tema={quote(sec)}">{esc(sec)}</a>
<h1>{esc(titulo)}</h1>
{resumen_visible}
<p class="nota-datos">Por <a href="{root}nosotros/">{ORG_NAME}</a> · {fechas} · {minutos} min de lectura</p>
{portada}
</div></header>
<div class="nota-grilla{'' if aside else ' nota-grilla--sola'}">
{aside}
<div class="nota-columna">
<div class="post-content" id="post-content">{cuerpo}</div>
{blog_productos.final(equipos, root, titulo, WHATSAPP)}
{cta}
</div>
</div>
</article>
<section class="cat-blog-links" id="post-guide">{relacionados}</section>
<section class="nota-mas"><div class="container"><h2>Seguí leyendo</h2><div class="nota-grid">{mas}</div><p><a class="btn btn--ghost" href="{root}blog/">Ver todas las notas</a></p></div></section>
</main>
<div id="site-footer">{footer or ''}</div>
<script src="{root}assets/js/site.js?v={JS_V}"></script>
<script src="{root}assets/js/blog.js?v={CSS_V}"></script>
<script>mountChrome('blog');</script>
</body>
</html>
'''


def pagina_listado(posts):
    ruta = BASE_DIR / 'blog' / 'index.html'
    c = ruta.read_text(encoding='utf-8')
    root = '../'
    cuenta = {s: sum(1 for p in posts if seccion(p['slug']) == s) for s in SECCIONES}
    chips = f'<button type="button" class="nota-chip" data-tema="" aria-pressed="true">Todas <span>{len(posts)}</span></button>' + ''.join(
        f'<button type="button" class="nota-chip" data-tema="{esc(s)}" aria-pressed="false">{esc(s)} <span>{n}</span></button>' for s, n in cuenta.items() if n)
    filtros = (f'<div id="blog-filtros"><label class="nota-buscar"><span>Buscar en el blog</span><input type="search" id="blog-buscar" placeholder="Ej.: alinear camiones, elevador de 2 columnas" autocomplete="off"></label>'
               f'<div class="nota-chips" role="group" aria-label="Temas">{chips}</div><p id="blog-sin" hidden>No hay notas con esa búsqueda.</p></div>')
    cards = ''.join(tarjeta(p, root, 'h2', i < 3) for i, p in enumerate(posts))
    if 'id="blog-filtros"' not in c:
        c = c.replace('<div class="prod-grid" id="blog-grid">', '<div id="blog-filtros"></div>\n    <div class="nota-grid" id="blog-grid">', 1)
    c = replace_empty_el(c, 'blog-filtros', filtros[len('<div id="blog-filtros">'):-len('</div>')])
    c = replace_empty_el(c, 'blog-grid', cards)
    # el listado ya viene en el HTML: no hace falta bajar el texto de todo el blog
    if 'assets/js/blog.js' not in c:
        c = re.sub(r"<script>\s*mountChrome\('blog'\);.*?</script>",
                   f"<script src=\"../assets/js/blog.js?v={CSS_V}\"></script>\n<script>mountChrome('blog');</script>", c, count=1, flags=re.S)
    if 'assets/css/blog.css' not in c:
        c = c.replace('</head>', f'<link rel="stylesheet" href="../assets/css/blog.css?v={CSS_V}">\n<link rel="alternate" type="application/rss+xml" title="Blog de {ORG_NAME}" href="/feed.xml">\n</head>', 1)
    ruta.write_text(c, encoding='utf-8')


def feed(posts):
    ar = timezone(timedelta(hours=-3))
    items = []
    for p in posts[:30]:
        url = f'{SITE_URL}/blog/{p["slug"]}/'
        f = datetime.fromisoformat(p['date']).replace(tzinfo=ar)
        items.append(f'<item><title>{esc(p["title"])}</title><link>{url}</link><guid>{url}</guid><pubDate>{format_datetime(f)}</pubDate>'
                     f'<category>{esc(seccion(p["slug"]))}</category><description>{esc(strip_html(p.get("excerpt", "")))}</description></item>')
    (BASE_DIR / 'feed.xml').write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom"><channel>'
        f'<title>Blog de {ORG_NAME}</title><link>{SITE_URL}/blog/</link><language>es-AR</language>'
        f'<atom:link href="{SITE_URL}/feed.xml" rel="self" type="application/rss+xml"/>'
        '<description>Notas técnicas sobre equipamiento para talleres y gomerías.</description>\n' + '\n'.join(items) + '\n</channel></rss>\n',
        encoding='utf-8')


def a_texto(c):
    """HTML de la nota → texto con estructura (títulos, listas, tablas y enlaces absolutos)."""
    c = re.sub(r'<(script|style)\b.*?</\1>', '', c, flags=re.S)

    def enlace(m):
        destino = m.group(1).replace('../../', '/')
        if destino.startswith('/'):
            destino = SITE_URL + destino
        t = strip_html(m.group(2))
        return f'[{t}]({destino})' if t else ''
    c = re.sub(r'<a\b[^>]*href="([^"]+)"[^>]*>(.*?)</a>', enlace, c, flags=re.S)
    c = re.sub(r'<figcaption[^>]*>(.*?)</figcaption>', r'\n(Imagen: \1)\n', c, flags=re.S)
    c = re.sub(r'<tr[^>]*>(.*?)</tr>', lambda m: '\n| ' + ' | '.join(strip_html(x) for x in re.findall(r'<t[hd][^>]*>(.*?)</t[hd]>', m.group(1), re.S)) + ' |', c, flags=re.S)
    c = re.sub(r'<h2[^>]*>', '\n\n### ', c)
    c = re.sub(r'<(h3|h4|summary)[^>]*>', '\n\n#### ', c)
    c = re.sub(r'<li[^>]*>', '\n- ', c)
    c = re.sub(r'</(p|h2|h3|h4|summary|ul|ol|table|div|section|figure)>', '\n', c)
    c = html.unescape(re.sub(r'<[^>]+>', '', c))
    c = re.sub(r'[ \t]+', ' ', c)
    return re.sub(r'\n\s*\n\s*\n+', '\n\n', '\n'.join(x.strip() for x in c.split('\n'))).strip()


def texto_para_ia(posts):
    out = [f'# Blog de {ORG_NAME}: texto completo', '',
           f'> {len(posts)} notas sobre equipamiento para talleres y gomerías en Argentina, de la más nueva a la más vieja. Cada una indica su dirección y fecha; citar la página original.', '']
    for p in posts:
        out += [f'## {html.unescape(p["title"])}', '',
                f'URL: {SITE_URL}/blog/{p["slug"]}/', f'Tema: {seccion(p["slug"])} · Publicada: {p.get("date", "")[:10]}'
                + (f' · Actualizada: {p["updated"][:10]}' if p.get('updated') else ''), '', a_texto(p.get('content') or p.get('excerpt', '')), '']
    (BASE_DIR / 'llms-blog.txt').write_text('\n'.join(out), encoding='utf-8')


def cargar():
    posts = json.loads((BASE_DIR / 'data' / 'blog.json').read_text(encoding='utf-8'))
    return sorted(posts, key=lambda p: p.get('date', ''), reverse=True)


def build_all():
    posts = cargar()
    cat = json.loads((BASE_DIR / 'data' / 'catalog.json').read_text(encoding='utf-8'))
    productos = {p['slug']: p for p in cat['products']}
    (BASE_DIR / 'data' / 'blog.js').write_text(
        'window.BLOG_DATA = ' + json.dumps(json.loads((BASE_DIR / 'data' / 'blog.json').read_text(encoding='utf-8')), ensure_ascii=False) + _fin_blog_js(), encoding='utf-8')
    for p in posts:
        ruta = BASE_DIR / 'blog' / p['slug'] / 'index.html'
        ruta.parent.mkdir(parents=True, exist_ok=True)
        ruta.write_text(pagina_nota(p, posts, productos), encoding='utf-8')
    pagina_listado(posts)
    feed(posts)
    texto_para_ia(posts)
    print(f'✔ {len(posts)} notas, listado del blog, feed.xml y llms-blog.txt')


def _fin_blog_js():
    viejo = (BASE_DIR / 'data' / 'blog.js').read_text(encoding='utf-8').rstrip('\n')
    return ';' if viejo.endswith(';') else ''
