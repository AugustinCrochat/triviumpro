"""Genera worker.js a partir de redirects.map.

Cloudflare no puede resolver estos redirects con el archivo _redirects: en
Workers con assets estáticos el tope es de 100 reglas y acá hay 426, así que
el build fallaba con "Maximum number of dynamic _redirects rules limit of 100
exceeded". El Worker los resuelve con un lookup en un objeto, sin ese límite.

Uso:
    python3 scripts/generate_worker.py
"""

import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCE = os.path.join(BASE_DIR, 'redirects.map')
TARGET = os.path.join(BASE_DIR, 'worker.js')


def parse():
    exact, prefix = {}, []
    with open(SOURCE, encoding='utf-8') as f:
        for n, raw in enumerate(f, 1):
            line = raw.strip()
            if not line or line.startswith('#'):
                continue
            parts = line.split()
            if len(parts) != 3:
                raise SystemExit(f"redirects.map línea {n}: se esperaban 3 campos, hay {len(parts)}")
            src, dst, code = parts
            if code != '301':
                raise SystemExit(f"redirects.map línea {n}: sólo se admiten 301, hay {code}")
            if src.endswith('*'):
                prefix.append((src[:-1], dst.replace(':splat', '')))
            else:
                exact[src] = dst
    return exact, prefix


def main():
    exact, prefix = parse()

    dup = len(exact) + len(prefix)
    body = f"""// GENERADO por scripts/generate_worker.py — no editar a mano.
// La fuente de verdad es redirects.map ({dup} reglas).
//
// Existe porque _redirects no sirve acá: Cloudflare limita a 100 las reglas en
// Workers con assets estáticos, y el build fallaba al superarlo.
//
// La tienda (/api/tienda/*) se atiende desde api/mercadopago.js, que sí se
// edita a mano. Se resuelve antes que los redirects para que ninguna regla de
// redirects.map pueda tapar un endpoint.

import {{ handleApi }} from "./api/mercadopago.js";

// Link corto de una selección del folleto (/f/<code>): sirve el mismo HTML
// que /folleto-<secreto>/ — el cliente pide los datos a /api/folleto/<code>
// (ver api/folleto.js) en vez de leerlos de la query string. El secreto vive
// acá, en código que corre en el Worker y nunca se manda al navegador, así
// que no queda expuesto como quedaría si estuviera en un JS del sitio.
const FOLLETO_PATH = "/folleto-8f3a1c9d/";
const F_CODE = /^\\/f\\/([A-Za-z0-9]{{4,16}})\\/?$/;
// precios.js se referencia sin "../" desde el HTML del folleto (vive en la
// misma carpeta que index.html), así que en /folleto-<secreto>/ resuelve
// solo. En /f/<code> esa ruta relativa resuelve a /f/precios.js en vez de
// /folleto-<secreto>/precios.js — de ahí este alias, con el mismo cuidado de
// no escribir el secreto en ningún JS que llegue al navegador.
const F_PRECIOS = "/f/precios.js";

const EXACT = {json.dumps(exact, ensure_ascii=False, indent=1, sort_keys=True)};

const PREFIX = {json.dumps(prefix, ensure_ascii=False, indent=1)};

function destinoPara(pathname) {{
  // Se prueban las dos formas: el catálogo usa barra final, pero Google
  // conserva URLs viejas sin ella.
  const alterna = pathname.endsWith("/") ? pathname.slice(0, -1) : pathname + "/";
  const exacto = EXACT[pathname] ?? EXACT[alterna];
  if (exacto) return exacto;

  for (const [desde, hacia] of PREFIX) {{
    if (pathname.startsWith(desde)) return hacia + pathname.slice(desde.length);
  }}
  return null;
}}

export default {{
  async fetch(request, env, ctx) {{
    try {{
      const url = new URL(request.url);
      if (url.pathname.startsWith("/api/")) return handleApi(request, env, url, ctx);

      if (url.pathname === F_PRECIOS) {{
        const destino = new URL(FOLLETO_PATH + "precios.js", url.origin);
        return env.ASSETS.fetch(new Request(destino, request));
      }}

      if (F_CODE.test(url.pathname)) {{
        const destino = new URL(FOLLETO_PATH, url.origin);
        return env.ASSETS.fetch(new Request(destino, request));
      }}

      const destino = destinoPara(decodeURIComponent(url.pathname));
      if (destino) {{
        const salida = new URL(destino, url.origin);
        salida.search = url.search;
        return Response.redirect(salida.toString(), 301);
      }}
    }} catch (e) {{
      // Ante cualquier problema resolviendo el redirect, se sirve el asset:
      // más vale un 404 puntual que tumbar el sitio entero.
    }}
    return env.ASSETS.fetch(request);
  }},
}};
"""
    with open(TARGET, 'w', encoding='utf-8') as f:
        f.write(body)
    print(f"✔ worker.js — {len(exact)} exactos + {len(prefix)} por prefijo")


if __name__ == '__main__':
    main()
