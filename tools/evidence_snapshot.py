"""Bounded, content-checked reuse of read-only game derivations.

No on-disk cache or fixture relocking. Strict and advisory images have separate
entries. Exact replay may opt into bounded process reuse with a complete,
freshly content-hashed identity; ordinary reads need an explicit snapshot scope.
"""
from contextlib import contextmanager
from contextvars import ContextVar
from functools import wraps
import json
from collections import OrderedDict
from pathlib import Path
import pickle
import time

from common import require, sha256, json_bytes, FormatError
from repo_paths import batched_paths,canonical_path

_PROCESS = OrderedDict()

_ACTIVE = ContextVar('evidence_snapshot', default=None)
_VALIDATED = ContextVar('evidence_snapshot_inputs', default=())


class Snapshot:
    def __init__(self, enabled=True):
        self.enabled = enabled
        self.entries = {}
        self.parsed = {}
        self.hits = self.misses = self.invalidations = 0
        self.hash_seconds = self.derive_seconds = 0.0

    @batched_paths
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
                try:resolved[key]=canonical_path(root,path)
                except FormatError:
                    actual=path.resolve()
                    require(actual.is_relative_to(root),'snapshot input escapes workspace: '+str(actual))
                    raise
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
        from curated_unreferenced_entries import INPUT as uncalled_entry_input
        read(root / uncalled_entry_input)
        from dead_code_extents import inputs as dead_code_inputs
        for name in dead_code_inputs(root):read(root / name)
        from audio_sequence_data import inputs as code_data_inputs
        for name in code_data_inputs(root):read(root / name)
        if strict:
            from runtime_accounting import input_identity as runtime_input_identity
            values.update(runtime_input_identity(root))
            from data_providers import input_identity as provider_input_identity
            values.update(provider_input_identity(root))
            from reconstructed_asm import input_identity as reconstructed_asm_inputs
            values.update(reconstructed_asm_inputs(root))
            from code_data_providers import input_identity as code_data_inputs
            values.update(code_data_inputs(root))
            from resident_mixed import source_object_inputs
            for name in source_object_inputs(root):read(root / name)
            from startup_recovery import inputs as startup_inputs
            for name in startup_inputs(root):read(root / name)
            analysis = document(root / 'evidence/functions/ledger.json')
            for name in analysis.get('analysis_identity', {}):read(root / 'tools' / name)
            for name in ('runtime-matches.json', 'overlay-topology.json'):
                read(root / 'evidence/experiments' / name)
            ledger_path = root / 'recovery/ledger.json'
            ledger = document(ledger_path)
            # Census reads canonical functions only. Attempts and queue blockers
            # can change during a batch without changing any derived output.
            if values[str(ledger_path.resolve())] is not None:
                values[str(ledger_path.resolve())] = sha256(json_bytes(dict(
                    functions=ledger['functions'], code_data_providers=ledger.get('code_data_providers', {}), reconstructed_asm=ledger.get('reconstructed_asm', {}), mixed_source_objects=ledger.get('mixed_source_objects', {}), dead_code_functions=ledger.get('dead_code_functions', {}), data_providers=ledger.get('data_providers', {}))))
            for item in list(ledger.get('mixed_source_objects', {}).values())+list(ledger.get('dead_code_functions', {}).values()):
                read(root / item['source']); read(root / item['proof'])
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

    def _discard_scope(self, root, strict):
        root_key = str(Path(root).resolve())
        strict = bool(strict)
        for key in list(self.entries):
            if key[0] == root_key and key[1] == strict:
                del self.entries[key]

    def load(self, root, strict, loader, namespace='game', identity=None):
        strict = bool(strict)
        root_key = str(Path(root).resolve())
        key = root_key, strict, namespace
        stage = next((row for row in reversed(_VALIDATED.get())
                      if row[0] is self and row[1] == root_key and row[2] == strict), None)
        def current_inputs():
            values = dict(stage[3]) if stage is not None else self.inputs(root, strict)
            if identity is not None:
                values['@identity:' + namespace] = identity
            return values
        before = current_inputs()
        entry = self.entries.get(key)
        if entry is not None and entry[0] == before:
            if namespace == 'game':self.hits += 1
            return pickle.loads(entry[1])
        if entry is not None:
            if namespace == 'game':self.invalidations += 1
            self._discard_scope(root, strict)
        if namespace == 'game':self.misses += 1
        started = time.perf_counter()
        try:
            # The enclosing load already hashes this complete closure before
            # and after the loader. Nested reads of the same strictness share
            # that observation instead of hashing it at every namespace layer.
            token=None
            if stage is None:
                token=_VALIDATED.set(_VALIDATED.get()+((self,root_key,strict,before),))
            try:value = loader()
            finally:
                if token is not None:_VALIDATED.reset(token)
            if stage is None:
                after = current_inputs()
                require(after == before,
                        'game derivation inputs changed during snapshot creation; retry verification')
            # The C serializer is much cheaper than recursively copying the large
            # census output. These bytes are created here and kept only in memory;
            # never deserialize a disk cache or worker-provided pickle.
            packed = pickle.dumps(value, protocol=pickle.HIGHEST_PROTOCOL)
        except BaseException:
            self._discard_scope(root, strict)
            raise
        self.derive_seconds += time.perf_counter() - started
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


