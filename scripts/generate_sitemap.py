"""
Genera sitemap.xml y robots.txt a partir de data/catalog.json y data/blog.json.

Uso:
    python3 scripts/generate_sitemap.py

Salida: sitemap.xml y robots.txt en la raíz del sitio.

Se excluyen las secciones marcadas noindex en vercel.json (cotizacion,
lista de revendedores).
"""

import json
import os
from datetime import date
from xml.sax.saxutils import escape

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
from site_config import SITE_URL

# Páginas estáticas: (ruta, prioridad, frecuencia)
STATIC_PAGES = [
    ("/", "1.0", "weekly"),
    ("/catalogo/", "0.9", "weekly"),
    ("/marcas/", "0.7", "monthly"),
    ("/instalacion-posventa-y-servicios/", "0.7", "monthly"),
    ("/nosotros/", "0.5", "yearly"),
    ("/contacto/", "0.5", "yearly"),
    ("/blog/", "0.7", "weekly"),
    ("/mapa-del-sitio/", "0.5", "weekly"),
    ("/envios-y-entregas/", "0.4", "yearly"),
    ("/cambios-devoluciones-y-arrepentimiento/", "0.4", "yearly"),
    ("/terminos-y-condiciones/", "0.3", "yearly"),
    ("/politica-de-privacidad/", "0.3", "yearly"),
]


def load(name):
    with open(os.path.join(BASE_DIR, "data", name), encoding="utf-8") as f:
        return json.load(f)


def url_entry(loc, lastmod=None, changefreq=None, priority=None, images=None):
    parts = [f"    <loc>{escape(loc)}</loc>"]
    if lastmod:
        parts.append(f"    <lastmod>{lastmod}</lastmod>")
    if changefreq:
        parts.append(f"    <changefreq>{changefreq}</changefreq>")
    if priority:
        parts.append(f"    <priority>{priority}</priority>")
    for src, titulo in (images or []):
        parts.append(f"    <image:image><image:loc>{escape(SITE_URL + '/' + src)}</image:loc>"
                     f"<image:title>{escape(titulo)}</image:title></image:image>")
    return "  <url>\n" + "\n".join(parts) + "\n  </url>"


LASTMOD_STATE = os.path.join(BASE_DIR, "scripts", "sitemap-lastmod.json")


def _git_date(path):
    """Fecha del último commit que tocó el archivo (para sembrar el estado)."""
    import subprocess
    try:
        out = subprocess.run(["git", "log", "-1", "--format=%cs", "--", path],
                             cwd=BASE_DIR, capture_output=True, text=True, timeout=10)
        return out.stdout.strip() or None
    except Exception:
        return None


class LastMod:
    """lastmod real por URL: la fecha cambia sólo si cambió el HTML de la página.

    Poner la fecha de hoy en todas las URLs le dice a Google que todo cambió
    todos los días, y termina ignorando el campo. Se guarda el hash del HTML de
    cada página en scripts/sitemap-lastmod.json (scripts/ no se publica); si el
    hash cambia, la fecha pasa a hoy. La primera vez se siembra con la fecha del
    último commit del archivo.
    """

    def __init__(self, today):
        self.today = today
        try:
            with open(LASTMOD_STATE, encoding="utf-8") as f:
                self.state = json.load(f)
        except (OSError, ValueError):
            self.state = {}

    def get(self, url_path):
        import hashlib
        rel = url_path.strip("/")
        file = os.path.join(BASE_DIR, rel, "index.html") if rel else os.path.join(BASE_DIR, "index.html")
        if not os.path.exists(file):
            return self.today
        with open(file, "rb") as f:
            digest = hashlib.sha1(f.read()).hexdigest()
        rec = self.state.get(url_path)
        if rec is None:
            self.state[url_path] = {"hash": digest, "date": _git_date(file) or self.today}
        elif rec["hash"] != digest:
            self.state[url_path] = {"hash": digest, "date": self.today}
        return self.state[url_path]["date"]

    def save(self):
        with open(LASTMOD_STATE, "w", encoding="utf-8") as f:
            json.dump(self.state, f, indent=0, sort_keys=True)
            f.write("\n")


