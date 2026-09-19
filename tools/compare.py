"""Compare a candidate executable with the locked oracle; never promote proof.

Raw content, allocation/order, and ordered relocation equality are reported
separately. Byte equality cannot establish independent source or natural linking.
"""
import argparse
from pathlib import Path
import sys
from common import FormatError, sha256, write_json
from census import ROOT, verify_lock, derive
from hunk import parse


def first_bytes(expected, actual):
    n = next((i for i, (a,b) in enumerate(zip(expected,actual)) if a != b), min(len(expected),len(actual)))
    if n == len(expected) == len(actual):
        return None
    return dict(offset=n, expected=expected[n:n+16].hex(), actual=actual[n:n+16].hex(),
                expected_size=len(expected), actual_size=len(actual))


def compare(expected, actual):
    report = dict(schema_version=1, expected_sha256=sha256(expected), actual_sha256=sha256(actual),
        whole_file_equal=expected == actual, first_file_mismatch=first_bytes(expected,actual),
        reconstruction_proof_level=None, natural_link_proven=False,
        caveat='Equality alone does not establish source reconstruction or toolchain provenance.')
    em = parse(expected)
    try:
        am = parse(actual)
    except FormatError as e:
        report.update(candidate_parse_error=str(e), hunk_content_equal=False,
                      hunk_layout_equal=False, relocations_equal=False)
        return report
    def layout(m):
        return [(h['number'],h['node'],h['type'],h['allocated_size'],h['initialized_size'],h['memory_flags_raw']) for h in m['hunks']]
    def relocs(m):
        return [(r['source_hunk'],r['source_offset'],r['target_hunk'],r['type'],r['width']) for r in m['relocations']]
    def first_list(a,b):
        n = next((i for i,(x,y) in enumerate(zip(a,b)) if x != y), min(len(a),len(b)))
        return None if n == len(a) == len(b) else dict(index=n, expected=a[n] if n<len(a) else None, actual=b[n] if n<len(b) else None)
    report.update(hunk_layout_equal=layout(em)==layout(am), first_layout_mismatch=first_list(layout(em),layout(am)),
                  relocations_equal=relocs(em)==relocs(am), first_relocation_mismatch=first_list(relocs(em),relocs(am)))
    def headers(m):
        return [(n['header_offset'],n['table_size_raw'],n['first_hunk'],n['last_hunk'],n['allocations'],n['resident_names'])
                for n in m['nodes']]
    def records(m):
        return [(r['file_offset'],r['type'],r['file_size'],r['logical_hunk']) for r in m['records']]
    report.update(header_layout_equal=headers(em)==headers(am), first_header_mismatch=first_list(headers(em),headers(am)),
                  file_record_layout_equal=records(em)==records(am), first_record_layout_mismatch=first_list(records(em),records(am)),
                  overlay_table_equal=em['overlay']==am['overlay'])
    checks = []
    actual_hunks = {h['number']:h for h in am['hunks']}
    for h in em['hunks']:
        ah = actual_hunks.get(h['number'])
        if ah is None:
            checks.append(dict(hunk=h['number'], equal=False, error='missing hunk'))
            continue
        def content(data, item):
            off = item['content_offset']
            return b'' if off is None else data[off:off+item['initialized_size']]
        eb, ab = content(expected,h), content(actual,ah)
        checks.append(dict(hunk=h['number'], equal=eb==ab, first_mismatch=first_bytes(eb,ab)))
    report.update(hunks=checks, hunk_content_equal=all(h['equal'] for h in checks) and len(em['hunks'])==len(am['hunks']))
    return report


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('candidate', type=Path)
    ap.add_argument('--report', type=Path, required=True, help='retain an experiment-specific comparison report')
    args = ap.parse_args()
    verify_lock(ROOT)
    _, files, _ = derive(ROOT)
    report = compare(files['DT1:DuckTales'], args.candidate.read_bytes())
    report['candidate_path'] = str(args.candidate)
    write_json(args.report, report)
    print('whole_file_equal=' + str(report['whole_file_equal']) + '; proof level remains unassigned')
    return 0 if report['whole_file_equal'] else 1


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (FormatError,OSError) as e:
        print(f'ERROR: {e}', file=sys.stderr)
        sys.exit(1)
