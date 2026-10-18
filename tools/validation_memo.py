"""Disposable JSON proof-validation memos; every reuse is content checked.

The registry supplies explicit in-memory inputs. During an unchanged validator
we observe file reads, path probes and directory enumerations. These inputs and
the tools import closure are hashed again before a validation scope returns.
No timestamps or on-disk Python objects grant acceptance.
"""
from names import to_mechanical
import ast
from contextlib import contextmanager
from contextvars import ContextVar
from functools import wraps
import json
import os
from pathlib import Path
import sys
import tempfile
from unittest.mock import patch

from common import require, sha256

_SESSION = ContextVar('acceptance_memo_session', default=None)
_READS = ContextVar('acceptance_memo_reads', default=None)
_QUIET = ContextVar('acceptance_memo_observing', default=False)
_STAT = Path.stat
_VERSION = 2


def compact_json(value):
    return json.dumps(value,sort_keys=True,separators=(',',':')).encode('ascii')


def digest(value):
    return sha256(compact_json(value))


def _encode(value):
    if isinstance(value, Path):
        return ['path', str(value)]
    if isinstance(value, bytes):
        return ['bytes', value.hex()]
    if isinstance(value, tuple):
        return ['tuple', [_encode(v) for v in value]]
    if isinstance(value, list):
        return ['list', [_encode(v) for v in value]]
    if isinstance(value, dict):
        return ['dict', [[k, _encode(v)] for k, v in value.items()]]
    return ['scalar', value]


def _decode(value):
    tag, data = value
    if tag == 'path':
        return Path(data)
    if tag == 'bytes':
        return bytes.fromhex(data)
    if tag == 'tuple':
        return tuple(_decode(v) for v in data)
    if tag == 'list':
        return [_decode(v) for v in data]
    if tag == 'dict':
        return {k: _decode(v) for k, v in data}
    if tag != 'scalar' or not (data is None or type(data) in (str, int, float, bool)):
        raise ValueError('invalid validation memo value')
    return data


def _observe(name, listing=False):
    reads = _READS.get()
    if reads is None or _QUIET.get() or isinstance(name, int):
        return
    token = _QUIET.set(True)
    try:
        absolute = os.path.abspath(os.fsdecode(name))
        # Import bytecode is interpreter output. Its source is bound by the
        # tools import closure; a first import may create its own .pyc.
        if absolute.endswith(('.pyc','.pyo')) or '__pycache__' in Path(absolute).parts:
            return
        key = ('list:' if listing else '') + absolute
        reads.add(key)
        _SESSION.get().observe(key)
    finally:
        _QUIET.reset(token)


def _audit(event, args):
    if event == 'open' and len(args) > 2 and args[2] & (os.O_WRONLY | os.O_RDWR):
        return
    if event in ('open', 'os.listdir', 'os.scandir') and args:
        _observe(args[0] if args[0] is not None else os.curdir, event != 'open')


sys.addaudithook(_audit)


def _stat(path, *args, **kwargs):
    _observe(path)
    return _STAT(path, *args, **kwargs)


def _fingerprint(name):
    listing = name.startswith('list:')
    path = Path(name[5:] if listing else name)
    target = str(path.resolve())
    try:
        if path.is_file():
            return dict(target=target, sha256=sha256((to_mechanical(path.read_bytes()) if _SESSION.get() is not None and path.is_relative_to(_SESSION.get().root / 'src') and path.suffix in ('.c', '.h', '.asm') else path.read_bytes())))
        if path.is_dir():
            return dict(target=target, entries=sorted(os.listdir(path))) if listing else dict(target=target, directory=True)
        return dict(target=target, absent=True)
    except FileNotFoundError:
        return dict(target=target, absent=True)


