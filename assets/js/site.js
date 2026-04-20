/* Trivium Center — shared site JS
   - injects header/footer/wa-float partials
   - renders catalog data dynamically
   - builds WhatsApp consultation links
*/

window.TRIVIUM = {
  whatsapp: "5491127015294",
  whatsappDisplay: "+54 9 11 2701-5294",
  email: "info@trivium.ar",
  brand: "Trivium Center",
  cityLine: "Importadores y distribuidores oficiales — Argentina"
};

const ICONS = {
  arrow: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="square"><path d="M5 12h14M13 5l7 7-7 7"/></svg>',
  wa: '<svg viewBox="0 0 32 32" fill="currentColor"><path d="M16.003 3C9.373 3 4 8.373 4 15.003c0 2.388.696 4.613 1.893 6.486L4 29l7.76-1.84A11.946 11.946 0 0016.003 28C22.633 28 28 22.633 28 16c0-3.185-1.245-6.18-3.505-8.44A11.933 11.933 0 0016.003 3zm0 2c2.936 0 5.7 1.14 7.779 3.22A10.936 10.936 0 0127 15.997C27 22.072 22.072 27 16 27c-1.85 0-3.652-.465-5.253-1.35l-.378-.21-4.51 1.07 1.11-4.38-.24-.395A10.93 10.93 0 015 15C5 8.925 9.925 4 16.003 4zm-4.7 5.26c-.23 0-.6.09-.914.43-.313.34-1.19 1.164-1.19 2.837 0 1.673 1.219 3.29 1.39 3.515.17.227 2.41 3.754 5.94 5.28 2.934 1.27 3.53 1.017 4.17.96.64-.06 2.07-.85 2.36-1.67.29-.82.29-1.52.2-1.67-.086-.15-.313-.24-.656-.41-.343-.17-2.03-1-2.344-1.11-.314-.114-.544-.17-.77.17-.228.34-.886 1.11-1.087 1.34-.2.23-.4.26-.743.09-.343-.17-1.45-.534-2.76-1.7-1.02-.91-1.708-2.03-1.907-2.37-.2-.343-.02-.528.15-.7.154-.152.343-.396.514-.596.17-.2.228-.34.342-.57.114-.228.057-.427-.028-.6-.086-.17-.77-1.85-1.05-2.534-.28-.68-.565-.58-.77-.6l-.656-.01z"/></svg>',
  phone: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6A19.79 19.79 0 0 1 2.12 4.18 2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72c.13.96.37 1.9.72 2.81a2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45c.91.35 1.85.59 2.81.72a2 2 0 0 1 1.72 2z"/></svg>',
  mail: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 6h16v12H4z"/><path d="m4 6 8 7 8-7"/></svg>',
  pin: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0z"/><circle cx="12" cy="10" r="3"/></svg>',
  menu: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4"><path d="M4 7h16M4 12h16M4 17h16"/></svg>',
  close: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4"><path d="M6 6l12 12M18 6L6 18"/></svg>',
  search: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg>'
};

function rootPath() {
  // returns '' or '../' based on depth — simple heuristic via <base data-root>
  const b = document.querySelector('meta[name="tv-root"]');
  return b ? b.content : '';
}

function waLink(message) {
  const base = `https://wa.me/${TRIVIUM.whatsapp}`;
  if (!message) return base;
  return base + '?text=' + encodeURIComponent(message);
}

