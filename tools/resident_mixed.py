"""Strict staged SDK-derived mixed-object verification; no promotion or output patching.

Only the bounded exit recipe is supported. Normal candidate-C rules stay intact.
The returned report establishes source-object evidence, not historical TU ownership
or natural root layout. Curated source facts are separate from generated ledgers.
"""
import json
import re
from pathlib import Path

from common import require, sha256
from repo_paths import canonical_path
from hunk import parse
from overlay_experiment import symbols, contribution
from resident_object import code_size
from compiler_oracle import harness
from analysis_support import signed16

FACT = 'evidence/source-facts/resident-exit.json'
PARTS = [('C_COMPILER', 0, 122), ('ASM', 122, 154),
         ('C_COMPILER', 154, 222), ('ASM', 222, 232), ('C_COMPILER', 232, 238)]


def read(root, path):
    return canonical_path(root, path).read_bytes()


def pinned(root, path):
    inventory = json.loads(read(root, 'evidence/toolchain/aztec-3.6a.json'))
    pins = {('toolchain/installed/aztec-3.6a/' + d['manifest']['volume'] + '/' + e['path']): e['sha256']
            for d in inventory['disks'] if d['status'] == 'VALIDATED'
            for e in d['manifest']['entries'] if e['kind'] == 'file'}
    raw = read(root, path)
    require(path in pins and sha256(raw) == pins[path], 'mixed pinned input differs')
    return raw


def expected_source(root):
    sdk = pinned(root, 'toolchain/installed/aztec-3.6a/SYS2/crt_src/_exit.c').decode('ascii')
    # Normalize source transport only; the recipe never normalizes emitted CODE.
    sdk = sdk.replace('\r\n', '\n')
    blocks = [
        '\tif (_detach_curdir)\t\t\t\t/* for DETACHed programs */\n\t\tUnLock(_detach_curdir);\n',
        '\tif (_trapaddr)\t\t\t\t\t/* clean up signal handling */\n\t\t*_trapaddr = _oldtrap;\n',
        '\tif (MathIeeeDoubTransBase)\n\t\t_CloseLibrary(MathIeeeDoubTransBase);\n',
    ]
    # Use exact SDK comments as well as operations, preventing arbitrary edits.
    for pattern in blocks[:2]:
        # SDK wording is fixed by the distribution pin; accept its actual line.
        prefix = pattern.split('/*')[0]
        line = next((x for x in sdk.splitlines(True) if x.startswith(prefix)), None)
        require(line is not None, 'mixed SDK branch absent')
        block = line + pattern.split('\n', 1)[1]
        require(sdk.count(block) == 1, 'mixed SDK branch ambiguous')
        sdk = sdk.replace(block, '')
    require(sdk.count(blocks[2]) == 1, 'mixed SDK fourth library branch absent')
    sdk = sdk.replace(blocks[2], '')
    body = sdk[sdk.index('_exit(code)'):].replace('_exit(code)', 'recovered(code)', 1)
    mapping = {'_devtab': 'G_h01_B3A6', '_numdev': 'G_h01_2EB0', '_cln': 'G_h01_B3C8',
               'MathTransBase': 'G_h01_B3CE', 'MathBase': 'G_h01_B3D2',
               'MathIeeeDoubBasBase': 'G_h01_B3D6', 'WBenchMsg': 'G_h01_B3B0',
               '_arg_lin': 'G_h01_B3BC', '_arg_len': 'G_h01_B3BA', '_argc': 'G_h01_B3B8',
               '_argv': 'G_h01_B3B4', 'close': 'F_h00_8640', '_FreeMem': 'F_h00_8980',
               '_CloseLibrary': 'F_h00_8788', '_Forbid': 'F_h00_8974', '_ReplyMsg': 'F_h00_8A12'}
    for old, new in mapping.items():
        body = re.sub(r'\b' + re.escape(old) + r'\b', new, body)
    body = body.replace('struct _dev', 'struct DevView').replace(
        '(*G_h01_B3C8)();', '(*(int (*)())G_h01_B3C8)();').replace('__savsp#', '_G_h01_B39E#')
    header = ('/* Experimental complete SDK-derived mixed C/assembly object.\n'
              '   Mechanical access views claim no original DATA/COMMON provider or types. */\n'
              'struct DevView { long fd; short mode; };\n'
              'extern struct DevView *G_h01_B3A6;\nextern short G_h01_2EB0;\n')
    header += ''.join('extern long G_h01_' + x + ';\n' for x in ('B3C8', 'B3CE', 'B3D2', 'B3D6', 'B3B0'))
    header += ('extern char *G_h01_B3BC;\nextern int G_h01_B3BA;\nextern int G_h01_B3B8;\n'
               'extern char **G_h01_B3B4;\nextern long G_h01_B39E;\n')
    header += ''.join('extern int F_h00_' + x + '();\n' for x in ('8640', '8980', '8788', '8974', '8A12'))
    return header + body


