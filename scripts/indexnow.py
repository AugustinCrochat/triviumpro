"""Avisa a los buscadores (Bing, Yandex y otros que usan IndexNow) de las URLs que cambiaron.

Uso:
    python3 scripts/indexnow.py            # páginas tocadas por el último commit
    python3 scripts/indexnow.py --all      # todas las URLs de sitemap.xml
    python3 scripts/indexnow.py --dry-run  # sólo lista lo que enviaría

La clave vive en /<clave>.txt en la raíz del sitio (IndexNow la verifica ahí),
así que hay que pushear antes de enviar. Bing alimenta a ChatGPT Search y Copilot.
"""

import glob
import json
import os
import re
import subprocess
import sys
import urllib.request

from site_config import SITE_URL

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENDPOINT = "https://api.indexnow.org/indexnow"


def find_key():
    for path in glob.glob(os.path.join(BASE_DIR, "*.txt")):
        name = os.path.basename(path)[:-4]
        if re.fullmatch(r"[0-9a-f]{32}", name):
            return name
    sys.exit("No hay archivo de clave <32 hex>.txt en la raíz")


def urls_from_sitemap():
    with open(os.path.join(BASE_DIR, "sitemap.xml"), encoding="utf-8") as f:
        return re.findall(r"<loc>([^<]+)</loc>", f.read())


def urls_from_last_commit():
    out = subprocess.run(
        ["git", "diff", "--name-only", "HEAD~1", "HEAD"],
        cwd=BASE_DIR, capture_output=True, text=True, check=True).stdout.split()
    urls = set()
    for path in out:
        if path == "index.html":
            urls.add(SITE_URL + "/")
        elif path.endswith("/index.html"):
            urls.add(f"{SITE_URL}/{path[:-len('index.html')]}")
    return sorted(urls)


def main():
    key = find_key()
    urls = urls_from_sitemap() if "--all" in sys.argv else urls_from_last_commit()
    print(f"{len(urls)} URLs")
    if "--dry-run" in sys.argv or not urls:
        for u in urls[:50]:
            print(" ", u)
        return
    host = SITE_URL.split("//", 1)[1]
    for i in range(0, len(urls), 10000):
        body = json.dumps({"host": host, "key": key,
                           "keyLocation": f"{SITE_URL}/{key}.txt",
                           "urlList": urls[i:i + 10000]}).encode()
        req = urllib.request.Request(
            ENDPOINT, data=body, headers={"Content-Type": "application/json; charset=utf-8",
                     "User-Agent": "trivium-pro-indexnow/1.0"})
        with urllib.request.urlopen(req, timeout=30) as r:
            print("IndexNow:", r.status)


if __name__ == "__main__":
    main()
