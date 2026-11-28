# -*- coding: utf-8 -*-
"""Páginas legales y de política comercial (requisitos de Google Merchant Center y de la Ley de
Defensa del Consumidor). Texto base: revisar con el asesor legal de Trivium Center S.A. antes de
darlo por definitivo. Los datos de la empresa salen de acá, en un solo lugar."""

EMPRESA = "Trivium Center S.A."
DOMICILIO = "Av. Donato Álvarez 7971, Córdoba, Argentina"
MAIL = "info@trivium.ar"
WA = "+54 9 11 2701-5294"
WA2 = "+54 9 351 399-4200"
DEFENSA = "https://www.argentina.gob.ar/produccion/defensadelconsumidor/formulario"
AAIP = "https://www.argentina.gob.ar/aaip"

ACTUALIZADO = "22 de octubre de 2026"

PAGINAS = [
 dict(slug='terminos-y-condiciones', h1='Términos y condiciones', crumb='Términos y condiciones',
  title='Términos y condiciones de compra', description='Términos y condiciones de compra de Trivium Pro: precios, pagos con Mercado Pago, entrega, garantía y defensa del consumidor.',
  html=f'''
<p class="muted">Última actualización: {ACTUALIZADO}</p>
<p>Estos términos regulan las compras realizadas en <strong>pro.trivium.ar</strong>, sitio de <strong>{EMPRESA}</strong> (Trivium Pro), con domicilio en {DOMICILIO}. Al comprar aceptás estas condiciones. La relación de consumo se rige por la Ley 24.240 de Defensa del Consumidor y sus normas complementarias.</p>

<h2>1. Quiénes somos</h2>
<p>{EMPRESA} es importadora y distribuidora de equipamiento para talleres mecánicos y gomerías, y fabricante de la línea Trivium Pro. Contacto: <a href="mailto:{MAIL}">{MAIL}</a>, WhatsApp {WA} y {WA2} (Ventas).</p>

<h2>2. Productos y precios</h2>
<ul>
<li>Los precios se expresan en <strong>pesos argentinos (ARS)</strong>, con <strong>IVA incluido</strong> (la alícuota figura en cada ficha).</li>
<li>Se calculan a partir de un valor en dólares y la <strong>cotización del dólar del día</strong>, por eso pueden actualizarse. El precio que rige es el que ves al momento de confirmar la compra.</li>
<li>El precio <strong>no incluye la instalación</strong> ni el flete, que se cotizan aparte según el equipo y el destino.</li>
<li>Las fotos y descripciones son ilustrativas; las especificaciones de cada ficha técnica prevalecen sobre cualquier imagen.</li>
<li>La disponibilidad se confirma al procesar el pedido. Si un producto no estuviera disponible, te avisaremos y podrás elegir otro equipo o la devolución de lo abonado.</li>
</ul>

<h2>3. Formas de pago</h2>
<p>El pago se realiza a través de <strong>Mercado Pago</strong>, con los medios de pago habilitados en su plataforma. {EMPRESA} no recibe ni almacena los datos de tu tarjeta. Mercado Pago procesa el pago bajo sus propios términos y política de privacidad.</p>

<h2>4. Facturación</h2>
<p>Emitimos factura electrónica por cada compra, a nombre del titular que indiques al comprar.</p>

<h2>5. Entrega e instalación</h2>
<p>Las condiciones de envío están en <a href="../envios-y-entregas/">Envíos y entregas</a>. La instalación y puesta en marcha las realiza nuestro equipo de técnicos y se cotizan por separado.</p>

<h2>6. Garantía</h2>
<p>Los equipos nuevos cuentan con <strong>garantía oficial</strong> y servicio técnico en todo el país, sin perjuicio de la garantía legal que establece la Ley 24.240 (art. 11 y siguientes). Para hacerla valer, escribinos por WhatsApp o a {MAIL} con el modelo y número de serie.</p>

<h2>7. Cambios, devoluciones y arrepentimiento</h2>
<p>Podés revocar tu compra dentro de los <strong>10 días corridos</strong> desde que recibís el producto. El detalle y el formulario están en <a href="../cambios-devoluciones-y-arrepentimiento/">Cambios, devoluciones y botón de arrepentimiento</a>.</p>

<h2>8. Datos personales</h2>
<p>El tratamiento de tus datos se describe en la <a href="../politica-de-privacidad/">Política de privacidad</a>.</p>

<h2>9. Defensa del consumidor y jurisdicción</h2>
<p>Ante cualquier inconveniente podés contactarnos primero y, si no se resuelve, presentar un reclamo en la <a href="{DEFENSA}" target="_blank" rel="noopener">Dirección Nacional de Defensa del Consumidor</a>. Para cualquier controversia será competente la justicia ordinaria del domicilio real del consumidor (art. 36, Ley 24.240).</p>
'''),
 dict(slug='cambios-devoluciones-y-arrepentimiento', h1='Cambios, devoluciones y botón de arrepentimiento', crumb='Cambios y devoluciones',
  title='Cambios, devoluciones y botón de arrepentimiento', description='Cómo cambiar, devolver o revocar una compra en Trivium Pro: 10 días corridos, botón de arrepentimiento y garantía.',
  html=f'''
<p class="muted">Última actualización: {ACTUALIZADO}</p>

<h2 id="arrepentimiento">Botón de arrepentimiento</h2>
<p>Si compraste a distancia (por este sitio, por WhatsApp o por teléfono), tenés derecho a <strong>revocar la compra dentro de los 10 días corridos</strong> contados desde que recibís el producto o desde la celebración del contrato, lo que ocurra último (art. 34, Ley 24.240 y Res. 424/2020). No hace falta que expliques el motivo.</p>
<p><a class="btn btn--primary" href="mailto:{MAIL}?subject=Bot%C3%B3n%20de%20arrepentimiento&body=Nombre%20y%20apellido%3A%0ADNI%3A%0AN%C3%BAmero%20de%20pedido%20o%20factura%3A%0AProducto%3A%0AFecha%20de%20recepci%C3%B3n%3A">Botón de arrepentimiento: enviar solicitud</a>
 <a class="btn" href="https://wa.me/5491127015294?text=Quiero%20revocar%20mi%20compra%20(bot%C3%B3n%20de%20arrepentimiento)" target="_blank" rel="noopener">Hacerlo por WhatsApp</a></p>
<p>Al enviar la solicitud indicanos tu nombre, DNI, número de pedido o factura, el producto y la fecha de recepción. Te confirmaremos la recepción por el mismo medio y coordinaremos la devolución.</p>

<h2>Cómo es la devolución</h2>
<ul>
<li>El producto debe devolverse <strong>sin uso</strong> y en su embalaje original, con sus accesorios y documentación.</li>
<li>Los <strong>gastos de devolución</strong> corren por cuenta del proveedor (art. 34, Ley 24.240).</li>
<li>Te reintegramos el importe abonado por el mismo medio de pago, dentro de los plazos de Mercado Pago, una vez recibido y revisado el equipo.</li>
<li>Si el equipo ya fue <strong>instalado</strong> por nuestro equipo, la revocación se coordina con soporte técnico para su desinstalación.</li>
</ul>

<h2>Cambios y productos con defectos</h2>
<ul>
<li>Si recibís un equipo dañado o distinto del pedido, <strong>avisanos dentro de las 48 horas</strong> con fotos del producto y del embalaje. Ayuda a que lo resolvamos rápido que hayas dejado constancia al recibirlo con el transportista.</li>
<li>Los equipos con <strong>fallas de fabricación</strong> están cubiertos por la garantía oficial y la garantía legal (Ley 24.240): reparación, cambio o devolución según corresponda.</li>
</ul>

<h2>Contacto</h2>
<p>{MAIL} · WhatsApp {WA} · WhatsApp ventas {WA2}. Atendemos de lunes a viernes de 9 a 18 h.</p>
<p>Si no resolvemos tu consulta, podés presentar un reclamo en la <a href="{DEFENSA}" target="_blank" rel="noopener">Dirección Nacional de Defensa del Consumidor</a>.</p>
'''),
 dict(slug='envios-y-entregas', h1='Envíos y entregas', crumb='Envíos y entregas',
  title='Envíos y entregas', description='Envíos de equipamiento para taller a todo el país: costo y plazo según destino, retiro en Buenos Aires y recepción del equipo. Instalación aparte.',
  html=f'''
<p class="muted">Última actualización: {ACTUALIZADO}</p>
<h2>Cobertura</h2>
<p>Enviamos a <strong>todo el país</strong>. Los equipos de taller son voluminosos y pesados, por eso el envío se <strong>cotiza según el equipo y el destino</strong>: pedinos la cotización por WhatsApp ({WA}) o por mail ({MAIL}) indicando el modelo y tu localidad.</p>
<h2>Retiro</h2>
<p>También podés retirar tu equipo en nuestro depósito de Buenos Aires (Centro Logístico Trivium Center). Coordinamos día y horario antes de que te acerques; te pedimos que lleves el comprobante de compra y tu DNI.</p>
<h2>Plazos</h2>
<p>El plazo depende de la disponibilidad del equipo y del destino. Te lo confirmamos al aceptar el pedido. Si el equipo no está en stock, te informamos la fecha estimada de entrega antes de que lo pagues.</p>
<h2>Recepción del equipo</h2>
<ul>
<li>Revisá el embalaje <strong>al recibirlo</strong>, en presencia del transportista, y dejá constancia de cualquier daño en el remito.</li>
<li>Si detectás un problema, avisanos dentro de las 48 horas con fotos (ver <a href="../cambios-devoluciones-y-arrepentimiento/">cambios y devoluciones</a>).</li>
<li>Para descargar los equipos conviene contar con personal y, en algunos casos, un autoelevador o una grúa: consultanos.</li>
</ul>
<h2>Instalación</h2>
<p>La colocación y puesta en marcha las realiza nuestro equipo de técnicos en todo el país y <strong>se cotiza aparte</strong> del precio del equipo y del flete. Ver <a href="../instalacion-posventa-y-servicios/">Instalación y posventa</a> y <a href="../zonas/">cobertura por zona</a>.</p>
'''),
 dict(slug='politica-de-privacidad', h1='Política de privacidad', crumb='Política de privacidad',
  title='Política de privacidad', description='Cómo Trivium Pro trata tus datos personales: qué datos recolectamos, para qué los usamos, con quién los compartimos y cómo ejercer tus derechos.',
  html=f'''
<p class="muted">Última actualización: {ACTUALIZADO}</p>
<p>{EMPRESA} (Trivium Pro), con domicilio en {DOMICILIO}, es responsable del tratamiento de los datos personales que recolecta en <strong>pro.trivium.ar</strong>, de acuerdo con la Ley 25.326 de Protección de los Datos Personales.</p>
<h2>Qué datos recolectamos</h2>
<ul>
<li><strong>Formularios y contacto:</strong> nombre, teléfono, correo, localidad y el mensaje que nos enviás al pedir una cotización o consultar por WhatsApp o mail.</li>
<li><strong>Compras:</strong> datos de facturación y entrega. El pago lo procesa <strong>Mercado Pago</strong>; nosotros no recibimos ni guardamos los datos de tu tarjeta.</li>
<li><strong>Uso del sitio:</strong> el sitio guarda en tu dispositivo (almacenamiento local) el contenido de tu carrito. No usamos cookies publicitarias propias.</li>
</ul>
<h2>Para qué los usamos</h2>
<p>Para responder tus consultas, cotizar, procesar y entregar tus compras, emitir facturas, brindar garantía y servicio técnico, y cumplir obligaciones legales. No vendemos tus datos.</p>
<h2>Con quién los compartimos</h2>
<p>Con proveedores que intervienen en el servicio: Mercado Pago (pagos), empresas de transporte (entrega) y nuestro equipo técnico (instalación). También cuando una norma o una autoridad lo exija.</p>
<h2>Tus derechos</h2>
<p>Podés pedir el <strong>acceso, la rectificación, la actualización o la supresión</strong> de tus datos escribiendo a <a href="mailto:{MAIL}">{MAIL}</a>. El titular puede ejercer el derecho de acceso en forma gratuita a intervalos no inferiores a seis meses, salvo que acredite un interés legítimo (art. 14, Ley 25.326).</p>
<p>La <a href="{AAIP}" target="_blank" rel="noopener">Agencia de Acceso a la Información Pública</a>, órgano de control de la Ley 25.326, tiene la atribución de atender las denuncias y reclamos que se interpongan por incumplimiento de las normas sobre protección de datos personales.</p>
<h2>Conservación y seguridad</h2>
<p>Conservamos los datos mientras dure la relación comercial y los plazos que exige la ley. Aplicamos medidas razonables de seguridad técnica y organizativa.</p>
<h2>Cambios en esta política</h2>
<p>Podemos actualizarla; la fecha de arriba indica la última versión.</p>
'''),
]
