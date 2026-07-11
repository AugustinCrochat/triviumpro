/* Lista de precios REVENDEDORES 2025 — Trivium Pro
   Confidencial. Solo referenciado desde la página secreta de esta carpeta.

   BASE = dólares. usd_reseller = "Precio de Reventa USD sin IVA" (columna K de la lista).
   El precio en pesos se calcula en vivo con el dólar OFICIAL VENTA (dolarapi.com).
   El "precio de lista sugerido" = usd_reseller sin el 15% de descuento = usd_reseller / 0.85.
   iva = alícuota a aclarar como "+ IVA" (por defecto 10,5% para las máquinas).

   Clave = SKU tal como figura en data/catalog.json.
   Solo los SKU listados acá se muestran en la página (fuente de verdad del listado).
*/
window.RESELLER_PRICES = {
  meta: {
    list_label: "Lista de precios 2025",
    audience: "Revendedores",
    reseller_discount: 0.15,   // el precio revendedor ya tiene 15% de descuento sobre el de lista
    default_iva: 10.5
  },
  items: {
    // Elevadores 2 columnas
    "1010124": { usd_reseller: 1640, caracteristicas: "Elevador 2 columnas 4000 kg — travesaño al piso" },
    "1010144": { usd_reseller: 1700, caracteristicas: "Elevador 2 columnas 4000 kg — travesaño arriba" },
    "1010271": { usd_reseller: 4246, caracteristicas: "Elevador 2 columnas 5000 kg — travesaño arriba alto" },
    // Elevadores 4 columnas
    "1010261": { usd_reseller: 6035, caracteristicas: "Elevador 4 columnas 5T — kit de alineación + Rolling Jack" },
    // Elevadores tijera
    "1010143": { usd_reseller: 1955, caracteristicas: "Elevador tijera móvil" },
    "1010127": { usd_reseller: 3485, caracteristicas: "Elevador tijera corto para embutir 3500 kg" },
    "1010263": { usd_reseller: 4335, caracteristicas: "Elevador tijera corto sobre piso 3000 kg — bajo perfil" },
    "1010282": { usd_reseller: 7302, caracteristicas: "Elevador tijera largo — kit de alineación" },
    "1010281": { usd_reseller: 2423, caracteristicas: "Elevador p/gomería 4.5T — piso" },
    // Elevador moto
    "1010223": { usd_reseller: 816,  caracteristicas: "Elevador para moto 454 kg — MT07" },
    // Elevador batería EV
    "1010290": { usd_reseller: 2376, caracteristicas: "Elevador p/batería EV 1T" },
    // Balanceadoras
    "1010272": { usd_reseller: 2210, caracteristicas: "Balanceadora de ruedas con monitor" },
    "1010122": { usd_reseller: 732,  caracteristicas: "Balanceadora para ruedas de auto" },
    "P-5406":  { usd_reseller: 1658, caracteristicas: "Balanceadora de ruedas para camión 10 a 24\"" },
    // Desarmadoras
    "1010265": { usd_reseller: 1012, caracteristicas: "Desarmadora rueda moto/auto" },
    "1010267": { usd_reseller: 2763, caracteristicas: "Desarmadora de neumáticos pro c/brazo p/run flat" },
    // Accesorios / equipamiento (IVA 21%)
    "1010034": { usd_reseller: 421,  iva: 21, caracteristicas: "Elevador (lift) para balanceadora" },
    "P-4451":  { usd_reseller: 421,  iva: 21, caracteristicas: "Inflador automático para neumáticos" }
  }
};
