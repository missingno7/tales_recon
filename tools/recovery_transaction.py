"""Serialized recovery-ledger writes and recoverable canonical publication.

Files are staged first; the ledger is the final commit point. An interrupted
publication fails closed until its journal is explicitly recovered. No game
bytes are used to produce reconstructed sources.
"""
from contextlib import contextmanager
import json
import os
from pathlib import Path
import tempfile
import uuid

from common import FormatError, require, sha256, json_bytes, write_json
import file_lock


def journals(ledger):
    return ledger.parent.parent / 'build/promotion-transactions'


def pending(ledger):
    return [p.parent.name for p in journals(ledger).glob('*/journal.json')
            if json.loads(p.read_text())['status'] == 'PREPARED']


@contextmanager
def ledger_lock(ledger, recovery=False):
    ledger = Path(ledger).resolve()
    with file_lock.locked(ledger.with_name('writer.lock'), 'recovery ledger writer', 120,
                          'recovery ledger', stale_after=3600):
        if not recovery:
            unfinished = pending(ledger)
            require(not unfinished, 'unfinished promotion transaction; run tools/promote_batch.py --recover ' +
                    ','.join(unfinished))
        yield


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
               (path.is_relative_to(root / 'src/recovered') and path.suffix == '.c') or
               (path.is_relative_to(root / 'recovery/proofs') and path.suffix == '.json'))
    require(allowed, 'unsupported promotion transaction target: ' + relative)
    return path


def _restore(root, ledger, directory, journal):
    # Inspect every target before restoring any, so a foreign edit is retained.
    for entry in journal['files']:
        path = target(root, entry['path'], ledger)
        require(digest(path) in (entry['before_sha256'], entry['after_sha256']),
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
        if digest(ledger) == last['after_sha256']:
            require(all(digest(target(root, e['path'], ledger)) == e['after_sha256'] for e in journal['files']),
                    'committed transaction artifacts changed')
            journal['status'] = 'COMMITTED'
            write_json(directory / 'journal.json', journal)
        else:
            require(digest(ledger) == last['before_sha256'], 'ledger conflicts with interrupted transaction')
            _restore(root, ledger, directory, journal)
        return journal['status']
