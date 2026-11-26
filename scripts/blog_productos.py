"""Enlaces de cada nota a sus productos: tarjeta al principio, franja en el medio, barra lateral,
bloque final y enlace en la primera mención de cada modelo.

La selección está en data/blog-productos.json (elegida a mano, el primero es el destacado).
Una nota que no figure ahí usa el emparejado automático de related.py: conviene agregarla.
Los precios no se escriben en el HTML: blog.js los completa con la misma regla del catálogo.
"""
import html
import json
import os
import re
from urllib.parse import quote

import related

BASE_DIR = related.BASE_DIR
_DATOS = None


def _datos():
    global _DATOS
    if _DATOS is None:
        with open(f'{BASE_DIR}/data/catalog.json', encoding='utf-8') as f:
            cat = json.load(f)
        with open(f'{BASE_DIR}/data/blog-productos.json', encoding='utf-8') as f:
            sel = json.load(f)
        prods = {p['slug']: p for p in cat['products']}
        faltan = sorted({s for v in sel.values() for s in v if s not in prods})
        if faltan:
            print('⚠ blog-productos.json nombra productos que no están en el catálogo:', ', '.join(faltan))
        # un modelo que corresponde a más de un producto no se enlaza solo
        alias = {}
        for p in cat['products']:
            for rx in related.model_aliases(p):
                alias.setdefault(rx.pattern, (rx, set()))[1].add(p['slug'])
        _DATOS = (prods, {b['slug']: b for b in cat['brands']}, {c['slug']: c for c in cat['categories']}, sel,
                  [(rx, next(iter(s))) for rx, s in alias.values() if len(s) == 1], related.build())
    return _DATOS


def elegidos(slug):
    prods, _, _, sel, _, auto = _datos()
    lista = sel.get(slug)
    if lista is None:
        lista = auto['post_products'].get(slug, [])
    return [prods[s] for s in lista if s in prods]


def _e(t):
    return html.escape(html.unescape(str(t or '')), quote=True)


def _foto(p, root):
    img = p.get('image') or ''
    mini = re.sub(r'^(assets/img/productos/)([^/]+)$', r'\1t/\2', img)
    if mini != img and os.path.exists(f'{BASE_DIR}/{mini}'):
        img = mini
    return f'<img src="{_e(root + img)}" alt="{_e(p["name"])}" width="480" height="480" loading="lazy" decoding="async">' if img else ''


def _url(p, root):
    return f'{root}producto/{p["slug"]}/'


def _datos_clave(p):
    """Capacidad y altura en los elevadores; en el resto, los dos primeros puntos de la ficha."""
    if 'elevador' in (p.get('category') or ''):
        d = [f'{t}: {p[k]}' for t, k in (('Capacidad', 'capacity'), ('Altura', 'lift_height')) if p.get(k) and p[k] != '—']
        if d:
            return d
    cortos = [b for b in (p.get('bullets') or []) if len(b) <= 90][:2]
    if cortos:
        return cortos
    resumen = re.sub(r'<[^>]+>', '', p.get('summary') or '').strip()
    return [resumen if len(resumen) <= 150 else resumen[:150].rsplit(' ', 1)[0].rstrip(',.;:') + '…'] if resumen else []


def _marca(p):
    return _datos()[1].get(p.get('brand'), {}).get('name', '')


def _categoria(p, root):
    c = _datos()[2].get(p.get('category'))
    if not c:
        return f'<a class="np-mas" href="{root}catalogo/">Ver todo el catálogo →</a>'
    nombre = html.unescape(c['name'])
    c_padre = _datos()[2].get(c.get('parent'))
    if c_padre:
        nombre, slug = html.unescape(c_padre['name']), c_padre['slug']
    else:
        slug = c['slug']
    return f'<a class="np-mas" href="{root}categoria/{slug}/">Ver todo en {_e(nombre.lower())} →</a>'


def destacado(p, root):
    puntos = ''.join(f'<li>{_e(x)}</li>' for x in _datos_clave(p))
    return (f'<aside class="np-destacado" aria-label="Equipo relacionado con esta nota">'
            f'<a class="np-destacado__foto" href="{_url(p, root)}" tabindex="-1" aria-hidden="true">{_foto(p, root)}</a>'
            f'<div class="np-destacado__txt"><span class="np-rotulo">Equipo relacionado · {_e(_marca(p))}</span>'
            f'<a class="np-nombre" href="{_url(p, root)}">{_e(p["name"])}</a><ul>{puntos}</ul>'
            f'<span class="np-precio" data-precio="{_e(p.get("sku"))}"></span>'
            f'<a class="np-boton" href="{_url(p, root)}">Ver ficha y especificaciones →</a></div></aside>')


