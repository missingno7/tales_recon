"""Compile recovered Amiga C with candidate DOS compilers for exploratory search.

Exact substring hits here are code-byte observations only. They do not promote
Amiga or DOS source and they do not prove an original compiler release.
"""
import argparse
from difflib import SequenceMatcher
import hashlib
import json
import os
from pathlib import Path
import subprocess
import struct

from dos_capstone import capstone

from dos_structure import EXE, analyze
from dos_functions import census, decoder


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PROFILES = {'msc500': Path('C:/tools/msc-5.00'),
                    'msc510': Path('C:/tools/msc-5.10')}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def index(data, at):
    value = data[at]
    return (((value & 127) << 8) | data[at+1], at+2) if value & 128 else (value, at+1)


def omf_code(data):
    """Read contiguous 16-bit CODE LEDATA for one controlled compiler probe."""
    names = []
    segments = []
    writes = []
    at = 0
    while at < len(data):
        if at+3 > len(data):
            raise ValueError('truncated OMF record')
        kind, size = data[at], struct.unpack_from('<H', data, at+1)[0]
        end = at+3+size
        if size < 1 or end > len(data) or sum(data[at:end]) & 255:
            raise ValueError('invalid OMF size/checksum')
        body = data[at+3:end-1]
        if kind == 0x96:
            p = 0
            while p < len(body):
                n = body[p]
                p += 1
                names.append(body[p:p+n].decode('ascii'))
                p += n
        elif kind == 0x98:
            p = 3
            name, p = index(body, p)
            cls, p = index(body, p)
            _, p = index(body, p)
            segments.append(dict(name=names[name-1], cls=names[cls-1],
                                 size=struct.unpack_from('<H', body, 1)[0]))
        elif kind == 0xa0:
            seg, p = index(body, 0)
            off = struct.unpack_from('<H', body, p)[0]
            writes.append((seg, off, body[p+2:]))
        at = end
    codes = [(i+1, s) for i, s in enumerate(segments) if s['cls'] == 'CODE']
    if len(codes) != 1:
        raise ValueError('probe needs exactly one CODE segment')
    seg, item = codes[0]
    out = bytearray(item['size'])
    touched = bytearray(item['size'])
    for n, offset, part in writes:
        if n != seg:
            continue
        if offset+len(part) > len(out) or any(touched[offset:offset+len(part)]):
            raise ValueError('overlapping/out-of-bounds CODE LEDATA')
        out[offset:offset+len(part)] = part
        touched[offset:offset+len(part)] = bytes([1])*len(part)
    if not all(touched):
        raise ValueError('incomplete CODE LEDATA')
    return bytes(out)


def omf_probe_fixups(data):
    """Bounded 16-bit FIXUPP/PUBDEF reader for controlled CODE-only probes."""
    externals = []
    publics = []
    fixups = []
    frame_threads = {}
    target_threads = {}
    last_segment = last_offset = None
    at = 0
    while at < len(data):
        kind, size = data[at], struct.unpack_from('<H', data, at+1)[0]
        end = at+3+size
        if size < 1 or end > len(data) or sum(data[at:end]) & 255:
            raise ValueError('invalid OMF record')
        body = data[at+3:end-1]
        if kind == 0x8c:  # EXTDEF
            p = 0
            while p < len(body):
                n = body[p]
                externals.append(body[p+1:p+1+n].decode('ascii'))
                p += 1+n
                _, p = index(body, p)
        elif kind == 0x90:  # PUBDEF
            group, p = index(body, 0)
            segment, p = index(body, p)
            if group == segment == 0:
                p += 2
            while p < len(body):
                n = body[p]
                name = body[p+1:p+1+n].decode('ascii')
                p += 1+n
                offset = struct.unpack_from('<H', body, p)[0]
                p += 2
                _, p = index(body, p)
                publics.append(dict(name=name, segment_index=segment, offset=offset))
        elif kind == 0xa0:  # LEDATA
            last_segment, p = index(body, 0)
            last_offset = struct.unpack_from('<H', body, p)[0]
        elif kind == 0x9c:  # FIXUPP, including persistent threads
            p = 0
            while p < len(body):
                if body[p] & 0x80:
                    locat = (body[p] << 8) | body[p+1]
                    p += 2
                    loc = (locat >> 10) & 15
                    offset = locat & 1023
                    self_relative = not ((locat >> 14) & 1)
                    fixdat = body[p]
                    p += 1
                    if fixdat & 0x80:
                        frame_method, frame_index = frame_threads[(fixdat >> 4) & 3]
                    else:
                        frame_method = (fixdat >> 4) & 7
                        frame_index = 0
                        if frame_method in (0, 1, 2):
                            frame_index, p = index(body, p)
                        elif frame_method == 3:
                            frame_index = struct.unpack_from('<H', body, p)[0]
                            p += 2
                    if fixdat & 8:
                        target_method, target_index = target_threads[fixdat & 3]
                    else:
                        target_method = fixdat & 3
                        target_index, p = index(body, p)
                    displacement = 0
                    if not fixdat & 4:
                        displacement = struct.unpack_from('<H', body, p)[0]
                        p += 2
                    if last_segment is None or loc not in (1, 3) or target_method != 2:
                        raise ValueError('unsupported controlled-probe FIXUPP')
                    fixups.append(dict(segment_index=last_segment,
                                       offset=last_offset+offset,
                                       width={1: 2, 3: 4}[loc],
                                       kind={1: 'offset16', 3: 'pointer32'}[loc],
                                       self_relative=self_relative,
                                       target=externals[target_index-1],
                                       frame_method=frame_method,
                                       frame_index=frame_index,
                                       displacement=displacement))
                else:
                    thread = body[p]
                    p += 1
                    is_frame = (thread >> 6) & 1
                    method = (thread >> 2) & 7
                    number = thread & 3
                    datum = 0
                    if not (is_frame and method in (4, 5, 6)):
                        datum, p = index(body, p)
                    (frame_threads if is_frame else target_threads)[number] = (method, datum)
        at = end
    return publics, fixups


