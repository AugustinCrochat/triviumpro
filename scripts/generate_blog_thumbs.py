#!/usr/bin/env python3
"""Genera las portadas 1100x600 del blog (barra roja, título, logo Trivium Pro y foto de producto).

Escribe en assets/img/blog/<slug>.webp. Las 4 notas de Oct-2026 y la de ALI se hicieron igual;
este script las unifica a todas. Requiere Chrome (headless) y Pillow.
Uso: python3 scripts/generate_blog_thumbs.py [slug-prefijo ...]
"""
import html, os, subprocess, sys, tempfile
from PIL import Image, ImageChops

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = "assets/img/productos/"

# slug-prefijo: (kicker, título, subtítulo, [imágenes de producto])
SPEC = {
 "hofmann-geoliner-880": ("NOVEDAD · HOFMANN", "Hofmann Geoliner 880", "Alineadora 3D de paso directo con IA", ["alineadora-3d-hofmann-geoliner-880"]),
 "como-centrar-una-rueda": ("GUÍA TÉCNICA · BALANCEO", "Cómo centrar una rueda en la balanceadora", "Conos, tuercas rápidas y adaptadores", ["set-de-4-conos-de-centrado-haweka", "tuerca-rapida-progrip-haweka"]),
 "mantenimiento-de-un-elevador": ("GUÍA TÉCNICA · ELEVADORES", "Mantenimiento de un elevador de taller", "Checklist diario, mensual y anual", ["elevador-dos-columnas-rotary-lift-spoa10"]),
 "que-compresor-y-red-de-aire": ("GUÍA TÉCNICA · AIRE COMPRIMIDO", "Qué compresor y qué red de aire necesita tu taller", "Caudal, presión y red de cañerías", ["llave-pistola-neumatica-de-impacto-kuani-ki-1481"]),
 "instalamos-tres-elevadores": ("INSTALACIÓN · ELEVADORES", "Tres elevadores para Punto Flash", "Instalación de elevadores de dos columnas", ["elevador-dos-columnas-4-toneladas-trivium-pro-monofasico"]),
 "que-tipo-de-elevador-elegir": ("GUÍA TÉCNICA · ELEVADORES", "Qué elevador elegir para cambio de aceite", "Cómo elegir según tu lubricentro", ["elevador-tijera-corto-3-toneladas-trivium-pro-e30-monofasico"]),
 "servicios-integrales": ("SERVICIOS · TODO EL PAÍS", "Servicios integrales para tus máquinas", "Instalación, mantenimiento y más en toda Argentina", ["@assets/img/servicio-posventa-trivium.webp"]),
 "geoliner-630": ("PRODUCTO · ALINEADORAS", "Geoliner 630", "La alineadora 3D compacta que revoluciona los talleres", ["alineadora-3d-para-autos-hofmann-geoliner-630"]),
 "la-importancia-del-mantenimiento": ("CASO DE ÉXITO · MANTENIMIENTO", "Mantenimiento preventivo en equipos de taller", "Caso exitoso: Lions Group", ["elevador-dos-columnas-rotary-lift-spoa10"]),
 "especificaciones-del-piso": ("GUÍA TÉCNICA · INSTALACIÓN", "El piso para un elevador de dos columnas", "Especificaciones para la instalación", ["elevador-dos-columnas-rotary-lift-spoa10-trio"]),
 "geometria-de-ruedas": ("GUÍA TÉCNICA · ALINEACIÓN", "Geometría de ruedas", "Todo lo que necesitás saber para mantener tu vehículo", ["alineadora-3d-para-autos-hofmann-geoliner-609"]),
 "instalamos-una-josam": ("INSTALACIÓN · ALINEADORAS", "Josam CV-Aligner en Mendoza", "Tecnología Snap-on para alinear vehículos pesados", ["alineadora-para-camiones-con-tecnologia-de-camara-josam-cv-aligner"]),
 "equipamiento-completo-para-repuestera": ("INSTALACIÓN · TRIVIUM PRO", "Repuestera del Milagro", "Nueva instalación Trivium Pro en Las Lajitas, Salta", ["balanceadora-con-pantalla-y-puntero-laser-g66"]),
 "errores-comunes": ("GUÍA TÉCNICA · BALANCEO", "Errores comunes al usar una balanceadora", "Y cómo evitarlos", ["balanceadora-de-ruedas-hofmann-geodyna-7200-para-gomeria"]),
 "como-se-alinea": ("GUÍA TÉCNICA · ALINEACIÓN", "¿Cómo se alinea un vehículo con una alineadora 3D?", "Guía de alineación 3D", ["alineadora-3d-para-autos-hofmann-geoliner-609"]),
 "hofmann-y-john-bean": ("MARCAS · HOFMANN · JOHN BEAN", "Hofmann y John Bean", "Dos marcas, una misma tecnología", ["alineadora-3d-hofmann-geoliner-880"]),
 "por-que-es-tan-importante": ("GUÍA TÉCNICA · ALINEADORAS", "Mantené actualizada tu alineadora", "Hofmann y John Bean", ["alineadora-3d-para-autos-hofmann-geoliner-630"]),
 "por-que-elegir-un-elevador": ("GUÍA TÉCNICA · ELEVADORES", "Brazos All-Vehicle de Rotary Lift", "Por qué elegir un elevador con brazos All-Vehicle", ["elevador-dos-columnas-spo55"]),
 "para-que-sirve-el-brazo": ("GUÍA TÉCNICA · DESARMADORAS", "El brazo auxiliar de la desarmadora", "Para qué sirve en neumáticos run-flat", ["brazo-auxiliar-para-neumaticos-run-flat-y-de-talon-bajo"]),
 "alineacion-de-colectivos": ("CASO · ALINEACIÓN DE PESADOS", "Alineación de colectivos", "Tecnología sueca: Josam CV-Aligner", ["alineadora-para-camiones-con-tecnologia-de-camara-josam-cv-aligner"]),
 "formacion-tecnica": ("CAPACITACIÓN · ALINEADORAS", "Formación técnica en Geoliner 630", "Neumáticos Pons – Córdoba", ["alineadora-3d-para-autos-hofmann-geoliner-630"]),
 "cuanto-espacio-dejar": ("GUÍA TÉCNICA · INSTALACIÓN", "Espacio entre alineadora y elevador", "Recomendaciones para una instalación óptima", ["elevador-tijera-largo-con-kit-de-alineacion"]),
 "la-importancia-de-balancear": ("GUÍA TÉCNICA · BALANCEO", "La importancia de balancear ruedas", "Beneficios clave para talleres y gomerías", ["balanceadora-de-ruedas-hofmann-geodyna-7600p"]),
 "ventajas-de-la-alineacion-de-camiones": ("GUÍA TÉCNICA · PESADOS", "Alineación de camiones", "Ventajas para empresas de mantenimiento", ["alineadora-para-camiones-con-tecnologia-de-camara-josam-cv-aligner"]),
 "capacitacion-y-puesta": ("SERVICIO · ALINEADORAS", "Capacitación y puesta en marcha", "Alineadora Hofmann Geoliner 630", ["alineadora-3d-para-autos-hofmann-geoliner-630"]),
 "existen-diferencias-reales": ("MARCAS · HOFMANN · JOHN BEAN", "Hofmann vs. John Bean", "¿Existen diferencias reales entre sus máquinas?", ["balanceadora-de-ruedas-hofmann-geodyna-9000p"]),
 "elevador-de-4-columnas-vs": ("GUÍA TÉCNICA · ELEVADORES", "4 columnas vs. tijera larga", "Cuál elegir para alineación", ["elevador-4-columnas-unite-pl-fs50", "elevador-tijera-largo-con-kit-de-alineacion"]),
 "balanceadoras-de-ruedas-con": ("GUÍA TÉCNICA · BALANCEO", "Balanceadoras: con o sin monitor", "Cuál elegir", ["balanceadora-con-pantalla-y-puntero-laser-g66", "balanceadora-de-ruedas-s901-trivium-pro"]),
 "la-importancia-de-ofrecer": ("GUÍA TÉCNICA · SERVICIOS", "Rotación de neumáticos", "Un servicio para sumar en tu taller o gomería", ["elevador-tijera-4500-kg-pl45h-para-gomeria-rotacion-balanceo-trivium-pro"]),
 "como-funciona-la-alineacion-3d": ("GUÍA TÉCNICA · ALINEACIÓN", "Cómo funciona la alineación 3D", "Tecnología y beneficios", ["alineadora-3d-hofmann-geoliner-880"]),
 "autocalibracion": ("GUÍA TÉCNICA · BALANCEO", "Autocalibración de balanceadoras", "Qué es y por qué es importante", ["balanceadora-de-ruedas-hofmann-geodyna-7400l"]),
 "como-elegir-la-alineadora": ("GUÍA DE COMPRA · ALINEADORAS", "Cómo elegir la alineadora ideal", "Para tu taller", ["alineadora-3d-para-autos-hofmann-geoliner-609"]),
 "como-elegir-el-elevador": ("GUÍA DE COMPRA · ELEVADORES", "Elevador para hacer alineación", "Cómo elegir el adecuado", ["elevador-tijera-alineacion-forward-lift-nbs40a-48"]),
 "diferencias-entre-maquinas": ("GUÍA TÉCNICA · TALLER", "Motores monofásicos y trifásicos", "Ventajas de cada uno en las máquinas de taller", ["desarmadora-para-neumaticos-de-auto-y-camioneta-monfasica-24-pulgadas-trivium-pro"]),
 "diferencias-entre-elevadores": ("GUÍA DE COMPRA · ELEVADORES", "Piso libre vs. travesaño al piso", "Diferencias entre elevadores de 2 columnas", ["elevador-dos-columnas-cuatro-toneladas-piso-libre", "elevador-dos-columnas-4-toneladas-trivium-pro-monofasico"]),
 "entendiendo-la-configuracion": ("GUÍA TÉCNICA · PESADOS", "Qué es un camión 6×2", "Configuración y uso en Argentina", ["balanceadora-de-ruedas-para-camion-y-pesados-u850-150-kilos-trivium-pro"]),
 "como-manejar-un-taller": ("GUÍA PARA TALLERES", "Cómo manejar un taller de autos", "De forma eficiente", ["elevador-dos-columnas-rotary-lift-spoa10"]),
 "como-abrir-un-taller": ("GUÍA PARA EMPRENDEDORES", "Cómo abrir un taller de alineación y balanceo", "Equipos y pasos para empezar", ["alineadora-3d-para-autos-hofmann-geoliner-630", "balanceadora-de-ruedas-hofmann-geodyna-7200-para-gomeria"]),
 "como-funcionan-las-desarmadoras": ("GUÍA TÉCNICA · DESARMADORAS", "Desarmadoras para neumáticos run-flat", "Guía para talleres y gomerías", ["desarmadora-con-brazo-auxiliar-para-run-flat-1256-s-pro-trivium-center"]),
 "los-beneficios-de-tener": ("GUÍA TÉCNICA · ALINEADORAS", "Una alineadora en tu taller", "Beneficios para talleres y gomerías", ["alineadora-3d-para-autos-hofmann-geoliner-609"]),
 "alineadoras-5d": ("GUÍA TÉCNICA · ALINEACIÓN", "Alineadoras 5D", "El mito de las «dimensiones» en equipos de alineación", ["alineadora-3d-para-autos-hofmann-geoliner-630"]),
 "como-funciona-una-alineadora": ("GUÍA TÉCNICA · ALINEADORAS", "Cómo funciona una alineadora", "Y su importancia en talleres y gomerías", ["alineadora-3d-para-autos-hofmann-geoliner-609"]),
 "como-mantener-tu-desarmadora": ("GUÍA TÉCNICA · DESARMADORAS", "Mantené tu desarmadora", "Mantenimiento preventivo en óptimas condiciones", ["desarmadora-para-neumaticos-de-auto-y-camioneta-monfasica-24-pulgadas-trivium-pro"]),
 "por-que-incorporar": ("GUÍA DE COMPRA · BALANCEADORAS", "Una balanceadora para tu gomería", "Por qué es una decisión inteligente", ["balanceadora-de-ruedas-hofmann-geodyna-7100-para-gomeria"]),
 "como-instalar-una-gomeria": ("GUÍA PARA EMPRENDEDORES", "Cómo instalar una gomería", "Guía completa para emprender con éxito", ["desarmadora-hofmann-monty-1270-con-desmontadora-de-neumaticos", "balanceadora-de-ruedas-hofmann-geodyna-7200-para-gomeria"]),
 "como-empezar-un-lubricentro": ("BLOG · LUBRICENTROS", "Cómo empezar un lubricentro", "Equipamiento y recomendaciones clave", ["elevador-dos-columnas-6000-kg-vehiculos-electricos"]),
 "equipamiento-esencial": ("GUÍA PARA EMPRENDEDORES", "Equipamiento para tu taller de neumáticos", "Lo esencial para empezar", ["desarmadora-hofmann-monty-3300-20-con-desmontadora-de-neumaticos", "balanceadora-de-ruedas-hofmann-geodyna-7200-para-gomeria"]),
 "certificacion-ali": ("GUÍA TÉCNICA · ELEVADORES", "Certificación ALI", "Qué es y por qué importa al elegir un elevador", ["elevador-dos-columnas-challenger-lifts-vle10"]),
 "las-maquinas-del-taller": ("CASO · TRIVIUM ARGÜELLO", "Las máquinas del taller Trivium Argüello", "Alineación, arme y desarme, balanceo", ["alineadora-3d-para-autos-hofmann-geoliner-630"]),
 "es-rentable-una-gomeria-como-calcular-ganancias-": ("GUÍA DE NEGOCIO · GOMERÍAS", "¿Es rentable una gomería?", "Ingresos, costos y punto de equilibrio", ["elevador-tijera-4500-kg-pl45h-para-gomeria-rotacion-balanceo-trivium-pro", "balanceadora-con-pantalla-y-puntero-laser-g66"]),
 "es-rentable-un-lubricentro-como-calcular-la-gana": ("GUÍA DE NEGOCIO · LUBRICENTROS", "¿Es rentable un lubricentro?", "Ganancia por servicio y punto de equilibrio", ["elevador-tijera-corto-3-toneladas-trivium-pro-e30-monofasico"]),
 "es-rentable-un-taller-mecanico-como-calcular-gan": ("GUÍA DE NEGOCIO · TALLERES", "¿Es rentable un taller mecánico?", "Ganancias, costos y equipos necesarios", ["elevador-dos-columnas-4-toneladas-trivium-pro-monofasico"]),
 "es-rentable-un-taller-de-alineacion-y-balanceo-i": ("GUÍA DE NEGOCIO · ALINEACIÓN Y BALANCEO", "¿Es rentable un taller de alineación y balanceo?", "Inversión, retorno y punto de equilibrio", ["alineadora-3d-para-autos-hofmann-geoliner-630"]),
 "como-abrir-un-taller-de-frenos-equipamiento-serv": ("GUÍA DE NEGOCIO · TALLER DE FRENOS", "Cómo abrir un taller de frenos", "Equipamiento, servicios y rentabilidad", ["elevador-tijera-rotary-lift-baja-altura"]),
 "elevador-tijera-tipos-capacidades-y-cual-elegir-": ("GUÍA DE COMPRA · ELEVADORES TIJERA", "Elevador tijera: cuál elegir", "Tipos, capacidades y usos", ["elevador-tijera-largo-con-kit-de-alineacion"]),
 "elevador-tijera-movil-para-detailing-por-que-con": ("GUÍA DE COMPRA · DETAILING", "Elevador tijera móvil para detailing", "Por qué conviene y cómo elegirlo", ["elevador-tijera-portatil-trivium-pro-b30m"]),
 "como-montar-un-taller-de-detailing-equipamiento-": ("GUÍA DE NEGOCIO · DETAILING", "Cómo montar un taller de detailing", "Equipamiento y servicios que más rinden", ["rmr6"]),
 "elevador-tijera-de-sobrepiso-plancha-elevadora-p": ("GUÍA DE COMPRA · GOMERÍAS", "Plancha elevadora para gomería", "Elevador tijera de sobrepiso: ventajas y modelos", ["elevador-tijera-ultradelgado-unite-pl-b30y", "elevador-tijera-4500-kg-pl45h-para-gomeria-rotacion-balanceo-trivium-pro"]),
 "como-elegir-una-desarmadora-de-neumaticos-tipos-": ("GUÍA DE COMPRA · DESARMADORAS", "Cómo elegir una desarmadora de neumáticos", "Tipos, tamaños y modelos", ["desarmadora-para-neumaticos-de-auto-y-camioneta-monfasica-24-pulgadas-trivium-pro"]),
 "elevador-de-4-columnas-para-que-sirve-capacidade": ("GUÍA DE COMPRA · ELEVADORES 4 COLUMNAS", "Elevador de 4 columnas: para qué sirve", "Capacidades y cuándo conviene", ["elevador-4-columnas-unite-pl-fs50"]),
 "como-elegir-un-elevador-de-2-columnas-capacidad-": ("GUÍA DE COMPRA · ELEVADORES 2 COLUMNAS", "Cómo elegir un elevador de 2 columnas", "Capacidad, brazos y altura", ["elevador-dos-columnas-rotary-lift-spoa10"]),
 "servicios-para-sumar-ticket-en-una-gomeria-y-que": ("GUÍA DE NEGOCIO · GOMERÍAS", "Servicios para sumar ticket en tu gomería", "Qué ofrecer y qué equipos necesitás", ["balanceadora-de-ruedas-hofmann-geodyna-7600p"]),
 "como-equipar-un-taller-para-autos-electricos-e-h": ("GUÍA TÉCNICA · VEHÍCULOS ELÉCTRICOS", "Taller para autos eléctricos e híbridos", "Elevador, baterías y herramientas", ["elevador-dos-columnas-6000-kg-vehiculos-electricos", "elevador-de-baterias-para-autos-electricos"]),
 "como-montar-una-gomeria-para-camiones-y-vehiculo": ("GUÍA DE NEGOCIO · GOMERÍA DE CAMIONES", "Cómo montar una gomería para camiones", "Equipos necesarios para vehículos pesados", ["desarmadora-para-ruedas-de-camiones-monty-4250p", "balanceadora-para-ruedas-de-camion-geodyna-980l"]),
 "como-montar-un-taller-de-motos-elevador-y-equipa": ("GUÍA DE NEGOCIO · TALLER DE MOTOS", "Cómo montar un taller de motos", "Elevador y equipamiento necesario", ["elevador-para-moto-direct-lift-procycle-dt", "elevador-para-motos-mt07-trivium-center-454-kilos"]),
 "como-elegir-una-balanceadora-de-ruedas-capacidad": ("GUÍA DE COMPRA · BALANCEADORAS", "Cómo elegir una balanceadora de ruedas", "Capacidad, tecnología y modelos", ["balanceadora-de-ruedas-hofmann-geodyna-7400l"]),
 "cuanto-cuesta-un-elevador-para-taller-que-influy": ("GUÍA DE COMPRA · ELEVADORES", "¿Cuánto cuesta un elevador para taller?", "Qué influye en el precio y cómo comparar", ["elevador-dos-columnas-rotary-lift-spoa10", "elevador-tijera-corto-3-toneladas-trivium-pro-e30-monofasico"]),
 "rotary-lift-o-trivium-pro-que-linea-conviene-seg": ("GUÍA DE COMPRA · MARCAS", "Rotary Lift o Trivium Pro", "Qué línea conviene según tu taller", ["elevador-dos-columnas-rotary-lift-spoa10", "elevador-dos-columnas-4-toneladas-trivium-pro-monofasico"]),
 "trivium-center-ahora-es-trivium-pro-que-cambia-y": ("NOVEDADES · TRIVIUM PRO", "Trivium Center ahora es Trivium Pro", "Qué cambia y dónde encontrarnos", ["elevador-dos-columnas-4-toneladas-trivium-pro-monofasico"]),
 "que-equipos-necesita-un-taller-mecanico-lista-co": ("GUÍA PARA EMPRENDEDORES", "Equipos para un taller mecánico", "Lista completa por prioridad", ["elevador-dos-columnas-4-toneladas-trivium-pro-monofasico", "balanceadora-de-ruedas-hofmann-geodyna-7600p"]),
}

