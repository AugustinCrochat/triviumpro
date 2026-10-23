#!/usr/bin/env python3
"""Fichas Haweka de varios ítems en el formato nuevo (reemplazan las hojas viejas del fabricante).

Conservan los nombres de archivo de las hojas viejas (las URLs ya indexadas siguen valiendo) y
traen todo su contenido: códigos Haweka, descripciones y notas técnicas, con foto y enlace a la
ficha web cuando el ítem es un producto del catálogo. Cada producto suelto tiene además su propia
ficha (generate_fichas.py + data/fichas_extra.json).

Después: gs (-dPDFSETTINGS=/printer) y set_ficha_metadata.py (que conoce
estos títulos en CATALOGOS).

Uso: python3 scripts/generate_haweka_catalogos.py
"""
import html, json, os, shutil, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import generate_fichas as gf
import make_ficha_chips as mc

ROOT, BUILD, E = gf.ROOT, gf.BUILD, html.escape
SITE = "https://pro.trivium.ar"
CAT = {p["slug"]: p for p in json.load(open(os.path.join(ROOT, "data/catalog.json"), encoding="utf-8"))["products"]}

EXTRA_CSS = """
.gi{display:grid;grid-template-columns:1fr 1fr;gap:0 6mm}
.it{display:flex;gap:3mm;align-items:center;padding:2mm 0;border-bottom:1px solid #e6e6e6}
.it .ph{width:20mm;height:18mm;flex:none;display:flex;align-items:center;justify-content:center}.it .ph img{max-width:100%;max-height:100%;object-fit:contain}
.it .ph.v{background:#f4f4f4;border-radius:1.6mm;color:#bbb;font-size:7pt;letter-spacing:.06em}
.it .tx{flex:1}.it .cd{font-size:8pt;font-weight:bold;color:#c8102e;letter-spacing:.04em}
.it .nm{font-size:10pt;font-weight:bold;line-height:1.2}.it .ds{font-size:8.2pt;color:#444;line-height:1.3;margin-top:.4mm}
.it a.lk{margin-top:1mm}
.tipos{display:grid;grid-template-columns:1fr 1fr;gap:2.4mm 5mm;margin-top:1mm}.tipos div{font-size:8.2pt;line-height:1.3;color:#444;border-left:3px solid #c8102e;padding-left:3mm}.tipos b{display:block;color:#111;font-size:9pt}
p.t{font-size:9pt;line-height:1.4;color:#333;margin:1.6mm 0}
ul.v{margin:1mm 0 0;padding-left:5mm;font-size:8.6pt;line-height:1.4;color:#333}
"""

