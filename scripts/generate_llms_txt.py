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
import html
import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
from site_config import SITE_URL, ORG_NAME


from guias_content import GUIAS
from origenes_content import ORIGENES
from zonas_content import ZONAS


def _notas_por_tema():
    """Todas las notas del blog agrupadas por tema, para que un asistente encuentre la página que responde."""
    from blog_layout import SECCIONES, cargar, seccion
    posts, out = cargar(), []
    for tema in SECCIONES:
        grupo = [p for p in posts if seccion(p['slug']) == tema]
        if grupo:
            out += ["", f"## Blog: {tema}", ""] + [f"- [{html.unescape(p['title'])}]({SITE_URL}/blog/{p['slug']}/)" for p in grupo]
    return out


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
        f"- [Catálogo en texto plano para IA]({SITE_URL}/llms-full.txt): cada equipo con especificaciones, origen, certificaciones, ficha PDF y video.",
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
        "- El precio se muestra en la ficha de los equipos que lo tienen publicado; "
        "el resto se cotiza.",
        "- No hay compra online: la compra se coordina por WhatsApp o desde "
        f"[Contacto]({SITE_URL}/contacto/).",
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
        "marcha y posventa con equipo técnico propio en todo el país. La instalación "
        "se cotiza aparte del precio del equipo.",
        "",
        "## Guías de compra",
        "",
        *[f"- [{g['h1']}]({SITE_URL}/guias/{g['slug']}/): {g['description']}"
          for g in GUIAS],
        "",
        "## Origen de fabricación y marcado CE",
        "",
        "Cada equipo muestra sobre la foto un sello con su origen de fabricación (el que "
        "declara el fabricante del modelo, no el de la marca) o el marcado CE. El marcado "
        "CE es una declaración de conformidad con la normativa europea y no indica el país "
        "de fabricación.",
        "",
        f"- [Origen y marcado CE]({SITE_URL}/origen/): índice con todos los sellos.",
        *[f"- [{o['h1']}]({SITE_URL}/origen/{o['slug']}/): {o['description']}"
          for o in ORIGENES],
        "",
        "## Certificación ALI de elevadores",
        "",
        "ALI (Automotive Lift Institute) certifica la seguridad estructural de los elevadores "
        "vehiculares y publica un directorio de modelos certificados. Estos elevadores del "
        "catálogo figuran en ese directorio (el modelo certificado y el enlace al directorio "
        "están en cada ficha); los de Trivium Pro no tienen certificación ALI.",
        "",
        *[f"- [{p['name']}]({SITE_URL}/producto/{p['slug']}/): modelo ALI certificado "
          f"{p['ali']['model']}"
          f"{' (familia de modelos)' if p['ali'].get('family') else ''}."
          for p in catalog['products'] if p.get('ali')],
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
        f"- [Texto completo de todas las notas]({SITE_URL}/llms-blog.txt)",
        *_notas_por_tema(),
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
