/* Lista de precios REVENDEDORES 2025 — Trivium Pro
   Confidencial. Solo referenciado desde la página secreta de esta carpeta.
   price_ars = "Precio de Reventa $ sin IVA" (columna L de la lista 2025).
   caracteristicas = descripción comercial corta tomada de la lista.
   price_ars = null  → se muestra "A consultar".
   Clave = SKU tal como figura en data/catalog.json.
*/
window.RESELLER_PRICES = {
  meta: {
    list_label: "Lista de precios 2025",
    audience: "Revendedores",
    currency_note: "Precios en pesos (ARS), sin IVA",
    usd_rate: 1510,
    updated: "2025"
  },
  items: {
    // Elevadores 2 columnas
    "1010124": { price_ars: 2475872,  caracteristicas: "Elevador 2 columnas 4000 kg — travesaño al piso" },
    "1010144": { price_ars: 2567000,  caracteristicas: "Elevador 2 columnas 4000 kg — travesaño arriba" },
    "1010271": { price_ars: 6411083,  caracteristicas: "Elevador 2 columnas 5000 kg — travesaño arriba alto" },
    "1010289": { price_ars: 6654948,  caracteristicas: "Elevador 2 columnas 6000 kg — travesaño arriba" },
    // Elevadores 4 columnas
    "1010261": { price_ars: 9112850,  caracteristicas: "Elevador 4 columnas 5T — kit de alineación + Rolling Jack" },
    // Elevadores tijera
    "1010143": { price_ars: 2952050,  caracteristicas: "Elevador tijera móvil" },
    "1010127": { price_ars: 5262350,  caracteristicas: "Elevador tijera corto para embutir 3500 kg" },
    "1010263": { price_ars: 6545850,  caracteristicas: "Elevador tijera corto sobre piso 3000 kg — bajo perfil" },
    "1010282": { price_ars: 11025265, caracteristicas: "Elevador tijera largo — kit de alineación" },
    "1010281": { price_ars: 3657975,  caracteristicas: "Elevador p/gomería 4.5T — piso" },
    // Elevador batería EV
    "1010290": { price_ars: 3587383,  caracteristicas: "Elevador p/batería EV 1T" },
    // Balanceadoras
    "1010272": { price_ars: 3337100,  caracteristicas: "Balanceadora de ruedas con monitor" },
    "1010122": { price_ars: 1105094,  caracteristicas: "Balanceadora para ruedas de auto" },
    "P-5406":  { price_ars: 2502825,  caracteristicas: "Balanceadora de ruedas para camión 10 a 24\"" },
    "1010034": { price_ars: 635333,   caracteristicas: "Elevador (lift) para balanceadora" },
    // Desarmadoras
    "1010265": { price_ars: 1527365,  caracteristicas: "Desarmadora rueda moto/auto" },
    "1010267": { price_ars: 4171375,  caracteristicas: "Desarmadora de neumáticos pro c/brazo p/run flat" },
    // Infladores
    "P-4451":  { price_ars: 635333,   caracteristicas: "Inflador automático para neumáticos" },
    // Sin precio en la lista 2025
    "1010223": { price_ars: null,     caracteristicas: "Elevador para moto 454 kg" },
    "1010292": { price_ars: null,     caracteristicas: "Balanceadora de ruedas U-659 con monitor" }
  }
};
