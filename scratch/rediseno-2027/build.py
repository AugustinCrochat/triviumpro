#!/usr/bin/env python3
"""Arma los bocetos estáticos del rediseño con datos reales del catálogo.

No toca nada del sitio publicado: scratch/ está en .assetsignore.
Los precios salen del feed de Google.
"""
import csv, html, json, pathlib, re

AQUI = pathlib.Path(__file__).resolve().parent
RAIZ = AQUI.parents[1]
R = '../../'
cat = json.loads((RAIZ / 'data/catalog.json').read_text())
posts = json.loads((RAIZ / 'data/blog.json').read_text())
posts = posts if isinstance(posts, list) else posts['posts']
posts.sort(key=lambda p: p['date'], reverse=True)
P = {p['sku']: p for p in cat['products']}
BR = {b['slug']: b.get('name', b['slug']) for b in cat['brands']}

PRECIOS = {}
with open(RAIZ / 'feeds/google-merchant.tsv', encoding='utf-8') as f:
    for row in csv.DictReader(f, delimiter='\t'):
        slug = row['link'].rstrip('/').split('/')[-1]
        PRECIOS[slug] = '$ ' + f"{int(float(row['price'].split()[0]) + .5):,}".replace(',', '.')

e = html.escape
def precio(p): return PRECIOS.get(p['slug'], 'A cotizar')
def kg(p):
    d = re.sub(r'[^\d]', '', (p.get('capacity') or ''))
    return int(d) if d else 0
def fkg(n): return f'{n:,}'.replace(',', '.') + ' kg'
def mm(p):
    # 121 mm en el SPOA10TRIO es la altura MÍNIMA del adaptador, no la elevación.
    if p['sku'] == '1010017': return None
    v = re.sub(r'[^\d]', '', p.get('lift_height') or '')
    return v or None
def origen(p):
    b = p.get('badges') or []
    return {'made-in-usa': 'EE. UU.', 'made-in-italy': 'Italia', 'ce-ue': 'Marcado CE',
            'made-in-germany': 'Alemania', 'made-in-sweden': 'Suecia',
            'made-in-taiwan': 'Taiwán'}.get(b[0] if b else '', '—')

WA = 'https://wa.me/5491127015294'
FUENTE = ('https://fonts.googleapis.com/css2?family=Archivo:ital,wdth,wght@0,62..125,100..900'
          '&display=swap')


def pagina(archivo, titulo, cuerpo, activo='', extra=''):
    nav = ''.join(f'<a href="{h}" class="{"on" if n == activo else ""}">{n}</a>' for n, h in [
        ('Elevadores', 'categoria.html'), ('Alineación', '#'), ('Balanceo', '#'),
        ('Desarmado', '#'), ('Servicio técnico', 'index.html#servicio'), ('Biblioteca técnica', 'blog.html')])
    doc = f'''<!doctype html><html lang="es-AR"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex">
<title>Boceto · {titulo}</title><link href="{FUENTE}" rel="stylesheet"><link rel="stylesheet" href="sistema.css"></head><body>
<div class="barra"><div class="w"><span><b>Trivium Pro</b>, antes Trivium Center. Equipamiento para talleres en todo el país.</span><span>Ventas +54 9 351 399-4200 &nbsp; WhatsApp +54 9 11 2701-5294</span></div></div>
<header class="cab"><div class="w"><a class="logo" href="index.html"><img src="{R}assets/img/logo-trivium.svg" alt="Trivium Pro"></a><nav>{nav}</nav>
<input class="buscar" placeholder="Buscar modelo: SPOA10, Geoliner…" aria-label="Buscar equipo"><a class="btn rojo chico" href="{WA}">Consultar</a></div></header>
<nav class="navcel">{nav}</nav><main>{cuerpo}</main>
<footer class="pie"><div class="w"><div class="g">
<div><img src="{R}assets/img/logo-trivium.svg" alt="" style="height:46px;margin-bottom:14px"><p>Equipamiento para talleres mecánicos, gomerías, concesionarias y flotas. Venta, instalación (se cotiza aparte) y servicio técnico.</p></div>
<div><h3>Equipos</h3><a>Elevadores</a><a>Alineadoras</a><a>Balanceadoras</a><a>Desarmadoras</a><a>Equipamiento de taller</a></div>
<div><h3>Servicio</h3><a>Instalación y posventa</a><a>Envíos y entregas</a><a>Cambios y devoluciones</a><a>Botón de arrepentimiento</a></div>
<div><h3>Información</h3><a>Biblioteca técnica</a><a>Guías de compra</a><a>Origen y marcado CE</a><a>Nosotros</a></div></div>
<div class="caj"><span><small>Sitio</small>pro.trivium.ar</span><span><small>Correo</small>info@trivium.ar</span><span><small>WhatsApp</small>+54 9 11 2701-5294</span><span><small>Ventas</small>+54 9 351 399-4200</span></div></div></footer>
<div class="marcaboceto">BOCETO · no publicado</div>{extra}</body></html>'''
    (AQUI / archivo).write_text(doc, encoding='utf-8')


