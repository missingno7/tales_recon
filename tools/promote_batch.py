"""Supervisor-only exact function promotions with one shared regression gate.

Every request is reverified normally. New mutually dependent functions still
use check_unit --member; independent batch entries cannot stand in for callees.
"""
import argparse
import copy
import json
from pathlib import Path
import sys

import check_function
import compiler_oracle
import compile_queue
from common import FormatError, require, sha256, json_bytes
from recovery_transaction import ledger_lock, digest, publish, recover
from repo_paths import active_files
from recovery_state import canonical_state


def input_snapshot(root, ledger, requests, compiled):
    paths = {ledger}
    for name, pattern in (('tools', '*.py'), ('tests', '*.py'), ('evidence', '*.json'), ('assets', '*'),
                          ('src/recovered', '*'), ('recovery/proofs', '*'), ('recovery/units', '*')):
        paths.update(p for p in active_files(root/name) if pattern=='*' or p.match(pattern))
    paths.update(Path(r['source']).resolve() for r in requests)
    paths.update(root / name for name in ('docs/toolchain.json', 'docs/blockers.json') if (root / name).is_file())
    for item in compiled:
        directory = Path(item['directory'])
        paths.add(directory / 'receipt.json')
        paths.update(directory / a['path'] for a in item['artifacts'])
        profile = compiler_oracle.PROFILES[item['identity']['profile']]
        paths.update(root / profile['base'] / 'bin' / name for name in ('cc', 'as', 'ln'))
        meta = item['identity']
        libbase = 'toolchain/installed/aztec-3.6a/SYS2' if meta['profile'] == 'aztec36-long' else profile['base']
        paths.add(root / libbase / 'lib' / meta['library'])
        for extra in meta.get('additional_libraries', []):
            paths.add(root / profile['base'] / 'lib' / extra['library'])
    return {str(p.resolve()): digest(p) for p in sorted(paths)}


def verification_snapshot(root, ledger, requests):
    state = input_snapshot(root, ledger, requests, [])
    # Verification may retain attempts/units and regenerate advisory ranking.
    # Its canonical dependencies, oracle evidence and toolchain must stay fixed.
    units = str((root / 'recovery/units').resolve())
    ranking = str((root / 'evidence/functions/ranking.json').resolve())
    state = {p: value for p, value in state.items()
             if p != str(ledger.resolve()) and p != ranking and not Path(p).is_relative_to(Path(units))}
    for request in requests:
        name = request['profiles'][0]
        profile = compiler_oracle.PROFILES[name]
        base = root / profile['base']
        paths = [base / 'bin' / tool for tool in ('cc', 'as', 'ln')]
        library = 'c32.lib' if name == 'aztec36-long' else 'c16.lib' if name == 'aztec50-short' else 'c.lib'
        libbase = root / 'toolchain/installed/aztec-3.6a/SYS2' if name == 'aztec36-long' else base
        paths.append(libbase / 'lib' / library)
        paths.extend(base / 'lib' / extra for extra in request.get('extra_libraries', []))
        state.update({str(p.resolve()): digest(p) for p in paths})
    return state


def span(item, report=None, root=None):
    extent = item.get('evidence_extent', item)
    end = extent['end']
    if report is not None:
        end = max(end, report.get('owned_code_data', {}).get('end', end))
    elif root is not None and item.get('state') == 'FUNCTION_WITH_DATA_MATCH':
        proof = json.loads((root / item['proof']).read_text())
        require(sha256((root / item['proof']).read_bytes()) == item['proof_sha256'], 'canonical proof changed')
        end = max(end, proof['data_ownership']['end'])
    return extent['hunk'], extent['start'], end


def validate_plan(root, ledger, entries):
    require(entries and len({e['id'] for e in entries}) == len(entries), 'batch needs unique function ids')
    intervals = {fid: span(item, root=root) for fid, item in ledger['functions'].items()}
    for entry in entries:
        fid, source, report = entry['id'], entry['source'], entry['report']
        require(report['verdict'] == 'EQUAL' and entry['compiled']['status'] == 'COMPILED',
                'every batch entry must be an exact compiled match: ' + fid)
        require(report.get('proof_level') in ('FUNCTION_CODE_MATCH', 'FUNCTION_WITH_DATA_MATCH'),
                'batch entry has no promotable contribution proof: ' + fid)
        require(report['source_sha256'] == sha256(source.encode('ascii')), 'batch source changed: ' + fid)
        prior = ledger['functions'].get(fid)
        require(not prior or prior['source_sha256'] == report['source_sha256'] or entry.get('replace_canonical'),
                'already promoted with another source; preserve canonical source: ' + fid)
        require(not prior or prior['state'] != 'FUNCTION_WITH_DATA_MATCH' or
                report['proof_level'] == 'FUNCTION_WITH_DATA_MATCH', 'replacement would discard owned CODE data: ' + fid)
        if report['proof_level'] == 'FUNCTION_WITH_DATA_MATCH':
            check_function.owned_code_data_boundary(entry['function'], entry['evidence'], report)
        candidate = span(entry['function'], report)
        for other, current in intervals.items():
            require(other == fid or current[0] != candidate[0] or current[2] <= candidate[1] or current[1] >= candidate[2],
                    'batch promotion overlaps canonical or batch contribution: ' + fid + '/' + other)
        intervals[fid] = candidate