def main():
    catalog = load("catalog.json")
    posts = load("blog.json")
    today = date.today().isoformat()
    lm = LastMod(today)

    entries = []

    for path, priority, freq in STATIC_PAGES:
        entries.append(url_entry(SITE_URL + path, lm.get(path), freq, priority))

    # Páginas pilar /guias/: salen de scripts/guias_content.py
    from guias_content import GUIAS
    entries.append(url_entry(f"{SITE_URL}/guias/", lm.get("/guias/"), "monthly", "0.8"))
    for g in GUIAS:
        entries.append(url_entry(f"{SITE_URL}/guias/{g['slug']}/", lm.get(f"/guias/{g['slug']}/"), "monthly", "0.8"))

    # Páginas de origen y marcado CE /origen/: salen de scripts/origenes_content.py
    from origenes_content import ORIGENES
    entries.append(url_entry(f"{SITE_URL}/origen/", lm.get("/origen/"), "monthly", "0.7"))
    for o in ORIGENES:
        entries.append(url_entry(f"{SITE_URL}/origen/{o['slug']}/", lm.get(f"/origen/{o['slug']}/"), "weekly", "0.7"))

    # Páginas por zona /zonas/: salen de scripts/zonas_content.py
    from zonas_content import ZONAS
    entries.append(url_entry(f"{SITE_URL}/zonas/", lm.get("/zonas/"), "monthly", "0.7"))
    for z in ZONAS:
        entries.append(url_entry(f"{SITE_URL}/zonas/{z['slug']}/", lm.get(f"/zonas/{z['slug']}/"), "monthly", "0.7"))

    for c in catalog["categories"]:
        entries.append(
            url_entry(f"{SITE_URL}/categoria/{c['slug']}/", lm.get(f"/categoria/{c['slug']}/"), "weekly", "0.8")
        )

    for b in catalog["brands"]:
        entries.append(
            url_entry(f"{SITE_URL}/marca/{b['slug']}/", lm.get(f"/marca/{b['slug']}/"), "monthly", "0.7")
        )

    pdfs = []
    for p in catalog["products"]:
        imgs = [(i, p["name"]) for i in dict.fromkeys([p.get("image")] + list(p.get("images") or [])) if i][:5]
        entries.append(
            url_entry(f"{SITE_URL}/producto/{p['slug']}/", lm.get(f"/producto/{p['slug']}/"), "monthly", "0.8", images=imgs)
        )
        import re as _re
        for f in _re.findall(r'href="(assets/pdf/[^"]+\.pdf)"', p.get("html_description", "")):
            if f not in pdfs: pdfs.append(f)

    # Fichas técnicas PDF: Google las indexa y rankean para "ficha técnica <modelo>".
    for f in pdfs:
        ruta = os.path.join(BASE_DIR, f)
        if os.path.exists(ruta):
            entries.append(url_entry(f"{SITE_URL}/{f}", _git_date(f) or today, "yearly", "0.5"))

    for post in posts:
        # date viene como 2025-10-29T23:49:21
        lastmod = post.get("date", "")[:10] or today
        entries.append(
            url_entry(f"{SITE_URL}/blog/{post['slug']}/", lastmod, "yearly", "0.6")
        )

    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">\n'
        + "\n".join(entries)
        + "\n</urlset>\n"
    )

    lm.save()
    sitemap_path = os.path.join(BASE_DIR, "sitemap.xml")
    with open(sitemap_path, "w", encoding="utf-8") as f:
        f.write(xml)

    # Sin Disallow a propósito. Las secciones privadas se sacan del índice con
    # X-Robots-Tag: noindex desde _headers, y para que Google lea ese header
    # necesita poder rastrear la página: un Disallow se lo impediría y la URL
    # quedaría indexada igual. Además robots.txt es público, así que listar
    # /lista-revendedores-<slug>/ acá publicaría el slug que se busca ocultar.
    # Bots de IA: explícitos aunque "User-agent: *" ya los habilita. Un grupo
    # propio los deja documentados y evita que una regla futura sobre * los
    # corte sin querer. Buscadores/asistentes que citan la fuente (OAI-SearchBot,
    # ChatGPT-User, Claude-SearchBot, Claude-User, PerplexityBot,
    # Perplexity-User) y los crawlers de entrenamiento (GPTBot, ClaudeBot,
    # Google-Extended, Applebot-Extended): permitir ambos hace que el catálogo
    # entre en las respuestas y en los modelos.
    ai_bots = [
        "OAI-SearchBot", "ChatGPT-User", "GPTBot",
        "Claude-SearchBot", "Claude-User", "ClaudeBot",
        "PerplexityBot", "Perplexity-User",
        "Google-Extended", "Applebot-Extended",
    ]
    robots = (
        "User-agent: *\n"
        "Allow: /\n"
        "\n"
        + "".join(f"User-agent: {bot}\nAllow: /\n\n" for bot in ai_bots)
        + f"Sitemap: {SITE_URL}/sitemap.xml\n"
    )
    with open(os.path.join(BASE_DIR, "robots.txt"), "w", encoding="utf-8") as f:
        f.write(robots)

    print(f"✔ sitemap.xml — {len(entries)} URLs")
    print("✔ robots.txt")


if __name__ == "__main__":
    main()
