#!/usr/bin/env python3
"""Genera el feed de catálogo de Meta (Facebook/Instagram Commerce Manager)
a partir de data/catalog.json + data/prices-publico.json.

Solo incluye productos Trivium Pro que tienen precio público cargado.
El precio del feed es el PRECIO FINAL (con IVA incluido), en ARS, calculado
con el dólar oficial venta del día (dolarapi.com) — salvo los ítems con
"fixed_ars" en prices-publico.json, que usan ese valor fijo como base.

Como es un archivo estático, hay que volver a correr este script cada vez
que se quiera actualizar el feed con la cotización del día:

    python3 scripts/generate_meta_catalog.py

Salida:
  feeds/meta-catalogo.csv     Meta Commerce Manager (Facebook/Instagram).
  feeds/google-merchant.tsv   Google Merchant Center (Shopping y fichas gratuitas),
                              archivo de texto delimitado por tabs. Mismos precios
                              y mismos productos que el feed de Meta.
"""
import csv
import html as html_lib
import json
import re
import sys
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent
from site_config import SITE_URL
FALLBACK_RATE = 1520  # valor de referencia si falla la consulta en vivo


def load_prices_publico():
    return json.loads((ROOT / "data" / "prices-publico.json").read_text(encoding="utf-8"))


def get_official_rate():
    try:
        r = requests.get("https://dolarapi.com/v1/dolares/oficial", timeout=10)
        r.raise_for_status()
        j = r.json()
        if j.get("venta"):
            return j["venta"], True
    except Exception as e:
        print(f"Aviso: no se pudo obtener el dólar en vivo ({e}); uso {FALLBACK_RATE}", file=sys.stderr)
    return FALLBACK_RATE, False


def abs_url(path):
    if not path:
        return ""
    return f"{SITE_URL}/{path.lstrip('/')}"


def plain(text):
    text = re.sub(r"<[^>]+>", " ", text or "")
    text = html_lib.unescape(text).replace(" : ", ": ")
    return re.sub(r"\s+", " ", text).strip()


def clip(text, limit):
    text = plain(text)
    if len(text) <= limit:
        return text
    return text[:limit].rsplit(" ", 1)[0].rstrip(" .,;:-") + "…"


def product_type(p, cats):
    """'Elevadores > 2 Columnas': la jerarquía de categorías del sitio."""
    cat = cats.get(p.get("category"))
    names = []
    while cat:
        names.insert(0, cat["name"])
        cat = cats.get(cat.get("parent"))
    return " > ".join(names)


def main():
    catalog = json.loads((ROOT / "data" / "catalog.json").read_text(encoding="utf-8"))
    prices = load_prices_publico()
    rate, live = get_official_rate()
    print(f"Dólar oficial venta: {rate} ({'en vivo' if live else 'referencia'})")

    by_sku = {p["sku"]: p for p in catalog["products"]}
    cats = {c["slug"]: c for c in catalog["categories"]}
    google_rows = []
    items = prices["items"]
    default_iva = prices["meta"]["default_iva"]

    rows = []
    for sku, rec in items.items():
        # 'tienda': false = no se vende online. El feed alimenta anuncios de
        # compra, así que tampoco se publica ahí (típicamente son precios
        # todavía sin confirmar).
        if rec.get("tienda") is False:
            continue
        p = by_sku.get(sku)
        if not p:
            print(f"Aviso: SKU {sku} en prices-publico.json no existe en catalog.json, se omite", file=sys.stderr)
            continue

        base_ars = rec["fixed_ars"] if rec.get("fixed_ars") is not None else rec["usd"] * rate
        iva = rec.get("iva", default_iva)
        total_ars = round(base_ars * (1 + iva / 100), 2)

        bullets = p.get("bullets") or []
        description = " ".join(bullets) if bullets else p["name"]

        images = [p["image"]] if p.get("image") else []
        images += [im for im in (p.get("images") or []) if im not in images]

        # Google: título con la marca, descripción de texto plano de 100+
        # caracteres, y sin GTIN (marca propia, no tiene código de barras
        # registrado) → identifier_exists = no.
        g_title = p["name"] if "trivium" in p["name"].lower() else f"{p['name']} - Trivium Pro"
        g_desc = clip(description, 700)
        if len(g_desc) < 100:
            g_desc += (" Línea Trivium Pro para talleres y gomerías, con instalación "
                       "y servicio técnico en todo el país.")
        google_rows.append({
            "id": sku,
            "title": clip(g_title, 150),
            "description": g_desc,
            "link": f"{SITE_URL}/producto/{p['slug']}/",
            "image_link": abs_url(images[0]) if images else "",
            "additional_image_link": ",".join(abs_url(im) for im in images[1:10]),
            "availability": "in_stock",
            "price": f"{total_ars:.2f} ARS",
            "condition": "new",
            "brand": "Trivium Pro",
            "mpn": rec.get("modelo") or "",
            "identifier_exists": "no",
            "product_type": product_type(p, cats),
        })

        rows.append({
            "id": sku,
            "title": p["name"],
            "description": description,
            "availability": "in stock",
            "condition": "new",
            "price": f"{total_ars:.2f} ARS",
            "link": f"{SITE_URL}/producto/{p['slug']}/",
            "image_link": abs_url(images[0]) if images else "",
            "additional_image_link": ",".join(abs_url(im) for im in images[1:5]),
            "brand": "Trivium Pro",
        })

    rows.sort(key=lambda r: r["id"])

    out_dir = ROOT / "feeds"
    out_dir.mkdir(exist_ok=True)
    out_path = out_dir / "meta-catalogo.csv"
    fieldnames = ["id", "title", "description", "availability", "condition",
                  "price", "link", "image_link", "additional_image_link", "brand"]
    with out_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Escrito {out_path} con {len(rows)} productos")

    google_rows.sort(key=lambda r: r["id"])
    g_path = out_dir / "google-merchant.tsv"
    g_fields = ["id", "title", "description", "link", "image_link", "additional_image_link",
                "availability", "price", "condition", "brand", "mpn", "identifier_exists",
                "product_type"]
    with g_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=g_fields, delimiter="\t",
                                quoting=csv.QUOTE_MINIMAL)
        writer.writeheader()
        writer.writerows(google_rows)
    print(f"Escrito {g_path} con {len(google_rows)} productos")


if __name__ == "__main__":
    main()
