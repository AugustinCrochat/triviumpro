"""Contenido de las páginas por zona /zonas/<slug>/ y del hub /zonas/.

Criterio: una página de zona sólo existe si hay algo verdadero y específico
que decir de esa zona (una instalación, una capacitación, la sede). Una
plantilla con el nombre de la provincia cambiado es una "doorway page": Google
la trata como spam. Para el resto del país está el hub, que cubre las 24
jurisdicciones con la información común (envío, instalación, posventa).

Para sumar una zona: agregar una entrada a ZONAS con al menos un caso real
(idealmente una nota del blog) y regenerar con scripts/generate_zonas.py.

Los datos de servicio (posventa en 48–72 hs en todo el país) salen de
/instalacion-posventa-y-servicios/. Flete y tiempos de entrega se confirman en
cada cotización, como dice llms.txt.
"""

UPDATED = "2026-10-09"

# Jurisdicciones para el hub. (nombre, slug de zona o None)
JURISDICCIONES = [
    ("Buenos Aires", "buenos-aires"), ("Ciudad Autónoma de Buenos Aires", "buenos-aires"),
    ("Catamarca", None), ("Chaco", None), ("Chubut", None),
    ("Córdoba", "cordoba"), ("Corrientes", None), ("Entre Ríos", None),
    ("Formosa", None), ("Jujuy", None), ("La Pampa", None), ("La Rioja", None),
    ("Mendoza", "mendoza"), ("Misiones", None), ("Neuquén", None), ("Río Negro", None),
    ("Salta", "salta"), ("San Juan", None), ("San Luis", None), ("Santa Cruz", None),
    ("Santa Fe", None), ("Santiago del Estero", None), ("Tierra del Fuego", None),
    ("Tucumán", None),
]

PROCESO = """
<h2>Cómo trabajamos</h2>
<ol>
<li><strong>Asesoramiento.</strong> Analizamos el espacio, el flujo de trabajo, el tipo de vehículos y el presupuesto para recomendarte el equipamiento correcto.</li>
<li><strong>Cotización y envío.</strong> Cotizamos por separado el equipo, el flete y la instalación, según tu localidad.</li>
<li><strong>Instalación (se cotiza aparte).</strong> Nuestro equipo técnico propio viaja a tu taller y se encarga del montaje, el anclaje, la conexión hidráulica y eléctrica, la calibración y la prueba de funcionamiento.</li>
<li><strong>Capacitación.</strong> Entrenamos a tu equipo en uso seguro y mantenimiento preventivo.</li>
<li><strong>Posventa.</strong> Servicio técnico y repuestos originales de las marcas que representamos, con atención en 48 a 72 horas en todo el país.</li>
</ol>
"""

