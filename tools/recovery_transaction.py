"""Serialized recovery-ledger writes and recoverable canonical publication.

Files are staged first; the ledger is the final commit point. An interrupted
publication fails closed until its journal is explicitly recovered. No game
bytes are used to produce reconstructed sources.
"""
from contextlib import contextmanager
from contextvars import ContextVar
import json
import os
from pathlib import Path
import tempfile
import uuid

from common import FormatError, require, sha256, json_bytes, write_json
import file_lock


_LOCKED = ContextVar('recovery_locked_ledgers', default=())
_REPLACEMENT = ContextVar('recovery_replacement_transaction', default=None)


def journals(ledger):
    return ledger.parent.parent / 'build/promotion-transactions'


def pending(ledger):
    return [p.parent.name for p in journals(ledger).glob('*/journal.json')
            if json.loads(p.read_text())['status'] == 'PREPARED']


@contextmanager
def ledger_lock(ledger, recovery=False):
    ledger = Path(ledger).resolve()
    if ledger in _LOCKED.get():
        yield
        return
    with file_lock.locked(ledger.with_name('writer.lock'), 'recovery ledger writer', 120,
                          'recovery ledger', stale_after=3600):
        if not recovery:
            unfinished = pending(ledger)
            require(not unfinished, 'unfinished promotion transaction; run tools/promote_batch.py --recover ' +
                    ','.join(unfinished))
        token = _LOCKED.set((*_LOCKED.get(), ledger))
        try:yield
        finally:_LOCKED.reset(token)


def replace_bytes(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix=path.name + '.', suffix='.tmp', dir=path.parent)
    try:
        with os.fdopen(fd, 'wb') as out:
            out.write(data)
            out.flush()
            os.fsync(out.fileno())
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def digest(path):
    return sha256(path.read_bytes()) if path.is_file() else None


def target(root, relative, ledger):
    path = (root / relative).resolve()
    require(path.is_relative_to(root), 'transaction target escapes workspace')
    allowed = (path == ledger or
               (path.is_relative_to(root / 'src') and path.suffix == '.c') or
               (path.is_relative_to(root / 'src/recovered/asm-reconstructed') and path.suffix == '.asm') or
               (path.is_relative_to(root / 'src/recovered/code-data') and path.suffix == '.asm') or
               (path.is_relative_to(root / 'recovery/proofs') and path.suffix == '.json') or
               (path.is_relative_to(root / 'evidence') and path.suffix == '.json'))
    require(allowed, 'unsupported promotion transaction target: ' + relative)
    return path


def _restore(root, ledger, directory, journal):
    # Inspect every target before restoring any, so a foreign edit is retained.
    for entry in journal['files']:
        path = target(root, entry['path'], ledger)
        require(digest(path) in (entry['before_sha256'], entry['after_sha256'], *entry.get('intermediate_sha256', [])),
                'transaction recovery conflicts with a later edit: ' + entry['path'])
        if entry['before_sha256'] is not None:
            require(digest(directory / entry['before']) == entry['before_sha256'], 'transaction backup changed')
    for entry in reversed(journal['files']):
        path = target(root, entry['path'], ledger)
        if entry['before_sha256'] is None:
            if path.exists():
                path.unlink()
        else:
            replace_bytes(path, (directory / entry['before']).read_bytes())
    journal['status'] = 'ROLLED_BACK'
    write_json(directory / 'journal.json', journal)


def publish(root, ledger, artifacts, new_ledger, expected_ledger_sha256):
    """Caller holds ledger_lock. Return a journal id; commit ledger last."""
    root, ledger = Path(root).resolve(), Path(ledger).resolve()
    active = _REPLACEMENT.get()
    if active is not None:
        require(active.root == root and active.ledger == ledger, 'nested replacement belongs to another repository')
        return active.publish(artifacts, new_ledger, expected_ledger_sha256)
    require(digest(ledger) == expected_ledger_sha256, 'recovery ledger changed during batch verification')
    transaction = uuid.uuid4().hex
    directory = journals(ledger) / transaction
    directory.mkdir(parents=True)
    files = dict(artifacts)
    require(ledger not in files, 'ledger must be the final transaction artifact')
    files[ledger] = json_bytes(new_ledger)
    require(sha256(files[ledger]) != expected_ledger_sha256, 'transaction has no distinct ledger commit')
    entries = []
    for index, (path, data) in enumerate(files.items()):
        path = Path(path).resolve()
        relative = path.relative_to(root).as_posix()
        target(root, relative, ledger)
        before, after = 'before/%04d' % index, 'after/%04d' % index
        old = path.read_bytes() if path.is_file() else None
        if old is not None:
            replace_bytes(directory / before, old)
        replace_bytes(directory / after, data)
        entries.append(dict(path=relative, before=before, after=after,
                            before_sha256=sha256(old) if old is not None else None,
                            after_sha256=sha256(data)))
    journal = dict(schema_version=1, status='PREPARED', ledger=ledger.relative_to(root).as_posix(), files=entries)
    write_json(directory / 'journal.json', journal)
    try:
        for entry in entries:
            replace_bytes(root / entry['path'], (directory / entry['after']).read_bytes())
    except Exception:
        # A replacement can finish and then raise. The ledger hash determines
        # whether all preceding source/proof writes have already committed.
        if digest(ledger) != entries[-1]['after_sha256']:
            _restore(root, ledger, directory, journal)
            raise
    journal['status'] = 'COMMITTED'
    try:
        write_json(directory / 'journal.json', journal)
    except OSError:
        pass  # Explicit recovery recognizes the committed ledger after a crash.
    return transaction


