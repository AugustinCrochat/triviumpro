/* Ecommerce compartido — Trivium Pro
 *
 * Carrito, tabla de precios y checkout de Mercado Pago, en un solo lugar para
 * que /tienda/, las fichas de producto y /marca/trivium-pro/ compartan el mismo
 * estado: si alguien agrega un elevador desde la ficha y después navega a la
 * tienda, el carrito lo sigue.
 *
 * Depende de site.js (rootPath, waLink, loadCatalog, loadPublicPrices, TRIVIUM)
 * y de assets/css/tienda.css. Cargalo DESPUÉS de site.js.
 *
 * Uso mínimo en una página:
 *     await TIENDA.init();
 *     TIENDA.add('1010127');
 *
 * El precio que se muestra sale de /api/tienda/precios, el mismo endpoint que
 * el Worker usa para cobrar, así que la vidriera y el cobro no pueden diferir.
 */
window.TIENDA = (function () {
  const LS = 'tv_tienda_v1';
  const MAX_QTY = 10;

  let table = null;       // { rate, rate_live, items: { sku: {base_ars, iva, total_ars} } }
  let apiOk = false;      // false => el Worker no contestó; se cierra por WhatsApp
  let buyNowSku = null;   // compra directa: no toca el carrito guardado
  let productos = {};     // sku -> producto del catálogo
  let listeners = [];
  const cart = new Map();

  const fmt = (n) => '$ ' + new Intl.NumberFormat('es-AR', { maximumFractionDigits: 0 }).format(Math.round(n));

  /* ---------- Persistencia ---------- */
  function save() { try { localStorage.setItem(LS, JSON.stringify([...cart])); } catch (e) {} }
  function load() {
    try { (JSON.parse(localStorage.getItem(LS)) || []).forEach(([s, q]) => cart.set(s, q)); } catch (e) {}
  }

  /* ---------- Precios ----------
     El Worker manda. Si no contesta (deploy viejo, secret sin cargar) se
     recalcula acá con la misma fórmula para que la vidriera siga en pie, pero
     se deshabilita el pago online y se ofrece WhatsApp. */
  async function loadTable() {
    try {
      const r = await fetch(rootPath() + 'api/tienda/precios', { headers: { accept: 'application/json' } });
      if (r.ok) {
        const t = await r.json();
        if (t && t.items) { apiOk = true; return t; }
      }
    } catch (e) {}

    const [prices, dolar] = await Promise.all([loadPublicPrices(), fallbackRate()]);
    const items = {};
    for (const [sku, rec] of Object.entries(prices.items)) {
      if (rec.tienda === false) continue;
      const base = rec.fixed_ars != null ? rec.fixed_ars : rec.usd * dolar.rate;
      const iva = rec.iva != null ? rec.iva : prices.meta.default_iva;
      items[sku] = { base_ars: Math.round(base), iva, total_ars: Math.round(base * (1 + iva / 100)),
                     modelo: rec.modelo || null, grupo: rec.grupo || null, usd: rec.usd ?? null };
    }
    return { rate: dolar.rate, rate_live: dolar.live, items };
  }

  /* getOfficialRate() de site.js devuelve sólo el número, así que no permite
     distinguir una cotización real de la de referencia; acá hace falta saberlo
     para no rotular "sin conexión" un precio que sí está al día. */
  async function fallbackRate() {
    try {
      const r = await fetch('https://dolarapi.com/v1/dolares/oficial', { cache: 'no-store' });
      const j = await r.json();
      if (j && j.venta) return { rate: j.venta, live: true };
    } catch (e) {}
    return { rate: await getOfficialRate(), live: false };
  }

  /* ---------- API del carrito ---------- */
  const priceOf = (sku) => (table && table.items[sku]) || null;
  const sellable = (sku) => !!priceOf(sku);
  const has = (sku) => cart.has(sku);
  const count = () => [...cart.values()].reduce((a, b) => a + b, 0);
  const total = () => [...cart].reduce((t, [sku, q]) => t + ((priceOf(sku) || {}).total_ars || 0) * q, 0);

  function add(sku, qty) {
    if (!sellable(sku)) return false;
    cart.set(sku, Math.min(MAX_QTY, (cart.get(sku) || 0) + (qty || 1)));
    save(); emit(); return true;
  }
  function remove(sku) { cart.delete(sku); save(); emit(); }
  function toggle(sku) { has(sku) ? remove(sku) : add(sku); return has(sku); }
  function setQty(sku, q) {
    const n = Math.min(MAX_QTY, Math.max(1, q));
    cart.set(sku, n); save(); emit();
  }
  function onChange(fn) { listeners.push(fn); }
  function emit() { renderFab(); renderNavCart(); if (isOpen()) renderDrawer(); listeners.forEach(f => { try { f(); } catch (e) {} }); }

  /* ---------- UI ---------- */
  const ICON_CART = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="9" cy="20" r="1.5"/><circle cx="18" cy="20" r="1.5"/><path d="M2 3h3l2.7 12.4a2 2 0 0 0 2 1.6h7.7a2 2 0 0 0 2-1.6L21 7H6"/></svg>';
  // "Pagar con [logo de Mercado Pago]": el logo oficial, no un ícono propio
  // — es la misma convención que neumaticos-trivium en el botón de pago.
  const PAGAR_HTML = `Pagar con <img src="${rootPath()}assets/img/mercadopago-logo.svg" alt="Mercado Pago">`;
  const ICON_OK = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M20 6 9 17l-5-5"/></svg>';

  function mount() {
    if (document.getElementById('tn-drawer')) return;
    const el = document.createElement('div');
    el.innerHTML = `
      <button class="tn-fab" id="tn-fab" onclick="TIENDA.open()">
        ${ICON_CART}<span id="tn-fab-txt">Carrito</span> <span class="b" id="tn-fab-n">0</span>
      </button>
      <div class="tn-scrim" id="tn-scrim" onclick="TIENDA.close()"></div>
      <aside class="tn-drawer" id="tn-drawer" aria-hidden="true">
        <div class="tn-dhead"><h2 id="tn-dtitle">Tu carrito</h2><button onclick="TIENDA.close()" aria-label="Cerrar">&times;</button></div>
        <div class="tn-dbody" id="tn-dbody"></div>
        <div class="tn-dfoot" id="tn-dfoot"></div>
      </aside>
      <div id="tn-toast"></div>`;
    while (el.firstElementChild) document.body.appendChild(el.firstElementChild);

    // El carrito del header lo dibuja site.js como un hueco vacío.
    const nav = document.getElementById('tn-navcart');
    if (nav) nav.onclick = open;
  }

  function toast(msg) {
    const t = document.getElementById('tn-toast');
    if (!t) return;
    t.textContent = msg; t.classList.add('show');
    clearTimeout(t._t); t._t = setTimeout(() => t.classList.remove('show'), 2200);
  }

  function renderFab() {
    const fab = document.getElementById('tn-fab');
    if (!fab) return;
    const n = count();
    fab.classList.toggle('show', n > 0);
    document.getElementById('tn-fab-n').textContent = n;
    document.getElementById('tn-fab-txt').textContent = fmt(total());
  }
  function renderNavCart() {
    const nav = document.getElementById('tn-navcart');
    if (!nav) return;
    const n = count();
    nav.classList.toggle('show', n > 0);
    const b = nav.querySelector('.b');
    if (b) b.textContent = n;
  }

  const isOpen = () => { const d = document.getElementById('tn-drawer'); return d && d.classList.contains('show'); };
  function open() { mount(); renderDrawer(); document.getElementById('tn-scrim').classList.add('show'); const d = document.getElementById('tn-drawer'); d.classList.add('show'); d.setAttribute('aria-hidden', 'false'); }
  function close() { buyNowSku = null; const s = document.getElementById('tn-scrim'), d = document.getElementById('tn-drawer'); if (s) s.classList.remove('show'); if (d) { d.classList.remove('show'); d.setAttribute('aria-hidden', 'true'); } }
  function buyNow(sku) { if (!sellable(sku)) return; buyNowSku = sku; open(); }

  const lines = () => buyNowSku ? [[buyNowSku, 1]] : [...cart];

  function renderDrawer() {
    const ls = lines();
    document.getElementById('tn-dtitle').textContent = buyNowSku ? 'Comprar ahora' : 'Tu carrito';

    document.getElementById('tn-dbody').innerHTML = ls.length ? ls.map(([sku, q]) => {
      const p = productos[sku], pr = priceOf(sku);
      if (!p || !pr) return '';
      return `
        <div class="tn-line">
          <div class="tn-line-img">${p.image ? `<img src="${rootPath()}${p.image}" alt="">` : ''}</div>
          <div class="tn-line-info">
            <h4>${p.name}</h4>
            <div class="tn-line-price">${fmt(pr.total_ars * q)}</div>
            ${buyNowSku ? '' : `
              <div class="tn-qty">
                <button onclick="TIENDA.setQty('${sku}',${q - 1})" aria-label="Menos">−</button><span>${q}</span><button onclick="TIENDA.setQty('${sku}',${q + 1})" aria-label="Más">+</button>
              </div>
              <button class="tn-rm" onclick="TIENDA.remove('${sku}')">Quitar</button>`}
          </div>
        </div>`;
    }).join('') : '<p class="tn-empty">Todavía no agregaste equipos.</p>';

    const suma = ls.reduce((t, [sku, q]) => t + ((priceOf(sku) || {}).total_ars || 0) * q, 0);
    const wa = waLink('Hola, quiero comprar: ' + ls.map(([s, q]) => `${(productos[s] || {}).name || s} x${q}`).join(', '));

    document.getElementById('tn-dfoot').innerHTML = !ls.length ? '' : `
      <div class="tn-total"><span>Total (IVA incluido)</span><b>${fmt(suma)}</b></div>
      <p class="tn-note"><b>El envío no está incluido.</b> Una vez confirmado el pago te escribimos para coordinar la entrega y la instalación según tu localidad.</p>
      ${apiOk ? `
        <div class="tn-form">
          <div><label for="tn-nombre">Nombre y apellido</label><input id="tn-nombre" autocomplete="name" placeholder="Juan Pérez"></div>
          <div><label for="tn-email">Email</label><input id="tn-email" type="email" autocomplete="email" placeholder="juan@taller.com.ar"></div>
          <div><label for="tn-tel">Teléfono</label><input id="tn-tel" type="tel" autocomplete="tel" placeholder="11 2701-5294"></div>
          <div><label for="tn-loc">Localidad de entrega</label><input id="tn-loc" placeholder="Rosario, Santa Fe"></div>
          <label class="tn-check"><input type="checkbox" id="tn-ok" onchange="document.getElementById('tn-go').disabled=!this.checked">
            Entiendo que el costo de envío e instalación se acuerda por separado, después de la compra.</label>
        </div>
        <div class="tn-err" id="tn-err" hidden></div>
        <button class="tn-go" id="tn-go" disabled onclick="TIENDA.pagar()">${PAGAR_HTML}</button>
        <p class="tn-wa">¿Preferís coordinarlo con una persona? <a href="${wa}" target="_blank" rel="noopener">Escribinos por WhatsApp</a>.</p>`
      : `
        <p class="tn-note">El pago online está momentáneamente fuera de servicio. Cerramos la compra por WhatsApp con el mismo precio.</p>
        <a class="tn-go" href="${wa}" target="_blank" rel="noopener" style="display:block">Comprar por WhatsApp</a>`}`;
  }

  async function pagar() {
    const btn = document.getElementById('tn-go');
    const err = document.getElementById('tn-err');
    const email = (document.getElementById('tn-email').value || '').trim();
    if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) {
      err.textContent = 'Necesitamos un email válido para mandarte el comprobante.'; err.hidden = false; return;
    }
    err.hidden = true;
    btn.disabled = true; btn.textContent = 'Abriendo Mercado Pago…';

    try {
      const r = await fetch(rootPath() + 'api/tienda/checkout', {
        method: 'POST', headers: { 'content-type': 'application/json' },
        body: JSON.stringify({
          items: lines().map(([sku, qty]) => ({ sku, qty })),
          comprador: {
            nombre: (document.getElementById('tn-nombre').value || '').trim(),
            email,
            telefono: (document.getElementById('tn-tel').value || '').trim(),
            localidad: (document.getElementById('tn-loc').value || '').trim(),
          },
        }),
      });
      const data = await r.json();
      if (!r.ok || !data.init_point) throw new Error(data.mensaje || 'No pudimos abrir el checkout.');
      if (!buyNowSku) { cart.clear(); save(); }
      location.href = data.init_point;
    } catch (e) {
      err.textContent = e.message; err.hidden = false;
      btn.disabled = false; btn.innerHTML = PAGAR_HTML;
    }
  }

  /* ---------- Bloque de compra de la ficha de producto ---------- */
  function buyBox(sku, el) {
    const p = productos[sku], pr = priceOf(sku);
    if (!el) return;

    if (!pr) {
      // Equipo Trivium Pro sin precio cargado: no se inventa un botón.
      el.className = 'pd-ask';
      el.innerHTML = `
        <b>Precio a consultar</b>
        <p>Este equipo todavía no está disponible para compra online. Te pasamos precio y disponibilidad en el momento.</p>
        <a href="${waLink('Hola, quiero consultar el precio de: ' + ((p && p.name) || sku))}" target="_blank" rel="noopener">Consultar por WhatsApp</a>`;
      return;
    }

    const dentro = has(sku);
    el.className = 'pd-buy';
    el.innerHTML = `
      <div class="pd-buy-price">${fmt(pr.total_ars)}</div>
      <div class="pd-buy-iva">IVA ${String(pr.iva).replace('.', ',')}% incluido · precio final</div>
      <div class="pd-buy-envio">Envío e instalación a coordinar<span>Los cotizamos según tu localidad después de la compra.</span></div>
      <div class="pd-buy-acts">
        <button class="pd-buy-now" onclick="TIENDA.buyNow('${sku}')">Comprar ahora</button>
        <button class="pd-buy-add${dentro ? ' on' : ''}" id="pd-add-${sku}" onclick="TIENDA.toggleFrom('${sku}', this)">${dentro ? 'En el carrito' : 'Agregar al carrito'}</button>
      </div>
      <div class="pd-buy-trust">
        <div>${ICON_OK}<span>Importador oficial: <b>garantía y repuestos</b> en el país.</span></div>
        <div>${ICON_OK}<span>Instalación y servicio técnico <b>propios</b>.</span></div>
        <div>${ICON_OK}<span>Pagás con la <b>protección de Mercado Pago</b>.</span></div>
      </div>
      <div class="pd-buy-rate">Precio calculado con el dólar oficial venta de hoy (${fmt(table.rate)}).</div>`;
  }

  function toggleFrom(sku, btn) {
    const dentro = toggle(sku);
    btn.classList.toggle('on', dentro);
    btn.textContent = dentro ? 'En el carrito' : 'Agregar al carrito';
    if (dentro) toast('Agregado al carrito');
  }

  /* ---------- Arranque ---------- */
  let ready = null;
  function init() {
    if (ready) return ready;
    ready = (async () => {
      const [cat, t] = await Promise.all([loadCatalog(), loadTable()]);
      table = t;
      productos = Object.fromEntries(cat.products.map(p => [p.sku, p]));
      load();
      // Un carrito guardado puede tener un SKU que ya no se vende.
      [...cart.keys()].forEach(sku => { if (!sellable(sku)) cart.delete(sku); });
      save();
      mount(); emit();
      return table;
    })();
    return ready;
  }

  return { init, add, remove, toggle, toggleFrom, setQty, has, count, total, fmt,
           priceOf, sellable, open, close, buyNow, pagar, buyBox, toast, onChange,
           get table() { return table; }, get apiOk() { return apiOk; } };
})();
