#!/usr/bin/env python3
"""Fotos secundarias de detalle (zoom + pie de foto) para la galería de las máquinas.

Parte de data/zoom_photos.json: por producto, una lista de {"box": [x0, y0, x1, y1], "caption": "..."}
con el recorte (en píxeles de la foto principal) que muestra mejor un componente. El recorte se
amplía con LANCZOS (como la foto de las cámaras de la Geoliner 880 de la ficha) y se afina un poco.

Escribe assets/img/productos/<slug>-detalle-<n>.webp y las agrega al producto en data/catalog.json
(images + image_captions) y a data/catalog.js. Es idempotente: reemplaza los detalles anteriores.

Uso: python3 scripts/generate_zoom_photos.py [slug ...]
"""
import json, os, re, sys
from PIL import Image, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SALIDA = 900          # lado mayor de la foto de detalle
ESCALA_MAX = 3.6      # no se amplía más que esto: más allá se ve borroso

def recortar(src, box, dst):
    im = Image.open(src).convert("RGB")
    W, H = im.size
    x0, y0, x1, y1 = [max(0, min(v, lim)) for v, lim in zip(box, (W, H, W, H))]
    c = im.crop((x0, y0, x1, y1))
    k = min(SALIDA / max(c.size), ESCALA_MAX)
    c = c.resize((max(1, round(c.width * k)), max(1, round(c.height * k))), Image.LANCZOS)
    c = c.filter(ImageFilter.UnsharpMask(radius=1.4, percent=70, threshold=2))
    c.save(dst, "WEBP", quality=88)
    return c.size, k

def main():
    solo = set(sys.argv[1:])
    zoom = json.load(open(os.path.join(ROOT, "data/zoom_photos.json"), encoding="utf-8"))
    cat = json.load(open(os.path.join(ROOT, "data/catalog.json"), encoding="utf-8"))
    por_slug = {p["slug"]: p for p in cat["products"]}
    for slug, items in zoom.items():
        if solo and slug not in solo: continue
        p = por_slug[slug]
        base = [i for i in (p.get("images") or [p["image"]]) if not re.search(r"-detalle-\d+\.webp$", i)]
        # los detalles se recortan siempre de la foto principal (la primera)
        origen = os.path.join(ROOT, p["image"])
        nuevas, caps = [], dict(p.get("image_captions") or {})
        for k in [k for k in caps if re.search(r"-detalle-\d+\.webp$", k)]: caps.pop(k)
        for n, it in enumerate(items, 1):
            rel = f"assets/img/productos/{slug}-detalle-{n}.webp"
            (w, h), esc = recortar(origen, it["box"], os.path.join(ROOT, rel))
            nuevas.append(rel); caps[rel] = it["caption"]
            print(f"  {slug[:48]} #{n}: {w}x{h} (x{esc:.1f})")
        p["images"] = base + nuevas
        p["image_captions"] = caps
    json.dump(cat, open(os.path.join(ROOT, "data/catalog.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    with open(os.path.join(ROOT, "data/catalog.js"), "w", encoding="utf-8") as f:
        f.write("window.CATALOG_DATA = "); json.dump(cat, f, ensure_ascii=False); f.write(";")

if __name__ == "__main__":
    main()
