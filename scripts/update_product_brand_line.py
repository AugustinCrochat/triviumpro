import os, re

producto_dir = '/home/ag/Documents/apps/web-trivium/producto'

old_brand_line = '      <div class="brand-line">\n        <span class="chip chip--accent">${brand.name}</span>\n        ${ribbons}\n      </div>'

new_brand_line = '''      <div class="brand-line">
        ${brand.logo
          ? `<a class="brand-chip" href="${rootPath()}marca/${brand.slug}/" title="${brand.name}"><img src="${rootPath()}${brand.logo}" alt="${brand.name}"></a>`
          : `<span class="chip chip--accent">${brand.name}</span>`}
        ${ribbons}
      </div>'''

old_marca_row = '        <div class="row"><span>Marca</span><b>${brand.name}</b></div>'
new_marca_row = '        <div class="row"><span>Marca</span><b><a href="${rootPath()}marca/${brand.slug}/" style="color:var(--text);text-decoration:underline;text-underline-offset:3px">${brand.name}</a></b></div>'

updated = 0
skipped = 0
for root, dirs, files in os.walk(producto_dir):
    for fn in files:
        if fn == 'index.html':
            path = os.path.join(root, fn)
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            if old_brand_line in content:
                content = content.replace(old_brand_line, new_brand_line)
                content = content.replace(old_marca_row, new_marca_row)
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(content)
                updated += 1
            else:
                skipped += 1

print(f'Updated: {updated}, skipped: {skipped}')