DOS_COL = [P[s] for s in ('1010144', '1010124', '1010022', '1010001', 'CHALL-VLE10', '1010271',
                          '1010291', 'P-5083', '1010289', 'P-5090', '1010288')]
DOS_COL.sort(key=kg)


def tabla(lista, marcado=None):
    filas = []
    for p in lista:
        k = kg(p)
        h = mm(p)
        filas.append(f'''<tr data-kg="{k}" class="{'sel' if p['sku'] == marcado else ''}">
<td><a class="mod" href="producto.html"><img src="{R}{p['image']}" alt="" loading="lazy"><span>{e(p['name'].split(' - ')[-1].split(' – ')[-1] if (' - ' in p['name'] or ' – ' in p['name']) else p['name'])}<small>{e(BR.get(p.get('brand'), ''))}</small></span></a></td>
<td><span class="esc"><b class="dato">{fkg(k)}</b><i style="--p:{min(100, k / 8000 * 100):.0f}%"></i></span></td>
<td class="dato">{h + ' mm' if h else '<span class="nd">Consultar</span>'}</td><td>{origen(p)}</td>
<td>{'Certificado' if p.get('ali') else '<span class="nd">—</span>'}</td><td class="dato" style="white-space:nowrap">{precio(p)}</td></tr>''')
    return ('<div class="tw"><table class="tec"><thead><tr><th>Modelo</th><th>Capacidad (escala 0 a 8.000 kg)</th>'
            '<th>Elevación</th><th>Origen</th><th>ALI</th><th>Precio, IVA incl.</th></tr></thead><tbody>'
            + ''.join(filas) + '</tbody></table></div>')


FILTRO_JS = '''<script>
document.querySelectorAll('[data-min]').forEach(b=>b.onclick=()=>{
 document.querySelectorAll('[data-min]').forEach(x=>x.setAttribute('aria-pressed',x===b));
 document.querySelectorAll('[data-kg]').forEach(t=>t.hidden=+t.dataset.kg<+b.dataset.min||+t.dataset.kg>+b.dataset.max);});
</script>'''
CHIPS = '''<button class="chip" aria-pressed="true" data-min="0" data-max="99999">Todos</button>
<button class="chip" aria-pressed="false" data-min="0" data-max="4600">Hasta 4,5 t</button>
<button class="chip" aria-pressed="false" data-min="4601" data-max="6000">De 4,6 a 6 t</button>
<button class="chip" aria-pressed="false" data-min="6001" data-max="99999">Más de 6 t</button>'''

# Medidas del SPOA10 tomadas de la ficha técnica vigente.
ENTRA_JS = '''<script>
(()=>{const t=document.getElementById('techo'),a=document.getElementById('ancho');if(!t)return;
const f=()=>{for(const[i,n,r]of[['r-t',+t.value,3655],['r-a',+a.value,3469]]){const o=document.getElementById(i);
 if(!n){o.textContent='Ingresá tu medida';o.className='';continue}
 o.textContent=n>=r?'Alcanza, sobran '+(n-r)+' mm':'No alcanza, faltan '+(r-n)+' mm';o.className=n>=r?'ok':'no'}};
t.oninput=a.oninput=f;f()})();
</script>'''


def entra(oscura=True):
    return f'''<div class="entra">
<figure class="plano"><img src="img/spoa10-frente.png" alt="Plano frontal del Rotary SPOA10 con las cotas A a N"><figcaption><span><b>Rotary Lift SPOA10</b>, vista frontal</span><span>Referencias de la ficha técnica</span></figcaption></figure>
<div><h3>Cargá las medidas libres de tu taller, en milímetros</h3>
<div class="medir"><label>Altura de techo<input id="techo" inputmode="numeric" value="3900"></label><label>Ancho disponible<input id="ancho" inputmode="numeric" value="3400"></label></div>
<ul class="res"><li><span>Techo necesario: <b class="dato">3655 mm</b></span><span id="r-t"></span></li>
<li><span>Ancho total del equipo (C): <b class="dato">3469 mm</b></span><span id="r-a"></span></li></ul>
<p class="suave" style="margin-top:16px;font-size:.9rem">Es una primera comprobación. No reemplaza el relevamiento: el piso, la alimentación eléctrica y el espacio de circulación se revisan antes de instalar.</p>
<a class="btn {'claro' if oscura else 'lleno'}" href="{WA}">Mandar mis medidas a un técnico</a></div></div>'''


# ───────────────────────── PORTADA ─────────────────────────
familias = ''.join(f'''<a href="{'categoria.html' if t == 'Elevadores' else '#'}"><div class="im"><img src="{R}assets/img/productos/{i}" alt="{a}"></div><h3>{t}</h3><p>{d}</p><span class="n"><span>{n}</span><span aria-hidden="true">→</span></span></a>''' for t, i, a, d, n in [
    ('Elevadores', 'elevador-dos-columnas-cuatro-toneladas-piso-libre.webp', 'Elevador de dos columnas Trivium Pro', 'De 2 y 4 columnas, tijera y motos. Se eligen por capacidad, techo y tipo de trabajo.', '34 en catálogo'),
    ('Alineación', 'alineadora-3d-hofmann-geoliner-880.webp', 'Alineadora Hofmann Geoliner 880', 'Alineadoras 3D para autos y alineación de camiones por cámara.', '6 equipos'),
    ('Balanceo', 'balanceadora-de-ruedas-hofmann-geodyna-78002p.webp', 'Balanceadora Hofmann Geodyna 7800-2P', 'Balanceadoras para auto y camión, más conos y accesorios de centrado.', '9 balanceadoras'),
    ('Desarmado', '', 'Desarmadora de neumáticos', 'Desarmadoras para gomería, con o sin brazo auxiliar para run flat.', '8 desarmadoras')])
