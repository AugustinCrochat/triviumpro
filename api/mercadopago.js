/* API de la tienda — corre dentro del Worker (ver worker.js / generate_worker.py).
 *
 * Tres endpoints:
 *   GET  /api/tienda/precios   → tabla de precios del día (la usa /tienda/ y /lista-precios/)
 *   POST /api/tienda/checkout  → crea la preferencia de Mercado Pago, devuelve init_point
 *   POST /api/tienda/webhook   → notificaciones de MP (se registran en los logs del Worker)
 *
 * Por qué el precio se calcula acá y no en el navegador: el body del checkout
 * llega del cliente y cualquiera puede editarlo con las devtools. El Worker
 * ignora todo precio que venga en el request y lo recalcula desde
 * data/prices-publico.json con el dólar del día. El front pide la misma tabla a
 * /api/tienda/precios, así que muestra exactamente los números que se van a
 * cobrar y no hay diferencia entre la vidriera y el checkout.
 *
 * Requiere el secret MP_ACCESS_TOKEN (Access Token de producción de Mercado
 * Pago). Sin él, /checkout responde 503 y la tienda muestra el fallback a
 * WhatsApp en vez de romperse.
 */

import { crear as crearFolleto, obtener as obtenerFolleto } from './folleto.js';

const RATE_FALLBACK = 1520;      // mismo valor de referencia que usa site.js
const RATE_TTL = 900;            // 15 min de caché para la cotización
const MAX_ITEMS = 20;            // renglones distintos por orden
const MAX_QTY = 10;              // unidades por renglón

const json = (data, status = 200, extra = {}) =>
  new Response(JSON.stringify(data), {
    status,
    headers: { 'content-type': 'application/json; charset=utf-8', 'cache-control': 'no-store', ...extra },
  });

/* ---------- Cotización del dólar oficial (venta) ---------- */
async function getRate(ctx) {
  const key = new Request('https://tienda.trivium.ar/__rate');
  const cache = caches.default;

  const hit = await cache.match(key);
  if (hit) return hit.json();

  let out = { rate: RATE_FALLBACK, live: false };
  try {
    const r = await fetch('https://dolarapi.com/v1/dolares/oficial', { cf: { cacheTtl: RATE_TTL } });
    const j = await r.json();
    if (j && j.venta) out = { rate: j.venta, live: true };
  } catch (e) {
    // Se sigue con el valor de referencia: preferimos cobrar con un dólar
    // desactualizado antes que dejar la tienda caída.
  }

  if (out.live) {
    const store = json(out, 200, { 'cache-control': `public, max-age=${RATE_TTL}` });
    ctx.waitUntil(cache.put(key, store.clone()));
  }
  return out;
}

/* ---------- Datos del sitio (se leen del binding de assets) ---------- */
async function loadAsset(env, origin, path) {
  const res = await env.ASSETS.fetch(new Request(new URL(path, origin)));
  if (!res.ok) throw new Error(`No se pudo leer ${path} (${res.status})`);
  return res.json();
}

/* Precio de un ítem, en centavos redondeados a peso entero.
   base = precio sin IVA; total = lo que efectivamente se cobra. */
function priceOf(rec, defaultIva, rate) {
  const base = rec.fixed_ars != null ? rec.fixed_ars : rec.usd * rate;
  const iva = rec.iva != null ? rec.iva : defaultIva;
  return {
    usd: rec.usd ?? null,
    base_ars: Math.round(base),
    iva,
    total_ars: Math.round(base * (1 + iva / 100)),
  };
}

async function buildTable(env, origin, ctx) {
  const [prices, { rate, live }] = await Promise.all([
    loadAsset(env, origin, '/data/prices-publico.json'),
    getRate(ctx),
  ]);
  const defaultIva = prices.meta.default_iva;
  const items = {};
  for (const [sku, rec] of Object.entries(prices.items)) {
    if (rec.tienda === false) continue;
    items[sku] = { ...priceOf(rec, defaultIva, rate), modelo: rec.modelo || null, grupo: rec.grupo || null };
  }
  return { rate, rate_live: live, generado: new Date().toISOString(), items };
}

