from pathlib import Path
p=Path('docs/blockers.json')
for i,l in enumerate(p.read_text().splitlines(),1):
  if 245<=i<=265: print(f'{i}: {l}')
for root in [Path('experiments/work'), Path('experiments/fleet')]:
  if root.exists():
    for q in root.rglob('*'):
      if q.is_file() and ('ov11_F_5FB2' in q.name or 'ov11_F_5FB2' in str(q)):
        print('PATH',q)
        if q.suffix.lower() in ('.md','.txt','.json','.c'):
          try:
            s=q.read_text(errors='replace')
            if 'ov11_F_5FB2' in s or q.suffix=='.c': print(s[:7000])
          except Exception: pass