des = next(p for p in cat['products'] if p['slug'] == 'desarmadora-de-ruedas-con-brazo-auxiliar-pl-1256s-trivium-center')
familias = familias.replace(f'src="{R}assets/img/productos/" ', f'src="{R}{des["image"]}" ')

marcas = ''.join(f'<a href="#"><span><img src="{R}assets/img/marcas/logo-{s}.svg" alt="{n}"></span><span class="dato">{o}</span><span class="suave">{d}</span><span>Ver →</span></a>' for s, n, o, d in [
    ('rotary-lift', 'Rotary Lift', 'Estados Unidos', 'Elevadores de mayor calibre para talleres, concesionarias y flotas.'),
    ('hofmann', 'Hofmann', 'Grupo Snap-on', 'Alineación, balanceo y desarmado para uso intensivo.'),
    ('challenger-lifts', 'Challenger Lifts', 'Grupo Snap-on', 'Elevadores certificados ALI.'),
    ('direct-lift', 'Direct Lift', 'Rotary Solutions', 'Elevadores tijera y portátiles de diseño compacto.'),
    ('trivium-pro', 'Trivium Pro', 'Línea propia', 'La opción accesible para empezar o ampliar capacidad.')])

_inicio = (AQUI.parent.parent / 'index.html').read_text(encoding='utf-8')
_a = _inicio.index('<div class="clients-carousel">'); _b = _inicio.index('</section>', _a)
clientes = _inicio[_a:_b].replace('src="assets/', f'src="{R}assets/').rstrip()
if clientes.endswith('<!-- Services -->'): clientes = clientes[:-len('<!-- Services -->')]

FOTOS = [
    ('assets/img/servicios/instalacion-elevador.webp', 'Dos técnicos de Trivium ajustando la unidad hidráulica de un elevador', 'Nuestro equipo en un taller', 'Elevador de columnas', '70% 50%'),
    ('assets/img/blog/las-maquinas-del-taller-de-neumaticos-trivium-arguello-alineacion.webp', 'Técnico alineando una camioneta sobre un elevador tijera', 'Taller Trivium Argüello', 'Alineación', '35% 40%'),
    ('assets/img/servicios/balanceadora-en-uso.webp', 'Balanceo de una rueda en una balanceadora', 'Taller Trivium Argüello', 'Balanceo', '40% 50%'),
    ('assets/img/servicios/desarmadora-en-uso.webp', 'Rueda montada en una desarmadora de neumáticos', 'Taller Trivium Argüello', 'Armado y desarmado', '50% 50%')]
CARRUSEL = ('<div class="foto carr" aria-roledescription="carrusel" aria-label="Fotos de taller">' +
    ''.join(f'<figure class="diapo{" on" if i == 0 else ""}"><img src="{R}{src}" alt="{alt}" style="object-position:{pos}"{" fetchpriority=high" if i == 0 else " loading=lazy"}>'
            f'<figcaption class="rotulo"><span><small>En la foto</small><b>{donde}</b></span><span><small>Trabajo</small><b>{que}</b></span></figcaption></figure>'
            for i, (src, alt, donde, que, pos) in enumerate(FOTOS)) +
    '<div class="mandos"><button type="button" data-ir="-1" aria-label="Foto anterior">←</button>' +
    ''.join(f'<button type="button" class="punto" data-foto="{i}" aria-label="Foto {i + 1} de {len(FOTOS)}"></button>' for i in range(len(FOTOS))) +
    '<button type="button" data-ir="1" aria-label="Foto siguiente">→</button><button type="button" class="pausa">Pausar</button></div></div>')
CARRUSEL_JS = """<script>(()=>{const c=document.querySelector('.carr');if(!c)return;const d=[...c.querySelectorAll('.diapo')],p=[...c.querySelectorAll('.punto')],b=c.querySelector('.pausa');let i=0,t,parado=matchMedia('(prefers-reduced-motion: reduce)').matches,encima=false;
const ver=n=>{i=(n+d.length)%d.length;d.forEach((x,k)=>{x.classList.toggle('on',k===i);x.setAttribute('aria-hidden',k!==i)});p.forEach((x,k)=>x.setAttribute('aria-current',k===i))};
const reloj=()=>{clearInterval(t);b.textContent=parado?'Reproducir':'Pausar';if(!parado)t=setInterval(()=>{if(!encima&&!document.hidden)ver(i+1)},5000)};
c.querySelectorAll('[data-ir]').forEach(x=>x.onclick=()=>{ver(i+ +x.dataset.ir);reloj()});p.forEach((x,k)=>x.onclick=()=>{ver(k);reloj()});b.onclick=()=>{parado=!parado;reloj()};
c.onmouseenter=()=>encima=true;c.onmouseleave=()=>encima=false;
let x0=null;c.addEventListener('touchstart',e=>x0=e.touches[0].clientX,{passive:true});c.addEventListener('touchend',e=>{const dx=e.changedTouches[0].clientX-x0;if(Math.abs(dx)>40){ver(i-Math.sign(dx));reloj()}});
ver(0);reloj()})()</script>"""