/* ---------- POST /api/tienda/checkout ---------- */
async function checkout(request, env, url, ctx) {
  if (!env.MP_ACCESS_TOKEN) {
    return json({ error: 'checkout_no_configurado',
                  mensaje: 'El pago online todavía no está habilitado. Escribinos por WhatsApp y lo cerramos por ahí.' }, 503);
  }

  let body;
  try { body = await request.json(); } catch (e) { return json({ error: 'json_invalido' }, 400); }

  const pedidos = Array.isArray(body && body.items) ? body.items : [];
  if (!pedidos.length) return json({ error: 'carrito_vacio' }, 400);
  if (pedidos.length > MAX_ITEMS) return json({ error: 'demasiados_items' }, 400);

  const [tabla, catalog] = await Promise.all([
    buildTable(env, url.origin, ctx),
    loadAsset(env, url.origin, '/data/catalog.json'),
  ]);
  const bySku = Object.fromEntries(catalog.products.map(p => [p.sku, p]));

  const mpItems = [];
  let total = 0;
  for (const linea of pedidos) {
    const sku = String(linea && linea.sku || '');
    const precio = tabla.items[sku];
    const p = bySku[sku];
    if (!precio || !p) return json({ error: 'sku_desconocido', sku }, 400);

    const qty = Math.min(MAX_QTY, Math.max(1, Math.floor(Number(linea.qty) || 1)));
    total += precio.total_ars * qty;
    mpItems.push({
      id: sku,
      title: p.name.slice(0, 250),
      description: `${precio.modelo || p.sku} — IVA ${precio.iva}% incluido`.slice(0, 250),
      picture_url: p.image ? new URL('/' + p.image.replace(/^\/+/, ''), url.origin).toString() : undefined,
      category_id: 'others',
      quantity: qty,
      currency_id: 'ARS',
      unit_price: precio.total_ars,
    });
  }

  const ref = 'TP-' + Date.now().toString(36).toUpperCase() + '-' +
              Math.random().toString(36).slice(2, 6).toUpperCase();
  const tienda = new URL('/tienda/gracias/', url.origin).toString();

  const pref = {
    items: mpItems,
    external_reference: ref,
    statement_descriptor: 'TRIVIUM PRO',
    // El envío y la instalación se coordinan después de la compra, así que no
    // se le pide a MP que calcule ni cobre un flete.
    shipments: { mode: 'not_specified' },
    back_urls: { success: tienda, pending: tienda, failure: tienda },
    auto_return: 'approved',
    notification_url: new URL('/api/tienda/webhook', url.origin).toString(),
    metadata: { origen: 'tienda-web', referencia: ref, total_ars: total, dolar: tabla.rate },
  };

  const contacto = body && body.comprador;
  if (contacto && typeof contacto === 'object') {
    pref.payer = {
      name: String(contacto.nombre || '').slice(0, 120) || undefined,
      email: String(contacto.email || '').slice(0, 120) || undefined,
    };
    pref.metadata.telefono = String(contacto.telefono || '').slice(0, 40);
    pref.metadata.localidad = String(contacto.localidad || '').slice(0, 120);
  }

  const r = await fetch('https://api.mercadopago.com/checkout/preferences', {
    method: 'POST',
    headers: {
      authorization: `Bearer ${env.MP_ACCESS_TOKEN}`,
      'content-type': 'application/json',
      'x-idempotency-key': ref,
    },
    body: JSON.stringify(pref),
  });
  const data = await r.json().catch(() => ({}));

  if (!r.ok || !data.init_point) {
    console.error('MP preference falló', r.status, JSON.stringify(data));
    return json({ error: 'mp_error', status: r.status,
                  mensaje: 'No pudimos abrir el checkout de Mercado Pago. Probá de nuevo o escribinos por WhatsApp.' }, 502);
  }

  console.log(`Preferencia ${data.id} · ref ${ref} · ${mpItems.length} ítems · $${total}`);
  return json({ init_point: data.init_point, preference_id: data.id, referencia: ref, total_ars: total });
}

/* ---------- Router ---------- */
export async function handleApi(request, env, url, ctx) {
  const path = url.pathname.replace(/\/+$/, '');

  if (path === '/api/tienda/precios' && request.method === 'GET') {
    try {
      return json(await buildTable(env, url.origin, ctx), 200,
                  { 'cache-control': 'public, max-age=300' });
    } catch (e) {
      console.error('precios falló', e);
      return json({ error: 'precios_no_disponibles' }, 500);
    }
  }

  if (path === '/api/tienda/checkout') {
    if (request.method !== 'POST') return json({ error: 'metodo_no_permitido' }, 405);
    try {
      return await checkout(request, env, url, ctx);
    } catch (e) {
      console.error('checkout falló', e && e.stack || e);
      return json({ error: 'checkout_falló' }, 500);
    }
  }

  if (path === '/api/folleto' && request.method === 'POST') {
    try {
      return await crearFolleto(request, env);
    } catch (e) {
      console.error('crear folleto falló', e && e.stack || e);
      return json({ error: 'crear_folleto_fallo' }, 500);
    }
  }

  const folletoMatch = path.match(/^\/api\/folleto\/([A-Za-z0-9]+)$/);
  if (folletoMatch) {
    if (request.method !== 'GET') return json({ error: 'metodo_no_permitido' }, 405);
    try {
      return await obtenerFolleto(env, folletoMatch[1]);
    } catch (e) {
      console.error('obtener folleto falló', e && e.stack || e);
      return json({ error: 'obtener_folleto_fallo' }, 500);
    }
  }

  if (path === '/api/tienda/webhook') {
    if (request.method !== 'POST') return json({ error: 'metodo_no_permitido' }, 405);
    // Sin base de datos no hay nada que persistir: se deja registro en los logs
    // del Worker (observability está activado) y se contesta 200 para que MP no
    // reintente. El seguimiento real de la orden se hace en el panel de MP.
    try { console.log('MP webhook', JSON.stringify(await request.json())); } catch (e) {}
    return new Response('ok', { status: 200 });
  }

  return json({ error: 'no_encontrado' }, 404);
}
