# Publicar Trivium Pro en Google Merchant Center

Estado al 2026-10-22. Lo que ya está hecho en el sitio y lo que falta del lado de la cuenta.

## Ya resuelto en el sitio
- Feed de productos: `https://pro.trivium.ar/feeds/google-merchant.tsv` (16 equipos Trivium Pro con precio público; se regenera a diario a las 05:00 ART con el dólar del día, junto con las páginas, para que feed y ficha coincidan).
- Atributos: id, title, description (rica, hasta 1.500 caracteres), link, image_link (+ adicionales), availability, price (ARS con IVA), condition, brand, mpn, identifier_exists=no, product_type, google_product_category, custom_label_0/1, product_highlight[0..3], canonical_link.
- Páginas que Google exige: Términos y condiciones, Política de privacidad, Cambios/devoluciones + botón de arrepentimiento, Envíos y entregas, contacto con mail/WhatsApp/domicilio. Enlazadas en el pie de todo el sitio.
- Datos estructurados: Product + Offer (precio, IVA incluido, disponibilidad) + política de devoluciones (10 días) + certificaciones.

## Falta (cuenta / negocio)
1. **Checkout online**: cargar el secret del Worker `npx wrangler secret put MP_ACCESS_TOKEN` (Access Token de producción de Mercado Pago). Sin eso `/api/tienda/checkout` responde "no configurado" y la compra cae a WhatsApp; Google puede observar productos sin compra posible.
2. **Cuenta**: crear/entrar en Merchant Center, país Argentina, moneda ARS, idioma español.
3. **Dominio**: verificar y reclamar `pro.trivium.ar` (Search Console ya está dado de alta; sirve la misma verificación).
4. **Datos del negocio**: nombre, domicilio (Av. Donato Álvarez 7971, Córdoba), teléfono/mail, CUIT si lo piden.
5. **Envíos** (Configuración → Envío): definir tarifas/plazos. El sitio dice que el envío se cotiza según equipo y destino; en Merchant hay que elegir una regla (por ejemplo costo fijo de referencia o "sin cargo" con aclaración) que coincida con lo que se cobra.
6. **Devoluciones** (Configuración → Devoluciones): 10 días corridos, gastos de devolución a cargo del proveedor (igual que la página publicada).
7. **Feed**: Productos → Feeds → Archivo programado, URL del feed, descarga diaria (después de las 05:30 ART).
8. **Revisar diagnósticos**: precio no coincide (verificar el dólar), imagen, disponibilidad. `availability` va en `in_stock` para todos: confirmar que es cierto.
9. Revisar con el asesor legal el texto de los términos, la privacidad y las devoluciones; agregar CUIT y razón social completa si corresponde.

## Después
- Activar "Fichas gratuitas" (Surfaces across Google) y, si se quiere, campañas de Shopping/Performance Max.
- Cargar reseñas/valoraciones más adelante (suman en Shopping).
