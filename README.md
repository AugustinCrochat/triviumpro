# Trivium Center — Sitio estático

Sitio estático para [trivium.ar](https://trivium.ar), listo para publicar en **GitHub Pages**.

## Estructura

```
.
├── index.html              Home
├── catalogo.html           Listado general
├── categoria.html          Listado filtrado (?c=slug o ?b=slug)
├── producto.html           Ficha individual (?id=slug)
├── marcas.html             Marcas representadas
├── servicios.html          Servicios ofrecidos
├── nosotros.html           Quiénes somos
├── contacto.html           Formulario + datos
├── data/
│   └── catalog.json        ÚNICO archivo a editar para agregar productos
└── assets/
    ├── css/styles.css
    └── js/site.js
```

## Cómo agregar productos

Todo el catálogo vive en `data/catalog.json`. Cada producto tiene esta forma:

```json
{
  "sku": "ROT-SPOA10",
  "slug": "rotary-spoa10",
  "name": "Elevador 2 Columnas SPOA10",
  "category": "elevadores-2-columnas",
  "brand": "rotary-lift",
  "capacity": "4082 kg",
  "lift_height": "1930 mm",
  "summary": "Descripción corta que aparece en la ficha.",
  "bullets": ["Feature 1", "Feature 2", "..."],
  "badges": ["Top", "Oferta"]
}
```

- **slug** es la URL (`producto.html?id=<slug>`), debe ser único.
- **category** y **brand** deben coincidir con los slugs definidos arriba en `categories` / `brands`.
- **badges** son opcionales; se muestran como "cintas" en la tarjeta.

Para agregar una categoría o marca nueva, sumala al array correspondiente en el mismo JSON.

### Imágenes de producto

Hoy los productos muestran un placeholder a rayas con el SKU. Cuando tengas las imágenes:

1. Guardalas en `assets/img/productos/<slug>.jpg` (o `.webp`).
2. En `assets/js/site.js`, dentro de `productCard()`, reemplazá la línea `<span>Imagen / ${p.sku}</span>` por:
   ```js
   `<img src="${rootPath()}assets/img/productos/${p.slug}.jpg" alt="${p.name}" loading="lazy">`
   ```
3. Hacé lo mismo en `producto.html` (dentro del bloque `pd-gallery`).

## Publicar en GitHub Pages

1. Creá un repo nuevo en GitHub, p. ej. `trivium-site`.
2. Cloná este proyecto y subí los archivos al repo (`git init && git add . && git commit -m "init" && git push`).
3. En GitHub → **Settings → Pages**: Source = *Deploy from a branch*, Branch = `main`, Folder = `/ (root)`.
4. Si querés usar el dominio `trivium.ar`, agregá un archivo `CNAME` en la raíz con `trivium.ar` adentro, y configurá los DNS del dominio hacia los IPs de GitHub Pages (185.199.108–111.153).

## Contacto / WhatsApp

El teléfono y email viven en `assets/js/site.js`, al tope del archivo, dentro de `window.TRIVIUM`. Editá ahí para cambiarlos globalmente.

## Diseño

- **Paleta**: negro profundo + bone white + rojo industrial `#e4352b`.
- **Tipografías**: Archivo + Archivo Black + JetBrains Mono (todas Google Fonts).
- **Estilo**: industrial / técnico, tipografías fuertes, sin gradientes suaves.

---

© Trivium Center — Hecho en Argentina.

## Migración de imágenes (dejar de depender del WordPress)

Antes de dar de baja `trivium.ar` en WordPress, descargá todas las imágenes al repo:

```bash
python3 scripts/download_images.py
# o
bash scripts/download-images.sh
```

Esto:
1. Descarga las 159 imágenes referenciadas en `data/catalog.json` a `assets/img/productos/`.
2. Reescribe `catalog.json` reemplazando las URLs de `trivium.ar/wp-content/uploads/...` por rutas locales `assets/img/productos/...`.

Después `git add . && git commit -m "imágenes locales" && git push` y listo: el sitio ya no depende del WP.
