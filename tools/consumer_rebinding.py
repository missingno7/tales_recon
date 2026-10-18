"""Rebind consumer facts only across identical exact compiler results.

DATA proofs are replayed by data_providers.verify; their embedded hashes are
never patched. A replacement scope journals the source, C proof, facts, recipes,
DATA proofs and ledger together, and commits only after strict canonical replay.
"""
from contextlib import contextmanager
from contextvars import ContextVar
from copy import deepcopy
import json
from pathlib import Path

from common import require, sha256, json_bytes
from repo_paths import active_files

_INDEX = ContextVar('canonical_consumer_pin_index', default=None)


def result_identity(proof):
    comparison = proof.get('comparison', {})
    code = comparison.get('code_comparison', comparison)
    object_hash = proof.get('object_hash')
    require(isinstance(object_hash, str) and len(object_hash) == 64,
            'consumer rebinding needs a complete compiler object hash')
    require(comparison.get('verdict') == code.get('verdict') == 'EQUAL' and
            comparison.get('relocation_equal') is True and not comparison.get('relocation_issues'),
            'consumer rebinding requires an exact comparison and relocation proof')
    normalized = code.get('normalized_sha256')
    require(normalized and normalized == code.get('expected_sha256') and
            code.get('actual_length') == code.get('expected_length') and code.get('actual_length') is not None,
            'consumer rebinding needs a complete normalized comparison hash')
    owned = comparison.get('owned_code_data')
    if proof.get('state') == 'FUNCTION_WITH_DATA_MATCH':
        require(owned and owned == proof.get('data_ownership') and
                owned.get('actual_tail_sha256') == owned.get('expected_tail_sha256') and
                owned.get('actual_tail_sha256'), 'consumer rebinding needs an exact owned DATA tail')
    else:
        require(proof.get('state') == 'FUNCTION_CODE_MATCH' and not owned,
                'unsupported consumer replacement proof class')
    return (object_hash, normalized, proof.get('state'), proof.get('evidence_extent'),
            code['actual_length'], comparison.get('actual_length'), owned, proof.get('relocation_proof'))


def require_identical(old, new):
    require(result_identity(old) == result_identity(new),
            'consumer rebinding refused: compiled result differs (object, normalized CODE, extent, tail or bindings)')


def nodes(value):
    if isinstance(value, dict):
        yield value
        for child in value.values(): yield from nodes(child)
    elif isinstance(value, list):
        for child in value: yield from nodes(child)


class PinIndex:
    """One corpus scan per replacement batch; subsequent visits follow edges."""
    def __init__(self, root):
        self.root = Path(root).resolve()
        self.documents = {}; self.raw_hashes = {}; self.pairs = {}; self.references = {}
        for folder in ('evidence', 'recovery', 'docs'):
            for path in active_files(self.root / folder, '.json'):
                name = path.relative_to(self.root).as_posix()
                if name == 'recovery/ledger.json': continue
                raw = path.read_bytes()
                self.documents[name] = json.loads(raw)
                self.raw_hashes[name] = sha256(raw)
                self.index(name)

    def index(self, name):
        for group in (self.pairs, self.references):
            for paths in group.values(): paths.discard(name)
        for node in nodes(self.documents[name]):
            pair = (node.get('source_sha256'), node.get('proof_sha256'))
            if all(isinstance(v, str) for v in pair):self.pairs.setdefault(pair, set()).add(name)
            for key, value in node.items():
                if key.endswith('_sha256') and isinstance(value, str):
                    path = node.get(key[:-7])
                    if isinstance(path, str):self.references.setdefault(path, set()).add(name)

    def changes(self, prior, new):
        old_pair = (prior['source_sha256'], prior['proof_sha256'])
        pair = (new['source_sha256'], new['proof_sha256'])
        changed = {}
        for name in sorted(self.pairs.get(old_pair, ())):
            # Canonical DATA proofs must be regenerated. Other canonical proof
            # classes need an explicit producer, never a patched receipt.
            if name.startswith('recovery/proofs/'):
                if name.startswith('recovery/proofs/data/'):continue
                require(name == prior['proof'], 'no consumer-proof producer for ' + name)
                continue
            value = deepcopy(self.documents[name])
            for node in nodes(value):
                if (node.get('source_sha256'), node.get('proof_sha256')) == old_pair:
                    node.update(source_sha256=pair[0], proof_sha256=pair[1])
                    if node.get('source') == prior['source']:node['source'] = new['source']
            changed[name] = value
        # Rebind path+digest edges, including producer member fact hashes and
        # facts which name independently typed target facts. Iterate only the
        # affected closure. A cycle or unknown digest fails closed.
        pending = list(changed)
        steps = 0
        while pending:
            name = pending.pop(0); steps += 1
            require(steps <= max(100, len(self.documents)*4), 'cyclic fact digest dependencies')
            digest = sha256(json_bytes(changed[name]))
            for consumer in sorted(self.references.get(name, ())):
                if consumer.startswith('recovery/proofs/data/'):continue
                require(not consumer.startswith('recovery/proofs/'), 'no consumer-proof producer for ' + consumer)
                value = deepcopy(changed.get(consumer, self.documents[consumer])); touched = False
                for node in nodes(value):
                    for key in list(node):
                        if key.endswith('_sha256') and node.get(key[:-7]) == name and node[key] != digest:
                            require(node[key] in (self.raw_hashes[name], sha256(json_bytes(self.documents[name]))),
                                    'fact digest was already stale: ' + consumer)
                            node[key] = digest; touched = True
                if touched:
                    if 'members' in value and 'cache_key' in value and 'prefixes' in value:
                        from data_providers import batch_key
                        value['cache_key'] = batch_key(value)
                    changed[consumer] = value; pending.append(consumer)
        return changed

    def committed(self, artifacts):
        for path, raw in artifacts.items():
            name = Path(path).relative_to(self.root).as_posix()
            if name in self.documents:
                self.documents[name] = json.loads(raw);self.raw_hashes[name] = sha256(raw);self.index(name)


