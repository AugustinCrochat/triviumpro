#!/usr/bin/env python3
"""BOCETOS sobre la web PUBLICADA (index.html): sólo cambian el hero (carrusel de fotos) y el carrusel de
clientes. Genera inicio-a.html, inicio-b.html, portadas/ y portadas.html. No modifica nada fuera de esta carpeta."""
import html, json, subprocess, sys, tempfile
from pathlib import Path
from PIL import Image

AQUI = Path(__file__).resolve().parent
ROOT = AQUI.parent.parent
sys.path.insert(0, str(ROOT / 'scripts'))
from generate_blog_thumbs import SPEC
F = 'scratch/inicio-v3/fotos/'
SEGUNDOS = 3.5

DIAPOS = [  # foto, trabajo, texto alternativo, encuadre
    ('instalacion-elevador', 'Instalación de elevadores', 'Dos técnicos ajustando la unidad hidráulica de un elevador', '70% 50%'),
    ('josam-cabezal', 'Alineación de camiones · Josam', 'Cabezal de medición Josam montado en la rueda de un camión', '50% 60%'),
    ('taller-completo', 'Equipamiento de gomería', 'Taller con elevadores, balanceadora y autos en trabajo', '50% 65%'),
    ('josam-camion', 'Alineación de camiones', 'Camión sobre la fosa de alineación', '50% 58%'),
    ('alineacion-3d-target', 'Alineación 3D', 'Rueda con el target de la alineadora 3D sobre un elevador', '50% 38%'),
    ('balanceo-camioneta', 'Balanceo de camioneta', 'Balanceo de ruedas de una camioneta', '55% 55%'),
    ('colocando-target', 'Montaje del cabezal de alineación', 'Técnico colocando el soporte de alineación en una rueda', '50% 62%'),
    ('alineacion-utilitario', 'Alineación de utilitarios', 'Utilitario sobre un elevador tijera y balanceadora', '50% 42%'),
    ('desarmadora', 'Armado y desarmado', 'Técnico trabajando con una desarmadora de neumáticos', '50% 36%'),
]

CSS = """<style>
.marca-boceto{position:fixed;left:10px;bottom:10px;z-index:99;background:#ffd338;color:#111;font:700 12px sans-serif;padding:6px 10px}
.carr{position:relative;overflow:hidden;background:#0f1214;margin:0}
.carr figure{position:absolute;inset:0;margin:0;opacity:0;visibility:hidden;transition:opacity .45s,visibility .45s}
.carr figure.on{opacity:1;visibility:visible}
.carr figure img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}
.carr figcaption{position:absolute;left:0;bottom:0;background:#fff;color:#171717;border-top:4px solid var(--accent);padding:10px 18px;font-weight:700;font-size:.9rem}
.carr .mandos{position:absolute;right:10px;top:10px;z-index:2;display:flex;gap:2px;align-items:center;background:rgba(12,14,16,.72);padding:4px 6px;border-radius:6px}
.carr .mandos button{font-family:inherit;font-size:.74rem;font-weight:600;color:#fff;background:none;border:0;min-width:26px;height:30px;cursor:pointer;padding:0}
.carr .mandos .punto{min-width:16px}.carr .mandos .punto::before{content:"";display:block;width:11px;height:4px;margin:0 auto;background:#8b949b}
.carr .mandos .punto[aria-current=true]::before{background:var(--accent)}
.carr .mandos .pausa{padding:0 8px;margin-left:4px;border-left:1px solid #59636a}
@media (prefers-reduced-motion:reduce){.carr figure{transition:none}}
/* clientes: pegado al hero, compacto y sobre blanco */
.clientes-arriba{background:#fff;padding:10px 0 6px;border-bottom:1px solid var(--line)}
.clientes-arriba h2{text-align:center;font-size:.95rem;margin:0 0 4px}
.clientes-arriba .logo-wrap{height:46px}.clientes-arriba .clients-carousel{padding:2px 0}
.clientes-arriba .clients-carousel::before{background:linear-gradient(to right,#fff,transparent)}
.clientes-arriba .clients-carousel::after{background:linear-gradient(to left,#fff,transparent)}
.clientes-arriba .clients-track{animation-duration:34s}
</style>"""

