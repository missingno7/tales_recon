from __future__ import annotations
import argparse, collections, hashlib, json, os, re, shutil, subprocess, sys
from pathlib import Path

ROOT = next(p for p in Path(__file__).resolve().parents if (p / 'recovery' / 'ledger.json').is_file())
sys.path.insert(0, str(ROOT/'tools'))
from repo_paths import is_active_repo_path
HERE = Path(__file__).resolve().parent
INV_PATH = ROOT / 'build/workers/sol-link-inventory/inventory.json'
LEDGER_PATH = ROOT / 'recovery/ledger.json'
STAGE = ROOT / 'build' / 'game'
GUEST = STAGE / 'guest_source'

def sha(data): return hashlib.sha256(data).hexdigest()
def digest(path): return sha(path.read_bytes())
def read_json(path): return json.loads(path.read_text(encoding='utf-8'))
def write_json(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + '\n', encoding='utf-8', newline='\n')
def token_replace(text, old, new):
    return re.sub(r'(?<![A-Za-z0-9_])' + re.escape(old) + r'(?![A-Za-z0-9_])', new, text)

def remap_inline_asm(text, mapping):
    # C preprocessor macros do not rename symbols inside Aztec #asm blocks.
    pattern = re.compile(r'#asm\b[\s\S]*?#endasm\b', re.IGNORECASE)
    def replace_block(match):
        block = match.group(0)
        for source, target in sorted(mapping.items(), key=lambda item: -len(item[0])):
            if source != target: block = token_replace(block, source, target)
        return block
    return pattern.sub(replace_block, text)
def c_name(symbol):
    if not symbol or symbol.startswith('.') or not symbol.startswith('_'): return None
    return symbol[1:]
def clean_flags(profile, source_row=None):
    if profile in ('aztec36', 'aztec36-large-data', 'aztec36-x3'):
        return {'aztec36': [], 'aztec36-large-data': ['+D'], 'aztec36-x3': ['+X3']}[profile]
    if 'as;' in profile.lower(): return []
    flags = []
    if '+D' in profile: flags.append('+D')
    if '+X3' in profile: flags.append('+X3')
    if source_row:
        for flag in source_row.get('compile_flags', []):
            if flag not in flags: flags.append(flag)
    if 'aztec36' not in profile.lower(): raise ValueError('unknown compiler profile: ' + profile)
    return flags

def assert_unique_entry_names(names):
    normalized=[str(name).casefold() for name in names]
    duplicates=sorted(name for name,count in collections.Counter(normalized).items() if count>1)
    if duplicates: raise ValueError('duplicate staged entry names: '+', '.join(duplicates))
    return True

def select_accepted_sources(inv, ledger, root, active_path, digest_file):
    """Select accepted production sources against the live ledger and inventory."""
    provider_source_paths = {rec['source'] for rec in ledger.get('data_providers', {}).values()}
    accepted_sources = {}
    for ledger_key in ('functions', 'behavioral_functions', 'dead_code_functions', 'mixed_source_objects', 'reconstructed_asm'):
        for member_id, rec in ledger.get(ledger_key, {}).items():
            if ledger_key == 'functions' and member_id == 'ov11_F_66FE':
                continue
            accepted_sources[rec['source']] = rec
    for rec in ledger.get('code_data_providers', {}).values():
        for source, source_sha in rec.get('sources', {}).items():
            accepted_sources[source] = dict(source=source, source_sha256=source_sha, proof=rec.get('proof'),
                                            proof_sha256=rec.get('proof_sha256'), state='DATA_LAYOUT_MATCH')
    selected_rows = [row for row in inv['sources'] if row.get('selected')]
    overlap_provider_paths = sorted(row['source'] for row in selected_rows if row['source'] in provider_source_paths)
    src_rows = []
    for row in selected_rows:
        source = row['source']
        if source in provider_source_paths or source == 'src/recovered/ov11/ov11_F_66FE.c':
            continue
        if any(part.lower() in ('unit', 'units') for part in Path(source).parts):
            raise ValueError('unit-container source cannot enter the game build: ' + source)
        accepted = accepted_sources.get(source)
        if accepted is None:
            raise ValueError('selected inventory source is not accepted in the current ledger: ' + source)
        if row.get('source_sha256') != accepted.get('source_sha256'):
            raise ValueError('inventory source hash differs from current accepted ledger: ' + source)
        source_path = root / source
        if not active_path(source, root) or digest_file(source_path) != accepted.get('source_sha256'):
            raise ValueError('accepted source hash/path validation failed: ' + source)
        proof = accepted.get('proof')
        proof_sha = accepted.get('proof_sha256')
        if proof and proof_sha and digest_file(root / proof) != proof_sha:
            raise ValueError('accepted proof hash validation failed: ' + proof)
        src_rows.append(dict(row))
    return src_rows, overlap_provider_paths, provider_source_paths

def unique_job_name(ledger_sha256, job_root, requested=None):
    """Choose a queue-safe job name without reusing another pinned worker's job."""
    root = Path(job_root)
    if requested:
        if not re.fullmatch(r'[A-Za-z0-9_-]+', requested):
            raise ValueError('job name must contain only letters, digits, _ or -')
        if (root / requested).exists():
            raise ValueError('worker job already exists: ' + requested)
        return requested
    base = 'luna-game-build-' + ledger_sha256[:12]
    candidate, suffix = base, 2
    while (root / candidate).exists():
        candidate = base + '-' + str(suffix)
        suffix += 1
    return candidate

def unique_data_provider_rows(ledger):
    """Return one deterministic row per DATA source, rejecting ambiguous duplication."""
    rows = sorted(ledger.get('data_providers', {}).items())
    seen = {}
    for provider_id, record in rows:
        source = record['source']
        if source in seen:
            raise ValueError('DATA provider source selected more than once: %s (%s, %s)' % (source, seen[source], provider_id))
        seen[source] = provider_id
    return rows

def derive_missing_symbols(undefined, accepted_symbols, data_aliases=None, reference_plan=None):
    """Current unresolved data globals after accepted providers and staged bindings."""
    aliases=data_aliases or {}; refs=reference_plan or {}; missing=[]
    for row in undefined:
        symbol=row.get('symbol','')
        if row.get('cause') not in ('UNDEFINED_BSS_GLOBAL','UNDEFINED_INITIALIZED_DATA'): continue
        if not symbol or symbol in accepted_symbols or symbol in aliases: continue
        planned=refs.get(symbol)
        if planned and int(planned[1] or 0)==0: continue
        missing.append(row)
    return missing

def alias_view_expression(view, base_symbol, addend, dimensions=()):
    parsed=parse_type(view)
    if not parsed: raise ValueError('alias has no complete typed view: '+str(view))
    base,_declared_dimensions=parsed
    dimensions=tuple(int(n) for n in dimensions)
    base_name=base_symbol[1:] if base_symbol.startswith('_') else base_symbol
    if dimensions:
        pointer_type=base+' *' if len(dimensions)==1 else base+' (*)'+''.join('[%d]'%n for n in dimensions[1:])
        expression='(('+pointer_type+')((char *)&'+base_name+' + '+str(addend)+'))'
    else:
        expression='(*('+base+' *)((char *)&'+base_name+' + '+str(addend)+'))'
    return expression,dimensions

def choose_view(symbol, undef, conflict_map, declaration_map):
    dm = undef.get('data_model') or {}
    if dm.get('type'):
        return dm['type'], 'CURATED_DATA_MODEL:' + str(dm.get('basis', 'unspecified'))
    conf = conflict_map.get(symbol, {})
    views = list(conf.get('views') or []) + list(declaration_map.get(symbol, []))
    ranked = []
    for view in views:
        if isinstance(view, str): text, extent = view, 0
        else:
            text = view.get('view') or view.get('type') or view.get('declaration') or ''
            extent = view.get('extent_bytes') or view.get('extent') or 0
        if text: ranked.append((int(extent or 0), str(text), view))
    if ranked:
        ranked.sort(key=lambda x: (x[0], x[1]), reverse=True)
        extent, text, item = ranked[0]
        return text, 'MAX_DECLARED_VIEW:%s:%s' % (item.get('source', '?') if isinstance(item, dict) else '?', extent)
    # Some globals have a single mechanically parsed view and no conflict row.
    for row in []: pass
    return None, 'NO_TYPED_VIEW'

def parse_type(view):
    if not view: return None
    text = re.sub(r'\b(const|volatile|register|extern|static)\b', '', view).strip()
    text = re.sub(r'\s+', ' ', text)
    m = re.match(r'^(.*?)(\s*(?:\[\s*\d+\s*\]\s*)*)$', text)
    if not m: return None
    base = m.group(1).strip()
    dims = re.findall(r'\[\s*(\d+)\s*\]', m.group(2))
    if not base or base in ('void', 'function', 'UNKNOWN'): return None
    if re.search(r'\[\s*\]', text): return None
    return base, [int(x) for x in dims]

def extract_struct_bodies(source):
    found = {}
    for match in re.finditer(r'\bstruct\s+([A-Za-z_][A-Za-z0-9_]*)\s*\{', source):
        tag = match.group(1); start = match.end(); depth = 1; i = start
        while i < len(source) and depth:
            if source[i] == '{': depth += 1
            elif source[i] == '}': depth -= 1
            i += 1
        if depth == 0:
            body = source[start:i-1].strip()
            if body: found.setdefault(tag, body)
    return found

def c_struct_size(body, struct_bodies, active=()):
    if not body: return None
    size = 0
    max_align = 1
    for declaration in body.strip().strip('{}').split(';'):
        declaration = declaration.strip()
        if not declaration: continue
        m = re.match(r'^(.*?)\s+(.+)$', declaration)
        if not m: return None
        base, declarators = m.group(1).strip(), m.group(2).strip()
        for decl in declarators.split(','):
            decl = decl.strip()
            ptr = '*' in decl or '*' in base
            array = re.findall(r'\[\s*(0x[0-9a-fA-F]+|\d+)\s*\]', decl)
            if ptr: field_size = 4
            elif base in ('char','signed char','unsigned char'): field_size = 1
            elif base in ('short','unsigned short','int','unsigned int'): field_size = 2
            elif base in ('long','unsigned long','float','void *'): field_size = 4
            elif base.startswith('struct '):
                tag = base.split(None,1)[1]
                if tag in active or tag not in struct_bodies: return None
                field_size = c_struct_size(struct_bodies[tag], struct_bodies, active+(tag,))
                if field_size is None: return None
            else: return None
            count = 1
            for dim in array:
                try: count *= int(dim, 0)
                except ValueError: return None
            field_size *= count
            align = 1 if field_size == 1 else 2
            size = (size + align - 1) // align * align
            size += field_size
            max_align = max(max_align, align)
    return (size + max_align - 1) // max_align * max_align

def type_bytes(view, structs=None, explicit_body=None):
    parsed = parse_type(view)
    if not parsed: return None
    base, dims = parsed
    if '*' in base: size = 4
    elif base in ('char','signed char','unsigned char'): size = 1
    elif base in ('short','unsigned short','int','unsigned int'): size = 2
    elif base in ('long','unsigned long','float','void *'): size = 4
    elif base.startswith('struct ') and structs:
        tag = base.split(None, 1)[1]
        body_map = {name: (value[0] if isinstance(value, list) and value else value) for name, value in structs.items()}
        body = explicit_body or body_map.get(tag)
        if not body: return None
        size = c_struct_size(body, body_map)
        if size is None: return None
    else: return None
    for count in dims: size *= count
    return size