class Session:
    def __init__(self, root):
        self.root = Path(root).resolve()
        self.inputs = {}
        self.closures = {}
        self.shared = {}
        self.rows = {}
        self.pending = {}
        self.sources = {}
        self.hits = self.misses = 0

    def observe(self, name):
        if name not in self.inputs:
            token = _QUIET.set(True)
            try:
                self.inputs[name] = _fingerprint(name)
            finally:
                _QUIET.reset(token)
        return self.inputs[name]

    def closure(self, module):
        if module in self.closures:
            return self.closures[module]
        folder = Path(__file__).resolve().parent
        self.observe('list:'+str(folder))
        pending = [module, 'acceptance', 'validation_memo']
        found = {}
        while pending:
            name = pending.pop()
            if name in found:
                continue
            path = folder / (name + '.py')
            if not path.is_file():
                continue
            if name not in self.sources:
                raw=path.read_bytes();dependencies=[]
                source_hash=sha256(raw)
                require(self.observe(str(path))['sha256']==source_hash, 'validator changed while hashing import closure')
                for node in ast.walk(ast.parse(raw)):
                    if isinstance(node, ast.Import):
                        dependencies.extend(a.name.split('.')[0] for a in node.names)
                    elif isinstance(node, ast.ImportFrom) and node.module:
                        dependencies.append(node.module.split('.')[0])
                    elif isinstance(node, ast.Call) and (
                            isinstance(node.func, ast.Name) and node.func.id == '__import__' or
                            isinstance(node.func, ast.Attribute) and node.func.attr == 'import_module'):
                        if node.args and isinstance(node.args[0], ast.Constant) and isinstance(node.args[0].value, str):
                            dependencies.append(node.args[0].value.split('.')[0])
                        else:
                            dependencies.extend(p.stem for p in folder.glob('*.py'))
                self.sources[name]=(source_hash,dependencies)
            found[name],dependencies=self.sources[name]
            pending.extend(dependencies)
        closure_hash = digest(found)
        self.closures[module] = closure_hash
        return closure_hash

    def check(self):
        token = _QUIET.set(True)
        try:
            require(all(_fingerprint(n) == v for n, v in self.inputs.items()),
                    'proof validation inputs changed during snapshot creation; retry verification')
            for path,value in self.pending.items():
                try:
                    _write(path,value)
                except OSError:
                    # A performance memo is optional. On Windows a concurrent
                    # reader may hold the destination without delete sharing.
                    # The fresh proof and the complete scope check passed; an
                    # old/different cache key will simply revalidate next time.
                    pass
        finally:
            _QUIET.reset(token)



@contextmanager
def scope(root):
    current = _SESSION.get()
    if current is not None and current.root == Path(root).resolve():
        yield current
        return
    current = Session(root)
    token = _SESSION.set(current)
    try:
        with patch.object(Path, 'stat', _stat):
            yield current
            current.check()
    finally:
        _SESSION.reset(token)


def scoped(function):
    @wraps(function)
    def wrapped(root, *args, **kwargs):
        with scope(root):
            return function(root, *args, **kwargs)
    return wrapped


def _write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix='.memo-', suffix='.json', dir=path.parent)
    try:
        with os.fdopen(fd, 'wb') as stream:
            stream.write(compact_json(value))
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


@scoped
def validated(root, proof_class, ident, context, module, loader):
    """Reuse one row only for identical explicit inputs, read closure and tools."""
    session = _SESSION.get()
    parent = _READS.get()
    quiet = _QUIET.set(True)
    reads = set()
    try:
        code = session.closure(module)
        base = dict(version=_VERSION, proof_class=proof_class, id=ident,
                    context=digest(context), tools=code)
        memory_key = (proof_class, ident, base['context'], code)
        if memory_key in session.rows:
            packed, dependencies = session.rows[memory_key]
            reads.update(dependencies)
            session.hits += 1
            return _decode(packed)
        path = Path(root) / 'build/validation-memo' / proof_class / (sha256(ident.encode()) + '.json')
        try:
            memo = json.loads(path.read_bytes())
            dependencies = memo['inputs']
            current = {n: session.observe(n) for n in dependencies}
            key = digest(dict(base, inputs=current))
            if (memo['key'] == key and dependencies == current and
                    memo['value_sha256'] == digest(memo['value'])):
                value = _decode(memo['value'])
                reads.update(dependencies)
                session.hits += 1
                session.rows[memory_key] = (memo['value'], set(dependencies))
                return value
        except (OSError, ValueError, KeyError, TypeError):
            pass
        session.misses += 1
        _QUIET.reset(quiet)
        quiet = None
        trace = _READS.set(reads)
        try:
            value = loader()
        finally:
            _READS.reset(trace)
        quiet = _QUIET.set(True)
        dependencies = {n: session.observe(n) for n in sorted(reads)}
        packed = _encode(value)
        session.pending[path] = dict(key=digest(dict(base, inputs=dependencies)),
                          inputs=dependencies, value=packed,
                          value_sha256=digest(packed))
        session.rows[memory_key] = (packed, set(dependencies))
        return value
    finally:
        if parent is not None:
            parent.update(reads)
        if quiet is not None:
            _QUIET.reset(quiet)


def shared(function):
    """Reuse a common producer audit within one checked validation scope.

    Dependencies propagate to every consuming proof, even when the audit ran
    for a sibling first. Direct callers outside the registry always replay.
    """
    @wraps(function)
    def wrapped(root, *args, **kwargs):
        session = _SESSION.get()
        if session is None:
            return function(root, *args, **kwargs)
        key = (str(Path(root).resolve()), function.__module__, function.__name__, digest(_encode((args, kwargs))))
        parent = _READS.get()
        if key in session.shared:
            packed, reads = session.shared[key]
            if parent is not None:parent.update(reads)
            return _decode(packed)
        reads = set()
        trace = _READS.set(reads)
        try:
            value = function(root, *args, **kwargs)
        finally:
            _READS.reset(trace)
            if parent is not None:parent.update(reads)
        session.shared[key] = (_encode(value), reads)
        return value
    return wrapped