DOCS = [
 dict(archivo="web-ficha-accesorios-de-alineacion-y-balanceo.pdf",
  titulo="Accesorios Haweka para alineación y balanceo", kicker="Accesorios de balanceo · Haweka",
  sub="Espátula, nivel, pinza, calibres y campanas de sujeción · Códigos Haweka",
  resumen="Accesorios Haweka para alineación y balanceo: espátula, nivel de volante, pinza para contrapesos, calibres y campanas de sujeción, con código de cada uno.",
  imagen="assets/img/productos/calibre-haweka-para-medir-la-distancia-entre-bulones-de-ruedas.webp",
  paginas=[dict(intro="Herramientas de uso diario en alineación y balanceo, de la marca alemana Haweka. Cada código corresponde al artículo del fabricante; los que figuran como producto del catálogo tienen su propia ficha técnica y página en la web.",
   items=[
    ("900-e-008-089","Espátula","Para remover los contrapesos adhesivos.","espatula-para-despegar-contrapesos-adhesivos-en-llantas-de-aluminio-haweka"),
    ("921-001-000","Nivel","Indicador de nivel de volante.","indicador-de-nivel-de-volante-haweka"),
    ("900-008-006","Pinza","Clásica pinza para retirar los contrapesos.","pinza-para-plomos-contrapesos-haweka"),
    ("490-008-000","Calibre para medir los centros de llantas","Mide el diámetro del centro de la llanta para elegir el cono o la manga de centrado.",None),
    ("490 008 002","Calibre para medir la distancia entre bulones de ruedas","Mide la distancia entre bulones para elegir el adaptador correcto.","calibre-haweka-para-medir-la-distancia-entre-bulones-de-ruedas"),
    ("190 008 002","Campana de sujeción","Copa para tuerca de balanceadoras.",None),
    ("190 008 005","Tapa de goma","Para sujetar la campana: protector de copa 190 008 002 / 065.",None),
    ("190 008 021","Campana de fijación para llantas de aleación","Sujeta la rueda por la llanta de aleación.",None),
   ])]),
 dict(archivo="web-ficha-conos-y-mangas.pdf",
  titulo="Conos y mangas de centrado Haweka", kicker="Accesorios de balanceo · Haweka",
  sub="Conos, mangas, discos centradores y kits para balanceadoras · Códigos Haweka",
  resumen="Conos, mangas expansibles, discos centradores y kits de centrado Haweka para balanceadoras, con tipos, rangos y códigos; cómo centrar la rueda por el eje o por los pernos.",
  imagen="assets/img/productos/set-de-4-conos-de-centrado-haweka.webp",
  paginas=[
   dict(intro="Los adaptadores de centrado Haweka son los más universales del mercado actual: con el conjunto completo, el taller balancea con precisión cualquier tipo de rueda. Todo balanceo comienza con el montaje y el centrado correcto de la rueda.",
    tipos=[("Conos convencionales","Diseño de hace más de 60 años para ruedas metálicas livianas en autos con suspensiones mecánicas. Hoy producen más errores de los que resuelven."),
           ("Conos de bajo perfil (mangas)","Elemento de centrado ideal en sistemas de producción. Para llantas con centros de 52 mm a 121 mm. Flexibles, con excelentes resultados a precio competitivo."),
           ("Mangas expansibles de diámetro variable","Patentadas. Ideales para talleres con gran variedad de vehículos. Para llantas con centros de 54 mm a 94 mm."),
           ("Cilindros de centrado de diámetro específico","Mangas de diámetro específico: con este componente el técnico no puede cometer errores de medida.")],
    items=[
     ("150 400 110","Kit de 9 conos para balanceadora","Conos de 52,5 mm a 122 mm.","kit-de-9-conos-para-balanceadora-52-5-122-mm"),
     ("150 400 095","Set de conos de centrado (3 o 4 conos)","Set de conos de centrado de distintos diámetros.","conos-de-centrado-haweka"),
     ("150 400 049","Cono centrador 89–132 mm","Eje de la balanceadora de 40 mm de diámetro.",None),
     ("150 280 049","Cono centrador 4x4 89–132 mm","Eje de la balanceadora de 28 mm de diámetro.",None),
     ("190e400 045","Manga espaciadora","Para usar con los conos 150 280 049 y 150 400 049.",None),
     ("190e008 047","Anillo distanciador","Para los kits MB 280 400 061 y 160 400 056 y los conos 150 280 049 y 150 400 049.",None),
     ("160 400 056","Disco centrador MB Sprinter","Diámetro 161 mm.",None),
     ("160 400 053","Cono Toyota Hilux de bajo perfil","Para centrar ruedas con centros de 106 mm a 110 mm.",None),
    ]),
   dict(titulo2="Centrar la rueda: por el eje o por los pernos",
    intro="Sin el adaptador correcto al tipo, geometría y diseño de la rueda no hay balanceo correcto: un cero en la pantalla de la balanceadora no significa que la rueda esté bien balanceada. La rueda debe montarse y centrarse imitando lo más fielmente posible el montaje final en el vehículo.",
    bloques=[("Rueda centrada con el eje del vehículo","El centrado empieza por el eje: el orificio central de la llanta se ajusta al vehículo con gran precisión. El adaptador Haweka DuoExpert imita ese eje. En la conexión entre rueda y eje no hay un ángulo como el de un cono, y el eje no se monta por la parte exterior del rin, así que un cono por fuera nunca es correcto. La rueda se centra siempre por detrás.",
              ["Usá DuoExpert u otro adaptador que imite el eje del vehículo.","Centrá siempre la rueda por detrás."],"kit-haweka-duoexpert"),
             ("Rueda centrada con los pernos del vehículo","Acá el centrado se refuerza con la posición de los pernos. Con los Haweka QuickPlate o FlangePlate, la posición de los pernos se replica en la balanceadora de forma rápida, recreando la misma fricción que tendrá la rueda en el vehículo. Las copas de presión que traen las balanceadoras sujetan la rueda desde el centro pero no la centran según los pernos, por lo que no deben usarse en este tipo de rueda.",
              ["Usá QuickPlate o FlangePlate para imitar la posición de los pernos.","Como mínimo, centrá por detrás con un cono."],None)],
    cierre="Por qué toda balanceadora necesita adaptadores: los fabricantes equipan sus máquinas solo con conos estandarizados, una tecnología de más de 50 años que no sirve para muchas ruedas de hoy. Pesan las ruedas con revestimiento plástico, de hasta aro 28, más pesadas y sofisticadas, las de reposición, las de aleación y las de 8 o 10 pernos en camionetas, además de la rapidez que exige el taller y la falta de capacitación del técnico.")]),
 dict(archivo="39-ficha-805-818-000-805-995-000-probike-haweka.pdf",
  titulo="Dispositivo de fijación ProBike Haweka: Standard y Power Clamp", kicker="Accesorios de balanceo · Haweka",
  sub="Equilibrado de ruedas de moto · 805-818-000 y 805-995-000",
  resumen="Dispositivo de fijación ProBike de Haweka para equilibrar ruedas de moto (Standard 805-818-000 y Power Clamp 805-995-000): rango de agarre, componentes y ventajas.",
  imagen="assets/img/productos/centrado-de-ruedas-de-moto-probike.webp",
  paginas=[dict(intro="Permite el equilibrado estático y dinámico de ruedas de motocicleta, desde scooters con llantas de 10\" hasta ruedas anchas, chopper y off-road de hasta 21\". Se usa de forma flexible y mejoró año a año.",
   items=[
    ("805-818-000","ProBike Standard","Equilibra una gran variedad de ruedas de moto. Incluye placa adaptadora (más chica, ocupa menos espacio), el sistema de sujeción QuickFix Ø 14 mm, conos de centrado, manguitos de 15 a 28 mm y ruedas de scooter de 10\". Según la balanceadora hay dos tipos de adaptador para instalar el sistema: se elige al comprar.","dispositivo-de-fijacion-probike-haweka"),
    ("805-995-000","ProBike Power Clamp","Versión Power Clamp del dispositivo de fijación ProBike, con la misma gama de accesorios Haweka para el equilibrio estático y dinámico de ruedas de moto.","dispositivo-de-fijacion-probike-haweka"),
   ],
   extra_h="Ventajas de la ProBike",
   extra_li=["Resultados de equilibrado precisos.","Instalación fácil y rápida.","Rango de agarre de 360 mm a 740 mm.","Ideal para ruedas pequeñas de 10\" y para ruedas grandes todoterreno.","Manejo seguro y fácil; conexión óptima con la máquina.","Acople de rueda de scooter sin adaptadores de scooter.","Sin piezas de distancia entre la placa trasera y la placa base de la moto."]),
   dict(titulo2="Qué incluye el sistema ProBike",
    intro="Componentes del dispositivo de fijación ProBike y de sus kits de centrado adicionales.",
    lista=["Ala ProBike","Eje de centrado Ø 14 mm","Juego de conos de centrado Ø 15 – 30 mm","Juego de conos para scooter Ø 16 – 45 mm","Manguitos de centrado Ø 15 / 17 / 20 mm","Funda de centrado para Piaggio y Vespa","Pieza de presión Ø 14 mm para BMW / Moto Guzzi","Tablero de pared","QuickFix Ø 14 mm","Tuerca moleteada","Llave inglesa"],
    cierre="Uso del QuickFix: se desliza sobre el eje y la rueda se presiona contra la unidad de centrado; al ajustar el anillo plástico negro queda apretado contra la rueda. Terminado el equilibrado, se afloja el anillo, se presiona la palanca y se retira el QuickFix del eje.")]),
 dict(archivo="ficha-haweka-210-400-001-4-conos-expandibles-exhibidor.pdf",
  titulo="Conos expandibles y QuickPlate IV Haweka con exhibidor", kicker="Accesorios de balanceo · Haweka",
  sub="Conos expandibles 165 400 001 a 006 · QuickPlate IV 210 400 001 · Exhibidor",
  resumen="Conos expandibles Haweka de 54 a 86 mm (165 400 001/002/003/006), adaptador QuickPlate IV 210 400 001 y soporte exhibidor.",
  imagen="assets/img/productos/cono-expandible-haweka.webp",
  paginas=[dict(intro="Adaptadores de centrado Haweka para balanceadoras, con soporte exhibidor para tenerlos ordenados y a la vista en el taller.",
   items=[
    ("165 400 001","Cono expandible, rango 54 – 62 mm","Cono expandible patentado.","conos-expandibles-haweka-54-86-mm"),
    ("165 400 002","Cono expandible, rango 62 – 70 mm","Cono expandible patentado.","conos-expandibles-haweka-54-86-mm"),
    ("165 400 003","Cono expandible, rango 70 – 78 mm","Cono expandible patentado.","conos-expandibles-haweka-54-86-mm"),
    ("165 400 006","Cono expandible, rango 78 – 86 mm","Cono expandible patentado.","conos-expandibles-haweka-54-86-mm"),
    ("900e008 190","Soporte exhibidor","Para ordenar y exhibir los conos expandibles y adaptadores.","soporte-para-accesorios-haweka"),
    ("210 400 001","QuickPlate IV","Adaptador para centrar las ruedas por la posición de los pernos. Contiene 3 QuickPlate, 20 puntas adaptadoras variables y pared exhibidora.",None),
   ],
   extra_h="Ventajas del QuickPlate IV",
   extra_li=["No lleva tiempo elegir el diámetro correcto para los orificios de montaje.","Para diámetros estándar y no estándar de 95 mm a 182 mm.","Ajuste rápido del diámetro de ubicación de los orificios de fijación.","Fijación fácil gracias al sistema ProLock.","Cambio de cabeza rápido y fácil.","Adecuado para todos los accionamientos estándar con 4, 5 y 6 orificios de fijación.","Evita daños a la cubierta de la llanta.","Más delgado: permite equilibrar ruedas incluso en soportes con eje corto roscado."])]),
]

