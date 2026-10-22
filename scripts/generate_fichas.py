#!/usr/bin/env python3
"""Genera las fichas técnicas PDF de los productos con el formato Trivium Pro (HTML → Chrome).

Los datos salen de data/catalog.json y data/fichas_extra.json (ver scripts/fichas_datos.py). La
plantilla cuida el SEO y la lectura por LLM: título del PDF con el producto, texto real copiable
(sin letras sueltas), preguntas frecuentes, datos de origen y certificación, enlace a la ficha web
y sin posiciones absolutas en el contenido.

Uso: python3 scripts/generate_fichas.py [--slug SLUG ...] [--html]   (sin argumentos: todas)
     --html  deja también el HTML en /tmp/fichas_build/<slug>.html para revisarlo
"""
import html, os, re, subprocess, sys, shutil, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fichas_datos as fd
import make_ficha_chips as mc

ROOT = fd.ROOT
BUILD = "/tmp/fichas_build"
E = html.escape

CSS = """
@page{size:A4;margin:0}*{box-sizing:border-box}
body{margin:0;font-family:"Liberation Sans",Arial,Helvetica,sans-serif;color:#1a1a1a}
.page{width:210mm;min-height:297mm;padding:11mm 14mm 9mm;display:flex;flex-direction:column;page-break-after:always}
.page:last-child{page-break-after:auto}
.top{display:flex;align-items:center;border-bottom:1px solid #ccc;padding-bottom:2.5mm}
.top .lg{height:14mm;width:auto}
.top span{font-size:8pt;font-weight:bold;letter-spacing:.1em;white-space:nowrap}
.chips{display:flex;align-items:center;gap:3mm;margin-left:auto;margin-right:6mm;padding-left:10mm}.chips img{width:auto}
.kick{margin-top:4mm;font-size:8pt;letter-spacing:.1em;color:#c8102e;font-weight:bold;text-transform:uppercase}
h1{margin:1mm 0 1mm;font-size:19pt;line-height:1.12;font-weight:bold}
.sub{font-size:8.6pt;color:#555;line-height:1.3}
.hero{display:flex;gap:6mm;align-items:center;margin-top:3mm}
.hero .im{width:58mm;height:58mm;flex:none;display:flex;align-items:center;justify-content:center}
.hero .im img{max-width:100%;max-height:100%;object-fit:contain}
.ht{display:flex;flex-direction:column;gap:2.2mm;flex:1}
.ht p{border-left:3px solid #c8102e;padding-left:5mm;font-size:11pt;line-height:1.45;margin:0}
.lks{display:flex;gap:2mm;flex-wrap:wrap;padding-left:calc(5mm + 3px)}.lk{display:inline-flex;align-items:center;gap:1.4mm;border:.3mm solid #e3b5bc;border-radius:1.4mm;background:#fff7f8;color:#c8102e;text-decoration:none;font-size:8pt;font-weight:bold;padding:1mm 2.2mm}.lk .ic{width:3.4mm;height:3.4mm;flex:none}.lk i{font-style:normal;font-weight:normal}.ht{gap:2mm}
.tiles{display:flex;gap:2mm;margin-top:1mm}.tile{flex:1;background:#f2f2f2;border-radius:1.6mm;padding:1.6mm 2.2mm}
.tile b{display:block;font-size:10pt;line-height:1.15}.tile span{font-size:6.6pt;color:#666;text-transform:uppercase;letter-spacing:.03em}
h3{font-size:8pt;letter-spacing:.09em;margin:4mm 0 1.8mm;color:#333;text-transform:uppercase}
.cols{display:flex;gap:7mm}.cols>div:first-child{flex:1.12}.cols>div:last-child{flex:1}
.f{display:flex;gap:2.4mm;margin-bottom:2.2mm}.n{flex:none;width:4.4mm;height:4.4mm;border-radius:50%;background:#c8102e;color:#fff;font-size:7pt;font-weight:bold;text-align:center;line-height:4.4mm;margin-top:.4mm}
.f b{font-size:9.4pt}.f div{font-size:8.2pt;color:#444;line-height:1.3}
table{width:100%;border-collapse:collapse;font-size:8pt}td{padding:1.15mm 2mm;border-bottom:1px solid #fff;vertical-align:top}
tr:nth-child(odd) td{background:#f1f1f1}tr:nth-child(even) td{background:#f8f8f8}td+td{text-align:right;font-weight:bold}
.fin{background:#111;color:#fff;font-size:7.6pt;padding:1.8mm 2.4mm;margin-top:1mm}.fin b{color:#e5383b}
.gal{display:flex;gap:3mm}.gal div{flex:1;height:30mm;border:1px solid #e3e3e3;border-radius:1.6mm;display:flex;align-items:center;justify-content:center;background:#fff}.gal img{max-width:100%;max-height:100%;object-fit:contain}
.faq{display:grid;grid-template-columns:1fr 1fr;gap:2mm 5mm}.faq div{font-size:7.8pt;line-height:1.3;color:#444}.faq b{display:block;color:#111;font-size:8.2pt;margin-bottom:.4mm}
.main{flex:1}
.foot3{display:flex;gap:6mm;border-top:1px solid #ccc;padding-top:2mm;margin-top:4mm}.foot3>div{flex:1;font-size:7.3pt;color:#444;line-height:1.3}
.foot3 b{display:flex;align-items:center;gap:1.4mm;color:#000;font-size:8.3pt;margin-bottom:.5mm}.foot3 b:before{content:"";width:1.6mm;height:1.6mm;border-radius:50%;background:#c8102e;flex:none}
.ft{display:flex;justify-content:space-between;align-items:center;border-top:1px solid #ccc;padding-top:1.4mm;margin-top:2mm;font-size:7.3pt;color:#555}
.cajas{display:flex;gap:1.2mm;align-items:center}.lgp{height:6.2mm;width:auto;margin-right:1.2mm}
.caja{display:inline-flex;align-items:center;gap:1mm;border:.25mm solid #cfcfcf;border-radius:1.1mm;padding:.7mm 1.4mm;font-size:6.8pt;color:#444;text-decoration:none;background:#fff;white-space:nowrap}
.caja .ic{width:2.9mm;height:2.9mm;flex:none}.caja .wa{fill:#25D366;stroke:none}.caja .fl{width:4.2mm;height:2.8mm;flex:none;outline:.15mm solid #bbb}
"""