@contextmanager
def pin_scope(root):
    current = _INDEX.get()
    if current is not None:
        require(current.root == Path(root).resolve(), 'consumer pin scope belongs to another repository')
        yield current;return
    # Index lazily: ordinary publications with no prior canonical entry do not
    # need any corpus scan.
    token = _INDEX.set(PinIndex(root))
    try:yield _INDEX.get()
    finally:_INDEX.reset(token)


def publish(root, ledger_path, artifacts, ledger, prior, new_proof):
    """Publish a replacement and replay its affected typed DATA providers."""
    from recovery_transaction import publish as stage, digest, replacement_scope
    import census
    root = Path(root).resolve();ledger_path = Path(ledger_path).resolve()
    old = json.loads((root / prior['proof']).read_bytes())
    require(old.get('source') == prior['source'] and old.get('source_sha256') == prior['source_sha256'], 'old canonical source binding changed')
    require(sha256((root / prior['proof']).read_bytes()) == prior['proof_sha256'], 'old canonical proof changed')
    require_identical(old, new_proof)
    with replacement_scope(root, ledger_path, lambda:census.derive(root, promotion_evidence=True)) as replacement, pin_scope(root) as index:
        if '#' in new_proof['source']:
            from names import source_path
            replacement.snapshot([source_path(root,new_proof['source'])])
        changed = index.changes(prior, ledger['functions'][new_proof['id']])
        affected = set()
        pinned_proofs = index.pairs.get((prior['source_sha256'], prior['proof_sha256']), set())
        for ident, item in ledger.get('data_providers', {}).items():
            fact = changed.get(item['fact'], index.documents[item['fact']])
            if item['proof'] in pinned_proofs or item['fact'] in changed or fact['producer']['batch'] in changed:affected.add(ident)
        combined = dict(artifacts)
        combined.update({root/name:json_bytes(value) for name,value in changed.items()})
        transaction = stage(root, ledger_path, combined, ledger, digest(ledger_path))
        if affected:
            import data_providers
            from validation_memo import scope
            from game_image import game
            from names import read_source
            with census.advisory_image():blob,model,_ = game()
            analysis = json.loads((root/'evidence/functions/ledger.json').read_bytes())
            # Strict pre-state + unchanged exact compiler results retain the
            # canonical accepted set. The final strict replay validates all
            # canonical functions and DATA proofs before this journal commits.
            promotions = [dict(id=fid) for fid in ledger['functions']]
            refreshed = {}
            with scope(root):
                for ident in sorted(affected):
                    item = ledger['data_providers'][ident]
                    fact = json.loads((root/item['fact']).read_bytes())
                    previous = json.loads((root/item['proof']).read_bytes())
                    report = data_providers.verify(root,blob,model,analysis,ledger,promotions,fact,read_source(root,item['source']),None)
                    for key in ('object_sha256','actual_sha256','source_sha256','original','sections','symbols',
                                'relocation_bindings','original_relocations','candidate_relocations','data_hex','owned_literals'):
                        require(previous['comparison'].get(key) == report.get(key), 'DATA compiled result changed during consumer rebinding: '+ident+' '+key)
                    proof = dict(fact=fact,comparison=report,regression=previous['regression'])
                    raw = json_bytes(proof);refreshed[root/item['proof']] = raw
                    item['proof_sha256'] = sha256(raw)
            transaction = stage(root, ledger_path, refreshed, ledger, digest(ledger_path))
            combined.update(refreshed)
        index.committed(combined)
        return transaction
