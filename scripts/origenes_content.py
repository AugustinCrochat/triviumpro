"""Contenido de las páginas /origen/<slug>/ y del índice /origen/.

Cada página explica un sello que aparece sobre la foto de los productos ("Made in
USA", "Made in Italy"... y "Marcado CE") y lista los equipos que lo llevan. El
listado, los conteos y los links a marcas/categorías salen de data/catalog.json
(campo "badges" de cada producto): acá sólo va el texto.

Criterio editorial: el origen es el que declara el fabricante de cada modelo, no
el de la marca. Hofmann, por ejemplo, es una marca de Snap-on y sus equipos se
fabrican en más de un país, por eso el sello se indica modelo por modelo. Del
marcado CE no se afirma nada sobre el país de fabricación: es una declaración de
conformidad, no un origen.

Marcadores que reemplaza generate_origenes.py:
  {{N}}      cantidad de equipos con este sello
  {{QUE_HAY}} lista de marcas y categorías con links, calculada del catálogo
"""

UPDATED = "2026-10-21"

# Orden en que se muestran en el índice, la barra lateral y los "otros orígenes".
ORIGENES = [
# --------------------------------------------------------------------------
{
 "slug": "estados-unidos",
 "badge": "made-in-usa",
 "pais": "Estados Unidos",
 "h1": "Equipos de taller Made in USA",
 "title": "Equipos de taller Made in USA: elevadores y alineadoras",
 "description": ("Equipos de taller fabricados en Estados Unidos: elevadores Rotary Lift y Direct Lift, "
                 "alineadoras Hofmann Geoliner y balanceadoras Hofmann Geodyna. Catálogo con servicio "
                 "técnico en todo el país."),
 "chip": "Fabricación en EE. UU.",
 "resumen": ("En Trivium Pro hay <strong>{{N}} equipos de taller fabricados en Estados Unidos</strong>: "
             "elevadores Rotary Lift y Direct Lift, y alineadoras y balanceadoras Hofmann. El sello "
             "<strong>Made in USA</strong> sobre la foto indica el país de fabricación declarado por "
             "el fabricante de cada modelo."),
 "secciones": """
<h2>Qué significa Made in USA en un equipo de taller</h2>
<p>«Made in» indica el país donde se fabricó el producto. En Estados Unidos, la Comisión Federal de Comercio (FTC) exige que un producto rotulado «Made in USA» sea fabricado <em>todo o virtualmente todo</em> en el país, con componentes y mano de obra locales. Para un taller o una gomería, el origen importa por una razón práctica: define de dónde vienen los repuestos, quién da soporte técnico y qué normas de diseño sigue el equipo.</p>

<h2>Qué equipos de fabricación estadounidense hay en el catálogo</h2>
{{QUE_HAY}}

<h2>Marcas con equipos Made in USA</h2>
<ul>
<li><strong>Rotary Lift</strong>: elevadores de dos columnas, de cuatro columnas y de tijera para autos, camionetas y vehículos pesados. Más información en <a href="../../marca/rotary-lift/">Rotary Lift</a> y en la nota sobre <a href="../../blog/certificacion-ali-elevadores/">la certificación ALI de los elevadores</a>.</li>
<li><strong>Direct Lift</strong>, línea de elevadores de Rotary Solutions: ver <a href="../../marca/direct-lift/">Direct Lift</a>.</li>
<li><strong>Hofmann</strong>, marca de Snap-on: alineadoras 3D Geoliner y balanceadoras Geodyna. Hofmann fabrica en más de un país: por eso el sello se indica modelo por modelo y la mayoría de las desarmadoras Monty, por ejemplo, llevan el de <a href="../italia/">Italia</a>. Ver <a href="../../marca/hofmann/">Hofmann</a>.</li>
</ul>

<h2>Servicio técnico y repuestos en Argentina</h2>
<p>Trivium Pro importa y distribuye estas marcas en Argentina, con garantía y servicio técnico oficial en todo el país y stock de repuestos originales con trazabilidad. El montaje, la calibración y la puesta en marcha están a cargo de nuestro equipo y <strong>la instalación se cotiza aparte</strong> del precio del equipo.</p>

<h2>Cómo elegir</h2>
<p>El origen es un dato más, no el único. Para decidir entre modelos conviene mirar el uso (autos, camiones, volumen diario), el espacio disponible y el presupuesto. Estas guías ayudan:</p>
<ul>
<li><a href="../../guias/elevadores-para-taller/">Elevador para taller: guía de compra</a></li>
<li><a href="../../guias/alineadoras-3d/">Alineadora 3D: guía de compra</a></li>
<li><a href="../../guias/balanceadoras-de-ruedas/">Balanceadora de ruedas: guía de compra</a></li>
<li><a href="../../guias/equipos-de-taller-economicos/">Equipos de taller económicos: la línea Trivium Pro</a>, si buscás una alternativa de menor inversión con <a href="../marcado-ce/">marcado CE</a>.</li>
</ul>
""",
 "faqs": [
  ("¿Qué significa Made in USA en un equipo de taller?",
   "Que el fabricante declara que el equipo se fabricó en Estados Unidos. En ese país, la FTC exige que un producto con ese rótulo sea fabricado todo o virtualmente todo allí. En Trivium Pro el sello se indica modelo por modelo, según lo que declara cada fabricante."),
  ("¿Qué equipos Made in USA ofrece Trivium Pro?",
   "Hay {{N}} equipos con este sello: elevadores Rotary Lift y Direct Lift, y alineadoras y balanceadoras Hofmann. Podés verlos todos en esta página."),
  ("¿Toda la línea Hofmann es de Estados Unidos?",
   "No. Hofmann es una marca de Snap-on y fabrica en más de un país. Por ejemplo, las alineadoras Geoliner y las balanceadoras Geodyna 7400L, 7600P, 7800-2P, 9000p y 980L (para camión) son de Estados Unidos; la mayoría de las desarmadoras Monty y las balanceadoras Geodyna 7100 y 7200VCI son de Italia; y la alineadora de camiones Josam CV-Aligner es de Suecia. Cada producto lleva el sello de su origen."),
  ("¿Los equipos importados tienen servicio técnico y repuestos en Argentina?",
   "Sí. Trivium Pro ofrece garantía y servicio técnico oficial en todo el país y stock permanente de repuestos originales con garantía de trazabilidad."),
  ("¿La instalación está incluida en el precio?",
   "No. El montaje, la calibración y la puesta en marcha los hace nuestro equipo, pero la instalación se cotiza aparte del precio del equipo."),
 ],
 "posts": ["certificacion-ali-elevadores", "hofmann-y-john-bean-dos-marcas-una-misma-tecnologia",
           "por-que-elegir-un-elevador-con-brazos-all-vehicle-de-rotary-lift"],
},
# --------------------------------------------------------------------------
{
 "slug": "italia",
 "badge": "made-in-italy",
 "pais": "Italia",
 "h1": "Equipos de taller Made in Italy",
 "title": "Equipos Made in Italy: desarmadoras y balanceadoras",
 "description": ("Equipos de taller fabricados en Italia: desarmadoras de neumáticos Hofmann Monty y "
                 "balanceadoras Hofmann Geodyna. Catálogo, guías de compra y servicio técnico en "
                 "todo el país."),
 "chip": "Fabricación en Italia",
 "resumen": ("En Trivium Pro hay <strong>{{N}} equipos de taller fabricados en Italia</strong>: "
             "desarmadoras de neumáticos Hofmann Monty y balanceadoras Hofmann Geodyna. El sello "
             "<strong>Made in Italy</strong> indica el país de fabricación declarado por el fabricante de cada modelo."),
 "secciones": """
<h2>Qué significa Made in Italy en un equipo de taller</h2>
<p>«Made in Italy» indica que el equipo se fabricó en Italia, un país con una industria consolidada de equipamiento para neumáticos: desarmadoras, balanceadoras y accesorios. En Trivium Pro el sello se muestra por modelo, porque una misma marca puede fabricar en distintos países.</p>

<h2>Qué equipos de fabricación italiana hay en el catálogo</h2>
{{QUE_HAY}}

<h2>Hofmann: una marca, varios países</h2>
<p>Hofmann es una marca de Snap-on. La mayoría de sus desarmadoras <strong>Monty</strong> y las balanceadoras <strong>Geodyna 7100</strong> y <strong>7200VCI</strong> llevan el sello de Italia; las alineadoras 3D Geoliner y las balanceadoras Geodyna 7400L, 7600P, 7800-2P, 9000p y 980L (para camión), el de <a href="../estados-unidos/">Estados Unidos</a>; y la alineadora de camiones Josam CV-Aligner, el de <a href="../suecia/">Suecia</a>. Más en <a href="../../marca/hofmann/">Hofmann</a>.</p>

<h2>Cómo elegir una desarmadora o una balanceadora</h2>
<p>Antes de mirar el origen, conviene definir qué ruedas vas a atender (llantas de aleación, run flat, bajo perfil, camión), cuántas por día y qué espacio tenés. Estas guías lo explican paso a paso:</p>
<ul>
<li><a href="../../guias/desarmadoras-de-neumaticos/">Desarmadora de neumáticos: guía de compra</a></li>
<li><a href="../../guias/balanceadoras-de-ruedas/">Balanceadora de ruedas: guía de compra</a></li>
<li><a href="../../guias/equipar-una-gomeria/">Equipar una gomería: qué comprar y en qué orden</a></li>
</ul>

<h2>Servicio técnico y repuestos en Argentina</h2>
<p>Trivium Pro ofrece garantía y servicio técnico oficial en todo el país y repuestos originales con trazabilidad. La instalación y puesta en marcha las hace nuestro equipo y <strong>se cotizan aparte</strong> del precio del equipo.</p>
""",
 "faqs": [
  ("¿Qué equipos Made in Italy ofrece Trivium Pro?",
   "Hay {{N}} equipos con este sello: desarmadoras de neumáticos Hofmann Monty y las balanceadoras Hofmann Geodyna 7100 y 7200VCI."),
  ("¿Hofmann es una marca italiana?",
   "Hofmann es una marca de Snap-on. Fabrica en más de un país, así que cada producto lleva el sello de su origen: Italia, Estados Unidos o Suecia, según el modelo."),
  ("¿Dónde veo las desarmadoras de neumáticos?",
   "En la categoría Desarmadoras del catálogo, y en la guía de compra de desarmadoras de neumáticos, que explica cómo elegir según el tipo de rueda y el volumen de trabajo."),
  ("¿Hay servicio técnico y repuestos en Argentina?",
   "Sí. Trivium Pro ofrece garantía y servicio técnico oficial en todo el país y stock de repuestos originales. La instalación se cotiza aparte."),
 ],
 "posts": ["la-importancia-de-balancear-ruedas-beneficios-clave-para-talleres-y-gomerias",
           "autocalibracion-en-una-balanceadora-de-ruedas-que-es-y-por-que-es-importante"],
},
# --------------------------------------------------------------------------
{
 "slug": "alemania",
 "badge": "made-in-germany",
 "pais": "Alemania",
 "h1": "Accesorios de taller Made in Germany",
 "title": "Accesorios de balanceo Made in Germany (Haweka)",
 "description": ("Accesorios para balanceo de ruedas fabricados en Alemania: conos de centrado, tuercas "
                 "rápidas, calibres y herramientas Haweka para balanceadoras. Catálogo y envíos a todo "
                 "el país."),
 "chip": "Fabricación en Alemania",
 "resumen": ("En Trivium Pro hay <strong>{{N}} accesorios fabricados en Alemania</strong>: conos de centrado, "
             "tuercas rápidas, calibres y herramientas Haweka para balanceo de ruedas. El sello "
             "<strong>Made in Germany</strong> indica el país de fabricación declarado por el fabricante."),
 "secciones": """
<h2>Qué significa Made in Germany en un accesorio de balanceo</h2>
<p>«Made in Germany» indica que el producto se fabricó en Alemania. En los accesorios de balanceo el origen se nota en lo que más importa: la precisión de los conos, las tuercas y los adaptadores que sujetan la rueda en la balanceadora.</p>

<h2>Qué accesorios de fabricación alemana hay en el catálogo</h2>
{{QUE_HAY}}

<h2>Por qué importa el centrado en el balanceo</h2>
<p>Una balanceadora mide el desequilibrio respecto del eje sobre el que gira la rueda. Si la rueda no queda perfectamente centrada, el resultado queda desplazado aunque la balanceadora sea buena. Por eso los conos de centrado, las tuercas rápidas y los adaptadores se eligen según el tipo de llanta (de acero, de aleación, con o sin agujero central) y se mantienen en buen estado. Para entender el proceso completo, mirá la nota sobre <a href="../../blog/la-importancia-de-balancear-ruedas-beneficios-clave-para-talleres-y-gomerias/">la importancia de balancear ruedas</a> y la <a href="../../guias/balanceadoras-de-ruedas/">guía de compra de balanceadoras</a>.</p>

<h2>Haweka</h2>
<p>Los accesorios de este origen son de la marca <a href="../../marca/haweka/">Haweka</a>, especializada en accesorios y herramientas para el servicio de neumáticos y ruedas. Se ofrecen en la categoría <a href="../../categoria/accesorios-balanceo/">Accesorios de balanceo</a>.</p>

<h2>Envíos y consultas</h2>
<p>Enviamos a todo el país. Si no sabés qué cono o adaptador necesita tu balanceadora, contanos marca y modelo y te orientamos.</p>
""",
 "faqs": [
  ("¿Qué productos Made in Germany ofrece Trivium Pro?",
   "Hay {{N}} accesorios y herramientas Haweka para balanceo de ruedas: conos de centrado, conos expandibles, tuercas rápidas, calibres, pinzas para contrapesos y otros."),
  ("¿Sirven para cualquier balanceadora?",
   "Depende del eje y del diámetro del cono. Los accesorios indican las medidas compatibles en su ficha; si tenés dudas, consultanos con la marca y el modelo de tu balanceadora."),
  ("¿Por qué conviene usar conos de centrado de buena calidad?",
   "Porque la balanceadora mide respecto del eje de la rueda. Si el centrado tiene juego o los conos están gastados, el balanceo queda desplazado aunque la máquina esté bien calibrada."),
 ],
 "posts": ["la-importancia-de-balancear-ruedas-beneficios-clave-para-talleres-y-gomerias"],
},
# --------------------------------------------------------------------------
{
 "slug": "suecia",
 "badge": "made-in-sweden",
 "pais": "Suecia",
 "h1": "Equipos de taller Made in Sweden",
 "title": "Alineadora de camiones Made in Sweden: Josam CV-Aligner",
 "description": ("Equipo de taller fabricado en Suecia para vehículos pesados: alineadora de camiones "
                 "y colectivos Josam CV-Aligner. Catálogo, casos de instalación y servicio técnico en todo el país."),
 "chip": "Fabricación en Suecia",
 "resumen": ("En Trivium Pro hay <strong>{{N}} equipo fabricado en Suecia</strong>, pensado para "
             "vehículos pesados: la alineadora de camiones y colectivos <strong>Josam CV-Aligner</strong>. "
             "El sello <strong>Made in Sweden</strong> indica el país de fabricación declarado por el fabricante."),
 "secciones": """
<h2>Qué significa Made in Sweden en un equipo de taller</h2>
<p>«Made in Sweden» indica que el equipo se fabricó en Suecia. En el catálogo de Trivium Pro el origen sueco corresponde a la alineadora de vehículos pesados Josam CV-Aligner, un equipo donde la robustez y la precisión de medición son críticas.</p>

<h2>Qué equipo de fabricación sueca hay en el catálogo</h2>
{{QUE_HAY}}

<h2>Josam CV-Aligner</h2>
<p>Josam, marca de Snap-on, es la alineadora de camiones y colectivos que instalamos, por ejemplo, en Mendoza. Podés leer el caso en <a href="../../blog/instalamos-una-josam-cv-aligner-en-mendoza-tecnologia-snap-on-para-el-alineado-de-vehiculos-pesados/">Instalamos una Josam CV-Aligner en Mendoza</a>, la nota sobre <a href="../../blog/alineacion-de-colectivos-con-tecnologia-sueca-josam-cv-aligner/">alineación de colectivos con tecnología sueca</a> y los <a href="../../blog/ventajas-de-la-alineacion-de-camiones-para-empresas-de-mantenimiento/">beneficios de la alineación de camiones para flotas</a>.</p>

<h2>Si equipás un taller de pesados</h2>
<p>Mirá también las <a href="../../categoria/elevadores-pesados/">opciones de elevadores para pesados</a> y la <a href="../../guias/alineadoras-3d/">guía de alineadoras</a>.</p>

<h2>Servicio técnico y repuestos en Argentina</h2>
<p>Trivium Pro ofrece garantía y servicio técnico oficial en todo el país. La instalación y puesta en marcha las hace nuestro equipo y se cotizan aparte del precio del equipo.</p>
""",
 "faqs": [
  ("¿Qué equipo Made in Sweden ofrece Trivium Pro?",
   "Hay {{N}}: la alineadora de camiones y colectivos Josam CV-Aligner."),
  ("¿La Josam CV-Aligner sirve para colectivos y camiones?",
   "Sí, está pensada para alinear vehículos pesados. Tiene comunicación inalámbrica entre las unidades de medición. Mirá la nota sobre alineación de colectivos con tecnología sueca para ver cómo se usa."),
  ("¿Hay servicio técnico en Argentina?",
   "Sí. Trivium Pro ofrece garantía y servicio técnico oficial en todo el país. La instalación se cotiza aparte."),
 ],
 "posts": ["alineacion-de-colectivos-con-tecnologia-sueca-josam-cv-aligner",
           "ventajas-de-la-alineacion-de-camiones-para-empresas-de-mantenimiento"],
},
# --------------------------------------------------------------------------
{
 "slug": "taiwan",
 "badge": "made-in-taiwan",
 "pais": "Taiwán",
 "h1": "Herramientas neumáticas Made in Taiwan",
 "title": "Herramientas neumáticas Made in Taiwan (Kuani)",
 "description": ("Herramientas neumáticas fabricadas en Taiwán: llaves de impacto y llaves crique Kuani, "
                 "e inflador de neumáticos digital. Catálogo y envíos a todo el país."),
 "chip": "Fabricación en Taiwán",
 "resumen": ("En Trivium Pro hay <strong>{{N}} herramientas fabricadas en Taiwán</strong>: llaves de impacto "
             "neumáticas, llaves crique y un inflador de neumáticos digital de la marca Kuani. El sello "
             "<strong>Made in Taiwan</strong> indica el país de fabricación declarado por el fabricante."),
 "secciones": """
<h2>Qué significa Made in Taiwan en una herramienta de taller</h2>
<p>«Made in Taiwan» indica que la herramienta se fabricó en Taiwán, un centro de producción de herramientas manuales y neumáticas de uso profesional. En el catálogo de Trivium Pro es el origen de las herramientas neumáticas Kuani.</p>

<h2>Qué herramientas de fabricación taiwanesa hay en el catálogo</h2>
{{QUE_HAY}}

<h2>Cómo elegir una llave de impacto neumática</h2>
<p>Se elige por el uso: el cuadrante de la herramienta (tamaño del acople), el torque disponible, el consumo de aire y el peso. Las llaves de impacto se usan sobre todo para aflojar y apretar bulones de rueda, y para eso conviene un equipo de aire comprimido con caudal suficiente. Mirá la categoría <a href="../../categoria/herramientas-neumaticas/">Herramientas neumáticas</a> y la de <a href="../../categoria/aire-comprimido/">Aire comprimido</a>, y la guía para <a href="../../guias/equipar-una-gomeria/">equipar una gomería</a>.</p>

<h2>Envíos y consultas</h2>
<p>Enviamos a todo el país. Si dudás qué modelo se ajusta a tu trabajo, contanos qué vas a hacer con la herramienta y te recomendamos.</p>
""",
 "faqs": [
  ("¿Qué herramientas Made in Taiwan ofrece Trivium Pro?",
   "Hay {{N}} productos de la marca Kuani: llaves de impacto neumáticas, llaves crique neumáticas y un inflador de neumáticos digital."),
  ("¿Necesito un compresor para usar una llave neumática?",
   "Sí. Las herramientas neumáticas funcionan con aire comprimido: el compresor tiene que entregar el caudal y la presión que indica la ficha de cada herramienta."),
  ("¿Se envían a todo el país?",
   "Sí, enviamos a todo el país. El costo de envío se cotiza según la localidad."),
 ],
 "posts": ["la-importancia-de-ofrecer-rotacion-de-neumaticos-en-un-taller-o-gomeria"],
},
# --------------------------------------------------------------------------
{
 "slug": "marcado-ce",
 "badge": "ce-ue",
 "pais": "Marcado CE",
 "h1": "Equipos de taller con marcado CE",
 "title": "Marcado CE en equipos de taller: qué es y qué equipos lo llevan",
 "description": ("Qué es el marcado CE y qué equipos de taller Trivium Pro lo llevan: elevadores, "
                 "balanceadoras, desarmadoras y más. Qué significa, qué no significa y cómo se relaciona "
                 "con la seguridad de la máquina."),
 "chip": "Conformidad europea",
 "resumen": ("<strong>{{N}} equipos de la línea Trivium Pro llevan marcado CE</strong>: elevadores, "
             "balanceadoras, desarmadoras, equipamiento y accesorios. El marcado CE es la declaración del "
             "fabricante de que el producto cumple los requisitos de seguridad, salud y protección ambiental "
             "de la normativa europea que le aplica. <strong>No indica el país de fabricación</strong> ni es un sello de calidad."),
 "secciones": """
<h2>Qué es el marcado CE</h2>
<p>El marcado CE es la declaración del fabricante de que un producto cumple los requisitos de seguridad, salud y protección del ambiente de la legislación de la Unión Europea que le corresponde. Es obligatorio para comercializar ciertos productos en el Espacio Económico Europeo. El fabricante evalúa la conformidad, prepara la documentación técnica y firma una declaración de conformidad; en productos de mayor riesgo interviene además un organismo notificado.</p>

<h2>Qué normativa aplica a un equipo de taller</h2>
<p>Según el tipo de equipo, intervienen principalmente:</p>
<ul>
<li>La <strong>Directiva de Máquinas 2006/42/CE</strong>, que será reemplazada por el Reglamento (UE) 2023/1230 a partir del 20 de enero de 2027. Cubre elevadores, balanceadoras, desarmadoras y otras máquinas.</li>
<li>La <strong>Directiva de Baja Tensión 2014/35/UE</strong>, para la seguridad eléctrica.</li>
<li>La <strong>Directiva de Compatibilidad Electromagnética 2014/30/UE</strong>, para evitar interferencias.</li>
</ul>
<p>Para cada familia de equipos existen además normas armonizadas; por ejemplo, la EN 1493 para elevadores de vehículos.</p>

<h2>Qué equipos Trivium Pro llevan marcado CE</h2>
{{QUE_HAY}}

<h2>Qué no significa el marcado CE</h2>
<ul>
<li><strong>No indica el país de fabricación.</strong> «CE» no quiere decir «fabricado en Europa»: lo llevan productos fabricados en cualquier país que se vendan en el mercado europeo.</li>
<li><strong>No es un sello de calidad ni de desempeño.</strong> Habla de conformidad con requisitos esenciales de seguridad, no de durabilidad ni de prestaciones.</li>
<li><strong>No reemplaza la certificación ALI</strong> que tienen algunos elevadores: esa es una certificación independiente de terceros específica para elevadores de vehículos. Ver <a href="../../blog/certificacion-ali-elevadores/">qué es la certificación ALI</a>.</li>
</ul>

<h2>Qué mirar al comprar un equipo con marcado CE</h2>
<p>Pedí el manual, la placa de identificación del equipo y, si la necesitás para tu seguro o tu habilitación, la documentación disponible del modelo. Consultanos por el equipo que te interesa. Para comparar opciones, mirá la guía de <a href="../../guias/equipos-de-taller-economicos/">equipos de taller económicos de la línea Trivium Pro</a>.</p>

<h2>Servicio técnico</h2>
<p>Trivium Pro ofrece garantía y servicio técnico oficial en todo el país y repuestos originales. La instalación se cotiza aparte del precio del equipo.</p>
""",
 "faqs": [
  ("¿Qué es el marcado CE?",
   "Es la declaración del fabricante de que el producto cumple los requisitos de seguridad, salud y protección ambiental de la legislación de la Unión Europea que le aplica."),
  ("¿CE significa fabricado en Europa?",
   "No. El marcado CE no indica el país de fabricación: lo llevan productos hechos en cualquier país que se comercialicen en el mercado europeo."),
  ("¿Qué equipos de Trivium Pro llevan marcado CE?",
   "Los {{N}} equipos de la línea Trivium Pro del catálogo: elevadores de dos y cuatro columnas, de tijera y para motos, balanceadoras, desarmadoras, equipamiento de taller y accesorios de balanceo."),
  ("¿El marcado CE es lo mismo que la certificación ALI?",
   "No. El marcado CE es una declaración del fabricante sobre conformidad con la normativa europea. La certificación ALI es una certificación independiente de terceros, propia de los elevadores de vehículos."),
  ("¿Es obligatorio el marcado CE en Argentina?",
   "Es un requisito de la Unión Europea, no argentino. En Argentina rigen además las reglamentaciones locales que apliquen a cada tipo de equipo. Consultanos por el modelo que te interesa."),
 ],
 "posts": ["certificacion-ali-elevadores"],
},
]
