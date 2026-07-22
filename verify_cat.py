# -*- coding: utf-8 -*-
import sys
import importlib.util
from collections import Counter

spec = importlib.util.spec_from_file_location('tc', 'tiendas_catalogo.py')
tc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tc)

checks = ['1374','1387','1419','1420','1713','1714','1864','3784','3793','3920','4778']
for d in checks:
    v = tc.TIENDAS_BY_DET.get(d, 'NO ENCONTRADO')
    print(f'{d}: {v}')

print('Total:', len(tc.TIENDAS))
dups = {d: c for d, c in Counter(t[0] for t in tc.TIENDAS).items() if c > 1}
print('Dups:', dups if dups else 'Ninguno')
