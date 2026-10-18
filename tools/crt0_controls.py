"""Replay complete CRT0 producer and natural COMMON-order controls.

This rule proves the behavior of pinned candidate tools, not original game
ownership, release, source filename, or natural resident layout. No acceptance.
"""
from names import read_source
import json
from pathlib import Path

from common import require, sha256
from repo_paths import canonical_path
from resident_mixed import pinned
from hunk import parse
from overlay_experiment import symbols, contribution, relocation_profile

BASE = 'evidence/rules/crt0-controls'
SDK = 'toolchain/installed/aztec-3.6a/SYS2/crt_src/crt0.a68'
PREFIX = 'toolchain/installed/aztec-3.6a/'
TOOLS = {PREFIX + p for p in ('SYS1/bin/cc', 'SYS1/bin/as', 'SYS1/bin/ln',
                             'SYS2/bin/lb', 'SYS1/lib/c.lib')}
FIELDS = (4, 8, 16, 30, 38, 78, 96)


def read(root, path):
    return (read_source(root, path, names_root=None) if str(path).startswith('src/') else canonical_path(root, path).read_bytes())


def commands(scope):
    names = ('main', 'provider') if scope == 'allocation' else ('main',)
    result = ['Old2:bin/lb >extract.log Old1:lib/c.lib -x crt0' +
              (' _close' if scope == 'order' else ''),
              'Old1:bin/as -o crt0-source.o crt0-source.asm >crt0-source-as.log']
    for name in names:
        result += [f'Old1:bin/cc -a +X3 -o {name}.asm {name}.c <compiler-input.txt >{name}-cc.log',
                   f'Old1:bin/as -o {name}.o {name}.asm <compiler-input.txt >{name}-as.log']
    for variant in (('base', 'shifted') if scope == 'allocation' else ('dos-first',)):
        for kind in ('lib', 'source'):
            obj = 'crt0.o' if kind == 'lib' else 'crt0-source.o'
            before = {'base': '', 'shifted': 'provider.o ', 'dos-first': '_close.o '}[variant]
            label = variant + '-' + kind
            result.append(f'Old1:bin/ln -m -t -o {label}.exe {before}{obj} +o1 main.o +o0 Old1:lib/c.lib >{label}-ln.log')
    return result


def index(rows, label):
    require(len({r['path'] for r in rows}) == len(rows), 'CRT0 duplicate ' + label)
    return {r['path']: r for r in rows}


