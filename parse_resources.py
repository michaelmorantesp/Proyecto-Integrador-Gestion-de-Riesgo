import json
from bs4 import BeautifulSoup

print('============= IPYNB =============')
with open('09_proyecto_consolidado_final.ipynb', encoding='utf-8') as f:
    nb = json.load(f)
    for i, cell in enumerate(nb.get('cells', [])):
        if cell['cell_type'] == 'markdown':
            content = ''.join(cell['source']).replace('\n', ' ')
            if len(content) > 0:
                print(f"[MD {i}]: {content[:100]}...")
        elif cell['cell_type'] == 'code':
            lines = [ln for ln in cell['source'] if 'def ' in ln or 'import ' in ln or 'plot' in ln]
            if lines:
                print(f"[CODE {i}]: {lines[0]}")

print('\n============= HTML SECCION 6 =============')
try:
    with open('Riesgo_Clases-VI-y-VII.html', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')
        headers = soup.find_all(['h1', 'h2', 'h3', 'h4'])
        for h in headers:
            if '6' in h.text or 'secci' in h.text.lower():
                print('HEADER:', h.text)
                sibling = h.find_next_sibling()
                for _ in range(5):
                    if sibling:
                        print(' ->', sibling.text[:100])
                        sibling = sibling.find_next_sibling()
except Exception as e:
    print('Error HTML', e)
