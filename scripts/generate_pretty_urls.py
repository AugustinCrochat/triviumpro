import os
import json
import re
import html as html_lib
import shutil

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, 'data', 'catalog.json')
from site_config import SITE_URL, ORG_NAME, load_chrome


def esc(s):
    return html_lib.escape(str(s or ''), quote=True)


def strip_tags(s):
    """Texto plano a partir de HTML, para meta descriptions."""
    text = re.sub(r'<[^>]+>', ' ', s or '')
    text = html_lib.unescape(text)
    return re.sub(r'\s+', ' ', text).strip()


def clamp(text, limit=158):
    """Recorta en el límite de palabra, sin cortar al medio."""
    text = re.sub(r'\s+', ' ', (text or '')).strip()
    if len(text) <= limit:
        return text
    cut = text[:limit].rsplit(' ', 1)[0].rstrip(' .,;:·-')
    return cut + '…'


def load_public_offers():
    """Precios públicos + dólar del día, para las offers del Product schema.

    Entra todo lo público en data/prices-publico.json. Los ítems con
    tienda:false llevan 'tienda': False: se ven sólo en su ficha (igual que en
    site.js), no en grillas, guías ni feeds. El dólar se pide en vivo con fallback fijo, igual que
    generate_meta_catalog.py: sin red, el generador sigue andando.
    """
    import urllib.request
    from datetime import date, timedelta

    path = os.path.join(BASE_DIR, 'data', 'prices-publico.json')
    if not os.path.exists(path):
        return {}, None
    with open(path, encoding='utf-8') as f:
        prices = json.load(f)

    rate = 1535
    try:
        with urllib.request.urlopen('https://dolarapi.com/v1/dolares/oficial', timeout=8) as r:
            j = json.load(r)
            if j.get('venta'):
                rate = j['venta']
    except Exception:
        pass

    valid = (date.today() + timedelta(days=30)).isoformat()
    out = {}
    for sku, rec in prices['items'].items():
        base = rec['fixed_ars'] if rec.get('fixed_ars') is not None else rec['usd'] * rate
        iva = rec.get('iva', prices['meta']['default_iva'])
        out[sku] = {
            'price': round(base * (1 + iva / 100), 2),
            'iva': iva,
            'modelo': rec.get('modelo'),
            'tienda': rec.get('tienda') is not False,
            'valid': valid,
        }
    return out, rate


# <title> orientado a búsqueda de compra. El H1 sigue siendo el nombre corto.
CATEGORY_TITLES = {
    'elevadores': 'Elevadores para taller y gomería',
    'elevadores-2-columnas': 'Elevadores de 2 columnas para taller',
    'elevadores-4-columnas': 'Elevadores de 4 columnas para alineación',
    'elevadores-tijera': 'Elevadores tijera para taller y gomería',
    'elevadores-pesados': 'Elevadores para camiones y pesados',
    'elevadores-motos': 'Elevadores para motos',
    'alineadoras': 'Alineadoras 3D para autos y camiones',
    'balanceadoras': 'Balanceadoras de ruedas para gomería',
    'desarmadoras': 'Desarmadoras de neumáticos para gomería',
}


# Posicionamiento por marca: Trivium Pro es la línea económica; Hofmann, Rotary
# Lift y Challenger Lifts son las marcas de mayor calibre. (título, descripción)
BRAND_SEO = {
    'trivium-pro': (
        "Equipos de taller económicos",
        "Trivium Pro, línea económica: {n} equipos para talleres y gomerías "
        "(elevadores, balanceadoras, desarmadoras) a precio accesible. Instalación "
        "a cotizar en todo el país."),
    'hofmann': (
        "Hofmann Argentina: alineadoras y balanceadoras",
        "Hofmann (Snap-on): {n} equipos de alineación, balanceo y desarmado de mayor "
        "calibre para talleres de alto volumen. Instalación a cotizar en todo el país."),
    'rotary-lift': (
        "Rotary Lift Argentina: elevadores para taller",
        "Rotary Lift: {n} elevadores de mayor calibre para talleres, concesionarias "
        "y flotas. Distribuidor oficial; instalación a cotizar en todo el país."),
    'challenger-lifts': (
        "Challenger Lifts Argentina: elevadores",
        "Challenger Lifts (Snap-on): elevadores certificados ALI de mayor calibre "
        "para uso intensivo. Instalación a cotizar en todo el país."),
}


def product_meta_description(prod):
    """Meta description de ficha: nombre + un diferencial + llamado a cotizar.

    Antes se usaban los bullets crudos, que en varias fichas son etiquetas
    sueltas ("Eléctricos a batería · Exóticos de perfil bajo"): no dicen qué
    es el equipo. El nombre ya trae tipo, capacidad, marca y modelo.
    """
    cta = " Cotizá envío e instalación a todo el país."
    extra = ''
    for b in prod.get('bullets') or []:
        b = re.sub(r'\s+', ' ', strip_tags(b)).replace(' : ', ': ').strip()
        if len(b) >= 35:
            extra = b.rstrip('. ')
            break
    if prod.get('summary'):
        extra = strip_tags(prod['summary']).rstrip('. ')
    base = prod['name'].strip().rstrip('.')
    head = f"{base}. {extra}."
    if len(head) + len(cta) > 158:
        head = f"{base}."
    return clamp(head, 158 - len(cta)) + cta


def make_seo_block(canonical, description, jsonld=None):
    """canonical + meta description + JSON-LD. Los OG se agregan aparte."""
    out = [
        f'<link rel="canonical" href="{esc(canonical)}">',
        f'<meta name="description" content="{esc(description)}">',
        # max-image-preview:large habilita las vistas previas grandes en Google
        # (Discover incluido); sin esto Google recorta la imagen a thumbnail.
        '<meta name="robots" content="index, follow, max-image-preview:large">',
    ]
    for block in (jsonld or []):
        payload = json.dumps(block, ensure_ascii=False, separators=(',', ':'))
        # Evita cerrar el <script> antes de tiempo si algún texto trae "</script>"
        payload = payload.replace('</', '<\\/')
        out.append(f'<script type="application/ld+json">{payload}</script>')
    return '\n'.join(out)


