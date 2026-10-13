"""Replace a canonical source and re-prove every receipt that pinned it, or change nothing.

A complete-unit receipt names the exact source hashes of its canonical
dependencies (``dependency_sources``).  Replacing one of those sources leaves
such receipts stale, so the evidence loaders reject the whole canonical state.
The replacement and the re-proof of every dependent therefore run as one
transaction: one regression gate on the consistent pre-state, the replacement
with the dependents withdrawn from the ledger (the state they were first
proved in, so every intermediate canonical state stays loadable), then each
dependent re-verified exactly from its own unchanged canonical source against
the new one.  Any failure restores the prior ledger, proofs and sources.
Dependents proved in a multi-member or object-grouped unit are not
re-derivable from their proof alone and refuse the replacement.
"""
import json

from analysis_support import ROOT
from common import require
from repo_paths import canonical_path

# Receipt fields that mean the dependent's proof needs its own unit options.
UNIT_OPTION_KEYS = ('object_groups', 'object_partition', 'proven_object_groups',
                    'object_group_merged_declarations', 'profile_record', 'member_profiles')


def dependents(fid, digest, ledger):
    """Canonical proofs whose complete-unit receipt pins ``fid`` at ``digest``."""
    found = []
    for other, item in sorted(ledger['functions'].items()):
        if other == fid or not item.get('proof'):
            continue
        proof = json.loads(canonical_path(ROOT, item['proof']).read_bytes())
        name = proof['comparison'].get('complete_unit_receipt')
        if not name:
            continue
        unit = json.loads(canonical_path(ROOT, name).read_bytes())
        if unit.get('dependency_sources', {}).get(fid) == digest:
            found.append((other, item, proof, unit))
    return found


def reproof_request(other, item, proof, unit):
    """The single-target request that re-derives a dependent's proof."""
    require(unit.get('id') == other and not any(k in unit for k in UNIT_OPTION_KEYS),
            'replacement would stale a grouped or multi-member unit receipt; re-prove it explicitly first: ' + other)
    profile = proof['compiler'].get('profile')
    require(profile, 'dependent proof names no compiler profile: ' + other)
    return dict(id=other, source=item['source'], profiles=[profile],
                owned_code_data=item['state'] == 'FUNCTION_WITH_DATA_MATCH')


def replace(fid, write):
    """Run ``write(regression)`` (the replacement promotion), then re-prove dependents.

    ``write`` must promote ``fid`` with the given regression receipt and
    ``replace_canonical``.  Returns the dependent re-proof reports.
    """
    import check_function
    ledger = check_function.recovery()
    prior = ledger['functions'][fid]
    requests = [reproof_request(*d) for d in dependents(fid, prior['source_sha256'], ledger)]
    for request in requests:
        require(not dependents(request['id'], ledger['functions'][request['id']]['source_sha256'], ledger),
                'replacement dependent is itself pinned by another receipt: ' + request['id'])
    regression = check_function.regression_receipt()
    paths = [check_function.LEDGER, ROOT / prior['source'], ROOT / prior['proof']]
    paths += [ROOT / ledger['functions'][r['id']]['proof'] for r in requests]
    saved = {p: p.read_bytes() for p in paths}
    try:
        write(regression)
        if requests:
            from recovery_transaction import ledger_lock
            with ledger_lock(check_function.LEDGER):
                current = check_function.recovery()
                for request in requests:
                    current['functions'].pop(request['id'])
                check_function.write_recovery(current, check_function.LEDGER)
        reports = check_function.check_many(requests, regression=regression) if requests else []
        for request, report in zip(requests, reports):
            require(report['verdict'] == 'EQUAL' and report.get('promotion'),
                    'dependent re-proof failed against the replacement: ' + request['id'])
        return reports
    except BaseException:
        for path, data in saved.items():
            path.write_bytes(data)
        raise
