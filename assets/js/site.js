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

// Brand logos map (slug → image path relative to root)
const BRAND_LOGOS = {
  'rotary-lift':  'assets/img/marcas/logo-rotary-lift.svg',
  'hofmann':      'assets/img/marcas/logo-hofmann.svg',
  'direct-lift':  'assets/img/marcas/logo-direct-lift.svg',
  'forward-lift': 'assets/img/marcas/logo-forward-lift.svg',
  'trivium-pro':  'assets/img/marcas/logo-trivium-pro.svg',
};

const MAIN_BRANDS = ['rotary-lift', 'hofmann', 'direct-lift', 'trivium-pro'];

const CAT_ICONS = {
  'elevadores': 'assets/img/iconos/elevadores.svg',
  'alineadoras': 'assets/img/iconos/alineadoras.svg',
  'balanceadoras': 'assets/img/iconos/balanceadoras.svg',
  'desarmadoras': 'assets/img/iconos/desarmadoras.svg'
};

function renderBrandBar() {
  const root = rootPath();
  const items = MAIN_BRANDS.map(slug => {
    const logo = BRAND_LOGOS[slug];
    const name = { 'rotary-lift': 'Rotary Lift', 'hofmann': 'Hofmann', 'direct-lift': 'Direct Lift', 'forward-lift': 'Forward Lift', 'trivium-pro': 'Trivium Pro' }[slug];
    return `<a class="brand-bar__item" href="${root}marca/${slug}/" aria-label="${name}" data-slug="${slug}">
      <img src="${root}${logo}" alt="${name}" loading="lazy">
    </a>`;
  }).join('');
  return `<div class="brand-bar" id="brand-bar"><div class="container brand-bar__inner">${items}</div></div>`;
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
        ['Muebles de Taller', 'categoria/muebles-taller/']
      ]
    },
    { href: `${root}marcas/`, label: 'Marcas', key: 'marcas' },
    { href: `${root}instalacion-posventa-y-servicios/`, label: 'Servicios', key: 'servicios' },
    { href: `${root}blog/`, label: 'Blog', key: 'blog' },
    { href: `${root}nosotros/`, label: 'Nosotros', key: 'nosotros' },
    { href: `${root}contacto/`, label: 'Contacto', key: 'contacto' }
  ];
  const subHtml = (items) => {
    const primary = items.slice(0, 4);
    const secondary = items.slice(4);
    const primaryHtml = primary.map(([t, h]) => {
      const slug = h.split('/')[1];
      const icon = CAT_ICONS[slug] ? `<img src="${root}${CAT_ICONS[slug]}" class="cat-icon" alt="">` : '';
      return `<a href="${root}${h}" class="submenu-primary">${icon}<strong>${t}</strong></a>`;
    }).join('');
    const sepHtml = secondary.length ? `<div class="submenu-sep"></div>` : '';
    const secondaryHtml = secondary.map(([t, h]) => `<a href="${root}${h}">${t}</a>`).join('');
    return `<div class="submenu">${primaryHtml}${sepHtml}${secondaryHtml}</div>`;
  };
  const links = main.map(l =>
    `<li class="${l.sub ? 'has-menu' : ''}">
       <a href="${l.href}" class="${active===l.key?'active':''}">${l.label}</a>
       ${l.sub ? subHtml(l.sub) : ''}
     </li>`).join('');

  const header = `
    <header class="header" id="main-header">
      <div class="container nav">
        <button class="btn-burger" aria-label="Menú" onclick="toggleMobileNav()">${ICONS.menu}</button>
        <a class="brand" href="${root}" aria-label="Trivium Center">
          <img src="${root}assets/img/logo-trivium.svg" alt="Trivium Center" class="logo-img">
        </a>
        <ul class="nav-links">${links}</ul>
        <div class="nav-cta">
          <a class="btn btn--ghost btn--sm hide-sm" href="${root}contacto/">Pedir cotización</a>
          <a class="btn btn--primary btn--sm btn--wa-red" href="${waLink('Hola, quiero hacer una consulta.')}">${ICONS.wa}<span class="nav-wa-text"> WhatsApp</span></a>
        </div>
      </div>
    </header>
    <div class="mobile-nav" id="mobileNav" onclick="if(event.target.id==='mobileNav')toggleMobileNav()">
      <div class="panel">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:24px;">
          <img src="${root}assets/img/logo-trivium.svg" alt="Trivium" height="24">
          <button class="btn-burger" onclick="toggleMobileNav()">${ICONS.close}</button>
        </div>
        
        <div class="mobile-menu-section">
          <h5>Categorías</h5>
          <div class="mobile-cat-list">
            ${(main[0].sub||[]).slice(0,4).map(([t,h]) => {
              const slug = h.split('/')[1];
              const icon = CAT_ICONS[slug] ? `<img src="${root}${CAT_ICONS[slug]}" class="cat-icon" alt="">` : '';
              return `<a href="${root}${h}" class="bold">${icon}<strong>${t}</strong></a>`;
            }).join('')}
            <div class="sep"></div>
            ${(main[0].sub||[]).slice(4).map(([t,h]) => `<a href="${root}${h}">${t}</a>`).join('')}
          </div>
        </div>

        <div class="mobile-menu-section">
          <h5>Trivium</h5>
          ${main.slice(1).map(l => `<a href="${l.href}">${l.label}</a>`).join('')}
        </div>

        <div class="mobile-menu-section" style="margin-top:auto; padding-top:24px; border-top:1px solid var(--line);">
          <h5>Contacto</h5>
          <a href="mailto:${TRIVIUM.email}" class="contact-link">${ICONS.mail} ${TRIVIUM.email}</a>
          <a href="${waLink()}" class="contact-link">${ICONS.wa} ${TRIVIUM.whatsappDisplay}</a>
        </div>
      </div>
    </div>`;

  return header;
}

