#!/usr/bin/env python3
"""Genera llms-full.txt: el catálogo completo en texto plano para que un LLM (o un buscador con IA)
tenga, en una sola lectura, cada equipo con sus datos técnicos, origen, certificaciones, ficha PDF,
video y precio de lista (cuando es público). Complementa llms.txt (que es el índice).

Uso: python3 scripts/generate_llms_full.py
"""
import json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fichas_datos as fd
from site_config import SITE_URL, ORG_NAME
from generate_pretty_urls import load_public_offers
from guias_content import GUIAS

ROOT = fd.ROOT

def main():
    d, extra = fd.cargar()
    offers, rate = load_public_offers()
    cats = {c["slug"]: c for c in d["categories"]}
    brands = {b["slug"]: b for b in d["brands"]}
    L = [f"# {ORG_NAME}: catálogo completo", "",
         f"> {ORG_NAME} (antes Trivium Center) es importador y distribuidor oficial de equipamiento para talleres mecánicos y gomerías en Argentina: "
         "elevadores, alineadoras, balanceadoras, desarmadoras, herramientas neumáticas y muebles de taller. Representa a Rotary Lift, Hofmann y Challenger Lifts "
         "(líneas premium) y fabrica su línea propia Trivium Pro (económica). Envíos, colocación (equipo de técnicos propio) y servicio técnico en todo el país. "
         "La instalación se cotiza aparte del precio del equipo.", "",
         f"Contacto: info@trivium.ar · WhatsApp +54 9 11 2701-5294 · WhatsApp ventas +54 9 351 399-4200. Sitio: {SITE_URL}/",
         "Los precios, cuando figuran, son de lista en pesos argentinos con IVA, calculados con el dólar oficial del día; consultá siempre la ficha del producto.", ""]
    top = [c for c in d["categories"] if not c.get("parent")]
    for top_c in top:
        fam = {top_c["slug"]} | {c["slug"] for c in d["categories"] if c.get("parent") == top_c["slug"]}
        prods = [p for p in d["products"] if p.get("category") in fam]
        if not prods: continue
        L += [f"## {top_c['name']}", ""]
        for p in prods:
            s = fd.build_spec(p, d, extra)
            L.append(f"### {p['name']}")
            L.append(f"- URL: {SITE_URL}/producto/{p['slug']}/")
            if s["marca"]: L.append(f"- Marca: {s['marca']}")
            if s["sku"]: L.append(f"- SKU: {s['sku']}")
            if s["categoria"]: L.append(f"- Categoría: {s['categoria']}")
            if s["origen"]: L.append(f"- Origen de fabricación: {s['origen'][1]}")
            if s["ce"]: L.append("- Marcado CE (conformidad con la normativa de la Unión Europea)")
            if s["ali"]: L.append(f"- Certificación ALI: modelo certificado {s['ali']['model']} (directorio de ALI, Automotive Lift Institute)")
            offer = offers.get(p.get("sku"))
            if offer: L.append(f"- Precio de lista: ${offer['price']:,.0f} ARS con IVA (instalación no incluida)".replace(",", "."))
            if s["resumen"]: L.append(f"- Resumen: {s['resumen']}")
            if s["destacado"] and s["destacado"] != s["resumen"]: L.append(f"- Descripción: {s['destacado']}")
            if s["specs"]:
                L.append("- Especificaciones: " + "; ".join(f"{a}: {b}" for a, b in s["specs"][:12]))
            if s["features"]:
                L.append("- Características: " + "; ".join((f"{a}: {b}" if a else b) for a, b in s["features"][:6]))
            L.append(f"- Ideal para: {s['ideal']}")
            pdf = f"assets/pdf/ficha-tecnica-{p['slug']}.pdf"
            if not os.path.exists(os.path.join(ROOT, pdf)):
                m = re.search(r'href="(assets/pdf/[^"]+\.pdf)"', p.get("html_description", ""))
                pdf = m.group(1) if m else ""
            if pdf: L.append(f"- Ficha técnica (PDF): {SITE_URL}/{pdf}")
            if s["video"]: L.append(f"- Video: {s['video']}")
            L.append("")
    L += ["## Guías de compra", ""] + [f"- {g['h1']}: {SITE_URL}/guias/{g['slug']}/ — {g['description']}" for g in GUIAS] + [""]
    open(os.path.join(ROOT, "llms-full.txt"), "w", encoding="utf-8").write("\n".join(L) + "\n")
    print(f"✔ llms-full.txt — {len(d['products'])} equipos, {len(''.join(L)) // 1024} KB")

if __name__ == "__main__":
    main()
