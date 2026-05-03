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
  cityLine: "Importadores y distribuidores oficiales — Argentina",
  env: (function() {
    const h = window.location.hostname;
    if (h === 'localhost' || h === '127.0.0.1' || h.startsWith('192.168.')) return 'local';
    if (h.endsWith('.vercel.app')) return 'staging';
    return 'production';
  })()
};

const ICONS = {
  arrow: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="square"><path d="M5 12h14M13 5l7 7-7 7"/></svg>',
  wa: '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/></svg>',
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
    { href: `${root}blog/`, label: 'Blog', key: 'blog' },
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
        <a class="brand" href="${root}" aria-label="Trivium Center">
          <img src="${root}assets/img/logo-trivium.svg" alt="Trivium Center" height="36" style="display:block;width:auto">
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
            <div class="brand" style="margin-bottom:12px">
              <img src="${root}assets/img/logo-trivium.svg" alt="Trivium Center" height="32" style="display:block;width:auto">
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
  
  // Try to infer from path
  const path = location.pathname;
  if (name === 'id') {
    if (path.includes('/producto/')) {
      return path.split('/producto/')[1].split('/')[0];
    }
    // Generic fallback for blog posts at root /slug/
    const parts = path.split('/').filter(Boolean);
    if (parts.length === 1 && !['catalogo','marcas','servicios','nosotros','contacto'].includes(parts[0])) {
      return parts[0];
    }
    // If it's the last part of the path and we are looking for id (used by blog)
    if (parts.length > 0) return parts[parts.length - 1];
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

function blogUrl(post) { return `${rootPath()}blog/${post.slug}/`; }

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