def publish_verified(requests, entries, verified_inputs=None):
    """Internal verified-entry handoff; never trusts a worker-authored receipt."""
    require([r['id'] for r in requests] == [e['id'] for e in entries], 'batch request/entry identities differ')
    require(all(Path(r['source']).read_text() == e['source'] for r, e in zip(requests, entries)),
            'candidate changed before publication')
    root, ledger_path = check_function.ROOT.resolve(), check_function.LEDGER.resolve()
    with ledger_lock(ledger_path):
        require(verified_inputs is None or verification_snapshot(root, ledger_path, requests) == verified_inputs,
                'canonical verification inputs changed; reverify the batch')
        ledger = check_function.recovery()
        validate_plan(root, ledger, entries)
        compiled = [e['compiled'] for e in entries]
        before = input_snapshot(root, ledger_path, requests, compiled)
        regression = check_function.regression_receipt()
        require(regression.get('passed') is True, 'promotion requires a passing regression receipt')
        require(input_snapshot(root, ledger_path, requests, compiled) == before,
                'promotion inputs changed during regression; reverify the batch')
        regression = dict(regression, batch_members=[e['id'] for e in entries],
                          batch_inputs_sha256=sha256(json_bytes(before)))
        artifacts, updated, promoted = {}, copy.deepcopy(ledger), []
        for entry in entries:
            fid, report = entry['id'], check_function.durable_unit(entry['report'])
            proof = check_function.promotion_proof(fid, entry['source'], report, entry['compiled'],
                                                   entry['function'], report['proof_level'], regression)
            proof_path = root / 'recovery/proofs' / (fid + '.json')
            source_path = root / proof['source']
            artifacts[source_path] = entry['source'].encode('ascii')
            artifacts[proof_path] = json_bytes(proof)
            item = {key: proof[key] for key in ('state', 'source', 'source_sha256', 'evidence_extent', 'compiler_selection')}
            item.update(proof=proof_path.relative_to(root).as_posix(), proof_sha256=sha256(artifacts[proof_path]))
            updated['functions'][fid] = item
            updated['blockers'].pop(fid, None)
            promoted.append(item)
        transaction = publish(root, ledger_path, artifacts, canonical_state(updated), before[str(ledger_path)])
    return dict(status='PROMOTED', transaction=transaction, functions=[e['id'] for e in entries],
                promotions=promoted, regression=regression)


def run(requests, verify_only=False):
    require(isinstance(requests, list) and requests, 'batch manifest must be a nonempty JSON array')
    require(len({r['id'] for r in requests}) == len(requests), 'batch needs unique function ids')
    for request in requests:
        require(len(request.get('profiles', [])) == 1, 'choose exactly one explicit profile for each batch entry')
        require(not request.get('owned_static_data'), 'initialized DATA proof is not independently promotable')
    # Freeze candidate text before verification; reread afterward rather than
    # accepting a receipt for an edited source file.
    texts = [Path(r['source']).read_text() for r in requests]
    ledger_hash = digest(check_function.LEDGER)
    verified_inputs = verification_snapshot(check_function.ROOT, check_function.LEDGER, requests)
    compile_queue.install()
    reports = check_function.check_many(requests, promote_equal=False)
    entries = []
    for request, text, report in zip(requests, texts, reports):
        fid = request['id']
        require(report['verdict'] == 'EQUAL', 'batch verification failed; no canonical writes: ' + fid)
        require(report['source_sha256'] == sha256(text.encode('ascii')) and Path(request['source']).read_text() == text,
                'candidate changed during batch verification: ' + fid)
        f, evidence = check_function.validated_function(fid)
        compiled = compiler_oracle.cached(report['cache_key'])
        require(compiled is not None, 'verified compiler artifact is missing')
        entries.append(dict(id=fid, source=text, report=report, compiled=compiled,
                            function=f, evidence=evidence, replace_canonical=bool(request.get('replace_canonical'))))
    require(len(entries) == len(requests), 'verifier did not return every batch entry')
    if verify_only:
        require(verification_snapshot(check_function.ROOT, check_function.LEDGER, requests) == verified_inputs,
                'canonical verification inputs changed; reverify the batch')
        validate_plan(check_function.ROOT, check_function.recovery(), entries)
        return dict(status='VERIFIED_ONLY', functions=[e['id'] for e in entries], canonical_writes=False,
                    initial_ledger_sha256=ledger_hash)
    result = publish_verified(requests, entries, verified_inputs)
    check_function.save_rank()
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('manifest', type=Path, nargs='?')
    parser.add_argument('--verify-only', action='store_true')
    parser.add_argument('--recover', metavar='TRANSACTION_ID')
    args = parser.parse_args(argv)
    if args.recover:
        require(args.manifest is None and not args.verify_only, '--recover accepts only a transaction id')
        result = dict(status=recover(check_function.LEDGER, args.recover))
    else:
        require(args.manifest is not None, 'a batch manifest is required')
        result = run(json.loads(args.manifest.read_text()), args.verify_only)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (FormatError, OSError, ValueError, KeyError) as exc:
        print(json.dumps(dict(status='BLOCKED', reason=str(exc))))
        sys.exit(2)
