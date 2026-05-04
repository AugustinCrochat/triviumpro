import json
import re
import os

base_dir = '/home/ag/Documents/apps/web-trivium'
catalog_json_path = os.path.join(base_dir, 'data', 'catalog.json')

with open(catalog_json_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Collect assets in use
assets_in_use = set()
for p in data['products']:
    if 'image' in p and p['image']:
        assets_in_use.add(p['image'].strip('/'))
    if 'images' in p and p['images']:
        for img in p['images']:
            assets_in_use.add(img.strip('/'))
    if 'html_description' in p and p['html_description']:
        # Match all assets/ paths
        found = re.findall(r'assets/(?:img|pdf)/[^"\']+\.[a-zA-Z0-9]+', p['html_description'])
        for f_path in found:
            assets_in_use.add(f_path.strip('/'))

# Check categories for images (if any)
for c in data['categories']:
    if 'image' in c and c['image']:
        assets_in_use.add(c['image'].strip('/'))

# Check brands for logos
for b in data['brands']:
    if 'logo' in b and b['logo']:
        assets_in_use.add(b['logo'].strip('/'))

# Directories to clean
dirs_to_clean = [
    'assets/img/productos',
    'assets/pdf'
]

deleted_count = 0
for d in dirs_to_clean:
    full_dir = os.path.join(base_dir, d)
    if not os.path.exists(full_dir):
        continue
    
    for filename in os.listdir(full_dir):
        rel_path = os.path.join(d, filename)
        if rel_path.strip('/') not in assets_in_use:
            # Double check if it's referenced as absolute path in some fields
            if ('/' + rel_path) in assets_in_use:
                continue
            
            full_path = os.path.join(base_dir, rel_path)
            if os.path.isfile(full_path):
                os.remove(full_path)
                print(f"Deleted orphan asset: {rel_path}")
                deleted_count += 1

print(f"Total orphan assets deleted: {deleted_count}")