// Add scroll listener for header shrinking
window.addEventListener('scroll', () => {
  const header = document.getElementById('main-header');
  if (!header) return;
  if (window.scrollY > 20) {
    header.classList.add('scrolled');
  } else {
    header.classList.remove('scrolled');
  }
});

function toggleMobileNav() {
  document.getElementById('mobileNav').classList.toggle('open');
}

function renderFooter() {
  const root = rootPath();
  return `
    <footer class="footer">
      <div class="container">
        <div class="grid">
          <div class="footer-brand-col">
            <div class="brand" style="margin-bottom:16px">
              <img src="${root}assets/img/logo-trivium.svg" alt="Trivium Center" height="32" style="display:block;width:auto;filter:brightness(0) invert(1)">
            </div>
            <p class="tagline">Importadores y distribuidores oficiales de equipamiento profesional para talleres y concesionarias en Argentina.</p>
            <div class="footer-socials">
              <a href="https://instagram.com/triviumcenter" target="_blank" aria-label="Instagram">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="2" width="20" height="20" rx="5" ry="5"></rect><path d="M16 11.37A4 4 0 1 1 12.63 8 4 4 0 0 1 16 11.37z"></path><line x1="17.5" y1="6.5" x2="17.51" y2="6.5"></line></svg>
              </a>
            </div>
          </div>
          
          <div>
            <h5>Catálogo</h5>
            <ul class="footer-links">
              <li><a href="${root}categoria/elevadores/">Elevadores</a></li>
              <li><a href="${root}categoria/alineadoras/">Alineadoras</a></li>
              <li><a href="${root}categoria/balanceadoras/">Balanceadoras</a></li>
              <li><a href="${root}categoria/desarmadoras/">Desarmadoras</a></li>
              <li><a href="${root}categoria/muebles-taller/">Muebles de Taller</a></li>
            </ul>
          </div>

          <div>
            <h5>La Empresa</h5>
            <ul class="footer-links">
              <li><a href="${root}nosotros/">Nosotros</a></li>
              <li><a href="${root}marcas/">Marcas</a></li>
              <li><a href="${root}instalacion-posventa-y-servicios/">Servicios y Posventa</a></li>
              <li><a href="${root}contacto/">Contacto</a></li>
            </ul>
          </div>

          <div class="footer-contact-col">
            <h5>Contacto Directo</h5>
            <ul class="footer-contact-list">
              <li>
                <a href="mailto:${TRIVIUM.email}">
                  <span class="icon">${ICONS.mail}</span>
                  <span class="text">${TRIVIUM.email}</span>
                </a>
              </li>
              <li>
                <a href="${waLink()}">
                  <span class="icon">${ICONS.wa}</span>
                  <span class="text">${TRIVIUM.whatsappDisplay}</span>
                </a>
              </li>
              <li>
                <div class="hours">
                  <span class="icon">${ICONS.pin}</span>
                  <span class="text">Lunes a Viernes<br><b>9:00 a 18:00 hs</b></span>
                </div>
              </li>
            </ul>
          </div>
        </div>
        
        <div class="footer-bottom">
          <div class="legal">
            © ${new Date().getFullYear()} Trivium Center — Todos los derechos reservados.
          </div>
          <div class="origin">
            Equipamiento Industrial · Hecho en Argentina
          </div>
        </div>
      </div>
    </footer>
    <a class="wa-float" href="${waLink('Hola, quiero hacer una consulta.')}" target="_blank" rel="noopener">
      ${ICONS.wa} Consultar por WhatsApp
    </a>`;
}

function mountChrome(active) {
  const h = document.getElementById('site-header');
  const f = document.getElementById('site-footer');
  if (h) h.innerHTML = renderHeader(active) + renderBrandBar();
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
  const b = CATALOG.brands.find(b => b.slug === slug) || { name: '—', note: '', slug: '' };
  b.logo = BRAND_LOGOS[slug] || null;
  return b;
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
  let specHtml = '';
  if (p.category.includes('elevador')) {
    specHtml = `
      <div class="spec">
        <span>CAP <b>${p.capacity || '—'}</b></span>
        <span>ALT <b>${p.lift_height || '—'}</b></span>
      </div>`;
  } else if (p.category.includes('balanceadora')) {
    specHtml = `
      <div class="spec">
        <span title="Diámetro de llanta">DIA <b>${p.rim_diameter || '—'}</b></span>
        <span title="Precisión de equilibrado">PRE <b>${p.precision || '—'}</b></span>
      </div>`;
  } else if (p.category.includes('desarmadora')) {
    specHtml = `
      <div class="spec">
        <span title="Rango de sujeción">RAN <b>${p.clamping_range || '—'}</b></span>
        <span title="Peso de la máquina">PES <b>${p.capacity || '—'}</b></span>
      </div>`;
  } else {
    specHtml = `
      <div class="spec" style="visibility: hidden">
        <span>— <b>—</b></span>
        <span>— <b>—</b></span>
      </div>`;
  }

  const brandTag = `<span class="brand-tag">${brand.name}</span>`;
  return `
    <a class="prod-card" href="${productUrl(p)}">
      <div class="thumb">
        <div class="ribbon">${ribbons}</div>
        ${img}
      </div>
      <div class="body">
        ${brandTag}
        <h3>${p.name}</h3>
        ${specHtml}
      </div>
    </a>`;
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