def compile_source(source, profile, tc, flags, runner, workroot):
    tool_hashes = {name: sha((tc/name).read_bytes())
                   for name in ('CL.EXE', 'C1.EXE', 'C1L.EXE', 'C2.EXE', 'C3.EXE')}
    runner_hash = sha(runner.read_bytes())
    identity = sha((source+profile+' '.join(flags)+''.join(tool_hashes.values())+
                    runner_hash).encode())
    work = workroot / identity[:16]
    work.mkdir(parents=True, exist_ok=True)
    unit = work/'UNIT.C'
    unit.write_bytes(source.replace('\r\n', '\n').replace('\n', '\r\n').encode('ascii'))
    command = [str(runner), '-e', '-v5.00', str(tc/'CL.EXE'), '/c'] + flags + ['UNIT.C']
    env = {'PATH': str(tc), 'MSDOS_PATH': str(tc), 'TEMP': '.',
           'TMP': '.', 'MSDOS_TEMP': '.'}
    obj = work/'UNIT.OBJ'
    reused = obj.exists()
    if not reused:
        result = subprocess.run(command, cwd=work.resolve(), env=env,
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                timeout=90, creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
        (work/'compiler.log').write_bytes(result.stdout)
        if result.returncode or not obj.exists():
            return dict(error='compiler failed', returncode=result.returncode,
                        log=result.stdout.decode('latin1')[-1000:], command=command)
    raw = obj.read_bytes()
    try:
        code = omf_code(raw)
    except ValueError as exc:
        return dict(error='object parse: '+str(exc), command=command,
                    object_sha256=sha(raw))
    return dict(code=code, profile=profile, flags=flags,
                compiler_hashes=tool_hashes, runner_sha256=runner_hash,
                command=command, object_sha256=sha(raw), code_sha256=sha(code),
                cache_hit=reused)


def probe(paths, profiles, flags):
    binary = EXE.read_bytes()
    root_image, structure = analyze(binary)
    catalog = census(binary)
    images = [('root', root_image)] + [
        ('dos_ov%02d' % row['overlay_number'],
         binary[row['file_start']+row['header_bytes']:row['file_end']])
        for row in structure['overlays']]
    md = decoder()
    runner = Path('C:/tools/nmlgcdos/msdos.exe')
    if not runner.is_file():
        raise ValueError('missing DOS runner')
    results = []
    for path in paths:
        source = (ROOT/path).read_text()
        for name, tc in profiles.items():
            compiled = compile_source(source, name, tc, flags, runner,
                                      ROOT/'build/dos/cross-probes')
            entry = dict(source=str(path), source_sha256=sha(source.encode()),
                         profile=name)
            if 'error' in compiled:
                entry.update(compiled)
                results.append(entry)
                continue
            code = compiled.pop('code')
            compiled.pop('cache_hit', None)
            entry.update(compiled)
            entry['code_bytes'] = len(code)
            entry['exact_occurrences'] = [dict(image=image, offset=at)
                for image, body in images
                for at in [body.find(code)] if at >= 0]
            needle = [i.mnemonic for i in md.disasm(code, 0)]
            similar = []
            for overlay in catalog['overlays']:
                for f in overlay['candidates']:
                    if f['extent'] != 'CLOSED_CFG' or not f['mnemonics']:
                        continue
                    if not max(8, len(code)//3) <= f['span_bytes'] <= len(code)*3+64:
                        continue
                    score = SequenceMatcher(None, needle, f['mnemonics'],
                                            autojunk=False).ratio()
                    similar.append(dict(id=f['id'], score=round(score, 4),
                                        span_bytes=f['span_bytes']))
            entry['top_mnemonic_shapes'] = sorted(similar,
                key=lambda x: (-x['score'], abs(x['span_bytes']-len(code))))[:3]
            results.append(entry)
    return dict(schema_version=1, role='EXPLORATORY_CROSS_VERSION_PROBE',
                dos_executable_sha256=structure['executable_sha256'],
                runner_sha256=sha(runner.read_bytes()),
                warning='Compiler resemblance and mnemonic ranking alone prove no source correspondence.',
                results=results)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('sources', nargs='+', type=Path)
    parser.add_argument('--profile', action='append', choices=DEFAULT_PROFILES,
                        help='default: msc500 and msc510')
    parser.add_argument('--flag', action='append',
                        help='repeat to override default /AM /O /Gs')
    parser.add_argument('--write', type=Path)
    args = parser.parse_args()
    selected = {name: DEFAULT_PROFILES[name]
                for name in (args.profile or list(DEFAULT_PROFILES))}
    result = probe(args.sources, selected, args.flag or ['/AM', '/O', '/Gs'])
    if args.write:
        args.write.parent.mkdir(parents=True, exist_ok=True)
        args.write.write_text(json.dumps(result, indent=2)+'\n')
    for row in result['results']:
        print(row['source'], row['profile'], row.get('code_bytes'),
              'exact', row.get('exact_occurrences', []),
              'top', row.get('top_mnemonic_shapes', [])[:1], row.get('error', ''))


if __name__ == '__main__':
    main()
