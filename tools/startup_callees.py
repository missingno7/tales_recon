"""Independent complete leaf identities for the bounded resident startup recipe.

This is a binding prerequisite, not runtime accounting or startup acceptance.
The accepted-public-entry requirement in library_a4 remains unchanged.
"""
from names import to_mechanical
import json
from pathlib import Path

from common import require, sha256
from repo_paths import canonical_path
from resident_mixed import pinned
from hunk import parse
from overlay_experiment import symbols, contribution

BASE = 'evidence/rules/startup-callees'
GROUPS = [
    ('exec', '_SysBase', [('alert', '_Alert', 24, 12, 34628),
                         ('_waitpor', '__WaitPort', 12, 6, 35386),
                         ('_getmsg', '__GetMsg', 12, 6, 35228)]),
    ('dos', '_DOSBase', [('_current', '__CurrentDir', 12, 6, 34460),
                       ('_input', '__Input', 8, 2, 34496),
                       ('_output', '__Output', 8, 2, 34542),
                       ('_open', '__Open', 14, 8, 34528)]),
]
ARCHIVES = {'exec': '9d6a62b0ddafd602e1563e9141585c89c076f7a50e21e75e850c9bc876556d46',
            'dos': '18c0f44ba64e05761483c12f45ddd46b2da26453962127d4f02fe05dec36fc86'}


def read(root, path):
    return (to_mechanical(canonical_path(root, path).read_bytes()) if str(path).startswith('src/') else canonical_path(root, path).read_bytes())


def dosbase(root, blob, model, sysbase, bias):
    """Bound the original initializer; this does not accept the CRT0 object.

The SDK supplies the OpenLibrary ABI/role evidence. Original instructions
derive the handle coordinate, rather than assuming a matching leaf's base.
"""
    sdk = pinned(root, 'toolchain/installed/aztec-3.6a/SYS2/crt_src/crt0.a68').decode('ascii')
    for text in ('move.l\t4,a6', 'move.l\ta6,_SysBase', 'lea\tdos_name,a1',
                 'jsr\t-408(a6)', 'move.l\td0,_DOSBase', "dc.b\t'dos.library',0"):
        require(sdk.count(text) == 1, 'startup DOS initializer SDK role differs')
    raw = contribution(blob, model, 0, 30226, 56)
    require(raw[:6] == bytes.fromhex('2c780004294e') and
            bias + int.from_bytes(raw[6:8], 'big', signed=True) == sysbase,
            'startup DOS initializer ExecBase binding differs')
    # Complete intervening SDK FPU guard, parameter save, and supervisor thunk.
    # These fixed instructions preserve the ExecBase register into OldOpenLibrary.
    require(raw[8:36] == bytes.fromhex('48e78080082e0004012967104bfa00084eaeffe2600642a7f35f4e73'),
            'startup DOS initializer intervening control differs')
    require(raw[36:38] == bytes.fromhex('43fa') and raw[40:46] == bytes.fromhex('4eaefe682940'),
            'startup DOS initializer call/store differs')
    name = 30226 + 38 + int.from_bytes(raw[38:40], 'big', signed=True)
    require(name == 30296 and contribution(blob, model, 0, name, 12) == b'dos.library\0',
            'startup DOS initializer name differs')
    target = bias + int.from_bytes(raw[46:48], 'big', signed=True)
    require(target == 43406, 'startup DOS initializer handle differs')
    require(not any(r['source_hunk'] == 0 and r['source_offset'] < 30282 and
                    r['source_offset'] + r['width'] > 30226 for r in model['relocations']),
            'startup DOS initializer unexpected relocation')
    return target