def recover(ledger, transaction):
    require(len(transaction) == 32 and all(c in '0123456789abcdef' for c in transaction),
            'invalid promotion transaction id')
    ledger = Path(ledger).resolve()
    root = ledger.parent.parent
    with ledger_lock(ledger, recovery=True):
        directory = journals(ledger) / transaction
        journal = json.loads((directory / 'journal.json').read_text())
        require(journal['ledger'] == ledger.relative_to(root).as_posix(), 'journal belongs to another ledger')
        require(journal['status'] == 'PREPARED', 'transaction is already resolved')
        last = journal['files'][-1]
        require(target(root, last['path'], ledger) == ledger, 'journal has no final ledger commit')
        if journal.get('mode') == 'EXACT_REPLACEMENT':
            _restore(root, ledger, directory, journal)
        elif digest(ledger) == last['after_sha256']:
            require(all(digest(target(root, e['path'], ledger)) == e['after_sha256'] for e in journal['files']),
                    'committed transaction artifacts changed')
            journal['status'] = 'COMMITTED'
            write_json(directory / 'journal.json', journal)
        else:
            require(digest(ledger) == last['before_sha256'], 'ledger conflicts with interrupted transaction')
            _restore(root, ledger, directory, journal)
        return journal['status']


class ReplacementTransaction:
    """One recoverable journal for a source and its dependent proof refreshes.

    Intermediate ledgers may have stale dependency pins. They are never a
    committed replacement: the complete strict canonical replay must pass before
    COMMITTED. Recovery rolls a PREPARED replacement back, even if its latest
    intermediate ledger write finished. Every overwritten version is hash-bound.
    """
    def __init__(self, root, ledger):
        self.root = Path(root).resolve(); self.ledger = Path(ledger).resolve()
        self.id = uuid.uuid4().hex
        self.directory = journals(self.ledger) / self.id
        self.entries = {}
        self.journal = dict(schema_version=1, status='PREPARED', mode='EXACT_REPLACEMENT',
                            ledger=self.ledger.relative_to(self.root).as_posix(), files=[])

    def snapshot(self, paths):
        """Journal physical module bytes without rewriting a supervisor's source."""
        self.publish({Path(p).resolve():Path(p).read_bytes() for p in paths},
                     None,digest(self.ledger),snapshot_only=True)

    def publish(self, artifacts, new_ledger, expected, *, snapshot_only=False):
        require(digest(self.ledger) == expected, 'recovery ledger changed during replacement')
        files = dict(artifacts)
        require(self.ledger not in files, 'ledger must be the final transaction artifact')
        files[self.ledger] = self.ledger.read_bytes() if snapshot_only else json_bytes(new_ledger)
        for path, data in files.items():
            path = Path(path).resolve(); relative = path.relative_to(self.root).as_posix()
            target(self.root, relative, self.ledger)
            if relative not in self.entries:
                index = len(self.entries)
                old = path.read_bytes() if path.is_file() else None
                before, after = 'before/%04d' % index, 'after/%04d' % index
                if old is not None:replace_bytes(self.directory / before, old)
                self.entries[relative] = dict(path=relative, before=before, after=after,
                    before_sha256=sha256(old) if old is not None else None,
                    after_sha256=sha256(data), intermediate_sha256=[])
            else:
                entry = self.entries[relative]
                require(digest(path) == entry['after_sha256'], 'replacement conflicts with a later edit: ' + relative)
                if entry['after_sha256'] not in entry['intermediate_sha256']:
                    entry['intermediate_sha256'].append(entry['after_sha256'])
                entry['after_sha256'] = sha256(data)
            replace_bytes(self.directory / self.entries[relative]['after'], data)
        # Persist the rollback graph before touching any canonical file.
        ledger_name = self.ledger.relative_to(self.root).as_posix()
        self.journal['files'] = [e for n,e in self.entries.items() if n != ledger_name] + [self.entries[ledger_name]]
        write_json(self.directory / 'journal.json', self.journal)
        if not snapshot_only:
            for path, data in files.items():replace_bytes(path, data)
        return self.id


@contextmanager
def replacement_scope(root, ledger, validate):
    """Serialize, journal and strictly validate the entire replacement closure."""
    active = _REPLACEMENT.get()
    if active is not None:
        require(active.root == Path(root).resolve() and active.ledger == Path(ledger).resolve(),
                'nested replacement belongs to another repository')
        yield active
        return
    with ledger_lock(ledger):
        transaction = ReplacementTransaction(root, ledger)
        token = _REPLACEMENT.set(transaction)
        try:
            yield transaction
            if transaction.entries:
                validate()
                transaction.journal['status'] = 'COMMITTED'
                write_json(transaction.directory / 'journal.json', transaction.journal)
        except BaseException:
            if transaction.entries and (transaction.directory/'journal.json').exists():
                _restore(transaction.root, transaction.ledger, transaction.directory, transaction.journal)
            raise
        finally:_REPLACEMENT.reset(token)
