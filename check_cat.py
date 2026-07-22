import tiendas_catalogo as tc
from collections import Counter

checks = ['1420','1714','1864','3001','3758','3784','3793','3920','4778','3884','2362','1191','2290','4180']
for det in checks:
    v = tc.TIENDAS_BY_DET.get(det, 'NO ENCONTRADO')
    print(f'{det}: {v}')

print('---')
print('Total tiendas:', len(tc.TIENDAS))

dets = [d for d, n in tc.TIENDAS]
dups = {d: c for d, c in Counter(dets).items() if c > 1}
print('Duplicados:', dups if dups else 'Ninguno')
