"""Bounded, content-checked reuse of read-only game derivations.

No on-disk cache, fixture relocking, or cached verification verdicts. Outside
an explicit scope every read derives afresh. Strict and advisory images have
separate entries, and every reuse hashes the current inputs rather than stats.
"""
from contextlib import contextmanager
from contextvars import ContextVar
from functools import wraps
import json
from pathlib import Path
import pickle
import time

from common import require, sha256, json_bytes

_ACTIVE = ContextVar('evidence_snapshot', default=None)


class Snapshot:
    def __init__(self, enabled=True):
        self.enabled = enabled
        self.entries = {}
        self.parsed = {}
        self.hits = self.misses = self.invalidations = 0
        self.hash_seconds = self.derive_seconds = 0.0

    def inputs(self, root, strict):
        """Actual census/proof dependencies, including ledger-directed paths."""
        started = time.perf_counter()
        root = Path(root).resolve()
        values = {}
        resolved = {}
        contents = {}

        def target(path):
            key = str(path)
            if key not in resolved:
                resolved[key] = path.resolve()
            return resolved[key]

        def read(path):
            path = target(path)
            require(path.is_relative_to(root), 'snapshot input escapes workspace: ' + str(path))
            if str(path) in contents:return contents[str(path)]
            try:raw = path.read_bytes()
            except FileNotFoundError:raw = None
            contents[str(path)] = raw
            values[str(path)] = sha256(raw) if raw is not None else None
            return raw

        def document(path):
            raw = read(path)
            if raw is None:return {}
            key = str(target(path))
            digest = sha256(raw)
            prior = self.parsed.get(key)
            if prior is None or prior[0] != digest:
                prior = digest, json.loads(raw)
                self.parsed[key] = prior
            return prior[1]

        from census import inputs
        for path in inputs(root):read(path)
        for path in sorted((root / 'tools').glob('*.py')):read(path)
        read(root / 'evidence/fixture-lock.json')
        if strict:
            analysis = document(root / 'evidence/functions/ledger.json')
            for name in analysis.get('analysis_identity', {}):read(root / 'tools' / name)
            for name in ('runtime-matches.json', 'overlay-topology.json'):
                read(root / 'evidence/experiments' / name)
            ledger_path = root / 'recovery/ledger.json'
            ledger = document(ledger_path)
            # Census reads canonical functions only. Attempts and queue blockers
            # can change during a batch without changing any derived output.
            if values[str(ledger_path.resolve())] is not None:
                values[str(ledger_path.resolve())] = sha256(json_bytes(ledger['functions']))
            for item in ledger.get('functions', {}).values():
                read(root / item['source'])
                proof = document(root / item['proof'])
                unit_name = proof.get('comparison', {}).get('complete_unit_receipt')
                if unit_name:
                    unit_path = root / unit_name
                    unit = document(unit_path)
                    read(unit_path.parent / 'unit.c')
                    if unit.get('object_groups') is not None:
                        for member in unit['ordered_members']:
                            read(unit_path.parent / 'parts' / (member['id'] + '.c'))
        self.hash_seconds += time.perf_counter() - started
        return values

    def load(self, root, strict, loader):
        key = str(Path(root).resolve()), strict
        before = self.inputs(root, strict)
        entry = self.entries.get(key)
        if entry is not None and entry[0] == before:
            self.hits += 1
            return pickle.loads(entry[1])
        if entry is not None:
            self.invalidations += 1
            del self.entries[key]
        self.misses += 1
        started = time.perf_counter()
        value = loader()
        self.derive_seconds += time.perf_counter() - started
        require(self.inputs(root, strict) == before,
                'game derivation inputs changed during snapshot creation; retry verification')
        # The C serializer is much cheaper than recursively copying the large
        # census output. These bytes are created here and kept only in memory;
        # never deserialize a disk cache or worker-provided pickle.
        packed = pickle.dumps(value, protocol=pickle.HIGHEST_PROTOCOL)
        self.entries[key] = before, packed
        return pickle.loads(packed)


@contextmanager
def snapshot(enabled=True):
    """Nested scopes share one snapshot; outer exit discards all retained data."""
    current = _ACTIVE.get()
    if current is not None:
        yield current
        return
    current = Snapshot(enabled)
    token = _ACTIVE.set(current)
    try:
        yield current
    finally:
        _ACTIVE.reset(token)
        current.entries.clear()
        current.parsed.clear()


def scoped(function):
    @wraps(function)
    def wrapped(*args, **kwargs):
        with snapshot():
            return function(*args, **kwargs)
    return wrapped


def game_read(root, loader):
    active = _ACTIVE.get()
    if active is None or not active.enabled:return loader()
    from census import _PROMOTION_EVIDENCE
    return active.load(root, bool(_PROMOTION_EVIDENCE[0]), loader)
