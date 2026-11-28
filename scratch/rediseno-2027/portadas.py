#!/usr/bin/env python3
"""BOCETO de portadas de blog (1100x600), dos propuestas. No toca assets/img/blog.
Uso: python3 scratch/rediseno-2027/portadas.py   -> portadas/{a,b}-N.webp y portadas.html"""
import html, json, os, subprocess, sys, tempfile
from pathlib import Path
from PIL import Image

AQUI = Path(__file__).resolve().parent
ROOT = AQUI.parent.parent
sys.path.insert(0, str(ROOT / 'scripts'))
from generate_blog_thumbs import SPEC, P, trim

CUANTAS = 9   # las notas más nuevas, para que el boceto del blog quede completo
LOGO = (ROOT / 'assets/img/logo-trivium.svg').as_uri()
BASE = """<!doctype html><meta charset="utf-8"><link href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@62..125,100..900&display=swap" rel="stylesheet">
<style>*{margin:0;padding:0;box-sizing:border-box}body{width:1100px;height:600px;position:relative;overflow:hidden;font-family:Archivo,sans-serif;color:#12171b}
.fotos{position:absolute;display:flex;align-items:center;justify-content:center;gap:14px}
.fotos img{object-fit:contain;mix-blend-mode:multiply;min-width:0;flex:1;height:100%;width:100%}
h1{font-stretch:118%;font-weight:800;letter-spacing:-.015em;line-height:1.04}
.cat{font-stretch:76%;font-weight:700;letter-spacing:.05em;text-transform:uppercase}</style>"""


def plano(cat, titulo, sub, imgs, fs):
    """A: lámina técnica clara, con línea de cota y rótulo."""
    return BASE + f"""<style>body{{background:#fff}}
.marco{{position:absolute;inset:22px;border:2px solid #12171b}}
.col{{position:absolute;left:22px;top:22px;width:586px;height:556px;border-right:2px solid #12171b}}
.txt{{position:absolute;left:36px;top:40px;width:522px}}
h1{{font-size:{fs}px}}
.cota{{height:28px;margin:26px 0 14px;width:522px;position:relative}}
.cota i{{position:absolute;left:0;right:0;top:13px;height:3px;background:#ff1e00}}
.cota:before,.cota:after{{content:'';position:absolute;top:0;width:3px;height:28px;background:#ff1e00}}.cota:before{{left:0}}.cota:after{{right:0}}
.cota b{{position:absolute;left:0;top:0;width:100%;height:28px;background:linear-gradient(45deg,transparent 0)}}
.sub{{font-size:31px;line-height:1.25;color:#434d55;font-weight:500}}
.rot{{position:absolute;left:0;bottom:0;width:100%;height:86px;border-top:2px solid #12171b;display:flex}}
.rot>div{{display:flex;align-items:center;padding:0 28px}}
.rot .l{{border-right:2px solid #12171b}}.rot img{{height:44px}}.rot .cat{{font-size:25px;line-height:1.1}}
.fondo{{position:absolute;left:608px;top:24px;width:468px;height:552px;background:#fff}}
.fotos{{left:634px;top:56px;width:420px;height:488px}}</style>
<div class="fondo"></div><div class="fotos">{imgs}</div><div class="marco"></div>
<div class="col"><div class="txt"><h1>{titulo}</h1><div class="cota"><i></i></div><p class="sub">{sub}</p></div>
<div class="rot"><div class="l"><img src="{LOGO}"></div><div><span class="cat">{cat}</span></div></div></div>"""


def banda(cat, titulo, sub, imgs, fs):
    """B: el equipo grande arriba y el título en una banda oscura."""
    return BASE + f"""<style>body{{background:#eceeed}}
.fotos{{left:250px;top:26px;width:820px;height:344px}}
.cat{{position:absolute;left:52px;top:42px;font-size:24px;width:220px;line-height:1.15;border-top:5px solid #ff1e00;padding-top:14px}}
.b{{position:absolute;left:0;bottom:0;width:100%;height:206px;background:#12171b;color:#fff;display:flex;align-items:center;gap:40px;padding:0 52px}}
.b div{{flex:1}}h1{{font-size:{round(fs*.84)}px}}.sub{{font-size:23px;color:#c9d1d6;margin-top:12px;line-height:1.25}}
.b img{{height:64px}}</style>
<div class="fotos">{imgs}</div><div class="cat">{cat}</div>
<div class="b"><div><h1>{titulo}</h1><p class="sub">{sub}</p></div><img src="{LOGO}"></div>"""


def main():
    posts = json.loads((ROOT / 'data/blog.json').read_text(encoding='utf-8'))
    salida = AQUI / 'portadas'; salida.mkdir(exist_ok=True)
    tmp = Path(tempfile.mkdtemp())
    hechas = []
    nuevas = sorted(posts, key=lambda x: x.get('date', ''), reverse=True)[:CUANTAS]
    for n, p in enumerate(nuevas):
        clave = max((k for k in SPEC if p['slug'].startswith(k)), key=len)
        kicker, titulo, sub, nombres = SPEC[clave]
        imgs = ''
        for j, nom in enumerate(nombres):
            origen = ROOT / (nom[1:] if nom.startswith('@') else P + nom + '.webp')
            dst = tmp / f'{n}_{j}.png'; trim(str(origen), str(dst))
            imgs += f'<img src="{dst.as_uri()}">'
        fs = 60 if len(titulo) <= 28 else 54 if len(titulo) <= 38 else 47
        for letra, fn in (('a', plano), ('b', banda)):
            h = tmp / f'{letra}{n}.html'; png = tmp / f'{letra}{n}.png'
            h.write_text(fn(html.escape(kicker), html.escape(titulo), html.escape(sub), imgs, fs), encoding='utf-8')
            subprocess.run(['google-chrome', '--headless=new', '--disable-gpu', '--hide-scrollbars', '--allow-file-access-from-files',
                            '--window-size=1100,600', '--virtual-time-budget=8000', f'--screenshot={png}', h.as_uri()],
                           check=True, capture_output=True)
            Image.open(png).convert('RGB').save(salida / f'{letra}-{n}.webp', 'WEBP', quality=88)
        hechas.append(p['slug'])
        print('✔', p['slug'])
    (salida / 'muestras.json').write_text(json.dumps(hechas), encoding='utf-8')
    bloque = lambda l, t, d: (f'<h2>{t}</h2><p>{d}</p><div class="g">' +
                              ''.join(f'<img src="portadas/{l}-{i}.webp" alt="">' for i in range(len(hechas))) + '</div>')
    (AQUI / 'portadas.html').write_text(
        '<!doctype html><html lang="es"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Boceto · Portadas</title>'
        '<style>body{font-family:Archivo,Arial,sans-serif;max-width:1240px;margin:0 auto;padding:24px 16px;background:#cfd3d5;color:#12171b}'
        '.g{display:grid;grid-template-columns:repeat(auto-fit,minmax(360px,1fr));gap:18px;margin-bottom:48px}img{width:100%;height:auto;display:block}</style>'
        + bloque('a', 'Propuesta A · Lámina', 'Clara, con marco, línea de cota y rótulo, como un plano.')
        + bloque('b', 'Propuesta B · Banda', 'El equipo grande sobre gris y el título en una banda oscura.') + '</html>', encoding='utf-8')


if __name__ == '__main__':
    main()