def format_build_report(counts, stub_symbols, stub_objects, reservations, unresolved_bytes):
    lines = [
        'Objects by proof category:',
        '  EXACT_C: %d' % counts.get('EXACT_C', 0),
        '  RECOVERED_ASM: %d mixed C/ASM object(s)' % counts.get('MIXED_EXACT_C_AND_RECOVERED_ASM', 0),
        '  RECONSTRUCTED_ASM: %d' % counts.get('RECONSTRUCTED_ASM', 0),
        '  BEHAVIORALLY_RECONSTRUCTED: %d (separate behavioral proof; never exact C)' % counts.get('BEHAVIORALLY_RECONSTRUCTED', 0),
        '  TYPED_CODE_DATA: %d' % counts.get('TYPED_CODE_DATA', 0),
        '  TYPED_DATA providers: %d' % counts.get('DATA_LAYOUT_MATCH', 0),
        '  UNRESOLVED CODE bytes: %s' % (unresolved_bytes if unresolved_bytes is not None else 'unknown'),
        'LINK_ONLY_STUBS (%d symbols in %d objects):' % (len(stub_symbols), len(stub_objects)),
    ]
    by_symbol = {row.get('symbol'): row for row in stub_symbols if row.get('symbol')}
    for obj in stub_objects:
        symbols = obj.get('symbols', [])
        sizes = [by_symbol.get(symbol, {}).get('bytes') for symbol in symbols]
        if obj.get('cause') == 'MEASURED_RESERVATION':
            total = obj.get('bytes')
        elif sizes and all(value is not None for value in sizes):
            total = sum(sizes)
        else:
            total = None
        names = ', '.join(symbols[:4]) + (' ?' if len(symbols) > 4 else '')
        lines.append('  %s: %s bytes; %d symbol(s); %s' %
                     (obj.get('object', obj.get('file', 'stub')), total if total is not None else 'unknown', len(symbols), names))
    lines.append('Per-symbol LINK_ONLY_STUBS list:')
    for row in stub_symbols:
        size=row.get('bytes')
        lines.append('  %s: %s bytes; %s' % (row.get('symbol'), size if size is not None else 'unknown', row.get('cause','link-only')))
    for row in reservations:
        lines.append('  %s: %d bytes; MEASURED_RESERVATION; zero-fill only, recovery credit 0' %
                     (row.get('anchor'), row.get('bytes', row['end']-row['start'])))
    lines.append('STUB_FREE: %s' % ('YES' if not stub_symbols and not reservations else 'NO'))
    lines.append('Full per-symbol list: LINK_ONLY_STUBS/manifest.json')
    return '\n'.join(lines)

def topology_report(image_path):
    sys.path.insert(0, str(ROOT/'tools'))
    import hunk
    from ofs import OFSDisk
    raw=Path(image_path).read_bytes()
    linked=hunk.parse(raw)
    linked_tree=hunk.manx_overlay(linked,raw)
    cfg=read_json(ROOT/'docs/toolchain.json')['game_trace']
    disk_path=Path(cfg['disks'][0]['source'])
    if not disk_path.is_absolute(): disk_path=ROOT/disk_path
    disk=OFSDisk(disk_path.read_bytes()); disk.parse()
    original_raw=disk.files['DuckTales']
    original=hunk.parse(original_raw)
    original_tree=hunk.manx_overlay(original,original_raw)
    def summarize(model,tree,blob):
        root_data=next(row for row in model['hunks'] if row['number']==1)
        h1=blob[root_data['content_offset']:root_data['content_offset']+root_data['initialized_size']]
        reloc={(r['source_offset'],r['target_hunk']) for r in model['relocations']
               if r['source_hunk']==1 and r['type']=='HUNK_RELOC32'}
        jmps=[off for off in range(max(0,min(800,len(h1))-5))
              if h1[off:off+2]==b'\x4e\xf9' and (off+2,0) in reloc]
        return dict(hunk_count=len(model['hunks']),node_header_count=len(model['nodes']),
            nodes=[dict(id=n['id'],first_hunk=n['first_hunk'],last_hunk=n['last_hunk'],hunks=n['hunks']) for n in model['nodes']],
            overlay_slot_count=tree['slot_count'],physical_overlay_count=tree['physical_overlay_count'],
            empty_slots=[x['slot'] for x in tree['slots'] if x['status']=='EMPTY'],
            per_slot_entry_counts=[len(x['symbols']) for x in tree['slots']],
            chip_hunks=[x['number'] for x in model['hunks'] if x['memory_flags_raw']&1],
            root_jmp_slot_count=len(jmps),root_jmp_offsets=jmps,
            hunks=[dict(number=x['number'],node=x['node'],type=x['type'],declared_size=x['declared_size'],
                allocated_size=x['allocated_size'],chip=bool(x['memory_flags_raw']&1)) for x in model['hunks']])
    current=summarize(linked,linked_tree,raw); prior=summarize(original,original_tree,original_raw)
    match=dict(hunk_count=current['hunk_count']==prior['hunk_count'],
        nodes=[x['id'] for x in current['nodes']]==[x['id'] for x in prior['nodes']],
        node_hunk_counts=[len(x['hunks']) for x in current['nodes']]==[len(x['hunks']) for x in prior['nodes']],
        chip_hunks=current['chip_hunks']==prior['chip_hunks'],
        root_jump_slots=current['root_jmp_slot_count']==prior['root_jmp_slot_count'])
    return dict(file=str(Path(image_path)),parse='PASS',bytes=len(raw),sha256=linked['sha256'],
        linked=current,original=prior,topology_match=match,
        note='Root JMP slot differences can come from normally extracted runtime library entries; no post-link patching was applied.')

def data_symbol_offsets(map_path):
    """Hunk-1 (DATA) symbol offsets from an ln map."""
    offsets, current = {}, None
    for line in Path(map_path).read_text(encoding='utf-8', errors='replace').splitlines():
        heading = re.match(r'Segment\s+\d+:\s+Hunk\s+(\d+)', line)
        if heading:
            current = int(heading.group(1)); continue
        m = re.match(r'\s*([0-9a-fA-F]{8})\s+(\S+)', line)
        if current == 1 and m:
            offsets[m.group(2)] = int(m.group(1), 16)
    return offsets


def link_with_original_data_layout(guest, stage, link, data_manifest, passes=3):
    """Link, then lay initialized DATA out at the ORIGINAL relative offsets.

    Accepted DATA providers are separate objects, so raw (unadmitted) spans
    between them collapsed and arrays spanning a gap shifted (G_h01_27E4[48]
    read another object's pointer and the build wrote into audio code). Each
    pass measures every provider's drift in the map and inserts zero-filled,
    labelled LINK_ONLY gap modules before providers whose drift changed. ln
    rounds module data to even sizes, so a 1-byte residue can remain where the
    original packed odd objects back to back; it is reported, not hidden.
    Returns the residual drift steps (empty when every provider is placed exactly)."""
    import vamos_backend as vb
    ledger = read_json(LEDGER_PATH).get('data_providers', {})
    anchors = []  # (original DATA offset, linked symbol, provider object)
    for row in data_manifest:
        fact = read_json(ROOT / ledger[row['id']]['fact'])
        definition = min((d for d in fact.get('definitions', []) if d.get('symbol')),
                         key=lambda d: d.get('offset', 0), default=None)
        if definition is None:
            continue
        anchors.append((fact['original']['start'] + definition.get('offset', 0),
                        '_' + definition['symbol'].lstrip('_'), row['object']))
    anchors.sort()
    guest_cmd, link_args = vb.link_guest_command(link)
    gaps = {}
    lnk = guest / 'link.lnk'
    base_lines = lnk.read_text(encoding='ascii').splitlines()
    residual = None
    for _ in range(passes):
        lines = []
        for line in base_lines:
            if line in gaps:
                lines.append('LINK_ONLY_STUBS/gap_%s.o' % line[:-2])
            lines.append(line)
        lnk.write_text('\n'.join(lines) + '\n', encoding='ascii', newline='\n')
        sysroot = stage / 'vamos-sys' / 'link'; sysroot.mkdir(parents=True, exist_ok=True)
        vb._run_guest(vb._runtime()[0], sysroot, vb.toolchain_root(), guest, guest_cmd, link_args,
                      guest / 'link-ln.log', timeout=1800)
        placed = data_symbol_offsets(guest / 'DuckTales.sym')
        rows = [(o, placed[s] - o, obj) for o, s, obj in anchors if s in placed]
        if not rows:
            return 'no provider symbols in map'
        steps = [(rows[i][2], rows[i-1][1] - rows[i][1]) for i in range(1, len(rows)) if rows[i][1] != rows[i-1][1]]
        residual = [(obj, need) for obj, need in steps if need <= 0 or need % 2]
        fixable = [(obj, need - (need % 2)) for obj, need in steps if need > 0 and need - (need % 2) > 0]
        if not fixable:
            break
        for obj, size in fixable:
            gaps[obj] = gaps.get(obj, 0) + size
            name = 'gap_' + obj[:-2]
            source = guest / 'LINK_ONLY_STUBS' / (name + '.asm')
            source.write_text('; LINK_ONLY_STUBS: zero placeholder for raw DATA before %s (%d bytes);\n'
                              '; keeps the original relative DATA layout. NOT recovered data.\n'
                              '\tdseg\n\tds.b %d\n\tend\n' % (obj, gaps[obj], gaps[obj]), encoding='ascii', newline='\n')
            vb._run_guest(vb._runtime()[0], sysroot, vb.toolchain_root(), guest, 'Old1:bin/as',
                          ['-o', 'LINK_ONLY_STUBS/%s.o' % name, 'LINK_ONLY_STUBS/%s.asm' % name],
                          guest / 'LINK_ONLY_STUBS' / (name + '-as.log'), timeout=120)
    return [(obj, need) for obj, need in (residual or [])][:20]


A4_BIAS = 0x7FFE  # Manx small data: A4 = DATA hunk origin + 32766


def symbolize_a4_displacements(text, address_symbols, objname):
    """Staged assembly only: a numeric `-$2c5c(a4)` names a DATA address of the
    ORIGINAL layout (A4 - $2C5C = DATA+$53A2 = G_h01_53A2). Rewrite it to that
    symbol so the linker resolves it for this build's layout. The module must be
    `far data` (absolute data references); accepted sources stay unchanged."""
    pattern = re.compile(r'(-?)\$([0-9A-Fa-f]+)\(a4\)')
    found = pattern.findall(text)
    if not found:
        return text
    if not re.search(r'^\s*far\s+data\b', text, re.M):
        raise SystemExit('numeric A4 displacement outside a far-data module: ' + objname)
    def replace(m):
        displacement = int(m.group(2), 16) * (-1 if m.group(1) else 1)
        address = A4_BIAS + displacement
        symbol = address_symbols.get(address)
        if not symbol:
            raise SystemExit('no symbol for A4 displacement %s in %s (DATA+%04X)' % (m.group(0), objname, address))
        return '_' + symbol
    text = pattern.sub(replace, text)
    names = sorted({'_' + address_symbols[A4_BIAS + int(h, 16) * (-1 if s else 1)] for s, h in found})
    header = ''.join('\tpublic %s\n' % n for n in names)
    return re.sub(r'^(\s*far\s+data\s*\n)', lambda m: m.group(1) + header, text, count=1, flags=re.M)


