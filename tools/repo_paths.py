"""One boundary for repository discovery and canonical inputs.

Scratch can be consumed by an explicit compiler request, never by discovery.
Quarantined material cannot be consumed even by an explicit canonical path.
"""
import os
from pathlib import Path
from common import require

IGNORED_PARTS = frozenset(('.git', 'build', 'to_delete', '__pycache__',
                           '.pytest_cache', 'compile-cache', 'worker-jobs'))


def is_active_repo_path(path, root=None):
    path = Path(path)
    if root is not None:
        try:
            path = path.resolve().relative_to(Path(root).resolve())
        except ValueError:
            return False
    return not any(p.lower() in IGNORED_PARTS for p in path.parts)


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
    require(is_active_repo_path(path, root), 'canonical input is outside active repository: '+str(relative))
    return path


def candidate_path(root, path):
    """Explicit scratch is allowed; quarantine and symlink escapes are not."""
    path = Path(path).resolve()
    root = Path(root).resolve()
    require(path.is_relative_to(root), 'candidate input escapes repository')
    require('to_delete' not in [p.lower() for p in path.relative_to(root).parts],
            'quarantined candidate input is forbidden')
    return path
