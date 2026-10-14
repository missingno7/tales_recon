"""One boundary for repository discovery and canonical inputs.

Scratch can be consumed by an explicit compiler request, never by discovery.
Quarantined material cannot be consumed even by an explicit canonical path.
"""
import os
from functools import lru_cache
from pathlib import Path
from common import require

IGNORED_PARTS = frozenset(('.git', 'build', 'to_delete', '__pycache__',
                           '.pytest_cache', 'compile-cache', 'worker-jobs'))


@lru_cache(maxsize=64)
def _resolved_root(absolute):
    # A repository root is resolved once per process; on Windows each
    # resolve() is a costly final-path syscall and roots never move mid-run.
    return Path(absolute).resolve()


def resolved_root(root):
    return _resolved_root(os.path.abspath(root))


def _active_parts(relative):
    return not any(p.lower() in IGNORED_PARTS for p in relative.parts)


def is_active_repo_path(path, root=None):
    path = Path(path)
    if root is not None:
        try:
            path = path.resolve().relative_to(resolved_root(root))
        except ValueError:
            return False
    return _active_parts(path)


def active_files(root, suffix=None):
    """Prune before descending; do not follow directory symlinks."""
    root = Path(root).resolve()
    for base, dirs, files in os.walk(root, followlinks=False):
        dirs[:] = sorted(d for d in dirs if is_active_repo_path(Path(base)/d, root)
                         and not (Path(base)/d).is_symlink())
        for name in sorted(files):
            path = Path(base)/name
            if is_active_repo_path(path, root) and (suffix is None or path.suffix == suffix):
                yield path


def canonical_path(root, relative):
    path = (Path(root)/relative).resolve()
    try:
        active = _active_parts(path.relative_to(resolved_root(root)))
    except ValueError:
        active = False
    require(active, 'canonical input is outside active repository: '+str(relative))
    return path


def candidate_path(root, path):
    """Explicit scratch is allowed; quarantine and symlink escapes are not."""
    path = Path(path).resolve()
    root = resolved_root(root)
    require(path.is_relative_to(root), 'candidate input escapes repository')
    require('to_delete' not in [p.lower() for p in path.relative_to(root).parts],
            'quarantined candidate input is forbidden')
    return path
