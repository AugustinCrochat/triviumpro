#!/usr/bin/env python3
"""
Descarga todas las imágenes referenciadas en data/catalog.json al directorio
assets/img/productos/ y reescribe el JSON usando rutas relativas.
Usa solo stdlib (urllib).

Ejecución:
    python3 scripts/download_images.py
"""
import json, os, re, sys, unicodedata
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError

ROOT = Path(__file__).resolve().parent.parent
CATALOG = ROOT / "data" / "catalog.json"
IMG_DIR = ROOT / "assets" / "img" / "productos"
IMG_DIR.mkdir(parents=True, exist_ok=True)

def clean(name: str) -> str:
    name = unicodedata.normalize("NFD", name).encode("ascii", "ignore").decode()
    name = name.lower()
    name = re.sub(r"[^a-z0-9._-]+", "-", name)
    return name

def download(url: str, dest: Path) -> bool:
    if dest.exists() and dest.stat().st_size > 0:
        return True
    try:
        req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urlopen(req, timeout=30) as r:
            data = r.read()
        dest.write_bytes(data)
        print(f"  ✔ {dest.name}  ({len(data)//1024} KB)")
        return True
    except (URLError, HTTPError) as e:
        print(f"  ✘ {url}  → {e}", file=sys.stderr)
        return False

def main():
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    used = set()
    url_to_local = {}

    # Build mapping
    urls = set()
    for p in catalog["products"]:
        if p.get("image"):
            urls.add(p["image"])
        for u in p.get("images", []) or []:
            urls.add(u)

    print(f"▶ {len(urls)} URLs únicas a descargar")
    for url in sorted(urls):
        base = clean(os.path.basename(url.split("?")[0]))
        name = base
        i = 1
        while name in used:
            stem, ext = os.path.splitext(base)
            name = f"{stem}-{i}{ext}"; i += 1
        used.add(name)
        dest = IMG_DIR / name
        if download(url, dest):
            url_to_local[url] = f"assets/img/productos/{name}"
        else:
            url_to_local[url] = None

    # Rewrite catalog with local paths
    ok, missing = 0, 0
    for p in catalog["products"]:
        if p.get("image"):
            local = url_to_local.get(p["image"])
            if local: p["image"] = local; ok += 1
            else: missing += 1
        if p.get("images"):
            new_imgs = []
            for u in p["images"]:
                local = url_to_local.get(u)
                if local: new_imgs.append(local)
            p["images"] = new_imgs

    CATALOG.write_text(json.dumps(catalog, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n✔ catalog.json actualizado — {ok} imágenes rewritas, {missing} fallidas")

if __name__ == "__main__":
    main()
