"""Owner-annotated exclusive lock files for parallel experiment processes.

A lock is a file created with ``O_EXCL`` that records its owner (pid, host,
start time, purpose).  Waiters poll with a bounded timeout.  A lock whose owner
process is gone, or an unannotated lock older than ``stale_after`` seconds, is
*reported* as stale; it is never removed or taken over automatically.
"""
from contextlib import contextmanager
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import socket
import sys
import time
import uuid

from common import FormatError


HOST = socket.gethostname()


def pid_alive(pid):
    """True when a process with ``pid`` exists on this host (conservative)."""
    if type(pid) is not int or pid <= 0:
        return False
    if pid == os.getpid():
        return True
    if sys.platform == "win32":
        # os.kill(pid, 0) would terminate the process on Windows.
        import ctypes
        from ctypes import wintypes
        kernel = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel.OpenProcess.restype = wintypes.HANDLE
        kernel.OpenProcess.argtypes = (wintypes.DWORD, wintypes.BOOL, wintypes.DWORD)
        handle = kernel.OpenProcess(0x1000, False, pid)  # PROCESS_QUERY_LIMITED_INFORMATION
        if not handle:
            return ctypes.get_last_error() == 5  # access denied: it exists
        try:
            code = wintypes.DWORD()
            if not kernel.GetExitCodeProcess(handle, ctypes.byref(code)):
                return True
            return code.value == 259  # STILL_ACTIVE
        finally:
            kernel.CloseHandle(handle)
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def owner_record(purpose):
    return dict(pid=os.getpid(), host=HOST, token=uuid.uuid4().hex,
                started=datetime.now(timezone.utc).isoformat(timespec="seconds"),
                started_epoch=time.time(), purpose=purpose)


def inspect(path):
    """Describe a lock file; ``None`` when absent."""
    path = Path(path)
    try:
        stat = path.stat()
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return None
    except OSError as exc:
        return dict(path=str(path), owner=None, age_seconds=None, state="UNREADABLE", error=str(exc))
    try:
        owner = json.loads(text) if text.strip() else None
    except json.JSONDecodeError:
        owner = None
    if not isinstance(owner, dict):
        owner = None
    age = max(0.0, time.time() - stat.st_mtime)
    if owner is None:
        state = "UNANNOTATED"
    elif owner.get("host") != HOST:
        state = "OTHER_HOST"
    else:
        state = "LIVE" if pid_alive(owner.get("pid")) else "DEAD_OWNER"
    return dict(path=str(path), owner=owner, age_seconds=round(age, 1), state=state)


def stale_reason(info, stale_after):
    """Return a report string when the lock can never be released by its owner."""
    if info is None:
        return None
    if info["state"] == "DEAD_OWNER":
        return "owner pid %s (started %s) is not running" % (info["owner"].get("pid"), info["owner"].get("started"))
    if info["state"] in ("UNANNOTATED", "OTHER_HOST") and stale_after is not None and info["age_seconds"] > stale_after:
        return "lock has no live local owner and is %.0f s old" % info["age_seconds"]
    return None


def try_acquire(path, purpose):
    """Create the lock atomically; return the owner record or ``None``."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    owner = owner_record(purpose)
    try:
        fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError:
        return None
    except PermissionError:
        # Windows reports a lock file that is being deleted, or briefly
        # opened by a reader, as access denied: treat it as busy.
        if path.parent.is_dir():
            return None
        raise
    try:
        os.write(fd, json.dumps(owner, sort_keys=True).encode("utf-8"))
    finally:
        os.close(fd)
    return owner


def release(path, owner):
    """Remove the lock only when it still carries this owner's token."""
    path = Path(path)
    info = inspect(path)
    if info is not None and (info["owner"] or {}).get("token") == owner["token"]:
        unlink_retry(path)


def unlink_retry(path, attempts=50, delay=0.02):
    """Delete a file, tolerating Windows readers that briefly hold it open."""
    for attempt in range(attempts):
        try:
            Path(path).unlink()
            return True
        except FileNotFoundError:
            return False
        except PermissionError:
            if attempt == attempts - 1:
                raise
            time.sleep(delay)


def stale_message(label, path, reason):
    return (label + " lock is stale (" + reason + "); it was NOT removed. Confirm no process uses " +
            str(path) + ", then delete that one file.")


def acquire(path, purpose, timeout, label="exclusive", poll=0.1, stale_after=3600):
    """Wait up to ``timeout`` seconds; report stale or timed-out locks."""
    deadline = time.monotonic() + timeout
    while True:
        owner = try_acquire(path, purpose)
        if owner is not None:
            return owner
        info = inspect(path)
        reason = stale_reason(info, stale_after)
        if reason:
            raise FormatError(stale_message(label, path, reason))
        if time.monotonic() >= deadline:
            held = "" if info is None else " (state %s, age %s s, owner %s)" % (
                info["state"], info["age_seconds"], json.dumps(info["owner"], sort_keys=True))
            raise FormatError(label + " lock is held: " + str(path) + held)
        time.sleep(poll)


@contextmanager
def locked(path, purpose, timeout, label="exclusive", poll=0.1, stale_after=3600):
    owner = acquire(path, purpose, timeout, label, poll, stale_after)
    try:
        yield owner
    finally:
        release(path, owner)
