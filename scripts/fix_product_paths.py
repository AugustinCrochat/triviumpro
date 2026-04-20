import os
from pathlib import Path

PRODUCT_DIR = Path("producto")

def main():
    print("▶ Corrigiendo rutas de descripción en páginas de productos...")
    
    # Nuevo fragmento de script que corrige las rutas dinámicamente
    fix_script = """
  if (p.html_description) {
    const wrap = document.getElementById('pd-wrap');
    const descEl = document.createElement('div');
    descEl.className = 'rich-html';
    descEl.style.gridColumn = '1 / -1';
    descEl.style.marginTop = '20px';
    
    // Fix relative paths in WooCommerce HTML
    let html = p.html_description;
    const root = rootPath();
    if (root) {
      html = html.replace(/href="assets\\//g, `href="${root}assets/`);
      html = html.replace(/src="assets\\//g, `src="${root}assets/`);
    }
    descEl.innerHTML = html;
    wrap.appendChild(descEl);
  }
"""

    old_fragment = """
  if (p.html_description) {
    const wrap = document.getElementById('pd-wrap');
    const descEl = document.createElement('div');
    descEl.className = 'rich-html';
    descEl.style.gridColumn = '1 / -1';
    descEl.style.marginTop = '20px';
    descEl.innerHTML = p.html_description;
    wrap.appendChild(descEl);
  }
"""

    count = 0
    for root, dirs, files in os.walk(PRODUCT_DIR):
        if "index.html" in files:
            file_path = Path(root) / "index.html"
            content = file_path.read_text(encoding="utf-8")
            if old_fragment in content:
                new_content = content.replace(old_fragment, fix_script)
                file_path.write_text(new_content, encoding="utf-8")
                count += 1
                
    print(f"✔ Se actualizaron {count} archivos de producto.")

if __name__ == "__main__":
    main()
