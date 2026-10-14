"""Keep tests with shared repository state out of the xdist worker pool."""
from pathlib import Path

SERIAL_MODULES = {
    'test_evidence_snapshot.py',
    'test_terminal_padding.py',
    'test_fleet.py',
    'test_resident_fleet.py',
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