function renderHeader(active) {
  const root = rootPath();
  const main = [
    { href: `${root}catalogo/`, label: 'Catálogo', key: 'catalogo',
      sub: [
        ['Elevadores', 'categoria/elevadores/'],
        ['Alineadoras', 'categoria/alineadoras/'],
        ['Balanceadoras', 'categoria/balanceadoras/'],
        ['Desarmadoras', 'categoria/desarmadoras/'],
        ['Herramientas Neumáticas', 'categoria/herramientas-neumaticas/'],
        ['Lubricación', 'categoria/lubricacion/'],
        ['Muebles de Taller', 'categoria/muebles-taller/'],
        ['Aire Comprimido Prevost', 'categoria/aire-comprimido/'],
        ['Alineación de Faros', 'categoria/alineacion-faros/']
      ]
    },
    { href: `${root}marcas/`, label: 'Marcas', key: 'marcas' },
    { href: `${root}instalacion-posventa-y-servicios/`, label: 'Servicios', key: 'servicios' },
    { href: `${root}blog.html`, label: 'Blog', key: 'blog' },
    { href: `${root}nosotros/`, label: 'Nosotros', key: 'nosotros' },
    { href: `${root}contacto/`, label: 'Contacto', key: 'contacto' }
  ];
  const subHtml = (items) =>
    `<div class="submenu">${items.map(([t, h]) => `<a href="${root}${h}">${t}</a>`).join('')}</div>`;
  const links = main.map(l =>
    `<li class="${l.sub ? 'has-menu' : ''}">
       <a href="${l.href}" class="${active===l.key?'active':''}">${l.label}</a>
       ${l.sub ? subHtml(l.sub) : ''}
     </li>`).join('');

  const topbar = `
    <div class="topbar">
      <div class="container row">
        <div><span class="muted">★ Distribuidores oficiales</span> <span class="sep">/</span> <span>Rotary · Hofmann · Direct Lift · Forward · Prevost</span></div>
        <div class="hide-sm">
          <a href="mailto:${TRIVIUM.email}">${TRIVIUM.email}</a>
          <span class="sep">/</span>
          <a href="${waLink()}">${TRIVIUM.whatsappDisplay}</a>
        </div>
      </div>
    </div>`;

  const header = `
    <header class="header">
      <div class="container nav">
        <a class="brand" href="${root}">
          <span class="mark">T</span>
          <span>Trivium<br><small>CENTER / AR</small></span>
        </a>
        <ul class="nav-links">${links}</ul>
        <div class="nav-cta">
          <a class="btn btn--ghost btn--sm hide-sm" href="${root}contacto/">Pedir cotización</a>
          <a class="btn btn--primary btn--sm" href="${waLink('Hola, quiero hacer una consulta.')}">${ICONS.wa} WhatsApp</a>
          <button class="btn-burger" aria-label="Menú" onclick="toggleMobileNav()">${ICONS.menu}</button>
        </div>
      </div>
    </header>
    <div class="mobile-nav" id="mobileNav" onclick="if(event.target.id==='mobileNav')toggleMobileNav()">
      <div class="panel">
        <div style="display:flex;justify-content:space-between;align-items:center;">
          <b class="mono" style="letter-spacing:.2em;color:var(--text-mute)">MENÚ</b>
          <button class="btn-burger" onclick="toggleMobileNav()">${ICONS.close}</button>
        </div>
        <h5>Navegación</h5>
        ${main.map(l => `<a href="${l.href}">${l.label}</a>`).join('')}
        <h5>Categorías</h5>
        ${(main[0].sub||[]).map(([t,h]) => `<a href="${root}${h}">${t}</a>`).join('')}
        <h5>Contacto</h5>
        <a href="mailto:${TRIVIUM.email}">${TRIVIUM.email}</a>
        <a href="${waLink()}">WhatsApp ${TRIVIUM.whatsappDisplay}</a>
      </div>
    </div>`;

  return topbar + header;
}

function toggleMobileNav() {
  document.getElementById('mobileNav').classList.toggle('open');
}

