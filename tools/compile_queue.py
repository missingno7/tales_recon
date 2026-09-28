"""Coalescing, waiting front end for the batched historical compiler oracle.

``compiler_oracle.compile_many`` fails immediately when another compile holds
``build/compiler-oracle.lock``.  With several parallel experiment processes
that turns most cache misses into errors.  This module keeps the oracle, its
cache identities and its receipts byte-for-byte unchanged and adds only
process coordination around it:

* Cache hits return at once and never wait for or touch any lock.
* A request with cache misses is spooled under ``build/compile-queue/requests``.
  One process at a time becomes the *leader* (``leader.lock``, owner-annotated),
  sweeps every live spooled request into a single oracle batch, and compiles it
  with one emulator boot.  Other requesters wait until their keys are cached.
* Waiting is bounded (``TALES_COMPILE_WAIT_SECONDS``, default 1800 s).  A lock
  whose owner process is gone is reported, never removed or taken over.

``compiler_oracle.py`` is deliberately not edited: its file hash is part of the
cache identity of cross-overlay proxy and named-entry trials.  ``install()``
routes ``check_function``/``check_unit`` through this queue for the current
process only (used by ``shape_search.py`` and ``fleet.py``).
"""
import json
import os
from pathlib import Path
import time
import uuid

import compiler_oracle
from common import FormatError, require, write_json
import file_lock


ROOT = compiler_oracle.ROOT
QUEUE = ROOT / "build/compile-queue"
INNER_LOCK = ROOT / "build/compiler-oracle.lock"
MAX_BATCH_TRIALS = 48
STALE_AFTER = 3600
_original_compile_many = compiler_oracle.compile_many


def wait_timeout():
    try:
        return float(os.environ.get("TALES_COMPILE_WAIT_SECONDS", "1800"))
    except ValueError:
        return 1800.0


def trial_key(trial):
    """The unchanged oracle identity for one trial (same arguments as compile_many)."""
    objects = compiler_oracle.object_specs(trial)
    key, _, _ = compiler_oracle.identity(
        trial["source"], trial["profile"], trial.get("target_node", 1),
        objects if trial.get("objects") is not None else None, trial.get("local_functions", ()),
        trial.get("entry_function", "recovered"), trial.get("extra_libraries", ()))
    return key


def is_cached(key):
    """Cheap presence test; full validation happens in ``compiler_oracle.cached``."""
    return (compiler_oracle.CACHE / key / "receipt.json").is_file()


def load(key):
    return compiler_oracle.cached(key)


def _portable(trial):
    """JSON form of a trial (tuples become lists; identity is unaffected)."""
    return json.loads(json.dumps(trial))


def _spool_dir():
    return QUEUE / "requests"


def _write_spool(trials, keys):
    directory = _spool_dir()
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / ("%d-%s.json" % (os.getpid(), uuid.uuid4().hex[:12]))
    write_json(path, dict(schema_version=1, pid=os.getpid(), host=file_lock.HOST, created=time.time(),
                          trials=[dict(key=k, trial=_portable(t)) for k, t in zip(keys, trials)]))
    return path


def pending_requests():
    """Live spooled requests (oldest first) and stale ones (reported, not removed)."""
    live, stale = [], []
    directory = _spool_dir()
    if not directory.is_dir():
        return live, stale
    for path in sorted(directory.glob("*.json"), key=lambda p: (p.stat().st_mtime, p.name)):
        try:
            request = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if request.get("host") == file_lock.HOST and not file_lock.pid_alive(request.get("pid")):
            stale.append(str(path))
            continue
        live.append((path, request))
    return live, stale


def _batch(own):
    """Own misses first, then other live spooled misses, deduplicated and capped."""
    chosen, seen = [], set()
    for key, trial in own:
        if key not in seen and not is_cached(key):
            seen.add(key); chosen.append(trial)
    live, _ = pending_requests()
    for _, request in live:
        for item in request.get("trials", []):
            key = item.get("key")
            if len(chosen) >= MAX_BATCH_TRIALS:
                return chosen
            if isinstance(key, str) and key not in seen and not is_cached(key):
                seen.add(key); chosen.append(item["trial"])
    return chosen


def _inner_lock_report():
    info = file_lock.inspect(INNER_LOCK)
    if info is not None and info["state"] != "LIVE" and info["age_seconds"] > STALE_AFTER:
        raise FormatError(file_lock.stale_message(
            "compiler oracle", INNER_LOCK, "unannotated oracle lock is %.0f s old" % info["age_seconds"]))


def compile_many(trials, timeout=None, poll=0.25):
    """Drop-in replacement for ``compiler_oracle.compile_many`` (same results)."""
    trials = list(trials)
    keys = [trial_key(t) for t in trials]
    initially_cached = {k for k in set(keys) if is_cached(k)}
    if len(initially_cached) == len(set(keys)):
        # Fast path: validated cache hits, no lock, no statistics write.
        results = [load(k) for k in keys]
        require(all(r is not None for r in results), "compiler cache entry disappeared")
        return results
    own = [(k, t) for k, t in zip(keys, trials) if k not in initially_cached]
    spool = _write_spool([t for _, t in own], [k for k, _ in own])
    deadline = time.monotonic() + (wait_timeout() if timeout is None else timeout)
    leader = QUEUE / "leader.lock"
    unproductive = 0
    try:
        while any(not is_cached(k) for k, _ in own):
            owner = file_lock.try_acquire(leader, "compile-queue leader")
            if owner is not None:
                try:
                    batch = _batch(own)
                    if batch:
                        try:
                            _original_compile_many(batch)
                        except FormatError as exc:
                            if "compiler worker already active" not in str(exc):
                                raise
                            # A direct (non-queued) oracle caller is compiling.
                            _inner_lock_report()
                        except Exception:
                            # Statistics or other post-cache failures must not
                            # discard compiled receipts this request needs.
                            if any(not is_cached(k) for k, _ in own):
                                raise
                        else:
                            unproductive += any(not is_cached(k) for k, _ in own)
                            require(unproductive < 2, "compiler oracle returned without caching requested trials")
                finally:
                    file_lock.release(leader, owner)
                if not any(not is_cached(k) for k, _ in own):
                    break
            else:
                reason = file_lock.stale_reason(file_lock.inspect(leader), STALE_AFTER)
                if reason:
                    raise FormatError(file_lock.stale_message("compile-queue leader", leader, reason))
            if time.monotonic() >= deadline:
                info = file_lock.inspect(leader)
                raise FormatError("compile queue wait timed out; leader " + json.dumps(info, sort_keys=True) +
                                  "; oracle lock " + json.dumps(file_lock.inspect(INNER_LOCK), sort_keys=True) +
                                  " (raise TALES_COMPILE_WAIT_SECONDS or inspect build/compile-queue)")
            time.sleep(poll)
    finally:
        try:
            file_lock.unlink_retry(spool)
        except OSError:
            pass  # a leftover request of a finished process is skipped as stale
    results = []
    for key in keys:
        item = load(key)
        require(item is not None, "compiled cache entry is missing or invalid: " + key)
        results.append(dict(item, cache_hit=key in initially_cached))
    return results


def install():
    """Route this process's verifiers through the queue (no source edits)."""
    import check_function
    import check_unit
    check_function.compile_many = compile_many
    check_unit.compile_many = compile_many
    return compile_many


def status():
    live, stale = pending_requests()
    return dict(leader=file_lock.inspect(QUEUE / "leader.lock"), oracle_lock=file_lock.inspect(INNER_LOCK),
                pending_requests=len(live), pending_trials=sum(len(r.get("trials", [])) for _, r in live),
                stale_requests=stale)
