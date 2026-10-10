"""Genera las páginas por zona /zonas/<slug>/ y el hub /zonas/.

Texto en scripts/zonas_content.py. Plantilla: guia.html (la misma de /guias/).

Uso:
    python3 scripts/generate_zonas.py
"""
import os

from generate_pretty_urls import (
    BASE_DIR, SITE_URL, ORG_NAME, breadcrumb_html, breadcrumb_jsonld,
    create_index_file, esc, faq_html, faq_jsonld, make_seo_block, blog_links_html,
)
from generate_guias import load
from zonas_content import ZONAS, JURISDICCIONES, PROCESO, UPDATED

ROOT2 = '../../'
OG_IMAGE = f"{SITE_URL}/assets/img/og-trivium.png"
ORG_REF = {"@type": "Organization", "name": ORG_NAME, "url": SITE_URL + '/'}


def cta(nombre):
    return ('<div class="cta"><p><strong>¿Querés cotizar para tu taller?</strong> Contanos qué '
            'necesitás y tu localidad, y te armamos la propuesta con los equipos y, por separado, '
            'el envío, la instalación y la capacitación.</p>'
            '<a class="btn btn--primary" href="https://wa.me/5491127015294?text='
            f'Hola%2C%20quiero%20cotizar%20equipamiento%20para%20mi%20taller%20en%20{esc(nombre).replace(" ", "%20")}.">'
            'Pedir cotización por WhatsApp</a></div>')


def service_jsonld(z, url):
    ld = {
        "@context": "https://schema.org",
        "@type": "Service",
        "name": f"Venta, instalación y servicio técnico de equipamiento para talleres en {z['nombre']}",
        "serviceType": "Equipamiento para talleres y gomerías",
        "url": url,
        "provider": ORG_REF,
        "areaServed": {"@type": "AdministrativeArea", "name": z['nombre'],
                       "containedInPlace": {"@type": "Country", "name": "Argentina"}},
    }
    return ld


def local_jsonld():
    return {
        "@context": "https://schema.org",
        "@type": "LocalBusiness",
        "name": ORG_NAME,
        "url": SITE_URL + '/',
        "image": f"{SITE_URL}/assets/img/logo-trivium.svg",
        "telephone": "+54 9 11 2701-5294",
        "email": "info@trivium.ar",
        "address": {"@type": "PostalAddress", "streetAddress": "Av. Donato Álvarez 7971",
                    "addressLocality": "Córdoba", "addressCountry": "AR"},
        "areaServed": {"@type": "Country", "name": "Argentina"},
    }


def main():
    blog_by_slug = {p['slug']: p for p in load('blog.json')}
    template = os.path.join(BASE_DIR, 'guia.html')

    for z in ZONAS:
        url = f"{SITE_URL}/zonas/{z['slug']}/"
        body = (z['intro'] + z['secciones'].replace('{{PROCESO}}', PROCESO) + cta(z['nombre']))
        crumbs = [("Inicio", ""), ("Zonas", "zonas/"), (z['nombre'], None)]
        jsonld = [
            breadcrumb_jsonld([("Inicio", SITE_URL + '/'), ("Zonas", SITE_URL + '/zonas/'),
                               (z['nombre'], url)]),
            service_jsonld(z, url),
            faq_jsonld(z['faqs']),
        ]
        if z.get('local'):
            jsonld.append(local_jsonld())
        create_index_file(
            os.path.join(BASE_DIR, 'zonas', z['slug']), template, 2,
            title=z['title'],
            og={'type': 'website', 'title': z['title'], 'description': z['description'],
                'image': OG_IMAGE, 'url': url},
            seo=make_seo_block(url, z['description'], jsonld),
            body={
                'crumbs': breadcrumb_html(crumbs, ROOT2),
                'guia-title': esc(z['h1']),
                'guia-tag': esc(z['nombre']),
                'guia-updated': f"Actualizado: {UPDATED}",
                'guia-body': body,
                'guia-faq': faq_html("Preguntas frecuentes", z['faqs']),
                'guia-posts': blog_links_html("Casos y notas de la zona", z['posts'], blog_by_slug, ROOT2),
            },
        )
        print(f"  -> zonas/{z['slug']}/")

    # Hub /zonas/
    url = f"{SITE_URL}/zonas/"
    title = "Envíos, instalación y servicio técnico en todo el país"
    desc = ("Vendemos, enviamos e instalamos equipamiento para talleres y gomerías en las 24 "
            "jurisdicciones de Argentina, con servicio técnico propio y repuestos originales.")
    filas = []
    for nombre, slug in JURISDICCIONES:
        if slug:
            filas.append(f'<li><a href="{esc(slug)}/">{esc(nombre)}</a></li>')
        else:
            filas.append(f'<li>{esc(nombre)}</li>')
    hub = (
        '<div class="respuesta"><p><strong>En resumen:</strong> vendemos, enviamos e instalamos '
        'equipamiento para talleres, gomerías y concesionarias en todo el país. La sede está en '
        'Córdoba y el equipo técnico viaja a cada instalación. La posventa tiene atención en 48 a '
        '72 horas en todo el país. La instalación se cotiza aparte.</p></div>'
        '<h2>Provincias donde trabajamos</h2>'
        '<p>Cubrimos las 23 provincias y la Ciudad Autónoma de Buenos Aires. Las que tienen link '
        'cuentan con una página con casos y datos de la zona.</p>'
        f'<ul class="zonas-lista">{"".join(filas)}</ul>'
        + PROCESO
        + cta("todo el país")
    )
    jsonld = [
        breadcrumb_jsonld([("Inicio", SITE_URL + '/'), ("Zonas", url)]),
        {"@context": "https://schema.org", "@type": "Service",
         "name": "Venta, instalación y servicio técnico de equipamiento para talleres",
         "url": url, "provider": ORG_REF,
         "areaServed": {"@type": "Country", "name": "Argentina"}},
    ]
    create_index_file(
        os.path.join(BASE_DIR, 'zonas'), template, 1,
        title=title,
        og={'type': 'website', 'title': title, 'description': desc, 'image': OG_IMAGE, 'url': url},
        seo=make_seo_block(url, desc, jsonld),
        body={'crumbs': breadcrumb_html([("Inicio", ""), ("Zonas", None)], '../'),
              'guia-title': 'Envíos, instalación y posventa en todo el país',
              'guia-tag': 'Cobertura', 'guia-updated': f"Actualizado: {UPDATED}",
              'guia-body': hub, 'guia-faq': '', 'guia-posts': ''},
    )
    print("  -> zonas/")


if __name__ == '__main__':
    main()
