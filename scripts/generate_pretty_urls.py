import os
import json
import shutil

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, 'data', 'catalog.json')

def create_index_file(target_dir, template_path, root_depth, title=None, description=None):
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
    
    # Update title and description if provided
    if title:
        content = content.replace('<title>Trivium Center</title>', f'<title>{title} — Trivium Center</title>')
    
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
            # print(f"  -> producto/{slug}/") # too many to print
            create_index_file(os.path.join(BASE_DIR, 'producto', slug), prod_template, 2)

    print(f"Done! Generated folders for {len(catalog['products'])} products and {len(catalog['categories'])} categories.")

if __name__ == "__main__":
    main()