def _mini(p, root):
    return (f'<a class="np-mini" href="{_url(p, root)}"><span class="np-mini__foto">{_foto(p, root)}</span>'
            f'<span class="np-mini__txt"><span class="np-rotulo">{_e(_marca(p))}</span><b>{_e(p["name"])}</b>'
            f'<span class="np-precio" data-precio="{_e(p.get("sku"))}"></span><span class="np-ver">Ver ficha →</span></span></a>')


def franja(lista, root, principal):
    return (f'<aside class="np-franja"><strong>Más equipos para ver</strong><div class="np-minis">'
            f'{"".join(_mini(p, root) for p in lista)}</div>{_categoria(principal, root)}</aside>')


def final(lista, root, titulo, whatsapp):
    if not lista:
        return ''
    tarjetas = []
    for p in lista:
        msg = quote(f'Hola, leí la nota «{titulo}» y quiero cotizar: {html.unescape(p["name"])}')
        tarjetas.append(f'<li>{_mini(p, root)}<a class="np-wa" href="https://wa.me/{whatsapp}?text={msg}" rel="noopener">Cotizar por WhatsApp</a></li>')
    return (f'<section class="np-final" id="equipos-de-la-nota"><h2>Equipos relacionados con esta nota</h2>'
            f'<ul>{"".join(tarjetas)}</ul>{_categoria(lista[0], root)}</section>')


def lateral(p, root):
    return (f'<a class="np-lateral" href="{_url(p, root)}"><span class="np-lateral__foto">{_foto(p, root)}</span>'
            f'<span class="np-rotulo">Equipo relacionado</span><b>{_e(p["name"])}</b><span class="np-ver">Ver ficha →</span></a>')


# --- enlace en la primera mención de cada modelo ---
_NO_TOCAR = ('a', 'h1', 'h2', 'h3', 'h4', 'figure', 'figcaption', 'summary', 'script', 'style', 'button', 'aside', 'svg')


def enlazar_modelos(cuerpo, root, maximo=6):
    alias = _datos()[4]
    hechos = set(re.findall(r'producto/([a-z0-9.\-]+)/', cuerpo))
    trozos = re.split(r'(<[^>]+>)', cuerpo)
    pila, nuevos = [], 0
    for i, t in enumerate(trozos):
        if t.startswith('<'):
            m = re.match(r'<\s*(/?)\s*([a-zA-Z0-9]+)', t)
            if m and m.group(2).lower() in _NO_TOCAR and not t.endswith('/>'):
                if m.group(1):
                    if m.group(2).lower() in pila:
                        pila.remove(m.group(2).lower())
                else:
                    pila.append(m.group(2).lower())
            continue
        if pila or not t.strip() or nuevos >= maximo:
            continue
        hallazgos = []
        for rx, slug in alias:
            if slug not in hechos:
                m = rx.search(t)
                if m:
                    hallazgos.append((m.start(), -len(m.group(0)), m.end(), slug))
        corte, partes = 0, []
        for ini, _, fin, slug in sorted(hallazgos):
            if ini < corte or slug in hechos or nuevos >= maximo:
                continue
            partes += [t[corte:ini], f'<a class="np-enlace" href="{root}producto/{slug}/">{t[ini:fin]}</a>']
            corte = fin
            hechos.add(slug)
            nuevos += 1
        if partes:
            trozos[i] = ''.join(partes) + t[corte:]
    return ''.join(trozos)


def insertar(cuerpo, lista, root):
    """Tarjeta destacada después del resumen (o del primer párrafo) y franja a mitad de la nota."""
    cuerpo = enlazar_modelos(cuerpo, root)
    if not lista:
        return cuerpo
    m = re.search(r'<p class="nota-resumen">.*?</p>', cuerpo, re.S) or re.search(r'<p[\s>].*?</p>', cuerpo, re.S)
    pos = m.end() if m else 0
    cuerpo = cuerpo[:pos] + destacado(lista[0], root) + cuerpo[pos:]
    otros = lista[1:4]
    titulos = [x.start() for x in re.finditer(r'<h2[\s>]', cuerpo)]
    if len(otros) >= 2 and len(titulos) >= 4:
        medio = titulos[len(titulos) // 2]
        cuerpo = cuerpo[:medio] + franja(otros, root, lista[0]) + cuerpo[medio:]
    return cuerpo
