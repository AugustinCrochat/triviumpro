"""Contenido de la página /marcas/.

Los datos que cambian (cantidad de equipos, categorías, sellos de origen de cada
marca, logos) salen de data/catalog.json y de los archivos en assets/img/marcas/;
acá sólo va el texto editorial de cada marca. Lo escribe a mano y se apoya en lo que ya
decían el sitio y el catálogo: no se agregan cifras ni afirmaciones que no estén
publicadas (ver scripts/origenes_content.py para el criterio sobre origen).

generate_marcas.py arma la página.
"""

UPDATED = "2026-10-21"

# Marcas premium importadas, en el orden en que se muestran. La marca propia
# (Trivium Pro) va aparte, destacada.
PREMIUM = ["rotary-lift", "hofmann", "challenger-lifts", "direct-lift", "forward-lift",
           "haweka", "prevost"]
PROPIA = "trivium-pro"

# slug -> datos editoriales.
#   nombre_seo : "Marca Argentina" + qué es, para H3 y datos estructurados
#   resumen    : una línea que dice qué hace la marca (la cita un LLM o un snippet)
#   desc       : 2-3 oraciones
#   ideal      : para quién conviene
#   origen_txt : cómo se escribe el origen cuando no sale de los sellos de los productos
MARCAS = {
    "rotary-lift": {
        "nombre_seo": "Rotary Lift Argentina",
        "resumen": "Elevadores hidráulicos para taller, concesionaria y flota.",
        "desc": ("Líder mundial en elevadores hidráulicos desde 1925 y estándar de calidad de la industria "
                 "automotriz. En Trivium Pro encontrás elevadores de dos columnas, de cuatro columnas y "
                 "de tijera. Somos distribuidores oficiales en Argentina."),
        "ideal": "Talleres, concesionarias y flotas de uso intensivo.",
        "origen_txt": "Estados Unidos · Madison, IN",
    },
    "hofmann": {
        "nombre_seo": "Hofmann Argentina",
        "resumen": "Alineadoras 3D, balanceadoras y desarmadoras de neumáticos de Snap-on.",
        "desc": ("Hofmann es la marca premium de Snap-on para alineadoras 3D, balanceadoras y servicio de "
                 "neumáticos: alineadoras Geoliner, balanceadoras Geodyna y desarmadoras Monty. "
                 "Fabrica en más de un país, por eso el origen se indica modelo por modelo."),
        "ideal": "Talleres y gomerías de alto volumen que buscan precisión de primer nivel.",
        "origen_txt": "Snap-on · Estados Unidos, Italia y Suecia según el modelo",
    },
    "challenger-lifts": {
        "nombre_seo": "Challenger Lifts Argentina",
        "resumen": "Elevadores de dos y cuatro columnas de Snap-on.",
        "desc": ("Challenger Lifts es la marca de elevadores de Snap-on: elevadores de dos y cuatro "
                 "columnas de alta resistencia para talleres y concesionarias."),
        "ideal": "Talleres y concesionarias que necesitan elevadores robustos.",
        "origen_txt": "Snap-on · Estados Unidos",
    },
    "direct-lift": {
        "nombre_seo": "Direct Lift Argentina (Rotary Solutions)",
        "resumen": "Elevadores tijera y portátiles de diseño compacto.",
        "desc": ("Direct Lift, de Rotary Solutions, ofrece elevadores tijera y portátiles para talleres y "
                 "garajes, con diseños compactos e instalación simplificada."),
        "ideal": "Talleres y garajes con poco espacio.",
        "origen_txt": "Estados Unidos · Kentucky",
    },
    "forward-lift": {
        "nombre_seo": "Forward Lift Argentina",
        "resumen": "Elevadores de gran capacidad, fijos y móviles.",
        "desc": ("Forward Lift se especializa en elevadores para camiones, buses y vehículos pesados, con "
                 "soluciones móviles y fijas de gran capacidad. Incluye también elevadores tijera para alineación."),
        "ideal": "Talleres de pesados y de alineación.",
        "origen_txt": "Estados Unidos · Indiana",
    },
    "haweka": {
        "nombre_seo": "Haweka Argentina: accesorios y herramientas para balanceo de ruedas",
        "resumen": "Accesorios y herramientas alemanas para balanceo y servicio de ruedas.",
        "desc": ("Haweka® reúne conos de centrado, conos expandibles, tuercas rápidas, calibres, pinzas "
                 "y espátulas para contrapesos y dispositivos de fijación, como el ProBike. Se eligen según el "
                 "eje de la balanceadora y el tipo de llanta."),
        "ideal": "Gomerías y talleres que balancean todo tipo de llantas y necesitan un centrado preciso.",
        "origen_txt": "Alemania",
    },
    "prevost": {
        "nombre_seo": "Prevost Argentina: redes de aire comprimido de aluminio",
        "resumen": "Red modular de aire comprimido de aluminio, sin soldadura.",
        "desc": ("Prevost Piping System es un sistema modular de distribución de aire comprimido 100 % aluminio: "
                 "sin óxido, sin soldadura y con la posibilidad de ampliar o reconfigurar la red sin rehacerla. "
                 "Tiene garantía de 10 años del fabricante y el proyecto y la instalación los hace Trivium."),
        "ideal": "Talleres y gomerías que instalan o amplían su red de aire.",
        "origen_txt": "Francia",
    },
    "trivium-pro": {
        "nombre_seo": "Trivium Pro: línea económica de equipos de taller",
        "resumen": "Nuestra línea propia de equipos de taller, a precio accesible.",
        "desc": ("Nuestra línea propia de equipos seleccionados y validados por Trivium: elevadores, "
                 "balanceadoras, desarmadoras, muebles y equipamiento de taller, con excelente relación "
                 "precio-calidad y respaldo local de posventa y repuestos. Todos los equipos de la línea "
                 "llevan marcado CE."),
        "ideal": "Talleres y gomerías que arrancan o amplían capacidad.",
        "origen_txt": "Marca propia · Argentina",
    },
}