function renderFooter() {
  const root = rootPath();
  return `
    <footer class="footer">
      <div class="container">
        <div class="grid">
          <div>
            <div class="brand">
              <span class="mark" style="display:inline-grid;place-items:center;width:36px;height:36px;background:var(--accent);font-family:var(--display);vertical-align:middle;margin-right:10px;">T</span>
              <span style="font-family:var(--display);font-size:1.25rem;text-transform:uppercase;vertical-align:middle;">Trivium Center</span>
            </div>
            <p class="tagline">Soluciones para talleres y concesionarias. Importadores y distribuidores de equipamiento profesional en Argentina.</p>
            <p class="mono" style="font-size:.72rem;color:var(--text-mute);letter-spacing:.18em;text-transform:uppercase;margin-top:14px;">EST. — Buenos Aires, AR</p>
          </div>
          <div>
            <h5>Catálogo</h5>
            <ul>
              <li><a href="${root}categoria/elevadores/">Elevadores</a></li>
              <li><a href="${root}categoria/alineadoras/">Alineadoras</a></li>
              <li><a href="${root}categoria/balanceadoras/">Balanceadoras</a></li>
              <li><a href="${root}categoria/desarmadoras/">Desarmadoras</a></li>
              <li><a href="${root}categoria/lubricacion/">Lubricación</a></li>
              <li><a href="${root}categoria/aire-comprimido/">Aire Comprimido</a></li>
            </ul>
          </div>
          <div>
            <h5>Trivium</h5>
            <ul>
              <li><a href="${root}nosotros/">Nosotros</a></li>
              <li><a href="${root}marcas/">Marcas</a></li>
              <li><a href="${root}instalacion-posventa-y-servicios/">Servicios</a></li>
              <li><a href="${root}contacto/">Contacto</a></li>
            </ul>
          </div>
          <div>
            <h5>Contacto</h5>
            <ul>
              <li><a href="mailto:${TRIVIUM.email}">${TRIVIUM.email}</a></li>
              <li><a href="${waLink()}">${TRIVIUM.whatsappDisplay}</a></li>
              <li><span class="muted">Lun–Vie · 9 a 18 h</span></li>
            </ul>
          </div>
        </div>
        <div class="bottom">
          <span>© ${new Date().getFullYear()} Trivium Center — Todos los derechos reservados</span>
          <span>Sitio estático · Hecho en Argentina</span>
        </div>
      </div>
    </footer>
    <a class="wa-float" href="${waLink('Hola, quiero hacer una consulta.')}" target="_blank" rel="noopener">
      ${ICONS.wa} Consultar
    </a>`;
}

function mountChrome(active) {
  const h = document.getElementById('site-header');
  const f = document.getElementById('site-footer');
  if (h) h.innerHTML = renderHeader(active);
  if (f) f.innerHTML = renderFooter();
}

// ---------- Catalog ----------
let CATALOG = null;
async function loadCatalog() {
  if (CATALOG) return CATALOG;
  return new Promise((resolve, reject) => {
    const script = document.createElement('script');
    script.src = rootPath() + 'data/catalog.js';
    script.onload = () => {
      CATALOG = window.CATALOG_DATA;
      resolve(CATALOG);
    };
    script.onerror = reject;
    document.head.appendChild(script);
  });
}

function productUrl(p) { return `${rootPath()}producto/${encodeURIComponent(p.slug)}/`; }
function categoryUrl(slug) { return `${rootPath()}categoria/${encodeURIComponent(slug)}/`; }
function brandUrl(slug) { return `${rootPath()}marca/${encodeURIComponent(slug)}/`; }

function brandById(slug) {
  return CATALOG.brands.find(b => b.slug === slug) || { name: '—', note: '' };
}
function categoryById(slug) {
  return CATALOG.categories.find(c => c.slug === slug) || { name: '—' };
}