def pagina(doc, pg, idx, total):
    chips = ""
    bf = os.path.join(ROOT, "assets/img/marcas/logo-haweka.svg")
    for ext in ("svg", "webp", "png"):
        f = os.path.join(ROOT, f"assets/img/marcas/logo-haweka.{ext}")
        if os.path.exists(f): bf = f; break
    chips += f'<a href="{SITE}/marca/haweka/"><img src="file://{bf}" style="height:8mm;max-width:34mm"></a>'
    chips += f'<a href="{SITE}/origen/alemania/"><img src="file://{BUILD}/origin-made-in-germany.png" style="height:12mm"></a>'
    h1 = pg.get("titulo2") or doc["titulo"]
    kick = doc["kicker"]
    sub = doc["sub"] if idx == 0 else f"{doc['titulo']} · página {idx + 1} de {total}"
    body = f'<p class="t">{E(pg["intro"])}</p>' if pg.get("intro") else ""
    if pg.get("tipos"):
        body += '<h3>Tipos de adaptador</h3><div class="tipos">' + "".join(f"<div><b>{E(a)}</b>{E(b)}</div>" for a, b in pg["tipos"]) + "</div>"
    if pg.get("items"):
        body += '<h3>Artículos y códigos</h3><div class="gi">'
        for cod, nom, des, slug in pg["items"]:
            if slug:
                ph = f'<div class="ph"><img src="file://{ROOT}/{CAT[slug]["image"]}"></div>'
                lk = f'<a class="lk" href="{SITE}/producto/{slug}/">{gf.svg_inline("web-rojo.svg", "ic")}Ver ficha del producto <i>↗</i></a>'
            else:
                ph, lk = '<div class="ph v">HAWEKA</div>', ""
            body += f'<div class="it">{ph}<div class="tx"><div class="cd">HAWEKA {E(cod)}</div><div class="nm">{E(nom)}</div><div class="ds">{E(des)}</div>{lk}</div></div>'
        body += "</div>"
    if pg.get("extra_h"):
        body += f'<h3>{E(pg["extra_h"])}</h3><ul class="v">' + "".join(f"<li>{E(x)}</li>" for x in pg["extra_li"]) + "</ul>"
    if pg.get("lista"):
        body += '<h3>Componentes</h3><ul class="v">' + "".join(f"<li>{E(x)}</li>" for x in pg["lista"]) + "</ul>"
    for t, txt, pts, slug in pg.get("bloques", []):
        lk = f' <a class="lk" href="{SITE}/producto/{slug}/">{gf.svg_inline("web-rojo.svg", "ic")}Ver {E(CAT[slug]["name"])} <i>↗</i></a>' if slug else ""
        body += f'<h3>{E(t)}</h3><p class="t">{E(txt)}</p><ul class="v">' + "".join(f"<li>{E(x)}</li>" for x in pts) + f"</ul>{lk}"
    if pg.get("cierre"):
        body += f'<p class="t" style="margin-top:3mm">{E(pg["cierre"])}</p>'
    flag = f'<a class="caja o" href="{SITE}/origen/alemania/">Origen: {gf.svg_inline("alemania.svg", "fl")}Alemania</a>'
    cajas = (f'<a href="{SITE}/"><img class="lgp" src="file://{ROOT}/assets/img/marcas/logo-trivium-pro.svg" alt="Trivium Pro"></a>'
             f'<a class="caja" href="{SITE}/marca/haweka/">{gf.svg_inline("globo.svg", "ic")}pro.trivium.ar</a>'
             f'<a class="caja" href="mailto:info@trivium.ar">{gf.svg_inline("mail.svg", "ic")}info@trivium.ar</a>'
             f'<a class="caja w" href="https://wa.me/5491127015294">{gf.WA}+54 9 11 2701-5294</a>')
    return (f'<div class="page"><div class="top"><a href="{SITE}/"><img class="lg" src="file://{ROOT}/assets/img/marcas/logo-trivium-pro.svg" alt="Trivium Pro"></a><div class="chips">{chips}</div><span>FICHA TÉCNICA</span></div>'
            f'<div class="main"><div class="kick">{E(kick)}</div><h1>{E(h1)}</h1><div class="sub">{E(sub)}</div>{body}</div>'
            '<div class="foot3"><div><b>Instalación en tu taller</b>Contamos con un equipo de técnicos para la colocación de tu equipo, en todo el país.</div><div><b>Servicio técnico oficial</b>Garantía y servicio técnico oficial en todo el país.</div><div><b>Repuestos originales</b>Stock permanente con garantía de trazabilidad.</div></div>'
            f'<div class="ft"><div class="cajas">{cajas}</div>{flag}</div></div>')

def main():
    os.makedirs(BUILD, exist_ok=True)
    mc.main(BUILD)
    for doc in DOCS:
        pgs = "".join(pagina(doc, pg, i, len(doc["paginas"])) for i, pg in enumerate(doc["paginas"]))
        titulo = f"Ficha técnica {doc['titulo']} | Trivium Pro"
        h = os.path.join(BUILD, "hw-" + doc["archivo"].replace(".pdf", ".html"))
        open(h, "w", encoding="utf-8").write(f'<!doctype html><html lang="es"><head><meta charset="utf-8"><title>{E(titulo)}</title><meta name="author" content="Trivium Pro"><style>{gf.CSS}{EXTRA_CSS}</style></head><body>{pgs}</body></html>')
        pdf = os.path.join(BUILD, "hw-" + doc["archivo"])
        gf.chrome_pdf(h, pdf)
        n = gf.paginas(pdf)
        if n != len(doc["paginas"]): print(f"⚠ {doc['archivo']}: {n} páginas (se esperaban {len(doc['paginas'])})")
        shutil.copy(pdf, os.path.join(ROOT, "assets/pdf", doc["archivo"]))
        print(f"✔ {doc['archivo']} ({n} pág.)")

if __name__ == "__main__":
    main()
