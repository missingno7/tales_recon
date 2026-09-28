from pathlib import Path
p=Path('experiments/worker-ffp-link/ov11_F_5FB2.c')
print('=== prior FFP candidate ===')
print(p.read_text() if p.exists() else 'missing')
d=Path('docs/source-shape-search.md').read_text(errors='replace').splitlines()
print('=== relevant docs headings/config ===')
for i,l in enumerate(d):
 if 'Schema v2' in l or 'manifest-v2' in l or 'with-m-lib' in l or 'options' in l or 'profile' in l and i<100:
  print(f'-- {i+1} --')
  print('\n'.join(f'{j+1}: {d[j]}' for j in range(max(0,i-3),min(len(d),i+22))))
