/* Folleto/catálogo de equipos — renderer de /folleto-<secreto>/.
 *
 * Se configura con FOLLETO.render({...}) desde la página. Depende de site.js
 * (loadCatalog, categoryById, productUrl, rootPath, getQuery, TRIVIUM,
 * CAT_ICONS) y de assets/css/folleto.css.
 *
 * El orden NO se reordena acá: las secciones siguen el orden de
 * catalog.categories y dentro de cada una los productos quedan como están en
 * catalog.json, igual que en /catalogo/. Cada ficha es un link a su página de
 * producto.
 *
 * Selección + link para compartir
 * --------------------------------
 * El vendedor puede tildar equipos puntuales y cargar su nombre/WhatsApp/mail;
 * "Generar link" arma una URL con esos datos en la query string (?sel=...&
 * vn=...&vp=...&ve=...) — no hay backend, así que todo el estado vive en el
 * link mismo. Quien abre ese link ve sólo los equipos elegidos y una tarjeta
 * con los datos del vendedor al pie (y en el PDF si lo descarga).
 */
window.FOLLETO = (function () {
  const fmtARS = (n) => '$ ' + new Intl.NumberFormat('es-AR', { maximumFractionDigits: 0 }).format(Math.round(n));
  // El catálogo usa '' y '—' indistintamente para "sin dato".
  const dato = (v) => (v && v !== '—' && v !== '-') ? v : null;
  const LS_VENDOR = 'tv_folleto_vendedor';

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
      const d = await (await fetch('https://dolarapi.com/v1/dolares/oficial', { cache: 'no-store' })).json();
      if (d && d.venta) return { rate: d.venta, live: true };
    } catch (e) {}
    return { rate: await getOfficialRate(), live: false };
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

  function esc(s) {
    return String(s == null ? '' : s).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  }

  function card(p, pr, chip, selected) {
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

    return `
      <a class="fo-card" href="${productUrl(p)}">
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

  function vendorFromQuery() {
    const sel = (getQuery('sel') || '').split(',').map(s => s.trim()).filter(Boolean);
    const vn = (getQuery('vn') || '').trim();
    const vp = (getQuery('vp') || '').trim();
    const ve = (getQuery('ve') || '').trim();
    const shared = !!(sel.length || vn || vp || ve);
    return { shared, sel, vendor: (vn || vp || ve) ? { name: vn, phone: vp, email: ve } : null };
  }

  function loadSavedVendor() {
    try { return JSON.parse(localStorage.getItem(LS_VENDOR)) || {}; } catch (e) { return {}; }
  }
  function saveVendor(v) {
    try { localStorage.setItem(LS_VENDOR, JSON.stringify(v)); } catch (e) {}
  }

  function vendorCardHtml(v) {
    const initials = (v.name || '?').trim().split(/\s+/).slice(0, 2).map(w => w[0]).join('').toUpperCase();
    const links = [
      v.phone && `<a href="https://wa.me/${v.phone.replace(/[^\d]/g, '')}" target="_blank" rel="noopener">${ICONS.wa}${v.phone}</a>`,
      v.email && `<a href="mailto:${esc(v.email)}">${ICONS.mail}${esc(v.email)}</a>`,
    ].filter(Boolean).join('');
    return `
      <div class="fo-vendor">
        <span class="fo-vendor-av">${esc(initials || 'TP')}</span>
        <div class="fo-vendor-info">
          <span class="fo-vendor-kick">Preparado especialmente para vos por</span>
          <b class="fo-vendor-name">${esc(v.name) || 'Un asesor de Trivium Pro'}</b>
          ${links ? `<div class="fo-vendor-links">${links}</div>` : ''}
        </div>
      </div>`;
  }

  /* opts: productos(catalog), items, defaultIva, titulo, bajada, mostrarMarca */
  async function render(opts) {
    const cat = await loadCatalog();
    const { rate, live } = await getRate();
    const { shared, sel, vendor } = vendorFromQuery();

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
            card(p, precio(opts.items[p.sku], rate, opts.defaultIva), opts.mostrarMarca ? chipDe(p.brand) : '', sel.includes(p.sku))
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
          <div>Dólar oficial venta<b>${fmtARS(rate)}${live ? '' : ' (ref.)'}</b></div>
          <div>Equipos<b>${lista.length} · ${conPrecio} con precio</b></div>
          <div>Contacto<b>${TRIVIUM.whatsappDisplay}</b></div>
          <div>Web<b>pro.trivium.ar</b></div>
        </div>
      </header>
      <div class="fo-inner">
        ${vendor ? vendorCardHtml(vendor) : ''}
        ${grupos.map(seccion).join('')}
        <div class="fo-foot">
          <b>Condiciones.</b> Precios de lista en pesos argentinos, calculados con el dólar oficial venta del día
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
        const f = b.dataset.f;
        document.querySelectorAll('.fo-group').forEach(s => { s.hidden = !(f === 'todas' || s.dataset.grupo === f); });
      });
    }

    if (shared) {
      setupSharedBanner();
    } else {
      setupSelection(lista);
      setupSharePanel(lista, rate, opts, vendor);
    }
  }

  /* ---------- Modo "vista compartida": banner en vez de las herramientas de venta ---------- */
  function setupSharedBanner() {
    const shareBtn = document.getElementById('fo-share-toggle');
    if (shareBtn) shareBtn.hidden = true;
    const txt = document.getElementById('fo-actions-txt');
    if (txt) txt.innerHTML = 'Esta es una selección personalizada. <a href="./">Ver el catálogo completo →</a>';
  }

  /* ---------- Selección de equipos (checkboxes sobre las fichas) ---------- */
  function setupSelection(lista) {
    const doc = document.getElementById('fo-doc');
    const selected = new Set();

    doc.addEventListener('click', (e) => {
      const chk = e.target.closest('.fo-check');
      if (!chk) return;
      e.preventDefault();
      e.stopPropagation();
      const sku = chk.dataset.sku;
      if (selected.has(sku)) { selected.delete(sku); chk.classList.remove('on'); }
      else { selected.add(sku); chk.classList.add('on'); }
      chk.setAttribute('aria-checked', selected.has(sku));
      doc.dispatchEvent(new CustomEvent('tv-selection-change', { detail: { size: selected.size } }));
    });

    FOLLETO._selected = selected; // usado por el panel de compartir
  }

  /* ---------- Panel "Compartir con un cliente" ---------- */
  function setupSharePanel(lista, rate, opts, vendorActual) {
    const toggleBtn = document.getElementById('fo-share-toggle');
    const panel = document.getElementById('fo-share-panel');
    const doc = document.getElementById('fo-doc');
    if (!toggleBtn || !panel) return;

    const saved = loadSavedVendor();
    panel.innerHTML = `
      <div class="fo-share-in">
        <div class="fo-share-col">
          <h3>1. Elegí los equipos</h3>
          <p class="hint">Tocá el círculo de cada ficha para marcarla. Si no marcás ninguno, se comparten todos los que ves ahora.</p>
          <div class="fo-share-row">
            <button class="fo-btn fo-ghost fo-btn-sm" id="fo-pick-all" type="button">Marcar todos</button>
            <button class="fo-btn fo-ghost fo-btn-sm" id="fo-pick-none" type="button">Vaciar selección</button>
            <span class="fo-pick-count" id="fo-pick-count">0 elegidos</span>
          </div>
        </div>
        <div class="fo-share-col">
          <h3>2. Tus datos</h3>
          <p class="hint">Van a aparecer al pie del catálogo que reciba tu cliente.</p>
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
            <input id="fo-share-link" readonly placeholder="Completá tu nombre y generá el link">
            <button class="fo-btn fo-primary fo-btn-sm" id="fo-share-generate" type="button">Generar link</button>
          </div>
          <p class="fo-share-ok" id="fo-share-ok" hidden>¡Listo! Link copiado al portapapeles.</p>
        </div>
      </div>`;

    const countEl = panel.querySelector('#fo-pick-count');
    const updateCount = () => {
      const n = FOLLETO._selected.size;
      countEl.textContent = n === 1 ? '1 elegido' : `${n} elegidos`;
    };
    doc.addEventListener('tv-selection-change', updateCount);

    panel.querySelector('#fo-pick-all').addEventListener('click', () => {
      doc.querySelectorAll('.fo-check').forEach(chk => {
        FOLLETO._selected.add(chk.dataset.sku);
        chk.classList.add('on');
        chk.setAttribute('aria-checked', 'true');
      });
      updateCount();
    });
    panel.querySelector('#fo-pick-none').addEventListener('click', () => {
      FOLLETO._selected.clear();
      doc.querySelectorAll('.fo-check.on').forEach(chk => { chk.classList.remove('on'); chk.setAttribute('aria-checked', 'false'); });
      updateCount();
    });

    toggleBtn.addEventListener('click', () => {
      panel.hidden = !panel.hidden;
      doc.classList.toggle('fo-selecting', !panel.hidden);
      toggleBtn.classList.toggle('on', !panel.hidden);
    });

    panel.querySelector('#fo-share-generate').addEventListener('click', () => {
      const name = panel.querySelector('#fo-v-name').value.trim();
      const phone = panel.querySelector('#fo-v-phone').value.trim();
      const email = panel.querySelector('#fo-v-email').value.trim();
      saveVendor({ name, phone, email });

      const qs = new URLSearchParams();
      if (FOLLETO._selected.size) qs.set('sel', [...FOLLETO._selected].join(','));
      if (name) qs.set('vn', name);
      if (phone) qs.set('vp', phone);
      if (email) qs.set('ve', email);

      const url = new URL(window.location.href);
      url.search = qs.toString();
      const link = url.toString();

      const linkInput = panel.querySelector('#fo-share-link');
      linkInput.value = link;
      linkInput.hidden = false;

      const ok = panel.querySelector('#fo-share-ok');
      navigator.clipboard?.writeText(link).then(() => {
        ok.hidden = false;
        setTimeout(() => { ok.hidden = true; }, 4000);
      }).catch(() => {
        linkInput.select();
      });
    });
  }

  return { render };
})();
