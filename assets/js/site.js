/* Trivium Pro — shared site JS
   - injects header/footer/wa-float partials
   - renders catalog data dynamically
   - builds WhatsApp consultation links
*/

window.TRIVIUM = {
  whatsapp: "5491127015294",
  whatsappDisplay: "+54 9 11 2701-5294",
  email: "info@trivium.ar",
  brand: "Trivium Pro",
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
  'challenger-lifts': 'assets/img/marcas/logo-challenger-lifts.svg',
  'direct-lift':  'assets/img/marcas/logo-direct-lift.svg',
  'forward-lift': 'assets/img/marcas/logo-forward-lift.svg',
  'trivium-pro':  'assets/img/marcas/logo-trivium-pro.svg',
  // Existía el archivo en assets/img/marcas/ pero faltaba acá: Prevost nunca
  // mostraba su logo en ningún lado por este olvido.
  'prevost':      'assets/img/marcas/logo-prevost.svg',
  // Logo raster (PNG/WebP, no SVG): se pasó como imagen.
  'haweka':       'assets/img/marcas/logo-haweka.webp',
};

const MAIN_BRANDS = ['rotary-lift', 'hofmann', 'challenger-lifts', 'direct-lift', 'trivium-pro'];

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
    const name = { 'rotary-lift': 'Rotary Lift', 'hofmann': 'Hofmann', 'challenger-lifts': 'Challenger Lifts', 'direct-lift': 'Direct Lift', 'forward-lift': 'Forward Lift', 'trivium-pro': 'Trivium Pro' }[slug];
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
        <a class="brand" href="${root}" aria-label="Trivium Pro">
          <img src="${root}assets/img/logo-trivium.svg" alt="Trivium Pro" class="logo-img">
        </a>
        <ul class="nav-links">${links}</ul>
        <div class="nav-cta">
          <!-- El carrito sólo se muestra cuando tiene algo: lo prende
               tienda.js. En las páginas donde no se vende nada, un carrito
               vacío en el header es ruido. -->
          <button class="tn-navcart" id="tn-navcart" aria-label="Ver carrito">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="9" cy="20" r="1.5"/><circle cx="18" cy="20" r="1.5"/><path d="M2 3h3l2.7 12.4a2 2 0 0 0 2 1.6h7.7a2 2 0 0 0 2-1.6L21 7H6"/></svg>
            <span class="b">0</span>
          </button>
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
        
        <div class="mobile-menu-section" style="padding-bottom:20px; margin-bottom:4px;">
          <h5>Contacto</h5>
          <a href="mailto:${TRIVIUM.email}" class="contact-link">${ICONS.mail} ${TRIVIUM.email}</a>
          <a href="${waLink()}" class="contact-link">${ICONS.wa} ${TRIVIUM.whatsappDisplay}</a>
        </div>

        <div class="mobile-menu-section">
          <h5>Categorías</h5>
          <div class="mobile-cat-list">
            ${(main[0].sub||[]).slice(0,4).map(([t,h]) => {
              const slug = h.split('/')[1];
              const icon = CAT_ICONS[slug] ? `<img src="${root}${CAT_ICONS[slug]}" class="cat-icon" alt="">` : '';
              return `<a href="${root}${h}" class="bold">${icon}<strong>${t}</strong></a>`;
            }).join('')}
            ${(main[0].sub||[]).slice(4).map(([t,h]) => `<a href="${root}${h}">${t}</a>`).join('')}
          </div>
        </div>

        <div class="mobile-menu-section">
          <h5>Trivium</h5>
          ${main.slice(1).map(l => `<a href="${l.href}">${l.label}</a>`).join('')}
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
              <img src="${root}assets/img/logo-trivium.svg" alt="Trivium Pro" height="32" style="display:block;width:auto;">
            </div>
            <p class="tagline">Importadores y distribuidores oficiales de equipamiento profesional para talleres y concesionarias en Argentina.</p>
            <div class="footer-socials">
              <a href="https://www.instagram.com/trivium.center/" target="_blank" rel="noopener" aria-label="Instagram">
                <svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zM12 0C8.741 0 8.333.014 7.053.072 2.695.272.273 2.69.073 7.052.014 8.333 0 8.741 0 12c0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.981 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98C15.668.014 15.259 0 12 0zm0 5.838a6.162 6.162 0 100 12.324 6.162 6.162 0 000-12.324zM12 16a4 4 0 110-8 4 4 0 010 8zm6.406-11.845a1.44 1.44 0 100 2.881 1.44 1.44 0 000-2.881z"/></svg>
              </a>
              <a href="https://www.facebook.com/profile.php?id=61571497817317" target="_blank" rel="noopener" aria-label="Facebook">
                <svg viewBox="0 0 24 24" fill="currentColor"><path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/></svg>
              </a>
              <a href="https://www.youtube.com/channel/UCkyhOuIT5A9nZ7qCAszVIaQ" target="_blank" rel="noopener" aria-label="YouTube">
                <svg viewBox="0 0 24 24" fill="currentColor"><path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/></svg>
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
              <li><a href="${root}guias/">Guías de compra</a></li>
              <li><a href="${root}origen/">Origen y marcado CE</a></li>
              <li><a href="${root}zonas/">Envíos y cobertura</a></li>
              <li><a href="${root}contacto/">Contacto</a></li>
            </ul>
          </div>

          <div>
            <h5>Compra y políticas</h5>
            <ul class="footer-links">
              <li><a href="${root}envios-y-entregas/">Envíos y entregas</a></li>
              <li><a href="${root}cambios-devoluciones-y-arrepentimiento/">Cambios y devoluciones</a></li>
              <li><a href="${root}cambios-devoluciones-y-arrepentimiento/#arrepentimiento">Botón de arrepentimiento</a></li>
              <li><a href="${root}terminos-y-condiciones/">Términos y condiciones</a></li>
              <li><a href="${root}politica-de-privacidad/">Política de privacidad</a></li>
              <li><a href="https://www.argentina.gob.ar/produccion/defensadelconsumidor/formulario" target="_blank" rel="noopener">Defensa del Consumidor</a></li>
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
                <a href="https://wa.me/5493513994200" target="_blank" rel="noopener">
                  <span class="icon">${ICONS.wa}</span>
                  <span class="text">+54 9 351 399-4200 (Ventas)</span>
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
            © ${new Date().getFullYear()} Trivium Pro — Una unidad de
            <a href="https://trivium.ar/" style="color:inherit">Trivium Center</a>.
          </div>
          <div class="origin">
            Equipamiento Industrial · Hecho en Argentina ·
            <a href="https://neumaticos.trivium.ar/" style="color:inherit">Neumáticos Trivium</a>
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
    script.src = rootPath() + 'data/catalog.js?v=20261022f';
    script.onload = () => {
      CATALOG = window.CATALOG_DATA;
      resolve(CATALOG);
    };
    script.onerror = reject;
    document.head.appendChild(script);
  });
}