# Fichas ya hechas a mano en el formato nuevo (no se regeneran sin --slug)
YA_NUEVAS = {"elevador-dos-columnas-4535-kg-rotary-lift-spoa10", "elevador-dos-columnas-4536-kg-rotary-lift-spoa10trio",
             "elevador-dos-columnas-4000-kg-travesano-al-piso-unite-pl-4-0-2d", "elevador-dos-columnas-4000-kg-piso-libre-unite-pl-4-0-2a",
             "elevador-dos-columnas-6000-kg-vehiculos-electricos", "alineadora-3d-hofmann-geoliner-630", "alineadora-3d-hofmann-geoliner-880",
             "lift-para-balanceadoras-u-l01", "elevador-dos-columnas-simetrico-4536-kg-challenger-lifts-vle10",
             "elevador-tijera-alineacion-4000-kg-forward-lift-nbs40a-48", "elevador-dos-columnas-5000-kg-trivium-pro-u-t50msd"}

def svg_inline(nombre, cls):
    s = open(os.path.join(fd.ROOT, "assets/img/iconos/contacto", nombre), encoding="utf-8").read()
    s = re.sub(r"<\?xml.*?\?>", "", s).strip()
    return s.replace("<svg ", f'<svg class="{cls}" ', 1)

WA = ('<svg class="ic wa" viewBox="0 0 24 24"><path d="' + re.search(r'WA_PATH = \((.*?)\)\n\ndef', open(os.path.join(ROOT, "scripts/update_ficha_contacto.py"), encoding="utf-8").read(), re.S).group(1).replace('"\n           "', "").replace('"', "").replace(" \n", "") + '"/></svg>')
ORI_F = {"US": "estados-unidos", "IT": "italia", "DE": "alemania", "SE": "suecia", "TW": "taiwan", "CN": "marcado-ce"}
BANDERAS = {"US": "usa.svg", "CN": "china.svg", "IT": "italia.svg", "DE": "alemania.svg"}

def tiles(specs):
    prio = [r"capacidad", r"altura", r"alcance|di[aá]metro|rango", r"potencia|motor|energ", r"velocidad|tiempo", r"peso", r"tensi|voltaje|alimentaci", r"presi[oó]n|par "]
    usados, out = set(), []
    for pat in prio:
        for i, (a, b) in enumerate(specs):
            if i not in usados and re.search(pat, a, re.I) and len(b) <= 22:
                usados.add(i); out.append((b, a)); break
        if len(out) == 4: break
    return out

