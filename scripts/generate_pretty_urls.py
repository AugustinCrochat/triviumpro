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

    Sólo entra lo que ya es público en data/prices-publico.json y visible en la
    ficha (tienda != false): el schema nunca puede mostrar un precio que la
    página no muestra. El dólar se pide en vivo con fallback fijo, igual que
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
        if rec.get('tienda') is False:
            continue
        base = rec['fixed_ars'] if rec.get('fixed_ars') is not None else rec['usd'] * rate
        iva = rec.get('iva', prices['meta']['default_iva'])
        out[sku] = {
            'price': round(base * (1 + iva / 100), 2),
            'modelo': rec.get('modelo'),
            'valid': valid,
        }
    return out, rate


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


def product_card_html(prod, brands_by_slug, root):
    """Réplica estática de productCard() de site.js, para que el HTML traiga los links."""
    brand = brands_by_slug.get(prod.get('brand'), {})
    brand_name = brand.get('name', '')
    img = ''
    if prod.get('image'):
        img = (f'<img src="{esc(root + prod["image"])}" alt="{esc(prod["name"])}" '
               f'loading="lazy" width="400" height="300">')
    specs = ''
    if prod.get('capacity') or prod.get('lift_height'):
        specs = ('<div class="spec">'
                 f'<span>Capacidad <b>{esc(prod.get("capacity", "—"))}</b></span>'
                 f'<span>Altura <b>{esc(prod.get("lift_height", "—"))}</b></span>'
                 '</div>')
    return (
        f'<a class="prod-card" href="{esc(root)}producto/{esc(prod["slug"])}/">'
        f'<div class="thumb">{img}</div>'
        f'<div class="body">'
        f'<span class="brand-tag">{esc(brand_name)}</span>'
        f'<h3>{esc(prod["name"])}</h3>'
        f'{specs}'
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
        'tienda': ("Tienda",
             f"Comprá online equipamiento para taller con Mercado Pago: elevadores, "
             f"balanceadoras y desarmadoras Trivium Pro con precio final e IVA incluido. "
             f"Envío e instalación a coordinar en todo el país.",
             f"Tienda online — {ORG_NAME}"),
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
            jsonld = [{
                "@context": "https://schema.org",
                "@type": "Organization",
                "name": ORG_NAME,
                "url": f"{SITE_URL}/",
                "logo": f"{SITE_URL}/assets/img/logo-trivium.svg",
                "description": desc,
                "areaServed": {"@type": "Country", "name": "Argentina"},
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
            }]

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
            desc = clamp(
                f"{nombre} para taller: {len(prods)} equipos en stock y a pedido. "
                f"{tagline} Representantes oficiales Rotary Lift y Hofmann en Argentina. "
                f"Envíos a todo el país."
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
            grid = ''.join(product_card_html(p, brands_by_slug, root2) for p in prods)
            create_index_file(
                os.path.join(BASE_DIR, 'categoria', slug), cat_template, 2,
                title=nombre,
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
            crumbs = [("Inicio", ""), ("Marcas", "marcas/"), (brand['name'], None)]
            jsonld = [breadcrumb_jsonld([
                (n, SITE_URL + '/' + (h or '')) if h is not None else (n, url)
                for n, h in crumbs
            ])]
            if prods:
                jsonld.append(itemlist_jsonld(prods))
            grid = ''.join(product_card_html(p, brands_by_slug, root2) for p in prods)
            create_index_file(
                os.path.join(BASE_DIR, 'marca', slug), cat_template, 2,
                title=f"{brand['name']} Argentina",
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
            desc = clamp(raw_desc)

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
                product_ld["offers"] = {
                    "@type": "Offer",
                    "url": url,
                    "priceCurrency": "ARS",
                    "price": offer['price'],
                    "priceValidUntil": offer['valid'],
                    "availability": "https://schema.org/InStock",
                    "itemCondition": "https://schema.org/NewCondition",
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
                f'{specs}{bullets}'
                f'{rich}'
                f'</div></article>'
            )

            related = [p for p in catalog['products']
                       if p.get('category') == prod.get('category') and p['slug'] != slug][:8]
            related_html = ''.join(product_card_html(p, brands_by_slug, root2) for p in related)

            create_index_file(
                os.path.join(BASE_DIR, 'producto', slug), prod_template, 2,
                title=prod['name'], og=og,
                seo=make_seo_block(url, desc, jsonld),
                body={
                    'crumbs': breadcrumb_html(crumbs, root2),
                    'pd-wrap': pd_html,
                    'related': related_html,
                },
            )

    update_static_pages(catalog)

    print(f"Done! Generated folders for {len(catalog['products'])} products and {len(catalog['categories'])} categories.")

if __name__ == "__main__":
    main()
