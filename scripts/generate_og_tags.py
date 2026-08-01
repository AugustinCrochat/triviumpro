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
from site_config import SITE_URL, ORG_NAME


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


def inject_head(content, title, og_block, seo_block):
    # Limpia inyecciones previas para que el script sea idempotente
    content = re.sub(r'\n?<meta property="og:[^>]*>', '', content)
    content = re.sub(r'\n?<meta name="twitter:[^>]*>', '', content)
    content = re.sub(r'\n?<link rel="canonical"[^>]*>', '', content)
    content = re.sub(r'\n?<meta name="description"[^>]*>', '', content)
    content = re.sub(
        r'\n?<script type="application/ld\+json">.*?</script>', '', content, flags=re.S
    )

    content = re.sub(
        r'<title>[^<]*</title>',
        f'<title>{esc(title)} — {ORG_NAME}</title>',
        content,
        count=1,
    )
    return content.replace('</head>', og_block + '\n' + seo_block + '\n</head>', 1)


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
        description = clamp(strip_html(post.get('excerpt', ''))) or title
        image_path = post.get('image', '')
        image_url = f"{SITE_URL}/{image_path}" if image_path else ''
        published = post.get('date', '')

        article_ld = {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": title[:110],
            "description": strip_html(post.get('excerpt', '')),
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
            make_seo_block(url, description, [article_ld, crumbs_ld]),
        )
        content = replace_empty_el(content, 'crumbs', crumbs_html)
        content = replace_empty_el(content, 'post-title', esc(title))
        content = replace_empty_el(content, 'post-date', esc(pretty_date))
        content = replace_empty_el(content, 'post-content', body_html)
        content = replace_empty_el(content, 'more-posts', more_html)
        page_path.write_text(content, encoding='utf-8')
        count += 1

    print(f"✔ {count} artículos del blog con OG, canonical, description y JSON-LD")


if __name__ == "__main__":
    update_blog()
