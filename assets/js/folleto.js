/* Folleto/catálogo de equipos — renderer de /folleto-<secreto>/.
 *
 * Se configura con FOLLETO.render({...}) desde la página. Depende de site.js
 * (loadCatalog, categoryById, productUrl, rootPath, getQuery, TRIVIUM,
 * CAT_ICONS, ICONS) y de assets/css/folleto.css.
 *
 * El orden NO se reordena acá: las secciones siguen el orden de
 * catalog.categories y dentro de cada una los productos quedan como están en
 * catalog.json, igual que en /catalogo/. Cada ficha es un link a su página de
 * producto — salvo en modo selección (ver abajo), donde el click elige en vez
 * de navegar.
 *
 * Selección + link para compartir
 * --------------------------------
 * El vendedor toca "Buscar equipos" para entrar en modo selección: ahí
 * cualquier click en una ficha la marca (no navega), y un buscador filtra por
 * nombre/modelo/marca. Carga su nombre, WhatsApp, mail y opcionalmente una
 * foto; "Generar link" arma una URL con todo eso en la query string
 * (?sel=...&vn=...&vp=...&ve=...&vf=...) — no hay backend, así que todo el
 * estado vive en el link mismo. Quien lo abre ve sólo esos equipos y una
 * tarjeta con los datos del vendedor al pie de la portada, sin ninguna de las
 * herramientas de venta (esas son sólo para quien arma el link).
 */