def leaf_groups(root, blob, model, bases, bias):
    """Replay the exact retained experiments against independently proved bases."""
    library = pinned(root, 'toolchain/installed/aztec-3.6a/SYS1/lib/c.lib')
    rows = []
    for kind, base, leaves in GROUPS:
        directory = BASE + '/' + kind
        archive = read(root, 'toolchain/installed/aztec-3.6a/Library Source/' + kind + '.arc')
        require(sha256(archive) == ARCHIVES[kind], 'startup leaf SDK archive differs')
        receipt = json.loads(read(root, directory + '/receipt.json'))
        commands = ['Old2:bin/lb >extract.log Old1:lib/c.lib -x ' + ' '.join(x[0] for x in leaves)]
        commands += ['Old1:bin/as >%s-as.log -o %s.o %s.asm' % (n, n, n) for n in ('root1', 'root2')]
        for member, _, _, _, _ in leaves:
            commands.append('Old1:bin/as >%s-as.log -o %s-source.o %s.asm' % (member, member, member))
            for name in ('root1', 'root2'):
                for origin in ('lib', 'source'):
                    prefix = member + '-' + name + '-' + origin
                    obj = member + ('' if origin == 'lib' else '-source') + '.o'
                    commands.append('Old1:bin/ln >%s.log -m -t -o %s %s %s.o' % (prefix, prefix, obj, name))
        require([s['command'] for s in receipt['steps']] == commands and
                all(s['returncode'] == 0 for s in receipt['steps']), 'startup leaf recipe differs')
        tools = {'toolchain/installed/aztec-3.6a/' + p for p in ('SYS1/bin/as', 'SYS1/bin/ln', 'SYS2/bin/lb')}
        require({t['path'] for t in receipt['tool_inputs']} == tools and len(receipt['tool_inputs']) == 3,
                'startup leaf tool set differs')
        for item in receipt['tool_inputs']:
            require(sha256(pinned(root, item['path'])) == item['sha256'], 'startup leaf tool pin differs')
        sources = {s['path']: s for s in receipt['source_files']}
        require(len(sources) == len(receipt['source_files']) and
                set(sources) == {'root1.asm', 'root2.asm'} | {x[0] + '.asm' for x in leaves},
                'startup leaf source inventory differs')
        artifacts = {a['path']: a for a in receipt['artifacts']}
        require(len(artifacts) == len(receipt['artifacts']), 'startup duplicate leaf artifact')
        def artifact(name):
            raw = read(root, directory + '/' + name)
            item = artifacts.get(name)
            require(item and item['sha256'] == sha256(raw) and item['size'] == len(raw),
                    'startup leaf artifact missing or changed')
            return raw
        for name in sources:
            require(sha256(artifact(name)) == sources[name]['sha256'], 'startup leaf source receipt differs')
        for member, symbol, size, field, target in leaves:
            parts = [p.split('\n', 1)[1] for p in archive.decode('ascii').split('\f')
                     if p.strip().startswith(member + '.a68\n')]
            require(len(parts) == 1 and artifact(member + '.asm') == parts[0].encode('ascii'),
                    'startup leaf SDK source differs')
            obj, assembled = artifact(member + '.o'), artifact(member + '-source.o')
            require(library.count(obj) == 1 and obj[:2] == assembled[:2] == b'AJ' and
                    obj[2:10].rstrip(b'\0').decode('ascii') == member and
                    int.from_bytes(obj[10:14], 'big') == int.from_bytes(assembled[10:14], 'big') == size and
                    obj[14:22] == assembled[14:22] == bytes(8), 'startup whole library object differs')
            variants = []
            for name in ('root1', 'root2'):
                expected = '\tpublic ' + base + '\n\tdseg\n' + ('\tdc.w 1,2,3\n' if name == 'root2' else '') + base + '\n\tdc.l 0\n'
                require(artifact(name + '.asm') == expected.encode('ascii'), 'startup leaf DATA source differs')
                root_obj = artifact(name + '.o')
                require(root_obj[:2] == b'AJ' and int.from_bytes(root_obj[10:14], 'big') == 0 and
                        int.from_bytes(root_obj[14:18], 'big') == (4 if name == 'root1' else 10) and
                        root_obj[18:22] == bytes(4), 'startup leaf DATA object differs')
                for origin in ('lib', 'source'):
                    prefix = member + '-' + name + '-' + origin
                    b = artifact(prefix); m = parse(b); sm = symbols(artifact(prefix + '.sym').decode('ascii'))
                    h = next(h for h in m['hunks'] if h['number'] == 0)
                    rounded = (size + 3) & ~3
                    require(h['initialized_size'] == h['allocated_size'] == rounded and not m['relocations'] and
                            sm.get((0, symbol)) == 0, 'startup leaf CODE clipped or relocated')
                    require(contribution(b, m, 0, 0, rounded)[size:] == bytes(rounded - size),
                            'startup leaf terminal alignment differs')
                    raw = contribution(b, m, 0, 0, size)
                    require(raw[field - 2:field] == bytes.fromhex('2c6c') and
                            bias + int.from_bytes(raw[field:field + 2], 'big', signed=True) ==
                            sm.get((1, base)) == (0 if name == 'root1' else 6), 'startup leaf base binding differs')
                    data = next(h for h in m['hunks'] if h['number'] == 1)
                    payload = bytes(4) if name == 'root1' else bytes.fromhex('000100020003000000000000')
                    require(data['initialized_size'] == data['allocated_size'] == len(payload) and
                            b[data['content_offset']:data['content_offset'] + len(payload)] == payload,
                            'startup leaf complete DATA differs')
                    variants.append(raw[:field] + bytes(2) + raw[field + 2:])
            require(len(set(variants)) == 1, 'startup leaf source/library links differ')
            needle = variants[0][:field] + (bases[base] - bias).to_bytes(2, 'big', signed=True) + variants[0][field + 2:]
            matches = []
            for h in model['hunks']:
                if h['type'] != 'CODE':
                    continue
                raw = blob[h['content_offset']:h['content_offset'] + h['initialized_size']]
                pos = raw.find(needle)
                while pos >= 0:
                    if pos % 2 == 0 and not any(r['source_hunk'] == h['number'] and r['source_offset'] < pos + size and
                                               r['source_offset'] + r['width'] > pos for r in model['relocations']):
                        matches.append((h['number'], pos))
                    pos = raw.find(needle, pos + 1)
            require(matches == [(0, target)], 'startup original leaf identity not unique')
            rows.append(dict(member=member, symbol=symbol, hunk=0, start=target, size=size,
                             base=base, base_offset=bases[base], accounting_promoted=False))
    return rows


