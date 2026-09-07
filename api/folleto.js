/* Links cortos de selecciones del folleto (/f/<code>).
 *
 * El folleto arma un link con todo el estado —equipos elegidos, nombre,
 * WhatsApp, mail y opcionalmente una foto del vendedor— para no depender de
 * ningún backend. El problema es que una foto sola, aunque comprimida, ya son
 * varios miles de caracteres en la URL. Este endpoint guarda ese estado en
 * Cloudflare KV (binding FOLLETO_LINKS) bajo un código corto; el link que se
 * comparte es sólo /f/<code>, y el worker sirve ahí el mismo HTML del folleto
 * (ver worker.js), que a su vez pide estos datos por acá.
 *
 * Sin autenticación: cualquiera con el código puede leer esa selección, igual
 * que cualquiera con el link viejo (?sel=...) podía verlo. No hay más dato
 * sensible acá que el que ya viajaba en la URL.
 */

const CODE_LEN = 7;
// Sin 0/O/I/l/1: ambiguos al dictar o transcribir el código a mano.
const CODE_CHARS = 'ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz23456789';
const TTL_SECONDS = 60 * 60 * 24 * 180; // 6 meses: es una selección de venta, no un archivo a conservar
const MAX_SEL = 300;
const MAX_TEXT = 200;
const MAX_PHOTO_B64 = 40000; // ~30 KB decodificados: de sobra para un avatar de 56px

const json = (data, status = 200, extra = {}) =>
  new Response(JSON.stringify(data), {
    status,
    headers: { 'content-type': 'application/json; charset=utf-8', 'cache-control': 'no-store', ...extra },
  });

function randomCode() {
  const bytes = crypto.getRandomValues(new Uint8Array(CODE_LEN));
  let out = '';
  for (const b of bytes) out += CODE_CHARS[b % CODE_CHARS.length];
  return out;
}

function clampText(s, max) {
  return typeof s === 'string' ? s.slice(0, max) : '';
}

export async function crear(request, env) {
  if (!env.FOLLETO_LINKS) return json({ error: 'kv_no_configurado' }, 503);

  let body;
  try { body = await request.json(); } catch (e) { return json({ error: 'json_invalido' }, 400); }

  const sel = Array.isArray(body.sel)
    ? body.sel.filter((s) => typeof s === 'string').slice(0, MAX_SEL)
    : [];
  const data = {
    sel,
    vn: clampText(body.vn, MAX_TEXT),
    vp: clampText(body.vp, MAX_TEXT),
    ve: clampText(body.ve, MAX_TEXT),
    vf: clampText(body.vf, MAX_PHOTO_B64),
  };

  // Colisión de 7 caracteres en un alfabeto de 58 es ~1 en 2×10¹²: un
  // reintento sobra, pero el chequeo es gratis y evita pisar un link ajeno.
  let code = randomCode();
  for (let i = 0; i < 3 && (await env.FOLLETO_LINKS.get(code)) !== null; i++) code = randomCode();

  await env.FOLLETO_LINKS.put(code, JSON.stringify(data), { expirationTtl: TTL_SECONDS });
  return json({ code });
}

export async function obtener(env, code) {
  if (!env.FOLLETO_LINKS) return json({ error: 'kv_no_configurado' }, 503);
  if (!/^[A-Za-z0-9]{4,16}$/.test(code)) return json({ error: 'codigo_invalido' }, 400);

  const raw = await env.FOLLETO_LINKS.get(code);
  if (!raw) return json({ error: 'no_encontrado' }, 404);
  return new Response(raw, {
    status: 200,
    headers: { 'content-type': 'application/json; charset=utf-8', 'cache-control': 'no-store' },
  });
}
