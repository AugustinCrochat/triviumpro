/* Precios públicos — equipos Trivium Pro (fichas de producto)
   Confidencial NO. Se muestra en las páginas /producto/ del sitio.

   Fuente: "Precio Venta CONTADO U$D sin IVA" de la lista de precios interna
   (columna E), NO el precio de reventa/revendedor (ese es confidencial y
   vive en lista-revendedores-5d2f2e5e/prices.js).

   El precio en pesos se calcula en vivo con el dólar OFICIAL VENTA
   (dolarapi.com), salvo que el ítem tenga "fixed_ars" — en ese caso se
   muestra ese valor fijo en pesos en vez de recalcularlo con el dólar.

   Clave = SKU tal como figura en data/catalog.json.
*/
window.PUBLIC_PRICES = {
  meta: {
    default_iva: 10.5
  },
  items: {
    // Elevadores 2 columnas
    "1010124": { fixed_ars: 2750000, iva: 10.5 }, // PL-4.2D — precio fijo, no se recalcula con el dólar
    "1010144": { usd: 2000,  iva: 10.5 }, // PL-4.0 2AD
    "1010271": { usd: 4995,  iva: 10.5 }, // U-T50MSD
    // Elevador 4 columnas
    "1010261": { usd: 7100,  iva: 10.5 }, // PL-FS50
    // Elevadores tijera
    "1010143": { usd: 2300,  iva: 10.5 }, // PL-B30M
    "1010127": { usd: 4100,  iva: 10.5 }, // PL-E30
    "1010282": { usd: 8590,  iva: 10.5 }, // PL-C55
    "1010263": { usd: 5100,  iva: 10.5 }, // PL-B30Y
    "1010281": { usd: 2850,  iva: 10.5 }, // PL-45H
    // Elevador batería EV
    "1010290": { usd: 2795,  iva: 10.5 }, // U-DP5
    // Balanceadoras
    "1010272": { usd: 2600,  iva: 10.5 }, // G-66
    "1010122": { usd: 861,   iva: 10.5 }, // S-901
    // Desarmadoras
    "1010265": { usd: 1190,  iva: 10.5 }, // PL-1200U
    "1010267": { usd: 3250,  iva: 10.5 }, // PL-1256S
    // Accesorios (IVA 21%)
    "1010034": { usd: 495,   iva: 21 }    // U-L01
  }
};
