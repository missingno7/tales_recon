"""Integration-test proposer, NOT a model or a general recovery algorithm.

Replays independently authored bootstrap C for four IDs; deliberately fails the
fifth item to exercise cached non-convergence and continued queue processing.
"""
import json
from pathlib import Path
import sys

package=json.load(sys.stdin)
known={'ov14_F_03AE','ov14_F_03C2','ov04_F_00C4','ov04_F_00E6'}
source=(Path(__file__).parent/(package['id']+'.c')).read_text() if package['id'] in known else 'recovered() { return 0; }\n'
print(json.dumps(dict(source=source)))
