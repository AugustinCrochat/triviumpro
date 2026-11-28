#!/usr/bin/env python3
"""Control: el precio de cada ficha prerenderizada (schema Offer) tiene que ser
el mismo que el del feed de Google Merchant. Google rechaza los que no coinciden.

Uso: python3 scripts/check_precios.py   (después de los generadores)
"""
import csv
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def ofertas(nodo):
    if isinstance(nodo, dict):
        if nodo.get('@type') == 'Product' and isinstance(nodo.get('offers'), dict):
            yield nodo['offers']
        for v in nodo.values():
            yield from ofertas(v)
    elif isinstance(nodo, list):
        for v in nodo:
            yield from ofertas(v)


def main():
    comparadas, errores = 0, []
    with open(ROOT / 'feeds' / 'google-merchant.tsv', encoding='utf-8') as f:
        for fila in csv.DictReader(f, delimiter='\t'):
            slug = fila['link'].split('?')[0].rstrip('/').rsplit('/', 1)[-1]
            pagina = ROOT / 'producto' / slug / 'index.html'
            if not pagina.exists():
                errores.append(f"{slug}: está en el feed y no tiene ficha")
                continue
            bloques = re.findall(r'<script type="application/ld\+json">(.*?)</script>',
                                 pagina.read_text(encoding='utf-8'), re.S)
            precios = [float(o['price']) for b in bloques for o in ofertas(json.loads(b)) if o.get('price')]
            feed = float(fila['price'].split()[0])
            comparadas += 1
            if not precios:
                errores.append(f"{slug}: ficha sin precio, feed {feed:.2f}")
            elif abs(precios[0] - feed) > 1:
                errores.append(f"{slug}: ficha {precios[0]:.2f}, feed {feed:.2f}")
    if errores:
        print('\n'.join(errores))
        sys.exit(f"✘ {len(errores)} diferencias de precio ({comparadas} fichas comparadas)")
    if not comparadas:
        sys.exit("✘ no se comparó ninguna ficha")
    print(f"✔ {comparadas} fichas con el mismo precio que el feed")


if __name__ == '__main__':
    main()