def trim(path, out):
    im = Image.open(path).convert("RGB")
    diff = ImageChops.difference(im, Image.new("RGB", im.size, (255, 255, 255))).convert("L").point(lambda v: 255 if v > 14 else 0)
    bb = diff.getbbox()
    if bb:
        pad = 4
        bb = (max(bb[0]-pad, 0), max(bb[1]-pad, 0), min(bb[2]+pad, im.width), min(bb[3]+pad, im.height))
        im = im.crop(bb)
    im.save(out)

def page(kicker, title, sub, imgs):
    n = len(title)
    fs = 56 if n <= 24 else 48 if n <= 38 else 42
    two = len(imgs) > 1
    ims = "".join(f'<img src="{i}">' for i in imgs)
    return f"""<!doctype html><html><head><meta charset="utf-8"><link href="https://fonts.googleapis.com/css2?family=Archivo:wght@500;800&display=swap" rel="stylesheet">
<style>*{{margin:0;padding:0;box-sizing:border-box}}body{{width:1100px;height:600px;position:relative;overflow:hidden;font-family:Archivo,Arial,sans-serif;background:#fff}}
.l{{position:absolute;left:0;top:0;width:600px;height:600px;background:linear-gradient(135deg,#fff,#f4f3f1)}}
.bar{{position:absolute;left:0;top:0;width:14px;height:600px;background:#ff2a00}}
.k{{position:absolute;left:64px;top:58px;color:#ff2a00;font-weight:800;font-size:16px;letter-spacing:.2em}}
.t{{position:absolute;left:64px;top:92px;width:510px;max-height:330px;font-size:{fs}px;line-height:1.08;font-weight:800;letter-spacing:-.02em;color:#111}}
.s{{margin-top:22px;width:500px;letter-spacing:0;font-size:24px;font-weight:500;color:#444;line-height:1.3}}
.logo{{position:absolute;left:252px;top:490px;width:130px;height:62px}}
.p{{position:absolute;left:630px;top:30px;width:440px;height:540px;display:flex;align-items:center;justify-content:center;gap:10px}}
.p img{{max-width:{'48%' if two else '100%'};max-height:{'70%' if two else '100%'};object-fit:contain}}</style></head><body>
<div class="l"></div><div class="bar"></div><div class="k">{html.escape(kicker)}</div>
<div class="t">{html.escape(title)}<div class="s">{html.escape(sub)}</div></div>
<img class="logo" src="logo.svg"><div class="p">{ims}</div></body></html>"""