def marked_source(source):
    index = [0]
    def mark(match):
        i = index[0]
        index[0] += 1
        return ('#asm\n\tpublic\t_runtime_asm_begin%d\n_runtime_asm_begin%d:\n' % (i, i)
                + match[1] + '\tpublic\t_runtime_asm_end%d\n_runtime_asm_end%d:\n#endasm' % (i, i))
    result = re.sub(r'#asm\n(.*?)#endasm', mark, source, flags=re.S)
    require(index[0] == 2, 'mixed SDK assembly block count differs')
    return result


def control(root, directory, source):
    receipt = json.loads(read(root, directory + '/receipt.json'))
    commands = ['Old1:bin/cc -a +X3 -o candidate.asm candidate.c <compiler-input.txt >candidate-cc.log',
                'Old1:bin/as -o candidate.o candidate.asm <compiler-input.txt >candidate-as.log',
                'Old1:bin/cc -a +X3 -o root.asm root.c <compiler-input.txt >root-cc.log',
                'Old1:bin/as -o root.o root.asm <compiler-input.txt >root-as.log',
                'Old1:bin/ln -m -t -o candidate.exe root.o candidate.o Old1:lib/c.lib <compiler-input.txt >candidate-ln.log']
    require([x['command'] for x in receipt['steps']] == commands and
            all(x['returncode'] == 0 for x in receipt['steps']), 'mixed producing recipe differs')
    required_tools = {'toolchain/installed/aztec-3.6a/SYS1/' + x for x in ('bin/cc', 'bin/as', 'bin/ln', 'lib/c.lib')}
    require({x['path'] for x in receipt['tool_inputs']} == required_tools, 'mixed tool identities missing')
    for tool in receipt['tool_inputs']:
        require(sha256(pinned(root, tool['path'])) == tool['sha256'], 'mixed tool receipt differs')
    require(read(root, directory + '/candidate.c') == source.encode('ascii'), 'mixed source does not rederive')
    root_source = harness(source, 0)
    require(read(root, directory + '/root.c') == root_source.encode('ascii'), 'mixed harness does not rederive')
    for name, text in [('candidate.c', source), ('root.c', root_source)]:
        matches = [x for x in receipt['source_files'] if x['path'] == name]
        require(len(matches) == 1 and matches[0]['sha256'] == sha256(text.encode('ascii')), 'mixed source receipt differs')
    for name in ('candidate.asm', 'candidate.o', 'root.asm', 'root.o', 'candidate.exe', 'candidate.sym'):
        raw = read(root, directory + '/' + name)
        matches = [x for x in receipt['artifacts'] if x['path'] == name]
        require(len(matches) == 1 and matches[0]['sha256'] == sha256(raw), 'mixed artifact receipt differs')
    path = canonical_path(root, directory)
    require(read(root, directory + '/candidate.o')[14:22] == bytes(8), 'mixed object owns unexplained storage')
    blob = read(root, directory + '/candidate.exe'); model = parse(blob)
    sm = symbols(read(root, directory + '/candidate.sym').decode('ascii'))
    start = sm[(0, '_recovered')]
    require(code_size(path / 'candidate.o') == 238 and sm[(0, '_main')] + code_size(path / 'root.o') == start,
            'mixed whole-object bounds differ')
    require(sm[(0, '.begin')] == start + 238, 'mixed object end differs')
    require(not any(r['source_hunk'] == 0 and r['source_offset'] < start + 238 and
                    r['source_offset'] + r['width'] > start for r in model['relocations']), 'mixed unexpected CODE relocation')
    require(not any(h == 0 and start <= off < start + 238 and name.startswith('_F_h00_')
                    for (h, name), off in sm.items()), 'mixed unrelated function inside object')
    return contribution(blob, model, 0, start, 238), sm, start, model


