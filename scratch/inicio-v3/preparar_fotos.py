#!/usr/bin/env python3
"""Copia las fotos elegidas a fotos/ en webp y SIN metadatos (las del celular pueden traer ubicación),
y arma las versiones sin fondo de los logos de Subaru y YPF. No toca assets/."""
import base64, io, re, subprocess, tempfile
from pathlib import Path
from PIL import Image, ImageOps, ImageDraw

AQUI = Path(__file__).resolve().parent
ROOT = AQUI.parent.parent
CASA = Path.home()
LOCAL = CASA / 'Documents/apps/neumaticos-trivium/public/images/local'
JOSAM = CASA / 'Documents/apps/trivium-erp/video/public/anuncios/josam'
BAJADAS = CASA / 'Downloads'

FOTOS = {   # nombre: (origen, segundo del video o None)
    'instalacion-elevador': (ROOT / 'assets/img/servicios/instalacion-elevador.webp', None),
    'josam-camion': (JOSAM / 'entrada.mp4', 2.0),
    'josam-cabezal': (JOSAM / 'cabezal.mp4', 2.6),
    'taller-completo': (LOCAL / 'taller-de-gomeria-con-cuatro-autos-neumaticos-trivium-arguello-cordoba.webp', None),
    'alineacion-3d-target': (LOCAL / 'target-alineadora-rueda-auto-elevador-trivium-cordoba.webp', None),
    'balanceo-camioneta': (LOCAL / 'cambio-de-cubiertas-en-camioneta-pickup-con-balanceadora-hofmann-trivium-cordoba.webp', None),
    'alineacion-utilitario': (LOCAL / 'balanceadora-y-alineadora-utilitario-taller-trivium-cordoba.webp', None),
    'colocando-target': (BAJADAS / 'geoliner 630/PXL_20260630_142830992.jpg', None),
    'desarmadora': (BAJADAS / 'PXL_20260820_133021993.mp4', 70.6),
    'balanceadora': (LOCAL / 'tecnico-balanceando-rueda-balanceadora-trivium-cordoba.webp', None),
    'fachada': (LOCAL / 'fachada-local-neumaticos-trivium-cordoba.webp', None),
    'posventa': (ROOT / 'assets/img/servicio-posventa-trivium.webp', None),
}

for nombre, (origen, seg) in FOTOS.items():
    if seg is not None:
        cuadro = Path(tempfile.mkdtemp()) / 'c.png'
        subprocess.run(['ffmpeg', '-y', '-v', 'error', '-ss', str(seg), '-i', str(origen), '-frames:v', '1', str(cuadro)], check=True)
        origen = cuadro
    im = ImageOps.exif_transpose(Image.open(origen)).convert('RGB')
    im.thumbnail((1600, 1600))
    limpia = Image.new('RGB', im.size); limpia.paste(im)
    limpia.save(AQUI / 'fotos' / f'{nombre}.webp', 'WEBP', quality=82)
    print(nombre, limpia.size)

# Subaru: imagen incrustada con fondo blanco -> transparente sólo el blanco conectado al borde
svg = (ROOT / 'assets/img/clientes/logo-subaru-inchcape.svg').read_text()
im = Image.open(io.BytesIO(base64.b64decode(re.search(r'base64,([^"]+)', svg)[1]))).convert('RGBA')
marco = ImageOps.expand(im, 1, (255, 255, 255, 255))
ImageDraw.floodfill(marco, (0, 0), (255, 255, 255, 0), thresh=40)
im = marco.crop((1, 1, marco.width - 1, marco.height - 1))
im.crop(im.getbbox()).save(AQUI / 'logos/logo-subaru.webp', 'WEBP', lossless=True)

# YPF: se saca el rectángulo azul y las letras pasan a azul
svg = (ROOT / 'assets/img/clientes/logo-ypf.svg').read_text()
svg, n = re.subn(r'<path[^>]*id="path1246"[^>]*>(</path>)?', '', svg)
assert n == 1 and 'fill:#ffffff' in svg
(AQUI / 'logos/logo-ypf.svg').write_text(svg.replace('fill:#ffffff', 'fill:#005090'))
