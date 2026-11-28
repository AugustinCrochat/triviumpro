"""Cotización dólar blue COMPRA, única para todos los generadores (desde el 28/11/2026).

Si no se puede obtener, corta con error: publicar con un valor fijo viejo deja
las fichas con un precio distinto al del feed y al que ve el visitante (pasó:
dolarapi rechaza con 403 el User-Agent por defecto de urllib).

Para generar sin red, pasar la cotización a mano:
    DOLAR=1675 python3 scripts/generate_pretty_urls.py
"""
import functools
import json
import os
import urllib.request

URL = 'https://dolarapi.com/v1/dolares/blue'


@functools.lru_cache(maxsize=None)
def dolar_blue_compra():
    manual = os.environ.get('DOLAR')
    if manual:
        return float(manual)
    req = urllib.request.Request(URL, headers={'User-Agent': 'price-generator/1.0'})
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            compra = json.load(r).get('compra')
    except Exception as e:
        raise SystemExit(f"No se pudo obtener el dólar blue ({e}). No se genera nada. "
                         "Reintentar o usar DOLAR=<cotización>.")
    if not compra:
        raise SystemExit("dolarapi respondió sin 'compra'. No se genera nada.")
    return compra