def verify(root):
    sdk = pinned(root, SDK)
    library = pinned(root, PREFIX + 'SYS1/lib/c.lib')
    ordinary = []
    controls = []
    for scope in ('allocation', 'order'):
        directory = BASE + '/' + scope
        receipt = json.loads(read(root, directory + '/receipt.json'))
        require([s['command'] for s in receipt['steps']] == commands(scope) and
                all(s['returncode'] == 0 for s in receipt['steps']), 'CRT0 producing recipe differs')
        inputs = index(receipt['tool_inputs'], 'tool input')
        require(set(inputs) == TOOLS, 'CRT0 tool inventory incomplete')
        for path, item in inputs.items():
            require(sha256(pinned(root, path)) == item['sha256'], 'CRT0 producer pin differs')
        expected = {'crt0-source.asm': sdk, 'compiler-input.txt': b'\n',
                    'main.c': b'main(argc,argv) int argc; char **argv; { return 0; }\n'}
        if scope == 'allocation':
            expected['provider.c'] = b'long control_initialized = 1;\nlong control_common[2];\n'
        sources = index(receipt['source_files'], 'source')
        require(set(sources) == set(expected), 'CRT0 source inventory differs')
        for name, raw in expected.items():
            require(read(root, directory + '/' + name) == raw and
                    sources[name]['sha256'] == sha256(raw), 'CRT0 source does not rederive')
        artifacts = index(receipt['artifacts'], 'artifact')
        variants = ('base', 'shifted') if scope == 'allocation' else ('dos-first',)
        needed = set(expected) | {'crt0.o', 'crt0-source.o', 'crt0-source-as.log', 'extract.log'}
        for name in (('main', 'provider') if scope == 'allocation' else ('main',)):
            needed.update(name + suffix for suffix in ('.asm', '.o', '-cc.log', '-as.log'))
        if scope == 'order':
            needed.add('_close.o')
        for variant in variants:
            for kind in ('lib', 'source'):
                needed.update(variant + '-' + kind + suffix for suffix in ('.exe', '.sym', '-ln.log'))
        require(needed <= set(artifacts), 'CRT0 required artifact missing')
        for name, item in artifacts.items():
            require(Path(name).name == name and '/' not in name and '\\' not in name,
                    'CRT0 artifact path differs')
            raw = read(root, directory + '/' + name)
            require(sha256(raw) == item['sha256'] and len(raw) == item['size'], 'CRT0 artifact differs')
        for name in ('crt0.o', 'crt0-source.o'):
            raw = read(root, directory + '/' + name)
            require(raw[:2] == b'AJ' and [int.from_bytes(raw[n:n+4], 'big') for n in (10, 14, 18)] == [122, 0, 0],
                    'CRT0 complete object storage differs')
            if name == 'crt0.o':
                require(library.count(raw) == 1, 'CRT0 library membership differs')
        if scope == 'order':
            obj = read(root, directory + '/_close.o')
            require(library.count(obj) == 1 and
                    [int.from_bytes(obj[n:n+4], 'big') for n in (10, 14, 18)] == [12, 0, 0],
                    'CRT0 earlier DOS consumer differs')
        for variant in variants:
            blob = read(root, directory + '/' + variant + '-lib.exe')
            require(blob == read(root, directory + '/' + variant + '-source.exe'),
                    'CRT0 whole source/library executables differ')
            model = parse(blob)
            maps = [symbols(read(root, directory + '/' + variant + '-' + kind + '.sym').decode('ascii'))
                    for kind in ('lib', 'source')]
            require(maps[0] == maps[1], 'CRT0 source/library symbols differ')
            sm = maps[0]
            start = sm[(0, '.begin')]
            require(sm[(0, '_geta4')] == start + 114 and sm[(0, '_segload')] == start + 122,
                    'CRT0 complete linked boundary differs')
            raw = contribution(blob, model, 0, start, 122)
            h1 = next(h for h in model['hunks'] if h['number'] == 1)
            end, allocation = h1['initialized_size'], h1['allocated_size']
            require(sm[(1, '__H1_end')] == sm[(2, '__H2_org')] == end and
                    sm[(2, '__H2_end')] == allocation, 'CRT0 COMMON hunk bounds differ')
            values = [end-32766, end-32766, (allocation-end)//4-1,
                      sm[(2, '__savsp')]-32766, sm[(2, '_SysBase')]-32766,
                      sm[(2, '_DOSBase')]-32766, sm[(0, '__main')]-start-96]
            require((allocation-end) % 4 == 0 and
                    [int.from_bytes(raw[n:n+2], 'big', signed=True) for n in FIELDS] == values,
                    'CRT0 independently resolved fields differ')
            require(relocation_profile(model, 0, start, 122) ==
                    [dict(offset=116, type='HUNK_RELOC32', width=4, target_hunk=1, addend=32766)],
                    'CRT0 relocation differs')
            require(raw[102:114] == b'dos.library\0', 'CRT0 SDK literal differs')
            ordinary.append(bytes(b for n, b in enumerate(raw) if not any(f <= n < f+2 for f in FIELDS)))
            offsets = {name: sm[(2, name)] for name in ('__savsp', '_SysBase', '_DOSBase')}
            wanted = {'base': (36, 112, 36, 40, 44), 'shifted': (40, 124, 48, 52, 56),
                      'dos-first': (36, 112, 40, 44, 36)}[variant]
            require((end, allocation, *offsets.values()) == wanted, 'CRT0 measured allocation/order differs')
            controls.append(dict(variant=variant, initialized=end, allocated=allocation,
                                 common_offsets=offsets, fields=dict(zip(map(str, FIELDS), values)),
                                 executable_sha256=sha256(blob)))
    require(len(set(ordinary)) == 1 and len(ordinary[0]) == 108,
            'CRT0 non-field bytes change between contexts')
    return dict(schema_version=1, status='VERIFIED_CRT0_PRODUCER_AND_COMMON_ORDER', acceptance=False,
                accounting_promoted=False, object_code_bytes=122, ordinary_bytes=108,
                controls=controls, original_storage_ownership='UNKNOWN', original_object_order='UNKNOWN',
                exact_historical_release='UNKNOWN',
                next_gate='Bind complete original CRT0 against canonical entry, startup, saved-stack and base identities; then review runtime admission separately.')


if __name__ == '__main__':
    print(json.dumps(verify(Path(__file__).resolve().parents[1]), indent=2))