def itemlist_jsonld(products, brands_by_slug=None):
    """ItemList de una categoría o marca: ayuda a Google (y a un asistente de
    compras) a entender que la página es un listado de productos concretos, no
    sólo texto — mismo criterio que las 'rich results' de listados de e-commerce."""
    items = []
    for i, p in enumerate(products, 1):
        items.append({
            "@type": "ListItem",
            "position": i,
            "url": f"{SITE_URL}/producto/{p['slug']}/",
            "name": p['name'],
        })
    return {"@context": "https://schema.org", "@type": "ItemList",
            "itemListElement": items}


def faq_jsonld(items):
    """items: lista de (pregunta, respuesta en texto plano)."""
    return {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": q,
                "acceptedAnswer": {"@type": "Answer", "text": a},
            }
            for q, a in items
        ],
    }


def faq_html(title, items):
    """<details>/<summary> nativos: sin JS, visibles para usuarios y crawlers
    por igual, a diferencia del resto del cuerpo que sólo lleva contenido
    prerenderizado para el crawler porque site.js lo pisa al hidratar."""
    if not items:
        return ''
    entries = ''.join(
        f'<details><summary>{esc(q)}</summary><p>{esc(a)}</p></details>'
        for q, a in items
    )
    return f'<div class="container"><h2>{esc(title)}</h2>{entries}</div>'


# Preguntas frecuentes por categoría raíz: apuntan a las búsquedas reales
# ("elevador de auto", "alineadora computarizada") y a las comparaciones que
# resuelven un LLM al recomendar equipamiento (línea premium vs. económica).
CATEGORY_FAQS = {
    'elevadores': [
        ("¿Qué elevador de auto conviene para un taller multimarca?",
         "Para un taller que recibe autos y SUVs en general, el estándar es un elevador "
         "de dos columnas de 4 a 4,5 toneladas, como los Rotary Lift SPOA. Si el taller "
         "también levanta utilitarios o camionetas pesadas, conviene sumar un elevador "
         "de cuatro columnas o uno de mayor capacidad."),
        ("¿Elevador de dos columnas o de cuatro columnas, cuál elegir?",
         "El de dos columnas ocupa menos espacio y da acceso total a la parte baja del "
         "vehículo, ideal para mecánica general. El de cuatro columnas es más estable "
         "para alineación, service rápido y almacenaje de vehículos, y no requiere "
         "puntos de levante específicos."),
        ("¿Cuál es la diferencia entre un elevador Rotary Lift y uno de la línea Trivium Pro?",
         "Rotary Lift es la marca premium: fabricación en EE.UU., mayor vida útil y "
         "el estándar de los talleres de concesionarias. La línea Trivium Pro es "
         "equipamiento económico propio, pensado para talleres que buscan una "
         "relación precio-calidad más ajustada sin resignar norma de seguridad."),
        ("¿Los elevadores para motos y para camiones son distintos a los de auto?",
         "Sí. Un elevador para motos usa una plataforma y trabas específicas para dos "
         "ruedas, y uno para camiones o vehículos pesados tiene mayor capacidad de "
         "carga y columnas reforzadas. Trivium Pro tiene líneas dedicadas a cada caso."),
    ],
    'alineadoras': [
        ("¿Qué es una alineadora computarizada y para qué sirve?",
         "Es un equipo con cámaras o sensores que mide el ángulo de las ruedas "
         "(convergencia, caída, avance) contra la especificación del fabricante, para "
         "corregir el desgaste irregular de neumáticos y la dirección del vehículo."),
        ("¿Hofmann es una marca líder en alineadoras?",
         "Sí, Hofmann (Snap-on) es una de las marcas de referencia mundial en "
         "alineación de precisión, con equipos 3D e IA para talleres y concesionarias."),
        ("¿Qué alineadora conviene para un taller que recién arranca?",
         "Depende del volumen de autos por día y del presupuesto: una alineadora 3D "
         "de entrada da precisión suficiente para la mayoría de los talleres, mientras "
         "que los equipos Hofmann de alta gama suman mayor velocidad de medición y "
         "reportes para clientes exigentes."),
    ],
    'balanceadoras': [
        ("¿Qué balanceadora necesito para ruedas de auto y camioneta?",
         "Una balanceadora electrónica estándar cubre autos y SUVs; si el taller "
         "también trabaja con ruedas de camioneta o llantas grandes, conviene un "
         "modelo con mayor capacidad de diámetro y peso de rueda."),
        ("¿Qué diferencia hay entre una balanceadora manual y una automática?",
         "La automática mide y posiciona el punto de balanceo sin que el operario "
         "gire la rueda a mano, lo que agiliza el trabajo y reduce el margen de "
         "error en talleres de alto volumen."),
    ],
    'desarmadoras': [
        ("¿Qué desarmadora de neumáticos conviene para una gomería?",
         "Para uso general de autos alcanza una desarmadora estándar sin brazo de "
         "ayuda; para llantas de aleación, run-flat o de camioneta conviene un modelo "
         "con brazo de ayuda y mordazas que no dañen la llanta."),
        ("¿Las desarmadoras sirven también para llantas de aleación?",
         "Sí, siempre que tengan mordazas protegidas o de plástico para no marcar la "
         "llanta; es un punto a revisar antes de comprar si el taller trabaja con "
         "aros de aleación."),
    ],
}