FAQS = [
    ("¿Qué marcas de equipamiento para taller representa Trivium Pro en Argentina?",
     "Rotary Lift, Hofmann, Challenger Lifts, Direct Lift, Forward Lift, Haweka y Prevost, además de la línea "
     "propia Trivium Pro. Elevadores, alineadoras, balanceadoras, desarmadoras, accesorios de balanceo y redes "
     "de aire comprimido."),
    ("¿Qué diferencia hay entre las marcas premium y Trivium Pro?",
     "Las marcas premium (Rotary Lift, Hofmann, Challenger Lifts y otras) son importadas y están pensadas para "
     "un uso intensivo. Trivium Pro es la línea propia: equipos de precio más accesible, con marcado CE y respaldo "
     "local de posventa y repuestos, pensados para talleres que arrancan o amplían capacidad."),
    ("¿Hofmann y Challenger Lifts son de la misma empresa?",
     "Sí, las dos son marcas de Snap-on. Hofmann cubre alineación, balanceo y desarmado de neumáticos; "
     "Challenger Lifts, elevadores."),
    ("¿De qué país son los equipos?",
     "Depende de cada modelo: el origen lo declara el fabricante y se muestra con un sello sobre la foto. "
     "Hay equipos de Estados Unidos, Italia, Alemania, Suecia y Taiwán. Podés ver cada grupo en la sección "
     "de origen del sitio."),
    ("¿Tienen garantía y servicio técnico oficial?",
     "Sí. Trivium Pro ofrece garantía y servicio técnico oficial en todo el país y stock permanente de "
     "repuestos originales con garantía de trazabilidad."),
    ("¿La instalación está incluida en el precio?",
     "No. El montaje, la calibración y la puesta en marcha los hace nuestro equipo, pero la instalación se "
     "cotiza aparte del precio del equipo."),
]
