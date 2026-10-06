"""Whole provider controls only; no original ownership or accounting admission."""
import json
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'tools'))
from common import require, sha256
from repo_paths import canonical_path
from hunk import parse
from overlay_experiment import symbols

DIRECTORY = 'evidence/rules/runtime-vars-variant'


def replay(root=ROOT):
    root = Path(root).resolve()
    read = lambda p: canonical_path(root, p).read_bytes()
    provenance = json.loads(read('evidence/rules/runtime-vars/source-provenance.json'))
    archive = read(provenance['archive'])
    require(sha256(archive) == provenance['archive_sha256'], 'SDK archive differs')
    parts = [p.split('\n', 1)[1] for p in archive.decode('ascii').split('\f') if p.strip().startswith('vars.c\n')]
    require(len(parts) == 1 and sha256(parts[0].encode('ascii')) == provenance['source_sha256'], 'SDK vars source differs')
    source = parts[0]
    name_line = 'char *_detach_name = 0;\t\t\t/* for DETACHED programs */\n'
    dir_line = 'long _detach_curdir = 0;\n'
    require(source.count(name_line) == source.count(dir_line) == 1, 'SDK initializer selection differs')
    variants = dict(removed=source.replace(name_line, '').replace(dir_line, ''),
        common=source.replace(name_line, 'char *_detach_name;\t\t\t/* for DETACHED programs */\n').replace(dir_line, 'long _detach_curdir;\n'))
    receipt = json.loads(read(DIRECTORY + '/receipt.json'))
    commands = []
    for name, text in variants.items():
        require(read(DIRECTORY + '/' + name + '.c') == text.encode('ascii'), 'variant source does not rederive')
        commands += [f'Old1:bin/cc -a +X3 -I Old1:include -o {name}.asm {name}.c <compiler-input.txt >{name}-cc.log',
                     f'Old1:bin/as -o {name}.o {name}.asm >{name}-as.log']
    for name in ('root1', 'root2'): commands.append(f'Old1:bin/as -o {name}.o {name}.asm >{name}-as.log')
    for variant in variants:
        for root_name in ('root1', 'root2'):
            label = variant + '-' + root_name
            commands.append(f'Old1:bin/ln -m -t -o {label}.exe {root_name}.o {variant}.o >{label}-ln.log')
    require([s['command'] for s in receipt['steps']] == commands and all(s['returncode'] == 0 for s in receipt['steps']),
            'complete producing commands differ or failed')
    inventory = json.loads(read('evidence/toolchain/aztec-3.6a.json'))
    pins = {'toolchain/installed/aztec-3.6a/' + d['manifest']['volume'] + '/' + e['path']: e['sha256']
            for d in inventory['disks'] if d['status'] == 'VALIDATED'
            for e in d['manifest']['entries'] if e['kind'] == 'file'}
    required = {p for p in pins if p.startswith('toolchain/installed/aztec-3.6a/SYS1/include/')}
    required |= {'toolchain/installed/aztec-3.6a/SYS1/bin/' + t for t in ('cc', 'as', 'ln')}
    require(required <= {t['path'] for t in receipt['tool_inputs']}, 'complete compiler/header inputs missing')
    for t in receipt['tool_inputs']:
        require(t['path'] in pins and sha256(read(t['path'])) == pins[t['path']] == t['sha256'], 'pinned input differs')
    for collection in ('source_files', 'artifacts'):
        for item in receipt[collection]:
            require(sha256(read(DIRECTORY + '/' + item['path'])) == item['sha256'], 'retained artifact differs')
    rows = []
    expected_names = {'_SysBase','_DOSBase','_MathBase','_MathTransBase','_MathIeeeDoubBasBase',
        '_MathIeeeDoubTransBase','__savsp','__stkbase','_errno','_Enable_Abort','__argc','__arg_len',
        '__argv','__arg_lin','_WBenchMsg','__devtab','__oldtrap','__trapaddr'}
    for variant, common_size in [('removed', 64), ('common', 72)]:
        obj = read(DIRECTORY + '/' + variant + '.o')
        require(obj[:2] == b'AJ' and [int.from_bytes(obj[p:p+4], 'big') for p in (10,14,18)] == [0,2,0],
                'whole provider object sizes differ')
        wanted = expected_names | ({'__detach_name','__detach_curdir'} if variant == 'common' else set())
        for root_name, prefix in [('root1', b''), ('root2', bytes.fromhex('000100020003'))]:
            expected_root = '\tpublic .begin\n.begin\n\trts\n' + ('\tdseg\n\tdc.w 1,2,3\n' if prefix else '')
            require(read(DIRECTORY + '/' + root_name + '.asm') == expected_root.encode('ascii'), 'authored root differs')
            label = variant + '-' + root_name
            raw = read(DIRECTORY + '/' + label + '.exe'); model = parse(raw)
            sm = symbols(read(DIRECTORY + '/' + label + '.sym').decode('ascii'))
            data = next(h for h in model['hunks'] if h['number'] == 1)
            payload = prefix + bytes.fromhex('0014') + (bytes(2) if not prefix else b'')
            require(not model['relocations'] and data['initialized_size'] == len(payload) and
                    raw[data['content_offset']:data['content_offset'] + len(payload)] == payload,
                    'complete initialized DATA differs')
            require(data['zero_fill_size'] == common_size and data['allocated_size'] == len(payload) + common_size,
                    'complete COMMON allocation differs')
            # The map labels COMMON as H2 but its small-data coordinates start
            # after initialized H1; the load file reserves COMMON in H1's tail.
            require(sm[(1, '__numdev')] == len(prefix) and sm[(2, '__H2_org')] == len(payload) and
                    sm[(2, '__H2_end')] - sm[(2, '__H2_org')] == common_size and
                    next(h for h in model['hunks'] if h['number'] == 2)['allocated_size'] == 4,
                    'provider/data symbol bounds differ')
            names = {n for (h,n), off in sm.items() if h == 2 and not n.startswith('__H')}
            require(names == wanted and all(len(payload) <= sm[(2,n)] < len(payload) + common_size for n in wanted),
                    'complete COMMON symbol set differs')
            rows.append(dict(variant=variant, root=root_name, object_data=2, common_bytes=common_size,
                initialized_data_hex=payload.hex(), numdev_offset=len(prefix),
                common_fields={n: sm[(2,n)] - len(payload) for n in sorted(wanted)},
                original_ownership='UNKNOWN', accounting_promoted=False))
    return dict(status='WHOLE_PROVIDER_VARIANTS_DIFFER_IN_COMMON', acceptance=False, controls=rows,
        conclusion='Identical initialized provider bytes cannot choose between complete COMMON allocations64 and72. No original provider, padding, DATA or COMMON ownership accepted.')


if __name__ == '__main__':
    print(json.dumps(replay(), indent=2))
