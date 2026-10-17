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
    config.addinivalue_line(
        'markers', 'vamos_equivalence: slow opt-in pinned-vamos equivalence corpus')


def pytest_collection_modifyitems(config, items):
    pytest = __import__('pytest')
    marker = pytest.mark.regression_serial
    run_vamos = 'vamos_equivalence' in (config.option.markexpr or '')
    skip_vamos = pytest.mark.skip(
        reason='select with -m vamos_equivalence to run the slow pinned-vamos corpus')
    for item in items:
        name = Path(str(item.path)).name
        cls = getattr(item, 'cls', None)
        if name in SERIAL_MODULES or (name, getattr(cls, '__name__', None)) in SERIAL_CLASSES:
            item.add_marker(marker)
        if item.get_closest_marker('vamos_equivalence') and not run_vamos:
            item.add_marker(skip_vamos)
