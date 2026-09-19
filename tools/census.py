"""Generate or verify deterministic archaeological evidence, never a game build."""
import argparse
import json
from pathlib import Path
import re
import sys

from common import FormatError, json_bytes, require, sha256
from ofs import OFSDisk
from hunk import parse, manx_overlay

ROOT = Path(__file__).resolve().parents[1]


def inputs(root):
    supplied = sorted(p for p in (root / 'assets').rglob('*') if p.is_file())
    require(supplied, 'no supplied assets')
    return supplied


def fixture_identity(root):
    return [dict(path=p.relative_to(root).as_posix(), size=p.stat().st_size, sha256=sha256(p.read_bytes()))
            for p in inputs(root)]


def verify_lock(root):
    path = root / 'evidence/fixture-lock.json'
    require(path.exists(), 'fixture lock missing: explicitly initialize with --init-lock')
    lock = json.loads(path.read_text())
    require(lock['supplied_inputs'] == fixture_identity(root), 'fixture lock mismatch: original inputs changed; lock was NOT updated')
    return lock


def derive(root):
    outputs, files, disks = {}, {}, []
    outputs['evidence/analysis-tools.json'] = dict(schema_version=1, classification='ANALYSIS_ONLY',
        tools=[dict(path=p.relative_to(root).as_posix(), sha256=sha256(p.read_bytes()), size=p.stat().st_size)
               for p in sorted((root / 'tools').glob('*.py'))])
    for index, path in enumerate(sorted((root / 'assets').glob('*.adf')), 1):
        disk = OFSDisk(path.read_bytes())
        manifest = disk.parse()
        manifest['input_path'] = path.relative_to(root).as_posix()
        disks.append(manifest)
        outputs[f'evidence/filesystem/disk{index}.json'] = manifest
        outputs[f'evidence/disks/disk{index}.json'] = {k: manifest[k] for k in
            ('input_path','volume','size','sha256','boot','root','bitmap')}
        for name, content in sorted(disk.files.items()):
            identity = manifest['volume'] + ':' + name
            require(identity not in files, f'duplicate disk/path {identity}')
            files[identity] = content
    require(len(disks) == 2 and {d['volume'] for d in disks} == {'DT1','DT2'}, 'expected DT1 and DT2')
    require('DT1:DuckTales' in files, 'main executable absent')
    exe = files['DT1:DuckTales']
    model = parse(exe)
    tree = manx_overlay(model, exe)
    outputs['evidence/executable/hunks.json'] = {k:v for k,v in model.items() if k != 'relocations'}
    outputs['evidence/executable/relocations.json'] = dict(schema_version=1, count=len(model['relocations']),
                                                        relocations=model['relocations'])
    outputs['evidence/executable/overlay-tree.json'] = tree
    strings, anchors = [], []
    # Maximal printable runs are search candidates, NOT proof of strings or code boundaries.
    for h in model['hunks']:
        if h['content_offset'] is None:
            continue
        data = exe[h['content_offset']:h['content_offset'] + h['initialized_size']]
        for m in re.finditer(rb'[\x20-\x7e]{5,}', data):
            strings.append(dict(hunk=h['number'], offset=m.start(), text=m.group().decode('ascii'),
                                classification='CANDIDATE', trailing_nul=m.end() < len(data) and data[m.end()] == 0))
        for m in re.finditer(rb'(?i)DT[12]:[a-z0-9_.-]+\.(?:arc|as)\x00', data):
            text = m.group()[:-1].decode('ascii')
            match = [f for f in files if f.lower() == text.lower()]
            require(len(match) == 1, f'asset anchor does not resolve: {text}')
            anchors.append(dict(hunk=h['number'], node=h['node'], offset=m.start(), size=len(m.group()),
                                file_offset=h['content_offset'] + m.start(), text=text,
                                asset=match[0], confidence='OBSERVED',
                                evidence='NUL-terminated disk-qualified name matches disk census; no caller inferred'))
    outputs['evidence/executable/strings.json'] = dict(candidates=strings, asset_anchors=anchors)
    outputs['evidence/assets.json'] = dict(schema_version=1, files=[dict(path=p, size=len(b), sha256=sha256(b),
        format_status='UNKNOWN', signature_hex=b[:16].hex(),
        string_anchors=[a for a in anchors if a['asset'] == p]) for p,b in sorted(files.items())
        if p.lower().endswith(('.arc','.as'))])
    ranges, symbols, instructions = [], [], []
    for slot in tree['slots']:
        for s in slot['symbols']:
            symbols.append(dict(name=f'h{s["target_hunk"]:02d}_{s["target_offset"]:06x}',
                                hunk=s['target_hunk'], offset=s['target_offset'],
                                kind='OVERLAY_ENTRY', naming_origin='RECONSTRUCTED_ADDRESS', state='OBSERVED',
                                evidence=s))
    dh = next(h for h in model['hunks'] if h['number'] == 1)
    verified = []
    for slot in tree['slots']:
        for s in slot['symbols']:
            t = s['trampoline_offset']
            verified.append((t, t + 8, 'OVERLAY_RUNTIME', 'MANX_RUNTIME', 'overlay table + trampoline crosscheck'))
            instructions.append(dict(hunk=1, offset=t, raw=exe[dh['content_offset'] + t:dh['content_offset'] + t + 4].hex(),
                decoded=f'bsr.w h01+0x{s["bridge_offset"]:x}', length=4, direct_calls=[dict(hunk=1,offset=s['bridge_offset'])],
                direct_branches=[], indirect_calls=[], relocated_references=[], strings_referenced=[],
                likely_stack_arguments=None, register_saves_restores=None, confidence='OBSERVED',
                evidence='structurally verified overlay trampoline; next four bytes are inline dispatch data'))
    for bridge in sorted({s['bridge_offset'] for e in tree['slots'] for s in e['symbols']}):
        verified.append((bridge, bridge + 6, 'OVERLAY_RUNTIME', 'MANX_RUNTIME', 'JMP opcode + HUNK_RELOC32'))
        manager = tree['manager_entry_offsets'][0]
        instructions.append(dict(hunk=1, offset=bridge,
            raw=exe[dh['content_offset'] + bridge:dh['content_offset'] + bridge + 6].hex(),
            decoded=f'jmp h00+0x{manager:x}', length=6, direct_calls=[], direct_branches=[dict(hunk=0,offset=manager)],
            indirect_calls=[], relocated_references=[dict(hunk=0,offset=manager)], strings_referenced=[],
            likely_stack_arguments=None, register_saves_restores=None, confidence='OBSERVED',
            evidence='absolute JMP bridge with independent relocation record'))
    for h in model['hunks']:
        spans = list(verified) if h['number'] == 1 else []
        spans += [(a['offset'],a['offset']+a['size'],'STRING','UNKNOWN','exact asset filename anchor')
                  for a in anchors if a['hunk'] == h['number']]
        spans.sort()
        cursor = 0
        for start,end,kind,owner,evidence in spans:
            require(cursor <= start < end <= h['initialized_size'], 'overlapping byte classifications')
            if cursor < start:
                ranges.append(dict(hunk=h['number'], start=cursor, end=start, classification='UNKNOWN', ownership='UNKNOWN'))
            ranges.append(dict(hunk=h['number'], start=start, end=end, classification=kind, ownership=owner, evidence=evidence))
            cursor = end
        if cursor < h['initialized_size']:
            ranges.append(dict(hunk=h['number'], start=cursor, end=h['initialized_size'],classification='UNKNOWN', ownership='UNKNOWN'))
        if h['zero_fill_size']:
            ranges.append(dict(hunk=h['number'], start=h['initialized_size'],end=h['allocated_size'],
                               classification='BSS', ownership='UNKNOWN',
                               evidence='allocation minus initialized content; no source COMMON attribution'))
    allocated = sum(h['allocated_size'] for h in model['hunks'])
    require(sum(r['end'] - r['start'] for r in ranges) == allocated, 'byte accounting gap')
    unknown = sum(r['end'] - r['start'] for r in ranges if r['classification'] == 'UNKNOWN')
    outputs['evidence/executable/byte-map.json'] = dict(schema_version=1, allocation_sum_bytes=allocated,
        note='Sum across all hunks, not simultaneous runtime RAM use. HUNK_CODE/DATA are containers, not per-byte classifications.',
        initialized_bytes=sum(h['initialized_size'] for h in model['hunks']), unknown_bytes=unknown,
        classified_bytes=allocated-unknown, ranges=ranges)
    outputs['evidence/executable/instructions.json'] = dict(schema_version=1,
        scope='Verified resident overlay trampolines/bridge only; no speculative linear disassembly.',
        decoded_instruction_bytes=sum(i['length'] for i in instructions), instructions=instructions)
    outputs['evidence/executable/ownership.json'] = dict(schema_version=1,
        note='MANX_RUNTIME means observed overlay ABI role, not exact historical library-object identity.', ranges=ranges)
    modules = []
    for node in model['nodes']:
        hs = [h for h in model['hunks'] if h['number'] in node['hunks']]
        rs = [r for r in ranges if r['hunk'] in node['hunks']]
        size = sum(h['allocated_size'] for h in hs)
        unclassified = sum(r['end']-r['start'] for r in rs if r['classification'] == 'UNKNOWN')
        owner_unknown = sum(r['end']-r['start'] for r in rs if r['ownership'] == 'UNKNOWN')
        modules.append(dict(id=node['id'], historical_identity='HUNK_HEADER + logical hunk range',
            hunks=node['hunks'], source_filename_provenance='UNKNOWN',
            semantic_role='investment / stock market' if node['id'] == 'ov07' else None,
            semantic_confidence='CANDIDATE' if node['id'] == 'ov07' else 'UNKNOWN',
            name_origin='RECONSTRUCTED_SEMANTIC' if node['id'] == 'ov07' else 'RECONSTRUCTED_CONTAINER_ID',
            asset_anchors=[a for a in anchors if a['node'] == node['id']],
            byte_size=size, initialized_bytes=sum(h['initialized_size'] for h in hs),
            classified_bytes=size-unclassified, unknown_bytes=unclassified, ownership_unknown_bytes=owner_unknown,
            game_owned_bytes=0, runtime_bytes=size-owner_unknown,
            functions_identified=None, overlay_entries_identified=sum(s['hunk'] in node['hunks'] for s in symbols),
            functions_reconstructed=0, code_matched_bytes=0, data_matched_bytes=0,
            relocation_records=sum(r['source_hunk'] in node['hunks'] for r in model['relocations']),
            relocations_resolved=0, current_proof_level=None, evidence_status='TOPOLOGY_OBSERVED',
            next_blocker='TOOLCHAIN-001' if node['id']=='ov07' else 'OWNERSHIP-001'))
    outputs['docs/modules.json'] = dict(schema_version=1, modules=modules)
    outputs['docs/symbols.json'] = dict(schema_version=1, symbols=symbols, historical_symbols_present=False)
    outputs['docs/data-layout.json'] = dict(schema_version=1, ranges=[r for r in ranges
        if r['hunk'] in (1,2) or r['classification']=='STRING'], typed_game_objects=0)
    outputs['docs/progress.json'] = dict(schema_version=1, milestone='IMMUTABLE_TOPOLOGY_CENSUS',
        reconstruction_complete=False, pilot_complete=False, independent_game_build_available=False,
        supplied_disks=len(disks), extracted_files=len(files), executable_size=len(exe),
        executable_hunks=len(model['hunks']), physical_overlays=len(model['nodes'])-1,
        overlay_slots=tree['slot_count'], overlay_entries=len(symbols), relocations=len(model['relocations']),
        file_bytes_accounted=model['accounted_file_bytes'], file_bytes_unparsed=model['unparsed_bytes'],
        allocation_sum_bytes=allocated, classification_unknown_bytes=unknown,
        ownership_unknown_bytes=sum(m['ownership_unknown_bytes'] for m in modules),
        reconstructed_functions=0, matched_source_bytes=0, current_proof_level=None,
        phases={'0':'CENSUS_COMPLETE','1':'CENSUS_COMPLETE','2':'CENSUS_COMPLETE',
                '3':'STATIC_TOPOLOGY_VALIDATED_RUNTIME_NOT_TRACED','4':'PARTIAL_CONSERVATIVE_MAP',
                '5':'MANX_ABI_OBSERVED_VERSION_UNKNOWN','6':'OVERLAY_GLUE_ONLY','7':'NOT_RUN','8':'PILOT_SELECTED_NOT_RECONSTRUCTED'},
        pilot='ov07', next_action='Pin candidate Manx distributions, match runtime objects, then fingerprint compiler and recover pilot control flow.')
    outputs['evidence/executable/pilot.json'] = dict(schema_version=1, node='ov07', hunk=7,
        selection_reason='invest.arc and invart.arc anchors plus investment text; coherent candidate, not the smallest overlay',
        initialized_size=next(h['initialized_size'] for h in model['hunks'] if h['number']==7),
        entries=[s for s in symbols if s['hunk']==7],
        candidate_text=[s for s in strings if s['hunk']==7 and (len(s['text']) >= 12 or 'invest' in s['text'].lower())],
        complete_function_census=False, compiler_provenance='UNRESOLVED', reconstruction_proof_level=None)
    return outputs, files, model


