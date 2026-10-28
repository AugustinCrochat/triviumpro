#!/usr/bin/env python3
"""Genera /equipos/: landing con las 4 familias (elevadores, alineadoras, balanceadoras,
desarmadoras) a la vista, con filtro por línea (Económica = Trivium Pro / Premium = importadas).
Usa de molde el encabezado y el pie de /nosotros/ (igual que generate_politicas.py) y arma las
tarjetas desde data/catalog.json. Después correr generate_pretty_urls.py para canonical/meta/JSON-LD.

Uso: python3 scripts/generate_equipos.py
"""
import html, json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
esc = lambda s: html.escape(str(s or ''), quote=True)

FAMILIAS = [
    ('elevadores', 'Elevadores', 'elevadores.svg',
     '2 columnas, 4 columnas, tijera, pesados y motos.'),
    ('alineadoras', 'Alineadoras', 'alineadoras.svg',
     'Alineación 3D de precisión para autos y camiones.'),
    ('balanceadoras', 'Balanceadoras', 'balanceadoras.svg',
     'Balanceo digital para gomerías y servicios de rueda.'),
    ('desarmadoras', 'Desarmadoras', 'desarmadoras.svg',
     'Manuales y automáticas, con brazos auxiliares.'),
]
TIPOS = {  # etiqueta corta de subtipo, para la tarjeta
    'elevadores-2-columnas': '2 columnas', 'elevadores-4-columnas': '4 columnas',
    'elevadores-tijera': 'Tijera', 'elevadores-pesados': 'Pesados', 'elevadores-motos': 'Motos',
}

CSS = '''<style>
.eq-tiles{display:grid;grid-template-columns:repeat(4,1fr);gap:12px}
.eq-tile{display:flex;flex-direction:column;align-items:center;gap:6px;text-align:center;padding:18px 10px;background:#fff;border:1px solid var(--line);border-radius:var(--radius-lg);color:var(--text);text-decoration:none;transition:border-color .15s,box-shadow .15s}
.eq-tile:hover{border-color:var(--accent);box-shadow:var(--shadow)}
.eq-tile img{width:40px;height:40px}
.eq-tile b{font-size:1.02rem}
.eq-tile span{font-size:.8rem;color:var(--text-dim)}
.eq-bar{position:sticky;top:0;z-index:20;background:rgba(255,255,255,.96);backdrop-filter:blur(6px);border-bottom:1px solid var(--line)}
.eq-bar .container{display:flex;align-items:center;gap:10px;padding-top:10px;padding-bottom:10px}
.eq-bar nav{display:flex;gap:6px;overflow-x:auto;flex:1;scrollbar-width:none}
.eq-bar nav::-webkit-scrollbar{display:none}
.eq-bar nav a{white-space:nowrap;padding:8px 12px;border:1px solid var(--line);border-radius:999px;font-size:.85rem;font-weight:600;color:var(--text);text-decoration:none}
.eq-bar nav a:hover{border-color:var(--accent);color:var(--accent)}
.eq-bar select{height:40px;border:1px solid var(--line-2);border-radius:10px;padding:0 10px;font:inherit;font-size:.88rem;font-weight:600;background:#fff;color:var(--text);max-width:48vw}
.eq-sec{scroll-margin-top:64px}
.eq-head{display:flex;align-items:flex-end;justify-content:space-between;gap:12px;flex-wrap:wrap;margin-bottom:14px}
.eq-head h2{margin:0}
.eq-head p{margin:4px 0 0;color:var(--text-dim)}
.eq-row{display:flex;gap:14px;overflow-x:auto;scroll-snap-type:x proximity;padding:2px 2px 14px;margin:0 -2px}
.eq-row .prod-card{flex:0 0 232px;scroll-snap-align:start}
.eq-tipo{display:inline-block;font-size:.7rem;font-weight:700;letter-spacing:.06em;text-transform:uppercase;color:var(--text-dim)}
.eq-vacio{display:none;padding:18px;border:1px dashed var(--line-2);border-radius:var(--radius-lg);color:var(--text-dim)}
.eq-sec.is-empty .eq-vacio{display:block}
.eq-sec.is-empty .eq-row{display:none}
@media (max-width:720px){
  .eq-tiles{grid-template-columns:repeat(2,1fr);gap:10px}
  .eq-tile{padding:16px 8px}
  .eq-bar nav{display:none}
  .eq-bar select{max-width:none;flex:1}
  .eq-row .prod-card{flex-basis:70vw}
}
</style>
'''

JS = '''<script>
(function(){
  var sel=document.getElementById('eq-linea');
  function aplicar(){
    var v=sel.value;
    document.querySelectorAll('.eq-sec').forEach(function(sec){
      var n=0;
      sec.querySelectorAll('.prod-card').forEach(function(c){
        var ok=v==='todas'||c.dataset.linea===v;
        c.style.display=ok?'':'none'; if(ok)n++;
      });
      sec.classList.toggle('is-empty',n===0);
      var el=sec.querySelector('[data-n]'); if(el)el.textContent=n;
      var t=document.querySelector('.eq-tile[href="#'+sec.id+'"] span'); if(t)t.textContent=n+(n===1?' equipo':' equipos');
    });
    try{history.replaceState(null,'',v==='todas'?location.pathname+location.hash:'?linea='+v+location.hash)}catch(e){}
  }
  var q=new URLSearchParams(location.search).get('linea');
  if(q&&sel.querySelector('option[value="'+q+'"]'))sel.value=q;
  sel.addEventListener('change',aplicar); aplicar();
})();
</script>
'''