def callees(root, blob, model, analysis, promotions, ledger, directory):
    from library_a4 import load_library_a4
    rows = load_library_a4(root, blob, model, analysis, promotions, ledger)
    doc = json.loads(read(root, 'evidence/contributions/library-a4.json'))
    for group, target, symbol in [('freemem_unit', 35200, '__FreeMem'),
                                   ('closelib_unit', 34696, '__CloseLibrary')]:
        g = next((g for g in doc['groups'] if g['id'] == group), None)
        require(g is not None and any(r['id'] == 'runtime_' + group for r in rows), 'mixed accepted runtime unit missing')
        definition = next(d for d in g['definitions'] if d['symbol'] == symbol)
        require(g['original']['start'] + definition['offset'] == target, 'mixed private callee target differs')
    base = next(g for g in doc['groups'] if g['id'] == 'closelib_unit')['reference']['original_offset']
    library = pinned(root, 'toolchain/installed/aztec-3.6a/SYS1/lib/c.lib')
    archive_path = 'toolchain/installed/aztec-3.6a/Library Source/exec.arc'
    archive = read(root, archive_path)
    require(any(a['path'] == archive_path and a['sha256'] == sha256(archive) for a in doc['archives']),
            'mixed leaf SDK archive differs')
    receipt = json.loads(read(root, directory + '/receipt.json'))
    commands = ['Old2:bin/lb >extract.log Old1:lib/c.lib -x _forbid _replyms']
    commands += ['Old1:bin/as >%s-as.log -o %s.o %s.asm' % (x, x, x) for x in ('root1', 'root2')]
    for member in ('_forbid', '_replyms'):
        commands.append('Old1:bin/as >%s-as.log -o %s-source.o %s.asm' % (member, member, member))
        for root_name in ('root1', 'root2'):
            for kind in ('lib', 'source'):
                prefix = member + '-' + root_name + '-' + kind
                obj = member + ('' if kind == 'lib' else '-source') + '.o'
                commands.append('Old1:bin/ln >%s.log -m -t -o %s %s %s.o' % (prefix, prefix, obj, root_name))
    require([s['command'] for s in receipt['steps']] == commands and
            all(s['returncode'] == 0 for s in receipt['steps']), 'mixed leaf producing recipe differs')
    require({x['path'] for x in receipt['tool_inputs']} ==
            {'toolchain/installed/aztec-3.6a/SYS1/bin/as', 'toolchain/installed/aztec-3.6a/SYS1/bin/ln',
             'toolchain/installed/aztec-3.6a/SYS2/bin/lb'}, 'mixed leaf tool identities missing')
    for item in receipt['tool_inputs']:
        require(sha256(pinned(root, item['path'])) == item['sha256'], 'mixed leaf tool differs')
    def artifact(name):
        raw = read(root, directory + '/' + name)
        matches = [a for a in receipt['artifacts'] if a['path'] == name]
        require(len(matches) == 1 and matches[0]['sha256'] == sha256(raw), 'mixed leaf artifact receipt differs')
        return raw
    for member, symbol, size, field, target in [('_forbid', '__Forbid', 8, 2, 35188),
                                               ('_replyms', '__ReplyMsg', 12, 6, 35346)]:
        sdk_parts = [p.split('\n', 1)[1] for p in archive.decode('ascii').split('\f')
                     if p.strip().startswith(member + '.a68\n')]
        source = read(root, directory + '/' + member + '.asm')
        require(len(sdk_parts) == 1 and source == sdk_parts[0].encode('ascii'), 'mixed leaf SDK source differs')
        inputs = [s for s in receipt['source_files'] if s['path'] == member + '.asm']
        require(len(inputs) == 1 and inputs[0]['sha256'] == sha256(source), 'mixed leaf source receipt differs')
        obj = artifact(member + '.o'); assembled = artifact(member + '-source.o')
        require(obj[:2] == assembled[:2] == b'AJ' and library.count(obj) == 1 and
                int.from_bytes(obj[10:14], 'big') == int.from_bytes(assembled[10:14], 'big') == size and
                obj[14:22] == assembled[14:22] == bytes(8), 'mixed complete leaf object differs')
        variants = []
        for root_name in ('root1', 'root2'):
            expected_root = ('\tpublic _SysBase\n\tdseg\n' +
                             ('\tdc.w 1,2,3\n' if root_name == 'root2' else '') + '_SysBase\n\tdc.l 0\n')
            require(read(root, directory + '/' + root_name + '.asm') == expected_root.encode('ascii'),
                    'mixed leaf authored DATA source differs')
            for kind in ('lib', 'source'):
                prefix = member + '-' + root_name + '-' + kind
                b = artifact(prefix); m = parse(b); sm = symbols(artifact(prefix + '.sym').decode('ascii'))
                h = next(h for h in m['hunks'] if h['number'] == 0)
                require(h['initialized_size'] == h['allocated_size'] == size and not m['relocations'],
                        'mixed leaf CODE clipped or relocation added')
                raw = contribution(b, m, 0, sm[(0, symbol)], size)
                require(raw[field - 2:field] == bytes.fromhex('2c6c') and
                        analysis['a4']['bias'] + int.from_bytes(raw[field:field + 2], 'big', signed=True) ==
                        sm[(1, '_SysBase')] == (0 if root_name == 'root1' else 6), 'mixed leaf base identity differs')
                data = next(h for h in m['hunks'] if h['number'] == 1)
                payload = bytes(4) if root_name == 'root1' else bytes.fromhex('000100020003000000000000')
                require(data['initialized_size'] == data['allocated_size'] == len(payload) and
                        b[data['content_offset']:data['content_offset'] + len(payload)] == payload,
                        'mixed leaf DATA constructor differs')
                variants.append(raw[:field] + bytes(2) + raw[field + 2:])
        require(len(set(variants)) == 1, 'mixed source/library leaf control differs')
        needle = variants[0][:field] + (base - analysis['a4']['bias']).to_bytes(2, 'big', signed=True) + variants[0][field + 2:]
        matches = []
        for h in model['hunks']:
            if h['type'] != 'CODE':
                continue
            raw = blob[h['content_offset']:h['content_offset'] + h['initialized_size']]; pos = 0
            while True:
                off = raw.find(needle, pos)
                if off < 0:
                    break
                pos = off + 1
                if off % 2 == 0 and not any(r['source_hunk'] == h['number'] and r['source_offset'] < off + size and
                                           r['source_offset'] + r['width'] > off for r in model['relocations']):
                    matches.append((h['number'], off))
        require(matches == [(0, target)], 'mixed original leaf identity not unique')


