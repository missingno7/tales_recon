"""Bounded retained startup producer audit, not a callee or acceptance proof.

Re-derive sources with the reviewed recipes, require a complete pinned input
inventory, and check both the ordinary and label-only +X3 object boundaries.
No original executable bytes are inputs to this audit.
"""
from names import to_mechanical
import json
from pathlib import Path
import runpy

from common import require, sha256
from repo_paths import canonical_path
from hunk import parse
from overlay_experiment import symbols, contribution
from resident_object import code_size

BASE = 'evidence/rules/startup-mechanical'
FACT = 'evidence/source-facts/resident-startup.json'
SDK = 'toolchain/installed/aztec-3.6a/SYS2/crt_src/_main.c'
PARTS = [['C_COMPILER', 0, 48], ['ASM', 48, 54],
         ['C_COMPILER', 54, 310], ['COMPILER_OWNED_DATA', 310, 312]]


def read(root, path):
    return (to_mechanical(canonical_path(root, path).read_bytes()) if str(path).startswith('src/') else canonical_path(root, path).read_bytes())


def index(rows, label):
    require(len({r['path'] for r in rows}) == len(rows), 'startup duplicate ' + label)
    return {r['path']: r for r in rows}


def commands(scope):
    profiles = ([('candidate', 'candidate', ''), ('x3', 'candidate', '+X3 '),
                 ('marked', 'marked', ''), ('root', 'root', ''), ('overlay', 'overlay', '')]
                if scope == 'abi' else
                [('marked', 'marked', '+X3 '), ('root', 'root', ''), ('overlay', 'overlay', '')])
    result = []
    for name, source, flags in profiles:
        result += [f'Old1:bin/cc -a {flags}-I Old1:include -o {name}.asm {source}.c <compiler-input.txt >{name}-cc.log',
                   f'Old1:bin/as -o {name}.o {name}.asm <compiler-input.txt >{name}-as.log']
    for name in (('candidate', 'x3', 'marked') if scope == 'abi' else ('marked',)):
        result.append(f'Old1:bin/ln -m -t -o {name}.exe root.o {name}.o +o1 overlay.o +o0 Old1:lib/c.lib >{name}-ln.log')
    return result, profiles


def source_views(root):
    recipes = Path(__file__).resolve().parents[1] / BASE
    views = runpy.run_path(str(recipes / 'source_recipe.py'))['source_views'](root)
    return runpy.run_path(str(recipes / 'abi_recipe.py'))['abi_views'](views)


