#!/usr/bin/env python3
"""Arma los datos de cada ficha técnica a partir de data/catalog.json (+ data/fichas_extra.json,
que se completa a mano con lo que sale de las hojas viejas y de la información online).

build_spec(producto) devuelve un dict con todo lo que necesita la plantilla (generate_fichas.py).
"""
import html, json, os, re
from html.parser import HTMLParser

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def cargar():
    d = json.load(open(os.path.join(ROOT, "data/catalog.json"), encoding="utf-8"))
    extra_path = os.path.join(ROOT, "data/fichas_extra.json")
    extra = json.load(open(extra_path, encoding="utf-8")) if os.path.exists(extra_path) else {}
    return d, extra

def limpio(t):
    t = re.sub(r"<[^>]+>", " ", t or "")
    return re.sub(r"\s+", " ", html.unescape(t)).strip()

class _Desc(HTMLParser):
    """Lee el html_description de WooCommerce: destacado, características y grupos de especificaciones."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.pila = []; self.destacado = ""; self.caracts = []; self.grupos = []; self.buf = ""; self.cur = None
        self.en_li = False; self.en_h4 = False; self.en_hl = False; self.en_feat = False; self.en_spec = False; self.h4 = ""
    def handle_starttag(self, tag, attrs):
        a = dict(attrs); c = a.get("class", "")
        if tag == "p" and "product-page-highlight" in c: self.en_hl = True; self.buf = ""
        if tag == "ul" and "product-page-features-list" in c: self.en_feat = True
        if tag == "div" and "product-page-spec-group" in c: self.en_spec = True; self.cur = {"titulo": "", "items": []}
        if tag == "h4": self.en_h4 = True; self.h4 = ""
        if tag == "li": self.en_li = True; self.buf = ""
    def handle_endtag(self, tag):
        if tag == "p" and self.en_hl: self.destacado = limpio(self.buf); self.en_hl = False
        if tag == "h4" and self.en_h4:
            self.en_h4 = False
            if self.cur is not None: self.cur["titulo"] = limpio(self.h4)
        if tag == "li" and self.en_li:
            self.en_li = False; t = limpio(self.buf)
            if t:
                if self.en_feat and not self.en_spec: self.caracts.append(t)
                elif self.cur is not None: self.cur["items"].append(t)
        if tag == "ul" and self.en_feat and self.cur is None: self.en_feat = False
        if tag == "div" and self.en_spec and self.cur is not None and tag == "div":
            pass
    def handle_data(self, d):
        if self.en_h4: self.h4 += d
        if self.en_li or self.en_hl: self.buf += d
    def cierra_grupo(self): pass

def parsear_desc(t):
    p = _Desc(); p.feed(t or "")
    # los grupos se cierran al abrir el siguiente: reconstruir por regex (más robusto que seguir los <div>)
    grupos = []
    for m in re.finditer(r'<div class="product-page-spec-group">(.*?)</div>', t or "", re.S):
        g = m.group(1)
        tit = limpio(re.search(r"<h4[^>]*>(.*?)</h4>", g, re.S).group(1)) if "<h4" in g else ""
        items = [limpio(x) for x in re.findall(r"<li[^>]*>(.*?)</li>", g, re.S)]
        grupos.append((tit, [i for i in items if i]))
    return p.destacado, p.caracts, grupos

def par(item):
    """'Capacidad: 4000kg' -> ('Capacidad', '4000kg'); sin dos puntos -> (item, '')."""
    if ":" in item:
        a, b = item.split(":", 1)
        if 0 < len(a) <= 48 and b.strip():
            return a.strip(), b.strip()
    return item.strip(), ""

CATEGORIA_IDEAL = {
    "elevadores": "talleres mecánicos, gomerías, lubricentros y concesionarias",
    "elevadores-2-columnas": "talleres mecánicos multimarca y de servicio general",
    "elevadores-4-columnas": "alineación, estacionamiento y servicio de vehículos pesados",
    "elevadores-tijera": "gomerías, lubricentros y talleres con poco espacio",
    "elevadores-pesados": "camiones, colectivos y vehículos pesados",
    "elevadores-motos": "talleres de motos y cuatriciclos",
    "alineadoras": "talleres de alineación y gomerías que ofrecen alineación",
    "balanceadoras": "gomerías y talleres que balancean ruedas",
    "desarmadoras": "gomerías y talleres de neumáticos",
    "herramientas-neumaticas": "talleres y gomerías con red de aire comprimido",
    "muebles-taller": "ordenar herramientas y repuestos en el puesto de trabajo",
    "equipamiento-taller": "talleres mecánicos y gomerías",
    "accesorios-balanceo": "balanceadoras y servicios de alineación y balanceo",
    "aire-comprimido": "talleres, gomerías y lubricentros",
}

ORIGEN = {"made-in-usa": ("US", "Estados Unidos"), "made-in-italy": ("IT", "Italia"), "made-in-germany": ("DE", "Alemania"),
          "made-in-sweden": ("SE", "Suecia"), "made-in-taiwan": ("TW", "Taiwán")}

VALOR = re.compile(r"\d")
UNIDAD = re.compile(r"(mm|cm|kg|kgs|lb|lbs|kw|hp|cv|rpm|r\.p\.m|seg|s\b|db|v\b|hz|psi|bar|nm|\"|”|m3|l/min|cfm|min|°|%|ton|litros|pulg)", re.I)
RUIDO = re.compile(r"trivium|www\.|pro\.trivium|whatsapp|@|origen|ficha|pag\.|tel[eé]fono|garant", re.I)

SUELTAS = {"angosto", "estándar", "estandar", "amplio", "modelo", "peso", "ancho", "alto", "largo"}

def specs_de_pdf(p):
    """Pares etiqueta/valor leídos del PDF viejo del producto (pdftotext -layout): 'Etiqueta | valor' o 'Etiqueta: valor'."""
    import subprocess
    pares, vistos = [], set()
    for f in re.findall(r'href="(assets/pdf/[^"]+\.pdf)"', p.get("html_description", "")):
        ruta = os.path.join(ROOT, f)
        if not os.path.exists(ruta) or "/ficha-tecnica-" in f: continue
        t = subprocess.run(["pdftotext", "-layout", "-f", "1", "-l", "2", ruta, "-"], capture_output=True, text=True).stdout
        for linea in t.splitlines():
            trozos = [x.strip(" •·-–.\t") for x in re.split(r"\s{3,}", linea.strip()) if x.strip()]
            # tabla en columnas: "Etiqueta      valor"  (sin ':' ni '|')
            for a, b in zip(trozos, trozos[1:]):
                a2 = re.sub(r"^[A-Z]\.\s*", "", a)
                if (3 <= len(a2) <= 46 and not RUIDO.search(a2) and not re.search(r"\d{3}", a2) and VALOR.search(b) and UNIDAD.search(b)
                        and len(b.split()) <= 7 and not RUIDO.search(b) and a2.lower() not in vistos):
                    vistos.add(a2.lower()); pares.append([a2, b.strip(" .")])
            for trozo in trozos:
                trozo = trozo.strip(" •·-–.\t")
                if not trozo or RUIDO.search(trozo): continue
                m = re.match(r"^([A-Za-zÁÉÍÓÚÑáéíóúñ][^:|]{2,46}?)\s*[:|]\s*(.{1,40})$", trozo)
                if not m: continue
                a, b = m.group(1).strip(), m.group(2).strip(" .")
                if VALOR.search(b) and UNIDAD.search(b) and len(b.split()) <= 7 and a.lower() not in vistos:
                    vistos.add(a.lower()); pares.append([a, b])
    pares = [x for x in pares if x[0].lower() not in SUELTAS and "especificaci" not in x[1].lower()]
    return pares[:16]

def build_spec(p, d, extra):
    brands = {b["slug"]: b for b in d["brands"]}; cats = {c["slug"]: c for c in d["categories"]}
    ex = extra.get(p["slug"], {})
    dest, caracts, grupos = parsear_desc(p.get("html_description", ""))
    cat = cats.get(p.get("category"), {}); marca = brands.get(p.get("brand"), {})
    resumen = ex.get("resumen") or p.get("summary") or dest or ""
    destacado = ex.get("destacado") or dest or p.get("summary") or ""
    feats = ex.get("caracteristicas")
    if feats is None:
        fuente = caracts or p.get("bullets") or []
        feats = []
        for t in fuente:
            a, b = par(t)
            feats.append([a, b] if b and len(a) < 46 else ["", t])
    specs = ex.get("specs")
    if specs is None:
        specs = []
        for tit, items in grupos:
            for it in items:
                a, b = par(it)
                if b: specs.append([a, b])
        if len(specs) < 3:
            for a, b in specs_de_pdf(p):
                if all(a.lower() != x[0].lower() for x in specs): specs.append([a, b])
        if not specs:
            if p.get("capacity") not in (None, "", "—"): specs.append(["Capacidad", str(p["capacity"])])
            if p.get("lift_height") not in (None, "", "—"): specs.append(["Altura de elevación", str(p["lift_height"])])
    mv = re.search(r'product-page-btn-video[^>]*href="([^"]+)"', p.get("html_description", "")) or re.search(r'href="([^"]+)"[^>]*product-page-btn-video', p.get("html_description", ""))
    video = mv.group(1) if mv and mv.group(1).startswith("http") else ""
    modelo = ex.get("modelo") or ""
    origen = next(((ORIGEN[b][0], ORIGEN[b][1]) for b in p.get("badges", []) if b in ORIGEN), None)
    if "ce-ue" in p.get("badges", []) and not origen:
        origen = ("CN", "China")
    return dict(
        slug=p["slug"], name=p["name"], sku=p.get("sku", ""), categoria=cat.get("name", ""), cat_slug=p.get("category", ""),
        marca=marca.get("name", ""), marca_slug=p.get("brand", ""), modelo=modelo, resumen=resumen, destacado=destacado,
        features=feats, specs=specs, origen=origen, ce="ce-ue" in p.get("badges", []), ali=p.get("ali"),
        video=video, imagen=p.get("image", ""), galeria=[i for i in (p.get("images") or []) if i != p.get("image")][:3],
        ideal=ex.get("ideal") or CATEGORIA_IDEAL.get(p.get("category"), "talleres y gomerías"),
        url=f"https://pro.trivium.ar/producto/{p['slug']}/", capacidad=p.get("capacity", ""), extra=ex,
    )

if __name__ == "__main__":
    d, extra = cargar()
    out = {}
    for p in d["products"]:
        s = build_spec(p, d, extra)
        out[p["slug"]] = dict(features=len(s["features"]), specs=len(s["specs"]), destacado=bool(s["destacado"]), galeria=len(s["galeria"]))
    import collections
    print(collections.Counter((v["features"] > 0, v["specs"] >= 3) for v in out.values()))
    json.dump(out, open("/tmp/fichas_resumen.json", "w"), indent=1)