guias = ''.join(f'<a href="#"><span>{t}<small>{d}</small></span><span aria-hidden="true">→</span></a>' for t, d in [
    ('Elevadores para taller', 'Tipos, capacidad y requisitos del piso'), ('Alineadoras 3D', 'Qué espacio y qué elevador necesitan'),
    ('Seguridad de elevadores', 'Certificación ALI e inspección'), ('Equipar una gomería', 'Qué comprar y en qué orden'),
    ('Comparar dos cotizaciones', 'Qué pedir y qué documentación exigir')])


_muestras = json.loads((AQUI / 'portadas' / 'muestras.json').read_text(encoding='utf-8'))
def portada(p):
    return f"portadas/a-{_muestras.index(p['slug'])}.webp" if p['slug'] in _muestras else R + p['image']


def nota_card(p):
    return f'<article><a href="nota.html"><img src="{portada(p)}" alt="" loading="lazy"><h3>{e(p["title"])}</h3></a></article>'


pagina('index.html', 'Portada', f'''
<section class="hero"><div class="g"><div class="t">
<h1>Máquinas de taller, con técnicos que las instalan.</h1>
<p class="baj">Elevadores, alineadoras, balanceadoras y desarmadoras. Te ayudamos a elegir según tus medidas y tu volumen de trabajo, y damos servicio técnico en todo el país.</p>
<div class="acc"><a class="btn rojo" href="categoria.html">Ver equipos</a><a class="btn claro" href="{WA}">Hablar con un técnico</a></div>
<p class="ex">¿Nos conocías como Trivium Center? Somos el mismo equipo.</p></div>
{CARRUSEL}</div></section>
<div class="w"><div class="hechos">
<div><b>15+ años</b><div class="cota">trayectoria</div><span class="tx">en equipamiento para talleres.</span></div>
<div><b>1 año</b><div class="cota">garantía oficial</div><span class="tx">sobre los equipos.</span></div>
<div><b>Todo el país</b><div class="cota">instalación</div><span class="tx">con equipo técnico. Se cotiza aparte.</span></div>
<div><b>48 a 72 h</b><div class="cota">posventa</div><span class="tx">en servicio de posventa.</span></div></div></div>

<section class="sec"><div class="w"><div class="enc"><h2>¿Qué trabajo hace tu taller?</h2><p class="suave">Empezá por la tarea. Dentro de cada familia vas a encontrar marcas importadas de mayor calibre y nuestra línea Trivium Pro.</p></div>
<div class="fam">{familias}</div><div class="otras"><a class="chip">Herramientas neumáticas</a><a class="chip">Muebles de taller</a><a class="chip">Equipamiento general</a><a class="chip">Accesorios de balanceo</a><a class="chip">Aire comprimido Prevost</a></div></div></section>

<section class="sec gris"><div class="w"><div class="enc"><h2>Elevadores de 2 columnas, lado a lado</h2><p class="suave">Los mismos datos, en las mismas unidades. Filtrá por lo que vas a levantar.</p></div>
<div class="filtros">{CHIPS}<a class="btn chico der" href="categoria.html">Ver los 34 elevadores</a></div>{tabla(DOS_COL)}</div></section>

<section class="sec oscura"><div class="w"><div class="enc"><h2>Antes de elegir, medí.</h2><p class="suave">Un elevador se compra una vez y se usa durante años. Lo primero es saber si entra.</p></div>{entra()}</div></section>

<section class="sec"><div class="w"><div class="enc"><h2>Marcas, y para qué sirve cada una</h2><p class="suave">El origen de fabricación se informa por modelo en cada ficha, porque no siempre coincide con el país de la marca.</p></div><div class="marcas">{marcas}</div></div></section>

<section class="sec gris" id="servicio"><div class="w"><div class="enc"><h2>La venta es una parte del trabajo</h2><p class="suave">Así acompañamos un equipo, desde la primera consulta.</p></div>
<div class="serv"><figure class="foto"><img src="{R}assets/img/servicio-posventa-trivium.webp" alt="Técnicos de Trivium trabajando sobre la columna de un elevador" loading="lazy"></figure>
<ol class="pasos"><li><div><h3>Medidas y uso</h3><p>Qué vehículos entran, cuánto pesan, cuánta altura y qué alimentación hay.</p></div></li>
<li><div><h3>Cotización completa</h3><p>Equipo, envío e instalación detallados por separado.</p></div></li>
<li><div><h3>Instalación y capacitación</h3><p>Las coordina nuestro equipo técnico según la localidad. Se cotizan aparte.</p></div></li>
<li><div><h3>Posventa y repuestos</h3><p>Servicio técnico y repuestos originales.</p></div></li></ol></div></div></section>

<section class="sec crema"><div class="w"><div class="enc"><h2>Empresas que confían en nosotros</h2><p></p></div></div>{clientes}</section>

<section class="sec gris"><div class="w"><div class="enc"><h2>Biblioteca técnica</h2><p class="suave">Guías de compra para decidir y notas de taller para trabajar mejor.</p></div>
<div class="dos"><div class="indice">{guias}</div><div class="notas" style="grid-template-columns:1fr 1fr;align-content:start">{''.join(nota_card(p) for p in posts[:4])}</div></div></div></section>''', extra=FILTRO_JS + ENTRA_JS + CARRUSEL_JS)