def verify(root, *, control_base=BASE):
    inventory = json.loads(read(root, 'evidence/toolchain/aztec-3.6a.json'))
    pins = {'toolchain/installed/aztec-3.6a/' + d['manifest']['volume'] + '/' + e['path']: e['sha256']
            for d in inventory['disks'] if d['status'] == 'VALIDATED'
            for e in d['manifest']['entries'] if e['kind'] == 'file'}
    require(sha256(read(root, SDK)) == pins.get(SDK), 'startup SDK differs')
    # Execute reviewed program code from this tool's repository, never a recipe
    # selected by a receipt or by the candidate root supplied to this verifier.
    views = source_views(root)
    expected = {name + '.c': value.encode('ascii') for name, value in views.items()}
    expected['compiler-input.txt'] = b'\n'
    tools = {p for p in pins if p.startswith('toolchain/installed/aztec-3.6a/SYS1/include/')}
    tools.update('toolchain/installed/aztec-3.6a/SYS1/' + p
                 for p in ('bin/cc', 'bin/as', 'bin/ln', 'lib/c.lib'))
    fact = json.loads(read(root, FACT))
    require(fact == dict(schema_version=1, acceptance=False,
                         status='STAGED_SOURCE_OBJECT_FACT', id='resident_F_766C',
                         original=dict(hunk=0, start=30316, end=30628), code_end=30626,
                         sdk_source=SDK, profile='aztec36-x3',
                         mechanical_directory=BASE + '/abi', artifact_prefix='x3',
                         partition_directory=BASE + '/partition', artifact_partition_prefix='marked',
                         partitions=PARTS, original_filename='UNKNOWN', original_tu='UNKNOWN',
                         original_storage_ownership='UNKNOWN'), 'startup staged fact differs')
    controls = []
    for scope, prefix in [('abi', 'x3'), ('partition', 'marked')]:
        directory = control_base + '/' + scope
        receipt = json.loads(read(root, directory + '/receipt.json'))
        producing, profiles = commands(scope)
        require([s['command'] for s in receipt['steps']] == producing and
                all(s['returncode'] == 0 for s in receipt['steps']), 'startup producing recipe differs')
        inputs = index(receipt['tool_inputs'], 'tool input')
        require(set(inputs) == tools, 'startup tool/header inventory incomplete')
        for path, item in inputs.items():
            require(item['sha256'] == pins[path] == sha256(read(root, path)), 'startup tool/header pin differs')
        sources = index(receipt['source_files'], 'source input')
        require(set(sources) == set(expected), 'startup source inventory differs')
        for name, raw in expected.items():
            require(read(root, directory + '/' + name) == raw and
                    sources[name]['sha256'] == sha256(raw), 'startup source does not rederive')
        artifacts = index(receipt['artifacts'], 'artifact')
        needed = set(expected)
        for name, _, _ in profiles:
            needed.update(name + suffix for suffix in ('.asm', '.o', '-cc.log', '-as.log'))
        for name in (('candidate', 'x3', 'marked') if scope == 'abi' else ('marked',)):
            needed.update(name + suffix for suffix in ('.exe', '.sym', '-ln.log'))
        require(needed <= set(artifacts), 'startup required artifact missing')
        for name, item in artifacts.items():
            require(Path(name).name == name and '/' not in name and '\\' not in name,
                    'startup artifact path differs')
            raw = read(root, directory + '/' + name)
            require(sha256(raw) == item['sha256'] and len(raw) == item['size'], 'startup artifact differs')
        obj = read(root, directory + '/' + prefix + '.o')
        require(obj[:2] == b'AJ' and len(obj) >= 22 and
                [int.from_bytes(obj[n:n + 4], 'big') for n in (10, 14, 18)] == [312, 0, 0],
                'startup complete object storage differs')
        blob = read(root, directory + '/' + prefix + '.exe')
        model = parse(blob)
        sm = symbols(read(root, directory + '/' + prefix + '.sym').decode('ascii'))
        start = sm[(0, '_recovered')]
        require(start == sm[(0, '_main')] + code_size(canonical_path(root, directory + '/root.o')) and
                sm[(0, '_segload')] == start + 312, 'startup linked object bounds differ')
        require(not any(r['source_hunk'] == 0 and r['source_offset'] < start + 312 and
                        r['source_offset'] + r['width'] > start for r in model['relocations']),
                'startup unexpected CODE relocation')
        raw = contribution(blob, model, 0, start, 312)
        require(raw[310:] == b'*\0', 'startup literal differs')
        controls.append((raw, sm, start))
    raw, sm, start = controls[0]
    marked, ms, mst = controls[1]
    require(raw == marked, 'startup marker changes CODE')
    require([ms[(0, n)] - mst for n in ('_startup_asm_begin', '_startup_asm_end')] == [48, 54],
            'startup marker span differs')
    bindings = lambda m: {k: v for k, v in m.items() if k[1].startswith(('_G_h01_', '_F_h00_', '_F_h03_'))}
    require(bindings(sm) == bindings(ms), 'startup marker changes bindings')
    return dict(status='VERIFIED_STARTUP_PRODUCER_ONLY', acceptance=False,
                code_bytes=312, c_compiler_bytes=304, sdk_asm_bytes=6, compiler_literal_bytes=2,
                source_sha256=sha256(expected['candidate.c']), partitions=PARTS,
                remaining_gate='Independent complete callees, original field identities, fresh unchanged compilation and mixed code/literal admission',
                original_storage_ownership='UNKNOWN')


if __name__ == '__main__':
    print(json.dumps(verify(Path(__file__).resolve().parents[1]), indent=2))
