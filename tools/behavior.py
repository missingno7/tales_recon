"""Read-only behavior-coverage report derived from existing ledgers.

Matching accounting answers "which bytes are independently produced". This
report answers the port-oriented questions from the same evidence, without
storing any new state:

* code by proof class per node (exact C, assembly, typed code data, pinned
  runtime library, unresolved);
* every unresolved function candidate and its recorded blocker;
* the platform surface game code reaches: pinned runtime/OS members called
  from non-runtime code, and functions that address custom-chip/CIA
  registers absolutely;
* data-model and readability state of the accepted source.

Inputs: evidence/hybrid/accounting.json, evidence/functions/ledger.json,
recovery/ledger.json, docs/blockers.json and src/. The heuristics (absolute
hardware operands, mechanical names) are lower bounds, not proofs.
"""
import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]

CODE_CLASSES = {
    'RECOVERED_C': 'exact_c',
    'BEHAVIORAL_C': 'behavioral',
    'RECOVERED_ASM': 'asm',
    'RECONSTRUCTED_ASM': 'asm',
    'TYPED_CODE_DATA': 'code_data',
    'COMPILER_OWNED_DATA': 'code_data',
    'CLASSIFIED_PADDING': 'code_data',
    'PINNED_RUNTIME': 'runtime',
    'RAW_ORACLE_DEBT': 'unresolved',
}
HARDWARE = re.compile(r'\$(?:00)?(?:dff[0-9a-f]{3}|bf[de][0-9a-f]{3})\b', re.I)
MECHANICAL_GLOBAL = re.compile(r'\bG_h\d\d_[0-9A-F]{4}\b')
MECHANICAL_CALLEE = re.compile(r'\bF_h\d\d_[0-9A-F]{4}\b')
EXTERN = re.compile(r'\bextern\s+([^;{}()]+?)\s*;')
ENTRY = re.compile(r"^[a-z ]*[*]*recovered *[(]", re.M)


def node_of(hunk):
    return {0: 'resident', 1: 'resident.data', 2: 'resident.bss'}.get(hunk, 'ov%02d' % hunk)


def load(root):
    read = lambda p: json.loads((root / p).read_text())
    return (read('evidence/hybrid/accounting.json'), read('evidence/functions/ledger.json'),
            read('recovery/ledger.json'), read('docs/blockers.json').get('function_blockers', {}))


