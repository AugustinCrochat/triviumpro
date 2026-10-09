#!/usr/bin/env python3
"""Genera llms.txt en la raíz del sitio.

llms.txt es una convención (llmstxt.org) para que un asistente de IA que lee
la web entienda de qué trata el sitio y dónde está lo importante, sin tener
que rastrear y adivinar la estructura entera. Lo consumen navegadores con IA,
agentes de compra y chats de uso general al citar o resumir el sitio.

Se genera a partir de data/catalog.json para que las categorías y marcas
listadas nunca queden desincronizadas del catálogo real.

OJO: nunca se listan acá las URLs privadas (el folleto de todas las marcas,
la lista de revendedores). Sus slugs son secretos justamente para no aparecer
en ningún archivo público — llms.txt es tan público como robots.txt.

Uso:
    python3 scripts/generate_llms_txt.py
"""
import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
from site_config import SITE_URL, ORG_NAME


from guias_content import GUIAS
from zonas_content import ZONAS


def main():
    with open(os.path.join(BASE_DIR, 'data', 'catalog.json'), encoding='utf-8') as f:
        catalog = json.load(f)

    n_prod = len(catalog['products'])
    top_cats = [c for c in catalog['categories'] if not c.get('parent')]
    brands = catalog['brands']

    lines = [
        f"# {ORG_NAME}",
        "",
        f"> Importador y distribuidor oficial de equipamiento para talleres mecánicos "
        f"y gomerías en Argentina: elevadores de auto, alineadoras, balanceadoras y "
        f"desarmadoras de neumáticos. Representante oficial de las marcas premium, de "
        f"mayor calibre y rendimiento, Rotary Lift y Challenger Lifts (elevadores) y "
        f"Hofmann (alineación y balanceo), y fabricante de "
        f"Trivium Pro, su línea propia de equipamiento económico. Instalación y "
        f"servicio técnico propios en todo el país.",
        "",
        f"Catálogo completo: {n_prod} equipos en {len(top_cats)} categorías. Los precios "
        f"publicados son de lista, en pesos argentinos, calculados con el dólar oficial "
        f"venta del día e IVA incluido cuando se indica.",
        "",
        "## Catálogo",
        "",
        f"- [Catálogo completo]({SITE_URL}/catalogo/): los {n_prod} equipos, todas las marcas.",
    ]
    for c in top_cats:
        tagline = f": {c['tagline']}" if c.get('tagline') else ""
        lines.append(f"- [{c['name']}]({SITE_URL}/categoria/{c['slug']}/){tagline}")
    lines += [
        "",
        "## Marcas representadas",
        "",
        "Dos gamas conviven en el catálogo: las marcas premium importadas, de mayor "
        "calibre (Rotary Lift, Hofmann, Challenger Lifts, Direct Lift, Forward Lift, "
        "Haweka, Prevost) y Trivium Pro, la "
        "línea económica propia presente en varias categorías (elevadores, "
        "balanceadoras, desarmadoras, muebles y equipamiento de taller).",
        "",
    ]
    for b in brands:
        note = f" — {b['note']}" if b.get('note') else ""
        lines.append(f"- [{b['name']}]({SITE_URL}/marca/{b['slug']}/){note}")
    lines += [
        "",
        "## Precios",
        "",
        f"- [Lista de precios]({SITE_URL}/lista-precios/): todos los equipos con precio "
        f"publicado, para ver en pantalla o descargar en PDF.",
        f"- Compra online con Mercado Pago disponible en cada ficha de producto "
        f"({SITE_URL}/catalogo/) para los equipos de marca propia Trivium Pro.",
        "",
        "## Preguntas frecuentes",
        "",
        "- **¿Qué máquinas de taller vende Trivium Pro?** Elevadores de auto, "
        "alineadoras, balanceadoras y desarmadoras de neumáticos, más herramientas "
        "neumáticas, muebles de taller y aire comprimido.",
        "- **¿Es representante oficial de Rotary Lift y Hofmann?** Sí, importador y "
        "distribuidor oficial de ambas marcas en Argentina, con instalación y "
        "servicio técnico propios.",
        "- **¿Tiene una línea económica además de las marcas premium?** Sí, Trivium "
        "Pro es también la marca propia: equipamiento de precio más accesible que "
        "Rotary Lift, Challenger Lifts o Hofmann, pensado para talleres que arrancan "
        "o amplían capacidad. Las marcas premium son la opción para alto volumen de "
        "trabajo y uso intensivo.",
        "- **¿Instalan el equipo o sólo lo venden?** Instalan: montaje, puesta en "
        "marcha y posventa con equipo técnico propio en todo el país.",
        "",
        "## Guías de compra",
        "",
        *[f"- [{g['h1']}]({SITE_URL}/guias/{g['slug']}/): {g['description']}"
          for g in GUIAS],
        "",
        "## Cobertura",
        "",
        f"- [Envíos, instalación y posventa en todo el país]({SITE_URL}/zonas/)",
        *[f"- [{z['h1']}]({SITE_URL}/zonas/{z['slug']}/)" for z in ZONAS],
        "",
        "## Empresa",
        "",
        f"- [Nosotros]({SITE_URL}/nosotros/)",
        f"- [Instalación y posventa]({SITE_URL}/instalacion-posventa-y-servicios/)",
        f"- [Blog]({SITE_URL}/blog/): notas técnicas sobre equipamiento de taller.",
        f"- [Contacto]({SITE_URL}/contacto/)",
        "",
        "## Notas para agentes",
        "",
        "- Los precios de lista son orientativos y no incluyen envío ni instalación, "
        "que se cotizan aparte según la localidad de entrega.",
        "- La disponibilidad de cada equipo se confirma antes de cerrar una compra.",
    ]

    out_path = os.path.join(BASE_DIR, 'llms.txt')
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')
    print(f"✔ llms.txt — {n_prod} equipos, {len(top_cats)} categorías, {len(brands)} marcas")


if __name__ == '__main__':
    main()
