#!/usr/bin/env bash
# Descarga todas las imágenes de productos desde trivium.ar (WordPress)
# al repo local, y reescribe data/catalog.json para usar rutas relativas.
#
# Uso:
#   bash scripts/download-images.sh
# Requiere: curl, jq, python3

set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

mkdir -p assets/img/productos

echo "▶ Descargando imágenes a assets/img/productos/ ..."
python3 scripts/download_images.py

echo "✔ Listo. Revisá git status y commiteá los cambios."