def verify(root, blob, model, analysis, promotions, ledger, *, fact=None):
    root = Path(root).resolve()
    fact = json.loads(read(root, FACT)) if fact is None else fact
    require(analysis['game_sha256'] == sha256(blob), 'mixed game identity differs')
    require(fact['schema_version'] == 1 and fact['id'] == 'resident_F_8552' and
            fact['original'] == dict(hunk=0, start=34130, end=34368), 'mixed source extent differs')
    require([tuple(p) for p in fact['partitions']] == PARTS, 'mixed curated partition differs')
    require(fact['sdk_source'] == 'toolchain/installed/aztec-3.6a/SYS2/crt_src/_exit.c', 'mixed SDK selector differs')
    require(fact['status'] == 'STAGED_SOURCE_OBJECT_FACT' and fact['original_storage_ownership'] ==
            fact['original_filename'] == fact['original_tu'] == 'UNKNOWN', 'mixed unsupported ownership claim')
    for key, value in [('inbound', 'resident_F_8534'), ('close_callee', 'resident_F_8640')]:
        require(fact[key] == value and value in ledger['functions'] and
                any(p['id'] == value for p in promotions), 'mixed canonical anchor missing')
        item = ledger['functions'][value]
        require(sha256(read(root, item['source'])) == item['source_sha256'] and
                sha256(read(root, item['proof'])) == item['proof_sha256'], 'mixed canonical anchor stale')
    inbound = json.loads(read(root, ledger['functions'][fact['inbound']]['proof']))
    require(any(x.get('identity') == dict(symbol='_F_h00_8552', hunk=0, offset=34130, addend=0)
                for x in inbound['comparison']['relocation_proof']), 'mixed inbound binding absent')
    callees(root, blob, model, analysis, promotions, ledger, fact['leaf_directory'])
    source = expected_source(root)
    c, sm, start, cm = control(root, fact['mechanical_directory'], source)
    marked, msm, mstart, _ = control(root, fact['partition_directory'], marked_source(source))
    require(c == marked, 'mixed marker changes full CODE')
    for key, value in sm.items():
        if key[1].startswith(('_F_h00_', '_G_h01_')):
            require(msm.get(key) == value, 'mixed marker changes binding')
    for index, (lo, hi) in enumerate([(122, 154), (222, 232)]):
        require(msm[(0, '_runtime_asm_begin%d' % index)] - mstart == lo and
                msm[(0, '_runtime_asm_end%d' % index)] - mstart == hi, 'mixed source-language markers differ')
    # Coprocessor decoding is confined to this positively pinned SDK recipe.
    import capstone
    md = capstone.Cs(capstone.CS_ARCH_M68K, capstone.CS_MODE_BIG_ENDIAN | capstone.CS_MODE_M68K_040)
    md.detail = True
    original = contribution(blob, model, 0, 34130, 238)
    ei, ai = list(md.disasm(original, 0)), list(md.disasm(c, 0))
    require(sum(x.size for x in ei) == sum(x.size for x in ai) == 238 and
            [(x.address, x.size, x.mnemonic) for x in ei] == [(x.address, x.size, x.mnemonic) for x in ai] and
            not any(x.mnemonic.startswith('dc.') for x in ei + ai), 'mixed complete instruction decode differs')
    fields = []; mask = set(); bias = analysis['a4']['bias']
    data = next(h for h in cm['hunks'] if h['number'] == 1)
    bss = next(h for h in cm['hunks'] if h['number'] == 2)
    orgs = [off for (h, name), off in sm.items() if name == '__H2_org']
    require(orgs == [data['initialized_size']] and bss['allocated_size'] == 4, 'mixed COMMON convention differs')
    for e, a in zip(ei, ai):
        pos = e.address + 2
        if '(a4)' in e.op_str:
            require(e.size == a.size == 4 and '(a4)' in a.op_str, 'mixed unsupported A4 field')
            old = bias + signed16(int.from_bytes(original[pos:pos + 2], 'big'))
            actual = bias + signed16(int.from_bytes(c[pos:pos + 2], 'big'))
            name = '_G_h01_%04X' % old
            require(any(n == name and off == actual and h in (1, 2) for (h, n), off in sm.items()) and
                    0 <= actual < data['allocated_size'], 'mixed global identity differs')
        elif e.mnemonic == 'jsr' and '(pc)' in e.op_str:
            require(e.size == a.size == 4 and '(pc)' in a.op_str, 'mixed unsupported call field')
            old = 34130 + pos + signed16(int.from_bytes(original[pos:pos + 2], 'big'))
            actual = start + pos + signed16(int.from_bytes(c[pos:pos + 2], 'big'))
            name = '_F_h00_%04X' % old
            require(sm.get((0, name)) == actual, 'mixed callee identity differs')
        else:
            continue
        require(original[e.address:pos] == c[e.address:pos], 'mixed reference opcode differs')
        fields.append(dict(site=e.address, symbol=name, original_offset=old))
        mask.update(range(pos, pos + 2))
    require(len(fields) == 29 and len(mask) == 58 and
            all(a == b for i, (a, b) in enumerate(zip(original, c)) if i not in mask), 'mixed complete byte comparison differs')
    require({x['original_offset'] for x in fields if x['symbol'].startswith('_F')} ==
            {34368, 35200, 34696, 35188, 35346}, 'mixed callee set differs')
    return dict(status='VERIFIED_STAGED_MIXED_OBJECT', acceptance=False, code_bytes=238,
                c_compiler_bytes=196, sdk_asm_bytes=42, field_identities=fields,
                source_sha256=sha256(source.encode('ascii')), storage_ownership='UNKNOWN')


