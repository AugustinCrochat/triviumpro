#!/usr/bin/env python3
"""Portadas 1200x630 (JPG) de las páginas de categoría y de marca: las usan og:image, twitter:image
y el JSON-LD (image / primaryImageOfPage) para que Google y las redes tengan una foto de producto en
vez del logo SVG.

Escribe assets/img/og/categoria-<slug>.jpg y assets/img/og/marca-<slug>.jpg. Mismo estilo que las
portadas del blog (generate_blog_thumbs.page). Requiere Chrome sin cabeza y Pillow.

Uso: python3 scripts/generate_listing_covers.py [slug ...]
"""
import json, os, shutil, signal, subprocess, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image
import generate_blog_thumbs as gb

ROOT = gb.ROOT
OUT = os.path.join(ROOT, "assets/img/og")

def elegir(prods, n=2):
    """Hasta n productos con foto, de marcas y categorías distintas si se puede."""
    sel, marcas, cats = [], set(), set()
    for p in prods:
        if p.get("image") and p.get("brand") not in marcas and p["category"] not in cats:
            sel.append(p); marcas.add(p.get("brand")); cats.add(p["category"])
        if len(sel) == n: return sel
    for p in prods:
        if p.get("image") and p not in sel:
            sel.append(p)
        if len(sel) == n: break
    return sel

def captura(html_path, png, intentos=3):
    for i in range(intentos):
        perfil = tempfile.mkdtemp(prefix="chrome-cover-")
        p = subprocess.Popen(["google-chrome", "--headless", "--no-sandbox", "--disable-gpu", "--hide-scrollbars",
                              f"--user-data-dir={perfil}", "--window-size=1100,600", "--virtual-time-budget=5000",
                              f"--screenshot={png}", html_path],
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
        try: p.wait(timeout=90)
        except subprocess.TimeoutExpired: pass
        finally:
            try: os.killpg(p.pid, signal.SIGKILL)
            except (ProcessLookupError, PermissionError): pass
            shutil.rmtree(perfil, ignore_errors=True)
        if os.path.exists(png) and os.path.getsize(png) > 1000: return
    raise RuntimeError("Chrome no generó " + png)

def main():
    only = set(sys.argv[1:])
    cat = json.load(open(os.path.join(ROOT, "data/catalog.json"), encoding="utf-8"))
    cats = {c["slug"]: c for c in cat["categories"]}
    os.makedirs(OUT, exist_ok=True)
    tmp = tempfile.mkdtemp()
    os.symlink(os.path.join(ROOT, "assets/img/logo-trivium.svg"), os.path.join(tmp, "logo.svg"))
    trabajos = []
    for c in cat["categories"]:
        subs = {s["slug"] for s in cat["categories"] if s.get("parent") == c["slug"]}
        prods = [p for p in cat["products"] if p["category"] == c["slug"] or p["category"] in subs]
        trabajos.append((f"categoria-{c['slug']}", "EQUIPAMIENTO DE TALLER", c.get("seo_name") or c["name"],
                         c.get("tagline") or f"{len(prods)} productos", prods))
    for b in cat["brands"]:
        prods = [p for p in cat["products"] if p.get("brand") == b["slug"]]
        trabajos.append((f"marca-{b['slug']}", "MARCAS · TRIVIUM PRO", b["name"], b.get("note") or "", prods))
    for nombre, kicker, titulo, sub, prods in trabajos:
        if only and not any(o in nombre for o in only): continue
        sel = elegir(prods)
        if not sel: continue
        srcs = []
        for j, p in enumerate(sel):
            dst = os.path.join(tmp, f"{nombre}_{j}.png")
            gb.trim(os.path.join(ROOT, p["image"]), dst); srcs.append(os.path.basename(dst))
        h = os.path.join(tmp, nombre + ".html"); png = os.path.join(tmp, nombre + ".png")
        open(h, "w", encoding="utf-8").write(gb.page(kicker, titulo, sub, srcs))
        captura(h, png)
        im = Image.open(png).convert("RGB")
        lienzo = Image.new("RGB", (1200, 630), (255, 255, 255)); lienzo.paste(im, (0, 15))
        lienzo.paste(im.crop((0, 0, 1100, 1)).resize((1100, 15)), (0, 0))        # prolonga la franja roja y el fondo
        lienzo.paste(im.crop((0, 599, 1100, 600)).resize((1100, 15)), (0, 615))
        lienzo.save(os.path.join(OUT, nombre + ".jpg"), "JPEG", quality=88, optimize=True)
        print("✔", nombre)

if __name__ == "__main__":
    main()