def main():
    only = sys.argv[1:]
    import json
    posts = json.load(open(os.path.join(ROOT, "data/blog.json"), encoding="utf-8"))
    tmp = tempfile.mkdtemp()
    os.symlink(os.path.join(ROOT, "assets/img/logo-trivium.svg"), os.path.join(tmp, "logo.svg"))
    for p in posts:
        key = max((k for k in SPEC if p["slug"].startswith(k)), key=len, default=None)
        if not key or (only and not any(p["slug"].startswith(o) for o in only)):
            continue
        kicker, title, sub, imgs = SPEC[key]
        srcs = []
        for j, name in enumerate(imgs):
            src = os.path.join(ROOT, name[1:] if name.startswith("@") else P + name + ".webp")
            dst = os.path.join(tmp, f"{p['id']}_{j}.png")
            trim(src, dst); srcs.append(os.path.basename(dst))
        h = os.path.join(tmp, f"{p['id']}.html"); png = os.path.join(tmp, f"{p['id']}.png")
        open(h, "w", encoding="utf-8").write(page(kicker, title, sub, srcs))
        subprocess.run(["google-chrome", "--headless", "--no-sandbox", "--disable-gpu", "--hide-scrollbars",
                        "--window-size=1100,600", "--virtual-time-budget=5000", f"--screenshot={png}", h],
                       check=True, capture_output=True)
        Image.open(png).convert("RGB").save(os.path.join(ROOT, p["image"]), "WEBP", quality=85)
        print("✔", p["slug"])

if __name__ == "__main__":
    main()
