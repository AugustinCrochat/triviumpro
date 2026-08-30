/* Folleto de equipos — renderer compartido.
 *
 * Lo usan dos páginas con el mismo código y distinto alcance:
 *   /folleto/               marca propia, público
 *   /folleto-<secreto>/     todas las marcas, privado (noindex + Disallow)
 *
 * Se configura con FOLLETO.render({...}) desde cada página. Depende de site.js
 * (loadCatalog, categoryById, rootPath, TRIVIUM) y de assets/css/folleto.css.
 */
window.FOLLETO = (function () {
  const GROUP_ORDER = ['Elevadores', 'Alineadoras', 'Balanceadoras', 'Desarmadoras',
                       'Accesorios de Balanceo', 'Herramientas Neumáticas',
                       'Equipamiento de Taller', 'Muebles de Taller'];

  const fmtARS = (n) => '$ ' + new Intl.NumberFormat('es-AR', { maximumFractionDigits: 0 }).format(Math.round(n));
  // El catálogo usa '' y '—' indistintamente para "sin dato".
  const dato = (v) => (v && v !== '—' && v !== '-') ? v : null;

  function topCategoryName(p) {
    const c = categoryById(p.category);
    const parent = c && c.parent ? categoryById(c.parent) : null;
    return (parent && parent.name) || (c && c.name) || 'Otros';
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
    return { base: Math.round(base), iva, total: Math.round(base * (1 + iva / 100)) };
  }

  function card(p, pr, marcaLabel) {
    const img = p.image
      ? `<img src="${rootPath()}${p.image}" alt="${p.name}" loading="lazy" onerror="this.replaceWith(Object.assign(document.createElement('span'),{className:'ph',textContent:'Sin imagen'}))">`
      : `<span class="ph">Sin imagen</span>`;
    const spec = [dato(p.capacity) && `Cap. <b>${p.capacity}</b>`, dato(p.lift_height) && `Alt. <b>${p.lift_height}</b>`]
      .filter(Boolean).map(s => `<span>${s}</span>`).join('');

    const bloque = pr
      ? `<div class="fo-final">${fmtARS(pr.total)}</div>
         <div class="fo-sub">IVA ${String(pr.iva).replace('.', ',')}% incluido · sin IVA ${fmtARS(pr.base)}</div>`
      : `<div class="fo-ask">Consultar precio<span>Disponibilidad a confirmar</span></div>`;

    return `
      <article class="fo-card">
        <div class="fo-thumb">${img}${marcaLabel ? `<span class="fo-brand">${marcaLabel}</span>` : ''}</div>
        <div class="fo-body">
          <h3 class="fo-name">${p.name}</h3>
          <div class="fo-model">${[pr && pr.modelo, 'SKU ' + p.sku].filter(Boolean).join(' · ')}</div>
          ${spec ? `<div class="fo-spec">${spec}</div>` : ''}
          <div class="fo-price">${bloque}</div>
        </div>
      </article>`;
  }

  /* opts:
       productos(catalog) -> lista de productos a mostrar
       items              -> { sku: {usd|fixed_ars, iva, modelo} }
       defaultIva, titulo, bajada, mostrarMarca (bool) */
  async function render(opts) {
    const cat = await loadCatalog();
    const { rate, live } = await getRate();

    const lista = opts.productos(cat);
    const marcaDe = Object.fromEntries((cat.brands || []).map(b => [b.slug, b.name]));

    const buckets = {};
    lista.forEach(p => { const g = topCategoryName(p); (buckets[g] = buckets[g] || []).push(p); });
    const grupos = [...GROUP_ORDER.filter(g => buckets[g]), ...Object.keys(buckets).filter(g => !GROUP_ORDER.includes(g))];

    const conPrecio = lista.filter(p => opts.items[p.sku]).length;
    const hoy = new Date().toLocaleDateString('es-AR', { day: '2-digit', month: 'long', year: 'numeric' });

    const seccion = (g) => {
      const items = buckets[g].slice().sort((a, b) => a.name.localeCompare(b.name, 'es'));
      return `<section class="fo-group" data-grupo="${g}">
          <h2>${g} <span style="color:var(--text-mute);font-weight:600">· ${items.length}</span></h2>
          <div class="fo-grid">${items.map(p => {
            const rec = opts.items[p.sku];
            const pr = precio(rec, rate, opts.defaultIva);
            if (pr && rec.modelo) pr.modelo = rec.modelo;
            return card(p, pr, opts.mostrarMarca ? (marcaDe[p.brand] || '') : '');
          }).join('')}</div>
        </section>`;
    };

    document.getElementById('fo-doc').innerHTML = `
      <div class="fo-head">
        <img src="${rootPath()}assets/img/marcas/logo-trivium-pro.svg" alt="Trivium Pro"
             onerror="this.replaceWith(Object.assign(document.createElement('b'),{textContent:'Trivium Pro'}))">
        <div>
          <h1>${opts.titulo}</h1>
          <p>${opts.bajada}</p>
        </div>
        <div class="fo-meta">
          <div>Vigente al <b>${hoy}</b></div>
          <div>Dólar oficial venta: <b>${fmtARS(rate)}</b>${live ? '' : ' (referencia)'}</div>
          <div>${TRIVIUM.whatsappDisplay} · ${TRIVIUM.email}</div>
        </div>
      </div>
      ${grupos.map(seccion).join('')}
      <div class="fo-foot">
        <b>Condiciones.</b> ${conPrecio} de ${lista.length} equipos con precio de lista publicado; el resto se cotiza a pedido.
        Precios en pesos argentinos calculados con el dólar oficial venta del día (${fmtARS(rate)}), sujetos a modificación sin previo aviso.
        <b>No incluyen envío ni instalación</b>, que se cotizan aparte según la localidad de entrega. Consultá disponibilidad antes de cerrar la operación.<br>
        <b>${TRIVIUM.brand}</b> — ${TRIVIUM.cityLine} · ${TRIVIUM.whatsappDisplay} · ${TRIVIUM.email} · pro.trivium.ar
      </div>`;

    // Filtros por rubro: sólo esconden secciones, así el PDF sale con lo que se ve.
    const cont = document.getElementById('fo-filters');
    if (cont) {
      const btn = (v, l, n) => `<button data-f="${v}" class="${v === 'todas' ? 'on' : ''}">${l}${n != null ? ` (${n})` : ''}</button>`;
      cont.innerHTML = btn('todas', 'Todos los rubros', lista.length) + grupos.map(g => btn(g, g, buckets[g].length)).join('');
      cont.addEventListener('click', (e) => {
        const b = e.target.closest('button'); if (!b) return;
        cont.querySelectorAll('button').forEach(x => x.classList.toggle('on', x === b));
        const f = b.dataset.f;
        document.querySelectorAll('.fo-group').forEach(s => {
          s.hidden = !(f === 'todas' || s.dataset.grupo === f);
        });
      });
    }
  }

  return { render };
})();
