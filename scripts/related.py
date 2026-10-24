"""Enlaces internos automáticos entre notas del blog, fichas de producto y guías.

Devuelve, para cada nota, los equipos y las otras notas más afines, y para cada
ficha, las notas que nombran ese modelo. Todo sale de data/blog.json y
data/catalog.json, así que al agregar una nota o un equipo los enlaces se
recalculan solos con el resto de las páginas.

Criterios:
  - Mención explícita: el modelo del equipo (SPOA10, PL-45H, Geoliner 320...)
    aparece en el texto de la nota. Es la señal más fuerte.
  - Afinidad de texto (TF-IDF + coseno) entre la nota y el nombre, resumen y
    bullets del equipo, o entre dos notas.
  - Reparto: a igualdad de afinidad se prefieren las fichas con menos enlaces
    entrantes, para que no se concentren en las mismas cinco máquinas.
  - Se descartan los destinos que la nota ya enlaza en su cuerpo.

Resultado determinista (sin red ni azar): si no cambian los datos, no cambia el HTML.
"""

import html
import json
import math
import os
import re
from collections import Counter

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

STOP = set("""
para como pero porque cuando donde mismo cada todo toda todos todas esta este estos estas
esto esos esas entre sobre desde hasta tambien tiene tienen tener hace hacer puede pueden
poder segun sino solo otro otra otros otras muy mas menos cual cuales quien quienes
son fue ser son estan estar hay uno una unos unas del los las que con por sin
trivium taller talleres equipo equipos pro
""".split())

# Familias de modelo: la palabra sola no identifica el equipo, hace falta el número.
MODEL_WORDS = ('geoliner', 'geodyna', 'monty', 'unite', 'easymont')

_HTML_TAG = re.compile(r'<[^>]+>')


def plain(text):
    return html.unescape(_HTML_TAG.sub(' ', text or ''))


def tokens(text):
    out = []
    for w in re.findall(r'[a-záéíóúñü0-9]+', plain(text).lower()):
        if len(w) < 4 or w in STOP:
            continue
        # Plural simple: "elevadores" y "elevador" cuentan como lo mismo.
        if w.endswith('es') and len(w) > 5:
            w = w[:-2]
        elif w.endswith('s') and len(w) > 4:
            w = w[:-1]
        out.append(w)
    return out


def model_aliases(prod):
    """Identificadores del modelo que alguien escribiría en una nota.

    Devuelve regex ya compilados. 'SPOA10' no debe coincidir con 'SPOA10TRIO',
    por eso se pide que no haya letra o dígito pegado antes ni después.
    """
    name = prod['name']
    raw = set()
    # Código con letras y números: SPOA10, PL-45H, KI-1478, U-850, G66, DL9...
    for m in re.finditer(r'(?<![\wÀ-ÿ])([A-Za-z]{1,6}[-\s]?\d[A-Za-z0-9.\-]*)', name):
        tok = m.group(1).strip('-. ')
        # Medidas ("4535 kg", "40/20/10 Ton") no son modelos.
        if re.fullmatch(r'(kg|ton|mm|m|w|hp|v|l)', re.sub(r'[\d.\-\s]', '', tok), re.I):
            continue
        if re.search(r'[A-Za-z]', tok) and re.search(r'\d', tok) and len(tok) >= 3:
            raw.add(tok)
    # Familia + número: "Geoliner 320", "Monty 3300-20", "Geodyna 7100".
    for word in MODEL_WORDS:
        for m in re.finditer(rf'\b{word}\s+([A-Za-z]?\d[\w\-]*)', name, re.I):
            raw.add(f'{word} {m.group(1)}')
    pats = []
    for r in raw:
        runs = re.findall(r'[A-Za-z]+|\d+', r)
        body = r'[\s\-.]*'.join(re.escape(x) for x in runs)
        pats.append(re.compile(rf'(?<![\wÀ-ÿ]){body}(?![a-z0-9])', re.I))
    return pats


def _vector(counts, idf):
    v = {t: (1 + math.log(c)) * idf.get(t, 0) for t, c in counts.items()}
    n = math.sqrt(sum(x * x for x in v.values())) or 1
    return {t: x / n for t, x in v.items()}


def _cos(a, b):
    if len(a) > len(b):
        a, b = b, a
    return sum(x * b.get(t, 0) for t, x in a.items())


def _linked(post, kind):
    """Slugs de /blog/, /producto/ o /guias/ que la nota ya enlaza en su cuerpo."""
    return set(re.findall(rf'/{kind}/([a-z0-9\-]+)/?', post.get('content') or ''))


