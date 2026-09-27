"""Read-only overlay closure map from exact promotions and immutable census facts.

This is a planning aid, not an ownership or source-unit proof. It never fills
unclaimed gaps or infers original translation-unit boundaries.
"""
import argparse
import json

from analysis_support import ROOT
from common import require, sha256
from owned_code_data import expected_string_tail


def partition(size, intervals):
    """Tile one initialized CODE hunk with proven contributions and debt."""
    rows = []
    cursor = 0
    for item in sorted(intervals, key=lambda x: (x['start'], x['end'])):
        start, end = item['start'], item['end']
        require(cursor <= start < end <= size, 'overlapping or out-of-range overlay contribution')
        if cursor < start:
            rows.append(dict(kind='UNCLAIMED', start=cursor, end=start, size=start-cursor))
        rows.append(dict(item, size=end-start))
        cursor = end
    if cursor < size:
        rows.append(dict(kind='UNCLAIMED', start=cursor, end=size, size=size-cursor))
    return rows


def contribution_intervals(root, functions, promotions):
    by_id = {f['id']: f for f in functions}
    intervals = {}
    for fid, item in promotions.items():
        f = by_id.get(fid)
        require(f is not None, 'promoted function absent from census: '+fid)
        extent = item['evidence_extent']
        require(all(extent[k] == f[k] for k in ('hunk', 'start', 'end', 'size', 'sha256')),
                'promoted extent differs from census: '+fid)
        source = root / item['source']
        proof_path = root / item['proof']
        require(source.is_file() and sha256(source.read_bytes()) == item['source_sha256'],
                'promoted source identity differs: '+fid)
        require(proof_path.is_file() and sha256(proof_path.read_bytes()) == item['proof_sha256'],
                'promotion receipt identity differs: '+fid)
        proof = json.loads(proof_path.read_text())
        require(proof['id'] == fid and proof['state'] == item['state'] and
                proof['comparison']['verdict'] == 'EQUAL', 'invalid promotion receipt: '+fid)
        target = intervals.setdefault(f['hunk'], [])
        target.append(dict(kind='VERIFIED_CODE', id=fid, start=f['start'], end=f['end']))
        if item['state'] == 'FUNCTION_WITH_DATA_MATCH':
            tail, ownership = expected_string_tail(f)
            claimed = proof['data_ownership']
            require(claimed['start'] == ownership['start'] and claimed['end'] == ownership['end'] and
                    claimed['expected_tail_sha256'] == sha256(tail) and
                    claimed['actual_tail_sha256'] == sha256(tail),
                    'owned literal contribution differs: '+fid)
            target.append(dict(kind='VERIFIED_LITERAL', id=fid,
                               start=ownership['start'], end=ownership['end']))
    return intervals


def report(root=ROOT, node=None):
    census = json.loads((root/'evidence/functions/ledger.json').read_text())
    recovered = json.loads((root/'recovery/ledger.json').read_text())
    modules = json.loads((root/'docs/modules.json').read_text())['modules']
    ranking = json.loads((root/'evidence/functions/ranking.json').read_text())['candidates']
    rank = {x['id']: i for i, x in enumerate(ranking)}
    intervals = contribution_intervals(root, census['functions'], recovered['functions'])
    results = []
    for module in modules:
        if not module['id'].startswith('ov') or node and module['id'] != node:
            continue
        require(len(module['hunks']) == 1, 'overlay should contain one CODE hunk')
        hunk = module['hunks'][0]
        size = module['initialized_bytes']
        tiles = partition(size, intervals.get(hunk, []))
        unclaimed = [x for x in tiles if x['kind'] == 'UNCLAIMED']
        candidates = [f for f in census['functions'] if f['hunk'] == hunk and
                      f['id'] not in recovered['functions'] and f['ownership'] == 'UNKNOWN']
        for gap in unclaimed:
            contained = [f for f in candidates if gap['start'] <= f['start'] and f['end'] <= gap['end']]
            contained.sort(key=lambda f: (rank.get(f['id'], 10**9), f['start']))
            gap['candidates'] = [dict(id=f['id'], start=f['start'], end=f['end'],
                                      extent=f['extent_status'],
                                      state='BLOCKED' if f['id'] in recovered['blockers']
                                            else ranking[rank[f['id']]]['state'] if f['id'] in rank
                                            else 'DISCOVERED')
                                 for f in contained]
        local_calls = []
        for f in census['functions']:
            if f['hunk'] != hunk:
                continue
            for call in f['direct_callees']:
                if call['hunk'] == hunk and call['id'] not in recovered['functions']:
                    local_calls.append(dict(caller=f['id'], callee=call['id'], site=call['site'],
                                            caller_verified=f['id'] in recovered['functions']))
        proven_code = sum(x['size'] for x in tiles if x['kind'] == 'VERIFIED_CODE')
        proven_literals = sum(x['size'] for x in tiles if x['kind'] == 'VERIFIED_LITERAL')
        unclaimed_bytes = sum(x['size'] for x in unclaimed)
        require(proven_code + proven_literals + unclaimed_bytes == size,
                'overlay initialized CODE partition is incomplete')
        results.append(dict(node=module['id'], hunk=hunk, initialized_code_bytes=size,
                            verified_function_bytes=proven_code,
                            verified_literal_bytes=proven_literals,
                            unclaimed_bytes=unclaimed_bytes,
                            closed_candidates=sum(f['extent_status'] == 'CLOSED_CFG' for f in candidates),
                            uncertain_candidates=sum(f['extent_status'] != 'CLOSED_CFG' for f in candidates),
                            unresolved_local_calls=local_calls, tiles=tiles,
                            complete_overlay_proven=False))
    require(not node or results, 'unknown overlay node: '+str(node))
    return dict(schema_version=1, method='DIAGNOSTIC_ONLY',
                note='Unclaimed CODE may contain code, data, padding, or runtime; candidate extents grant no ownership. DATA/BSS and natural link remain separate obligations.',
                overlays=results)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--node', help='one physical overlay, for example ov14')
    parser.add_argument('--json', action='store_true', help='include interval details as JSON')
    args = parser.parse_args()
    result = report(node=args.node)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        for row in result['overlays']:
            print('%s CODE %d: verified functions %d, literals %d, unclaimed %d; '
                  '%d closed / %d uncertain candidates, %d calls into unrecovered local code' %
                  (row['node'], row['initialized_code_bytes'], row['verified_function_bytes'],
                   row['verified_literal_bytes'], row['unclaimed_bytes'],
                   row['closed_candidates'], row['uncertain_candidates'],
                   len(row['unresolved_local_calls'])))
            if args.node:
                for gap in row['tiles']:
                    if gap['kind'] != 'UNCLAIMED':
                        continue
                    ids = ', '.join(x['id'] for x in gap['candidates'][:5]) or 'no function candidate'
                    print('  %04X..%04X %d bytes: %s' % (gap['start'], gap['end'], gap['size'], ids))


if __name__ == '__main__':
    main()
