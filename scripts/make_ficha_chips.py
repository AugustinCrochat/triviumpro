#!/usr/bin/env python3
"""Genera los PNG de las insignias del encabezado de las fichas PDF (logo de marca,
sello de origen, marcado CE) con Chrome headless, a 4x, sobre fondo blanco.

Uso: python3 scripts/make_ficha_chips.py <carpeta_salida> [MODELO_ALI ...]
(con modelos ALI genera solo ali-<modelo>.png)
Crea: brand-<slug>.png, origin-<id>.png, ce.png (alto 26 pt aprox.; 1 pt = 4 px x 1.333)
"""
import os, subprocess, sys, tempfile, html

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
H = 28  # pt
SC = 4

def shot(body, w, h, out):
    tmp = tempfile.mkdtemp(); f = os.path.join(tmp, "c.html")
    open(f, "w", encoding="utf-8").write(
        f'<!doctype html><meta charset=utf-8><style>*{{margin:0;box-sizing:border-box}}body{{background:#fff;width:{w}px;height:{h}px;display:flex;align-items:center;justify-content:center;font-family:"Liberation Sans",Arial,sans-serif}}</style>{body}')
    subprocess.run(["google-chrome", "--headless", "--no-sandbox", "--disable-gpu", "--hide-scrollbars",
                    f"--window-size={w},{h}", f"--force-device-scale-factor={SC}", f"--screenshot={out}", f], check=True, capture_output=True)
    # recorte al contenido (el lienzo es más grande que la insignia) con un margen mínimo
    subprocess.run(["convert", out, "-fuzz", "1%", "-trim", "+repage", "-bordercolor", "white", "-border", "6", out], check=True)

def ali_chip(outdir, modelo):
    """Sello ALI Validated + modelo certificado (ALI exige el modelo junto al sello)."""
    logo = os.path.join(ROOT, "assets/img/iconos/ali-validated.png")
    body = (f'<div style="display:flex;align-items:center;gap:6px;border:1px solid #d6d6d6;border-radius:4px;padding:3px 7px">'
            f'<img src="file://{logo}" style="height:34px;width:auto">'
            f'<div style="display:flex;flex-direction:column;line-height:1.15"><span style="font-size:7px;color:#555">MODELO CERTIFICADO</span>'
            f'<b style="font-size:11px">{html.escape(modelo)}</b></div></div>')
    shot(body, 190, 60, os.path.join(outdir, f"ali-{modelo}.png"))


def main(outdir):
    os.makedirs(outdir, exist_ok=True)
    if len(sys.argv) > 2:
        for m in sys.argv[2:]:
            ali_chip(outdir, m)
        return
    px = H * 96 / 72  # alto en px CSS
    marcas = {s: os.path.join(ROOT, "assets/img/marcas", f) for s, f in
              [("rotary-lift", "logo-rotary-lift.svg"), ("hofmann", "logo-hofmann.svg"), ("direct-lift", "logo-direct-lift.svg"),
               ("forward-lift", "logo-forward-lift.svg"), ("challenger-lifts", "logo-challenger-lifts.svg")]}
    for s, path in marcas.items():
        shot(f'<img src="file://{path}" style="height:{px:.0f}px;width:auto;max-width:200px">', 260, int(px) + 12, os.path.join(outdir, f"brand-{s}.png"))
    for oid, flag, txt in [("made-in-usa", "usa.svg", "MADE IN USA"), ("made-in-italy", "italy.svg", "MADE IN ITALY"),
                           ("made-in-germany", "germany.svg", "MADE IN GERMANY"), ("made-in-sweden", "sweden.svg", "MADE IN SWEDEN"),
                           ("made-in-taiwan", "taiwan.svg", "MADE IN TAIWAN")]:
        p = os.path.join(ROOT, "assets/img/iconos/origen", flag)
        body = (f'<div style="border:1px solid #d6d6d6;border-radius:4px;padding:3px 5px;display:flex;flex-direction:column;align-items:stretch;gap:2px;width:78px">'
                f'<img src="file://{p}" style="width:100%;height:auto;box-shadow:0 0 0 1px rgba(0,0,0,.15)">'
                f'<span style="font-weight:800;font-size:7.5px;letter-spacing:.04em;text-align:center;white-space:nowrap">{html.escape(txt)}</span></div>')
        shot(body, 100, 90, os.path.join(outdir, f"origin-{oid}.png"))
    ce = os.path.join(ROOT, "assets/img/iconos/origen/ce.webp")
    shot(f'<img src="file://{ce}" style="height:{px:.0f}px;width:{px:.0f}px;object-fit:cover">', int(px) + 12, int(px) + 12, os.path.join(outdir, "ce.png"))
    print("✔ insignias en", outdir)

if __name__ == "__main__":
    main(sys.argv[1])