faqs = fd.faqs

def render(s, n_feat=6, n_spec=14, n_faq=4, galeria=True):
    img = lambda r: "file://" + os.path.join(ROOT, r)
    chips = ""
    brand_file = None
    for ext in ("svg", "webp", "png"):
        f = os.path.join(ROOT, f"assets/img/marcas/logo-{s['marca_slug']}.{ext}")
        if os.path.exists(f) and s["marca_slug"] != "trivium-pro": brand_file = f; break
    ORI = {"US": "estados-unidos", "IT": "italia", "DE": "alemania", "SE": "suecia", "TW": "taiwan", "CN": "marcado-ce"}
    SITE = "https://pro.trivium.ar"
    if brand_file: chips += f'<a href="{SITE}/marca/{s["marca_slug"]}/"><img src="file://{brand_file}" style="height:8mm;max-width:34mm"></a>'
    if s["origen"] and s["origen"][0] in ("US", "IT", "DE") :
        oid = {"US": "made-in-usa", "IT": "made-in-italy", "DE": "made-in-germany"}[s["origen"][0]]
        chips += f'<a href="{SITE}/origen/{ORI[s["origen"][0]]}/"><img src="file://{BUILD}/origin-{oid}.png" style="height:12mm"></a>'
    elif s["ce"]:
        chips += f'<a href="{SITE}/origen/marcado-ce/"><img src="file://{BUILD}/ce.png" style="height:10mm"></a>'
    if s["ali"]:
        a_ = s["ali"]
        chips += (f'<a href="https://www.autolift.org/ali-directory-of-certified-car-lifts/search-certified-car-lifts/?productCat={a_["cat"]}&amp;manufac={a_["manufac"]}&amp;ModNum&amp;rateval=%3D&amp;rateload&amp;searchsubmit=Search&amp;lift_id={a_["lift_id"]}">'
                  f'<img src="file://{BUILD}/ali-{s["ali"]["model"]}.png" style="height:10.5mm"></a>')
    feats = ""
    for i, (a, b) in enumerate(s["features"][:n_feat], 1):
        feats += f'<div class="f"><span class="n">{i}</span><div>' + (f'<b>{E(a)}</b><br>{E(b)}' if a else E(b)) + '</div></div>'
    rows = "".join(f"<tr><td>{E(a)}</td><td>{E(b)}</td></tr>" for a, b in s["specs"][:n_spec])
    tl = "".join(f'<div class="tile"><b>{E(v)}</b><span>{E(l)}</span></div>' for v, l in tiles(s["specs"]))
    gal = ""
    if galeria and s["galeria"]:
        gal = '<h3>Imágenes del producto</h3><div class="gal">' + "".join(f'<div><img src="{img(g)}" alt="{E(s["name"])}"></div>' for g in s["galeria"]) + "</div>"
    faq = "".join(f"<div><b>{E(q)}</b>{E(a)}</div>" for q, a in faqs(s)[:n_faq])
    flag = f'<a class="caja" href="https://pro.trivium.ar/origen/{ORI_F[s["origen"][0]]}/">Origen: {svg_inline("contacto_" + BANDERAS[s["origen"][0]], "fl") if False else svg_inline(BANDERAS.get(s["origen"][0], "usa.svg"), "fl")}{E(s["origen"][1])}</a>' if s["origen"] and s["origen"][0] in BANDERAS else ""
    kicker = " · ".join(x for x in (s["categoria"], s["marca"]) if x)
    subt = " · ".join(x for x in ((f"Modelo: {s['modelo']}" if s["modelo"] else ""), (f"SKU {s['sku']}" if s["sku"] else ""), E(s["resumen"])) if x)
    titulo = f"Ficha técnica {s['name']}" + ("" if "Trivium Pro" in s["name"] else " | Trivium Pro")
    cajas = (f'<a href="https://pro.trivium.ar/"><img class="lgp" src="file://{ROOT}/assets/img/marcas/logo-trivium-pro.svg" alt="Trivium Pro"></a>'
             f'<a class="caja" href="{s["url"]}">{svg_inline("globo.svg", "ic")}pro.trivium.ar</a>'
             f'<a class="caja" href="mailto:info@trivium.ar">{svg_inline("mail.svg", "ic")}info@trivium.ar</a>'
             f'<a class="caja" href="https://wa.me/5491127015294">{WA}+54 9 11 2701-5294</a>'
             f'<a class="caja" href="https://wa.me/5493513994200">{WA}+54 9 351 399-4200 (Ventas)</a>')
    return f"""<!doctype html><html lang="es"><head><meta charset="utf-8"><title>{E(titulo)}</title>
<meta name="author" content="Trivium Pro"><meta name="description" content="{E(s['resumen'])}"><style>{CSS}</style></head><body><div class="page">
<div class="top"><a href="https://pro.trivium.ar/"><img class="lg" src="file://{ROOT}/assets/img/marcas/logo-trivium-pro.svg" alt="Trivium Pro"></a><div class="chips">{chips}</div><span>FICHA TÉCNICA</span></div>
<div class="main"><div class="kick">{E(kicker)}</div><h1>{E(s['name'])}</h1><div class="sub">{subt}</div>
<div class="hero"><div class="im"><img src="{img(s['imagen'])}" alt="{E(s['name'])}"></div><div class="ht"><p>{E(s['destacado'] or s['resumen'])}</p><div class="lks"><a class="lk" href="{s['url']}">{svg_inline("web-rojo.svg", "ic")}Ver ficha del producto en la web <i>↗</i></a>{('<a class="lk" href="' + s['video'] + '">' + svg_inline("video-rojo.svg", "ic") + 'Ver video del producto <i>↗</i></a>') if s['video'] else ''}</div><div class="tiles">{tl}</div></div></div>
<div class="cols"><div><h3>Características principales</h3>{feats}</div><div><h3>Especificación técnica</h3><table>{rows}</table><div class="fin"><b>Financiación disponible:</b> consultá planes de pago.</div></div></div>
{gal}<h3>Preguntas frecuentes</h3><div class="faq">{faq}</div></div>
<div class="foot3"><div><b>Instalación en tu taller</b>Contamos con un equipo de técnicos para la colocación de tu equipo, en todo el país.</div><div><b>Servicio técnico oficial</b>Garantía y servicio técnico oficial en todo el país.</div><div><b>Repuestos originales</b>Stock permanente con garantía de trazabilidad.</div></div>
<div class="ft"><div class="cajas">{cajas}</div>{flag}</div></div></body></html>"""

