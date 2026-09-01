/* Folleto/catálogo de equipos — renderer de /folleto-<secreto>/.
 *
 * Se configura con FOLLETO.render({...}) desde la página. Depende de site.js
 * (loadCatalog, categoryById, productUrl, rootPath, TRIVIUM, CAT_ICONS) y de
 * assets/css/folleto.css.
 *
 * El orden NO se reordena acá: las secciones siguen el orden de
 * catalog.categories y dentro de cada una los productos quedan como están en
 * catalog.json, igual que en /catalogo/. Cada ficha es un link a su página de
 * producto.
 */
window.FOLLETO = (function () {
  const fmtARS = (n) => '$ ' + new Intl.NumberFormat('es-AR', { maximumFractionDigits: 0 }).format(Math.round(n));
  // El catálogo usa '' y '—' indistintamente para "sin dato".
  const dato = (v) => (v && v !== '—' && v !== '-') ? v : null;

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

  function card(p, pr, chip) {
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
        <div class="fo-thumb">${img}${chip}</div>
        <div class="fo-body">
          <h3 class="fo-name">${p.name}</h3>
          ${modelo ? `<div class="fo-model">${modelo}</div>` : ''}
          ${spec ? `<div class="fo-spec">${spec}</div>` : ''}
          <div class="fo-price"><div class="fo-price-txt">${bloque}</div><span class="fo-go">${ICON_GO}</span></div>
        </div>
      </a>`;
  }

  /* opts: productos(catalog), items, defaultIva, titulo, bajada, mostrarMarca */
  async function render(opts) {
    const cat = await loadCatalog();
    const { rate, live } = await getRate();

    const lista = opts.productos(cat);
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
            card(p, precio(opts.items[p.sku], rate, opts.defaultIva), opts.mostrarMarca ? chipDe(p.brand) : '')
          ).join('')}</div>
        </section>`;
    };

    document.getElementById('fo-doc').innerHTML = `
      <header class="fo-cover">
        <img src="${rootPath()}assets/img/marcas/logo-trivium-pro.svg" alt="Trivium Pro"
             onerror="this.replaceWith(Object.assign(document.createElement('b'),{textContent:'Trivium Pro'}))">
        <h1>${opts.titulo}</h1>
        <p class="sub">${opts.bajada}</p>
        <div class="fo-cover-band">
          <div>Vigencia<b>${hoy}</b></div>
          <div>Dólar oficial venta<b>${fmtARS(rate)}${live ? '' : ' (ref.)'}</b></div>
          <div>Equipos<b>${lista.length} · ${conPrecio} con precio</b></div>
          <div>Contacto<b>${TRIVIUM.whatsappDisplay}</b></div>
          <div>Web<b>pro.trivium.ar</b></div>
        </div>
      </header>
      <div class="fo-inner">
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
    const cont = document.getElementById('fo-filters');
    if (cont) {
      const btn = (v, l, n) => `<button data-f="${v}" class="${v === 'todas' ? 'on' : ''}">${l}${n != null ? ` (${n})` : ''}</button>`;
      cont.innerHTML = btn('todas', 'Todos los rubros', lista.length) + grupos.map(g => btn(g, g, buckets[g].items.length)).join('');
      cont.addEventListener('click', (e) => {
        const b = e.target.closest('button'); if (!b) return;
        cont.querySelectorAll('button').forEach(x => x.classList.toggle('on', x === b));
        const f = b.dataset.f;
        document.querySelectorAll('.fo-group').forEach(s => { s.hidden = !(f === 'todas' || s.dataset.grupo === f); });
      });
    }
  }

  return { render };
})();