def command_groups(commands):
    """Split the staged command list into independent cc+as pairs / lone as steps,
    plus the final link."""
    # Shell setup lines (e.g. C:FailAt) only matter inside the WinUAE guest.
    tool = [c for c in commands if re.match(r'Old[12]:bin/', c)]
    body, link = tool[:-1], tool[-1]
    groups, i = [], 0
    while i < len(body):
        if 'bin/cc ' in body[i]:
            groups.append(body[i:i+2]); i += 2
        else:
            groups.append([body[i]]); i += 1
    return groups, link


def redirect_log(command):
    return next((t[1:] for t in command.split() if t.startswith('>')), 'vamos.log')


def run_vamos_build(commands, guest, stage, workers=None):
    """Compile and link the staged build under vamos, in parallel.

    vamos output is byte-identical to WinUAE for float-free Aztec 3.6a sources
    and for the whole-game link (docs/toolchain.json). Float/double sources and
    any compile that opens a math library are returned for the WinUAE worker."""
    from concurrent.futures import ThreadPoolExecutor
    import vamos_backend as vb
    toolchain = vb.toolchain_root(); vamos, _ = vb._runtime()
    workers = workers or vb.worker_count()
    groups, link = command_groups(commands)
    def source_of(group):
        tokens = group[0].split()
        return guest / tokens[-1] if 'bin/cc ' in group[0] else None
    winuae = [g for g in groups if source_of(g) is not None and source_of(g).is_file()
              and vb.has_float_type(source_of(g).read_text(encoding='latin-1'))]
    # Setup steps (e.g. lb extracting crt0 from c.lib) share the work directory
    # with everything else: run them first, serially, never beside a compile.
    setup = [g for g in groups if not re.match(r'Old[12]:bin/(cc|as) ', g[0])]
    todo = [g for g in groups if g not in winuae and g not in setup]
    def run(item):
        # Aztec cc/as write fixed-name temporaries in their current directory,
        # so concurrent steps must not share Work:. Each group runs in a private
        # copy holding only its input (staged sources include only system
        # headers), and its outputs are copied back.
        index, group = item
        sysroot = stage / 'vamos-sys' / str(index)
        shutil.rmtree(sysroot, ignore_errors=True)
        work = sysroot / 'work'; work.mkdir(parents=True)
        source = group[0].split()[-1]
        inputs = {source} if (guest / source).is_file() else set()
        for name in inputs | {'compiler-input.txt'}:
            (work / name).parent.mkdir(parents=True, exist_ok=True); shutil.copy2(guest / name, work / name)
        for command in group:
            guest_cmd, args = vb.link_guest_command(command)
            trace = sysroot / 'cc.trace.log' if guest_cmd.endswith('bin/cc') else None
            vb._run_guest(vamos, sysroot, toolchain, work, guest_cmd, args, work / redirect_log(command),
                          trace=trace, timeout=600)
            if trace is not None and vb.trace_math_libraries(trace.read_bytes()):
                return group
        for path in work.rglob('*'):
            rel = path.relative_to(work).as_posix()
            if path.is_file() and rel not in inputs and rel != 'compiler-input.txt':
                (guest / rel).parent.mkdir(parents=True, exist_ok=True); shutil.copy2(path, guest / rel)
        return None
    for item in enumerate(setup, start=len(todo)):
        require_none = run(item)
        if require_none is not None:
            raise SystemExit('setup step opened a math library: ' + item[1][0])
    with ThreadPoolExecutor(max_workers=workers) as pool:
        winuae += [g for g in pool.map(run, enumerate(todo)) if g is not None]
    return winuae, link