def chrome_pdf(html_path, pdf_path):
    subprocess.run(["google-chrome", "--headless", "--no-sandbox", "--disable-gpu", "--no-pdf-header-footer", f"--print-to-pdf={pdf_path}", html_path],
                   check=True, capture_output=True)

def paginas(pdf):
    out = subprocess.run(["pdfinfo", pdf], capture_output=True, text=True).stdout
    return int(re.search(r"Pages:\s+(\d+)", out).group(1))

def generar(s, guardar_html=False):
    os.makedirs(BUILD, exist_ok=True)
    pasos = [dict(), dict(galeria=False), dict(n_faq=3, galeria=False), dict(n_faq=3, n_spec=12, n_feat=5, galeria=False),
             dict(n_faq=2, n_spec=10, n_feat=5, galeria=False), dict(n_faq=2, n_spec=8, n_feat=4, galeria=False)]
    for kw in pasos:
        h = os.path.join(BUILD, s["slug"] + ".html"); open(h, "w", encoding="utf-8").write(render(s, **kw))
        pdf = os.path.join(BUILD, s["slug"] + ".pdf"); chrome_pdf(h, pdf)
        if paginas(pdf) == 1: break
    destino = os.path.join(ROOT, "assets/pdf", f"ficha-tecnica-{s['slug']}.pdf")
    shutil.copy(pdf, destino)
    return destino, paginas(pdf), kw

if __name__ == "__main__":
    d, extra = fd.cargar()
    args = sys.argv[1:]
    slugs = [args[i + 1] for i, a in enumerate(args) if a == "--slug"]
    os.makedirs(BUILD, exist_ok=True)
    mc.main(BUILD)  # insignias: marca, origen, CE
    for p in d["products"]:
        if slugs and p["slug"] not in slugs: continue
        if not slugs and p["slug"] in YA_NUEVAS: continue
        s = fd.build_spec(p, d, extra)
        if s["ali"]: mc.ali_chip(BUILD, s["ali"]["model"])
        dest, n, kw = generar(s)
        print(f"✔ {os.path.basename(dest)} ({n} pág.{'; reducida' if kw else ''})")
