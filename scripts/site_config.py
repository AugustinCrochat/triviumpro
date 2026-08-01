"""Configuración compartida de los generadores.

SITE_URL es el dominio canónico: entra en los canonical, los og:url, el
JSON-LD, el sitemap y los links del feed de Meta. Estaba repetido en cuatro
scripts, así que migrar de dominio eran cuatro ediciones que podían quedar
desincronizadas — y una sola mal puesta manda a Google señales contradictorias.

Para migrar a pro.trivium.ar se cambia acá y se regenera todo.
"""

SITE_URL = "https://trivium.ar"

ORG_NAME = "Trivium Center"
