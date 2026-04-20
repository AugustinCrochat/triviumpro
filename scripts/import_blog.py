import json
import os
import re
import urllib.request
from pathlib import Path

# Configuración
API_URL = "https://trivium.ar/wp-json/wp/v2/posts?_embed&per_page=100"
BLOG_JSON = Path("data/blog.json")
BLOG_JS = Path("data/blog.js")
IMG_DIR = Path("assets/img/blog")
IMG_DIR.mkdir(parents=True, exist_ok=True)

def download_img(url, filename):
    dest = IMG_DIR / filename
    if dest.exists(): return f"assets/img/blog/{filename}"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=20) as r:
            dest.write_bytes(r.read())
        return f"assets/img/blog/{filename}"
    except:
        return None

def main():
    print("▶ Recuperando artículos desde la API...")
    try:
        req = urllib.request.Request(API_URL, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as r:
            posts_raw = json.loads(r.read().decode())
    except Exception as e:
        print(f"✘ Error al conectar con la API: {e}")
        return

    blog_data = []
    for p in posts_raw:
        # Extraer imagen destacada
        img_url = p.get("_embedded", {}).get("wp:featuredmedia", [{}])[0].get("source_url")
        local_img = None
        if img_url:
            ext = img_url.split(".")[-1].split("?")[0]
            filename = f"{p['slug']}.{ext}"
            local_img = download_img(img_url, filename)
            print(f"  ✔ Imagen: {filename}")

        blog_data.append({
            "id": p["id"],
            "slug": p["slug"],
            "date": p["date"],
            "title": p["title"]["rendered"],
            "excerpt": p["excerpt"]["rendered"],
            "content": p["content"]["rendered"],
            "image": local_img
        })

    # Guardar JSON
    BLOG_JSON.write_text(json.dumps(blog_data, indent=2, ensure_ascii=False), encoding="utf-8")
    
    # Guardar JS
    BLOG_JS.write_text(f"window.BLOG_DATA = {json.dumps(blog_data, ensure_ascii=False)};", encoding="utf-8")
    
    print(f"\n✔ ¡Listo! {len(blog_data)} artículos importados.")

if __name__ == "__main__":
    main()
