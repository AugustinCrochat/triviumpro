import json
import os
import re
from urllib.request import urlopen, Request
from pathlib import Path
import unicodedata

CATALOG = "data/catalog.json"
JS_FILE = "data/catalog.js"
PDF_DIR = Path("assets/pdf")
PDF_DIR.mkdir(parents=True, exist_ok=True)

def clean_name(name: str) -> str:
    name = unicodedata.normalize("NFD", name).encode("ascii", "ignore").decode()
    name = name.lower()
    name = re.sub(r"[^a-z0-9._-]+", "-", name)
    return name

def download(url: str, dest: Path) -> bool:
    if dest.exists() and dest.stat().st_size > 0:
        return True
    try:
        req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urlopen(req, timeout=30) as r:
            data = r.read()
        dest.write_bytes(data)
        print(f"  Downloaded: {dest.name}")
        return True
    except Exception as e:
        print(f"  Error downloading {url}: {e}")
        return False

def main():
    with open(CATALOG, "r", encoding="utf-8") as f:
        cat = json.load(f)
    
    # Busca todas las URLs que contengan wp-content y terminen en .pdf (case insensitive)
    url_pattern = re.compile(r'https?://[^\s"\'<>]+wp-content[^\s"\'<>]+\.pdf', re.IGNORECASE)
    
    downloaded = {}
    
    for p in cat["products"]:
        if "html_description" in p and p["html_description"]:
            urls = url_pattern.findall(p["html_description"])
            for url in urls:
                filename = clean_name(url.split("/")[-1])
                local_path = f"assets/pdf/{filename}"
                dest = PDF_DIR / filename
                
                if url not in downloaded:
                    if download(url, dest):
                        downloaded[url] = local_path
                    else:
                        downloaded[url] = None
                
                if downloaded[url]:
                    p["html_description"] = p["html_description"].replace(url, downloaded[url])
    
    with open(CATALOG, "w", encoding="utf-8") as f:
        json.dump(cat, f, indent=2, ensure_ascii=False)
        
    with open(JS_FILE, "w", encoding="utf-8") as f:
        f.write("window.CATALOG_DATA = ")
        json.dump(cat, f, ensure_ascii=False)
        f.write(";")
        
    print(f"Total procesado: {len(downloaded)} PDFs únicos.")

if __name__ == "__main__":
    main()
