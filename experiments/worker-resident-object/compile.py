from pathlib import Path
import json
import sys
sys.path.insert(0, str(Path('tools').resolve()))
from compiler_oracle import compile_many
source=Path('experiments/worker-resident-object/probe.c').read_text(encoding='ascii')
res=compile_many([dict(source=source,profile='aztec36',extra_libraries=['m.lib'])])
print(json.dumps(res[0],indent=2))