def card(p, brands, idx):
    b = brands.get(p['brand'], {})
    linea = 'economica' if p['brand'] == 'trivium-pro' else 'premium'
    img = p.get('image') or ''
    thumb = re.sub(r'^(assets/img/productos/)([^/]+)$', r'\1t/\2', img)
    lazy = '' if idx < 2 else ' loading="lazy"'
    foto = (f'<img src="../{esc(thumb)}" alt="{esc(p["name"])}" width="480" height="480"{lazy} '
            f'onerror="if(this.dataset.f!==\'1\'){{this.dataset.f=\'1\';this.src=\'../{esc(img)}\'}}">'
            if img else '')
    logo = (f'<span class="thumb-brand"><img src="../{esc(b["logo"])}" alt="{esc(b.get("name"))}"></span>'
            if b.get('logo') else '')
    tipo = TIPOS.get(p['category'])
    spec = ''
    if p['category'].startswith('elevadores') and p.get('capacity'):
        spec = f'<div class="spec"><span>CAP <b>{esc(p["capacity"])}</b></span></div>'
    return (f'<a class="prod-card" href="../producto/{esc(p["slug"])}/" data-linea="{linea}">'
            f'<div class="thumb">{foto}{logo}</div><div class="body">'
            f'<span class="brand-tag">{esc(b.get("name", ""))}</span>'
            + (f'<span class="eq-tipo">{esc(tipo)}</span>' if tipo else '')
            + f'<h3>{esc(p["name"])}</h3>{spec}</div></a>')


def main():
    data = json.load(open(os.path.join(ROOT, 'data/catalog.json'), encoding='utf-8'))
    brands = {b['slug']: b for b in data['brands']}
    # logo de marca como en site.js (BRAND_LOGOS): si existe el svg, se usa
    for s, b in brands.items():
        f = f'assets/img/marcas/logo-{s}.svg'
        if os.path.exists(os.path.join(ROOT, f)):
            b['logo'] = f

    def de_familia(p, fam):
        return p['category'] == fam or p['category'].startswith(fam + '-')

    tiles, secciones = [], []
    for slug, nombre, icono, desc in FAMILIAS:
        prods = [p for p in data['products'] if de_familia(p, slug) and p.get('image')]
        # económica primero: es lo que más se busca en esta landing
        prods.sort(key=lambda p: (p['brand'] != 'trivium-pro',))
        n = len(prods)
        tiles.append(f'<a class="eq-tile" href="#{slug}"><img src="../assets/img/iconos/{icono}" alt="">'
                     f'<b>{nombre}</b><span>{n} equipos</span></a>')
        cards = ''.join(card(p, brands, i) for i, p in enumerate(prods))
        secciones.append(f'''<section class="section eq-sec" id="{slug}"{' style="background:var(--bg-2)"' if len(secciones) % 2 else ''}>
  <div class="container">
    <div class="eq-head">
      <div><h2>{nombre}</h2><p>{desc}</p></div>
      <a class="btn btn--ghost btn--sm" href="../categoria/{slug}/">Ver todas (<span data-n>{n}</span>) →</a>
    </div>
    <div class="eq-row">{cards}</div>
    <div class="eq-vacio">No tenemos {nombre.lower()} en esta línea. Probá con <b>Todas las líneas</b> o <a href="../contacto/" style="color:var(--accent)">consultanos</a>.</div>
  </div>
</section>''')

    molde = open(os.path.join(ROOT, 'nosotros/index.html'), encoding='utf-8').read()
    i = molde.index('<section class="cat-hero">'); j = molde.index('<div id="site-footer">')
    cabeza, pie = molde[:i], molde[j:]
    pie = pie.replace("mountChrome('nosotros')", "mountChrome('')")
    titulo = 'Elevadores, alineadoras, balanceadoras y desarmadoras'
    cabeza = re.sub(r'<title>.*?</title>', f'<title>{titulo} — Trivium Pro</title>', cabeza, count=1, flags=re.S)
    cabeza = cabeza.replace('</head>', CSS + '</head>', 1)

    cuerpo = f'''<section class="cat-hero">
  <div class="container">
    <div class="breadcrumbs"><a href="../">Inicio</a><span>/</span> Equipos</div>
    <h1>Equipos para tu taller</h1>
    <p class="sub">Elegí qué necesitás. Línea económica Trivium Pro o premium de marcas importadas.</p>
    <div class="eq-tiles" style="margin-top:20px">{''.join(tiles)}</div>
  </div>
</section>

<div class="eq-bar">
  <div class="container">
    <nav aria-label="Secciones">{''.join(f'<a href="#{s}">{n}</a>' for s, n, _, _ in FAMILIAS)}</nav>
    <select id="eq-linea" aria-label="Filtrar por línea">
      <option value="todas">Todas las líneas</option>
      <option value="economica">Económica (Trivium Pro)</option>
      <option value="premium">Premium (importadas)</option>
    </select>
  </div>
</div>

{chr(10).join(secciones)}

<section class="cta-banner">
  <div class="container">
    <h2>¿No sabés cuál elegir?</h2>
    <p>Te asesoramos según tu taller, tu espacio y tu presupuesto.</p>
    <a class="btn btn--primary btn--lg" href="../contacto/">Hablar con un asesor</a>
  </div>
</section>

'''
    d = os.path.join(ROOT, 'equipos'); os.makedirs(d, exist_ok=True)
    open(os.path.join(d, 'index.html'), 'w', encoding='utf-8').write(
        cabeza + cuerpo + pie.replace('</body>', JS + '</body>', 1))
    print('✔ equipos/', {s: sum(1 for p in data["products"] if de_familia(p, s) and p.get("image")) for s, *_ in FAMILIAS})


if __name__ == '__main__':
    main()