def load_source_objects(root, blob, model, analysis, promotions, ledger):
    """Reconcile curated whole-object evidence with descent, without promotion.

    CFG reachability and compiler object extent answer different questions.
    Keep both; a staged source fact cannot enlarge normal C acceptance bounds.
    No recorded experiment verdict or generated metric is trusted here.
    """
    path = canonical_path(root, FACT)
    if not path.exists():
        return []
    raw = path.read_bytes()
    fact = json.loads(raw)
    report = verify(root, blob, model, analysis, promotions, ledger, fact=fact)
    matches = [f for f in analysis['functions'] if f['id'] == fact['id']]
    require(len(matches) == 1, 'mixed descent entry missing or duplicated')
    cfg = matches[0]; original = fact['original']
    require(cfg['hunk'] == original['hunk'] and cfg['start'] == original['start'] and
            cfg['start'] < cfg['end'] <= original['end'] and cfg['size'] == cfg['end'] - cfg['start'],
            'mixed descent extent conflicts')
    require(cfg['sha256'] == sha256(contribution(blob, model, cfg['hunk'], cfg['start'], cfg['size'])),
            'mixed descent bytes differ')
    require(cfg['id'] not in ledger['functions'], 'mixed staged object already promoted')
    require(not any(f['id'] != cfg['id'] and f['hunk'] == cfg['hunk'] and
                    original['start'] < f['start'] < original['end']
                    for f in analysis['functions']), 'mixed source object contains another entry')
    require(not any(p['hunk'] == cfg['hunk'] and p['start'] < original['end'] and
                    p['end'] > original['start'] for p in promotions),
            'mixed source object overlaps accepted source')
    return [dict(id=fact['id'], status=report['status'], acceptance=False,
                 fact=dict(path=FACT, sha256=sha256(raw)),
                 source_sha256=report['source_sha256'],
                 original=original, size=report['code_bytes'],
                 cfg_extent={k: cfg[k] for k in ('start', 'end', 'size', 'extent_status', 'confidence')},
                 extent_basis='PINNED_SDK_DERIVATION_AND_COMPLETE_LINKED_OBJECT',
                 partitions=[dict(language=language, start=original['start'] + lo,
                                  end=original['start'] + hi) for language, lo, hi in fact['partitions']],
                 c_compiler_bytes=report['c_compiler_bytes'], sdk_asm_bytes=report['sdk_asm_bytes'],
                 field_identities=report['field_identities'],
                 original_storage_ownership='UNKNOWN', original_filename='UNKNOWN', original_tu='UNKNOWN')]


