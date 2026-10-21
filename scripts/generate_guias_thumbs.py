#!/usr/bin/env python3
"""Miniaturas 480x300 de /guias/ (assets/img/guias/<slug>.webp): foto(s) de producto sobre fondo gris claro."""
import os
from PIL import Image, ImageChops

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, "assets/img/productos/")
W, H = 480, 300
SPEC = {
    "balanceadoras-de-ruedas": ["balanceadora-de-ruedas-hofmann-geodyna-7200-para-gomeria"],
    "alineadoras-3d": ["alineadora-3d-para-autos-hofmann-geoliner-630"],
    "elevadores-para-taller": ["elevador-dos-columnas-rotary-lift-spoa10"],
    "desarmadoras-de-neumaticos": ["desarmadora-hofmann-monty-3300-24-con-desmontadora-de-neumaticos"],
    "equipar-una-gomeria": ["desarmadora-para-neumaticos-de-auto-y-camioneta-monfasica-24-pulgadas-trivium-pro",
                            "balanceadora-de-ruedas-s901-trivium-pro"],
    "equipos-de-taller-economicos": ["elevador-dos-columnas-4-toneladas-trivium-pro-monofasico"],
}

def load(name):
    im = Image.open(P + name + ".webp").convert("RGB")
    d = ImageChops.difference(im, Image.new("RGB", im.size, (255, 255, 255))).convert("L").point(lambda v: 255 if v > 14 else 0)
    return im.crop(d.getbbox()) if d.getbbox() else im

os.makedirs(os.path.join(ROOT, "assets/img/guias"), exist_ok=True)
for slug, names in SPEC.items():
    canvas = Image.new("RGB", (W, H), (255, 255, 255))
    ims = [load(n) for n in names]
    slot = W // len(ims)
    for i, im in enumerate(ims):
        im.thumbnail((slot - 24, H - 24), Image.LANCZOS)
        canvas.paste(im, (i * slot + (slot - im.width) // 2, (H - im.height) // 2))
    canvas.save(os.path.join(ROOT, f"assets/img/guias/{slug}.webp"), "WEBP", quality=85)
    print("✔", slug)
