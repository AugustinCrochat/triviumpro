/* Pruebas de api/mercadopago.js (la API de la tienda que corre en el Worker).
 *
 *     node scripts/test-tienda-api.mjs
 *
 * No necesita wrangler ni red: stubea env.ASSETS (lee los JSON del disco),
 * caches y las dos llamadas salientes — dolarapi y la API de Mercado Pago —
 * con un dólar fijo de 1535 para que los números den siempre igual.
 *
 * Lo que más importa acá es el bloque "el precio del cliente se ignora": el
 * body del checkout llega del navegador, y el Worker tiene que recalcular todo
 * desde data/prices-publico.json. */
import { readFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import { dirname, resolve } from 'node:path';

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const { handleApi } = await import(ROOT + '/api/mercadopago.js');

// Los precios esperados salen del propio JSON: si mañana entra una lista nueva
// el test sigue valiendo en vez de romperse por un número viejo.
const PRECIOS = JSON.parse(await readFile(ROOT + '/data/prices-publico.json', 'utf8'));
const RATE = 1535;
const esperado = (sku) => {
  const r = PRECIOS.items[sku];
  const base = r.fixed_ars != null ? r.fixed_ars : r.usd * RATE;
  const iva = r.iva != null ? r.iva : PRECIOS.meta.default_iva;
  return { base: Math.round(base), iva, total: Math.round(base * (1 + iva / 100)) };
};
const E30 = esperado('1010127'), UL01 = esperado('1010223'), FIJO = esperado('1010124');
const store = new Map();
// Como en Cloudflare: cada match() devuelve una Response nueva, no la misma
// instancia (si no, el body se consume en la primera lectura).
globalThis.caches = { default: {
  match: async (k) => store.has(k.url) ? new Response(store.get(k.url), { headers: { 'content-type': 'application/json' } }) : undefined,
  put: async (k, v) => { store.set(k.url, await v.text()); },
}};

let mpBody = null;
const realFetch = globalThis.fetch;
globalThis.fetch = async (url, opts = {}) => {
  const u = String(url.url || url);
  if (u.includes('dolarapi')) return new Response(JSON.stringify({ compra: 1535 }), { headers: { 'content-type': 'application/json' } });
  if (u.includes('mercadopago')) {
    mpBody = JSON.parse(opts.body);
    return new Response(JSON.stringify({ id: 'PREF-123', init_point: 'https://mp.test/checkout/PREF-123' }),
                        { headers: { 'content-type': 'application/json' } });
  }
  throw new Error('llamada saliente inesperada: ' + u);
};

const env = {
  MP_ACCESS_TOKEN: 'TEST-TOKEN',
  ASSETS: { fetch: async (req) => {
    const p = new URL(req.url || req).pathname;
    try { return new Response(await readFile(ROOT + p, 'utf8'), { headers: { 'content-type': 'application/json' } }); }
    catch (e) { return new Response('not found', { status: 404 }); }
  }},
};
const ctx = { waitUntil: (p) => p };
const call = (path, init) => {
  const url = new URL('https://pro.trivium.ar' + path);
  return handleApi(new Request(url, init), env, url, ctx);
};

let fail = 0;
const ok = (cond, msg) => { console.log((cond ? '  ✔ ' : '  ✘ ') + msg); if (!cond) fail++; };

console.log('\nGET /api/tienda/precios');
{
  const r = await call('/api/tienda/precios');
  const t = await r.json();
  ok(r.status === 200, 'responde 200');
  ok(t.rate === 1535 && t.rate_live, 'toma el dólar de dolarapi (1535, en vivo)');
  // 'tienda: false' (precio no confirmado, ver U-850) se filtra en la API,
  // así que el conteo esperado es el de vendibles, no el del JSON crudo.
  const vendibles = Object.values(PRECIOS.items).filter(r => r.tienda !== false).length;
  ok(Object.keys(t.items).length === vendibles, `devuelve ${vendibles} SKUs vendibles (${Object.keys(t.items).length})`);
  const e30 = t.items['1010127'];   // PL-E30: usd 4100, iva 10.5
  ok(e30.base_ars === E30.base, `PL-E30 sin IVA = ${e30.base_ars}`);
  ok(e30.total_ars === E30.total, `PL-E30 final con IVA = ${e30.total_ars}`);
  const fijo = t.items['1010124'];  // PL-4.2D: fixed_ars, no se recalcula
  ok(fijo.base_ars === PRECIOS.items['1010124'].fixed_ars, 'PL-4.2D respeta fixed_ars y no usa el dólar');
  ok(fijo.total_ars === FIJO.total, 'PL-4.2D final = fixed_ars + IVA');
  const acc = t.items['1010223'];   // PL-MT07: iva 21
  ok(acc.iva === UL01.iva && acc.total_ars === UL01.total, `PL-MT07 usa el IVA del JSON (${UL01.iva}%)`);
}

console.log('\nPOST /api/tienda/checkout');
{
  const r = await call('/api/tienda/checkout', {
    method: 'POST', headers: { 'content-type': 'application/json' },
    body: JSON.stringify({ items: [{ sku: '1010127', qty: 2 }, { sku: '1010223', qty: 1 }],
                           comprador: { nombre: 'Ana Gómez', email: 'ana@taller.ar', telefono: '1122334455', localidad: 'Rosario' } }),
  });
  const d = await r.json();
  ok(r.status === 200 && d.init_point === 'https://mp.test/checkout/PREF-123', 'devuelve el init_point de MP');
  ok(/^TP-[A-Z0-9]+-[A-Z0-9]{4}$/.test(d.referencia), `genera referencia (${d.referencia})`);
  const suma = E30.total * 2 + UL01.total;
  ok(d.total_ars === suma, `total ${d.total_ars} = 2×PL-E30 + 1×PL-MT07`);
  ok(mpBody.items[0].unit_price === E30.total, 'a MP le manda el precio CON IVA');
  ok(mpBody.items[0].quantity === 2, 'respeta la cantidad');
  ok(mpBody.shipments.mode === 'not_specified', 'no le pide flete a MP (envío a coordinar)');
  ok(mpBody.auto_return === 'approved' && mpBody.back_urls.success === 'https://pro.trivium.ar/tienda/gracias/', 'back_urls apuntan a /tienda/gracias/');
  ok(mpBody.payer.email === 'ana@taller.ar' && mpBody.metadata.localidad === 'Rosario', 'pasa los datos del comprador');
  ok(mpBody.items[0].picture_url.startsWith('https://pro.trivium.ar/assets/img/'), 'la foto va con URL absoluta');
}

console.log('\nSeguridad: el precio del cliente se ignora');
{
  await call('/api/tienda/checkout', {
    method: 'POST', headers: { 'content-type': 'application/json' },
    body: JSON.stringify({ items: [{ sku: '1010127', qty: 1, unit_price: 1, total_ars: 1, precio: 1 }] }),
  });
  ok(mpBody.items[0].unit_price === E30.total, 'un precio de $1 inyectado en el body no llega a MP');
}
{
  const r = await call('/api/tienda/checkout', {
    method: 'POST', headers: { 'content-type': 'application/json' },
    body: JSON.stringify({ items: [{ sku: '1010127', qty: 9999 }] }),
  });
  await r.json();
  ok(mpBody.items[0].quantity === 10, 'la cantidad se topea en 10');
}

console.log('\nErrores');
{
  ok((await call('/api/tienda/checkout', { method: 'POST', headers: {'content-type':'application/json'}, body: '{"items":[]}' })).status === 400, 'carrito vacío → 400');
  const r = await call('/api/tienda/checkout', { method: 'POST', headers: {'content-type':'application/json'}, body: '{"items":[{"sku":"NO-EXISTE"}]}' });
  ok(r.status === 400 && (await r.json()).error === 'sku_desconocido', 'SKU inexistente → 400 sku_desconocido');
  ok((await call('/api/tienda/checkout', { method: 'GET' })).status === 405, 'GET al checkout → 405');
  ok((await call('/api/tienda/nada')).status === 404, 'endpoint inexistente → 404');
  ok((await call('/api/tienda/webhook', { method: 'POST', headers: {'content-type':'application/json'}, body: '{"type":"payment"}' })).status === 200, 'webhook → 200');
  const sinToken = await handleApi(new Request('https://pro.trivium.ar/api/tienda/checkout', { method: 'POST', headers: {'content-type':'application/json'}, body: '{"items":[{"sku":"1010127"}]}' }),
                                   { ...env, MP_ACCESS_TOKEN: undefined }, new URL('https://pro.trivium.ar/api/tienda/checkout'), ctx);
  ok(sinToken.status === 503, 'sin MP_ACCESS_TOKEN → 503 (la tienda cae a WhatsApp)');
}

console.log(fail ? `\n${fail} fallo(s)` : '\nTodo OK');
process.exit(fail ? 1 : 0);