def verify(root, blob, model, analysis, promotions, ledger):
    from library_a4 import load_library_a4
    require(analysis['game_sha256'] == sha256(blob) and analysis['a4']['bias'] == 32766,
            'startup binding oracle identity differs')
    accepted = load_library_a4(root, blob, model, analysis, promotions, ledger)
    doc = json.loads(read(root, 'evidence/contributions/library-a4.json'))
    bases = {g['reference']['original_offset'] for g in doc['groups'] if g['reference']['symbol'] == '_SysBase'}
    require(bases == {45986}, 'startup SysBase identity differs')
    for group, entry, symbol in [('allocmem_unit', 35114, '__AllocMem'), ('findtask_unit', 35172, '__FindTask')]:
        g = next(g for g in doc['groups'] if g['id'] == group)
        require(any(r['id'] == 'runtime_' + group for r in accepted) and
                any(g['original']['start'] + d['offset'] == entry and d['symbol'] == symbol for d in g['definitions']),
                'startup accepted helper identity differs')
    dos = dosbase(root, blob, model, 45986, 32766)
    rows = leaf_groups(root, blob, model, {'_SysBase': 45986, '_DOSBase': dos}, 32766)
    return dict(status='VERIFIED_STARTUP_LEAF_BINDINGS', acceptance=False, leaf_bytes=90, leaves=rows,
                accepted_private_helpers=[35114, 35172], storage_ownership='UNKNOWN')


if __name__ == '__main__':
    from analysis_support import ROOT, game
    from recovery_state import evidence
    from recovery_evidence import load_promotions
    blob, model, _ = game(); analysis = evidence()
    ledger = json.loads(read(ROOT, 'recovery/ledger.json'))
    print(json.dumps(verify(ROOT, blob, model, analysis, load_promotions(ROOT, blob, model, analysis), ledger), indent=2))
