import json
import os
from pathlib import Path

BLOG_JSON = Path("data/blog.json")
TEMPLATE = Path("articulo.html")

def main():
    if not BLOG_JSON.exists():
        print("✘ No se encontró data/blog.json")
        return
    
    with open(BLOG_JSON, "r", encoding="utf-8") as f:
        posts = json.load(f)
    
    template_content = TEMPLATE.read_text(encoding="utf-8")
    
    # Asegurarnos de que el template use rutas relativas correctas
    # Cambiamos assets/ por ../assets/ porque ahora el archivo estará un nivel más abajo
    template_content = template_content.replace('href="assets/', 'href="../assets/')
    template_content = template_content.replace('src="assets/', 'src="../assets/')
    # Meta tag para que el JS sepa que está en un subnivel
    template_content = template_content.replace('<meta name="tv-root" content="">', '<meta name="tv-root" content="../">')

    print(f"▶ Generando {len(posts)} carpetas de artículos...")
    
    for p in posts:
        slug = p["slug"]
        post_dir = Path(slug)
        post_dir.mkdir(exist_ok=True)
        
        index_file = post_dir / "index.html"
        index_file.write_text(template_content, encoding="utf-8")
        
    print("✔ Estructura de carpetas completada.")

if __name__ == "__main__":
    main()
