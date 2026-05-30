#!/bin/bash
# Asset optimization script: images → WebP, PDFs → Ghostscript /ebook
# Run from project root: bash scripts/optimize-assets.sh
set -euo pipefail

SITE_DIR="$(cd "$(dirname "$0")/.." && pwd)"
IMG_DIR="$SITE_DIR/assets/img"
PDF_DIR="$SITE_DIR/assets/pdf"

img_saved=0
pdf_saved=0

echo "========================================"
echo " Trivium Asset Optimizer"
echo "========================================"
echo ""

# ─── 1. JPG / JPEG / PNG → WebP ─────────────────────────────────────────────
echo "── Imágenes (JPG/PNG → WebP) ─────────────"
while IFS= read -r src; do
  dst="${src%.*}.webp"
  convert "$src" -quality 85 "$dst"
  old=$(stat -c%s "$src")
  new=$(stat -c%s "$dst")
  if [ "$new" -lt "$old" ]; then
    saved=$(( old - new ))
    img_saved=$(( img_saved + saved ))
    pct=$(( saved * 100 / old ))
    echo "  ✓ $(basename "$src")  →  $(basename "$dst")  (-${pct}%)"
    rm "$src"
  else
    # WebP would be larger — keep original, remove webp
    rm "$dst"
    echo "  – $(basename "$src")  sin cambios (ya comprimido)"
  fi
done < <(find "$IMG_DIR" -type f \( -name "*.jpg" -o -name "*.jpeg" -o -name "*.png" \))

# ─── 2. GIF animado → WebP animado ──────────────────────────────────────────
echo ""
echo "── GIF animado → WebP animado ────────────"
while IFS= read -r src; do
  dst="${src%.*}.webp"
  ffmpeg -i "$src" -c:v libwebp -lossless 0 -q:v 75 -loop 0 -an "$dst" -y 2>/dev/null
  old=$(stat -c%s "$src")
  new=$(stat -c%s "$dst")
  saved=$(( old - new ))
  img_saved=$(( img_saved + saved ))
  pct=$(( saved * 100 / old ))
  echo "  ✓ $(basename "$src")  →  $(basename "$dst")  (-${pct}%)"
  rm "$src"
done < <(find "$IMG_DIR" -type f -name "*.gif")

# ─── 3. Comprimir PDFs con Ghostscript /ebook ────────────────────────────────
echo ""
echo "── PDFs (Ghostscript /ebook 150dpi) ──────"
while IFS= read -r src; do
  tmp="${src}.tmp"
  gs -sDEVICE=pdfwrite -dCompatibilityLevel=1.4 -dPDFSETTINGS=/ebook \
     -dNOPAUSE -dQUIET -dBATCH -sOutputFile="$tmp" "$src"
  old=$(stat -c%s "$src")
  new=$(stat -c%s "$tmp")
  if [ "$new" -lt "$old" ]; then
    saved=$(( old - new ))
    pdf_saved=$(( pdf_saved + saved ))
    pct=$(( saved * 100 / old ))
    mv "$tmp" "$src"
    echo "  ✓ $(basename "$src")  (-${pct}%)"
  else
    rm "$tmp"
    echo "  – $(basename "$src")  sin cambios"
  fi
done < <(find "$PDF_DIR" -name "*.pdf" -type f)

# ─── 4. Actualizar referencias en JSON / JS / HTML ──────────────────────────
echo ""
echo "── Actualizando referencias ──────────────"

python3 - "$SITE_DIR" <<'PYEOF'
import sys, re, os

SITE = sys.argv[1]
PATTERN = re.compile(r'(assets/img/[^\s"\'<>]+)\.(jpg|jpeg|png|gif)\b')

targets = [
    os.path.join(SITE, "data", "catalog.json"),
    os.path.join(SITE, "data", "blog.json"),
    os.path.join(SITE, "data", "catalog.js"),
    os.path.join(SITE, "data", "blog.js"),
]

# Also find all HTML files
for root, dirs, files in os.walk(SITE):
    dirs[:] = [d for d in dirs if d not in ('node_modules', '.git')]
    for fn in files:
        if fn.endswith('.html'):
            targets.append(os.path.join(root, fn))

for path in targets:
    if not os.path.exists(path):
        continue
    with open(path) as fh:
        content = fh.read()
    new_content = PATTERN.sub(r'\1.webp', content)
    if new_content != content:
        with open(path, 'w') as fh:
            fh.write(new_content)
        count = len(PATTERN.findall(content))
        print(f"  ✓ {os.path.relpath(path, SITE)}  ({count} refs)")
PYEOF

# ─── 5. Resumen ──────────────────────────────────────────────────────────────
echo ""
echo "========================================"
echo " Resumen"
echo "========================================"
printf "  Imágenes ahorradas:  %d KB\n" "$(( img_saved / 1024 ))"
printf "  PDFs ahorrados:      %d KB\n" "$(( pdf_saved / 1024 ))"
printf "  TOTAL ahorrado:      %d KB (%.1f MB)\n" \
  "$(( (img_saved + pdf_saved) / 1024 ))" \
  "$(echo "scale=1; (${img_saved} + ${pdf_saved}) / 1048576" | bc)"
echo ""
echo "── Tamaño final ──────────────────────────"
du -sh "$IMG_DIR" "$PDF_DIR"