# ───────────────────────── PRODUCTO ─────────────────────────
spoa = P['1010001']
imgs = ''.join(f'<img src="{R}{i}" alt="">' for i in spoa['images']) + '<img src="img/spoa10-planta.png" alt="Vista en planta">'
specs = [('', 'Capacidad', '4535 kg (10.000 lb)'), ('A', 'Elevación', '1962 mm'), ('B', 'Altura total de la columna (estándar)', '3556 mm'), ('C', 'Ancho total', '3469 mm'), ('D', 'Espacio libre para el vehículo', '2413 mm'), ('E', 'Altura del travesaño superior', '3455 mm'), ('F–G', 'Brazo delantero (mín. / máx.)', '604 / 1036 mm'), ('H–I', 'Brazo trasero (mín. / máx.)', '1016 / 1548 mm'), ('J', 'Altura mínima del adaptador', '121 mm'), ('K–L', 'Adaptador bajo / alto', '178 / 260 mm'), ('M', 'Interior de la columna', '2699 mm'), ('N', 'Altura del cilindro (elevación total)', '3632 mm'), ('', 'Altura de techo necesaria', '3655 mm'), ('', 'Motor', '2 CV'), ('', 'Alimentación', '208/230 V monofásico'), ('', 'Tiempo de elevación', '45 s'), ('', 'Carga máxima por brazo', '1134 kg')]
filas = ''.join(f'<tr><td class="letra">{a}</td><td>{b}</td><td class="dato" style="font-size:1.05rem">{c}</td></tr>' for a, b, c in specs)
chapa = ''.join(f'<div><dt>{a}</dt><dd>{b}</dd></div>' for a, b in [('Capacidad', '4535 kg'), ('Elevación', '1962 mm'), ('Techo necesario', '3655 mm'), ('Ancho total', '3469 mm'), ('Alimentación', '208/230 V mono'), ('Tiempo de subida', '45 s'), ('Fabricación', 'Estados Unidos'), ('Certificación ALI', 'SPOA10X')])

pagina('producto.html', 'Ficha SPOA10', f'''
<div class="w miga">Inicio / Elevadores / 2 columnas / Rotary Lift SPOA10</div>
<div class="w prod"><div class="gal"><div class="gr"><img src="{R}{spoa['image']}" alt="Elevador de dos columnas Rotary Lift SPOA10 con un vehículo levantado"><span class="sello"><img src="{R}assets/img/iconos/origen/usa.svg" alt="">MADE IN USA</span></div><div class="mins">{imgs}</div></div>
<div><img src="{R}assets/img/marcas/logo-rotary-lift.svg" alt="Rotary Lift" style="height:30px;margin-bottom:16px">
<h1 style="font-size:clamp(1.8rem,3vw,2.5rem)">Elevador de 2 columnas Rotary SPOA10, 4535 kg</h1>
<p class="suave" style="margin-top:12px">Asimétrico, sin travesaño en el piso, con brazos TRIO™ de tres etapas.</p>
<div class="chapa"><header><span>SPOA10</span><span class="dato">Cód. 1010001</span></header><dl>{chapa}</dl></div>
<div class="acc2"><a class="btn rojo" href="{WA}">Pedir cotización del SPOA10</a><a class="btn" href="ficha.pdf">Ficha técnica PDF</a><a class="btn" href="#entra">¿Entra en mi taller?</a></div>
<p class="suave" style="font-size:.86rem;margin-top:14px">Precio a cotizar. Consultá planes de financiación. Instalación no incluida.</p></div></div>
<nav class="sub"><div class="w"><a href="#para">Para qué sirve</a><a href="#entra">¿Entra en tu taller?</a><a href="#spec">Especificaciones</a><a href="#brazos">Brazos y adaptadores</a><a href="#comparar">Comparar</a><a href="#preg">Preguntas</a></div></nav>
<section class="sec" id="para"><div class="w"><p class="resp">El SPOA10 es un elevador de 2 columnas asimétrico para autos y utilitarios de hasta 4535 kg. Las columnas giradas permiten abrir más las puertas con el vehículo arriba, y el piso queda libre para mover carros y herramientas.</p>
<div class="pend"><b>Pendiente de ustedes (acá se demuestra la experiencia):</b> 3 o 4 líneas firmadas por un técnico. Por ejemplo, qué revisa del piso antes de instalar, qué error ve seguido y cuándo recomienda otro modelo. No lo escribo yo, porque tiene que ser verdadero.</div></div></section>
<section class="sec oscura" id="entra"><div class="w"><div class="enc"><h2>¿Entra en tu taller?</h2><p class="suave">Compará tus medidas con las del equipo.</p></div>{entra()}</div></section>
<section class="sec" id="spec"><div class="w"><div class="enc"><h2>Especificaciones</h2><p class="suave">Las letras corresponden a los planos.</p></div>
<div class="entra"><div class="tw"><table class="tec"><tbody>{filas}</tbody></table></div><figure class="plano" style="position:sticky;top:140px"><img src="img/spoa10-planta.png" alt="Plano en planta con envergadura de brazos"><figcaption><span><b>Vista superior</b></span><span>Posición de brazos</span></figcaption></figure></div></div></section>
<section class="sec gris" id="brazos"><div class="w"><div class="enc"><h2>Brazos TRIO™ y adaptadores</h2><p class="suave">Se incluye un modelo de adaptador. El resto se vende por separado.</p></div>
<div class="tres"><figure><img src="img/ad-fa.png" alt="Adaptador Flip Up"><figcaption><b>Flip Up (FA)</b></figcaption></figure><figure><img src="img/ad-ra.png" alt="Adaptador redondo"><figcaption><b>Redondo (RA)</b></figcaption></figure><figure><img src="img/ad-ta.png" alt="Adaptador para camiones"><figcaption><b>Camiones (TA)</b></figcaption></figure></div></div></section>
<section class="sec" id="comparar"><div class="w"><div class="enc"><h2>Comparalo antes de decidir</h2><p class="suave">Otros elevadores de 2 columnas del catálogo.</p></div>{tabla([P[s] for s in ('1010144', '1010022', '1010001', 'CHALL-VLE10', '1010271')], '1010001')}</div></section>
<section class="sec gris faq" id="preg"><div class="w dos"><h2>Preguntas frecuentes</h2><div>
<details open><summary>¿Qué altura de techo necesita el SPOA10?</summary><p>3655 mm. La columna estándar mide 3556 mm y el travesaño superior queda a 3455 mm.</p></details>
<details open><summary>¿Funciona con corriente monofásica?</summary><p>Sí. La ficha indica motor de 2 CV con alimentación monofásica de 208/230 V.</p></details>
<details open><summary>¿La instalación está incluida?</summary><p>No. Contamos con técnicos para instalarlo en todo el país y la instalación se cotiza aparte.</p></details></div></div></section>''', 'Elevadores', ENTRA_JS)


