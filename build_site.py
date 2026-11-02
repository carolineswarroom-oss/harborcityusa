#!/usr/bin/env python3
"""Rebuild the deployable standalone page from catalog.json and index.template.html."""
from pathlib import Path
import json
root=Path(__file__).parent
catalog=json.loads((root/'catalog.json').read_text(encoding='utf-8'))
raw=json.dumps(catalog,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')
html=(root/'index.template.html').read_text(encoding='utf-8').replace('__CATALOG_JSON__',raw)
(root/'index.html').write_text(html,encoding='utf-8')
print(f'Built index.html with {len(catalog)} KDP book records')
