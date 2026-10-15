"""The planning map must not turn candidate boundaries into owned bytes."""
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from overlay_frontier import partition
from common import FormatError


class OverlayFrontierTests(unittest.TestCase):
    def test_code_literal_and_unclaimed_bytes_tile_hunk(self):
        rows = partition(16, [dict(kind='VERIFIED_CODE', id='f', start=2, end=6),
                              dict(kind='VERIFIED_LITERAL', id='f', start=6, end=9)])
        self.assertEqual([(x['kind'], x['start'], x['end']) for x in rows],
                         [('UNCLAIMED', 0, 2), ('VERIFIED_CODE', 2, 6),
                          ('VERIFIED_LITERAL', 6, 9), ('UNCLAIMED', 9, 16)])
        self.assertEqual(sum(x['size'] for x in rows), 16)

    def test_overlapping_claims_fail_closed(self):
        with self.assertRaises(FormatError):
            partition(16, [dict(kind='VERIFIED_CODE', start=2, end=8),
                           dict(kind='VERIFIED_LITERAL', start=7, end=10)])