# ───────────────────────── CATEGORÍA ─────────────────────────
def card(p):
    h = mm(p)
    return f'''<a class="card" data-kg="{kg(p)}" href="producto.html"><div class="im"><img src="{R}{p['image']}" alt="{e(p['name'])}" loading="lazy"></div><span class="rot">{e(BR.get(p.get('brand'), ''))} · {origen(p)}</span><h3>{e(p['name'])}</h3>
<div class="sp"><span>Capacidad<b class="dato">{fkg(kg(p))}</b></span><span>Elevación<b class="dato">{h + ' mm' if h else 'Consultar'}</b></span></div><div class="pr">{precio(p)}<small>{'IVA incluido' if p['slug'] in PRECIOS else 'Respondemos por WhatsApp'}</small></div></a>'''


pagina('categoria.html', 'Elevadores de 2 columnas', f'''
<section class="catcab"><div class="w"><h1>Elevadores de 2 columnas</h1><p>Son los más usados en mecánica general: dejan libre la parte baja del vehículo y ocupan poco lugar. Se eligen por la capacidad según el vehículo más pesado que vas a subir, por la altura de techo y por el tipo de base: con piso libre o con travesaño al piso.</p></div></section>
<section class="sec" style="padding-top:28px"><div class="w"><div class="filtros">{CHIPS}<span class="der rot">Vista:</span><a class="chip on">Fotos</a><a class="chip" href="#tabla">Tabla comparativa</a></div>
<div class="grilla">{''.join(card(p) for p in DOS_COL[:8])}</div>
<div id="tabla" style="margin-top:64px"><div class="enc"><h2>Tabla comparativa</h2><p class="suave">Es la misma lista, preparada para comparar.</p></div>{tabla(DOS_COL)}</div></div></section>''', 'Elevadores', FILTRO_JS)


# ───────────────────────── BLOG Y NOTA ─────────────────────────
d = posts[0]
pagina('blog.html', 'Biblioteca técnica', f'''
<section class="catcab"><div class="w"><h1>Biblioteca técnica</h1><p>Guías de compra y notas de taller sobre elevación, alineación, balanceo y desarmado.</p></div></section>
<section class="sec"><div class="w"><a class="destacada" href="nota.html"><img src="{portada(d)}" alt="" style="width:100%"><div><span class="rot">Alineación de camiones · 25 de noviembre de 2026</span><h2 style="margin:10px 0 14px">{e(d['title'])}</h2><p class="suave">{e(html.unescape(re.sub(r'<[^>]+>', '', d.get('excerpt', ''))).strip())}</p></div></a>
<div class="dos"><div><div class="enc" style="grid-template-columns:1fr"><h2 style="font-size:1.5rem">Guías de compra</h2></div><div class="indice">{guias}</div></div>
<div><div class="filtros"><a class="chip on">Todas</a><a class="chip">Alineación</a><a class="chip">Balanceo</a><a class="chip">Desarmado</a><a class="chip">Elevadores</a><a class="chip">Gestión del taller</a><a class="chip">Instalaciones</a></div>
<div class="notas" style="grid-template-columns:1fr 1fr">{''.join(nota_card(p) for p in posts[1:9])}</div></div></div></div></section>''', 'Biblioteca técnica')

