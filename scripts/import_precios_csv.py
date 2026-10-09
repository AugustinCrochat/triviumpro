#!/usr/bin/env python3
"""Importa la lista de precios interna (CSV exportado de la planilla) y genera
los dos archivos de precios que consume el sitio.

    python3 scripts/import_precios_csv.py [ruta/al.csv]

Salidas:
  data/prices-publico.json          Solo marca propia (Trivium Pro). PÚBLICO:
                                    lo leen las fichas, /tienda/, /folleto/,
                                    el feed de Meta y el Worker.
  <FOLLETO_DIR>/precios.js          Todas las marcas. NO público: vive dentro
                                    de la carpeta de slug secreto, igual que
                                    lista-revendedores-5d2f2e5e/prices.js.

Por qué la separación: publicar en /data/ los precios de Rotary, Hofmann o
Josam los deja a un fetch de distancia de cualquiera, incluida la competencia.
Todo lo que no sea marca propia se sirve solo desde la carpeta secreta.

El CSV fuente se guarda en scripts/precios/ y no en la raíz: 'scripts' está en
.assetsignore, así que Cloudflare no lo sirve. En la raíz quedaría público.

Columnas del CSV (0-indexed), según el export de la planilla:
    5 SKU · 6 marca · 7 modelo · 8 características
    9 'Precio Venta CONTADO U$D sin IVA' · 13 alícuota de IVA
"""
import csv
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CSV_DEFAULT = ROOT / "scripts" / "precios" / "precios-dolar.csv"
FOLLETO_DIR = ROOT / "folleto-8f3a1c9d"     # slug secreto, igual criterio que revendedores
MARCA_PROPIA = "trivium-pro"

COL_SKU, COL_MARCA, COL_MODELO, COL_DESC, COL_USD, COL_IVA = 5, 6, 7, 8, 9, 13

# Precios en pesos fijados a mano: la BASE sin IVA queda clavada en este valor
# y no se recalcula con el dólar; el IVA se suma aparte como en cualquier otro
# ítem. Se respetan aunque el CSV traiga un USD para ese SKU.
#
# 1010124 (PL-4.2D): confirmado el 2026-08-30 — va $2.750.000 + IVA 10,5%
# ($3.038.750 final). El CSV lo trae a USD 1929, que daría ~$3.270.000; ese
# valor se ignora a propósito.
FIXED_ARS = {"1010124": 2750000}

# Equipos cuyo SKU del sitio no existe en la planilla, mapeados a mano contra la
# fila correcta del CSV. Cuatro de ellos quedaron en el catálogo con un SKU
# provisorio ("P-3041" y compañía) y por eso nunca cruzaron.
#
# Se hace con un mapa explícito y NO adivinando por parecido de nombre: un match
# difuso equivocado le pone a una máquina el precio de otra, y eso se descubre
# recién cuando un cliente reclama.
#
#   SKU del sitio -> SKU en el CSV
MATCH_MANUAL = {
    "P-3041":  "1010171",   # Elevador 4 columnas 8165 kg → ROTARY SM18 (la ficha del CSV dice 8165 kg)
    "P-4371":  "1010010",   # Elevador tijera corto 3000 kg → DIRECT LIFT DIG30
    "P-3338":  "1010118",   # Desarmadora Hofmann Monty 8800 → HOFMANN Monty 8800
    "1010053": "4010059",   # Llave crique neumática KI-2422 → Kuani ki-2422
    # OJO: el modelo coincide (U-850) pero la descripción del CSV habla de una
    # PL-2900 14-26". Confirmar con la lista antes de publicarlo como definitivo.
    "P-5406":  "1010300",   # Balanceadora de camión U-850
}

# Equipos que se muestran en el folleto con precio pero NO se venden online.
# 'tienda': false los saca de /tienda/ y del checkout. Se usa cuando el precio
# todavía no está confirmado: mostrarlo como referencia es barato, cobrarlo mal
# no.
SIN_VENTA_ONLINE = {
    "P-5406",   # precio mapeado a mano, pendiente de confirmar (ver arriba)
}


# Factor sobre el precio de planilla para los precios PUBLICADOS en la web.
# Se aplica acá, al generar data/prices-publico.json, y no en cada consumidor:
# así fichas, /tienda/, /lista-precios/, el feed y el Worker leen todos el mismo
# número y no hay un segundo cálculo que pueda desincronizarse. El folleto
# interno (folleto-8f3a1c9d/precios.js) conserva los precios de planilla.
PRECIO_WEB_FACTOR = 1.25

# Ítems con precio público fijado a mano: se publican tal cual, sin el factor.
# U-L01: $762.300 + IVA 21%, definido el 2026-10-07. tienda:false = se muestra
# en la ficha pero no entra a la venta online.
PUBLICO_MANUAL = {
    "1010034": {"modelo": "U-L01", "iva": 21, "fixed_ars": 762300, "tienda": False},
}


