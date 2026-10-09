"""Contenido de las páginas pilar /guias/<slug>/.

Cada guía es una página de compra para una búsqueda concreta ("balanceadora de
ruedas para gomería", "alineadora 3D"). Los datos de los equipos (nombre,
marca, capacidad, link) salen de data/catalog.json por slug: si cambia el
catálogo, la tabla comparativa se regenera sola. Acá sólo van el texto y la
nota de uso de cada equipo, que se sacó de la ficha técnica del propio producto.

No se publican precios: están pausados en el sitio y cambian con el dólar.
Las cifras técnicas vienen de las fichas y de notas del blog.
"""

UPDATED = "2026-10-09"

GUIAS = [
# --------------------------------------------------------------------------
{
 "slug": "balanceadoras-de-ruedas",
 "title": "Cómo elegir una balanceadora de ruedas para gomería y taller",
 "h1": "Balanceadora de ruedas: guía de compra",
 "description": ("Cómo elegir una balanceadora de ruedas para gomería o taller: con o sin "
                 "monitor, capacidad de rueda, autos o camiones, y comparativa de modelos "
                 "Hofmann y Trivium Pro."),
 "category": "balanceadoras",
 "intro": """
<div class="respuesta">
<p><strong>En resumen:</strong> para una gomería o taller que atiende autos y camionetas, buscá una balanceadora con capacidad de rueda de 65 a 70 kg, ingreso automático de las medidas de la llanta y freno de posicionamiento. Si el volumen de trabajo es alto o hay llantas de aleación, sumá puntero láser y modo de peso dividido y oculto. Para camiones, la capacidad mínima razonable es de 150 kg.</p>
<p>Trivium Pro tiene dos gamas: <strong>Hofmann Geodyna</strong> (premium, tecnología Snap-on) y la línea económica propia <strong>Trivium Pro / Unite</strong>.</p>
</div>
""",
 "secciones": """
<h2>Qué hace una balanceadora y por qué importa</h2>
<p>Una balanceadora mide el desequilibrio de masa de la rueda ya montada (llanta más neumático) y le indica al operario dónde y cuánto contrapeso colocar. Una rueda mal balanceada vibra en el volante, desgasta el neumático de forma despareja y castiga la suspensión. Por eso el balanceo es uno de los servicios más repetidos de cualquier gomería, y la máquina que más se usa en el día.</p>

<h2>Con monitor o sin monitor</h2>
<p>La decisión de fondo es cuánta automatización necesitás:</p>
<ul>
<li><strong>Sin monitor:</strong> más económicas. Hay que cargar a mano la distancia, el diámetro y el ancho de la rueda, y el resultado depende más de la experiencia del operario. Sirven para volumen bajo o balanceo ocasional.</li>
<li><strong>Con monitor:</strong> incorporan animación 3D, ingreso automático de las medidas, freno automático, puntero láser o iluminación LED que marca la posición del contrapeso. Reducen errores y tiempos de espera, y en talleres con mucho flujo la diferencia de tiempo se nota todos los días.</li>
</ul>
<p>Más detalle en la nota <a href="../../blog/balanceadoras-de-ruedas-con-o-sin-monitor-cual-elegir/">Balanceadoras con o sin monitor: ¿cuál elegir?</a>.</p>

<h2>Cinco criterios para elegir</h2>
<ol>
<li><strong>Tipo de vehículo.</strong> Autos y camionetas: capacidad de 65 a 70 kg por rueda. Camiones y pesados: 150 kg (U-850) o 250 kg (Geodyna 980L). Verificá siempre el peso máximo de rueda en la ficha.</li>
<li><strong>Volumen de trabajo.</strong> A más ruedas por día, más valen los ciclos cortos (el Geodyna 7600P tiene un ciclo de equilibrado de 4,5 segundos) y la medición automática.</li>
<li><strong>Tipo de llanta.</strong> Con llantas de aleación conviene el modo de <em>peso dividido y oculto</em>, que coloca los contrapesos detrás de los rayos para que no se vean desde afuera.</li>
<li><strong>Autocalibración y precisión.</strong> Una máquina que se autocalibra mantiene la precisión sin depender de un técnico. Leé <a href="../../blog/autocalibracion-en-una-balanceadora-de-ruedas-que-es-y-por-que-es-importante/">qué es la autocalibración y por qué importa</a>.</li>
<li><strong>Servicio técnico y repuestos.</strong> Una balanceadora parada es plata perdida. Trivium Pro hace la instalación, la capacitación y el servicio técnico en todo el país.</li>
</ol>

<h2>Comparativa de modelos</h2>
<p>La capacidad corresponde al peso máximo de rueda indicado en cada ficha técnica.</p>
{{TABLA}}

<h2>Premium Hofmann o línea económica Trivium Pro</h2>
<p>Las <strong>Geodyna de Hofmann</strong> (marca de Snap-on) son el estándar de concesionarias y de talleres de alto volumen: sistemas de medición propios (QuickBAL, Smart Sonar, Power Clamp), pantallas táctiles y, en el tope de gama, diagnóstico 3D sin contacto. La línea <strong>Trivium Pro / Unite</strong> está pensada para gomerías y talleres que quieren una máquina con monitor, autocalibración y puntero láser a una inversión más ajustada. Si dudás, contanos cuántas ruedas balanceás por día y te recomendamos la que se paga más rápido.</p>

<h2>Errores comunes al usar una balanceadora</h2>
<p>La mayoría de los problemas de balanceo vienen de la carga de datos y del montaje de la rueda, no de la máquina. Tenés los casos más frecuentes en <a href="../../blog/errores-comunes-al-usar-una-balanceadora-y-como-evitarlos/">Errores comunes al usar una balanceadora y cómo evitarlos</a>.</p>
""",
 "tabla": {
  "slugs": [
   ("balanceadora-de-ruedas-unite-u-659", "Con freno electromagnético, puntero láser y peso dividido y oculto."),
   ("balanceadora-de-ruedas-unite-g66", "Autocalibración, pantalla LED de 17\", ingreso automático de datos y puntero láser."),
   ("balanceadora-de-ruedas-unite-s-901", "Autocalibración y diagnóstico; cabina con bandeja de herramientas."),
   ("balanceadora-de-ruedas-hofmann-geodyna-7100-pantalla-led", "QuickBAL para ciclos cortos, modo de división de pesos, bloqueo por pedal."),
   ("balanceadora-de-ruedas-hofmann-geodyna-7400l", "easyALU para llantas de aleación y modo de peso dividido."),
   ("balanceadora-de-ruedas-hofmann-geodyna-7200vci", "Monitor TFT de 19\", Smart Sonar y sistema VPM."),
   ("balanceadora-de-ruedas-hofmann-geodyna-7800-2p", "Premium para concesionarias y centros de servicio, hasta 200 rpm de medición."),
   ("balanceadora-de-ruedas-hofmann-geodyna-7600p", "Pantalla táctil, Power Clamp y ciclo de 4,5 segundos; hasta 130 kg."),
   ("balanceadora-de-ruedas-hofmann-geodyna-9000p", "Diagnóstico 3D sin contacto con cámaras láser y pantalla táctil."),
   ("balanceadora-de-ruedas-para-camion-u-850-150-kg-trivium-pro", "Camiones: 150 kg con plataforma neumática elevadora."),
   ("balanceadora-para-ruedas-de-camion-hofmann-geodyna-980l", "Camiones y pesados: hasta 250 kg, con tecnología VPM."),
  ],
 },
 "faqs": [
  ("¿Qué balanceadora necesito para una gomería que atiende autos y camionetas?",
   "Una balanceadora con capacidad de 65 a 70 kg por rueda, ingreso automático de las medidas de la llanta, freno de posicionamiento y, si tu volumen es alto, puntero láser. Los modelos Unite G66 y U-659 de Trivium Pro y las Hofmann Geodyna 7100 a 7800 cubren ese rango."),
  ("¿Conviene una balanceadora con monitor o sin monitor?",
   "Si balanceás pocas ruedas por día y el presupuesto es limitado, una sin monitor alcanza. Si el taller tiene flujo constante, la de monitor reduce errores y tiempos porque carga las medidas automáticamente y marca la posición del contrapeso."),
  ("¿Qué balanceadora sirve para ruedas de camión?",
   "Necesitás una de mayor capacidad: la U-850 de Trivium Pro soporta 150 kg con plataforma neumática elevadora, y la Hofmann Geodyna 980L llega a 250 kg."),
  ("¿Qué es el peso dividido y oculto?",
   "Es un modo de balanceo para llantas de aleación: la máquina reparte el contrapeso en dos y lo ubica detrás de los rayos, de modo que no se ve desde el exterior de la rueda."),
  ("¿Qué diferencia hay entre una Hofmann Geodyna y una Trivium Pro?",
   "La Geodyna es la línea premium de Hofmann (Snap-on), con sistemas de medición propios y modelos de tope de gama. Trivium Pro es la línea económica propia, con monitor, autocalibración y puntero láser en los modelos principales."),
  ("¿Instalan y dan servicio técnico en todo el país?",
   "Sí. Trivium Pro hace la instalación, la puesta en marcha, la capacitación y el servicio técnico en todo el país. Escribinos por WhatsApp con tu provincia y te confirmamos tiempos."),
 ],
 "posts": [
  "balanceadoras-de-ruedas-con-o-sin-monitor-cual-elegir",
  "autocalibracion-en-una-balanceadora-de-ruedas-que-es-y-por-que-es-importante",
  "errores-comunes-al-usar-una-balanceadora-y-como-evitarlos",
  "la-importancia-de-balancear-ruedas-beneficios-clave-para-talleres-y-gomerias",
  "por-que-incorporar-una-balanceadora-de-ruedas-en-tu-gomeria-es-una-decision-inteligente",
 ],
},
# --------------------------------------------------------------------------
{
 "slug": "alineadoras-3d",
 "title": "Cómo elegir una alineadora 3D para tu taller",
 "h1": "Alineadora 3D: guía de compra",
 "description": ("Guía para elegir una alineadora 3D en Argentina: 2D vs 3D, elevador necesario, "
                 "espacio, autos y camiones, y comparativa de las Hofmann Geoliner y la Josam "
                 "CV-Aligner."),
 "category": "alineadoras",
 "intro": """
<div class="respuesta">
<p><strong>En resumen:</strong> una alineadora 3D mide los ángulos de la rueda con cámaras, sin cables hasta las ruedas, y es más rápida y precisa que una 2D. Para un taller de autos y camionetas, la línea Hofmann Geoliner (320, 609, 630 y 770) cubre desde equipos compactos sin consola hasta móviles de alta productividad. Para colectivos y camiones existe la Josam CV-Aligner. Antes de comprar, definí el elevador: la alineación se hace sobre un elevador de cuatro columnas, uno tijera largo o una fosa.</p>
</div>
""",
 "secciones": """
<h2>Qué mide una alineadora</h2>
<p>La alineación ajusta la geometría de las ruedas respecto del vehículo. Los parámetros principales son la <strong>convergencia</strong>, la <strong>caída</strong> y el <strong>avance (caster)</strong>, más ángulos complementarios como el KPI y el giro máximo. Una geometría fuera de tolerancia desgasta los neumáticos de forma despareja, hace que el auto "tire" hacia un lado y aumenta el consumo. Para entender el proceso paso a paso: <a href="../../blog/como-se-alinea-un-vehiculo-con-una-alineadora-3d/">cómo se alinea un vehículo con una alineadora 3D</a>.</p>

<h2>2D o 3D</h2>
<ul>
<li><strong>2D (convencional):</strong> menor inversión inicial y operación simple, pero lleva más tiempo, tiene precisión más limitada y necesita más espacio.</li>
<li><strong>3D:</strong> alta precisión, mediciones en tiempo real, mejor aprovechamiento del espacio y flujo de trabajo más rápido. Requiere una capacitación inicial, que Trivium Pro brinda al instalar el equipo.</li>
</ul>
<p>Sobre el "5D": las dimensiones extra son una cuestión de marketing, no de tecnología de medición. Lo explicamos en <a href="../../blog/alineadoras-5d-el-mito-de-las-dimensiones-en-equipos-de-alineacion/">Alineadoras 5D: el mito de las dimensiones</a>.</p>

<h2>El elevador también cuenta</h2>
<p>La alineadora no funciona sola: necesita una superficie nivelada donde las ruedas puedan moverse. Las opciones habituales son:</p>
<ul>
<li><strong>Elevador de cuatro columnas:</strong> el más usado para alinear por estabilidad y capacidad. Las ruedas descansan sobre plataformas.</li>
<li><strong>Elevador tijera para alineación:</strong> sin columnas que estorben, ideal para talleres con espacio acotado.</li>
<li><strong>Fosa:</strong> la Geoliner 320 es compatible con fosas y elevadores.</li>
</ul>
<p>Ver <a href="../../guias/elevadores-para-taller/">la guía de elevadores</a> y la nota sobre <a href="../../blog/cuanto-espacio-dejar-entre-la-alineadora-y-el-elevador-recomendaciones-para-una-instalacion-optima/">cuánto espacio dejar entre la alineadora y el elevador</a>.</p>

<h2>Cómo elegir según tu taller</h2>
<ol>
<li><strong>Espacio.</strong> Si el taller es chico, un equipo compacto sin consola (Geoliner 609) o con brazos de cámara plegables (Geoliner 770).</li>
<li><strong>Volumen.</strong> Más alineaciones por día justifican la interfaz inteligente y las actualizaciones automáticas de la Geoliner 630.</li>
<li><strong>Perfil de vehículos.</strong> Autos y SUVs: Geoliner. Colectivos, camiones y pesados: Josam CV-Aligner.</li>
<li><strong>Servicios nuevos.</strong> Si vas a ofrecer calibración de cámaras y sensores de asistencia a la conducción, existe el sistema Hofmann EZ-ADAS.</li>
<li><strong>Soporte.</strong> Verificá que haya técnicos en tu zona, repuestos y capacitación. Trivium Pro los incluye en todo el país.</li>
</ol>

<h2>Comparativa de modelos</h2>
{{TABLA}}

<h2>Hofmann y John Bean</h2>
<p>Hofmann es la marca de alineación de Snap-on y comparte tecnología con John Bean. Si estás comparando ambas, mirá <a href="../../blog/existen-diferencias-reales-entre-hofmann-y-john-bean/">¿Existen diferencias reales entre Hofmann y John Bean?</a>.</p>

<h2>Más ingresos con el mismo taller</h2>
<p>Sumar alineación es una de las formas más directas de aumentar los ingresos de una gomería o taller, porque se vende junto con el balanceo y el cambio de neumáticos. Más argumentos en <a href="../../blog/los-beneficios-de-tener-una-alineadora-en-tu-taller-o-gomeria/">los beneficios de tener una alineadora</a> y en la guía para <a href="../../blog/como-abrir-un-taller-de-alineacion-y-balanceo/">abrir un taller de alineación y balanceo</a>.</p>
""",
 "tabla": {
  "slugs": [
   ("alineadora-hofmann-geoliner-609", "Compacta, sin consola, ideal para poco espacio y fácil de instalar."),
   ("alineadora-3d-hofmann-geoliner-320", "Cámaras 3D, diseño compacto compatible con fosas y elevadores."),
   ("alineadora-3d-hofmann-geoliner-630", "Cámaras de alta velocidad y sistema VODI; actualizaciones en línea."),
   ("alineadora-hofmann-geoliner-770", "Móvil, brazos de cámaras plegables y centro de gravedad bajo."),
   ("alineadora-de-camiones-josam-cv-aligner", "Colectivos y vehículos pesados; comunicación inalámbrica entre unidades."),
   ("sistema-de-calibracion-hofmann-ez-adas", "Calibración de sistemas ADAS guiada por láser."),
  ],
 },
 "faqs": [
  ("¿Qué es una alineadora 3D y en qué se diferencia de una 2D?",
   "Una alineadora 3D usa cámaras que ven unos blancos montados en las ruedas y calcula los ángulos en tiempo real, sin cables hasta cada rueda. Es más rápida, más precisa y ocupa menos espacio que una 2D convencional."),
  ("¿Qué elevador necesito para usar una alineadora?",
   "Lo más habitual es un elevador de cuatro columnas o uno tijera largo para alineación. También se puede trabajar sobre fosa. Trivium Pro ofrece elevadores con kit de alineación incluido."),
  ("¿Cuál es la alineadora ideal para un taller con poco espacio?",
   "La Hofmann Geoliner 609 es compacta y no lleva consola, y la 770 tiene brazos de cámara plegables. Contanos las medidas del taller y te decimos cuál entra."),
  ("¿Hay alineadoras para camiones y colectivos?",
   "Sí. La Josam CV-Aligner alinea vehículos pesados con comunicación inalámbrica entre las unidades de medición. Es la que instalamos, por ejemplo, en Mendoza."),
  ("¿Las alineadoras 5D son mejores que las 3D?",
   "No necesariamente. Las dimensiones adicionales son un recurso de marketing; lo que determina la calidad es la tecnología de medición y el software del equipo."),
  ("¿Dan capacitación y puesta en marcha?",
   "Sí. Trivium Pro instala el equipo, lo pone en marcha y capacita a tus operarios, en todo el país."),
 ],
 "posts": [
  "como-elegir-la-alineadora-de-autos-ideal-para-tu-taller",
  "como-funciona-la-alineacion-3d-de-autos-tecnologia-y-beneficios",
  "como-se-alinea-un-vehiculo-con-una-alineadora-3d",
  "alineadoras-5d-el-mito-de-las-dimensiones-en-equipos-de-alineacion",
  "como-elegir-el-elevador-adecuado-para-hacer-alineacion",
  "existen-diferencias-reales-entre-hofmann-y-john-bean",
 ],
},
# --------------------------------------------------------------------------
{
 "slug": "elevadores-para-taller",
 "title": "Cómo elegir un elevador de autos para taller",
 "h1": "Elevador para taller: guía de compra",
 "description": ("Guía para elegir un elevador de autos: 2 columnas, 4 columnas, tijera o para "
                 "camiones. Capacidad, requisitos del piso y comparativa de Rotary Lift, "
                 "Challenger, Forward Lift, Direct Lift y Trivium Pro."),
 "category": "elevadores",
 "intro": """
<div class="respuesta">
<p><strong>En resumen:</strong> para mecánica general en un taller multimarca, el estándar es un <strong>elevador de dos columnas de 4 a 4,5 toneladas</strong>. Para alinear, conviene uno de <strong>cuatro columnas</strong> o <strong>tijera largo</strong>. Para gomería y cambio de neumáticos alcanza un <strong>tijera bajo</strong>. Para camiones y vehículos pesados, hay modelos de 4 columnas de hasta 13,6 toneladas.</p>
</div>
""",
 "secciones": """
<h2>Los cuatro tipos de elevador</h2>
<h3>Dos columnas</h3>
<p>Dan acceso total a la parte baja del vehículo, ocupan poco espacio y son el caballito de batalla de la mecánica general. Hay dos configuraciones: <strong>piso libre</strong> (sin travesaño, nada en el piso entre las columnas) y <strong>travesaño al piso</strong> (más económica, con un perfil bajo en el piso). Diferencias en <a href="../../blog/diferencias-entre-elevadores-de-2-columnas-de-piso-libre-y-travesano-al-piso/">piso libre vs. travesaño al piso</a>.</p>
<h3>Cuatro columnas</h3>
<p>Más estables y sin puntos de levante específicos: el vehículo sube apoyado en las ruedas. Son los preferidos para alineación, service rápido, camionetas y vehículos pesados.</p>
<h3>Tijera</h3>
<p>Compactos, sin columnas. Los de baja altura son ideales para gomería y cambio de neumáticos, los empotrados quedan a nivel del piso, y los de tijera largo con plataformas están pensados para alineación. Comparativa en <a href="../../blog/elevador-de-4-columnas-vs-elevador-de-tijera-largo-cual-elegir-para-alineacion/">4 columnas vs. tijera largo</a>.</p>
<h3>Pesados y motos</h3>
<p>Para camiones y vehículos comerciales hay elevadores de cuatro columnas de alta capacidad, y para motos, modelos con plataforma y trabas propias.</p>

<h2>Cómo elegir</h2>
<ol>
<li><strong>Capacidad.</strong> Autos y SUVs livianos: 4 toneladas. Camionetas y utilitarios: 5 toneladas o más. Siempre con margen sobre el vehículo más pesado que vayas a levantar.</li>
<li><strong>Tipo de trabajo.</strong> Mecánica general: dos columnas. Alineación: cuatro columnas o tijera largo. Neumáticos: tijera bajo. Aceite y service rápido: ver <a href="../../blog/que-tipo-de-elevador-elegir-para-cambio-de-aceite/">qué elevador elegir para cambio de aceite</a>.</li>
<li><strong>Tipo de vehículos.</strong> Los autos eléctricos pesan más y los exóticos son bajos: hay modelos de 6.000 kg para eléctricos y de perfil bajo con altura mínima de 100 a 110 mm.</li>
<li><strong>Seguridad.</strong> Buscá certificación ALI o CE y sistemas de seguridad redundantes (hidráulico, mecánico y eléctrico).</li>
<li><strong>Alimentación eléctrica.</strong> Verificá si el equipo es monofásico o trifásico: <a href="../../blog/diferencias-entre-maquinas-de-taller-con-motores-monofasicos-y-trifasicos-ventajas-de-cada-uno/">diferencias entre motores monofásicos y trifásicos</a>.</li>
</ol>

<h2>El piso: lo que no se ve en el catálogo</h2>
<p>Un elevador de dos columnas se ancla al piso, y el piso tiene que estar a la altura. Como referencia general (siempre hay que seguir el manual del fabricante y consultar a un ingeniero):</p>
<ul>
<li>Espesor mínimo de hormigón de 250 mm sin hierros, y 300 mm en total para elevadores estándar.</li>
<li>Resistencia a la compresión mínima de 20,7 MPa (210 kg/cm²); se recomienda de 27,6 a 40 MPa.</li>
<li>Curado de al menos 28 días, y superficie nivelada (tolerancia máxima de 5 mm por metro).</li>
</ul>
<p>El detalle completo está en <a href="../../blog/especificaciones-del-piso-para-la-instalacion-de-un-elevador-de-dos-columnas/">especificaciones del piso para un elevador de dos columnas</a>.</p>

<h2>Rotary Lift, Challenger, Forward, Direct Lift o Trivium Pro</h2>
<p>Somos representantes oficiales de <strong>Rotary Lift</strong>, con sus líneas <strong>Forward Lift</strong> y <strong>Direct Lift</strong>, y de <strong>Challenger Lifts</strong> (Snap-on). A la par, <strong>Trivium Pro</strong> es la línea económica propia, con elevadores de dos y cuatro columnas y tijeras para gomería. Si querés saber por qué los talleres eligen Rotary, leé <a href="../../blog/por-que-elegir-un-elevador-con-brazos-all-vehicle-de-rotary-lift/">brazos All Vehicle de Rotary Lift</a>.</p>

<h2>Comparativa de modelos</h2>
<p>Una selección de los modelos más pedidos. El catálogo completo está en <a href="../../categoria/elevadores/">Elevadores</a>.</p>
{{TABLA}}
""",
 "tabla": {
  "slugs": [
   ("elevador-dos-columnas-4535-kg-rotary-lift-spoa10", "El estándar para taller multimarca; sirve para eléctricos y exóticos."),
   ("elevador-dos-columnas-4536-kg-rotary-lift-spoa10trio", "Brazos de tres etapas TRIO y triple sistema de seguridad."),
   ("elevador-dos-columnas-simetrico-4536-kg-challenger-lifts-vle10", "Brazos Versymmetric y certificación ALI."),
   ("elevador-dos-columnas-4082-kg-direct-lift-dl9-by-rotary-lift", "Sin travesaño en el piso y triple sistema de seguridad."),
   ("elevador-dos-columnas-4000-kg-piso-libre-unite-pl-4-0-2a", "Línea económica, piso libre, plataforma mínima de 110 mm."),
   ("elevador-dos-columnas-6000-kg-vehiculos-electricos", "Para vehículos eléctricos y SUV pesadas."),
   ("elevador-dos-columnas-7250-kg-rotary-lift-spo16-cargo", "Trabajo pesado y vehículos comerciales."),
   ("elevador-cuatro-columnas-5000-kg-con-kit-para-alineacion", "Incluye kit de alineación y Rolling Jack."),
   ("elevador-cuatro-columnas-8165-kg-rotary-lift-sm18", "Autos, camiones y vehículos comerciales."),
   ("elevador-cuatro-columnas-13608-kg-rotary-lift-sm30s", "Camiones; certificación ALI Gold."),
   ("elevador-tijera-largo-5500-kg-con-kit-de-alineacion", "Tijera largo de bajo perfil para alineación."),
   ("elevador-tijera-gomeria-4500-kg-pl-45h", "Ultradelgado para gomería, altura mínima de 100 mm, sin obra civil."),
  ],
 },
 "faqs": [
  ("¿Qué elevador de auto conviene para un taller multimarca?",
   "Un elevador de dos columnas de 4 a 4,5 toneladas, como los Rotary Lift SPOA. Si además levantás utilitarios o camionetas pesadas, sumá uno de cuatro columnas o de mayor capacidad."),
  ("¿Elevador de dos columnas o de cuatro columnas?",
   "El de dos columnas ocupa menos espacio y deja libre la parte baja del vehículo, ideal para mecánica. El de cuatro columnas es más estable y es el recomendado para alineación y service rápido."),
  ("¿Qué elevador necesito para una gomería?",
   "Un elevador tijera de baja altura, como el PL-45H de 4.500 kg: altura mínima de 100 mm y no requiere obra civil. Además suele combinarse con una desarmadora y una balanceadora."),
  ("¿Qué piso necesita un elevador de dos columnas?",
   "Como mínimo, hormigón de 250 a 300 mm de espesor y resistencia de 20,7 MPa o más, nivelado y curado. Siempre hay que seguir el manual del fabricante."),
  ("¿Hay elevadores para autos eléctricos?",
   "Sí. Tenemos un elevador de dos columnas de 6.000 kg pensado para vehículos eléctricos y SUV, que pesan más que un auto convencional por las baterías."),
  ("¿Instalan el elevador y hacen la obra civil?",
   "Instalamos y ponemos en marcha el equipo en todo el país. Para la preparación del piso te pasamos las especificaciones del fabricante."),
 ],
 "posts": [
  "como-elegir-el-elevador-adecuado-para-hacer-alineacion",
  "diferencias-entre-elevadores-de-2-columnas-de-piso-libre-y-travesano-al-piso",
  "elevador-de-4-columnas-vs-elevador-de-tijera-largo-cual-elegir-para-alineacion",
  "que-tipo-de-elevador-elegir-para-cambio-de-aceite",
  "especificaciones-del-piso-para-la-instalacion-de-un-elevador-de-dos-columnas",
  "por-que-elegir-un-elevador-con-brazos-all-vehicle-de-rotary-lift",
 ],
},
# --------------------------------------------------------------------------
{
 "slug": "desarmadoras-de-neumaticos",
 "title": "Cómo elegir una desarmadora de neumáticos para gomería",
 "h1": "Desarmadora de neumáticos: guía de compra",
 "description": ("Guía para elegir una desarmadora de neumáticos: brazo auxiliar, run flat, "
                 "autos y camiones, y comparativa de las Hofmann Monty y la línea Trivium Pro."),
 "category": "desarmadoras",
 "intro": """
<div class="respuesta">
<p><strong>En resumen:</strong> si vas a trabajar con neumáticos de perfil bajo o run flat, necesitás una desarmadora con <strong>brazo auxiliar</strong>. Para autos y camionetas, buscá un plato de sujeción de hasta 24" o más; para camiones, una desarmadora específica con capacidad para ruedas de 1.500 kg. Si el volumen es alto, las Hofmann Monty sin palanca reducen el esfuerzo del operario y el riesgo de dañar la llanta.</p>
</div>
""",
 "secciones": """
<h2>Para qué sirve una desarmadora</h2>
<p>Separa el neumático de la llanta y lo vuelve a montar sin dañar ninguno de los dos. Es, junto con la balanceadora, el primer equipo que necesita una gomería. Su calidad se nota en tres cosas: el tiempo por rueda, el cuidado de la llanta (sobre todo en aleación) y el esfuerzo del operario.</p>

<h2>Tipos de desarmadora</h2>
<ul>
<li><strong>Semiautomáticas con brazo auxiliar:</strong> la opción más pedida en gomerías. El brazo auxiliar sostiene el neumático mientras se monta, y es indispensable para perfil bajo y run flat. Ver <a href="../../blog/para-que-sirve-el-brazo-auxiliar-en-una-desarmadora-de-neumaticos/">para qué sirve el brazo auxiliar</a>.</li>
<li><strong>Sin palanca (con cabezal automático):</strong> las Hofmann Monty 8800 y Quadriga usan tecnología sin palanca, con sistema de bloqueo central y elevador de ruedas integrado. Son para talleres de alta productividad.</li>
<li><strong>Para camiones:</strong> mandriles reforzados y capacidad para ruedas de gran peso y llantas de hasta 32".</li>
</ul>

<h2>Neumáticos run flat</h2>
<p>Los run flat tienen flancos reforzados que les permiten rodar sin aire unos 80 km, pero justamente por eso son mucho más rígidos y difíciles de desmontar. Con una desarmadora común se corre el riesgo de dañar el neumático y la llanta. Una desarmadora preparada para run flat tiene destalonador potente, brazo auxiliar con rodillos y mordazas de sujeción precisas. Más en <a href="../../blog/como-funcionan-las-desarmadoras-para-neumaticos-runflat-guia-para-talleres-y-gomerias/">cómo funcionan las desarmadoras para run flat</a>. Las Hofmann Monty 3300 cuentan con certificación WDK para neumáticos UHP y run flat.</p>

<h2>Cómo elegir</h2>
<ol>
<li><strong>Tamaño de llanta.</strong> Verificá el rango de sujeción: 12" a 26" para autos y camionetas, hasta 32" en camiones.</li>
<li><strong>Tipo de neumático.</strong> Perfil bajo y run flat: brazo auxiliar o sistema sin palanca.</li>
<li><strong>Volumen.</strong> A más ruedas por día, más valor tiene una máquina automatizada: se ahorra tiempo en cada rueda.</li>
<li><strong>Electricidad y aire.</strong> Las desarmadoras usan aire comprimido: conviene dimensionar bien el compresor. Ver <a href="../../guias/equipar-una-gomeria/">equipar una gomería</a>.</li>
<li><strong>Mantenimiento.</strong> Una desarmadora bien mantenida dura años: <a href="../../blog/como-mantener-tu-desarmadora-trivium-center-en-optimas-condiciones/">cómo mantenerla en óptimas condiciones</a>.</li>
</ol>

<h2>Comparativa de modelos</h2>
<p>La capacidad corresponde al dato indicado en cada ficha técnica.</p>
{{TABLA}}
""",
 "tabla": {
  "slugs": [
   ("desarmadora-de-ruedas-unite-pl-1200u", "Línea económica; brazo oscilante, plato de hasta 24\"."),
   ("desarmadora-de-ruedas-con-brazo-auxiliar-pl-1256s-trivium-center", "Brazo auxiliar de 360°, columna basculante neumática, llantas de 12\" a 26\"."),
   ("desarmadora-de-neumaticos-hofmann-monty-1270", "Destalonado sin dañar la llanta; diseño robusto."),
   ("desarmadora-de-neumaticos-hofmann-monty-3300-20", "Certificación WDK para UHP y run flat; llantas de hasta 20\"."),
   ("desarmadora-de-neumaticos-hofmann-monty-3300-24", "SmartSpeed, brazo neumático vertical y columna auxiliar EasyMont Pro."),
   ("desarmadora-de-neumaticos-hofmann-monty-8800", "Sin palanca, powerMONT con cámara y elevador de ruedas integrado."),
   ("desarmadora-de-neumaticos-automatica-hofmann-monty-quadriga-1-gp", "Automática con detección láser del contorno de la llanta."),
   ("desarmadora-de-ruedas-para-camion-hofmann-monty-4250p", "Camiones: ruedas de hasta 1.500 kg y llantas de 12\" a 32\"."),
  ],
 },
 "faqs": [
  ("¿Qué desarmadora necesito para neumáticos run flat?",
   "Una con brazo auxiliar o sistema sin palanca, destalonador potente y sujeción precisa. Las Hofmann Monty 3300 tienen certificación WDK para neumáticos UHP y run flat."),
  ("¿Para qué sirve el brazo auxiliar?",
   "Sujeta y guía el neumático durante el montaje y el desmontaje, lo que reduce el esfuerzo del operario y evita daños en neumáticos de perfil bajo y run flat."),
  ("¿Qué desarmadora sirve para camiones?",
   "La Hofmann Monty 4250P está diseñada para ruedas de camión de hasta 1.500 kg y llantas de 12\" a 32\"."),
  ("¿Qué diferencia hay entre una desarmadora Hofmann Monty y una Trivium Pro?",
   "Las Monty son la línea premium de Hofmann, con tecnologías como SmartSpeed y sistemas sin palanca. La línea Trivium Pro es la opción económica, con brazo auxiliar y capacidad para llantas de hasta 24\" a 26\"."),
  ("¿Qué más necesito para empezar una gomería?",
   "Además de la desarmadora, una balanceadora, compresor, herramientas neumáticas y un elevador o gato. Lo detallamos en nuestra guía para equipar una gomería."),
  ("¿Hacen instalación y capacitación?",
   "Sí, en todo el país. También ofrecemos mantenimiento preventivo y repuestos."),
 ],
 "posts": [
  "para-que-sirve-el-brazo-auxiliar-en-una-desarmadora-de-neumaticos",
  "como-funcionan-las-desarmadoras-para-neumaticos-runflat-guia-para-talleres-y-gomerias",
  "como-mantener-tu-desarmadora-trivium-center-en-optimas-condiciones",
  "equipamiento-esencial-para-comenzar-tu-taller-de-neumaticos",
 ],
},
# --------------------------------------------------------------------------
{
 "slug": "equipar-una-gomeria",
 "title": "Cómo equipar una gomería: máquinas y herramientas",
 "h1": "Equipar una gomería: qué comprar y en qué orden",
 "description": ("Qué máquinas necesita una gomería: desarmadora, balanceadora, compresor, "
                 "herramientas neumáticas, elevador y alineadora. Orden de compra y guía "
                 "para armar el taller."),
 "category": "desarmadoras",
 "intro": """
<div class="respuesta">
<p><strong>En resumen:</strong> el equipamiento mínimo de una gomería es una <strong>desarmadora de neumáticos</strong>, una <strong>balanceadora de ruedas</strong>, un <strong>compresor</strong> con instalación de aire, <strong>herramientas neumáticas</strong> y algo para levantar el vehículo (gato hidráulico o elevador tijera). La <strong>alineadora</strong> es el paso siguiente: es lo que más amplía los ingresos del taller una vez que el negocio arrancó.</p>
</div>
""",
 "secciones": """
<h2>Orden de compra recomendado</h2>
<ol>
<li><strong>Desarmadora de neumáticos.</strong> Sin ella no hay servicio. Elegila según el tipo de neumático que vas a atender (autos, camionetas, perfil bajo, run flat). Ver <a href="../../guias/desarmadoras-de-neumaticos/">la guía de desarmadoras</a>.</li>
<li><strong>Balanceadora de ruedas.</strong> Se vende en cada cambio de neumático. Ver <a href="../../guias/balanceadoras-de-ruedas/">la guía de balanceadoras</a>.</li>
<li><strong>Compresor y red de aire.</strong> Alimenta la desarmadora y las herramientas neumáticas. Para una instalación fija, tenemos <a href="../../categoria/aire-comprimido/">redes de aire comprimido Prevost de aluminio</a>.</li>
<li><strong>Herramientas neumáticas.</strong> Llaves de impacto, infladores y accesorios: <a href="../../categoria/herramientas-neumaticas/">ver herramientas neumáticas</a>.</li>
<li><strong>Elevador tijera o gato.</strong> Para levantar el vehículo y acceder a las ruedas. En gomería, el tijera de baja altura es el más práctico. Ver <a href="../../guias/elevadores-para-taller/">la guía de elevadores</a>.</li>
<li><strong>Alineadora.</strong> Cuando el flujo de clientes esté estable, sumá alineación. Ver <a href="../../guias/alineadoras-3d/">la guía de alineadoras</a>.</li>
</ol>

<h2>Muebles y organización</h2>
<p>Un taller ordenado trabaja más rápido. Carros, bancos y organizadores están en <a href="../../categoria/muebles-taller/">Muebles de taller</a> y el resto del equipamiento en <a href="../../categoria/equipamiento-taller/">Equipamiento de taller</a>.</p>

<h2>Equipos de referencia por etapa</h2>
{{TABLA}}

<h2>Antes de comprar, tres cosas a medir</h2>
<ul>
<li><strong>Electricidad.</strong> Verificá si necesitás conexión monofásica o trifásica según los equipos: <a href="../../blog/diferencias-entre-maquinas-de-taller-con-motores-monofasicos-y-trifasicos-ventajas-de-cada-uno/">monofásico vs trifásico</a>.</li>
<li><strong>Aire comprimido.</strong> Calculá el consumo simultáneo de la desarmadora y las herramientas.</li>
<li><strong>Espacio.</strong> Dejá circulación libre alrededor de cada equipo; una desarmadora y una balanceadora mal ubicadas hacen perder minutos por rueda.</li>
</ul>

<h2>Guías para emprender</h2>
<p>Si estás en la etapa de proyecto, estas notas complementan la guía: <a href="../../blog/como-instalar-una-gomeria-guia-completa-para-emprender-con-exito/">cómo instalar una gomería</a>, <a href="../../blog/equipamiento-esencial-para-comenzar-tu-taller-de-neumaticos/">equipamiento esencial para comenzar</a> y <a href="../../blog/la-importancia-de-ofrecer-rotacion-de-neumaticos-en-un-taller-o-gomeria/">la importancia de ofrecer rotación de neumáticos</a>.</p>

<div class="cta">
<p><strong>¿Querés que armemos la cotización completa?</strong> Contanos qué tipo de vehículos vas a atender y cuánto espacio tenés, y te armamos una propuesta con todos los equipos, la instalación y la capacitación.</p>
<a class="btn btn--primary" href="https://wa.me/5491127015294?text=Hola%2C%20quiero%20equipar%20una%20gomer%C3%ADa.">Pedir cotización por WhatsApp</a>
</div>
""",
 "tabla": {
  "slugs": [
   ("desarmadora-de-ruedas-con-brazo-auxiliar-pl-1256s-trivium-center", "Desarmadora con brazo auxiliar de 360° para empezar."),
   ("balanceadora-de-ruedas-unite-u-659", "Balanceadora de entrada con puntero láser y peso oculto."),
   ("elevador-tijera-gomeria-4500-kg-pl-45h", "Elevador tijera ultradelgado para gomería."),
   ("alineadora-hofmann-geoliner-609", "Alineadora compacta para ampliar el servicio."),
  ],
 },
 "faqs": [
  ("¿Qué máquinas necesito para abrir una gomería?",
   "Como mínimo una desarmadora de neumáticos, una balanceadora de ruedas, un compresor, herramientas neumáticas y un gato o elevador tijera. La alineadora es una ampliación posterior."),
  ("¿Por dónde conviene empezar?",
   "Por la desarmadora y la balanceadora, que son las máquinas que generan ingresos en cada cambio de neumáticos. Después el aire comprimido, las herramientas y el elevador."),
  ("¿Cuándo conviene sumar una alineadora?",
   "Cuando el flujo de clientes sea estable. La alineación se vende junto con el balanceo y es uno de los servicios que más aumenta el ticket del taller."),
  ("¿Pueden cotizarme todo el equipamiento junto?",
   "Sí. Armamos una propuesta completa según tus vehículos, tu espacio y tu presupuesto, con instalación y capacitación incluidas."),
  ("¿Venden a todo el país?",
   "Sí, enviamos e instalamos equipamiento en todo el país."),
 ],
 "posts": [
  "como-instalar-una-gomeria-guia-completa-para-emprender-con-exito",
  "equipamiento-esencial-para-comenzar-tu-taller-de-neumaticos",
  "como-abrir-un-taller-de-alineacion-y-balanceo",
  "la-importancia-de-ofrecer-rotacion-de-neumaticos-en-un-taller-o-gomeria",
 ],
},
{
 "slug": "equipos-de-taller-economicos",
 "title": "Equipos de taller económicos: elevadores, balanceadoras y desarmadoras",
 "h1": "Equipos de taller económicos: la línea Trivium Pro",
 "description": ("Equipos de taller económicos en Argentina: elevadores, balanceadoras y "
                 "desarmadoras Trivium Pro con precio, instalación y servicio técnico. "
                 "Cuándo conviene y cuándo elegir una marca premium."),
 "category": "elevadores",
 "intro": """
<div class="respuesta">
<p><strong>En resumen:</strong> si armás o ampliás un taller o una gomería y el presupuesto es lo que manda, la línea <strong>Trivium Pro</strong> cubre elevadores, balanceadoras, desarmadoras y equipamiento de taller a precio accesible, con instalación y servicio técnico propios en todo el país. Si el taller tiene alto volumen de trabajo y uso intensivo, las marcas de mayor calibre (<strong>Hofmann, Rotary Lift y Challenger Lifts</strong>) están pensadas para eso.</p>
</div>
""",
 "secciones": """
<h2>Qué es la línea Trivium Pro</h2>
<p>Trivium Pro es la marca propia de la empresa: equipamiento para talleres y gomerías de precio más accesible que las marcas importadas premium. Incluye elevadores de dos columnas, cuatro columnas y tijera, balanceadoras (incluida una para camiones), desarmadoras de neumáticos, elevadores para motos y equipamiento de taller. Varios modelos incorporan sistemas de seguridad como bloqueo mecánico o neumático, válvulas antiexplosión y, en algunos, certificación CE: el detalle está en la ficha de cada equipo.</p>

<h2>Línea económica o marca premium: cómo decidir</h2>
<p>No es una cuestión de "mejor o peor", sino de para qué trabajo está pensado cada equipo:</p>
<ul>
<li><strong>Elegí Trivium Pro</strong> si estás arrancando, si el volumen de trabajo es moderado o si necesitás equipar varias posiciones con un presupuesto ajustado.</li>
<li><strong>Elegí Hofmann, Rotary Lift o Challenger Lifts</strong> si el taller trabaja a alto volumen, atiende concesionarias o flotas, necesita tecnología de punta (alineación 3D, diagnóstico sin contacto, certificación ALI) o busca la máxima vida útil.</li>
<li><strong>Combinalas.</strong> Es común equipar con línea económica las posiciones de menor exigencia y reservar la marca premium para el equipo que más se usa.</li>
</ul>
<p>Si todavía estás definiendo qué comprar, mirá las guías por equipo: <a href="../../guias/elevadores-para-taller/">elevadores</a>, <a href="../../guias/balanceadoras-de-ruedas/">balanceadoras</a>, <a href="../../guias/desarmadoras-de-neumaticos/">desarmadoras</a> y <a href="../../guias/alineadoras-3d/">alineadoras</a>.</p>

<h2>Equipos de la línea económica con precio</h2>
<p>Una selección de equipos Trivium Pro por tipo de trabajo. El catálogo completo de la marca está en <a href="../../marca/trivium-pro/">Trivium Pro</a>.</p>
{{TABLA}}

<h2>Cómo armar un taller o una gomería con presupuesto ajustado</h2>
<ol>
<li><strong>Empezá por lo que genera ingresos de inmediato:</strong> desarmadora y balanceadora para una gomería, elevador de dos columnas o tijera para un taller mecánico.</li>
<li><strong>Sumá el aire comprimido y las herramientas neumáticas</strong> que necesite cada posición.</li>
<li><strong>Ampliá después:</strong> un segundo elevador, alineación, más posiciones.</li>
</ol>
<p>El orden detallado está en la guía <a href="../../guias/equipar-una-gomeria/">cómo equipar una gomería</a>. Consultá también por planes de pago y financiación.</p>
""",
 "tabla": {
  "precios": True,
  "slugs": [
   ("desarmadora-de-ruedas-unite-pl-1200u", "Desarmadora de entrada para gomería; plato de hasta 24\"."),
   ("desarmadora-de-ruedas-con-brazo-auxiliar-pl-1256s-trivium-center", "Con brazo auxiliar de 360°, llantas de 12\" a 26\"."),
   ("balanceadora-de-ruedas-unite-g66", "Con autocalibración, pantalla de 17\" y puntero láser."),
   ("balanceadora-de-ruedas-unite-s-901", "Con autocalibración y bandeja de herramientas."),
   ("elevador-tijera-gomeria-4500-kg-pl-45h", "Tijera ultradelgado para gomería, sin obra civil."),
   ("elevador-tijera-3000-kg-pl-e30", "Tijera para embutir, queda a nivel del piso."),
   ("elevador-tijera-portatil-3000-kg-pl-b30m", "Tijera portátil con triple sistema de seguridad."),
   ("elevador-dos-columnas-4000-kg-piso-libre-unite-pl-4-0-2a", "Dos columnas de piso libre para mecánica general."),
   ("elevador-dos-columnas-4000-kg-travesano-al-piso-unite-pl-4-0-2d", "Dos columnas con travesaño al piso."),
   ("elevador-dos-columnas-5000-kg-trivium-pro-u-t50msd", "Piso libre, 5.000 kg, certificación CE."),
   ("elevador-dos-columnas-6000-kg-vehiculos-electricos", "Para vehículos eléctricos y SUV pesadas."),
   ("elevador-cuatro-columnas-5000-kg-con-kit-para-alineacion", "Cuatro columnas con kit de alineación incluido."),
  ],
 },
 "faqs": [
  ("¿Qué equipos de taller económicos tiene Trivium Pro?",
   "Elevadores de dos columnas, cuatro columnas y tijera, balanceadoras (incluida una para camiones), desarmadoras de neumáticos, elevadores para motos y equipamiento de taller, todos de la línea propia Trivium Pro."),
  ("¿Cuáles son las máquinas más baratas para armar una gomería?",
   "Para una gomería, lo esencial es una desarmadora y una balanceadora, y un elevador tijera de baja altura o un gato. En la línea Trivium Pro tenés la desarmadora PL-1200U, las balanceadoras G-66 y S-901 y el elevador tijera PL-45H, con precio en la tabla de esta página."),
  ("¿La línea Trivium Pro es lo mismo que Hofmann o Rotary Lift?",
   "No. Hofmann, Rotary Lift y Challenger Lifts son marcas premium de mayor calibre, pensadas para alto volumen y uso intensivo. Trivium Pro es la línea económica propia, para talleres que arrancan o amplían capacidad con un presupuesto más ajustado."),
  ("¿Los equipos económicos incluyen instalación y servicio técnico?",
   "La instalación, la capacitación y el servicio técnico se cotizan según tu localidad, y los hacemos con equipo propio en todo el país. También hay repuestos."),
  ("¿Se puede financiar la compra?",
   "Sí, hay planes de pago y otras opciones. Consultá las condiciones por WhatsApp."),
  ("¿Los precios incluyen IVA?",
   "Sí. Los precios de esta página son finales con IVA incluido, en pesos, calculados con el dólar oficial del día."),
 ],
 "posts": [
  "equipamiento-esencial-para-comenzar-tu-taller-de-neumaticos",
  "como-instalar-una-gomeria-guia-completa-para-emprender-con-exito",
  "como-abrir-un-taller-de-alineacion-y-balanceo",
 ],
},
]