CSS_A = """<style>
.hero--home{padding:20px 0}
.hero--home h1{font-size:clamp(2.1rem,3.6vw,3.1rem)}.hero--home p.lead{margin:12px 0 18px}.hero--home .hero-nota{margin-top:10px}
.hero--home .stats{margin-top:14px;padding-top:12px}.hero--home .stats svg{height:30px!important}
.hero--home .carr{height:468px;border-radius:var(--radius-lg)}
@media(max-width:900px){.hero--home .inner{grid-template-columns:1fr}.hero--home .carr{height:320px}.carr .mandos .punto{min-width:13px}}
</style>"""

CSS_B = """<style>
.hero--home{padding:0;background:#12171b;color:#fff;border:0}
.hero--home .inner{max-width:none;padding:0;gap:0;grid-template-columns:minmax(0,5fr) minmax(0,7fr);align-items:stretch}
.hero--home .hero-texto{padding:22px 40px 18px max(24px,calc((100vw - 1180px)/2));align-self:center}
.hero--home h1{font-size:clamp(2.1rem,3.6vw,3.1rem)}.hero--home p.lead{margin:12px 0 18px}.hero--home .hero-nota{margin-top:10px}
.hero--home .stats{margin-top:14px;padding-top:12px}.hero--home .stats svg{height:30px!important}
.hero--home h1,.hero--home .stats b{color:#fff}.hero--home p.lead{color:#cbd2d6}.hero--home .hero-nota,.hero--home .stats span{color:#9aa4ab}
.hero--home .stats{border-color:#333c42}.hero--home .btn--ghost{background:transparent;color:#fff;border-color:#78838a}
.hero--home .carr{min-height:508px}
@media(max-width:900px){.hero--home .inner{grid-template-columns:1fr}.hero--home .hero-texto{padding:28px 16px}.hero--home .carr{order:-1;min-height:320px}.carr .mandos .punto{min-width:13px}}
</style>"""

JS = """<script>(()=>{const c=document.querySelector('.carr'),d=[...c.querySelectorAll('figure')],p=[...c.querySelectorAll('.punto')],b=c.querySelector('.pausa');let i=0,t,parado=matchMedia('(prefers-reduced-motion: reduce)').matches,encima=false;
const ver=n=>{i=(n+d.length)%d.length;d.forEach((x,k)=>{x.classList.toggle('on',k===i);x.setAttribute('aria-hidden',k!==i)});p.forEach((x,k)=>x.setAttribute('aria-current',k===i));const s=d[(i+1)%d.length].querySelector('img');s.loading='eager'};
const reloj=()=>{clearInterval(t);b.textContent=parado?'Reproducir':'Pausar';if(!parado)t=setInterval(()=>{if(!encima&&!document.hidden)ver(i+1)},__MS__)};
c.querySelectorAll('[data-ir]').forEach(x=>x.onclick=()=>{ver(i+ +x.dataset.ir);reloj()});p.forEach((x,k)=>x.onclick=()=>{ver(k);reloj()});b.onclick=()=>{parado=!parado;reloj()};
c.querySelector('.mandos').onmouseenter=()=>encima=true;c.querySelector('.mandos').onmouseleave=()=>encima=false;
let x0=null;c.addEventListener('touchstart',e=>x0=e.touches[0].clientX,{passive:true});c.addEventListener('touchend',e=>{const dx=e.changedTouches[0].clientX-x0;if(Math.abs(dx)>40){ver(i-Math.sign(dx));reloj()}});
ver(0);reloj()})()</script>""".replace('__MS__', str(int(SEGUNDOS * 1000)))


