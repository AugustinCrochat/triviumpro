#!/usr/bin/env python3
"""Rehace la página 2 de la ficha PDF de la Geoliner 630 (la ficha se había armado a mano y no tenía fuente).
La página 1 se conserva tal cual del PDF actual. 28/11: el equipo ya no incluye impresora (texto y foto) y usa garras AC200.

Uso: python3 scripts/ficha_630_pagina2.py   y después   python3 scripts/set_ficha_metadata.py <pdf>
"""
import os, shutil, subprocess, tempfile
import generate_fichas as g

ROOT, E = g.ROOT, g.E
PDF = os.path.join(ROOT, "assets/pdf/ficha-tecnica-alineadora-3d-hofmann-geoliner-630.pdf")
IMG = os.path.join(ROOT, "assets/img/fichas/geoliner-630")
SITE = "https://pro.trivium.ar"

TARJETAS = [
    (7, "travesano-inclinable.jpg", "Travesaño inclinable por control remoto", "La inclinación del travesaño se regula con control remoto, para dejar las cámaras en posición óptima según el vehículo y la altura del elevador."),
    (8, "poco-espacio.jpg", "Poco espacio en el taller", "Equipo compacto con espacio de guardado para las tarjetas (targets). Travesaño y columnas integrados a la consola."),
    (9, "nube.jpg", "Servicios en la nube", "Los datos se guardan en un servidor seguro: los informes se consultan en forma remota y se envían por mail al cliente."),
]
SPECS = [("Modelo", "geoliner® 630"), ("Código de fabricante", "EEWA721G"), ("Tipo", "3D · travesaño cruzado"),
         ("Diámetro de llanta (garras AC200)", "12\" – 24\" (30 – 61 cm)"), ("Ancho de vía", "48\" – 96\" (122 – 244 cm)"),
         ("Base de rueda", "79\" – 180\" (201 – 457 cm)"), ("Alimentación", "110 – 240 V · 50/60 Hz"),
         ("Peso de envío", "227 kg (501 lbs)"), ("Pantalla secundaria", "Compatible con tablet")]
ACCESORIOS = [
    ("Incluidos", ["Garras para ruedas AC200 con tarjetas 3D", "Fijador del volante", "Depresor del pedal del freno", "Dos cuñas para rueda"]),
    ("Opcionales", ["ROMESS"]),
    ("Software y conectividad", ["Acceso rápido al historial del vehículo desde el inicio", "Un año de especificaciones incluido; actualizaciones y suscripciones de 1 a 5 años",
                                 "Diagnóstico remoto para el servicio técnico", "Requiere conexión inalámbrica a Internet provista por el cliente"]),
]
PROCEDIMIENTOS = ["Brazo A (A-arm)", "Biela de dirección (drag link)", "Barra de dirección individual", "Ángulo de chasis", "SAI (inclinación del eje de dirección)",
                  "Divergencia en giro", "Giro máximo", "Compensación en elevado", "EZ-TOE", "Altura de conducción manual / a demanda / TIP",
                  "Calculadora de repuestos", "Asistencia de ajustes Mitchell1®"]
CSS = """
.page{height:297mm;padding:10.5mm 12mm 4.5mm}.top .lg{height:9mm}.top .chips a:first-child img{height:10.5mm!important;max-width:46mm!important}.top .chips a+a img{height:13mm!important}
.tj{display:flex;gap:5mm}.tj>div{flex:1}.tj img{width:100%;height:auto;border-radius:1.6mm;display:block;margin-bottom:2mm}
.tj .f{margin:0;align-items:center}.tj .f b{line-height:1.15}.tj p{margin:1.2mm 0 0;font-size:8.2pt;color:#444;line-height:1.35}
.cols{margin-top:2mm}.caja-sp{background:#f3f3f3;border-radius:2mm;padding:2mm 3mm}.caja-sp tr td{background:none;border-bottom:.2mm solid #ddd;padding:2mm 1mm}.caja-sp tr:last-child td{border:0}
h4{margin:0 0 1.2mm;font-size:8.6pt}ul{list-style:none;padding:0;margin:0 0 2.6mm}li{font-size:8.1pt;color:#333;line-height:1.3;margin-bottom:1.1mm;padding-left:4mm;position:relative}
li:before{content:"";position:absolute;left:0;top:1.1mm;width:1.5mm;height:1.5mm;border-radius:50%;background:#c8102e}
.pr{display:flex;flex-wrap:wrap;gap:1.6mm}.pr span{background:#f3f3f3;border-radius:1.2mm;padding:1.2mm 2.4mm;font-size:7.8pt}
.fin{margin-top:4mm}.num{text-align:right;font-size:7.3pt;color:#555;margin-top:1mm}
"""

