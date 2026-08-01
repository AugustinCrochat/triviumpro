"""Configuración compartida de los generadores.

SITE_URL es el dominio canónico: entra en los canonical, los og:url, el
JSON-LD, el sitemap y los links del feed de Meta. Estaba repetido en cuatro
scripts, así que migrar de dominio eran cuatro ediciones que podían quedar
desincronizadas — y una sola mal puesta manda a Google señales contradictorias.

Para migrar a pro.trivium.ar se cambia acá y se regenera todo.
"""

SITE_URL = "https://trivium.ar"

ORG_NAME = "Trivium Center"


def load_chrome(root_val):
    """Header y footer cacheados, con los '../' de esta página ya resueltos.

    Devuelve (None, None) si todavía no se generó el caché, para que los
    generadores sigan funcionando sin depender de Playwright.
    Se regenera con scripts/generate_chrome.py.
    """
    import json
    import os

    path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                        'data', 'chrome.json')
    if not os.path.exists(path):
        return None, None
    with open(path, encoding='utf-8') as f:
        data = json.load(f)
    token = data['root_token']
    return (data['header'].replace(token, root_val),
            data['footer'].replace(token, root_val))