ZONAS = [
{
 "slug": "cordoba",
 "nombre": "Córdoba",
 "title": "Equipamiento para talleres y gomerías en Córdoba",
 "h1": "Equipamiento para talleres y gomerías en Córdoba",
 "description": ("Elevadores, alineadoras, balanceadoras y desarmadoras en Córdoba. Sede en "
                 "Av. Donato Álvarez 7971, con instalación (a cotizar), capacitación y servicio técnico "
                 "propios. Distribuidores oficiales de Rotary Lift y Hofmann."),
 "intro": """
<div class="respuesta">
<p><strong>En resumen:</strong> Trivium Pro tiene su sede en Córdoba capital (Av. Donato Álvarez 7971) y desde ahí abastece, instala y da servicio técnico a talleres, gomerías y concesionarias de la provincia. Somos distribuidores oficiales de Rotary Lift (elevadores) y Hofmann (alineación y balanceo), y fabricamos la línea económica Trivium Pro.</p>
</div>
""",
 "secciones": """
<h2>Qué hacemos en Córdoba</h2>
<ul>
<li><strong>Venta de equipamiento:</strong> elevadores de dos y cuatro columnas, tijeras, alineadoras 3D, balanceadoras, desarmadoras, herramientas neumáticas y muebles de taller.</li>
<li><strong>Instalación y puesta en marcha</strong> con equipo técnico propio.</li>
<li><strong>Capacitación</strong> a los operarios en el taller del cliente.</li>
<li><strong>Servicio técnico y repuestos</strong> originales de las marcas que representamos.</li>
</ul>

<h2>Un caso en la provincia: capacitación en Neumáticos Pons</h2>
<p>Estuvimos en Córdoba con el equipo de Neumáticos Pons, parte de su red de gomerías, dando una capacitación sobre la alineadora 3D Hofmann Geoliner 630: configuración, interpretación de datos, lectura de ángulos y errores comunes. También revisamos el estado de los platos giratorios del elevador, los targets y las cámaras, y actualizamos la base de datos de vehículos. Podés leerlo completo en <a href="../../blog/formacion-tecnica-en-alineadora-3d-geoliner-630-en-neumaticos-pons-cordoba/">Formación técnica en Geoliner 630 en Neumáticos Pons</a>.</p>

<h2>Qué suelen necesitar los talleres de la zona</h2>
<p>Para abrir o ampliar un taller, estas son las guías que más ayudan a decidir:</p>
<ul>
<li><a href="../../guias/equipar-una-gomeria/">Cómo equipar una gomería</a>, para quien arranca.</li>
<li><a href="../../guias/alineadoras-3d/">Cómo elegir una alineadora 3D</a>, para sumar alineación.</li>
<li><a href="../../guias/elevadores-para-taller/">Cómo elegir un elevador</a>, con requisitos del piso.</li>
<li><a href="../../guias/balanceadoras-de-ruedas/">Balanceadoras</a> y <a href="../../guias/desarmadoras-de-neumaticos/">desarmadoras</a>.</li>
</ul>

<h2>Dónde estamos</h2>
<p>Av. Donato Álvarez 7971, Córdoba. Para visitas y retiros, coordiná antes por WhatsApp al <a href="https://wa.me/5491127015294">+54 9 11 2701-5294</a> o por mail a <a href="mailto:info@trivium.ar">info@trivium.ar</a>.</p>
<p>En el mismo local funciona <a href="https://neumaticos.trivium.ar/">Neumáticos Trivium</a>, nuestra gomería y outlet de neumáticos en Córdoba: <a href="https://neumaticos.trivium.ar/neumaticos-baratos">neumáticos baratos</a>, <a href="https://neumaticos.trivium.ar/neumaticos/carga">neumáticos de carga</a>, <a href="https://neumaticos.trivium.ar/neumaticos/at">neumáticos A/T</a> y servicios de <a href="https://neumaticos.trivium.ar/servicios/alineacion">alineación</a>, <a href="https://neumaticos.trivium.ar/servicios/balanceo">balanceo</a> y <a href="https://neumaticos.trivium.ar/servicios/rotacion-de-ruedas">rotación de ruedas</a>.</p>
{{PROCESO}}
""",
 "faqs": [
  ("¿Trivium Pro tiene sede en Córdoba?",
   "Sí. Atendemos al público en Av. Donato Álvarez 7971, Córdoba. Coordiná tu visita por WhatsApp o mail antes de ir."),
  ("¿Instalan los equipos en talleres de Córdoba?",
   "Sí. Nuestro equipo técnico propio hace el montaje, el anclaje, la conexión, la calibración y la prueba de funcionamiento, y capacita a tus operarios. La instalación se cotiza aparte."),
  ("¿Qué marcas venden en Córdoba?",
   "Representamos a Rotary Lift, Hofmann, Challenger Lifts, Direct Lift, Forward Lift, Haweka y Prevost, y tenemos la línea propia Trivium Pro."),
  ("¿Dan servicio técnico y repuestos en Córdoba?",
   "Sí. Ofrecemos servicio técnico oficial de las marcas que representamos, con atención en 48 a 72 horas, y repuestos originales."),
 ],
 "posts": ["formacion-tecnica-en-alineadora-3d-geoliner-630-en-neumaticos-pons-cordoba",
           "capacitacion-y-puesta-en-marcha-de-alineadora-hofmann-geoliner-630",
  'neumaticos-trivium-la-gomeria-de-cordoba-donde-usamos-lo-que-vendemos',
  'las-maquinas-del-taller-de-neumaticos-trivium-arguello'],
 "local": True,
},
{
 "slug": "mendoza",
 "nombre": "Mendoza",
 "title": "Equipamiento para talleres y gomerías en Mendoza",
 "h1": "Equipamiento para talleres y gomerías en Mendoza",
 "description": ("Equipamiento para talleres en Mendoza con instalación a cotizar y servicio técnico: "
                 "elevadores, alineadoras, balanceadoras y desarmadoras. Instalamos una "
                 "Josam CV-Aligner en LANZ Neumáticos – Dunlop Mendoza."),
 "intro": """
<div class="respuesta">
<p><strong>En resumen:</strong> vendemos, enviamos e instalamos equipamiento para talleres, gomerías y servicios de pesados en Mendoza. Instalamos una alineadora de camiones Josam CV-Aligner en LANZ Neumáticos – Dunlop Mendoza, concesionario oficial de la zona. Instalación, capacitación y posventa son con equipo técnico propio.</p>
</div>
""",
 "secciones": """
<h2>Un caso en Mendoza: Josam CV-Aligner en LANZ Neumáticos</h2>
<p>Instalamos una alineadora de camiones Josam CV-Aligner en LANZ Neumáticos – Dunlop Mendoza. La Josam está fabricada en Suecia, es parte del grupo Snap-on y está diseñada para alinear camiones, ómnibus y vehículos pesados con medición 3D por cámaras digitales, sin contacto mecánico, con fijación por imanes y reportes automáticos. Leé el caso completo en <a href="../../blog/instalamos-una-josam-cv-aligner-en-mendoza-tecnologia-snap-on-para-el-alineado-de-vehiculos-pesados/">Instalamos una Josam CV-Aligner en Mendoza</a>.</p>
<p>Si trabajás con flotas, transporte o vehículos pesados, mirá también <a href="../../blog/alineacion-de-colectivos-con-tecnologia-sueca-josam-cv-aligner/">alineación de colectivos con tecnología sueca</a> y <a href="../../blog/ventajas-de-la-alineacion-de-camiones-para-empresas-de-mantenimiento/">ventajas de la alineación de camiones</a>.</p>

<h2>Equipos para el taller mendocino</h2>
<ul>
<li><a href="../../guias/alineadoras-3d/">Alineadoras 3D</a>, para autos y camiones.</li>
<li><a href="../../guias/elevadores-para-taller/">Elevadores</a>, incluidos los de cuatro columnas de alta capacidad para pesados.</li>
<li><a href="../../guias/balanceadoras-de-ruedas/">Balanceadoras</a>, con modelos para ruedas de camión de hasta 250 kg.</li>
<li><a href="../../guias/desarmadoras-de-neumaticos/">Desarmadoras</a>, con modelos para camión.</li>
</ul>
{{PROCESO}}
""",
 "faqs": [
  ("¿Instalan equipos en Mendoza?",
   "Sí. Instalamos una alineadora de camiones Josam CV-Aligner en LANZ Neumáticos – Dunlop Mendoza, y hacemos instalación, capacitación y posventa en todo el país. La instalación se cotiza aparte."),
  ("¿Qué alineadora sirve para camiones y colectivos?",
   "La Josam CV-Aligner, que alinea vehículos pesados con medición por cámaras y comunicación inalámbrica entre las unidades."),
  ("¿Hacen envíos a Mendoza?",
   "Sí, enviamos a todo el país. El flete y los tiempos se confirman en la cotización según tu localidad."),
  ("¿Hay servicio técnico y repuestos en Mendoza?",
   "Sí. Ofrecemos servicio técnico de las marcas oficiales con atención en 48 a 72 horas en todo el país, y repuestos originales."),
 ],
 "posts": ["instalamos-una-josam-cv-aligner-en-mendoza-tecnologia-snap-on-para-el-alineado-de-vehiculos-pesados",
           "alineacion-de-colectivos-con-tecnologia-sueca-josam-cv-aligner",
           "ventajas-de-la-alineacion-de-camiones-para-empresas-de-mantenimiento"],
},
{
 "slug": "salta",
 "nombre": "Salta",
 "title": "Equipamiento para talleres y gomerías en Salta",
 "h1": "Equipamiento para talleres y gomerías en Salta",
 "description": ("Equipamiento completo para talleres en Salta: elevadores, alineadora 3D, "
                 "balanceadora y desarmadora, con instalación a cotizar. Instalamos un taller completo "
                 "en Las Lajitas."),
 "intro": """
<div class="respuesta">
<p><strong>En resumen:</strong> llegamos a Salta con equipo técnico propio. En Las Lajitas instalamos el equipamiento completo de un taller nuevo, Repuestera del Milagro: elevadores, balanceadora, desarmadora y alineadora 3D. Si estás armando un taller en el norte, podemos cotizar todo junto, con instalación y capacitación.</p>
</div>
""",
 "secciones": """
<h2>Un caso en Salta: taller completo en Las Lajitas</h2>
<p>En Las Lajitas, Salta, instalamos el equipamiento completo de Repuestera del Milagro:</p>
<ul>
<li>un elevador tijera Trivium Pro, para alineación e inspección rápida;</li>
<li>un elevador de dos columnas Direct Lift DL9, para mecánica general;</li>
<li>una balanceadora Trivium Pro G-66, con pantalla digital y medición automática;</li>
<li>una desarmadora Trivium Pro con brazo asistente;</li>
<li>una alineadora 3D Hofmann Geoliner.</li>
</ul>
<p>El detalle completo está en <a href="../../blog/equipamiento-completo-para-repuestera-del-milagro/">Equipamiento completo para Repuestera del Milagro</a>.</p>

<h2>Armar un taller desde cero</h2>
<p>Si estás en esa etapa, empezá por <a href="../../guias/equipar-una-gomeria/">cómo equipar una gomería</a> y por <a href="../../blog/como-abrir-un-taller-de-alineacion-y-balanceo/">cómo abrir un taller de alineación y balanceo</a>. Para cada equipo, tenés la guía de compra: <a href="../../guias/elevadores-para-taller/">elevadores</a>, <a href="../../guias/alineadoras-3d/">alineadoras</a>, <a href="../../guias/balanceadoras-de-ruedas/">balanceadoras</a> y <a href="../../guias/desarmadoras-de-neumaticos/">desarmadoras</a>.</p>
{{PROCESO}}
""",
 "faqs": [
  ("¿Instalan equipos en Salta?",
   "Sí. Instalamos un taller completo en Las Lajitas, Salta, para Repuestera del Milagro, con elevadores, balanceadora, desarmadora y alineadora 3D. La instalación se cotiza aparte del equipo."),
  ("¿Pueden cotizar un taller completo?",
   "Sí. Armamos una propuesta con todos los equipos y, por separado, la instalación y la capacitación, según tus vehículos, tu espacio y tu presupuesto."),
  ("¿Hacen envíos al norte del país?",
   "Sí, enviamos a todo el país. El flete y los tiempos se confirman en la cotización según tu localidad."),
  ("¿Dan servicio técnico en Salta?",
   "Sí. Ofrecemos servicio técnico y repuestos originales, con atención en 48 a 72 horas en todo el país."),
 ],
 "posts": ["equipamiento-completo-para-repuestera-del-milagro",
           "como-abrir-un-taller-de-alineacion-y-balanceo"],
},
{
 "slug": "buenos-aires",
 "nombre": "Buenos Aires",
 "title": "Equipamiento para talleres y gomerías en Buenos Aires y AMBA",
 "h1": "Equipamiento para talleres y gomerías en Buenos Aires y AMBA",
 "description": ("Elevadores, alineadoras, balanceadoras y desarmadoras para talleres en "
                 "Buenos Aires y AMBA, con instalación a cotizar y posventa. Servicio técnico en "
                 "Lions Group Bosch Car Service, Canning."),
 "intro": """
<div class="respuesta">
<p><strong>En resumen:</strong> vendemos, instalamos y damos servicio técnico a talleres, concesionarias y gomerías de la Ciudad de Buenos Aires y la provincia. Hacemos mantenimiento preventivo de los equipos instalados, como en Lions Group Bosch Car Service, en Canning. Atención comercial por WhatsApp al +54 9 11 2701-5294.</p>
</div>
""",
 "secciones": """
<h2>Un caso en la provincia: mantenimiento preventivo en Lions Group</h2>
<p>Visitamos a Lions Group Bosch Car Service, en Canning, para una revisión técnica de su balanceadora y la inspección de otros equipos clave. Verificamos el estado de su alineadora Geoliner 630 y de su elevador de dos columnas Rotary Lift. Es un buen ejemplo de por qué el mantenimiento preventivo evita paradas: <a href="../../blog/la-importancia-del-mantenimiento-preventivo-en-equipos-de-taller-caso-exitoso-lions-group/">leé el caso completo</a>.</p>

<h2>Oeste del Gran Buenos Aires: San Justo y La Matanza</h2>
<p>En el oeste del conurbano la competencia de gomerías es alta y el diferencial está en el equipo y en los servicios completos. El grupo Trivium abre su propia gomería, Neumáticos Trivium San Justo, en Pres. Juan Domingo Perón 2847, San Justo, en diciembre. Qué servicios compiten mejor y qué equipo hace falta está en <a href="../../blog/gomeria-en-buenos-aires-equipamiento-y-servicios-para-el-oeste-del-conurbano/">gomería en Buenos Aires: equipamiento y servicios para el oeste del conurbano</a>.</p>

<h2>Guías para decidir</h2>
<ul>
<li><a href="../../guias/elevadores-para-taller/">Cómo elegir un elevador</a></li>
<li><a href="../../guias/alineadoras-3d/">Cómo elegir una alineadora 3D</a></li>
<li><a href="../../guias/balanceadoras-de-ruedas/">Cómo elegir una balanceadora</a></li>
<li><a href="../../guias/desarmadoras-de-neumaticos/">Cómo elegir una desarmadora</a></li>
</ul>
{{PROCESO}}
""",
 "faqs": [
  ("¿Hacen instalación y servicio técnico en Buenos Aires y AMBA?",
   "Sí. Instalamos y damos servicio técnico en Buenos Aires y en todo el país. La instalación se cotiza aparte. Hacemos también mantenimiento preventivo de equipos instalados."),
  ("¿Con quién se puede hablar en Buenos Aires?",
   "Por WhatsApp al +54 9 11 2701-5294 o por mail a info@trivium.ar. Te respondemos en el día."),
  ("¿Qué marcas venden?",
   "Representamos a Rotary Lift, Hofmann, Challenger Lifts, Direct Lift, Forward Lift, Haweka y Prevost, y tenemos la línea propia Trivium Pro."),
  ("¿Qué hacen en el mantenimiento preventivo?",
   "Revisamos el estado de los equipos, como la balanceadora, la alineadora y el elevador, para detectar desgaste antes de que haya una parada."),
 ],
 "posts": ["la-importancia-del-mantenimiento-preventivo-en-equipos-de-taller-caso-exitoso-lions-group",
  'gomeria-en-buenos-aires-equipamiento-y-servicios-para-el-oeste-del-conurbano'],
},
]
