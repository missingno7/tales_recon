from pathlib import Path
for name in ['experiments/worker-resident-regabi/report.md','experiments/worker-ffp-link/report.md']:
 p=Path(name)
 print('\n===',name,'exists=',p.exists(),'===')
 if p.exists(): print(p.read_text(errors='replace')[:10000])
for root in ['experiments/worker-resident-regabi','experiments/worker-ffp-link']:
 p=Path(root)
 if p.exists():
  print('\nFILES',root)
  for q in p.iterdir():
   if q.is_file(): print(q.name, q.stat().st_size)
