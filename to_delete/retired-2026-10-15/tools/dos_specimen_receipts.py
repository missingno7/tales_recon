"""Reproduce two ov09/DOS-ov07 source-shape comparisons as secondary evidence."""
import argparse
import json
from pathlib import Path

from dos_cross_probe import compile_source, omf_probe_fixups, sha
from dos_structure import EXE, analyze


ROOT = Path(__file__).resolve().parents[1]
SPECS = [('ov09_F_18D0', 0x1226, 0x1263),
         ('ov09_F_1924', 0x1263, 0x128F)]


def receipts():
    binary = EXE.read_bytes()
    _, structure = analyze(binary)
    overlay = structure['overlays'][6]
    body = binary[overlay['file_start']+overlay['header_bytes']:overlay['file_end']]
    rows = []
    for name, start, end in SPECS:
        path = ROOT/'src/recovered/ov09'/ (name+'.c')
        source = path.read_text()
        built = compile_source(source, 'msc510', Path('C:/tools/msc-5.10'),
                               ['/AM', '/Os'], Path('C:/tools/nmlgcdos/msdos.exe'),
                               ROOT/'build/dos/specimen-probes')
        if 'error' in built:
            raise ValueError(name+': '+built['error'])
        code = built.pop('code')
        object_file = next(p for p in (ROOT/'build/dos/specimen-probes').glob('*/UNIT.OBJ')
                           if sha(p.read_bytes()) == built['object_sha256'])
        publics, fixups = omf_probe_fixups(object_file.read_bytes())
        original = body[start:end]
        masked = {at for f in fixups for at in range(f['offset'], f['offset']+f['width'])}
        unmasked = [at for at in range(min(len(code), len(original)))
                    if at not in masked and code[at] != original[at]]
        observed_relocs = sorted(x['load_offset']-start for x in overlay['relocations']
                                 if start <= x['load_offset'] < end)
        predicted_relocs = sorted(f['offset']+2 for f in fixups
                                  if f['kind'] == 'pointer32')
        field_values = {}
        for f in fixups:
            observed = original[f['offset']:f['offset']+f['width']]
            field_values.setdefault(f['target'], set()).add(observed.hex())
        tail = code[len(original):]
        rows.append(dict(amiga_function=name, amiga_source=str(path.relative_to(ROOT)),
                         amiga_source_sha256=sha(source.encode()),
                         dos_candidate='dos_ov07_F_%04X' % start,
                         dos_span=[start, end], dos_body_sha256=sha(original),
                         compiler='msc510', flags=['/AM', '/Os'],
                         compiler_hashes=built['compiler_hashes'],
                         object_sha256=built['object_sha256'],
                         object_code_bytes=len(code), dos_body_bytes=len(original),
                         publics=publics, fixups=fixups,
                         observed_external_fields={k: sorted(v) for k,v in field_values.items()},
                         unmatched_unmasked_offsets=unmasked,
                         object_tail_after_dos_body_hex=tail.hex(),
                         observed_overlay_relocation_sites=observed_relocs,
                         predicted_overlay_relocation_sites=predicted_relocs,
                         body_equal_after_external_bindings=
                            len(code) >= len(original) and not unmasked and
                            observed_relocs == predicted_relocs,
                         complete_object_code_equal_after_bindings=
                            len(code) == len(original) and not unmasked and
                            observed_relocs == predicted_relocs))
    return dict(schema_version=1, role='CROSS_VERSION_HYPOTHESIS_ONLY',
                dos_executable_sha256=structure['executable_sha256'],
                warning='An exact body with standalone trailing padding does not prove complete original translation-unit ownership.',
                results=rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', type=Path)
    args = parser.parse_args()
    data = receipts()
    if args.write:
        args.write.parent.mkdir(parents=True, exist_ok=True)
        args.write.write_text(json.dumps(data, indent=2)+'\n')
    for row in data['results']:
        print(row['amiga_function'], 'body equal',row['body_equal_after_external_bindings'],
              'complete object',row['complete_object_code_equal_after_bindings'],
              'tail',row['object_tail_after_dos_body_hex'])


if __name__ == '__main__':
    main()