def build():
    """Calcula los tres mapas. Devuelve un dict con:
         post_products[slug] -> [slug de producto]
         post_posts[slug]    -> [slug de nota]
         product_posts[slug] -> [slug de nota que nombra el modelo]
    """
    with open(os.path.join(BASE_DIR, 'data', 'blog.json'), encoding='utf-8') as f:
        posts = sorted(json.load(f), key=lambda p: p['slug'])
    with open(os.path.join(BASE_DIR, 'data', 'catalog.json'), encoding='utf-8') as f:
        products = sorted(json.load(f)['products'], key=lambda p: p['slug'])

    post_text = {p['slug']: plain(p['title']) + ' ' + plain(p['title']) + ' ' + plain(p.get('content')) for p in posts}
    prod_text = {p['slug']: ' '.join([p['name'], p['name'], p.get('summary') or '',
                                      ' '.join(p.get('bullets') or [])]) for p in products}

    # --- idf sobre todo el corpus (notas + fichas) ---
    docs = {('p', s): Counter(tokens(t)) for s, t in post_text.items()}
    docs.update({('f', s): Counter(tokens(t)) for s, t in prod_text.items()})
    df = Counter(t for c in docs.values() for t in c)
    n = len(docs)
    idf = {t: math.log(n / d) for t, d in df.items() if d < n * 0.5}
    vec = {k: _vector(c, idf) for k, c in docs.items()}

    # --- menciones explícitas de modelo ---
    aliases = {p['slug']: model_aliases(p) for p in products}
    mentions = {}  # (nota, producto) -> cantidad
    for ps, text in post_text.items():
        for fs, pats in aliases.items():
            c = sum(len(pt.findall(text)) for pt in pats)
            if c:
                mentions[(ps, fs)] = c

    product_posts = {}
    for (ps, fs), c in mentions.items():
        product_posts.setdefault(fs, []).append((c, ps))
    product_posts = {fs: [ps for _, ps in sorted(v, key=lambda x: (-x[0], x[1]))]
                     for fs, v in product_posts.items()}

    # --- notas -> equipos (con reparto de enlaces entrantes) ---
    inbound = Counter()
    for p in posts:
        for fs in _linked(p, 'producto'):
            inbound[fs] += 1

    with open(os.path.join(BASE_DIR, 'data', 'catalog.json'), encoding='utf-8') as f:
        cats = {c['slug']: c for c in json.load(f)['categories']}
    root_of = {f['slug']: (cats.get(f.get('category'), {}).get('parent') or f.get('category'))
               for f in products}

    post_products = {}
    for p in posts:
        ps = p['slug']
        ya = _linked(p, 'producto')
        sims = {f['slug']: _cos(vec[('p', ps)], vec[('f', f['slug'])]) for f in products}
        # Familia de la nota (elevadores, balanceadoras...): la que más pesa entre los
        # equipos que nombra o enlaza y, si no nombra ninguno, entre los 5 más afines.
        # El relleno por afinidad se limita a esa familia para no sugerir un elevador
        # en una nota de alineadoras.
        ancla = [fs for (q, fs) in mentions if q == ps] + [fs for fs in ya if fs in root_of]
        if ancla:
            familia = Counter(root_of[fs] for fs in ancla).most_common(1)[0][0]
        else:
            # Sin equipos nombrados: el título dice de qué trata ("balanceadora...").
            tt = set(tokens(p['title']))
            peso = Counter()
            for f in products:
                peso[root_of[f['slug']]] += len(tt & set(tokens(f['name'])))
            familia = peso.most_common(1)[0][0] if any(peso.values()) else None
        cands = []
        for f in products:
            fs = f['slug']
            if fs in ya:
                continue
            sim = sims[fs]
            m = mentions.get((ps, fs), 0)
            if m == 0 and (familia is None or sim < 0.08 or root_of[fs] != familia):
                continue
            # Mención explícita pasa siempre por delante; el resto, por afinidad
            # penalizada por cuántos enlaces entrantes tiene ya la ficha.
            score = (1 if m else 0, sim / (1 + 0.5 * inbound[fs]), fs)
            cands.append(score)
        cands.sort(key=lambda x: (-x[0], -x[1], x[2]))
        chosen = [c[2] for c in cands[:4]]  # menciones primero, luego relleno de la familia
        post_products[ps] = chosen
        for fs in chosen:
            inbound[fs] += 1

    # --- notas -> notas ---
    post_posts = {}
    for p in posts:
        ps = p['slug']
        ya = _linked(p, 'blog') | {ps}
        sims = sorted(
            ((_cos(vec[('p', ps)], vec[('p', o['slug'])]), o['slug'])
             for o in posts if o['slug'] not in ya),
            key=lambda x: (-x[0], x[1]))
        post_posts[ps] = [s for sim, s in sims[:3] if sim >= 0.12]

    return {'post_products': post_products, 'post_posts': post_posts,
            'product_posts': product_posts}


if __name__ == '__main__':
    r = build()
    pp = r['post_products']
    print('notas con equipos relacionados:', sum(1 for v in pp.values() if v), 'de', len(pp))
    print('notas con notas relacionadas:  ', sum(1 for v in r['post_posts'].values() if v), 'de', len(r['post_posts']))
    print('fichas con notas que nombran el modelo:', len(r['product_posts']))
    ins = Counter(f for v in pp.values() for f in v)
    print('fichas que reciben enlace desde alguna nota (nuevo):', len(ins))
    for s in list(pp)[:6]:
        print('\n', s)
        print('  equipos:', pp[s])
        print('  notas:  ', r['post_posts'][s])