def main():
    ap = argparse.ArgumentParser()
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument('--report', action='store_true', help='derive current selection/stubs and report completeness')
    mode.add_argument('--build', action='store_true', help='compile and link the selected from-source build')
    ap.add_argument('--output-dir', type=Path, default=ROOT/'build/game')
    ap.add_argument('--job', help='optional unused shared worker-job name; default derives a fresh name from the ledger hash')
    ap.add_argument('--backend', choices=('vamos','winuae'), default='vamos',
                    help='vamos: parallel, float/math compiles routed to WinUAE; winuae: one WinUAE job for everything')
    args = ap.parse_args()
    global STAGE, GUEST
    STAGE = args.output_dir if args.output_dir.is_absolute() else ROOT/args.output_dir
    STAGE = STAGE.resolve()
    GUEST = STAGE/'guest_source'
    inv = read_json(INV_PATH); ledger = read_json(LEDGER_PATH)
    data_provider_rows = unique_data_provider_rows(ledger)
    sys.path.insert(0, str(ROOT/'tools'))
    from data_model import derive_storage_plan
    storage_plan = derive_storage_plan(read_json(ROOT/'recovery/storage_curation.json'), ROOT)
    storage_aliases = storage_plan.get('derived',{}).get('aliases',{})
    # DATA-hunk address -> mechanical name (resident h01 names encode their offset).
    address_symbols = {int(n[6:], 16): n for n in storage_aliases if re.fullmatch(r'G_h01_[0-9A-F]{4}', n)}
    storage_plan_sha256 = sha(json.dumps(storage_plan, sort_keys=True, default=str).encode('utf-8'))
    git = subprocess.run(['git','-c','safe.directory='+ROOT.as_posix(),'rev-parse','HEAD'], cwd=ROOT, capture_output=True, text=True, check=True)
    head = git.stdout.strip()
    inv_hash = digest(INV_PATH); ledger_hash = digest(LEDGER_PATH)
    if not STAGE.exists(): STAGE.mkdir(parents=True)
    if not GUEST.exists(): GUEST.mkdir(parents=True)
    else:
        existing = list(GUEST.iterdir())
        if existing and not (args.build or args.report):
            raise SystemExit('guest_source is already populated; use --report or --build')
    src_rows, overlap_provider_paths, provider_source_paths = select_accepted_sources(
        inv, ledger, ROOT, is_active_repo_path, digest)
    # The accepted mixed exit objects collide with c.lib's canonical exit names.
    # Keep the accepted bodies intact but give the staging entries unique physical names;
    # planned references below are then routed to those entries.
    unique_exit_entries = {
        'src/recovered/resident/resident_F_8534.c': ('_recovered_exit_8534', 'recovered_exit_8534'),
        'src/recovered/resident/resident_F_8552.c': ('_recovered_exit_8552', 'recovered_exit_8552'),
    }
    for index, row in enumerate(src_rows):
        if row['source'] not in unique_exit_entries:
            continue
        row = dict(row)
        contract = dict(row.get('materialize_entry') or {})
        emit_symbol, emit_c_identifier = unique_exit_entries[row['source']]
        contract['emit_symbol'] = emit_symbol
        contract['emit_c_identifier'] = emit_c_identifier
        contract['reason'] = 'unique mechanics staging name; routes planned recovered exit references away from c.lib duplicate names'
        row['materialize_entry'] = contract
        src_rows[index] = row
    # Include the two current accepted RECONSTRUCTED_ASM providers missing from the
    # static link inventory. These stay separate objects and remain production inputs.
    accepted_asm_specs = {
        'resident_frameless_57D2': {
            'definitions': ['_recon_h00_57D2', '_end_stackstart'],
            'insert_before_source': 'src/recovered/asm-reconstructed/resident_driver_57E4.asm',
        },
        'resident_frameless_701A': {
            'definitions': ['_recon_h00_6FDE', '_recon_h00_701A', '_recon_h00_702E', '_end_debugfmt'],
            'insert_before_source': None,
        },
    }
    accepted_asm_rows = {}
    existing_source_paths = {r['source'] for r in src_rows}
    for key, spec in accepted_asm_specs.items():
        rec = ledger.get('reconstructed_asm', {}).get(key)
        if not rec:
            raise SystemExit('current ledger lacks accepted ASM provider ' + key)
        if digest(ROOT / rec['source']) != rec['source_sha256']:
            raise SystemExit('accepted ASM source hash differs: ' + key)
        if digest(ROOT / rec['proof']) != rec['proof_sha256']:
            raise SystemExit('accepted ASM proof hash differs: ' + key)
        if rec['source'] in existing_source_paths:
            continue
        row = dict(source=rec['source'], source_sha256=rec['source_sha256'], proof=rec['proof'],
                   proof_category='RECONSTRUCTED_ASM', definitions=spec['definitions'], materialize_entry=None)
        src_rows.append(row)
        existing_source_paths.add(rec['source'])
        accepted_asm_rows[key] = row
    selected_by_path = {r['source']: r for r in src_rows}
    selected_inventory_source_record_count = len(src_rows)
    inventory_obj_rows = []
    for source_object in inv['objects']:
        retained_sources = [source for source in source_object['sources'] if source not in provider_source_paths]
        if not retained_sources:
            continue
        filtered = dict(source_object)
        filtered['sources'] = retained_sources
        inventory_obj_rows.append(filtered)
    selected_inventory_object_count = len(inventory_obj_rows)
    stage_names_by_inventory = collections.defaultdict(list)
    obj_rows = []
    # The sources are accepted function/module TUs. Preserve the inventory order and
    # profile, but don't merge independent C namespaces without object-membership evidence.
    for inventory_obj in inventory_obj_rows:
        source_count = len(inventory_obj['sources'])
        for source_index, source_path in enumerate(inventory_obj['sources']):
            row = selected_by_path[source_path]
            staged_obj = dict(inventory_obj)
            staged_obj['_inventory_object'] = inventory_obj['object']
            staged_obj['_source_index'] = source_index
            staged_obj['sources'] = [source_path]
            staged_obj['members'] = [Path(source_path).stem]
            staged_obj['definitions'] = row.get('definitions', [])
            contract = row.get('materialize_entry') or {}
            if contract.get('emit_symbol'):
                staged_obj['link_exports'] = [contract['emit_symbol']]
            if source_count > 1:
                original_path = Path(inventory_obj['object'])
                staged_obj['object'] = (original_path.parent / (original_path.stem + '_s%02d' % source_index + original_path.suffix)).as_posix()
            obj_rows.append(staged_obj)
    accepted_asm_obj_rows = {}
    for key, row in accepted_asm_rows.items():
        staged_obj = dict(_inventory_object='accepted_asm/' + key, _source_index=0,
                          object='o/accepted_' + key + '.o', sources=[row['source']],
                          members=[Path(row['source']).stem], definitions=row['definitions'],
                          link_exports=row['definitions'], profiles=['aztec36 as'], node='root', hunk=0,
                          link_reference_plan=[])
        obj_rows.append(staged_obj)
        accepted_asm_obj_rows[key] = staged_obj
    object_profiles = {}
    symbol_to_phys = {}
    symbol_to_c = {}
    for row in src_rows:
        contract = row.get('materialize_entry')
        if contract:
            for sym in row.get('definitions', []):
                symbol_to_phys[sym] = contract['emit_symbol']
                symbol_to_c[sym] = contract['emit_c_identifier']
    ref_map = {}
    data_aliases = {}
    for obj in obj_rows:
        for item in obj.get('link_reference_plan', []):
            source, target = item.get('source_symbol'), item.get('target_symbol')
            addend = int(item.get('addend') or 0)
            if source and target and source != target:
                ref_map[source] = (target, addend, item.get('binding_kind'), item.get('status'))
            if source and target and addend and source.startswith('_G_') and target.startswith('_G_'):
                data_aliases[source] = (target, addend)
    for symbol, (target, addend, _, _) in ref_map.items():
        if symbol.startswith('_F_') and symbol in symbol_to_phys:
            continue
        if addend == 0:
            symbol_to_phys.setdefault(symbol, target)
            cname = c_name(target)
            if cname: symbol_to_c.setdefault(symbol, cname)
    accepted_asm_symbol_remaps = {
        '_F_h00_57D2': ('_recon_h00_57D2', 'recon_h00_57D2'),
        '_F_h00_701A': ('_recon_h00_701A', 'recon_h00_701A'),
    }
    for old, (physical, cname) in accepted_asm_symbol_remaps.items():
        symbol_to_phys[old] = physical
        symbol_to_c[old] = cname
    # Add only plan-backed aliases whose source and typed stub anchor lie inside the
    # exact same typed storage-plan member. This does not bridge unbounded gaps.
    storage_plan_aliases = []
    undefined_by_symbol = {x['symbol']: x for x in inv.get('undefined_symbols', [])}
    storage_objects = storage_plan.get('derived', {}).get('objects', [])
    for source_symbol, source_item in undefined_by_symbol.items():
        if source_item.get('cause') not in ('UNDEFINED_BSS_GLOBAL', 'UNDEFINED_INITIALIZED_DATA'):
            continue
        if source_symbol in data_aliases:
            continue
        source_name = source_symbol.lstrip('_')
        source_row = storage_aliases.get(source_name, {})
        if source_row.get('alias_kind') != 'INTERIOR':
            continue
        source_address = source_row.get('address')
        if source_address is None:
            continue
        choices = []
        for target_name, target_row in storage_aliases.items():
            target_symbol = '_' + target_name
            if target_symbol not in undefined_by_symbol or target_symbol == source_symbol:
                continue
            target_item = undefined_by_symbol[target_symbol]
            if target_item.get('cause') not in ('UNDEFINED_BSS_GLOBAL', 'UNDEFINED_INITIALIZED_DATA'):
                continue
            if target_row.get('object') != source_row.get('object'):
                continue
            modeled_type = target_row.get('modeled_type')
            if not modeled_type or modeled_type == 'UNKNOWN':
                continue
            target_address = target_row.get('address')
            if target_address is None or target_address > source_address:
                continue
            for plan_object in storage_objects:
                if plan_object.get('id') != target_row.get('object'):
                    continue
                for member in plan_object.get('members', []):
                    start, end = member.get('start'), member.get('end')
                    if member.get('type') != modeled_type or start is None or end is None:
                        continue
                    if target_address == start and start <= source_address < end:
                        choices.append((source_address-target_address, target_symbol, modeled_type, member.get('name'), start, end))
        if choices:
            delta, target_symbol, modeled_type, member_name, start, end = min(choices)
            data_aliases[source_symbol] = (target_symbol, delta)
            storage_plan_aliases.append(dict(source=source_symbol,target=target_symbol,addend=delta,
                storage_object=source_row.get('object'),member=member_name,member_type=modeled_type,
                member_start=start,member_end=end,evidence='source and target are in one typed storage-plan member'))
    # A name inside an accepted provider's object is a view of that provider at
    # its offset (G_h01_0971 is byte 1 of the int provider G_h01_0970). A separate
    # stand-in would read zero instead of the provider's value (the depth, 5).
    provider_symbols = set()
    for rec in read_json(LEDGER_PATH).get('data_providers', {}).values():
        for definition in read_json(ROOT/rec['fact']).get('definitions', []):
            if definition.get('symbol'):
                provider_symbols.add(definition['symbol'].lstrip('_'))
    base_of_object = {a.get('object'): name for name, a in storage_aliases.items()
                      if a.get('offset') == 0 and name in provider_symbols}
    for symbol, item in undefined_by_symbol.items():
        if item.get('cause') not in ('UNDEFINED_INITIALIZED_DATA', 'UNDEFINED_BSS_GLOBAL') or symbol in data_aliases:
            continue
        if symbol.lstrip('_') in provider_symbols:
            continue  # defined by an accepted provider (the inventory predates it)
        row = storage_aliases.get(symbol.lstrip('_'), {})
        base = base_of_object.get(row.get('object'))
        if base and row.get('offset'):
            data_aliases[symbol] = ('_' + base, row['offset'])
    # BSS layout: every storage-plan object in the zero-fill region becomes ONE
    # zero-fill reservation over its measured extent, and every undefined BSS
    # name inside it is a view at anchor+offset. Field relations inside an object
    # (e.g. the MemHeader at 542A whose fields 543A..5446 are written by name)
    # therefore hold as in the original; separate one-cell stubs broke them.
    # Zero-fill is what the original BSS held at load. Not a type or capacity claim.
    bss_start = 0x2EB4
    members_by_object = collections.defaultdict(list)
    for symbol, item in undefined_by_symbol.items():
        if item.get('cause') != 'UNDEFINED_BSS_GLOBAL' or symbol in data_aliases:
            continue
        row = storage_aliases.get(symbol.lstrip('_'), {})
        if row.get('object') and row.get('address') is not None and row['address'] >= bss_start:
            members_by_object[row['object']].append((row['address'], symbol))
    measured_reservations = []
    reservation_aliases = []
    reserved_symbols = set()
    objects_by_id = {x.get('id'): x for x in storage_objects}
    for object_id, members in sorted(members_by_object.items()):
        plan_object = objects_by_id.get(object_id) or {}
        start, end = plan_object.get('start'), plan_object.get('end')
        if start is None or end is None or start < bss_start or not all(start <= a < end for a, _ in members):
            continue
        # Keep each member's original word parity: start the span on the even
        # address at or below the object, and make the span even-sized.
        start -= start & 1
        end += end & 1
        anchor = '_LINK_ONLY_RES_H01_%04X' % start
        measured_reservations.append(dict(target=min(members)[1], object=object_id, start=start, end=end,
            bytes=end-start, anchor=anchor, status=plan_object.get('status'), members=len(members),
            classification='MEASURED_RESERVATION', recovery_credit=0,
            claim='zero-fill link span of one storage-plan object; not a type or capacity claim'))
        for address, symbol in members:
            reserved_symbols.add(symbol)
            reservation_aliases.append(dict(symbol=symbol, anchor=anchor, offset=address-start,
                address=address, object=object_id))
    # Word alignment can make adjacent objects overlap (an object at an odd
    # address rounds down into its neighbour): merge overlapping spans into one
    # block so every address is reserved, and labelled, exactly once.
    measured_reservations.sort(key=lambda r: r['start'])
    merged, renamed = [], {}
    for row in measured_reservations:
        if merged and row['start'] < merged[-1]['end']:
            last = merged[-1]
            if row['anchor'] != last['anchor']:  # equal anchors: same block, no rename
                renamed[row['anchor']] = last['anchor']
            last['end'] = max(last['end'], row['end']); last['bytes'] = last['end'] - last['start']
            last['members'] += row['members']; last['object'] += '+' + row['object']
        else:
            merged.append(row)
    measured_reservations = merged
    by_anchor = {r['anchor']: r for r in merged}
    for alias in reservation_aliases:
        anchor = renamed.get(alias['anchor'], alias['anchor'])
        while anchor in renamed: anchor = renamed[anchor]
        alias['anchor'] = anchor; alias['offset'] = alias['address'] - by_anchor[anchor]['start']
    # These two unresolved globals are initialized-DATA stubs, not BSS reservations.
    for target in ('_G_h01_27E4', '_G_h01_2A12'):
        data_aliases.pop(target, None)

    # Runtime callbacks in recovered exits are the game storage used by pinned library clients.
    runtime_library_storage_aliases = {
        '_cls_': dict(target='_G_h01_B3C4', evidence='accepted F_h00_8534 invokes the callback stored at h1+B3C4; pinned stdio.arc flsh_ assigns cls_=closall'),
        '__cln': dict(target='_G_h01_B3C8', evidence='accepted F_h00_8552 invokes the cleanup callback stored at h1+B3C8; pinned misc.arc lmalloc assigns _cln=cleanup'),
    }
    for source_symbol, row in runtime_library_storage_aliases.items():
        data_aliases[source_symbol] = (row['target'], 0)
    # Convert C-consumed storage interiors into typed source views of their base
    # objects. Keep the old assembler EQU only where a real ASM consumer still needs it.
    reservation_alias_symbols = {x['symbol'] for x in reservation_aliases}
    interior_aliases = {}
    for sym, (target, addend) in data_aliases.items():
        plan_row = storage_aliases.get(sym.lstrip('_'), {})
        if plan_row.get('alias_kind') == 'INTERIOR' or sym in reservation_alias_symbols or (sym.startswith('_G_h01_') and addend != 0):
            interior_aliases[sym] = (target, addend)
    assembler_alias_references = set()
    asm_block_re = re.compile(r'#asm\b[\s\S]*?#endasm\b', re.IGNORECASE)
    for obj in obj_rows:
        for source_path in obj.get('sources', []):
            source_text = (ROOT / source_path).read_text(encoding='utf-8')
            if source_path.endswith('.asm'):
                asm_text = source_text
            else:
                asm_text = '\n'.join(asm_block_re.findall(source_text))
            for sym in interior_aliases:
                if re.search(r'(?<![A-Za-z0-9_])' + re.escape(sym.lstrip('_')) + r'(?![A-Za-z0-9_])', asm_text):
                    assembler_alias_references.add(sym)
    emitted_data_aliases = {sym: value for sym, value in data_aliases.items()
                            if sym not in interior_aliases or sym in assembler_alias_references}
    alias_lines = ['; LINK MATERIALIZATION ONLY: symbol aliases, not reconstructed game code/data.\n',
                   '\tfar data\n', '\tdseg\n']
    for sym, (target, addend) in sorted(emitted_data_aliases.items()):
        alias_lines.append('\tpublic ' + target + '\n')
        alias_lines.append('\tcseg\n\tpublic ' + sym + '\n')
        addend_expr = ('+%d' % addend) if addend > 0 else (str(addend) if addend < 0 else '')
        alias_lines.append(sym + ' equ ' + target + addend_expr + '\n')
        alias_lines.append('\tdseg\n')
    if emitted_data_aliases:
        alias_lines.append('\tend\n')
        (GUEST/'LINK_MATERIALIZATION').mkdir(exist_ok=True)
        alias_path = GUEST/'LINK_MATERIALIZATION'/'data_aliases.asm'
        alias_path.write_text(''.join(alias_lines), encoding='ascii', newline='\n')
    else: alias_path = None

    compile_entries = []
    production_inputs = []
    object_args = []
    node_objects = collections.defaultdict(list)
    source_manifest = []
    source_view_alias_records = []
    source_view_array_address_adjustments = []
    staging_identifier_renames = []
    macro_unhandled = []
    # Define only the inventory-selected objects. Joined members are materialized as one TU.
    for oi, obj in enumerate(obj_rows):
        objname = 'obj_' + Path(obj['object']).stem + '.o'
        profile_set = set(obj.get('profiles') or [])
        if len(profile_set) != 1: raise SystemExit('object profile mix needs explicit recipe: ' + obj['object'] + ' ' + repr(profile_set))
        profile = next(iter(profile_set)); flags = clean_flags(profile)
        rows = []
        for src in obj['sources']:
            if src not in selected_by_path: raise SystemExit('object references non-selected source: ' + src)
            rows.append(selected_by_path[src])
        if not rows: raise SystemExit('empty selected object ' + obj['object'])
        contents = []
        for row in rows:
            original = (ROOT/row['source']).read_text(encoding='utf-8')
            if row['source'] in {
                'src/recovered/ov11/ov11_F_2C96.c',
                'src/recovered/ov11/ov11_F_3926.c',
                'src/recovered/ov11/ov11_F_506A.c',
                'src/recovered/ov11/ov11_F_67B0.c',
                'src/recovered/ov11/ov11_F_6A44.c',
                'src/recovered/ov11/ov11_F_7194.c',
            }:
                # The runtime entry is C identifier `index`; these six TUs also use
                # a local variable with that name, so rename only the local identifier
                # in this generated staging copy to keep the direct `_index` call.
                original = token_replace(original, 'index', 'link_local_index')
                staging_identifier_renames.append(dict(source=row['source'],from_identifier='index',to_identifier='link_local_index',reason='avoid shadowing pinned `_index` C identifier'))
            if sha((ROOT/row['source']).read_bytes()) != row['source_sha256']:
                raise SystemExit('accepted source hash differs from inventory: ' + row['source'])
            contract = row.get('materialize_entry')
            if contract:
                old = contract['from_source']; new = contract['emit_c_identifier']
                if not re.search(r'(?<![A-Za-z0-9_])'+re.escape(old)+r'(?![A-Za-z0-9_])', original):
                    raise SystemExit('entry token absent: ' + row['source'] + ' / ' + old)
                original = token_replace(original, old, new)
            original = remap_inline_asm(original, symbol_to_phys)
            if row['source'].endswith('.asm'):
                contents.append('; staged from accepted source: %s; proof class: %s\n%s\n' %
                                (row['source'], row.get('proof_category'), original))
            else:
                contents.append('/* staged from accepted source: %s; source/proof class: %s */\n%s\n' %
                                (row['source'], row.get('proof_category'), original))
            source_manifest.append(dict(source=row['source'], sha256=row['source_sha256'], proof=row.get('proof'),
                                        proof_category=row.get('proof_category'), object=obj['object'], materialize_entry=contract))
        text = '\n'.join(contents)
        c_body_for_alias_check = text
        is_asm = all(r['source'].endswith('.asm') for r in rows)
        if any(r['source'].endswith('.asm') for r in rows) and not is_asm:
            raise SystemExit('mixed C/ASM source group unsupported: ' + obj['object'])
        if not is_asm:
            macros = {}
            for sym, phys in symbol_to_phys.items():
                if sym in interior_aliases: continue
                cname = symbol_to_c.get(sym) or c_name(phys)
                if cname and sym.startswith('_'):
                    macro = sym[1:]
                    if macro != cname: macros[macro] = cname
            for sym, (target, addend, kind, status) in ref_map.items():
                if sym in interior_aliases: continue
                # A staged recovered definition's unique symbol takes precedence over
                # the inventory's canonical runtime-name binding for that call site.
                if addend or sym in symbol_to_phys: continue
                cname = symbol_to_c.get(sym) or c_name(target)
                if cname and sym.startswith('_'):
                    macro = sym[1:]
                    if macro != cname: macros[macro] = cname
                elif target.startswith('.'):
                    macro_unhandled.append(dict(object=obj['object'], source_symbol=sym, target_symbol=target, reason='assembler/compiler runtime entry; not a C identifier'))
            preamble = '/* Link-name materialization macros only. */\n' + ''.join('#define %s %s\n' % kv for kv in sorted(macros.items()))
            # Supply missing external views from the current typed storage model;
            # accepted source files remain untouched. This fixes omitted unit headers.
            type_declarations = []
            for source_row in rows:
                original_source = (ROOT/source_row['source']).read_text(encoding='utf-8')
                names = sorted(set(re.findall(r'\bG_h01_[0-9A-Fa-f]{4}\b', original_source)))
                for name in names:
                    if re.search(r'\b(?:extern|static)\b[^;]*\b'+re.escape(name)+r'\b', original_source): continue
                    plan_row = storage_aliases.get(name, {})
                    view = plan_row.get('modeled_type')
                    if not view or view == 'UNKNOWN':
                        candidates=[v for v in plan_row.get('views',[]) if v.get('type') and v.get('type')!='UNKNOWN']
                        candidates.sort(key=lambda v:(len(v.get('sources',[])),int(v.get('declared_extent') or 0),v.get('type','')))
                        view=candidates[-1].get('type') if candidates else None
                    if not view or view == 'UNKNOWN': continue
                    m = re.fullmatch(r'(.+?)(\s*(?:\[\s*\d+\s*\]\s*)*)', view)
                    if not m: continue
                    base_type, dims = m.group(1).strip(), m.group(2)
                    if base_type.startswith('struct '): continue
                    type_declarations.append('extern %s %s%s;\n' % (base_type, name, dims))
            # UiState's complete tag is independently declared in an accepted source.
            if 'struct UiState' in text and 'struct UiState {' not in text:
                ui_source = ROOT/'src/recovered/ov13/ov13_F_0000.c'
                ui_body = extract_struct_bodies(ui_source.read_text(encoding='utf-8')).get('UiState') if ui_source.is_file() else None
                if ui_body:
                    preamble += 'struct UiState { %s };\n' % ui_body.strip().strip('{}').strip()
            preamble += ''.join(sorted(set(type_declarations)))
            # Use the exact TU-local declaration as the view type, remove that extern,
            # and address the base through a char pointer so the linker sees only the
            # base data symbol in A4-relative relocations.
            c_without_asm = asm_block_re.sub(' ', c_body_for_alias_check)
            c_without_asm = re.sub(r'/\*[\s\S]*?\*/|//[^\n]*', ' ', c_without_asm)
            alias_macro_lines = []
            alias_base_declarations = []
            for alias_symbol, (base_symbol, addend) in sorted(interior_aliases.items()):
                alias_name = alias_symbol.lstrip('_')
                if not re.search(r'(?<![A-Za-z0-9_])' + re.escape(alias_name) + r'(?![A-Za-z0-9_])', c_without_asm):
                    continue
                def decl_pattern(name):
                    return re.compile(r'(?:extern[ \t]+)?(?P<type>[A-Za-z_]\w*(?:[ \t]+[A-Za-z_]\w*)*(?:[ \t]*\*)*)[ \t]+'
                                      + re.escape(name) + r'(?P<dims>(?:[ \t]*\[[ \t]*\d+[ \t]*\])*)[ \t]*;')
                ap = decl_pattern(alias_name)
                alias_decls = list(ap.finditer(text))
                if not alias_decls:
                    raise SystemExit('C interior alias has no TU-local declaration/view: ' + obj['object'] + ' ' + alias_symbol)
                views = {(m.group('type').strip(), tuple(re.findall(r'\[\s*(\d+)\s*\]', m.group('dims')))) for m in alias_decls}
                if len(views) != 1:
                    raise SystemExit('C interior alias has conflicting TU-local views: ' + obj['object'] + ' ' + alias_symbol + ' ' + repr(views))
                view_type, dimensions = next(iter(views))
                expression, dimensions = alias_view_expression(view_type, base_symbol, addend, dimensions)
                text = ap.sub('', text)
                base_name = base_symbol.lstrip('_')
                bp = decl_pattern(base_name)
                base_already_declared = bool(bp.search(preamble + text))
                if not base_already_declared and not re.search(r'(?m)^\s*#\s*define\s+' + re.escape(base_name) + r'\b', preamble + text):
                    alias_base_declarations.append('extern char %s;\n' % base_name)
                alias_macro_lines.append('#define %s %s\n' % (alias_name, expression))
                if dimensions:
                    address_pattern = re.compile(r'(\(\s*char\s*\*\s*\)\s*)&\s*' + re.escape(alias_name) + r'\b')
                    text, address_replacements = address_pattern.subn(lambda m: m.group(1) + alias_name, text)
                    if address_replacements:
                        source_view_array_address_adjustments.append(dict(object=obj['object'], source=rows[0]['source'],
                            alias_symbol=alias_symbol, replacements=address_replacements,
                            rewrite='(char *)&ARRAY_VIEW to (char *)ARRAY_VIEW because the source view macro is a pointer expression'))
                source_view_alias_records.append(dict(object=obj['object'], source=rows[0]['source'],
                    alias_symbol=alias_symbol, base_symbol=base_symbol, addend=addend, view_type=view_type,
                    array_dimensions=[int(x) for x in dimensions], declaration_removed=len(alias_decls),
                    base_extern_injected=not base_already_declared, replacement=expression,
                    profile=profile, emitted_code_changes='address arithmetic through the base symbol'))
            preamble += ''.join(sorted(set(alias_base_declarations)))
            preamble += ''.join(alias_macro_lines)
            text = preamble + text
        else:
            for sym, phys in sorted(symbol_to_phys.items(), key=lambda kv: -len(kv[0])):
                if sym != phys: text = token_replace(text, sym, phys)
            for sym, (target, addend, kind, status) in sorted(ref_map.items(), key=lambda kv: -len(kv[0])):
                if addend: continue
                if sym != target: text = token_replace(text, sym, target)
        if is_asm:
            text = symbolize_a4_displacements(text, address_symbols, objname)
        relsrc = Path('tu')/(Path(objname).stem + ('.asm' if is_asm else '.c'))
        dst = GUEST/relsrc; dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_text(text, encoding='ascii', newline='\n')
        if is_asm:
            compile_entries.append(dict(source=relsrc.as_posix(), object=objname, kind='asm', profile=profile, flags=[],
                                        log=objname[:-2]+'-as.log'))
        else:
            compile_entries.append(dict(source=relsrc.as_posix(), object=objname, kind='c', profile=profile, flags=flags,
                                        log=objname[:-2]+'-cc.log', as_log=objname[:-2]+'-as.log'))
        object_args.append(objname); node_objects[str(obj['node'])].append(objname)
        stage_names_by_inventory[obj['_inventory_object']].append(objname)
        production_inputs.append(dict(inventory_object=obj['_inventory_object'], object=obj['object'], staged_object=objname, node=obj['node'], hunk=obj['hunk'],
                                      members=obj['members'], sources=obj['sources'], profile=profile, flags=flags,
                                      expected_definitions=obj.get('link_exports') or obj.get('definitions', [])))
    # Current accepted DATA providers postdate the static inventory. Keep each provider in its own object.
    data_manifest = []
    for provider_id, rec in data_provider_rows:
        src_path = rec['source']; fact_path = ROOT/rec['fact']; src_path_abs = ROOT/src_path
        if not is_active_repo_path(src_path, ROOT) or digest(src_path_abs) != rec['source_sha256']:
            raise SystemExit('DATA provider source hash/path differs: ' + provider_id)
        if rec.get('proof') and rec.get('proof_sha256') and digest(ROOT/rec['proof']) != rec['proof_sha256']:
            raise SystemExit('DATA provider proof hash differs: ' + provider_id)
        fact = read_json(fact_path)
        profile = fact.get('producer', {}).get('profile', 'aztec36')
        flags = clean_flags(profile)
        src = src_path_abs.read_text(encoding='utf-8')
        # Apply only explicit object-level aliases from the inventory; provider definitions themselves keep canonical names.
        macros = {}
        for sym, (target, addend, kind, status) in ref_map.items():
            if addend: continue
            cname = symbol_to_c.get(sym) or c_name(target)
            if cname and sym.startswith('_') and sym[1:] != cname: macros[sym[1:]] = cname
        src = '/* staged accepted DATA provider: %s; proof class: DATA_LAYOUT_MATCH */\n' % provider_id + ''.join('#define %s %s\n' % x for x in sorted(macros.items())) + src
        objname = 'obj_data_' + provider_id + '.o'
        relsrc = Path('tu')/('data_' + provider_id + '.c'); (GUEST/relsrc).write_text(src,encoding='ascii',newline='\n')
        compile_entries.append(dict(source=relsrc.as_posix(),object=objname,kind='c',profile=profile,flags=flags,
                                    log=objname[:-2]+'-cc.log',as_log=objname[:-2]+'-as.log'))
        object_args.append(objname); node_objects['root'].append(objname)
        names=[d['symbol'] for d in fact.get('definitions',[]) if d.get('symbol')]
        for name in names: symbol_to_phys.setdefault('_'+name if not name.startswith('_') else name, '_'+name if not name.startswith('_') else name)
        data_manifest.append(dict(id=provider_id,source=src_path,sha256=rec['source_sha256'],proof=rec['proof'],
                                  proof_sha256=rec['proof_sha256'],profile=profile,object=objname,
                                  original=fact.get('original'),definitions=names,proof_class='DATA_LAYOUT_MATCH'))
    # Optional non-code aliases used by exact link-name/materialization contracts.
    alias_obj = None
    if alias_path:
        alias_obj='link_data_aliases.o'; object_args.append(alias_obj); node_objects['root'].append(alias_obj)
        compile_entries.append(dict(source='LINK_MATERIALIZATION/data_aliases.asm',object=alias_obj,kind='asm',profile='aztec36 as',flags=[],log='link_data_aliases-as.log'))
    # The Manx assembler exports only actual CODE labels here; aliases are 6-byte JMP bridges.
    # They bind c.lib startup calls to the accepted mixed recovery bodies without replacing them.
    exit_bridge_file = Path('LINK_MATERIALIZATION') / 'exit_entry_bridges.asm'
    exit_bridge_lines = [
        '; LINK_MATERIALIZATION ONLY: mechanics JMP bridges to accepted bodies; no recovery credit.',
        '\tfar data',
        '\tcseg',
        '\tpublic _exit',
        '\tpublic _recovered_exit_8534',
        '_exit',
        '\tjmp _recovered_exit_8534',
        '\tpublic __exit',
        '\tpublic _recovered_exit_8552',
        '__exit',
        '\tjmp _recovered_exit_8552',
        '\tdseg',
        '\tend',
        ''
    ]
    (GUEST / exit_bridge_file).parent.mkdir(exist_ok=True)
    (GUEST / exit_bridge_file).write_text(chr(10).join(exit_bridge_lines), encoding='ascii', newline='\n')
    exit_bridge_obj = 'link_exit_entry_bridges.o'
    compile_entries.append(dict(source=exit_bridge_file.as_posix(), object=exit_bridge_obj, kind='asm', profile='aztec36 as', flags=[], log='link_exit_entry_bridges-as.log'))
    object_args.append(exit_bridge_obj)
    node_objects['root'].append(exit_bridge_obj)

    # Create explicit link-only stubs. Their source is isolated and never enters recovery/proof accounting.
    stub_dir = GUEST/'LINK_ONLY_STUBS'; stub_dir.mkdir(exist_ok=True)
    header = ('/* LINK_ONLY_STUBS: synthetic zero storage/return values for this mechanics-only build.\n'
              ' * NOT recovered source, NOT a behavior implementation, and excluded from all recovery counts.\n'
              ' * Replace before any execution or behavioral claim. */\n')
    accepted_names = set()
    for obj in obj_rows:
        accepted_names.update(obj.get('definitions', []))
    for provider_id, rec in data_provider_rows:
        fact=read_json(ROOT/rec['fact'])
        for definition in fact.get('definitions',[]):
            name=definition.get('symbol')
            if name: accepted_names.add('_'+name if not name.startswith('_') else name)
    conflict_map={x['symbol']:x for x in inv.get('extern_view_conflicts',[])}
    declaration_map=collections.defaultdict(list)
    for source_row in src_rows:
        for ext in source_row.get('declared_externs',[]):
            if ext.get('kind') != 'data' or not ext.get('view'): continue
            sym=ext.get('name','')
            sym=sym if sym.startswith('_') else '_'+sym
            declaration_map[sym].append(dict(view=ext['view'],extent_bytes=ext.get('extent_bytes') or 0,source=source_row.get('source')))
    all_structs=collections.defaultdict(list)
    for row in inv['sources']:
        for tag,body in (row.get('struct_definitions') or {}).items():
            if body and body not in all_structs[tag]: all_structs[tag].append(body)
    for entry in inv.get('struct_body_variants',[]):
        tag=entry.get('tag')
        for body in entry.get('bodies',[]):
            if isinstance(body,str): raw=body
            else: raw=body.get('body') or body.get('definition') or body.get('fields') or ''
            if raw and raw not in all_structs[tag]: all_structs[tag].append(raw)
    # Also read simple struct definitions directly from the accepted C inputs; inventory variants are advisory views, not an ownership claim.
    for source_row in src_rows:
        if not source_row['source'].endswith('.c'): continue
        for tag,body in extract_struct_bodies((ROOT/source_row['source']).read_text(encoding='utf-8')).items():
            if body not in all_structs[tag]: all_structs[tag].append(body)
    for provider_id,rec in data_provider_rows:
        for tag,body in extract_struct_bodies((ROOT/rec['source']).read_text(encoding='utf-8')).items():
            if body not in all_structs[tag]: all_structs[tag].append(body)
    undef = inv['undefined_symbols']; stub_items=[]; deferred=[]; runtime_stubs=[]
    manual_link_views={
        '_G_h01_29DE':('unsigned short','audio period anchor; one typed link cell only; no handler slot or table extent inferred'),
        '_G_h01_2A0A':('unsigned char','resident_frameless_5868.asm clr.b; one byte link cell only'),
        '_G_h01_2B4A':('long','resident_driver_5796.asm stores/restores A4 through this pointer slot; one long link cell only'),
        '_G_h01_2B6E':('void *','resident_driver_544C.asm indexed long pointer read; one pointer link cell only; table extent unknown'),
        '_G_h01_2B86':('unsigned short','resident_driver_5D92.asm reads a word; one word link cell only'),
        '_G_h01_2B89':('unsigned char','resident_asm_559E.asm byte access; one byte link cell only'),
        '_G_h01_2B8A':('unsigned char','resident_asm_559E.asm byte access; one byte link cell only'),
        '_G_h01_2BC2':('void *','resident_callback_617C.asm indexed long pointer read; one pointer link cell only; table extent unknown'),
        '_G_h01_2BFE':('void *','resident_callback_61A0.asm pointer table anchor; one pointer link cell only; table extent unknown'),
        '_G_h01_27E4':('unsigned char','supervisor-authorized initialized-DATA link-only cell; one-cell mechanics placeholder, not a type or extent claim'),
        '_G_h01_2A12':('unsigned char','supervisor-authorized initialized-DATA link-only cell; one-cell mechanics placeholder, not a type or extent claim'),
    }
    missing_data_rows = derive_missing_symbols(undef, accepted_names, data_aliases, ref_map)
    missing_data_symbols = {row['symbol'] for row in missing_data_rows}
    for item in undef:
        cause=item['cause']; sym=item['symbol']
        if cause not in ('UNDEFINED_BSS_GLOBAL','UNDEFINED_INITIALIZED_DATA'): continue
        if sym not in missing_data_symbols: continue
        if sym in accepted_names: continue
        # A nonzero typed-interior alias already resolves through the materialization object.
        if sym in data_aliases or sym in reserved_symbols: continue
        if sym in ref_map and ref_map[sym][1] == 0: continue
        view,basis=choose_view(sym,item,conflict_map,declaration_map)
        plan_row=storage_aliases.get(sym.lstrip('_'),{})
        if plan_row.get('modeled_type') not in (None,'UNKNOWN'):
            view=plan_row['modeled_type']; basis='CURATED_STORAGE_PLAN:'+str(plan_row.get('object'))
        if sym in manual_link_views: view,basis=manual_link_views[sym]
        parsed=parse_type(view) if view else None
        if not parsed:
            deferred.append(dict(symbol=sym,cause=cause,view=view,basis=basis,reason='no safe scalar/array declaration view'))
            continue
        base,dims=parsed; cname=sym[1:] if sym.startswith('_') else sym
        struct_m=re.match(r'^struct\s+([A-Za-z_][A-Za-z0-9_]*)$',base)
        body=None
        if struct_m:
            tag=struct_m.group(1); variants=all_structs.get(tag,[])
            wanted=item.get('candidate_extent') or (item.get('data_model') or {}).get('extent')
            count=dims[0] if dims else 1
            stride=(int(wanted)//count) if wanted and count and int(wanted)%count==0 else None
            picked=(tag,variants[0]) if variants else None
            if not picked or (stride and c_struct_size(picked[1],{k:v[0] for k,v in all_structs.items()})!=stride):
                preferred=[]
                views=list(declaration_map.get(sym,[]))+list((conflict_map.get(sym) or {}).get('views') or [])
                for candidate in views:
                    text=candidate if isinstance(candidate,str) else candidate.get('view') or candidate.get('type') or ''
                    vm=re.match(r'^struct\s+([A-Za-z_][A-Za-z0-9_]*)',text)
                    if vm and vm.group(1) not in preferred: preferred.append(vm.group(1))
                candidates=[]
                for candidate_tag in preferred+sorted(set(all_structs)-set(preferred)):
                    for candidate_body in all_structs.get(candidate_tag,[]):
                        size=c_struct_size(candidate_body,{k:v[0] for k,v in all_structs.items()})
                        if size is not None and (stride is None or size==stride):
                            candidates.append((candidate_tag,candidate_body)); break
                if candidates: picked=candidates[0]
            if picked:
                tag,body=picked; unique='__LINK_STUB_'+re.sub(r'\W','_',cname)
                base='struct '+unique
            elif dims:
                deferred.append(dict(symbol=sym,cause=cause,view=view,basis=basis,reason='no source struct body matches independently bounded stride'))
                continue
        evidence=manual_link_views.get(sym,(None,None))[1]
        kind='bss' if cause=='UNDEFINED_BSS_GLOBAL' else 'data'
        stub_items.append(dict(symbol=sym,cname=cname,base=base,dims=dims,kind=kind,view=view,basis=basis,struct_body=body,struct_tag=struct_m.group(1) if struct_m else None,evidence=evidence,cause=cause,bytes=type_bytes(view,all_structs,body),recovery_credit=0))
    # The game-owned library base slots are typed missing BSS storage; runtime-owned bases stay with CRT/libraries.
    for item in undef:
        if item['cause']!='OS_LIBRARY_BASE_STORAGE_AND_BINDING': continue
        for candidate in item.get('provider_alias_candidates',[]):
            target=candidate.get('target')
            if target not in ('_GfxBase','_IntuitionBase','_LayersBase'): continue
            if target in accepted_names: continue
            view,basis=choose_view(item['symbol'],item,conflict_map,declaration_map); parsed=parse_type(view) if view else None
            if not parsed: continue
            base,dims=parsed
            if dims: base='void *'
            cname=target[1:]
            if not any(x['symbol']==target for x in stub_items):
                stub_items.append(dict(symbol=target,cname=cname,base=base,dims=[],kind='bss',view=view,basis='GAME_OWNED_OS_BASE:'+basis,struct_body=None,struct_tag=None,cause='OS_LIBRARY_BASE_STORAGE_AND_BINDING',bytes=type_bytes(view,all_structs),recovery_credit=0))
                runtime_stubs.append(target)
    # Keep each generated C TU below the compiler's small declaration table; these declarations are mechanics-only.
    chunk_size=280
    # Sizes of independently BOUNDED storage-plan objects override view sizes.
    import storage_plan as storage_plan_tool
    derived=storage_plan_tool.load(ROOT)["derived"]
    bounded={o['id']:o['end']-o['start'] for o in derived['objects'] if o.get('status')=='BOUNDED'}
    plan_sizes={name:bounded[a['object']] for name,a in derived['aliases'].items()
                if a.get('offset')==0 and a.get('object') in bounded}
    stub_objects=[]
    for kind in ('bss','data'):
        rows=[x for x in stub_items if x['kind']==kind]
        for chunk,start in enumerate(range(0,len(rows),chunk_size)):
            group=rows[start:start+chunk_size]
            if not group: continue
            filename='zero_%s_%02d.c'%(kind,chunk); rel=Path('LINK_ONLY_STUBS')/filename
            lines=[header]
            for row in group:
                if row['symbol'] in ('_G_h01_27E4', '_G_h01_2A12'):
                    lines.append('/* LINK_ONLY_STUBS initialized DATA placeholder for %s: link-only mechanics stub; no recovered type/extent claim. */\n' % row['symbol'])
                # A definition only supplies symbol, size and alignment; each TU keeps
                # its own extern view. Even-sized short arrays keep every stub (and
                # everything linked after it) word-aligned: a one-byte char stub
                # once left _G_h01_2A12 odd and the 68000 raised an address error.
                size=plan_sizes.get(row['cname']) or row.get('bytes')
                if size:
                    initializer=' = {0}' if kind=='data' else ''
                    lines.append('short %s[%d]%s;\n'%(row['cname'],(size+1)//2,initializer))
                    row['bytes']=size
                    continue
                if row.get('struct_body'):
                    body=row['struct_body'].strip()
                    lines.append('struct %s { %s };\n'%(row['base'][7:],body.strip().strip('{}').strip()))
                dims=''.join('[%d]'%n for n in row['dims'])
                initializer=' = {0}' if kind=='data' and row['dims'] else ' = 0' if kind=='data' else ''
                lines.append('%s %s%s%s;\n'%(row['base'],row['cname'],dims,initializer))
            (GUEST/rel).write_text(''.join(lines),encoding='ascii',newline='\n')
            objname='link_stub_'+kind+'_%02d.o'%chunk
            compile_entries.append(dict(source=rel.as_posix(),object=objname,kind='c',profile='aztec36',flags=[],log=objname[:-2]+'-cc.log',as_log=objname[:-2]+'-as.log'))
            object_args.append(objname); node_objects['root'].append(objname); stub_objects.append(dict(object=objname,file=rel.as_posix(),symbols=[x['symbol'] for x in group],cause=kind))
    # Exact zero-fill spans for the three supervisor-authorized measured gaps.
    # One assembly data block per reservation, with a real public label for every
    # member at its original offset: no C view rewriting, no EQU aliases.
    reservation_file=Path('LINK_ONLY_STUBS')/'measured_reservations.asm'
    reservation_lines=['; LINK_ONLY_STUBS MEASURED_RESERVATION: zero-fill spans of storage-plan objects.\n',
                       '; NOT recovered source and NOT a type or capacity claim; excluded from all counts.\n',
                       '\tfar data\n','\tdseg\n']
    labels_by_anchor=collections.defaultdict(list)
    for alias in reservation_aliases:
        labels_by_anchor[alias['anchor']].append((alias['offset'],alias['symbol']))
    # `bss name,size` entries of one module are laid out contiguously, in order,
    # byte-packed and uninitialized (probed with the pinned as/ln), so each
    # member keeps its exact offset and the executable carries no zero bytes.
    for row in measured_reservations:
        reservation_lines.append('; [%04X,%04X) %s, %d bytes\n' % (row['start'],row['end'],row['object'],row['bytes']))
        members=sorted(labels_by_anchor[row['anchor']])
        if not members or members[0][0]>0:
            members=[(0,'_LINK_ONLY_PAD_%04X' % row['start'])]+members
        for index,(offset,symbol) in enumerate(members):
            following=members[index+1][0] if index+1<len(members) else row['bytes']
            reservation_lines.append('\tpublic %s\n\tbss %s,%d\n' % (symbol,symbol,following-offset))
    reservation_lines.append('\tend\n')
    (GUEST/reservation_file).write_text(''.join(reservation_lines),encoding='ascii',newline='\n')
    reservation_obj='link_stub_measured_reservations.o'
    compile_entries.append(dict(source=reservation_file.as_posix(),object=reservation_obj,kind='asm',profile='aztec36 as',flags=[],log=reservation_obj[:-2]+'-as.log'))
    object_args.append(reservation_obj); node_objects['root'].append(reservation_obj)
    stub_objects.append(dict(object=reservation_obj,file=reservation_file.as_posix(),symbols=[x['anchor'] for x in measured_reservations],cause='MEASURED_RESERVATION',bytes=sum(x['bytes'] for x in measured_reservations),recovery_credit=0,classification='MEASURED_RESERVATION'))
    # Stack-call zero-return stand-ins for the only two genuinely missing game code providers.
    function_rows=[]
    for sym,ret in (('F_h00_463E','unsigned int'),):
        entry=header + '%s %s() { return 0; }\n'%(ret,sym)
        function_rows.append(dict(symbol='_'+sym,source_view=ret+' ()',return_type=ret,body_value=0,bytes=4,cause='unresolved-game-code',recovery_credit=0))
    functions_file=Path('LINK_ONLY_STUBS')/'missing_game_functions.c'
    # 463E is the game's random-number step. Its retained best candidate (byte-
    # exact except one eor operand order; agrees with the original on 4,000
    # executed inputs) is far closer than a zero return. Still a link-only
    # stand-in: UNRESOLVED, never counted as recovery.
    candidate=ROOT/'evidence/blockers/resident_F_463E.c'
    if candidate.is_file():
        body=re.sub(r'(?<![A-Za-z0-9_])recovered(?![A-Za-z0-9_])','F_h00_463E',candidate.read_text(encoding='ascii'))
        functions_text=header+'/* UNRESOLVED_CANDIDATE from evidence/blockers/resident_F_463E.c */\n'+body
        function_rows[0].update(cause='unresolved-game-code (best candidate source)',source='evidence/blockers/resident_F_463E.c')
    else:
        functions_text=header+'\n'.join('%s %s() { return 0; }'%(x['return_type'],x['symbol'][1:]) for x in function_rows)+'\n'
    (GUEST/functions_file).write_text(functions_text,encoding='ascii',newline='\n')
    fn_obj='link_stub_missing_game_functions.o'; compile_entries.append(dict(source=functions_file.as_posix(),object=fn_obj,kind='c',profile='aztec36',flags=[],log=fn_obj[:-2]+'-cc.log',as_log=fn_obj[:-2]+'-as.log'))
    object_args.append(fn_obj); node_objects['root'].append(fn_obj); stub_objects.append(dict(object=fn_obj,file=functions_file.as_posix(),symbols=[x['symbol'] for x in function_rows],cause='unresolved-game-code'))
    # The accepted 701A ASM proof keeps its separately named callback entry external.
    # Supply only the minimum link-time RTS label; this is a mechanics stub, not recovery.
    asm_dependency_file=Path('LINK_ONLY_STUBS')/'missing_asm_dependencies.asm'
    asm_dependency_symbol='_recon_h00_6FDE'
    asm_dependency_source=('; LINK_ONLY_STUBS: unresolved accepted-ASM dependency for the mechanics-only link.\n'
        '; NOT recovered source, NOT a behavior implementation, and excluded from all recovery counts.\n'
        '; One RTS label only; replace before any execution or behavioral claim.\n'
        '\tfar data\n\tdseg\n\tcseg\n\tpublic ' + asm_dependency_symbol + '\n'
        + asm_dependency_symbol + '\n\trts\n\tdseg\n\tend\n')
    (GUEST/asm_dependency_file).write_text(asm_dependency_source,encoding='ascii',newline='\n')
    asm_dependency_obj='link_stub_missing_asm_dependencies.o'
    compile_entries.append(dict(source=asm_dependency_file.as_posix(),object=asm_dependency_obj,kind='asm',profile='aztec36 as',flags=[],log='link_stub_missing_asm_dependencies-as.log'))
    object_args.append(asm_dependency_obj); node_objects['root'].append(asm_dependency_obj)
    asm_dependency_rows=[dict(symbol=asm_dependency_symbol,source=asm_dependency_file.as_posix(),kind='LINK_ONLY_STUBS_CODE_DEPENDENCY',body='rts only',bytes=2,cause='unresolved-accepted-asm-dependency',recovery_credit=0)]
    stub_objects.append(dict(object=asm_dependency_obj,file=asm_dependency_file.as_posix(),symbols=[asm_dependency_symbol],cause='unresolved-accepted-asm-dependency',recovery_credit=0))
    assert_unique_entry_names([entry['object'] for entry in compile_entries])
    # Preserve the inventory's resident order and sparse +oN tree; DATA providers and link-only inputs stay root.
    link_lines=['+ccd','crt0.o']
    root_inventory=next(n for n in inv['overlay']['nodes'] if n['node']=='root')
    inv_obj_map={o['object']:o for o in obj_rows}
    stackstart_anchor = next((o['object'] for o in inv['objects']
                              if 'src/recovered/asm-reconstructed/resident_driver_57E4.asm' in o.get('sources', [])), None)
    if 'resident_frameless_57D2' in accepted_asm_obj_rows and stackstart_anchor is None:
        raise SystemExit('cannot place accepted 57D2 provider adjacent to resident_driver_57E4')
    accepted_asm_names = {key: 'obj_' + Path(obj['object']).stem + '.o'
                          for key, obj in accepted_asm_obj_rows.items()}
    for original_obj in root_inventory['objects']:
        if original_obj == stackstart_anchor and 'resident_frameless_57D2' in accepted_asm_names:
            link_lines.append(accepted_asm_names['resident_frameless_57D2'])
        link_lines.extend(stage_names_by_inventory.get(original_obj, []))
    if 'resident_frameless_701A' in accepted_asm_names:
        link_lines.append(accepted_asm_names['resident_frameless_701A'])
    for row in data_manifest: link_lines.append(row['object'])
    if alias_obj: link_lines.append(alias_obj)
    link_lines.append(exit_bridge_obj)
    link_lines.extend(x['object'] for x in stub_objects)
    node_order=inv['overlay']['nodes']
    for node in node_order:
        if node.get('status')=='EMPTY' or node.get('node')=='root': continue
        link_lines.append('+o%d'%node['ln_node'])
        for original_obj in node['objects']:
            link_lines.extend(stage_names_by_inventory.get(original_obj, []))
    link_lines.extend(['+o0','Old1:lib/c.lib','Old1:lib/m.lib'])
    (GUEST/'link.lnk').write_text('\n'.join(link_lines)+'\n',encoding='ascii',newline='\n')
    (GUEST/'compiler-input.txt').write_text('n\n'*20,encoding='ascii',newline='\n')
    (GUEST/'objects.keep').write_text('Staging folder marker.\n',encoding='ascii',newline='\n')
    commands=['C:FailAt 1000000','Old2:bin/lb Old1:lib/c.lib -x crt0 >crt0-extract.log']
    for e in compile_entries:
        src=e['source']; obj=e['object']; stem=obj[:-2]
        if e['kind']=='c':
            flags=' '.join(e['flags']); include_flags='-I Old1:include ' if '+X3' in e['flags'] else ''
            commands.append('Old1:bin/cc <compiler-input.txt >%s -a %s%s%s'%(e['log'],(flags+' ') if flags else '',include_flags,src))
            commands.append('Old1:bin/as <compiler-input.txt >%s -o %s %s'%(e['as_log'],obj,'tu/'+Path(src).stem+'.asm' if src.startswith('tu/') else src.rsplit('.',1)[0]+'.asm'))
        else:
            commands.append('Old1:bin/as <compiler-input.txt >%s -o %s %s'%(e['log'],obj,src))
    commands.append('Old1:bin/ln <compiler-input.txt >link-ln.log -m -t -o DuckTales -f link.lnk')
    write_json(STAGE/'commands.json',commands)
    write_json(STAGE/'source-manifest.json',dict(head=head,inventory_base=inv.get('base_head'),inventory_sha256=inv_hash,
        canonical_ledger_sha256=ledger_hash,storage_plan_sha256=storage_plan_sha256,storage_plan_summary=storage_plan.get('derived',{}).get('summary'),
        selected_inventory_source_records=len(src_rows),selected_inventory_objects=selected_inventory_object_count,
        materialized_source_objects=len(obj_rows),accepted_data_providers=len(data_manifest),production_source_objects=len(obj_rows)+len(data_manifest),
        source_records=source_manifest,data_providers=data_manifest,compiled_objects=production_inputs,
        object_args=object_args,overlay_nodes=[dict(ln_node=n['ln_node'],node=n.get('node'),status=n.get('status'),objects=n.get('objects',[])) for n in node_order],
        link_argument_file=link_lines,link_object_count=len(link_lines)-sum(1 for x in link_lines if x.startswith('+o'))-3,
        selected_inventory_source_record_count_before_dedup=selected_inventory_source_record_count,
        excluded_inventory_data_provider_paths=overlap_provider_paths,
        alias_adapter=dict(file=str(alias_path.relative_to(STAGE)) if alias_path else None,object=alias_obj,aliases=emitted_data_aliases,storage_plan_aliases=storage_plan_aliases,reservation_aliases=reservation_aliases,aliases_converted_to_c_source_views=source_view_alias_records,aliases_retained_for_asm=sorted(assembler_alias_references)),
        exit_link_remaps={source:dict(symbol=values[0],c_identifier=values[1]) for source,values in unique_exit_entries.items()},
        exit_entry_aliases={'_exit':'_recovered_exit_8534','__exit':'_recovered_exit_8552','cause':'pinned CRT _main.c calls exit(0); c.lib (exit) then selects c.lib (_exit)','mechanics_object':'link_exit_entry_bridges.o'},
        runtime_library_storage_aliases=runtime_library_storage_aliases,
        runtime_symbol_remaps={'_F_h00_75D8':'_index'},
        accepted_asm_providers=[dict(key=key,source=row['source'],definitions=row['definitions'],object=accepted_asm_names.get(key),proof=row.get('proof'),proof_category=row.get('proof_category')) for key,row in accepted_asm_rows.items()],
        accepted_asm_symbol_remaps=accepted_asm_symbol_remaps,
        source_view_aliases=source_view_alias_records,
        source_view_array_address_adjustments=source_view_array_address_adjustments,
        aliases_retained_for_asm=sorted(assembler_alias_references),
        staging_identifier_renames=staging_identifier_renames,
        measured_reservations=measured_reservations,
        link_only_stub_objects=stub_objects,link_only_stub_symbols=stub_items+function_rows+asm_dependency_rows,stub_deferred=deferred,
        runtime_game_base_stubs=runtime_stubs,unlowered_c_runtime_aliases=macro_unhandled,
        proof_accounting='LINK_ONLY_STUBS and LINK_MATERIALIZATION are mechanics inputs only; no recovery credit.'))
    write_json(GUEST/'LINK_ONLY_STUBS'/'manifest.json',dict(schema_version=1,classification='LINK_ONLY_STUBS',recovery_credit=0,behavioral_claim=False,execution_prohibited_until_replaced=bool(stub_items or function_rows or asm_dependency_rows or measured_reservations),header_policy='Every stub source states that it is mechanics-only, is not recovered source, has no behavior proof, and is excluded from recovery counts.',storage_plan_sha256=storage_plan_sha256,objects=stub_objects,symbols=stub_items+function_rows+asm_dependency_rows,measured_reservations=measured_reservations,reservation_aliases=reservation_aliases,deferred_untyped_symbols=deferred))
    write_json(STAGE/'compile-plan.json',compile_entries)
    print('HEAD',head,'inventory base',inv.get('base_head'),'ledger sha256',ledger_hash)
    print('Production:',len(obj_rows),'source-level TUs from',selected_inventory_source_record_count,'selected inventory source records (',len(overlap_provider_paths),'provider duplicates excluded; accepted extra ASM',len(accepted_asm_rows),') +',len(data_manifest),'current DATA provider objects')
    print('C interior aliases remapped to source views:',len(source_view_alias_records),'across',len({x['object'] for x in source_view_alias_records}),'objects; array address adjustments',sum(x['replacements'] for x in source_view_array_address_adjustments),'; retained ASM EQU aliases',len(assembler_alias_references))
    print('LINK_ONLY_STUBS:',collections.Counter(x['cause'] for x in stub_objects),'typed storage symbols',len(stub_items),'deferred untyped',len(deferred),'functions',len(function_rows),'measured reservations',len(measured_reservations))
    print('LINK_MATERIALIZATION data aliases:',len(emitted_data_aliases),'(source-view interiors',len(interior_aliases),', storage-plan aliases',len(storage_plan_aliases),') link inputs',len(link_lines))
    proof_counts = collections.Counter(x.get('proof_category') for x in source_manifest)
    proof_counts['DATA_LAYOUT_MATCH'] = len(data_manifest)
    stub_symbols = stub_items + function_rows + asm_dependency_rows
    report = format_build_report(proof_counts, stub_symbols, stub_objects, measured_reservations,
                                 inv.get('summary',{}).get('code_hunk_bytes',{}).get('RAW_ORACLE_DEBT'))
    print(report)
    write_json(STAGE/'build-report.json',dict(head=head,ledger_sha256=ledger_hash,inventory_sha256=inv_hash,
        proof_counts=dict(proof_counts),stub_symbols=stub_symbols,stub_objects=stub_objects,
        measured_reservations=measured_reservations,STUB_FREE=(not stub_symbols and not measured_reservations),
        unresolved_code_bytes=inv.get('summary',{}).get('code_hunk_bytes',{}).get('RAW_ORACLE_DEBT')))
    print('Staged under',STAGE)
    if deferred: print('Deferred symbol report:',STAGE/'source-manifest.json')
    if args.report: return 0
    if digest(LEDGER_PATH) != ledger_hash:
        raise SystemExit('recovery ledger changed during staging; rerun to rederive accepted DATA selection')
    # Use the shared pinned Aztec worker lifecycle and retain every job artifact.
    sys.path.insert(0,str(ROOT/'tools'))
    from aztec_worker import prepare, collect
    if args.backend=='vamos':
        import time
        started=time.perf_counter()
        routed,link=run_vamos_build(commands,GUEST,STAGE)
        print('vamos compile/assemble: %.1fs; routed to WinUAE: %d group(s)'%(time.perf_counter()-started,len(routed)))
        if routed:
            sub=[c for g in routed for c in g]
            job=prepare(unique_job_name(ledger_hash,ROOT/'build/worker-jobs',None),GUEST,sub,
                        Path('C:/Program Files/WinUAE/winuae64.exe'),aztec36=True)
            shell=shutil.which('pwsh') or shutil.which('powershell')
            proc=subprocess.run([shell,'-NoProfile','-ExecutionPolicy','Bypass','-File',str(ROOT/'tools/run_worker.ps1'),
                                 '-Job',str(job),'-TimeoutSeconds',str(max(600,len(sub)*30))],capture_output=True,text=True)
            result=collect(job)
            require_ok=proc.returncode==0 and result.get('all_steps_succeeded')
            if not require_ok:
                print('WinUAE routed compiles failed',proc.returncode,proc.stderr[-2000:]); return 2
            for artifact in result['artifacts']:
                if artifact['path'].endswith(('.o','.asm','.log')):
                    dest=GUEST/artifact['path']; dest.parent.mkdir(parents=True,exist_ok=True)
                    shutil.copy2(job/'sys/work'/artifact['path'],dest)
        import vamos_backend as vb
        started=time.perf_counter()
        try:
            residual=link_with_original_data_layout(GUEST,STAGE,link,data_manifest)
        except Exception as exc:
            print('LINK FAILED:',exc); print((GUEST/'link-ln.log').read_text(errors='replace')[-3000:]); return 2
        print('vamos link (with DATA layout alignment): %.1fs; residual DATA drift: %s'%(time.perf_counter()-started,residual))
        # The per-group private work trees are scratch; outputs were copied back.
        shutil.rmtree(STAGE/'vamos-sys',ignore_errors=True)
        exe=GUEST/'DuckTales'
        if not exe.is_file(): print('link produced no executable'); return 2
        shutil.copy2(exe,STAGE/'DuckTales')
        if (GUEST/'DuckTales.sym').is_file(): shutil.copy2(GUEST/'DuckTales.sym',STAGE/'DuckTales.sym')
        topology=topology_report(exe)
        write_json(STAGE/'hunk-topology-comparison.json',topology)
        print('HUNK parse: PASS; topology comparison:',json.dumps(topology['topology_match'],sort_keys=True))
        return 0
    job_name=unique_job_name(ledger_hash,ROOT/'build/worker-jobs',args.job)
    job=prepare(job_name,GUEST,commands,Path('C:/Program Files/WinUAE/winuae64.exe'),aztec36=True)
    shell=shutil.which('pwsh') or shutil.which('powershell')
    if not shell: raise SystemExit('PowerShell not found')
    timeout=max(1800,len(commands)*3)
    proc=subprocess.run([shell,'-NoProfile','-ExecutionPolicy','Bypass','-File',str(ROOT/'tools/run_worker.ps1'),'-Job',str(job),'-TimeoutSeconds',str(timeout)],capture_output=True,text=True)
    (STAGE/'run_worker.stdout.log').write_text(proc.stdout,encoding='utf-8',newline='\n')
    (STAGE/'run_worker.stderr.log').write_text(proc.stderr,encoding='utf-8',newline='\n')
    print('run_worker return',proc.returncode,proc.stdout[-2000:],proc.stderr[-2000:])
    result=collect(job)
    write_json(STAGE/'worker-result.json',result)
    work=job/'sys/work'; out=STAGE/'artifacts'; out.mkdir(exist_ok=True)
    for artifact in result['artifacts']:
        source=work/artifact['path']; dest=out/artifact['path']; dest.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(source,dest)
    print('WORKER JOB',job,'all steps succeeded',result['all_steps_succeeded'],'step count',len(result['steps']))
    print('Step failures',[(s['index'],s['returncode'],s['command']) for s in result['steps'] if s['returncode']])
    print('Artifacts copied to',out)
    exe=out/'DuckTales'
    if proc.returncode==0 and result.get('all_steps_succeeded') and exe.is_file():
        shutil.copy2(exe,STAGE/'DuckTales')
        map_path=out/'DuckTales.sym'
        if map_path.is_file(): shutil.copy2(map_path,STAGE/'DuckTales.sym')
        topology=topology_report(exe)
        write_json(STAGE/'hunk-topology-comparison.json',topology)
        print('HUNK parse: PASS; topology comparison:',json.dumps(topology['topology_match'],sort_keys=True))
    return 0 if proc.returncode==0 else 2

if __name__=='__main__':
    raise SystemExit(main())
