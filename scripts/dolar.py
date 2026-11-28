"""Cotización del dólar oficial venta, única para todos los generadores.

Si no se puede obtener, corta con error: publicar con un valor fijo viejo deja
las fichas con un precio distinto al del feed y al que ve el visitante (pasó:
dolarapi rechaza con 403 el User-Agent por defecto de urllib).

Para generar sin red, pasar la cotización a mano:
    DOLAR_VENTA=1625 python3 scripts/generate_pretty_urls.py
"""
import functools
import json
import os
import urllib.request

URL = 'https://dolarapi.com/v1/dolares/oficial'


@functools.lru_cache(maxsize=None)
def dolar_venta():
    manual = os.environ.get('DOLAR_VENTA')
    if manual:
        return float(manual)
    req = urllib.request.Request(URL, headers={'User-Agent': 'price-generator/1.0'})
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            venta = json.load(r).get('venta')
    except Exception as e:
        raise SystemExit(f"No se pudo obtener el dólar oficial ({e}). No se genera nada. "
                         "Reintentar o usar DOLAR_VENTA=<cotización>.")
    if not venta:
        raise SystemExit("dolarapi respondió sin 'venta'. No se genera nada.")
    return venta
