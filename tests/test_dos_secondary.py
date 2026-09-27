"""DOS media is a separate, strictly parsed secondary oracle."""
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'tools'))
from dos_structure import analyze, decompress_reverse, overlay_chain


class DosSecondaryTests(unittest.TestCase):
    def test_reverse_exepack_fill_and_copy(self):
        self.assertEqual(decompress_reverse(b'Z\x04\x00\xb1', 4)[0], b'ZZZZ')
        self.assertEqual(decompress_reverse(b'abc\x03\x00\xb3', 3)[0], b'abc')

    def test_supplied_exe_is_complete_and_independently_recorded(self):
        raw = (ROOT/'assets/dos/DUCKTALE.EXE').read_bytes()
        _, actual = analyze(raw)
        measured = json.loads((ROOT/'evidence/dos/structure.json').read_text())
        self.assertEqual(actual, measured)
        self.assertEqual(len(actual['overlays']), 10)
        self.assertEqual(actual['root_exepack']['relocation_count'], 659)
        self.assertEqual(actual['unparsed_file_bytes'], 0)

    def test_nonzero_overlay_alignment_is_rejected(self):
        raw = bytearray((ROOT/'assets/dos/DUCKTALE.EXE').read_bytes())
        root, _ = overlay_chain(raw)
        raw[root['file_end']] = 1
        with self.assertRaisesRegex(ValueError, 'alignment'):
            overlay_chain(raw)
