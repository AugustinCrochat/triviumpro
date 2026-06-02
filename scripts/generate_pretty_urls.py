import os
import json
import re
import html as html_lib
import shutil

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, 'data', 'catalog.json')
SITE_URL = "https://trivium.ar"


def make_og_block(title, description, image_url, url, og_type="website"):
    t = html_lib.escape(title, quote=True)
    d = html_lib.escape(description, quote=True)
    img = html_lib.escape(image_url, quote=True)
    u = html_lib.escape(url, quote=True)
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


def create_index_file(target_dir, template_path, root_depth, title=None, description=None, og=None):
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
        content = re.sub(r'<title>[^<]*</title>', f'<title>{html_lib.escape(title)} — Trivium Center</title>', content, count=1)

    # Inject OG tags
    if og:
        og_block = make_og_block(og['title'], og.get('description', ''), og.get('image', ''), og['url'], og.get('type', 'website'))
        content = content.replace('</head>', og_block + '\n</head>', 1)

    target_path = os.path.join(target_dir, 'index.html')
    with open(target_path, 'w', encoding='utf-8') as f:
        f.write(content)

def main():
    print("Generating pretty URLs...")
    
    with open(DATA_PATH, 'r', encoding='utf-8') as f:
        catalog = json.load(f)

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

    # 2. Categories
    cat_template = os.path.join(BASE_DIR, 'categoria.html')
    if os.path.exists(cat_template):
        for cat in catalog['categories']:
            slug = cat['slug']
            print(f"  -> categoria/{slug}/")
            create_index_file(os.path.join(BASE_DIR, 'categoria', slug), cat_template, 2)

    # 3. Brands (using marca/ prefix as per old site)
    if os.path.exists(cat_template):
        for brand in catalog['brands']:
            slug = brand['slug']
            print(f"  -> marca/{slug}/")
            create_index_file(os.path.join(BASE_DIR, 'marca', slug), cat_template, 2)

    # 4. Products
    prod_template = os.path.join(BASE_DIR, 'producto.html')
    if os.path.exists(prod_template):
        for prod in catalog['products']:
            slug = prod['slug']
            if prod.get('summary'):
                desc = prod['summary']
            elif prod.get('bullets'):
                desc = ' · '.join(prod['bullets'][:3])
            else:
                desc = prod['name']
            og = {
                'type': 'product',
                'title': prod['name'],
                'description': desc[:160],
                'image': f"{SITE_URL}/{prod['image']}" if prod.get('image') else '',
                'url': f"{SITE_URL}/producto/{slug}/",
            }
            create_index_file(os.path.join(BASE_DIR, 'producto', slug), prod_template, 2, title=prod['name'], og=og)

    print(f"Done! Generated folders for {len(catalog['products'])} products and {len(catalog['categories'])} categories.")

if __name__ == "__main__":
    main()
