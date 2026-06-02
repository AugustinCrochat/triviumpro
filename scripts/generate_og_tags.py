#!/usr/bin/env python3
"""Inject Open Graph and Twitter Card meta tags into product and blog article pages."""

import json
import re
import html
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
SITE_URL = "https://trivium.ar"


def strip_html(text):
    text = re.sub(r'<[^>]+>', '', text)
    return html.unescape(text).strip()


def make_og_block(title, description, image_url, url, og_type="website"):
    t = html.escape(title, quote=True)
    d = html.escape(description, quote=True)
    img = html.escape(image_url, quote=True)
    u = html.escape(url, quote=True)
    return (
        f'<meta property="og:type" content="{og_type}">\n'
        f'<meta property="og:site_name" content="Trivium Center">\n'
        f'<meta property="og:title" content="{t}">\n'
        f'<meta property="og:description" content="{d}">\n'
        f'<meta property="og:image" content="{img}">\n'
        f'<meta property="og:url" content="{u}">\n'
        f'<meta name="twitter:card" content="summary_large_image">\n'
        f'<meta name="twitter:title" content="{t}">\n'
        f'<meta name="twitter:description" content="{d}">\n'
        f'<meta name="twitter:image" content="{img}">'
    )


def inject_og(content, title, og_block):
    # Remove any previously injected OG/Twitter tags
    content = re.sub(r'\n?<meta property="og:[^>]*>', '', content)
    content = re.sub(r'\n?<meta name="twitter:[^>]*>', '', content)

    # Update static <title> tag so crawlers see the real title
    content = re.sub(
        r'<title>[^<]*</title>',
        f'<title>{html.escape(title)} — Trivium Center</title>',
        content,
        count=1,
    )

    # Inject OG block just before </head>
    return content.replace('</head>', og_block + '\n</head>', 1)


def update_products():
    catalog_path = BASE_DIR / 'data' / 'catalog.json'
    with open(catalog_path, encoding='utf-8') as f:
        catalog = json.load(f)

    count = 0
    for prod in catalog['products']:
        slug = prod['slug']
        page_path = BASE_DIR / 'producto' / slug / 'index.html'
        if not page_path.exists():
            continue

        title = prod['name']

        if prod.get('summary'):
            description = prod['summary']
        elif prod.get('bullets'):
            description = ' · '.join(prod['bullets'][:3])
        else:
            description = title
        description = description[:160]

        image_path = prod.get('image', '')
        image_url = f"{SITE_URL}/{image_path}" if image_path else ''

        url = f"{SITE_URL}/producto/{slug}/"
        og_block = make_og_block(title, description, image_url, url, 'product')

        content = page_path.read_text(encoding='utf-8')
        page_path.write_text(inject_og(content, title, og_block), encoding='utf-8')
        count += 1

    print(f"✔ {count} páginas de productos actualizadas con OG tags")


def update_blog():
    blog_path = BASE_DIR / 'data' / 'blog.json'
    with open(blog_path, encoding='utf-8') as f:
        posts = json.load(f)

    count = 0
    for post in posts:
        slug = post['slug']
        page_path = BASE_DIR / 'blog' / slug / 'index.html'
        if not page_path.exists():
            continue

        title = post['title']

        excerpt = post.get('excerpt', '')
        description = strip_html(excerpt)[:160]
        if not description:
            description = title

        image_path = post.get('image', '')
        image_url = f"{SITE_URL}/{image_path}" if image_path else ''

        url = f"{SITE_URL}/blog/{slug}/"
        og_block = make_og_block(title, description, image_url, url, 'article')

        content = page_path.read_text(encoding='utf-8')
        page_path.write_text(inject_og(content, title, og_block), encoding='utf-8')
        count += 1

    print(f"✔ {count} artículos del blog actualizados con OG tags")


if __name__ == "__main__":
    update_products()
    update_blog()
