from pathlib import Path
pats=('regcall','register call','__reg','register parameter','D0/D1')
exts={'.md','.txt','.json','.c','.h','.cfg','.log'}
roots=[Path('docs'),Path('recovery'),Path('evidence'),Path('toolchain')]
n=0
for root in roots:
  if not root.exists(): continue
  for p in root.rglob('*'):
    if not p.is_file() or p.suffix.lower() not in exts: continue
    try: s=p.read_text(errors='replace')
    except Exception: continue
    hits=[(i+1,line[:240]) for i,line in enumerate(s.splitlines()) if any(q.lower() in line.lower() for q in pats)]
    if hits:
      print('FILE',p)
      for i,line in hits[:12]: print(f'{i}: {line}')
      n+=1
      if n>=30: raise SystemExit