cuerpo = d['content'].replace('../../assets/', R + 'assets/')
cuerpo, _n = re.subn(r'<p><strong>En resumen:</strong>\s*(\w)(.*?)</p>', lambda m: f'<div class="resumen"><strong>En resumen</strong><p>{m[1].upper()}{m[2]}</p></div><!--equipo-->', cuerpo, count=1, flags=re.S)
if not _n:
    _m = re.search(r'<(div|p)[^>]*class="nota-resumen".*?</\1>', cuerpo, re.S)
    assert _m, 'la nota no tiene resumen'
    cuerpo = cuerpo[:_m.end()] + '<!--equipo-->' + cuerpo[_m.end():]
indice = []
def ancla(m):
    indice.append(re.sub('<[^>]+>', '', m.group(1)))
    return f'<h2 id="s{len(indice)}">{m.group(1)}</h2>'
cuerpo = re.sub(r'<h2>(.*?)</h2>', ancla, cuerpo)
josam = next(p for p in cat['products'] if p['slug'] == 'alineadora-de-camiones-josam-cv-aligner')
assert '<!--equipo-->' in cuerpo
cuerpo = cuerpo.replace('<!--equipo-->', f'<div class="equipo"><img src="{R}{josam["image"]}" alt=""><div><span class="rot">Equipo relacionado · Josam</span><h3>{e(josam["name"])}</h3><a class="btn rojo chico" href="#">Ver ficha y especificaciones →</a></div></div>')
pagina('nota.html', d['title'], f'''<div class="w art"><nav class="toc"><b>En esta nota</b>{''.join(f'<a href="#s{i + 1}">{t}</a>' for i, t in enumerate(indice))}</nav>
<article class="cuerpo"><span class="rot">Biblioteca técnica / Alineación de camiones</span><h1 style="font-size:2.35rem;margin-top:10px">{e(d['title'])}</h1>
<div class="firma"><span><small>Escrito por</small><b>[Nombre y rol: a completar]</b></span><span><small>Revisión técnica</small><b>[Técnico: a completar]</b></span><span><small>Publicado</small><b>25/11/2026</b></span></div><figure class="portada"><img src="{portada(d)}" alt="{e(d['title'])}" width="1100" height="600"></figure>{cuerpo}</article>
<aside class="lado"><img src="{R}{josam['image']}" alt=""><h3>Josam CV-Aligner</h3><p class="suave" style="font-size:.9rem">El equipo del que habla esta nota.</p><a class="btn lleno chico" href="#">Ver el equipo</a></aside></div>''', 'Biblioteca técnica')


# ───────────────────────── FICHA PDF (A4, 2 páginas) ─────────────────────────
def hoja(n, cuerpo_h):
    return f'''<section class="hoja"><header><img src="{R}assets/img/logo-trivium.svg" alt="Trivium Pro"><div><img src="{R}assets/img/marcas/logo-rotary-lift.svg" alt="Rotary Lift"></div></header>{cuerpo_h}
<footer><span class="w2"><small>Equipo</small><b>Rotary Lift SPOA10</b></span><span><small>Fabricación</small><b>Estados Unidos</b></span><span><small>Web</small><a href="https://pro.trivium.ar/producto/{spoa['slug']}/"><b>pro.trivium.ar</b></a></span><span><small>Correo</small><a href="mailto:info@trivium.ar"><b>info@trivium.ar</b></a></span><span><small>WhatsApp</small><a href="{WA}"><b>+54 9 11 2701-5294</b></a></span><span><small>Ventas</small><a href="https://wa.me/5493513994200"><b>+54 9 351 399-4200</b></a></span><span><small>Hoja</small><b>{n} / 2</b></span></footer></section>'''