HOME_FAQS = [
    ("¿Qué máquinas de taller vende Trivium Pro?",
     "Elevadores de auto, alineadoras, balanceadoras y desarmadoras de neumáticos, "
     "más herramientas neumáticas, muebles de taller y equipos de aire comprimido. "
     "Catálogo completo en pro.trivium.ar/catalogo/."),
    ("¿Trivium Pro es representante oficial de Rotary Lift y Hofmann en Argentina?",
     "Sí, Trivium Pro representa e importa de forma oficial a Rotary Lift (elevadores, "
     "EE.UU.) y Hofmann (alineadoras y balanceadoras, Snap-on), con instalación y "
     "servicio técnico propios en todo el país."),
    ("¿Trivium Pro tiene una línea de equipamiento más económica?",
     "Sí, Trivium Pro es también la marca propia de la empresa: una línea de "
     "elevadores, balanceadoras, desarmadoras y equipamiento de taller de precio más "
     "accesible que las marcas premium, pensada para talleres que arrancan o amplían "
     "capacidad sin resignar norma de seguridad."),
    ("¿Trivium Pro instala el equipamiento o solo lo vende?",
     "Instala. El equipo técnico propio hace el montaje, la puesta en marcha y el "
     "servicio post-venta en todo el país, no sólo la venta del equipo. La "
     "instalación se cotiza aparte del precio del equipo."),
    ("¿Hacen envíos de equipamiento de taller a todo el país?",
     "Sí, Trivium Pro envía e instala en todo el territorio argentino, no sólo en "
     "Córdoba y Buenos Aires. El envío y la instalación se cotizan aparte."),
]


# Notas técnicas del blog que ya existen y responden justo lo que busca
# alguien en esa categoría — evita escribir contenido nuevo redundante:
# el blog ya tiene guías profundas, sólo faltaba enlazarlas desde acá.
CATEGORY_BLOG_POSTS = {
    'elevadores': [
        'como-elegir-el-elevador-adecuado-para-hacer-alineacion',
        'diferencias-entre-elevadores-de-2-columnas-de-piso-libre-y-travesano-al-piso',
        'elevador-de-4-columnas-vs-elevador-de-tijera-largo-cual-elegir-para-alineacion',
        'que-tipo-de-elevador-elegir-para-cambio-de-aceite',
        'por-que-elegir-un-elevador-con-brazos-all-vehicle-de-rotary-lift',
        'especificaciones-del-piso-para-la-instalacion-de-un-elevador-de-dos-columnas',
    ],
    'alineadoras': [
        'como-elegir-la-alineadora-de-autos-ideal-para-tu-taller',
        'como-funciona-una-alineadora-y-su-importancia-en-talleres-y-gomerias',
        'como-se-alinea-un-vehiculo-con-una-alineadora-3d',
        'alineadoras-5d-el-mito-de-las-dimensiones-en-equipos-de-alineacion',
        'los-beneficios-de-tener-una-alineadora-en-tu-taller-o-gomeria',
        'como-funciona-la-alineacion-3d-de-autos-tecnologia-y-beneficios',
    ],
    'balanceadoras': [
        'balanceadoras-de-ruedas-con-o-sin-monitor-cual-elegir',
        'autocalibracion-en-una-balanceadora-de-ruedas-que-es-y-por-que-es-importante',
        'errores-comunes-al-usar-una-balanceadora-y-como-evitarlos',
        'por-que-incorporar-una-balanceadora-de-ruedas-en-tu-gomeria-es-una-decision-inteligente',
        'la-importancia-de-balancear-ruedas-beneficios-clave-para-talleres-y-gomerias',
    ],
    'desarmadoras': [
        'para-que-sirve-el-brazo-auxiliar-en-una-desarmadora-de-neumaticos',
        'como-funcionan-las-desarmadoras-para-neumaticos-runflat-guia-para-talleres-y-gomerias',
        'como-mantener-tu-desarmadora-trivium-center-en-optimas-condiciones',
        'equipamiento-esencial-para-comenzar-tu-taller-de-neumaticos',
    ],
}


# Guía de compra (/guias/) que corresponde a cada categoría.
CATEGORY_GUIDES = {
    'elevadores': ('elevadores-para-taller', 'Guía de compra: cómo elegir un elevador para taller'),
    'elevadores-2-columnas': ('elevadores-para-taller', 'Guía de compra: cómo elegir un elevador para taller'),
    'elevadores-4-columnas': ('elevadores-para-taller', 'Guía de compra: cómo elegir un elevador para taller'),
    'elevadores-tijera': ('elevadores-para-taller', 'Guía de compra: cómo elegir un elevador para taller'),
    'elevadores-pesados': ('elevadores-para-taller', 'Guía de compra: cómo elegir un elevador para taller'),
    'alineadoras': ('alineadoras-3d', 'Guía de compra: cómo elegir una alineadora 3D'),
    'balanceadoras': ('balanceadoras-de-ruedas', 'Guía de compra: cómo elegir una balanceadora de ruedas'),
    'desarmadoras': ('desarmadoras-de-neumaticos', 'Guía de compra: cómo elegir una desarmadora de neumáticos'),
}


# Categorías sin guía propia que se resuelven con la guía de equipar una gomería
# o con la de su equipo principal.
CATEGORY_GUIDES.update({
    'accesorios-balanceo': ('balanceadoras-de-ruedas', 'Guía de compra: cómo elegir una balanceadora de ruedas'),
    'herramientas-neumaticas': ('equipar-una-gomeria', 'Guía: cómo equipar una gomería'),
    'aire-comprimido': ('equipar-una-gomeria', 'Guía: cómo equipar una gomería'),
    'equipamiento-taller': ('equipar-una-gomeria', 'Guía: cómo equipar una gomería'),
    'muebles-taller': ('equipar-una-gomeria', 'Guía: cómo equipar una gomería'),
})


