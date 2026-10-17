"""The fixture-locked executable image, without a census derivation.

`analysis_support.game()` derives the complete census (every proof class
re-validated) just to return the executable bytes and HUNK model, and inside a
promotion snapshot it re-hashes the whole input closure around each call.
Almost every caller discards the census outputs, so this returns the image
directly. It defers to `analysis_support.game()` whenever a caller-supplied
dead-code image or a function-census refresh is active.
"""
import pickle

from analysis_support import ROOT
from common import sha256

_IMAGE = {}


def image():
    """(executable bytes, HUNK model) from the fixture-locked disks.

    Cached per process under the content hashes of the disks and of the parser
    sources, so a changed input is never served stale; callers get a copy."""
    from census import inputs, verify_lock, _derive_uncached
    tools = ROOT / 'tools'
    key = tuple(sha256(p.read_bytes()) for p in inputs(ROOT)) + tuple(
        sha256((tools / n).read_bytes()) for n in ('census.py', 'hunk.py', 'ofs.py'))
    if key not in _IMAGE:
        verify_lock(ROOT)
        _, files, model = _derive_uncached(ROOT, promotion_evidence=False)
        _IMAGE.clear()
        _IMAGE[key] = pickle.dumps((files['DT1:DuckTales'], model), protocol=pickle.HIGHEST_PROTOCOL)
    return pickle.loads(_IMAGE[key])


def game():
    """Same contract as `analysis_support.game()`; census outputs are None."""
    from dead_code_extents import current_image, refreshing_analysis
    if current_image() is not None or refreshing_analysis():
        from analysis_support import game as full
        return full()
    blob, model = image()
    return blob, model, None
