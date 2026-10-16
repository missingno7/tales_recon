"""Keep tests with shared repository state out of the xdist worker pool.

Also puts tools/ on sys.path for every test module, so a module need not
carry its own path header (worker environments set PYTHONPATH and miss it).
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))

SERIAL_MODULES = {
    'test_evidence_snapshot.py',
    'test_terminal_padding.py',
    'test_compile_queue.py',
    'test_resident_recovery.py',
}
SERIAL_CLASSES = {
    ('test_consolidation.py', 'QuarantineTests'),
}


def pytest_configure(config):
    config.addinivalue_line(
        'markers', 'regression_serial: run after the xdist-safe regression tests')


def pytest_collection_modifyitems(items):
    marker = __import__('pytest').mark.regression_serial
    for item in items:
        name = Path(str(item.path)).name
        cls = getattr(item, 'cls', None)
        if name in SERIAL_MODULES or (name, getattr(cls, '__name__', None)) in SERIAL_CLASSES:
            item.add_marker(marker)