def product_guide_html(cat_slug, root):
    """Enlaces internos de la ficha hacia su guía de compra y al hub de zonas.

    Va en #pd-guide, fuera de #pd-wrap, porque producto.html reescribe #pd-wrap
    al hidratar y lo prerenderizado ahí no sobrevive al JS.
    """
    g = CATEGORY_GUIDES.get(cat_slug)
    parts = []
    if g:
        parts.append(f'<a href="{esc(root)}guias/{esc(g[0])}/">{esc(g[1])} →</a>')
    parts.append(f'<a href="{esc(root)}zonas/">Envíos, instalación y posventa en todo el país →</a>')
    items = ''.join(f'<li>{p}</li>' for p in parts)
    return (f'<div class="container"><h2>Antes de comprar</h2>'
            f'<ul class="guia-lista">{items}</ul></div>')


def guide_link_html(slug, root):
    g = CATEGORY_GUIDES.get(slug)
    if not g:
        return ''
    return (f'<div class="container"><h2>Antes de comprar</h2>'
            f'<p><a href="{esc(root)}guias/{esc(g[0])}/">{esc(g[1])} →</a></p></div>')


def blog_links_html(title, slugs, blog_by_slug, root):
    """Grilla de notas del blog relacionadas, con las mismas clases prod-card
    que usa el blog para 'Más noticias': no suma CSS nueva."""
    posts = [blog_by_slug[s] for s in slugs if s in blog_by_slug]
    if not posts:
        return ''
    cards = ''.join(
        f'<a class="prod-card" href="{esc(root)}blog/{esc(p["slug"])}/">'
        f'<div class="body"><h3>{esc(html_lib.unescape(p["title"]))}</h3></div></a>'
        for p in posts
    )
    return (f'<div class="container"><h2>{esc(title)}</h2>'
            f'<div class="prod-grid">{cards}</div></div>')


def breadcrumb_jsonld(items):
    """items: lista de (nombre, url_absoluta). El último suele ir sin url."""
    elements = []
    for i, (name, url) in enumerate(items, start=1):
        el = {"@type": "ListItem", "position": i, "name": name}
        if url:
            el["item"] = url
        elements.append(el)
    return {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": elements,
    }


def breadcrumb_html(items, root):
    """items: lista de (nombre, href_relativo o None para el actual)."""
    parts = []
    for name, href in items:
        if href:
            parts.append(f'<a href="{esc(root + href)}">{esc(name)}</a>')
        else:
            parts.append(f'<span>{esc(name)}</span>')
    return ' <span class="sep">/</span> '.join(parts)


def brand_logo_rel(slug):
    """'assets/img/marcas/logo-<slug>.svg' si el archivo existe, si no None.

    Fuente de verdad = el archivo en disco, no un mapa a mano: así no puede
    desincronizarse del BRAND_LOGOS de site.js (pasó con Prevost: tenía el
    archivo pero faltaba en el mapa y nunca mostraba su logo)."""
    rel = f'assets/img/marcas/logo-{slug}.svg'
    return rel if os.path.exists(os.path.join(BASE_DIR, rel)) else None


def price_tag_html(sku, offers_by_sku, en_ficha=False):
    """Réplica estática de cardPriceHtml() de site.js. En la ficha aclara que la
    instalación no está incluida en el precio."""
    offer = (offers_by_sku or {}).get(sku)
    if not offer or (not offer['tienda'] and not en_ficha):
        return ''
    monto = '$ ' + f"{round(offer['price']):,}".replace(',', '.')
    iva = offer['iva']
    iva_lbl = (str(int(iva)) if float(iva).is_integer() else str(iva).replace('.', ',')) + '%'
    nota = ' · Instalación no incluida' if en_ficha else ''
    return f'<div class="price-tag">{monto}<span>IVA {iva_lbl} incluido{nota}</span></div>'


# Espejo de ORIGIN_BADGES de assets/js/site.js (sellos de origen sobre la foto).
ORIGIN_BADGES = {
    'made-in-usa': ('Made in USA', 'assets/img/iconos/origen/usa.svg'),
    'made-in-italy': ('Made in Italy', 'assets/img/iconos/origen/italy.svg'),
}


def origin_badge_html(prod, root):
    for bid in prod.get('badges') or []:
        if bid in ORIGIN_BADGES:
            label, flag = ORIGIN_BADGES[bid]
            return (f'<span class="origin-badge"><img src="{esc(root + flag)}" alt="">'
                    f'{esc(label)}</span>')
    return ''


def product_card_html(prod, brands_by_slug, root, offers_by_sku=None):
    """Réplica estática de productCard() de site.js, para que el HTML traiga los links."""
    brand = brands_by_slug.get(prod.get('brand'), {})
    brand_name = brand.get('name', '')
    img = ''
    if prod.get('image'):
        img = (f'<img src="{esc(root + prod["image"])}" alt="{esc(prod["name"])}" '
               f'loading="lazy" width="400" height="300">')
    logo = brand_logo_rel(prod.get('brand', ''))
    thumb_brand = (f'<span class="thumb-brand"><img src="{esc(root + logo)}" alt="{esc(brand_name)}"></span>'
                   if logo else '')
    specs = ''
    if prod.get('capacity') or prod.get('lift_height'):
        specs = ('<div class="spec">'
                 f'<span>Capacidad <b>{esc(prod.get("capacity", "—"))}</b></span>'
                 f'<span>Altura <b>{esc(prod.get("lift_height", "—"))}</b></span>'
                 '</div>')
    price = price_tag_html(prod.get('sku', ''), offers_by_sku)
    return (
        f'<a class="prod-card" href="{esc(root)}producto/{esc(prod["slug"])}/">'
        f'<div class="thumb">{img}{thumb_brand}{origin_badge_html(prod, root)}</div>'
        f'<div class="body">'
        f'<span class="brand-tag">{esc(brand_name)}</span>'
        f'<h3>{esc(prod["name"])}</h3>'
        f'{specs}'
        f'{price}'
        f'</div></a>'
    )