def parse_usd(v):
    v = (v or "").strip()
    if not v or "#" in v:            # '#N/A' de la planilla
        return None
    m = re.search(r"([\d,]+\.?\d*)", v.replace("USD", "").strip())
    return float(m.group(1).replace(",", "")) if m else None


def parse_iva(v):
    m = re.search(r"([\d.]+)", (v or "").strip())
    return float(m.group(1)) if m else None


def norm(s):
    return re.sub(r"[^a-z0-9]", "", (s or "").lower())


def leer_csv(path):
    """sku -> lista de filas candidatas (hay SKUs repetidos con productos distintos)."""
    filas = defaultdict(list)
    with open(path, encoding="utf-8") as f:
        for r in csv.reader(f):
            if len(r) <= COL_IVA:
                continue
            sku = r[COL_SKU].strip()
            if not re.fullmatch(r"\d{7}", sku):
                continue
            usd = parse_usd(r[COL_USD])
            if usd is None:
                continue
            filas[sku].append({
                "usd": usd,
                "iva": parse_iva(r[COL_IVA]),
                "marca": r[COL_MARCA].strip(),
                "modelo": r[COL_MODELO].strip(),
                "desc": r[COL_DESC].strip(),
            })
    return filas


def elegir(candidatas, producto):
    """La planilla reusa algunos SKU para dos productos distintos (por ejemplo
    1010223 es un elevador de moto y también un comprobador de baterías). Se
    elige la fila cuyo modelo aparezca en el nombre del producto del sitio."""
    if len(candidatas) == 1:
        return candidatas[0]
    nombre = norm(producto["name"])
    for c in candidatas:
        m = norm(c["modelo"])
        if m and len(m) >= 3 and m in nombre:
            return c
    return candidatas[0]


def main():
    csv_path = Path(sys.argv[1]) if len(sys.argv) > 1 else CSV_DEFAULT
    if not csv_path.exists():
        raise SystemExit(f"No encuentro el CSV: {csv_path}")

    catalog = json.loads((ROOT / "data" / "catalog.json").read_text(encoding="utf-8"))
    filas = leer_csv(csv_path)

    publico, privado, sin_precio, ambiguos = {}, {}, [], []
    for p in sorted(catalog["products"], key=lambda x: x["sku"]):
        sku = p["sku"]
        cands = filas.get(MATCH_MANUAL.get(sku, sku))
        if not cands:
            sin_precio.append(p)
            continue
        if len(cands) > 1:
            ambiguos.append((sku, p["name"], [c["modelo"] for c in cands]))
        c = elegir(cands, p)

        item = {"modelo": c["modelo"] or None, "iva": c["iva"]}
        if sku in SIN_VENTA_ONLINE:
            item["tienda"] = False
        if sku in FIXED_ARS:
            item["fixed_ars"] = FIXED_ARS[sku]
        else:
            item["usd"] = c["usd"]

        privado[sku] = {**item, "marca": p["brand"] or c["marca"]}
        if p["brand"] == MARCA_PROPIA:
            web = dict(item)
            if "usd" in web:
                web["usd"] = round(web["usd"] * PRECIO_WEB_FACTOR, 2)
            if "fixed_ars" in web:
                web["fixed_ars"] = round(web["fixed_ars"] * PRECIO_WEB_FACTOR)
            publico[sku] = web
    publico.update(PUBLICO_MANUAL)

    # ---- público: solo marca propia ----
    destino_pub = ROOT / "data" / "prices-publico.json"
    doc = json.loads(destino_pub.read_text(encoding="utf-8"))["_doc"]
    destino_pub.write_text(json.dumps({
        "_doc": doc,
        "meta": {"default_iva": 10.5},
        "items": publico,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    # ---- privado: todas las marcas, dentro de la carpeta secreta ----
    FOLLETO_DIR.mkdir(exist_ok=True)
    (FOLLETO_DIR / "precios.js").write_text(
        "/* Precios de TODAS las marcas — CONFIDENCIAL.\n"
        "   Generado por scripts/import_precios_csv.py; no editar a mano.\n"
        "   Vive acá y no en /data/ porque /data/ es público: esto incluye los\n"
        "   precios de Rotary, Hofmann, Haweka y Josam.\n"
        "   'usd' es el precio de venta contado SIN IVA. */\n"
        "window.FOLLETO_PRECIOS = "
        + json.dumps({"meta": {"default_iva": 10.5}, "items": privado},
                     ensure_ascii=False, indent=2)
        + ";\n", encoding="utf-8")

    print(f"✔ data/prices-publico.json — {len(publico)} equipos {MARCA_PROPIA}")
    print(f"✔ {FOLLETO_DIR.name}/precios.js — {len(privado)} equipos, todas las marcas")
    print(f"  sin precio en el CSV: {len(sin_precio)} (van como 'Consultar')")
    if ambiguos:
        print(f"  SKU repetidos en la planilla, resueltos por modelo: {len(ambiguos)}")
        for sku, nombre, modelos in ambiguos:
            print(f"    {sku} {nombre[:45]} ← {modelos}")


if __name__ == "__main__":
    main()