def pagina2():
    chips = (f'<a href="{SITE}/marca/hofmann/"><img src="file://{ROOT}/assets/img/marcas/logo-hofmann.{ext()}" style="height:8mm;max-width:34mm"></a>'
             f'<a href="{SITE}/origen/estados-unidos/"><img src="file://{g.BUILD}/origin-made-in-usa.png" style="height:12mm"></a>')
    tarjetas = "".join(f'<div><img src="file://{IMG}/{f}" alt="{E(t)}"><div class="f"><span class="n">{n}</span><div><b>{E(t)}</b></div></div><p>{E(x)}</p></div>' for n, f, t, x in TARJETAS)
    specs = "".join(f"<tr><td>{E(a)}</td><td>{E(b)}</td></tr>" for a, b in SPECS)
    acc = "".join(f"<h4>{E(t)}</h4><ul>" + "".join(f"<li>{E(i)}</li>" for i in items) + "</ul>" for t, items in ACCESORIOS)
    proc = "".join(f"<span>{E(x)}</span>" for x in PROCEDIMIENTOS)
    cajas = (f'<a href="{SITE}/"><img class="lgp" src="file://{ROOT}/assets/img/marcas/logo-trivium-pro.svg" alt="Trivium Pro"></a>'
             f'<a class="caja" href="{SITE}/producto/alineadora-3d-hofmann-geoliner-630/">{g.svg_inline("globo.svg", "ic")}pro.trivium.ar</a>'
             f'<a class="caja" href="mailto:info@trivium.ar">{g.svg_inline("mail.svg", "ic")}info@trivium.ar</a>'
             f'<a class="caja w" href="https://wa.me/5491127015294">{g.WA}+54 9 11 2701-5294</a>')
    flag = f'<a class="caja o" href="{SITE}/origen/estados-unidos/">Origen: {g.svg_inline("usa.svg", "fl")}Estados Unidos</a>'
    return f"""<!doctype html><html lang="es"><head><meta charset="utf-8"><title>Ficha técnica Geoliner 630</title><style>{g.CSS}{CSS}</style></head><body><div class="page">
<div class="top"><a href="{SITE}/"><img class="lg" src="file://{ROOT}/assets/img/marcas/logo-trivium-pro.svg" alt="Trivium Pro"></a><div class="chips">{chips}</div><span>FICHA TÉCNICA</span></div>
<div class="main"><div class="kick">Alineadoras · Hofmann</div><h1>Geoliner 630 · continuación</h1>
<h3>Más características</h3><div class="tj">{tarjetas}</div>
<div class="cols"><div><h3>Especificación técnica</h3><div class="caja-sp"><table>{specs}</table></div></div><div><h3>Accesorios</h3>{acc}</div></div>
<h3>Procedimientos y mediciones del software</h3><div class="pr">{proc}</div>
<div class="fin"><b>Financiación disponible:</b> consultá planes de pago. Pedí tu cotización en <a href="{SITE}/contacto/">pro.trivium.ar/contacto</a> para empezar.</div></div>
<div class="foot3"><div><b>Instalación en tu taller</b>Contamos con un equipo de técnicos para la colocación de tu equipo, en todo el país.</div><div><b>Servicio técnico oficial</b>Garantía y servicio técnico oficial en todo el país.</div><div><b>Repuestos originales</b>Stock permanente con garantía de trazabilidad.</div></div>
<div class="ft"><div class="cajas">{cajas}</div>{flag}</div><div class="num">Página 2 de 2</div></div></body></html>"""

def ext():
    return next(e for e in ("svg", "webp", "png") if os.path.exists(os.path.join(ROOT, f"assets/img/marcas/logo-hofmann.{e}")))

if __name__ == "__main__":
    os.makedirs(g.BUILD, exist_ok=True); g.mc.main(g.BUILD)
    with tempfile.TemporaryDirectory() as t:
        h, p2, p1, junto = (os.path.join(t, n) for n in ("p2.html", "p2.pdf", "p1.pdf", "junto.pdf"))
        open(h, "w", encoding="utf-8").write(pagina2()); g.chrome_pdf(h, p2)
        assert g.paginas(p2) == 1, "la página 2 se desbordó"
        subprocess.run(["pdfseparate", "-f", "1", "-l", "1", PDF, p1], check=True)
        subprocess.run(["gs", "-q", "-dNOPAUSE", "-dBATCH", "-sDEVICE=pdfwrite", "-dPDFSETTINGS=/printer", "-dColorImageResolution=200", f"-sOutputFile={junto}", p1, p2], check=True)
        shutil.copy(junto, PDF)
    print("✔", os.path.relpath(PDF, ROOT))
