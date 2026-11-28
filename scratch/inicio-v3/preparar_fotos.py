#!/usr/bin/env python3
"""Copia las fotos elegidas a fotos/ en webp y SIN metadatos (las del celular pueden traer ubicación),
y arma las versiones sin fondo de los logos de Subaru y YPF. No toca assets/."""
import base64, io, re, subprocess, tempfile
from pathlib import Path
from PIL import Image, ImageOps, ImageDraw

AQUI = Path(__file__).resolve().parent
ROOT = AQUI.parent.parent
JOSAM = Path.home() / 'Documents/apps/trivium-erp/video/public/anuncios/josam'

# Fotos ORIGINALES del blog anterior, recuperadas del historial de git (eran las imágenes destacadas antes de
# reemplazarlas por portadas). nombre: (blob, recorte x0, y0, x1, y1). El recorte saca la marca de agua
# vieja "Trivium Center"; no se retoca ni se rellena nada.
DEL_BLOG = {
    'capacitacion-pons': ('f34879a868f07e9aedc099c9812094670752e649', (0, 0, 1, 1)),
    'puesta-en-marcha': ('8bd731b2cc5c437dcc8339926f9f7cca3c45afe3', (0, 0, 1, 1)),
    'josam-mendoza': ('85b4e0ef369b1f20b33c176a799400606b0bb35b', (0, 0, 1, 0.815)),
    'josam-rueda': ('53d674207eda87078c8d90f673bc70204f48b9b3', (0, 0, 1, 0.815)),
    'repuestera': ('0eb0e1f5c5cd3e700bf27612f05acaa1ecde5c84', (0, 0.165, 1, 1)),
    'elevador-rotary': ('07de7d5261f7b15d1f6c8de793cefc997393d2ed', (0, 0, 1, 0.775)),
    'capacitacion-rodavial': ('5e5415ee913dc3ca19749ce3fd6238d1b4167ab5', (0, 0, 1, 0.825)),
    'elevador-pickup': ('49045b094b383dc42c19972c8e694a75531cb3c7', (0, 0, 1, 1)),
    'colectivos': ('ccec77216d2392fae9cee53c04fd61fb3b40105b', (0, 0, 1, 0.825)),
    'punto-flash': ('f3175c752f23005ae25e27a65cd6642948fae87e', (0, 0, 1, 0.805)),
    'lions-group': ('e219cd582c860ac4bba94401ba6f199afc93246f', (0, 0, 1, 0.815)),
    'bahia-alineacion': ('1990c0aafbc494107d72da7181a57c23a1668ca4', (0, 0.165, 1, 1)),
    'piso-elevador': ('a77a29054fc2195cab8c3c896e6a72857e132d3e', (0, 0, 1, 0.81)),
    'target-3d': ('a1349b1fdf052f5ee3cdb1f31d24aad81bc90390', (0, 0, 1, 1)),
    'geometria': ('3f7060a9c18950b6accdfbd8106b81927dbf6860', (0, 0, 1, 0.81)),
    'runflat': ('73063907ed787896de01590d4a3a33dd4be107b5', (0, 0, 0.72, 1)),
    'arguello-alineacion': ('2da9d2f8ed269c226e90a32f163c66bbc4be3ca7', (0, 0, 1, 1)),
    'arguello-fachada': ('9dbdd2c5a786f74674f3c759833020878d447083', (0, 0, 1, 1)),
}

for viejo in (AQUI / 'fotos').glob('*.webp'):
    viejo.unlink()
for nombre, (blob, (x0, y0, x1, y1)) in DEL_BLOG.items():
    datos = subprocess.run(['git', '-C', str(ROOT), 'cat-file', 'blob', blob], check=True, capture_output=True).stdout
    im = Image.open(io.BytesIO(datos)).convert('RGB')
    im = im.crop((round(x0 * im.width), round(y0 * im.height), round(x1 * im.width), round(y1 * im.height)))
    limpia = Image.new('RGB', im.size); limpia.paste(im)   # sin metadatos
    limpia.save(AQUI / 'fotos' / f'{nombre}.webp', 'WEBP', quality=90)
    print(nombre, limpia.size)

# El video de la nota del eje desplazado: un cuadro de la toma real del cabezal.
cuadro = Path(tempfile.mkdtemp()) / 'c.png'
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-ss', '2.6', '-i', str(JOSAM / 'cabezal.mp4'), '-frames:v', '1', str(cuadro)], check=True)
Image.open(cuadro).convert('RGB').save(AQUI / 'fotos/josam-cabezal.webp', 'WEBP', quality=85)

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