def source_object_inputs(root):
    """Complete extra read graph for scoped census reuse, including absence.

    The verifier still rederives all claims on each cache miss. Hashing this graph
    only permits reuse while its actual inputs remain unchanged.
    """
    from repo_paths import active_files
    root = Path(root).resolve()
    paths = {FACT}
    fact_path = canonical_path(root, FACT)
    if not fact_path.exists():
        return sorted(paths)
    fact = json.loads(fact_path.read_bytes())
    paths.update([fact['sdk_source'], 'evidence/toolchain/aztec-3.6a.json',
                  'evidence/contributions/library-a4.json'])
    for key in ('mechanical_directory', 'partition_directory', 'leaf_directory'):
        directory = canonical_path(root, fact[key])
        paths.update(p.relative_to(root).as_posix() for p in active_files(directory))
        receipt_path = fact[key] + '/receipt.json'; paths.add(receipt_path)
        if canonical_path(root, receipt_path).exists():
            receipt = json.loads(read(root, receipt_path))
            paths.update(t['path'] for t in receipt['tool_inputs'])
    library = json.loads(read(root, 'evidence/contributions/library-a4.json'))
    paths.update([library['library']['path'], library['basis']['path']])
    paths.update(a['path'] for a in library['archives'])
    for group in library['groups']:
        for obj in group['objects']:
            paths.add(obj['source'])
            paths.update(obj[k]['path'] for k in ('library', 'assembled'))
        for control_row in group['controls']:
            paths.add(control_row['root_source'])
            paths.update(control_row[k]['path'] for k in ('executable', 'symbols', 'root_object'))
    for claim in library['receipts']:
        paths.add(claim['path'])
        receipt = json.loads(read(root, claim['path']))
        paths.update(t['path'] for t in receipt['tool_inputs'])
    return sorted(paths)


def main():
    from analysis_support import ROOT, game
    from recovery_state import evidence
    from recovery_evidence import load_promotions
    blob, model, _ = game(); analysis = evidence()
    ledger = json.loads((ROOT / 'recovery/ledger.json').read_text())
    promotions = load_promotions(ROOT, blob, model, analysis)
    report = verify(ROOT, blob, model, analysis, promotions, ledger)
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