def replace_empty_el(content, el_id, inner):
    """Rellena un contenedor vacío (<div id="x"></div>) con HTML prerenderizado.

    El JS lo sobrescribe al hidratar; esto existe para que el crawler vea el
    contenido y los links sin ejecutar JavaScript.

    Busca la etiqueta de cierre que corresponde contando anidamiento: el
    contenido inyectado trae <div> adentro, y un regex no-greedy cortaría en
    el primer </div>.
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


def make_og_block(title, description, image_url, url, og_type="website"):
    t = html_lib.escape(title, quote=True)
    d = html_lib.escape(description, quote=True)
    img = html_lib.escape(image_url, quote=True)
    u = html_lib.escape(url, quote=True)
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


def create_index_file(target_dir, template_path, root_depth, title=None, description=None,
                      og=None, seo=None, body=None):
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Adjust root path
    root_val = '../' * root_depth
    content = content.replace('meta name="tv-root" content=""', f'meta name="tv-root" content="{root_val}"')

    # Adjust asset paths (very basic replacement, assuming they start with assets/ or scripts/)
    # Better to use the rootPath() function in JS, but CSS/JS links in HTML need correction
    content = content.replace('href="assets/', f'href="{root_val}assets/')
    content = content.replace('src="assets/', f'src="{root_val}assets/')
    content = content.replace('src="scripts/', f'src="{root_val}scripts/')

    # Update title
    if title:
        content = re.sub(r'<title>[^<]*</title>', f'<title>{html_lib.escape(title)} — {ORG_NAME}</title>', content, count=1)

    # Inject OG tags
    if og:
        og_block = make_og_block(og['title'], og.get('description', ''), og.get('image', ''), og['url'], og.get('type', 'website'))
        content = content.replace('</head>', og_block + '\n</head>', 1)

    # canonical + meta description + JSON-LD
    if seo:
        content = content.replace('</head>', seo + '\n</head>', 1)

    # Header y footer: los inyecta site.js en el cliente, así que sin esto el
    # crawler ve la página sin navegación ni enlaces internos.
    header, footer = load_chrome(root_val)
    if header:
        content = replace_empty_el(content, 'site-header', header)
        content = replace_empty_el(content, 'site-footer', footer)

    # Contenido prerenderizado dentro de los contenedores que hidrata el JS
    for el_id, inner in (body or {}).items():
        content = replace_empty_el(content, el_id, inner)

    target_path = os.path.join(target_dir, 'index.html')
    with open(target_path, 'w', encoding='utf-8') as f:
        f.write(content)

def update_static_pages(catalog):
    """Completa las páginas sueltas: chrome, canonical, description y JSON-LD.

    index.html, /catalogo/, /marcas/, /blog/ y las institucionales no salen de
    ninguna plantilla — sus templates ya no existen en la raíz, así que el
    generador las salteaba y quedaban sin nada. Se editan a mano, así que acá
    sólo se agrega lo que falta, de forma idempotente: se limpia lo inyectado
    antes y se vuelve a poner. El contenido editorial no se toca.
    """
    n_prod = len(catalog['products'])
    n_cat = len(catalog['categories'])
    n_marcas = len(catalog['brands'])

    # carpeta: (nombre para las migas, descripción, título completo).
    # El título va explícito y no derivado del que había: la home usaba el
    # formato "Sitio — Bajada", así que reescribir sólo el sufijo la dejaba en
    # "Trivium Center — Trivium Pro".
    paginas = {
        '': (None,
             f"Equipamiento para talleres mecánicos y gomerías en todo el país: "
             f"elevadores, alineadoras, balanceadoras y desarmadoras. Representantes "
             f"oficiales de Rotary Lift y Hofmann en Argentina.",
             f"{ORG_NAME} — Equipamiento para talleres mecánicos en Argentina"),
        'catalogo': ("Catálogo",
             f"Catálogo completo: {n_prod} equipos para taller en {n_cat} categorías. "
             f"Elevadores, alineadoras, balanceadoras y desarmadoras, con instalación "
             f"y servicio en todo el país.",
             f"Catálogo completo — {ORG_NAME}"),
        'marcas': ("Marcas",
             f"Las {n_marcas} marcas que representamos: Rotary Lift, Hofmann, Forward "
             f"Lift, Direct Lift, Haweka y Trivium Pro. Distribuidores oficiales en "
             f"Argentina, con repuestos y soporte técnico.",
             f"Marcas que representamos — {ORG_NAME}"),
        'instalacion-posventa-y-servicios': ("Servicios",
             "Instalación, puesta en marcha, mantenimiento preventivo y servicio "
             "post-venta de equipamiento de taller en todo el país.",
             f"Instalación y posventa — {ORG_NAME}"),
        'nosotros': ("Nosotros",
             f"{ORG_NAME}: equipamiento para talleres y gomerías en Argentina. "
             f"Representantes oficiales de Rotary Lift y Hofmann, con servicio "
             f"técnico e instalación propios.",
             f"Nosotros — {ORG_NAME}"),
        'contacto': ("Contacto",
             "Pedí tu cotización de equipamiento para taller. Atendemos consultas "
             "técnicas y comerciales en todo el país.",
             f"Contacto — {ORG_NAME}"),
        'lista-precios': ("Lista de precios",
             f"Lista de precios actualizada de equipamiento para taller {ORG_NAME}: "
             f"precio de lista y precio final con IVA de cada equipo, lista para "
             f"imprimir o descargar en PDF.",
             f"Lista de precios — {ORG_NAME}"),
        'blog': ("Blog",
             "Notas técnicas sobre equipamiento de taller: cómo elegir elevadores "
             "y alineadoras, montar una gomería y mantener tus equipos.",
             f"Blog y noticias — {ORG_NAME}"),
    }

    for carpeta, (nombre, desc, titulo) in paginas.items():
        path = os.path.join(BASE_DIR, carpeta, 'index.html') if carpeta else os.path.join(BASE_DIR, 'index.html')
        if not os.path.exists(path):
            continue
        with open(path, encoding='utf-8') as fh:
            content = fh.read()

        root_val = '../' if carpeta else ''
        header, footer = load_chrome(root_val)
        if header:
            content = replace_empty_el(content, 'site-header', header)
            content = replace_empty_el(content, 'site-footer', footer)

        # El <title> y los OG están escritos a mano en cada archivo: hay que
        # reescribirlos o queda el nombre viejo del sitio tras el rebranding.
        content = re.sub(r'<title>.*?</title>',
                         f'<title>{html_lib.escape(titulo)}</title>',
                         content, count=1, flags=re.S)
        content = re.sub(r'\n?<meta property="og:[^>]*>', '', content)
        content = re.sub(r'\n?<meta name="twitter:[^>]*>', '', content)
        content = re.sub(r'\n?<link rel="canonical"[^>]*>', '', content)
        content = re.sub(r'\n?<meta name="description"[^>]*>', '', content)
        content = re.sub(r'\n?<meta name="robots"[^>]*>', '', content)
        content = re.sub(r'\n?<script type="application/ld\+json">.*?</script>', '',
                         content, flags=re.S)

        url = f"{SITE_URL}/{carpeta}/" if carpeta else f"{SITE_URL}/"
        if carpeta:
            jsonld = [breadcrumb_jsonld([("Inicio", f"{SITE_URL}/"), (nombre, url)])]
        else:
            # No hay SearchAction: el sitio no tiene buscador. Declarar uno que no
            # funciona es peor que no declarar nada — Google lo detecta al probarlo.
            #
            # No es LocalBusiness: Trivium Pro vende a talleres en todo el país,
            # no es un local a donde el público llega a comprar un elevador. La
            # dirección de Av. Donato Álvarez 7971 es la de Neumáticos Trivium
            # (misma razón social, TRIVIUM CENTER S.A.), así que va como address
            # de la Organization, no como local de esta marca.
            jsonld = [{
                "@context": "https://schema.org",
                "@type": ["Organization", "LocalBusiness"],
                "name": ORG_NAME,
                "legalName": "Trivium Center S.A.",
                "url": f"{SITE_URL}/",
                "logo": f"{SITE_URL}/assets/img/logo-trivium.svg",
                "description": desc,
                "areaServed": {"@type": "Country", "name": "Argentina"},
                "address": {
                    "@type": "PostalAddress",
                    "streetAddress": "Av. Donato Álvarez 7971",
                    "addressLocality": "Córdoba",
                    "addressCountry": "AR",
                },
                "email": "info@trivium.ar",
                "telephone": "+54 9 11 2701-5294",
                "contactPoint": [{
                    "@type": "ContactPoint",
                    "contactType": "sales",
                    "telephone": "+54 9 11 2701-5294",
                    "email": "info@trivium.ar",
                    "areaServed": "AR",
                    "availableLanguage": "Spanish",
                }],
                "sameAs": [
                    "https://www.instagram.com/trivium.center/",
                    "https://www.facebook.com/profile.php?id=61571497817317",
                    "https://www.youtube.com/channel/UCkyhOuIT5A9nZ7qCAszVIaQ",
                ],
            }, {
                "@context": "https://schema.org",
                "@type": "WebSite",
                "name": ORG_NAME,
                "url": f"{SITE_URL}/",
            }, faq_jsonld(HOME_FAQS)]

        og = make_og_block(titulo, desc,
                           f"{SITE_URL}/assets/img/og-trivium.png", url)
        content = content.replace('</head>', og + '\n' + make_seo_block(url, desc, jsonld) + '\n</head>', 1)
        with open(path, 'w', encoding='utf-8') as fh:
            fh.write(content)
    print(f"  -> {len(paginas)} páginas sueltas con chrome, canonical, description y JSON-LD")


def main():
    print("Generating pretty URLs...")
    
    with open(DATA_PATH, 'r', encoding='utf-8') as f:
        catalog = json.load(f)

    offers_by_sku, dolar_rate = load_public_offers()
    print(f"  ({len(offers_by_sku)} equipos con precio público para el schema Offer)")

    blog_path = os.path.join(BASE_DIR, 'data', 'blog.json')
    blog_by_slug = {}
    if os.path.exists(blog_path):
        with open(blog_path, encoding='utf-8') as f:
            blog_by_slug = {p['slug']: p for p in json.load(f)}

    # 1. Main Pages
    main_pages = {
        'nosotros.html': 'nosotros',
        'servicios.html': 'instalacion-posventa-y-servicios',
        'contacto.html': 'contacto',
        'marcas.html': 'marcas',
        'catalogo.html': 'catalogo'
    }
    
    for template, folder in main_pages.items():
        template_path = os.path.join(BASE_DIR, template)
        if os.path.exists(template_path):
            print(f"  -> {folder}/")
            create_index_file(os.path.join(BASE_DIR, folder), template_path, 1)

    brands_by_slug = {b['slug']: b for b in catalog['brands']}
    cats_by_slug = {c['slug']: c for c in catalog['categories']}
    root2 = '../../'

    def descendants(slug):
        """Una categoría padre incluye los productos de sus hijas."""
        kids = {c['slug'] for c in catalog['categories'] if c.get('parent') == slug}
        return {slug} | kids

    sidebar_cats = ''.join(
        f'<li><a href="{root2}categoria/{esc(c["slug"])}/">{esc(c["name"])}</a></li>'
        for c in catalog['categories']
    )
    sidebar_brands = ''.join(
        f'<li><a href="{root2}marca/{esc(b["slug"])}/">{esc(b["name"])}</a></li>'
        for b in catalog['brands']
    )

    # 2. Categories
    cat_template = os.path.join(BASE_DIR, 'categoria.html')
    if os.path.exists(cat_template):
        for cat in catalog['categories']:
            slug = cat['slug']
            print(f"  -> categoria/{slug}/")
            fam = descendants(slug)
            prods = [p for p in catalog['products'] if p.get('category') in fam]
            url = f"{SITE_URL}/categoria/{slug}/"
            tagline = cat.get('tagline') or ''
            # Las subcategorías de elevadores se llaman "Tijera" o "2 Columnas"
            # porque en el menú cuelgan de "Elevadores", pero como <title> y H1
            # no compiten por nada: ahí va el nombre largo.
            nombre = cat.get('seo_name') or cat['name']
            # En las 4 categorías donde compite gente buscando "barato" contra
            # gente buscando "el mejor", el <meta description> nombra las dos
            # puntas (Rotary Lift/Hofmann premium, Trivium Pro económica) para
            # calzar con ambas intenciones de búsqueda.
            if slug in ('elevadores', 'alineadoras', 'balanceadoras', 'desarmadoras'):
                premium = ("Rotary Lift y Challenger Lifts" if slug == 'elevadores' else "Hofmann")
                gama = (f"Premium de mayor calibre ({premium}) y línea económica "
                        "Trivium Pro.")
            else:
                gama = "Representantes oficiales Rotary Lift y Hofmann en Argentina."
            desc = clamp(
                f"{nombre} para taller: {len(prods)} equipos. {gama} "
                f"Instalación a cotizar en todo el país."
            )
            crumbs = [("Inicio", ""), ("Catálogo", "catalogo/")]
            if cat.get('parent') and cat['parent'] in cats_by_slug:
                parent = cats_by_slug[cat['parent']]
                crumbs.append((parent['name'], f"categoria/{parent['slug']}/"))
            crumbs.append((cat['name'], None))
            jsonld = [breadcrumb_jsonld([
                (n, SITE_URL + '/' + (h or '')) if h is not None else (n, url)
                for n, h in crumbs
            ])]
            if prods:
                jsonld.append(itemlist_jsonld(prods))
            # Las FAQ van sólo en la categoría raíz (elevadores, no
            # elevadores-tijera): ahí es donde busca la gente y donde un LLM
            # arma la comparación premium/económica, no en cada subtipo.
            faqs = CATEGORY_FAQS.get(slug, [])
            if faqs:
                jsonld.append(faq_jsonld(faqs))
            posts_html = blog_links_html(
                "Guías relacionadas", CATEGORY_BLOG_POSTS.get(slug, []), blog_by_slug, root2)
            posts_html = guide_link_html(slug, root2) + posts_html
            grid = ''.join(product_card_html(p, brands_by_slug, root2, offers_by_sku) for p in prods)
            create_index_file(
                os.path.join(BASE_DIR, 'categoria', slug), cat_template, 2,
                title=CATEGORY_TITLES.get(slug, nombre),
                og={'type': 'website', 'title': f"{nombre} — Equipamiento de taller",
                    'description': desc, 'image': f"{SITE_URL}/assets/img/logo-trivium.svg",
                    'url': url},
                seo=make_seo_block(url, desc, jsonld),
                body={
                    'crumbs': breadcrumb_html(crumbs, root2),
                    'cat-title': esc(nombre),
                    'cat-tag': esc(tagline),
                    'cat-count': f"{len(prods)} productos",
                    'count': f"{len(prods)} productos",
                    'cat-list': sidebar_cats,
                    'brand-list': sidebar_brands,
                    'grid': grid,
                    'cat-faq': faq_html(f"Preguntas frecuentes sobre {nombre.lower()}", faqs),
                    'cat-posts': posts_html,
                },
            )

    # 3. Brands (using marca/ prefix as per old site)
    if os.path.exists(cat_template):
        for brand in catalog['brands']:
            slug = brand['slug']
            print(f"  -> marca/{slug}/")
            prods = [p for p in catalog['products'] if p.get('brand') == slug]
            url = f"{SITE_URL}/marca/{slug}/"
            note = brand.get('note') or ''
            desc = clamp(
                f"{brand['name']} en Argentina: {len(prods)} equipos disponibles. {note}. "
                f"Venta, instalación y servicio post-venta en todo el país por {ORG_NAME}."
            )
            brand_title = f"{brand['name']} Argentina"
            if slug in BRAND_SEO:
                brand_title, desc = BRAND_SEO[slug]
                desc = clamp(desc.format(n=len(prods)))
            crumbs = [("Inicio", ""), ("Marcas", "marcas/"), (brand['name'], None)]
            jsonld = [breadcrumb_jsonld([
                (n, SITE_URL + '/' + (h or '')) if h is not None else (n, url)
                for n, h in crumbs
            ])]
            if prods:
                jsonld.append(itemlist_jsonld(prods))
            grid = ''.join(product_card_html(p, brands_by_slug, root2, offers_by_sku) for p in prods)
            create_index_file(
                os.path.join(BASE_DIR, 'marca', slug), cat_template, 2,
                title=brand_title,
                og={'type': 'website', 'title': f"{brand['name']} en Argentina",
                    'description': desc, 'image': f"{SITE_URL}/assets/img/logo-trivium.svg",
                    'url': url},
                seo=make_seo_block(url, desc, jsonld),
                body={
                    'crumbs': breadcrumb_html(crumbs, root2),
                    'cat-title': esc(brand['name']),
                    'cat-tag': esc(note),
                    'cat-count': f"{len(prods)} productos",
                    'count': f"{len(prods)} productos",
                    'cat-list': sidebar_cats,
                    'brand-list': sidebar_brands,
                    'grid': grid,
                    'cat-posts': (
                        f'<div class="container"><h2>Antes de comprar</h2>'
                        f'<p><a href="{root2}guias/equipos-de-taller-economicos/">'
                        f'Equipos de taller económicos: cuándo conviene la línea Trivium Pro →</a></p></div>'
                        if slug == 'trivium-pro' else ''),
                },
            )

    # 4. Products
    prod_template = os.path.join(BASE_DIR, 'producto.html')
    if os.path.exists(prod_template):
        for prod in catalog['products']:
            slug = prod['slug']
            url = f"{SITE_URL}/producto/{slug}/"
            brand = brands_by_slug.get(prod.get('brand'), {})
            cat = cats_by_slug.get(prod.get('category'), {})

            if prod.get('summary'):
                raw_desc = prod['summary']
            elif prod.get('bullets'):
                raw_desc = ' · '.join(prod['bullets'][:3])
            else:
                raw_desc = strip_tags(prod.get('html_description', '')) or prod['name']
            desc = product_meta_description(prod)

            og = {
                'type': 'product',
                'title': prod['name'],
                'description': desc,
                'image': f"{SITE_URL}/{prod['image']}" if prod.get('image') else '',
                'url': url,
            }

            # --- migas ---
            crumbs = [("Inicio", ""), ("Catálogo", "catalogo/")]
            if cat:
                if cat.get('parent') and cat['parent'] in cats_by_slug:
                    par = cats_by_slug[cat['parent']]
                    crumbs.append((par['name'], f"categoria/{par['slug']}/"))
                crumbs.append((cat['name'], f"categoria/{cat['slug']}/"))
            crumbs.append((prod['name'], None))

            # --- structured data ---
            product_ld = {
                "@context": "https://schema.org",
                "@type": "Product",
                "name": prod['name'],
                "description": strip_tags(raw_desc),
                "url": url,
                "sku": prod.get('sku', ''),
                "category": cat.get('name', ''),
            }
            if prod.get('image'):
                product_ld["image"] = [f"{SITE_URL}/{i}" for i in
                                       (prod.get('images') or [prod['image']])]
            if brand:
                product_ld["brand"] = {"@type": "Brand", "name": brand['name']}
            props = []
            if prod.get('capacity'):
                props.append({"@type": "PropertyValue", "name": "Capacidad",
                              "value": prod['capacity']})
            if prod.get('lift_height'):
                props.append({"@type": "PropertyValue", "name": "Altura de elevación",
                              "value": prod['lift_height']})
            if props:
                product_ld["additionalProperty"] = props
            offer = offers_by_sku.get(prod.get('sku'))
            if offer:
                if offer.get('modelo'):
                    product_ld["mpn"] = offer['modelo']
                product_ld["offers"] = {
                    "@type": "Offer",
                    "url": url,
                    "priceCurrency": "ARS",
                    "price": offer['price'],
                    "priceValidUntil": offer['valid'],
                    "availability": "https://schema.org/InStock",
                    "itemCondition": "https://schema.org/NewCondition",
                    "priceSpecification": {
                        "@type": "UnitPriceSpecification",
                        "price": offer['price'],
                        "priceCurrency": "ARS",
                        "valueAddedTaxIncluded": True,
                    },
                    "seller": {"@type": "Organization", "name": ORG_NAME},
                }
            jsonld = [product_ld, breadcrumb_jsonld([
                (n, SITE_URL + '/' + (h or '')) if h is not None else (n, url)
                for n, h in crumbs
            ])]

            # --- cuerpo prerenderizado ---
            gallery = ''
            if prod.get('image'):
                gallery = (f'<div class="pd-media"><img src="{esc(root2 + prod["image"])}" '
                           f'alt="{esc(prod["name"])}" width="800" height="600"></div>')
            bullets = ''
            if prod.get('bullets'):
                lis = ''.join(f'<li>{esc(b)}</li>' for b in prod['bullets'])
                bullets = f'<ul class="pd-bullets">{lis}</ul>'
            specs = ''
            spec_rows = [(k, prod.get(v)) for k, v in
                         (("Capacidad", 'capacity'), ("Altura de elevación", 'lift_height'),
                          ("SKU", 'sku'))]
            spec_rows = [(k, v) for k, v in spec_rows if v]
            if spec_rows:
                specs = ('<dl class="pd-specs">' +
                         ''.join(f'<dt>{esc(k)}</dt><dd>{esc(v)}</dd>' for k, v in spec_rows) +
                         '</dl>')
            brand_line = ''
            if brand:
                brand_line = (f'<p class="pd-brand"><a href="{root2}marca/{esc(brand["slug"])}/">'
                              f'{esc(brand["name"])}</a></p>')

            # html_description viene de WooCommerce con rutas relativas
            # ("assets/pdf/..."), que desde /producto/<slug>/ apuntan dos niveles
            # más abajo y dan 404. producto.html las reescribe al hidratar, pero
            # el HTML servido también tiene que salir correcto.
            rich = prod.get("html_description", "")
            rich = rich.replace('href="assets/', f'href="{root2}assets/')
            rich = rich.replace('src="assets/', f'src="{root2}assets/')
            pd_html = (
                f'<article class="pd-static">'
                f'{gallery}'
                f'<div class="pd-info">'
                f'<h1>{esc(prod["name"])}</h1>'
                f'{brand_line}'
                f'<p class="pd-summary">{esc(strip_tags(raw_desc))}</p>'
                f'{price_tag_html(prod.get("sku"), offers_by_sku, True)}'
                f'{specs}{bullets}'
                f'{rich}'
                f'</div></article>'
            )

            related = [p for p in catalog['products']
                       if p.get('category') == prod.get('category') and p['slug'] != slug][:8]
            related_html = ''.join(product_card_html(p, brands_by_slug, root2, offers_by_sku) for p in related)

            create_index_file(
                os.path.join(BASE_DIR, 'producto', slug), prod_template, 2,
                title=prod['name'], og=og,
                seo=make_seo_block(url, desc, jsonld),
                body={
                    'crumbs': breadcrumb_html(crumbs, root2),
                    'pd-wrap': pd_html,
                    'related': related_html,
                    'pd-guide': product_guide_html(prod.get('category'), root2),
                },
            )

    update_static_pages(catalog)

    print(f"Done! Generated folders for {len(catalog['products'])} products and {len(catalog['categories'])} categories.")

if __name__ == "__main__":
    main()