function productCard(p) {
  const brand = brandById(p.brand);
  const ribbons = (p.badges||[]).map(b => {
    const cls = b.toLowerCase().includes('oferta') ? 'chip--yellow'
              : b.toLowerCase().includes('nuevo') ? 'chip--green'
              : 'chip--accent';
    return `<span class="chip ${cls}">${b}</span>`;
  }).join('');
  const msg = `Hola Trivium, quiero consultar por: ${p.name} (${p.sku})`;
  const img = p.image
    ? `<img src="${rootPath()}${p.image}" alt="${p.name}" loading="lazy" onerror="this.style.display='none';this.nextElementSibling.style.display='grid'">
       <span style="display:none">Imagen / ${p.sku}</span>`
    : `<span>Imagen / ${p.sku}</span>`;
  return `
    <article class="prod-card">
      <a class="thumb" href="${productUrl(p)}">
        <div class="ribbon">${ribbons}</div>
        ${img}
      </a>
      <div class="body">
        <span class="brand-tag">${brand.name}</span>
        <h3><a href="${productUrl(p)}" style="color:inherit">${p.name}</a></h3>
        <div class="spec">
          <span>CAP <b>${p.capacity}</b></span>
          <span>ALT <b>${p.lift_height}</b></span>
        </div>
        <div class="actions">
          <a class="btn btn--primary" href="${waLink(msg)}" target="_blank" rel="noopener">${ICONS.wa} Consultar</a>
          <a class="btn btn--dark" href="${productUrl(p)}" aria-label="Ver ficha">${ICONS.arrow}</a>
        </div>
      </div>
    </article>`;
}

function renderGrid(containerSel, products) {
  const el = document.querySelector(containerSel);
  if (!el) return;
  if (!products.length) {
    el.innerHTML = `<p class="muted">No hay productos en esta categoría todavía. <a href="${waLink('Hola, quiero consultar por productos.')}" style="color:var(--accent)">Consultá por WhatsApp</a>.</p>`;
    return;
  }
  el.innerHTML = products.map(productCard).join('');
}

function getQuery(name) {
  const params = new URLSearchParams(location.search);
  if (params.has(name)) return params.get(name);
  
  // Try to infer from path: /producto/slug/ or /categoria/slug/
  const path = location.pathname;
  if (name === 'id' && path.includes('/producto/')) {
    return path.split('/producto/')[1].split('/')[0];
  }
  if (name === 'c' && path.includes('/categoria/')) {
    return path.split('/categoria/')[1].split('/')[0];
  }
  if (name === 'b' && path.includes('/marca/')) {
    return path.split('/marca/')[1].split('/')[0];
  }
  return null;
}

// ---------- Blog ----------
let BLOG = null;
async function loadBlog() {
  if (BLOG) return BLOG;
  return new Promise((resolve, reject) => {
    const script = document.createElement('script');
    script.src = rootPath() + 'data/blog.js';
    script.onload = () => {
      BLOG = window.BLOG_DATA;
      resolve(BLOG);
    };
    script.onerror = reject;
    document.head.appendChild(script);
  });
}

function blogUrl(post) { return `${rootPath()}${post.slug}/`; }

function blogCard(p) {
  const date = new Date(p.date).toLocaleDateString('es-AR', { day: '2-digit', month: 'long', year: 'numeric' });
  const img = p.image 
    ? `<img src="${rootPath()}${p.image}" alt="${p.title}" loading="lazy" style="width:100%;height:100%;object-fit:cover;">` 
    : `<div class="ph">Noticia</div>`;
  return `
    <article class="prod-card">
      <a class="thumb" href="${blogUrl(p)}" style="aspect-ratio:16/9">
        ${img}
      </a>
      <div class="body">
        <span class="brand-tag">${date}</span>
        <h3 style="font-size:1.15rem"><a href="${blogUrl(p)}" style="color:inherit">${p.title}</a></h3>
        <div class="excerpt" style="font-size:.9rem;color:var(--text-dim);margin-top:10px;display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden;">
          ${p.excerpt.replace(/<[^>]*>/g, '')}
        </div>
        <div class="actions" style="margin-top:20px">
          <a class="btn btn--dark btn--sm" href="${blogUrl(p)}">Leer más ${ICONS.arrow}</a>
        </div>
      </div>
    </article>`;
}

function renderBlogGrid(containerSel, posts) {
  const el = document.querySelector(containerSel);
  if (!el) return;
  el.innerHTML = posts.map(blogCard).join('');
}