window.FOLLETO = (function () {
  const fmtARS = (n) => '$ ' + new Intl.NumberFormat('es-AR', { maximumFractionDigits: 0 }).format(Math.round(n));
  // El catálogo usa '' y '—' indistintamente para "sin dato".
  const dato = (v) => (v && v !== '—' && v !== '-') ? v : null;
  const LS_VENDOR = 'tv_folleto_vendedor';

  // Sin tildes ni mayúsculas, para que "Rotary" encuentre "rotary lift" y
  // "alineacion" encuentre "alineación".
  const normalize = (s) => String(s || '')
    .normalize('NFD').replace(/[\u0300-\u036f]/g, '')
    .toLowerCase().trim();

  function topCategory(p) {
    const c = categoryById(p.category);
    const parent = c && c.parent ? categoryById(c.parent) : null;
    const top = parent || c || {};
    return { slug: top.slug || '', name: top.name || 'Otros' };
  }

  /* Cotización: se prefiere la del Worker para que el folleto muestre el mismo
     número que la tienda cobra. Si no está, se pide directo a dolarapi. */
  async function getRate() {
    try {
      const r = await fetch(rootPath() + 'api/tienda/precios', { headers: { accept: 'application/json' } });
      if (r.ok) { const t = await r.json(); if (t && t.rate) return { rate: t.rate, live: !!t.rate_live }; }
    } catch (e) {}
    try {
      const d = await (await fetch('https://dolarapi.com/v1/dolares/blue', { cache: 'no-store' })).json();
      if (d && d.compra) return { rate: d.compra, live: true };
    } catch (e) {}
    return { rate: await getDollarRate(), live: false };
  }

  function precio(rec, rate, defaultIva) {
    if (!rec) return null;
    const base = rec.fixed_ars != null ? rec.fixed_ars : rec.usd * rate;
    if (base == null || isNaN(base)) return null;
    const iva = rec.iva != null ? rec.iva : defaultIva;
    return { base: Math.round(base), iva, total: Math.round(base * (1 + iva / 100)), modelo: rec.modelo || null };
  }

  const ICON_GO = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="square"><path d="M5 12h14M13 5l7 7-7 7"/></svg>';
  const ICON_CHECK = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><path d="M20 6 9 17l-5-5"/></svg>';
  const ICON_CAMERA = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 8h3l1.6-2.4A2 2 0 0 1 10.3 4.6h3.4a2 2 0 0 1 1.7 1L17 8h3a1 1 0 0 1 1 1v10a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1V9a1 1 0 0 1 1-1z"/><circle cx="12" cy="13" r="3.5"/></svg>';

  function esc(s) {
    return String(s == null ? '' : s).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  }

  // Estado de filtro compartido entre los pills de rubro y el buscador: los
  // dos combinan sobre el mismo DOM ya renderizado, sin volver a pedir datos.
  const filterState = { rubro: 'todas', query: '' };

  function applyFilters() {
    document.querySelectorAll('.fo-group').forEach((g) => {
      const rubroOk = filterState.rubro === 'todas' || g.dataset.grupo === filterState.rubro;
      let anyVisible = false;
      g.querySelectorAll('.fo-card').forEach((card) => {
        const ok = !filterState.query || (card.dataset.search || '').includes(filterState.query);
        card.hidden = !ok;
        if (ok) anyVisible = true;
      });
      g.hidden = !(rubroOk && anyVisible);
    });
  }

  function card(p, pr, chip, selected, brandName) {
    const img = p.image
      ? `<img src="${rootPath()}${p.image}" alt="${p.name}" loading="lazy" onerror="this.replaceWith(Object.assign(document.createElement('span'),{className:'ph',textContent:'Sin imagen'}))">`
      : `<span class="ph">Sin imagen</span>`;
    const spec = [dato(p.capacity) && `Cap. ${p.capacity}`, dato(p.lift_height) && `Alt. ${p.lift_height}`]
      .filter(Boolean).map(s => `<span>${s}</span>`).join('');

    const bloque = pr
      ? `<div class="fo-final">${fmtARS(pr.total)}</div>
         <div class="fo-sub">IVA ${String(pr.iva).replace('.', ',')}% incluido · sin IVA ${fmtARS(pr.base)}</div>`
      : `<div class="fo-ask">Consultar precio<span>Disponibilidad a confirmar</span></div>`;

    // Los SKU provisorios del catálogo ("P-3041") no se imprimen.
    const modelo = [pr && pr.modelo, /^\d{7}$/.test(p.sku) ? 'SKU ' + p.sku : null].filter(Boolean).join(' · ');
    const searchBlob = esc(normalize([p.name, pr && pr.modelo, brandName, p.sku].filter(Boolean).join(' ')));

    return `
      <a class="fo-card${selected ? ' fo-card-picked' : ''}" href="${productUrl(p)}" data-search="${searchBlob}">
        <span class="fo-check${selected ? ' on' : ''}" data-sku="${esc(p.sku)}" role="checkbox" aria-checked="${!!selected}" title="Incluir en la selección">${ICON_CHECK}</span>
        <div class="fo-thumb">${img}${chip}</div>
        <div class="fo-body">
          <h3 class="fo-name">${p.name}</h3>
          ${modelo ? `<div class="fo-model">${modelo}</div>` : ''}
          ${spec ? `<div class="fo-spec">${spec}</div>` : ''}
          <div class="fo-price"><div class="fo-price-txt">${bloque}</div><span class="fo-go">${ICON_GO}</span></div>
        </div>
      </a>`;
  }

  const PHOTO_PREFIX = 'data:image/jpeg;base64,';
  const F_CODE_RE = /^\/f\/([A-Za-z0-9]{4,16})\/?$/;

  function toShared(sel, vn, vp, ve, vf) {
    const shared = !!(sel.length || vn || vp || ve || vf);
    // vf viaja sin el prefijo "data:image/jpeg;base64," para ahorrar esos
    // caracteres — se reconstruye acá, del único lado que lo lee.
    const photo = vf ? PHOTO_PREFIX + vf : '';
    return { shared, sel, vendor: (vn || vp || ve || vf) ? { name: vn, phone: vp, email: ve, photo } : null };
  }

  function sharedFromQuery() {
    const sel = (getQuery('sel') || '').split(',').map(s => s.trim()).filter(Boolean);
    return toShared(sel, (getQuery('vn') || '').trim(), (getQuery('vp') || '').trim(),
      (getQuery('ve') || '').trim(), (getQuery('vf') || '').trim());
  }

  /* El link corto (/f/<code>) no lleva nada en la query string: el código
     apunta a lo guardado en Cloudflare KV (ver api/folleto.js). Se resuelve
     acá para no tocar el resto del render — sigue viendo el mismo
     {shared, sel, vendor} de siempre. Si el código no resuelve (vencido,
     typo) se degrada al catálogo completo, no a una hoja en blanco. Los
     links viejos (?sel=...&vn=...) se siguen leyendo por compatibilidad. */
  async function resolveSharedState() {
    const m = location.pathname.match(F_CODE_RE);
    if (!m) return sharedFromQuery();
    try {
      const r = await fetch(`${rootPath()}api/folleto/${m[1]}`, { headers: { accept: 'application/json' } });
      if (r.ok) {
        const d = await r.json();
        return toShared(Array.isArray(d.sel) ? d.sel : [], d.vn || '', d.vp || '', d.ve || '', d.vf || '');
      }
    } catch (e) {}
    return { shared: false, sel: [], vendor: null };
  }

  function loadSavedVendor() {
    try { return JSON.parse(localStorage.getItem(LS_VENDOR)) || {}; } catch (e) { return {}; }
  }
  function saveVendor(v) {
    try { localStorage.setItem(LS_VENDOR, JSON.stringify(v)); } catch (e) {}
  }

  /* Recorta la foto al cuadrado central y la reduce a un JPEG chico: va
     codificada entera en la URL del link (no hay backend/almacenamiento), así
     que tiene que pesar lo menos posible. 56px a calidad .55 da ~1.5-3 KB en
     base64 (el link entero suele quedar bajo los 3000 caracteres). */
  function fileToSquareDataUri(file, size = 56, quality = 0.55) {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onerror = reject;
      reader.onload = () => {
        const img = new Image();
        img.onerror = reject;
        img.onload = () => {
          const side = Math.min(img.width, img.height);
          const sx = (img.width - side) / 2, sy = (img.height - side) / 2;
          const canvas = document.createElement('canvas');
          canvas.width = size; canvas.height = size;
          const ctx = canvas.getContext('2d');
          ctx.drawImage(img, sx, sy, side, side, 0, 0, size, size);
          resolve(canvas.toDataURL('image/jpeg', quality));
        };
        img.src = reader.result;
      };
      reader.readAsDataURL(file);
    });
  }

  function vendorCardHtml(v) {
    const initials = (v.name || '').trim().split(/\s+/).filter(Boolean).slice(0, 2).map(w => w[0]).join('').toUpperCase();
    const photo = v.photo
      ? `<img class="fo-vendor-photo" src="${esc(v.photo)}" alt="">`
      : `<span class="fo-vendor-photo fo-vendor-photo-fb">${esc(initials || 'TP')}</span>`;
    const links = [
      v.phone && `<a class="fo-vendor-pill fo-vendor-pill--wa" href="https://wa.me/${v.phone.replace(/[^\d]/g, '')}" target="_blank" rel="noopener">${ICONS.wa}<span>${esc(v.phone)}</span></a>`,
      v.email && `<a class="fo-vendor-pill" href="mailto:${esc(v.email)}">${ICONS.mail}<span>${esc(v.email)}</span></a>`,
    ].filter(Boolean).join('');
    return `
      <div class="fo-vendor">
        ${photo}
        <div class="fo-vendor-info">
          <b class="fo-vendor-name">${esc(v.name) || 'Asesor Trivium Pro'}</b>
          <span class="fo-vendor-role">Tu asesor en Trivium Pro</span>
        </div>
        ${links ? `<div class="fo-vendor-links">${links}</div>` : ''}
      </div>`;
  }

  /* opts: productos(catalog), items, defaultIva, titulo, bajada, mostrarMarca */
  async function render(opts) {
    const cat = await loadCatalog();
    const { rate, live } = await getRate();
    const { shared, sel, vendor } = await resolveSharedState();

    let lista = opts.productos(cat);
    if (shared && sel.length) {
      const want = new Set(sel);
      const filtrada = lista.filter(p => want.has(p.sku));
      if (filtrada.length) lista = filtrada; // sel inválido/vacío -> se muestra todo, no una hoja en blanco
    }

    const marcaDe = Object.fromEntries((cat.brands || []).map(b => [b.slug, b.name]));
    // Con logo cuando la marca lo tiene (BRAND_LOGOS de site.js); si no, texto.
    const chipDe = (slug) => {
      if (!slug || !marcaDe[slug]) return '';
      const logo = (typeof BRAND_LOGOS !== 'undefined') && BRAND_LOGOS[slug];
      return logo
        ? `<span class="fo-chip fo-chip-logo"><img src="${rootPath()}${logo}" alt="${marcaDe[slug]}"></span>`
        : `<span class="fo-chip">${marcaDe[slug]}</span>`;
    };

    // Secciones en el orden de catalog.categories; adentro, el mismo criterio
    // que /categoria/: primero por subcategoría en el orden en que están
    // declaradas (2 columnas, 4 columnas, tijera, pesados, motos...), y dentro
    // de cada subcategoría el orden del catálogo. El sort es estable, así que
    // el desempate lo da solo.
    // Sólo las subcategorías entran al orden: un producto colgado directo de la
    // categoría padre va al final, igual que en /categoria/ (allá ia === -1).
    const subOrden = Object.fromEntries(cat.categories.filter(c => c.parent).map((c, i) => [c.slug, i]));
    const buckets = {};
    lista.forEach(p => {
      const t = topCategory(p);
      (buckets[t.name] = buckets[t.name] || { slug: t.slug, items: [] }).items.push(p);
    });
    Object.values(buckets).forEach(b =>
      b.items.sort((a, x) => (subOrden[a.category] ?? 999) - (subOrden[x.category] ?? 999)));
    const ordenCat = cat.categories.filter(c => !c.parent).map(c => c.name);
    const grupos = [...ordenCat.filter(g => buckets[g]), ...Object.keys(buckets).filter(g => !ordenCat.includes(g))];

    const conPrecio = lista.filter(p => opts.items[p.sku]).length;
    const hoy = new Date().toLocaleDateString('es-AR', { day: '2-digit', month: 'long', year: 'numeric' });

    const seccion = (g) => {
      const { slug, items } = buckets[g];
      const icon = (typeof CAT_ICONS !== 'undefined' && CAT_ICONS[slug])
        ? `<img src="${rootPath()}${CAT_ICONS[slug]}" alt="">` : '';
      return `<section class="fo-group" data-grupo="${g}">
          <div class="fo-group-head">${icon}<h2>${g}</h2><span class="n">${items.length} ${items.length === 1 ? 'equipo' : 'equipos'}</span><span class="rule"></span></div>
          <div class="fo-grid">${items.map(p =>
            card(p, precio(opts.items[p.sku], rate, opts.defaultIva), opts.mostrarMarca ? chipDe(p.brand) : '', sel.includes(p.sku), marcaDe[p.brand])
          ).join('')}</div>
        </section>`;
    };

    const titulo = shared ? 'Selección de <em>equipos</em>' : opts.titulo;
    const bajada = shared
      ? 'Estos son los equipos que te preparamos, con precios de lista actualizados al día.'
      : opts.bajada;

    document.getElementById('fo-doc').innerHTML = `
      <header class="fo-cover">
        <img src="${rootPath()}assets/img/marcas/logo-trivium-pro.svg" alt="Trivium Pro"
             onerror="this.replaceWith(Object.assign(document.createElement('b'),{textContent:'Trivium Pro'}))">
        <h1>${titulo}</h1>
        <p class="sub">${bajada}</p>
        <div class="fo-cover-band">
          <div>Vigencia<b>${hoy}</b></div>
          <div>Cotización del dólar<b>${fmtARS(rate)}${live ? '' : ' (ref.)'}</b></div>
          <div>Equipos<b>${lista.length} · ${conPrecio} con precio</b></div>
          <div>Contacto<b>${TRIVIUM.whatsappDisplay}</b></div>
          <div>Web<b>pro.trivium.ar</b></div>
        </div>
      </header>
      <div class="fo-inner">
        ${vendor ? vendorCardHtml(vendor) : ''}
        ${grupos.map(seccion).join('')}
        <div class="fo-foot">
          <b>Condiciones.</b> Precios de lista en pesos argentinos, calculados con la cotización del dólar del día
          (${fmtARS(rate)}) y sujetos a modificación sin previo aviso. Los precios <b>no incluyen envío ni
          instalación</b>, que se cotizan aparte según la localidad de entrega. Los equipos sin precio publicado se
          cotizan a pedido. Consultá disponibilidad antes de cerrar la operación.<br>
          <b>${TRIVIUM.brand}</b> — ${TRIVIUM.cityLine} · ${TRIVIUM.whatsappDisplay} · ${TRIVIUM.email} · pro.trivium.ar
        </div>
      </div>`;

    // Filtros por rubro: sólo esconden secciones, así el PDF sale con lo que se ve.
    const filtCont = document.getElementById('fo-filters');
    if (filtCont) {
      const btn = (v, l, n) => `<button data-f="${v}" class="${v === 'todas' ? 'on' : ''}">${l}${n != null ? ` (${n})` : ''}</button>`;
      filtCont.innerHTML = btn('todas', 'Todos los rubros', lista.length) + grupos.map(g => btn(g, g, buckets[g].items.length)).join('');
      filtCont.addEventListener('click', (e) => {
        const b = e.target.closest('button'); if (!b) return;
        filtCont.querySelectorAll('button').forEach(x => x.classList.toggle('on', x === b));
        filterState.rubro = b.dataset.f;
        applyFilters();
      });
    }

    if (shared) {
      setupSharedBanner();
    } else {
      setupSelection();
      setupSharePanel();
    }
  }

  /* ---------- Modo "vista compartida": sólo queda el botón de descargar PDF ---------- */
  function setupSharedBanner() {
    document.body.classList.add('fo-shared-view');
  }

  /* ---------- Modo selección: en cualquier parte de la ficha se elige ---------- */
  function setupSelection() {
    const doc = document.getElementById('fo-doc');
    const selected = FOLLETO._selected = new Set();

    doc.addEventListener('click', (e) => {
      if (!doc.classList.contains('fo-selecting')) return; // navegación normal
      const cardEl = e.target.closest('.fo-card');
      if (!cardEl) return;
      e.preventDefault();
      e.stopPropagation();
      const chk = cardEl.querySelector('.fo-check');
      const sku = chk.dataset.sku;
      const on = selected.has(sku) ? (selected.delete(sku), false) : (selected.add(sku), true);
      chk.classList.toggle('on', on);
      chk.setAttribute('aria-checked', String(on));
      cardEl.classList.toggle('fo-card-picked', on);
      doc.dispatchEvent(new CustomEvent('tv-selection-change', { detail: { size: selected.size } }));
    });
  }

  /* ---------- Panel "Buscar equipos y compartir" ---------- */
  function setupSharePanel() {
    const toggleBtn = document.getElementById('fo-share-toggle');
    const panel = document.getElementById('fo-share-panel');
    const doc = document.getElementById('fo-doc');
    if (!toggleBtn || !panel) return;

    const saved = loadSavedVendor();
    let vendorPhoto = saved.photo || '';

    panel.innerHTML = `
      <div class="fo-share-in">
        <div class="fo-share-col">
          <h3>1. Elegí los equipos</h3>
          <p class="hint">Buscá por nombre, modelo o marca y tocá una ficha para agregarla. Si no elegís ninguna, se comparten todas las que ves ahora.</p>
          <div class="fo-search-row">
            <span class="fo-search-icon">${ICONS.search}</span>
            <input id="fo-search-input" type="text" placeholder="Buscar equipos…" autocomplete="off">
          </div>
          <div class="fo-share-row">
            <button class="fo-btn fo-ghost fo-btn-sm" id="fo-pick-all" type="button">Marcar visibles</button>
            <button class="fo-btn fo-ghost fo-btn-sm" id="fo-pick-none" type="button">Vaciar selección</button>
            <span class="fo-pick-count" id="fo-pick-count">0 elegidos</span>
          </div>
        </div>
        <div class="fo-share-col">
          <h3>2. Tus datos</h3>
          <p class="hint">Van a aparecer con tu foto al pie del catálogo que reciba tu cliente.</p>
          <div class="fo-vphoto-row">
            <label class="fo-vphoto-pick" for="fo-v-photo">
              <img id="fo-v-photo-img" alt="" ${vendorPhoto ? '' : 'hidden'} src="${esc(vendorPhoto)}">
              <span id="fo-v-photo-ph" ${vendorPhoto ? 'hidden' : ''}>${ICON_CAMERA}</span>
            </label>
            <input type="file" id="fo-v-photo" accept="image/*" hidden>
            <div class="fo-vphoto-txt"><b>Tu foto</b><span>Opcional, se recorta cuadrada</span></div>
          </div>
          <div class="fo-share-fields">
            <input id="fo-v-name" placeholder="Nombre y apellido" value="${esc(saved.name || '')}">
            <input id="fo-v-phone" placeholder="WhatsApp (ej. 5493511234567)" value="${esc(saved.phone || '')}">
            <input id="fo-v-email" placeholder="Email (opcional)" value="${esc(saved.email || '')}">
          </div>
        </div>
        <div class="fo-share-col fo-share-go">
          <h3>3. Compartilo</h3>
          <p class="hint">Genera un link con tu selección y tus datos — se abre como esta misma página, lista para ver o descargar en PDF.</p>
          <div class="fo-share-linkrow">
            <input id="fo-share-link" readonly placeholder="Tocá «Generar link» cuando termines">
            <button class="fo-btn fo-primary fo-btn-sm" id="fo-share-generate" type="button">Generar link</button>
          </div>
          <p class="fo-share-ok" id="fo-share-ok" hidden>¡Listo! Link copiado al portapapeles.</p>
        </div>
      </div>`;

    // Buscador: entra en modo selección apenas se escribe algo, así el click
    // en una ficha filtrada la elige en vez de abrir la ficha del producto.
    const searchInput = panel.querySelector('#fo-search-input');
    searchInput.addEventListener('input', () => {
      filterState.query = normalize(searchInput.value);
      // Buscar tiene que mirar todo el catálogo: si quedó un pill de rubro
      // marcado, "alineadora" no debería devolver cero resultados sólo
      // porque el pill activo dice "Elevadores".
      if (filterState.query && filterState.rubro !== 'todas') {
        filterState.rubro = 'todas';
        const filtCont = document.getElementById('fo-filters');
        filtCont?.querySelectorAll('button').forEach(b => b.classList.toggle('on', b.dataset.f === 'todas'));
      }
      applyFilters();
    });

    const countEl = panel.querySelector('#fo-pick-count');
    const updateCount = () => {
      const n = FOLLETO._selected.size;
      countEl.textContent = n === 1 ? '1 elegido' : `${n} elegidos`;
    };
    doc.addEventListener('tv-selection-change', updateCount);

    panel.querySelector('#fo-pick-all').addEventListener('click', () => {
      doc.querySelectorAll('.fo-card').forEach((cardEl) => {
        if (cardEl.hidden) return;
        const chk = cardEl.querySelector('.fo-check');
        FOLLETO._selected.add(chk.dataset.sku);
        chk.classList.add('on');
        chk.setAttribute('aria-checked', 'true');
        cardEl.classList.add('fo-card-picked');
      });
      updateCount();
    });
    panel.querySelector('#fo-pick-none').addEventListener('click', () => {
      FOLLETO._selected.clear();
      doc.querySelectorAll('.fo-card-picked').forEach((cardEl) => {
        cardEl.classList.remove('fo-card-picked');
        const chk = cardEl.querySelector('.fo-check');
        chk.classList.remove('on');
        chk.setAttribute('aria-checked', 'false');
      });
      updateCount();
    });

    panel.querySelector('#fo-v-photo').addEventListener('change', async (e) => {
      const file = e.target.files[0];
      if (!file) return;
      try {
        vendorPhoto = await fileToSquareDataUri(file);
        const img = panel.querySelector('#fo-v-photo-img');
        img.src = vendorPhoto; img.hidden = false;
        panel.querySelector('#fo-v-photo-ph').hidden = true;
      } catch (err) { /* foto corrupta o formato no soportado: se ignora */ }
    });

    toggleBtn.addEventListener('click', () => {
      panel.hidden = !panel.hidden;
      doc.classList.toggle('fo-selecting', !panel.hidden);
      toggleBtn.classList.toggle('on', !panel.hidden);
      if (!panel.hidden) {
        searchInput.focus();
        document.getElementById('fo-filters')?.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    });

    function longLinkFallback(sel, name, phone, email, vfRaw) {
      // Sin backend disponible (KV caído, offline), un link largo sigue
      // siendo mejor que ningún link: cae al esquema viejo por query string.
      // No hace falta armar la ruta a mano: esta función sólo es alcanzable
      // desde la página real del folleto (en /f/<code> no se arma el panel de
      // compartir), así que location.pathname ya es la correcta — y evita
      // escribir acá el slug secreto, que es justo lo que no debe salir en un
      // archivo público como este.
      const qs = new URLSearchParams();
      if (sel.length) qs.set('sel', sel.join(','));
      if (name) qs.set('vn', name);
      if (phone) qs.set('vp', phone);
      if (email) qs.set('ve', email);
      if (vfRaw) qs.set('vf', vfRaw);
      const url = new URL(window.location.href);
      url.search = qs.toString();
      return url.toString();
    }

    async function generateLink() {
      const name = panel.querySelector('#fo-v-name').value.trim();
      const phone = panel.querySelector('#fo-v-phone').value.trim();
      const email = panel.querySelector('#fo-v-email').value.trim();
      saveVendor({ name, phone, email, photo: vendorPhoto });

      const sel = [...FOLLETO._selected];
      const vfRaw = vendorPhoto ? (vendorPhoto.startsWith(PHOTO_PREFIX) ? vendorPhoto.slice(PHOTO_PREFIX.length) : vendorPhoto) : '';

      const linkInput = panel.querySelector('#fo-share-link');
      const genBtn = panel.querySelector('#fo-share-generate');
      linkInput.value = 'Generando link…';
      genBtn.disabled = true;

      let link;
      try {
        const r = await fetch(`${rootPath()}api/folleto`, {
          method: 'POST',
          headers: { 'content-type': 'application/json' },
          body: JSON.stringify({ sel, vn: name, vp: phone, ve: email, vf: vfRaw }),
        });
        if (!r.ok) throw new Error('status ' + r.status);
        const { code } = await r.json();
        link = `${location.origin}/f/${code}`;
      } catch (e) {
        link = longLinkFallback(sel, name, phone, email, vfRaw);
      }
      genBtn.disabled = false;

      linkInput.value = link;
      const ok = panel.querySelector('#fo-share-ok');
      navigator.clipboard?.writeText(link).then(() => {
        ok.hidden = false;
        setTimeout(() => { ok.hidden = true; }, 4000);
      }).catch(() => {
        linkInput.select();
      });

      // Si generaron el link desde la barra flotante, volvemos arriba a
      // buscar el link ya cargado y el aviso de "copiado".
      panel.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
    panel.querySelector('#fo-share-generate').addEventListener('click', generateLink);

    setupFloatBar(doc, panel, generateLink);
  }

  /* ---------- Barra flotante: aparece cuando el panel se scrollea fuera de vista ---------- */
  function setupFloatBar(doc, panel, generateLink) {
    const bar = document.getElementById('fo-float-bar');
    if (!bar || typeof IntersectionObserver === 'undefined') return;

    bar.innerHTML = `
      <span class="fo-float-count" id="fo-float-count">0 elegidos</span>
      <button class="fo-btn fo-ghost fo-btn-sm" id="fo-float-top" type="button">↑ Volver arriba</button>
      <button class="fo-btn fo-primary fo-btn-sm" id="fo-float-generate" type="button">Generar link</button>`;

    const countEl = bar.querySelector('#fo-float-count');
    doc.addEventListener('tv-selection-change', (e) => {
      const n = e.detail.size;
      countEl.textContent = n === 1 ? '1 elegido' : `${n} elegidos`;
    });

    bar.querySelector('#fo-float-top').addEventListener('click', () => {
      panel.scrollIntoView({ behavior: 'smooth', block: 'start' });
    });
    bar.querySelector('#fo-float-generate').addEventListener('click', generateLink);

    // Sólo se muestra mientras el panel está abierto y fuera de la pantalla:
    // si ya se ve el panel (o está cerrado) no hace falta duplicarlo.
    let panelVisible = true;
    const obs = new IntersectionObserver(([entry]) => {
      panelVisible = entry.isIntersecting;
      bar.hidden = panel.hidden || panelVisible;
    }, { threshold: 0 });
    obs.observe(panel);

    const toggleBtn = document.getElementById('fo-share-toggle');
    toggleBtn?.addEventListener('click', () => {
      bar.hidden = panel.hidden || panelVisible;
    });
  }

  return { render };
})();