@contextmanager
def validated_stage(root, strict=True):
    """Rehash a stage's full inputs once before and after its nested derivations."""
    active = _ACTIVE.get()
    if active is None or not active.enabled:
        yield
        return
    root_key = str(Path(root).resolve())
    strict = bool(strict)
    parent = next((row for row in reversed(_VALIDATED.get())
                   if row[0] is active and row[1] == root_key and row[2] == strict), None)
    if parent is not None:
        yield
        return
    before = active.inputs(root, strict)
    stack = _VALIDATED.get()
    token = _VALIDATED.set(stack + ((active, root_key, strict, before),))
    try:
        yield
    except BaseException:
        _VALIDATED.reset(token)
        active._discard_scope(root, strict)
        raise
    else:
        _VALIDATED.reset(token)
        try:
            after = active.inputs(root, strict)
            require(after == before,
                    'refresh stage inputs changed during derivation; retry verification')
        except BaseException:
            active._discard_scope(root, strict)
            raise


@contextmanager
def isolated_verification(root, enabled=True):
    """An isolated verifier run as one validated stage.

    Isolated runs write nothing that is a census or proof input, so the strict
    and advisory input sets are hashed once on entry and once on exit instead
    of on every derivation reuse. Promotion runs keep per-read rehashing.
    """
    if not enabled:
        yield
        return
    with snapshot(), validated_stage(root, strict=True), validated_stage(root, strict=False):
        yield


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
    return active.load(root, bool(_PROMOTION_EVIDENCE[0]), loader, namespace='game')


def memoized(root, namespace, identity, loader, strict=True, *, process_cache=False):
    """Memoize a read-only derivation only inside the active, rehashing scope."""
    if process_cache:
        # The caller must supply a complete, freshly content-hashed identity.
        # Only in-memory results created by this process are deserialized.
        key = str(Path(root).resolve()), bool(strict), namespace, identity
        packed = _PROCESS.get(key)
        if packed is None:
            packed = pickle.dumps(loader(), protocol=pickle.HIGHEST_PROTOCOL)
            _PROCESS[key] = packed
            while len(_PROCESS) > 16:_PROCESS.popitem(last=False)
        else:_PROCESS.move_to_end(key)
        return pickle.loads(packed)
    active = _ACTIVE.get()
    if active is None or not active.enabled:
        return loader()
    return active.load(root, bool(strict), loader, namespace=namespace, identity=identity)



@contextmanager
def content_stage(root,identity):
    """Nested derivations of a caller-checked complete content replay.

    Only a caller that hashes the complete closure before AND after its replay
    may use this scope. It grants no acceptance and changes no ordinary stage.
    """
    active=_ACTIVE.get()
    if active is None or not active.enabled:
        yield
        return
    root_key=str(Path(root).resolve());values={'@complete-content-replay':identity}
    token=_VALIDATED.set(_VALIDATED.get()+tuple((active,root_key,strict,values) for strict in [True,False]))
    try:yield
    finally:_VALIDATED.reset(token)
