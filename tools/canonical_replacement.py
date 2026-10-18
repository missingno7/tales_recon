"""Replace a canonical source and re-prove every receipt that pinned it, or change nothing.

A complete-unit receipt names the exact source hashes of its canonical
dependencies (``dependency_sources``).  Replacing one of those sources leaves
such receipts stale, so the evidence loaders reject the whole canonical state.
The replacement and the re-proof of every dependent therefore run as one
transaction: one regression gate on the consistent pre-state, the replacement
with the dependents retained as canonical consumers inside a recoverable
transaction, then each dependent re-verified exactly from its own unchanged canonical source against
the new one.  Any failure restores the prior ledger, proofs and sources.
Dependents proved in a multi-member or object-grouped unit are not
re-derivable from their proof alone and refuse the replacement.
"""
import json

from analysis_support import ROOT
from common import require
from repo_paths import canonical_path
from names import source_path

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
                **({'canonical_ref':item['source']} if '#' in item['source'] else {}),
                owned_code_data=item['state'] == 'FUNCTION_WITH_DATA_MATCH')


def closure(fid, ledger):
    """Every canonical proof that transitively pins ``fid``'s current source.

    Returns ``{id: (request, pinned_ids)}``: the re-proof request and the ids
    its complete-unit receipt pins (re-proved only after those are back).
    """
    found = {}
    pending = [fid]
    while pending:
        current = pending.pop()
        for other, item, proof, unit in dependents(current, ledger['functions'][current]['source_sha256'], ledger):
            if other in found:
                continue
            found[other] = (reproof_request(other, item, proof, unit), set(unit.get('dependency_sources', {})))
            pending.append(other)
    return found


def replace(fid, write, *, regression=None):
    """Run ``write(regression)`` (the replacement promotion), then re-prove dependents.

    ``write`` must promote ``fid`` with the given regression receipt and
    ``replace_canonical``.  Every transitive dependent is retained and
    re-proved in dependency order, each after the canonical sources its
    receipt pins are back.  Returns the dependent re-proof reports.
    """
    import check_function
    ledger = check_function.recovery()
    prior = ledger['functions'][fid]
    chain = closure(fid, ledger)
    if regression is None:regression = check_function.regression_receipt()
    from recovery_transaction import replacement_scope
    from consumer_rebinding import pin_scope
    import census
    with replacement_scope(ROOT,check_function.LEDGER,lambda:census.derive(ROOT,promotion_evidence=True)) as transaction, pin_scope(ROOT):
        transaction.snapshot([source_path(ROOT, prior['source'])])
        write(regression)
        return reprove(chain, regression)


def reprove(chain, regression):
    """Keep accepted consumers present while refreshing dependency receipts.

    Intermediate stale unit pins exist only inside the recoverable transaction;
    every dependent still takes the exact comparison route. Strict canonical
    replay must pass before COMMITTED; a failure restores the entire graph.
    """
    import check_function
    from census import advisory_image
    with advisory_image():
        reports = []
        waiting = dict(chain)
        while waiting:
            ready = sorted(o for o, (_, pins) in waiting.items() if not (pins & set(waiting)))
            require(ready, 'replacement dependents pin each other in a cycle: ' + ','.join(sorted(waiting)))
            for other in ready:
                request = waiting.pop(other)[0]
                report = check_function.check_many([request], regression=regression)[0]
                require(report['verdict'] == 'EQUAL' and report.get('promotion'),
                        'dependent re-proof failed against the replacement: ' + other)
                reports.append(report)
        return reports
