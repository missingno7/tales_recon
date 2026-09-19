"""Small deterministic evidence helpers; no build-time oracle interface."""
import hashlib
import json
import os
import tempfile


class FormatError(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise FormatError(message)


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def json_bytes(value):
    return (json.dumps(value, indent=2, ensure_ascii=True, sort_keys=True) + "\n").encode()


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    # A cancelled long-running grinder must not leave a truncated ledger.
    fd,name=tempfile.mkstemp(prefix=path.name+'.',suffix='.tmp',dir=path.parent)
    try:
        with os.fdopen(fd,'wb') as out:out.write(json_bytes(value))
        os.replace(name,path)
    finally:
        if os.path.exists(name):os.unlink(name)
