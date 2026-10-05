"""Reproduce one cross-version C-shape experiment without promoting source.

The tested C is derived from exact Amiga ov10_F_2B8A and ov10_F_2BAC.
Only OMF-declared external fixup fields may differ from the DOS ov06 span.
"""
import argparse
import json
from pathlib import Path
import struct

from dos_cross_probe import compile_source, omf_probe_fixups, sha
from dos_structure import EXE, analyze


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT/'evidence/rules/dos/ov10_shared_pair.c'
SPAN_START = 0x2390
SPAN_END = 0x23D2


def receipt():
    binary = EXE.read_bytes()
    _, structure = analyze(binary)
    ov = next(x for x in structure['overlays'] if x['overlay_number'] == 6)
    body = binary[ov['file_start']+ov['header_bytes']:ov['file_end']]
    original = body[SPAN_START:SPAN_END]
    source = SOURCE.read_text()
    results = []
    for profile, tc in [('msc500', Path('C:/tools/msc-5.00')),
                        ('msc510', Path('C:/tools/msc-5.10')),
                        ('msc600a', Path('C:/tools/msc-6.00a-simantw/BIN'))]:
        built = compile_source(source, profile, tc, ['/AM', '/Os'],
                               Path('C:/tools/nmlgcdos/msdos.exe'),
                               ROOT/'build/dos/pair-proof')
        if 'error' in built:
            results.append(dict(profile=profile, error=built['error']))
            continue
        code = built.pop('code')
        object_file = next(p for p in (ROOT/'build/dos/pair-proof').glob('*/UNIT.OBJ')
                           if sha(p.read_bytes()) == built['object_sha256'])
        publics, fixups = omf_probe_fixups(object_file.read_bytes())
        masked = set()
        values = {}
        for f in fixups:
            for offset in range(f['offset'], f['offset']+f['width']):
                masked.add(offset)
            if f['offset']+f['width'] <= len(original):
                raw = original[f['offset']:f['offset']+f['width']]
                values.setdefault(f['target'], set()).add(raw.hex())
        unmatched = [at for at in range(min(len(code), len(original)))
                     if at not in masked and code[at] != original[at]]
        in_span_reloc = sorted(x['load_offset']-SPAN_START
                               for x in ov['relocations']
                               if SPAN_START <= x['load_offset'] < SPAN_END)
        predicted_reloc = sorted(f['offset']+2 for f in fixups
                                 if f['kind'] == 'pointer32')
        results.append(dict(profile=profile, flags=['/AM', '/Os'],
            source_sha256=sha(source.encode()), original_span='dos_ov06:2390..23D2',
            original_sha256=sha(original), object_sha256=built['object_sha256'],
            compiler_hashes=built['compiler_hashes'], runner_sha256=built['runner_sha256'],
            code_bytes=len(code), original_bytes=len(original),
            publics=publics, fixups=fixups,
            observed_external_fields={name: sorted(v) for name, v in values.items()},
            differing_unmasked_offsets=unmatched,
            overlay_relocation_sites_relative=in_span_reloc,
            predicted_relocation_sites_relative=predicted_reloc,
            relocation_sites_equal=in_span_reloc == predicted_reloc,
            complete_code_equal_after_external_bindings=
                len(code) == len(original) and not unmatched and
                in_span_reloc == predicted_reloc and
                all(len(v) == 1 for v in values.values())))
    return dict(schema_version=1, role='CROSS_VERSION_HYPOTHESIS_ONLY',
                dos_executable_sha256=structure['executable_sha256'],
                amiga_sources=['src/recovered/ov10/ov10_F_2B8A.c',
                               'src/recovered/ov10/ov10_F_2BAC.c'],
                warning='External binding identity and shared C shape do not prove DOS source ownership, original compiler release, or any new Amiga bytes.',
                results=results)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', type=Path)
    args = parser.parse_args()
    result = receipt()
    if args.write:
        args.write.parent.mkdir(parents=True, exist_ok=True)
        args.write.write_text(json.dumps(result, indent=2)+'\n')
    for row in result['results']:
        print(row['profile'], 'equal after external bindings',
              row.get('complete_code_equal_after_external_bindings'),
              'unmasked differences', len(row.get('differing_unmasked_offsets', [])),
              'length', row.get('code_bytes'), '/', row.get('original_bytes'))


if __name__ == '__main__':
    main()