feats = ''.join(f'<li><b>{a}</b>{b}</li>' for a, b in [('Asimétrico', 'Columnas giradas para abrir más las puertas con el vehículo arriba.'), ('Piso libre', 'Sin travesaño que obstruya carros, gatos y bandejas.'), ('Brazos TRIO™', 'Tres etapas y adaptadores intercambiables.'), ('Triple seguridad', 'Hidráulica, traba mecánica y sensor superior de sobrealtura.'), ('Poco mantenimiento', 'Sin tornillos sinfín, cremalleras ni tuercas de bronce.'), ('Columnas «doble S»', 'Un cilindro hidráulico en cada columna.')])
grandes = ''.join(f'<div><small>{a}</small><b>{b}</b></div>' for a, b in [('Capacidad', '4535 kg'), ('Elevación', '1962 mm'), ('Techo necesario', '3655 mm'), ('Alimentación', '208/230 V')])
h1 = f'''<p class="miniatura">Elevador de 2 columnas asimétrico</p><h1>Rotary Lift SPOA10</h1><div class="nums">{grandes}</div>
<div class="p1"><img src="{R}{spoa['image']}" alt=""><div><p class="lead">Para autos y utilitarios de hasta 4535 kg (10.000 lb), con piso libre y máxima apertura de puertas.</p><ul>{feats}</ul></div></div>
<h2>Adaptadores intercambiables</h2><div class="ads"><figure><img src="img/ad-fa.png" alt=""><figcaption>Flip Up (FA)</figcaption></figure><figure><img src="img/ad-ra.png" alt=""><figcaption>Redondo (RA)</figcaption></figure><figure><img src="img/ad-ta.png" alt=""><figcaption>Camiones (TA)</figcaption></figure></div><p class="nota">Se incluye un modelo; el resto se vende por separado. <b>Certificación ALI:</b> modelo SPOA10X.</p>
<div class="inst"><b>Instalación en tu taller.</b> Contamos con un equipo de técnicos para la colocación de tu equipo, en todo el país. &nbsp;<a href="https://pro.trivium.ar/producto/{spoa['slug']}/">Ver ficha del producto en la web ↗</a></div>'''
h2 = f'''<h2 style="margin-top:0">Medidas</h2><div class="planos"><img src="img/spoa10-frente.png" alt="Vista frontal"><img src="img/spoa10-planta.png" alt="Vista superior"></div><h2>Especificación técnica</h2><table>{filas}</table>'''
css_pdf = '''@page{size:A4;margin:0}*{box-sizing:border-box;margin:0;padding:0}body{font-family:Archivo,Arial,sans-serif;color:#12171b;-webkit-print-color-adjust:exact;print-color-adjust:exact}
.hoja{width:210mm;height:297mm;padding:11mm 12mm 0;position:relative;overflow:hidden;page-break-after:always}
header{display:flex;justify-content:space-between;align-items:center;border-bottom:1.2mm solid #12171b;padding-bottom:4mm;margin-bottom:5mm}header img{height:11mm}header div img{height:8mm}
.miniatura{font-stretch:76%;color:#545f68;font-weight:600;font-size:11pt}h1{font-stretch:118%;font-size:27pt;font-weight:800;line-height:1.1}
.nums{display:grid;grid-template-columns:repeat(4,1fr);border:.5mm solid #12171b;margin:4mm 0}.nums div{padding:2.5mm 3mm}.nums div+div{border-left:.2mm solid #12171b}
small{display:block;font-stretch:76%;color:#545f68;font-size:7.5pt}.nums b{font-stretch:76%;font-size:18pt}
.p1{display:grid;grid-template-columns:82mm 1fr;gap:6mm}.p1>img{width:100%}.lead{font-size:11.5pt;line-height:1.4;border-left:1.4mm solid #ff1e00;padding-left:3mm;margin-bottom:3mm}
ul{list-style:none}li{font-size:8.6pt;line-height:1.35;padding:1.7mm 0;border-bottom:.2mm solid #cdd2d4}li b{display:block;font-size:9.4pt}
h2{font-stretch:118%;font-size:11.5pt;margin:5mm 0 2.5mm;border-top:.6mm solid #12171b;padding-top:2mm}
.ads{display:grid;grid-template-columns:repeat(3,1fr);gap:3mm}figure{border:.2mm solid #cdd2d4;text-align:center;font-size:8pt;font-weight:700;padding-bottom:1.5mm}figure img{width:100%;height:28mm;object-fit:contain}
.nota{font-size:8pt;color:#545f68;margin-top:2mm}.inst{margin-top:4mm;background:#eceeed;padding:3mm;font-size:8.8pt}.inst a{color:#cc1800;font-weight:700;white-space:nowrap}
.planos{display:grid;grid-template-columns:1.1fr 1fr;gap:4mm}.planos img{width:100%;height:84mm;object-fit:contain;border:.3mm solid #12171b;padding:2mm}
table{width:100%;border-collapse:collapse;font-size:9.4pt}td{padding:1.55mm 2mm;border-bottom:.2mm solid #cdd2d4}td.letra{width:13mm;color:#cc1800;font-weight:700;font-stretch:76%}td.dato{text-align:right;font-weight:700;font-stretch:76%;font-size:11pt!important}
footer{position:absolute;left:12mm;right:12mm;bottom:8mm;display:grid;grid-template-columns:1.25fr 1fr .85fr .95fr 1.15fr 1.15fr .45fr;border:.4mm solid #12171b;border-top:1.2mm solid #ff1e00}
footer span{padding:1.5mm 1.6mm;font-size:7pt;white-space:nowrap}footer span+span{border-left:.2mm solid #12171b}footer a{color:inherit;text-decoration:none}'''
(AQUI / 'ficha.html').write_text(f'<!doctype html><html lang="es-AR"><head><meta charset="utf-8"><title>Ficha técnica Rotary Lift SPOA10</title><link href="{FUENTE}" rel="stylesheet"><style>{css_pdf}</style></head><body>{hoja(1, h1)}{hoja(2, h2)}</body></html>', encoding='utf-8')
print('ok', len(PRECIOS), 'precios del feed;', len(indice), 'secciones en la nota')