def carrusel():
    figs = ''.join(
        f'<figure{" class=on" if i == 0 else ""}><img src="{F}{n}.webp" alt="{alt}" style="object-position:{pos}"'
        f'{" fetchpriority=high" if i == 0 else " loading=lazy"}><figcaption>{trabajo}</figcaption></figure>'
        for i, (n, trabajo, alt, pos) in enumerate(DIAPOS))
    puntos = ''.join(f'<button type="button" class="punto" aria-label="Foto {i + 1} de {len(DIAPOS)}"></button>' for i in range(len(DIAPOS)))
    return (f'<div class="carr" aria-roledescription="carrusel" aria-label="Fotos de trabajos en taller">{figs}'
            f'<div class="mandos"><button type="button" data-ir="-1" aria-label="Foto anterior">←</button>{puntos}'
            f'<button type="button" data-ir="1" aria-label="Foto siguiente">→</button><button type="button" class="pausa">Pausar</button></div></div>')


def tramo(s, desde, hasta):
    a = s.index(desde)
    return a, s.index(hasta, a)


def inicio(css):
    s = (ROOT / 'index.html').read_text(encoding='utf-8')
    a, b = tramo(s, '<div class="hero-fotos">', '</section>')
    s = s[:a] + carrusel() + '\n  </div>\n' + s[b:]
    a, b = tramo(s, '<!-- Clients carousel -->', '<div class="clients-carousel">')
    s = s[:a] + '<!-- Clients carousel -->\n<section class="clientes-arriba">\n  <h2>Empresas que confían en nosotros.</h2>\n  ' + s[b:]
    for viejo, nuevo in [('assets/img/clientes/logo-subaru-inchcape.svg', 'scratch/inicio-v3/logos/logo-subaru.webp'),
                         ('assets/img/clientes/logo-ypf.svg', 'scratch/inicio-v3/logos/logo-ypf.svg')]:
        assert viejo in s
        s = s.replace(viejo, nuevo)
    s = s.replace('<head>', '<head><base href="../../">', 1).replace('</head>', CSS + css + '</head>', 1)
    return s.replace('</body>', '<div class="marca-boceto">BOCETO · no publicado</div>' + JS + '</body>', 1)


# ───────── portadas para notas con foto ─────────
CON_FOTO = [  # nota (comienzo del slug), foto, encuadre
    ('alineacion-de-camiones-con-eje-desplazado', 'josam-cabezal', '50% 60%'),
    ('instalamos-una-josam-cv-aligner', 'josam-camion', '50% 62%'),
    ('las-maquinas-del-taller', 'taller-completo', '40% 60%'),
    ('neumaticos-trivium-la-gomeria', 'fachada', '48% 50%'),
    ('geoliner-630', 'colocando-target', '50% 65%'),
    ('como-funciona-la-alineacion-3d', 'alineacion-3d-target', '50% 38%'),
    ('errores-comunes-al-usar-una-balanceadora', 'balanceadora', '50% 40%'),
    ('como-mantener-tu-desarmadora', 'desarmadora', '50% 52%'),
    ('servicios-integrales', 'posventa', '60% 78%'),
]
SIN_FOTO = [2, 3, 4, 5]   # índices de la propuesta A (scratch/rediseno-2027/portadas): flotas, checklist, llave, ADAS


