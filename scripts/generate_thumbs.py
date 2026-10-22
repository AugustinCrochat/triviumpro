#!/usr/bin/env python3
"""Miniaturas para las tarjetas (categorías, buscador, listado del blog).

Las tarjetas muestran la foto a ~180-360 px; con la original de 1200 px una
categoría descarga >1 MB de más. Genera assets/img/productos/t/ y
assets/img/blog/t/ (webp). site.js usa la miniatura y cae a la original si no existe.
"""
import os
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JOBS = [('assets/img/productos', 480), ('assets/img/blog', 640)]

for d, w in JOBS:
    src, dst = os.path.join(ROOT, d), os.path.join(ROOT, d, 't')
    os.makedirs(dst, exist_ok=True)
    for f in sorted(os.listdir(src)):
        if not f.lower().endswith('.webp'):
            continue
        out = os.path.join(dst, f)
        if os.path.exists(out) and os.path.getmtime(out) >= os.path.getmtime(os.path.join(src, f)):
            continue
        im = Image.open(os.path.join(src, f))
        if im.width > w:
            im = im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)
        im.save(out, 'WEBP', quality=82, method=6)
        print('✔', d + '/t/' + f)
