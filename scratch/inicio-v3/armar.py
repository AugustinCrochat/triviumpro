#!/usr/bin/env python3
"""BOCETOS sobre la web PUBLICADA (index.html): sólo cambian el hero (carrusel de fotos) y el carrusel de
clientes. Genera inicio-b.html (la versión elegida el 28/11), portadas/ y portadas.html. No modifica nada fuera de esta carpeta."""
import html, json, sys, tempfile
from pathlib import Path
from PIL import Image

AQUI = Path(__file__).resolve().parent
ROOT = AQUI.parent.parent
sys.path.insert(0, str(ROOT / 'scripts'))
from generate_blog_thumbs import SPEC
sys.path.insert(0, str(AQUI))
from render import Chrome
F = 'scratch/inicio-v3/fotos/'
SEGUNDOS = 3.5

DIAPOS = [  # foto, trabajo, texto alternativo, encuadre
    ('capacitacion-pons', 'Capacitación en alineación 3D', 'Técnicos en una capacitación frente a la pantalla de una alineadora Hofmann', '22% 45%'),
    ('josam-mendoza', 'Alineación de camiones · Josam', 'Medición con una alineadora Josam detrás de un camión', '45% 50%'),
    ('puesta-en-marcha', 'Puesta en marcha y capacitación', 'Tres personas revisando un equipo de balanceo', '45% 40%'),
    ('josam-rueda', 'Alineación de camiones por cámara', 'Cabezal y escala de medición Josam en la rueda de un camión', '55% 50%'),
    ('repuestera', 'Instalación de equipos', 'Explicación de una balanceadora recién instalada', '62% 50%'),
    ('elevador-rotary', 'Elevadores Rotary Lift', 'Taller con un auto levantado en un elevador de dos columnas Rotary', '42% 50%'),
    ('elevador-pickup', 'Elevador de 2 columnas', 'Camioneta levantada en un elevador Rotary de dos columnas', '48% 45%'),
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
.clientes-arriba{background:#fff;padding:18px 0 6px;border-bottom:1px solid var(--line)}
.clientes-arriba h2{text-align:center;font-size:clamp(1.4rem,2.3vw,1.85rem);font-weight:800;line-height:1.15;letter-spacing:-.015em;color:#12171b;margin:0 0 10px;padding:0 16px}
.clientes-arriba h2::after{content:"";display:block;width:64px;height:4px;background:#ff1e00;margin:10px auto 0}
.clientes-arriba .logo-wrap{height:46px}.clientes-arriba .clients-carousel{padding:2px 0}
.clientes-arriba .clients-carousel::before{background:linear-gradient(to right,#fff,transparent)}
.clientes-arriba .clients-carousel::after{background:linear-gradient(to left,#fff,transparent)}
.clientes-arriba .clients-track{animation-duration:34s}
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
    ('alineacion-de-camiones-con-eje-desplazado', 'josam-cabezal', '50% 52%'),
    ('instalamos-una-josam-cv-aligner', 'josam-mendoza', '50% 30%'),
    ('formacion-tecnica-en-alineadora', 'capacitacion-pons', '50% 30%'),
    ('equipamiento-completo-para-repuestera', 'repuestera', '55% 30%'),
    ('capacitacion-y-puesta-en-marcha', 'capacitacion-rodavial', '50% 30%'),
    ('servicios-integrales', 'puesta-en-marcha', '45% 20%'),
    ('instalamos-tres-elevadores', 'punto-flash', '50% 30%'),
    ('la-importancia-del-mantenimiento-preventivo', 'lions-group', '45% 30%'),
    ('alineacion-de-colectivos', 'colectivos', '55% 40%'),
    ('ventajas-de-la-alineacion-de-camiones', 'josam-rueda', '55% 40%'),
    ('que-tipo-de-elevador-elegir', 'elevador-pickup', '50% 30%'),
    ('como-manejar-un-taller', 'elevador-rotary', '40% 30%'),
    ('cuanto-espacio-dejar', 'bahia-alineacion', '65% 50%'),
    ('especificaciones-del-piso', 'piso-elevador', '50% 40%'),
    ('como-se-alinea-un-vehiculo', 'target-3d', '50% 40%'),
    ('geometria-de-ruedas', 'geometria', '55% 35%'),
    ('como-funcionan-las-desarmadoras', 'runflat', '50% 15%'),
    ('las-maquinas-del-taller', 'arguello-alineacion', '50% 20%'),
    ('neumaticos-trivium-la-gomeria', 'arguello-fachada', '50% 30%'),
]
SIN_FOTO = [2, 3, 4, 5]   # índices de la propuesta A (scratch/rediseno-2027/portadas): flotas, checklist, llave, ADAS


def lamina(kicker, titulo, foto, pos):
    fs = 54 if len(titulo) <= 34 else 46
    logo = (ROOT / 'assets/img/logo-trivium.svg').as_uri()
    return f"""<!doctype html><meta charset="utf-8"><link href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@62..125,100..900&display=swap" rel="stylesheet">
<style>*{{margin:0;padding:0;box-sizing:border-box}}body{{width:1100px;height:600px;position:relative;overflow:hidden;font-family:Archivo,sans-serif;color:#fff;background:#12171b}}
.f{{position:absolute;inset:0;width:1100px;height:600px;object-fit:cover;object-position:{pos}}}
.v{{position:absolute;inset:0;background:linear-gradient(to top,rgba(10,13,16,.95) 0,rgba(10,13,16,.82) 24%,rgba(10,13,16,.34) 46%,rgba(10,13,16,0) 66%)}}
.txt{{position:absolute;left:48px;bottom:40px;width:820px}}
.k{{display:flex;align-items:center;gap:14px;font-size:21px;font-weight:700;font-stretch:76%;letter-spacing:.09em;text-transform:uppercase;margin-bottom:14px}}.k i{{width:54px;height:6px;background:#ff1e00}}
h1{{font-size:{fs}px;font-stretch:112%;font-weight:800;line-height:1.06;letter-spacing:-.015em;text-shadow:0 2px 14px rgba(0,0,0,.45)}}
.logo{{position:absolute;right:36px;bottom:38px;height:54px}}</style>
<img class="f" src="{(AQUI / 'fotos' / (foto + '.webp')).as_uri()}"><div class="v"></div>
<div class="txt"><div class="k"><i></i>{kicker}</div><h1>{titulo}</h1></div><img class="logo" src="{logo}">"""


def portadas():
    posts = json.loads((ROOT / 'data/blog.json').read_text(encoding='utf-8'))
    (AQUI / 'portadas').mkdir(exist_ok=True)
    tmp = Path(tempfile.mkdtemp())
    for viejo in (AQUI / 'portadas').glob('*.webp'):
        viejo.unlink()
    with Chrome() as chrome:
        for n, (pref, foto, pos) in enumerate(CON_FOTO):
            candidatas = [p for p in posts if p['slug'].startswith(pref)]
            if not candidatas:
                sys.exit(f'no hay nota que empiece con {pref}')
            p = max(candidatas, key=lambda x: x['date'])
            kicker, titulo, _sub, _imgs = SPEC[max((k for k in SPEC if p['slug'].startswith(k)), key=len)]
            h, png = tmp / f'{n}.html', tmp / f'{n}.png'
            h.write_text(lamina(html.escape(kicker), html.escape(titulo), foto, pos), encoding='utf-8')
            chrome.capturar(h.as_uri(), png)
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
    (AQUI / 'inicio-b.html').write_text(inicio(CSS_B), encoding='utf-8')
    portadas()