def lamina(kicker, titulo, foto, pos):
    fs = 52 if len(titulo) <= 28 else 46 if len(titulo) <= 40 else 40
    if max(map(len, html.unescape(titulo).split())) >= 11:   # palabras largas: que no toquen el marco
        fs = min(fs, 46)
    logo = (ROOT / 'assets/img/logo-trivium.svg').as_uri()
    return f"""<!doctype html><meta charset="utf-8"><link href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@62..125,100..900&display=swap" rel="stylesheet">
<style>*{{margin:0;padding:0;box-sizing:border-box}}body{{width:1100px;height:600px;position:relative;overflow:hidden;font-family:Archivo,sans-serif;color:#12171b;background:#fff}}
.f{{position:absolute;left:440px;top:0;width:660px;height:600px;object-fit:cover;object-position:{pos}}}
.col{{position:absolute;left:0;top:0;width:440px;height:600px;border:2px solid #12171b;border-width:22px 0 22px 22px;border-color:#fff}}
.marco{{position:absolute;left:22px;top:22px;width:418px;height:556px;border:2px solid #12171b}}
.txt{{position:absolute;left:52px;top:60px;width:366px}}
h1{{font-size:{fs}px;font-stretch:112%;font-weight:800;line-height:1.06;letter-spacing:-.015em}}
.cota{{height:28px;margin-top:28px;position:relative;border:solid #ff1e00;border-width:0 3px}}.cota i{{position:absolute;left:0;right:0;top:13px;height:3px;background:#ff1e00}}
.rot{{position:absolute;left:22px;bottom:22px;width:418px;height:92px;border-top:2px solid #12171b;display:flex;align-items:center}}
.rot img{{height:44px;margin:0 20px}}.rot span{{align-self:stretch;display:flex;align-items:center;border-left:2px solid #12171b;padding:0 18px;font-size:22px;line-height:1.1;font-weight:700;font-stretch:76%;letter-spacing:.05em;text-transform:uppercase}}</style>
<img class="f" src="{(AQUI / 'fotos' / (foto + '.webp')).as_uri()}"><div class="marco"></div>
<div class="txt"><h1>{titulo}</h1><div class="cota"><i></i></div></div>
<div class="rot"><img src="{logo}"><span>{kicker}</span></div>"""


def portadas():
    posts = json.loads((ROOT / 'data/blog.json').read_text(encoding='utf-8'))
    (AQUI / 'portadas').mkdir(exist_ok=True)
    tmp = Path(tempfile.mkdtemp())
    for n, (pref, foto, pos) in enumerate(CON_FOTO):
        candidatas = [p for p in posts if p['slug'].startswith(pref)]
        if not candidatas:
            sys.exit(f'no hay nota que empiece con {pref}')
        p = max(candidatas, key=lambda x: x['date'])
        kicker, titulo, _sub, _imgs = SPEC[max((k for k in SPEC if p['slug'].startswith(k)), key=len)]
        h, png = tmp / f'{n}.html', tmp / f'{n}.png'
        h.write_text(lamina(html.escape(kicker), html.escape(titulo), foto, pos), encoding='utf-8')
        subprocess.run(['google-chrome', '--headless=new', '--disable-gpu', '--hide-scrollbars', '--allow-file-access-from-files',
                        '--window-size=1100,600', '--virtual-time-budget=8000', f'--screenshot={png}', h.as_uri()], check=True, capture_output=True)
        Image.open(png).convert('RGB').save(AQUI / 'portadas' / f'{n}.webp', 'WEBP', quality=86)
        print('✔', p['slug'])
    rejilla = lambda srcs: '<div class="g">' + ''.join(f'<img src="{s}" alt="">' for s in srcs) + '</div>'
    (AQUI / 'portadas.html').write_text(
        '<!doctype html><html lang="es"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Boceto · Portadas</title>'
        '<style>body{font-family:Archivo,Arial,sans-serif;max-width:1240px;margin:0 auto;padding:24px 16px;background:#cfd3d5;color:#12171b}'
        '.g{display:grid;grid-template-columns:repeat(auto-fit,minmax(360px,1fr));gap:18px;margin-bottom:48px}img{width:100%;height:auto;display:block}</style>'
        '<h2>Notas con foto</h2>' + rejilla(f'portadas/{i}.webp' for i in range(len(CON_FOTO))) +
        '<h2>Notas sin foto: plantilla con la imagen del equipo</h2>' + rejilla(f'../rediseno-2027/portadas/a-{i}.webp' for i in SIN_FOTO) + '</html>', encoding='utf-8')


if __name__ == '__main__':
    (AQUI / 'inicio-a.html').write_text(inicio(CSS_A), encoding='utf-8')
    (AQUI / 'inicio-b.html').write_text(inicio(CSS_B), encoding='utf-8')
    portadas()