def report(root=ROOT):
    accounting, census, ledger, blockers = load(root)
    ranges = accounting['ranges']
    by_hunk = defaultdict(list)
    for r in ranges:
        by_hunk[r['hunk']].append(r)

    def overlap(hunk, start, end):
        result = Counter()
        for r in by_hunk[hunk]:
            lo, hi = max(start, r['start']), min(end, r['end'])
            if lo < hi:
                result[r['category']] += hi - lo
        return result

    code = defaultdict(Counter)
    data = Counter()
    for r in ranges:
        size = r['end'] - r['start']
        if r['hunk'] == 1:
            data['typed' if r['category'] == 'RECOVERED_DATA' else
                 'runtime' if r['category'] == 'PINNED_RUNTIME' else 'raw'] += size
        else:
            code[node_of(r['hunk'])][CODE_CLASSES[r['category']]] += size

    runtime_at = {}
    for r in ranges:
        if r['category'] == 'PINNED_RUNTIME':
            runtime_at.setdefault(r['hunk'], []).append(r)

    def runtime_member(hunk, offset):
        return next((r.get('id') for r in runtime_at.get(hunk, ()) if r['start'] <= offset < r['end']), None)

    functions = census['functions']
    unresolved, hardware = [], []
    services = defaultdict(set)
    states = Counter()
    for f in functions:
        bytes_by = overlap(f['hunk'], f['start'], f['end'])
        cls = CODE_CLASSES[bytes_by.most_common(1)[0][0]] if bytes_by else 'unresolved'
        states[(node_of(f['hunk']), cls)] += 1
        if cls == 'runtime':
            continue
        if cls == 'unresolved' and f['size']:
            blocker = blockers.get(f['id'], {}).get('reason', '')
            unresolved.append(dict(id=f['id'], size=f['size'], extent=f['extent_status'],
                                   blocker=blocker.split(':', 1)[0] if blocker else None))
        ops = ' '.join(i['operands'] for i in f['instructions'])
        if HARDWARE.search(ops):
            hardware.append(f['id'])
        for c in f['direct_callees']:
            member = runtime_member(c['hunk'], c['offset'])
            if member:
                services[member].add(f['id'])

    sources = sorted((root / 'src/recovered').rglob('*.c'))
    texts = [p.read_text(encoding='ascii', errors='replace') for p in sources]
    views = defaultdict(set)
    for text in texts:
        for decl in EXTERN.findall(text):
            name = re.search(r'(\w+)(?:\s*\[[^\]]*\])*\s*$', decl)
            if name and MECHANICAL_GLOBAL.fullmatch(name[1]):
                views[name[1]].add(re.sub(r'\s+', ' ', decl))
    readability = dict(
        c_sources=len(sources),
        mechanically_named_entries=sum(1 for t in texts if ENTRY.search(t)),
        distinct_mechanical_globals=len({g for t in texts for g in MECHANICAL_GLOBAL.findall(t)}),
        globals_with_conflicting_views=sum(1 for v in views.values() if len(v) > 1),
        distinct_mechanical_callees=len({g for t in texts for g in MECHANICAL_CALLEE.findall(t)}),
        shared_headers=len(list((root / 'include').glob('*.h'))),
    )
    totals = accounting['totals']
    return dict(
        code={k: dict(v) for k, v in sorted(code.items())},
        data_hunk=dict(data), bss_untyped=accounting.get('zero_fill_debt'),
        function_states={'%s/%s' % k: v for k, v in sorted(states.items())},
        unresolved=sorted(unresolved, key=lambda x: x['id']),
        platform_services={k: sorted(v) for k, v in sorted(services.items(), key=lambda kv: (-len(kv[1]), kv[0]))},
        absolute_hardware_access=sorted(hardware),
        readability=readability,
        ledger_counts={k: len(v) for k, v in ledger.items() if isinstance(v, dict)},
        file_bytes=totals['file_size'],
    )


def render(r):
    out = ['Code bytes by proof class (CODE hunks)', '']
    cols = ['exact_c', 'behavioral', 'asm', 'code_data', 'runtime', 'unresolved']
    out.append('| Node | ' + ' | '.join(cols) + ' |')
    out.append('| --- |' + ' ---: |' * len(cols))
    total = Counter()
    for node, row in r['code'].items():
        total.update(row)
        out.append('| %s | ' % node + ' | '.join(str(row.get(c, 0)) for c in cols) + ' |')
    out.append('| total | ' + ' | '.join(str(total.get(c, 0)) for c in cols) + ' |')
    d = r['data_hunk']
    out += ['', 'Resident DATA: %d typed, %d runtime, %d raw. BSS: %s bytes with no typed layout.'
            % (d.get('typed', 0), d.get('runtime', 0), d.get('raw', 0), r['bss_untyped']), '']
    nodes = sorted({k.split('/')[0] for k in r['function_states']})
    out.append('Function candidates by dominant class: ' + '; '.join(
        '%s %s' % (n, ' '.join('%s=%d' % (k.split('/')[1], v) for k, v in r['function_states'].items()
                               if k.split('/')[0] == n)) for n in nodes))
    out += ['', 'Unresolved non-empty function candidates (%d):' % len(r['unresolved'])]
    for u in r['unresolved']:
        out.append('  %-18s %5d %-9s %s' % (u['id'], u['size'], u['extent'][:9], u['blocker'] or ''))
    out += ['', 'Platform services reached from non-runtime code (%d members):' % len(r['platform_services'])]
    for name, callers in r['platform_services'].items():
        out.append('  %-26s %3d callers' % (name, len(callers)))
    out += ['', 'Absolute custom-chip/CIA access (%d functions): %s'
            % (len(r['absolute_hardware_access']), ' '.join(r['absolute_hardware_access'])), '']
    out.append('Readability: ' + ', '.join('%s=%s' % kv for kv in r['readability'].items()))
    return '\n'.join(out)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    ap.add_argument('--json', action='store_true')
    args = ap.parse_args(argv)
    r = report()
    print(json.dumps(r, indent=2) if args.json else render(r))


if __name__ == '__main__':
    main()