// ---------- Precios públicos (fichas de producto) ----------
let PUBLIC_PRICES = null;
async function loadPublicPrices() {
  if (PUBLIC_PRICES) return PUBLIC_PRICES;
  const r = await fetch(rootPath() + 'data/prices-publico.json');
  PUBLIC_PRICES = await r.json();
  return PUBLIC_PRICES;
}
async function getOfficialRate() {
  try {
    const r = await fetch('https://dolarapi.com/v1/dolares/oficial', { cache: 'no-store' });
    const j = await r.json();
    if (j && j.venta) return j.venta;
  } catch (e) {}
  return 1520; // valor de referencia si falla la consulta en vivo
}

// Precio final (con IVA) para las tarjetas de grilla. null si el equipo no
// tiene precio público o está marcado 'tienda: false' (precio sin confirmar,
// ver data/prices-publico.json) — no se muestra un número que no se sostiene.
let PRICE_RATE = null;
async function ensureCardPrices() {
  if (PRICE_RATE != null) return;
  await loadPublicPrices();
  PRICE_RATE = await getOfficialRate();
}
function cardPrice(sku, enFicha) {
  const rec = PUBLIC_PRICES && PUBLIC_PRICES.items[sku];
  if (!rec || (rec.tienda === false && !enFicha) || PRICE_RATE == null) return null;
  const base = rec.fixed_ars != null ? rec.fixed_ars : rec.usd * PRICE_RATE;
  const iva = rec.iva != null ? rec.iva : PUBLIC_PRICES.meta.default_iva;
  const total = base * (1 + iva / 100);
  const paso = rec.redondeo || 1; // 'redondeo': 1000 → al mil más cercano
  return { total: Math.round(total / paso) * paso, iva };
}
function cardPriceHtml(sku, enFicha) {
  const pr = cardPrice(sku, enFicha);
  if (!pr) return '';
  const monto = '$ ' + new Intl.NumberFormat('es-AR', { maximumFractionDigits: 0 }).format(pr.total);
  const ivaLbl = (Number.isInteger(pr.iva) ? pr.iva : String(pr.iva).replace('.', ',')) + '%';
  const nota = enFicha ? ' · Instalación no incluida' : '';
  return `<div class="price-tag">${monto}<span>IVA ${ivaLbl} incluido${nota}</span></div>`;
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

// Sellos de origen y conformidad (campo "badges" del producto). Para sumar un
// país: bandera en assets/img/iconos/origen/, una entrada acá y en
// ORIGIN_BADGES de scripts/generate_pretty_urls.py, y su página en
// scripts/origenes_content.py. El texto va en una línea debajo de la bandera.
// "href" es la página /origen/... a la que lleva el sello; "plain" saca el
// marco gris de la bandera (el logo CE ya trae su forma).
const ORIGIN_BADGES = {
  'made-in-usa':     { file: 'usa.svg',     text: 'Made in USA',     href: 'origen/estados-unidos/', name: 'Estados Unidos' },
  'made-in-italy':   { file: 'italy.svg',   text: 'Made in Italy',   href: 'origen/italia/',         name: 'Italia' },
  'made-in-germany': { file: 'germany.svg', text: 'Made in Germany', href: 'origen/alemania/',       name: 'Alemania' },
  'made-in-sweden':  { file: 'sweden.svg',  text: 'Made in Sweden',  href: 'origen/suecia/',         name: 'Suecia' },
  'made-in-taiwan':  { file: 'taiwan.svg',  text: 'Made in Taiwan',  href: 'origen/taiwan/',         name: 'Taiwán' },
  'ce-ue':           { file: 'ce.webp',     text: 'Marcado CE',      href: 'origen/marcado-ce/',     name: 'Marcado CE', plain: true },
};
// asLink: solo en la ficha del producto el sello es un <a> hacia /origen/...
// En las tarjetas de la grilla es una etiqueta informativa, sin clic: la tarjeta
// entera es un enlace al producto y, sobre todo en celular, un toque sobre el
// sello no tiene que llevar a otra página sin querer.
function originBadgeHtml(p, asLink) {
  const b = (p.badges || []).map(id => ORIGIN_BADGES[id]).find(Boolean);
  if (!b) return '';
  // El texto es un <svg> con textLength: se estira al ancho exacto de la bandera.
  const t = b.text.toUpperCase(), w = Math.round(t.length * 4.8);
  const inner = `<img src="${rootPath()}assets/img/iconos/origen/${b.file}" alt=""><svg class="ob-text" viewBox="0 0 ${w} 9" aria-hidden="true"><text x="0" y="7.3" textLength="${w}" lengthAdjust="spacingAndGlyphs">${t}</text></svg>`;
  const cls = 'origin-badge' + (b.plain ? ' origin-badge--plain' : '');
  if (!asLink) return `<span class="${cls}" title="${b.text}">${inner}</span>`;
  const label = b.plain ? 'Qué es el marcado CE' : `Equipos con origen ${b.name}`;
  // Marcado CE: cuadro explicativo (hover en escritorio; un toque en el celular, y otro toque abre la página).
  const pop = b.plain ? `<span class="ob-pop" role="tooltip"><b>Marcado CE</b>Declaración del fabricante de que el producto cumple la normativa de la Unión Europea en seguridad, salud y medio ambiente.<em class="ob-pop-t">Tocá de nuevo para más información</em><em class="ob-pop-h">Clic para más información</em></span>` : '';
  return `<a class="${cls}" href="${rootPath()}${b.href}" aria-label="${label}" ${b.plain ? 'aria-haspopup="true"' : ''}>${inner}${pop}</a>`;
}

// Certificación ALI: enlaza a la ficha del modelo en el directorio oficial de ALI.
// "family" = el modelo del directorio es la familia (X = variantes) a la que pertenece el equipo.
function aliUrl(a) {
  return 'https://www.autolift.org/ali-directory-of-certified-car-lifts/search-certified-car-lifts/?productCat=' + a.cat +
    '&manufac=' + a.manufac + '&ModNum&rateval=%3D&rateload&searchsubmit=Search&lift_id=' + a.lift_id;
}
function aliCertHtml(p) {
  const a = p.ali; if (!a) return '';
  const fecha = a.date ? a.date.slice(0, 4) : '';
  return `<a class="pd-ali" href="${aliUrl(a)}" target="_blank" rel="noopener noreferrer" aria-label="Ver la certificación ALI de ${a.model} en el directorio de ALI">
    <img src="${rootPath()}assets/img/iconos/ali-validated.png" alt="" width="56" height="56" onerror="this.remove()">
    <span><b>Certificación ALI</b><small>Modelo certificado ${a.model}${a.family ? ' (familia)' : ''}${fecha ? ' · desde ' + fecha : ''}</small><em>Ver certificado en el directorio de ALI ↗</em></span></a>`;
}

// <li> de la barra lateral "Origen": un item por sello con su cantidad de equipos.
function originSidebarHtml(activeId) {
  return Object.entries(ORIGIN_BADGES).map(([id, b]) => {
    const n = CATALOG.products.filter(p => (p.badges || []).includes(id)).length;
    return `<li><a class="${id === activeId ? 'active' : ''}" href="${rootPath()}${b.href}">${b.name}<b>${n}</b></a></li>`;
  }).join('');
}

// Miniatura (scripts/generate_thumbs.py): carpeta t/ junto a la original; si no existe, se usa la original.
function thumbSrc(path) { return path.replace(/^(assets\/img\/(?:productos|blog)\/)([^/]+)$/, '$1t/$2'); }

function productCard(p, idx) {
  // Las primeras fotos son lo primero que se ve (LCP): sin lazy, la primera con prioridad alta.
  const eager = idx === 0 ? 'fetchpriority="high"' : (idx > 0 && idx < 4 ? '' : 'loading="lazy"');
  const brand = brandById(p.brand);
  const msg = `Hola Trivium, quiero consultar por: ${p.name} (${p.sku})`;
  const img = p.image
    ? `<img src="${rootPath()}${thumbSrc(p.image)}" alt="${p.name}" width="480" height="480" ${eager} onerror="if(this.dataset.f!=='1'){this.dataset.f='1';this.src='${rootPath()}${p.image}';return}this.style.display='none';this.nextElementSibling.style.display='grid'">
       <span style="display:none">Imagen / ${p.sku}</span>`
    : `<span>Imagen / ${p.sku}</span>`;
  let specHtml = '';
  if (p.category.includes('elevador')) {
    specHtml = `
      <div class="spec">
        <span>CAP <b>${p.capacity || '—'}</b></span>
        <span>ALT <b>${p.lift_height || '—'}</b></span>
      </div>`;
  } else {
    specHtml = `
      <div class="spec" style="visibility: hidden">
        <span>— <b>—</b></span>
        <span>— <b>—</b></span>
      </div>`;
  }

  const brandTag = `<span class="brand-tag">${brand.name}</span>`;
  // Logo de marca sobre la foto, cuando la marca tiene uno (BRAND_LOGOS). Las
  // que no tienen (Haweka, Josam, Prevost...) se quedan con el brandTag de
  // texto de abajo, que ya existía.
  const thumbBrand = brand.logo
    ? `<span class="thumb-brand"><img src="${rootPath()}${brand.logo}" alt="${brand.name}"></span>` : '';
  return `
    <a class="prod-card" href="${productUrl(p)}">
      <div class="thumb">
        ${img}
        ${thumbBrand}
        ${originBadgeHtml(p)}
      </div>
      <div class="body">
        ${brandTag}
        <h3>${p.name}</h3>
        ${specHtml}
        ${cardPriceHtml(p.sku)}
      </div>
    </a>`;
}

async function renderGrid(containerSel, products) {
  const el = document.querySelector(containerSel);
  if (!el) return;
  if (!products.length) {
    el.innerHTML = `<p class="muted">No hay productos en esta categoría todavía. <a href="${waLink('Hola, quiero consultar por productos.')}" style="color:var(--accent)">Consultá por WhatsApp</a>.</p>`;
    return;
  }
  // Se cargan precios y dólar antes de pintar: así ninguna tarjeta parpadea
  // sin precio y después lo agrega.
  await ensureCardPrices();
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
    script.src = rootPath() + 'data/blog.js?v=20261022f';
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
    ? `<img src="${rootPath()}${thumbSrc(p.image)}" alt="${p.title}" width="640" height="360" loading="lazy" onerror="if(this.dataset.f!=='1'){this.dataset.f='1';this.src='${rootPath()}${p.image}'}" style="width:100%;height:100%;object-fit:cover;">` 
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

// Marcado CE en el celular: el primer toque muestra el cuadro explicativo, el segundo abre la página.
document.addEventListener('click', function (e) {
  const badge = e.target.closest ? e.target.closest('.origin-badge--plain[aria-haspopup]') : null;
  const abiertos = document.querySelectorAll('.origin-badge.ob-open');
  if (!badge) { abiertos.forEach(b => b.classList.remove('ob-open')); return; }
  if (window.matchMedia && window.matchMedia('(hover: none)').matches && !badge.classList.contains('ob-open')) {
    e.preventDefault(); abiertos.forEach(b => b.classList.remove('ob-open')); badge.classList.add('ob-open');
  }
});

// Fichas PDF en Android: el navegador no las abre, las descarga. Se abren en un visor propio (/ficha/) y ahí
// se puede descargar. En iPhone y escritorio el PDF se abre directo.
document.addEventListener('click', function (e) {
  const a = e.target.closest ? e.target.closest('a[href$=".pdf"]') : null;
  if (!a || !/Android/i.test(navigator.userAgent) || a.hasAttribute('download')) return;
  let u; try { u = new URL(a.getAttribute('href'), location.href); } catch (_) { return; }
  if (u.origin !== location.origin || !/^\/assets\/pdf\/[A-Za-z0-9._-]+\.pdf$/.test(u.pathname)) return;
  e.preventDefault();
  location.href = '/ficha/?f=' + encodeURIComponent(u.pathname.slice(1));
});

// Compartir la ficha técnica: en el celular abre el menú nativo con el PDF adjunto (WhatsApp, mail...);
// si el navegador no puede adjuntar archivos comparte el enlace, y si no hay menú nativo abre WhatsApp.
document.addEventListener('click', async function (e) {
  const b = e.target.closest ? e.target.closest('[data-share-ficha]') : null;
  if (!b) return;
  const url = new URL(b.getAttribute('data-share-ficha'), location.href).href;
  const nombre = (document.querySelector('h1') || {}).textContent || 'Ficha técnica';
  const titulo = 'Ficha técnica ' + nombre.trim();
  const texto = titulo + ' — Trivium Pro';
  try {
    if (navigator.canShare && navigator.share) {
      const r = await fetch(url);
      const file = new File([await r.blob()], url.split('/').pop(), { type: 'application/pdf' });
      if (navigator.canShare({ files: [file] })) { await navigator.share({ files: [file], title: titulo, text: texto }); return; }
    }
    if (navigator.share) { await navigator.share({ title: titulo, text: texto, url }); return; }
  } catch (err) { if (err && err.name === 'AbortError') return; }
  window.open('https://wa.me/?text=' + encodeURIComponent(texto + '\n' + url), '_blank', 'noopener');
});