def lock_document(root, files):
    return dict(schema_version=1, algorithm='SHA-256', source='user-supplied assets directory',
        policy='Originals are verification fixtures only. Default commands never update this lock.',
        supplied_inputs=fixture_identity(root),
        extracted_files=[dict(path=p,size=len(b),sha256=sha256(b)) for p,b in sorted(files.items())],
        main_executable=dict(path='DT1:DuckTales',size=len(files['DT1:DuckTales']),sha256=sha256(files['DT1:DuckTales'])))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument('--init-lock', action='store_true', help='one-time lock initialization; refuses replacement')
    mode.add_argument('--write', action='store_true', help='verify fixtures and regenerate derived JSON evidence')
    mode.add_argument('--check', action='store_true', help='verify fixtures and compare fresh evidence without writing')
    ap.add_argument('--extract', action='store_true', help='also materialize read-only-purpose oracle copies in build/fixtures')
    args = ap.parse_args(argv)
    lock_path = ROOT / 'evidence/fixture-lock.json'
    if args.init_lock:
        require(not lock_path.exists(), 'lock already exists; refusing to replace it')
    else:
        verify_lock(ROOT)
    outputs, files, model = derive(ROOT)
    expected_lock = lock_document(ROOT, files)
    if args.init_lock:
        outputs['evidence/fixture-lock.json'] = expected_lock
    else:
        require(json.loads(lock_path.read_text()) == expected_lock, 'extracted fixture identity mismatch')
    for name, value in sorted(outputs.items()):
        path = ROOT / name
        expected = json_bytes(value)
        if args.check:
            require(path.exists(), f'missing evidence: {name}')
            actual = path.read_bytes()
            if actual != expected:
                first = next((i for i,(a,b) in enumerate(zip(actual,expected)) if a != b), min(len(actual),len(expected)))
                raise FormatError(f'stale evidence: {name}, first mismatch byte 0x{first:x}')
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(expected)
    if args.extract:
        require(not args.check, '--extract is a write action; omit with --check')
        for name, content in files.items():
            volume, relative = name.split(':',1)
            path = ROOT / 'build/fixtures' / volume / relative
            require(path.resolve().is_relative_to((ROOT / 'build/fixtures').resolve()), 'unsafe extraction target')
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
    print(f'{"Verified" if args.check else "Generated"} {len(outputs)} evidence documents; '
          f'{len(files)} files, {len(model["hunks"])} hunks, {len(model["relocations"])} relocations; '
          f'{model["accounted_file_bytes"]} executable bytes accounted, zero unparsed.')
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (FormatError, OSError, json.JSONDecodeError) as e:
        print(f'ERROR: {e}', file=sys.stderr)
        sys.exit(1)
