"""Semantic names apply only to the generated view and must be valid, unique and evidenced."""
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))

import readable
from common import FormatError


def names(functions=None, globals_=None):
    return dict(schema_version=1, functions=functions or {}, globals=globals_ or {})


class NameTests(unittest.TestCase):
    def test_rename_maps_entry_callees_and_globals(self):
        n = names({'resident_F_2816': dict(name='arc_read_index', evidence='e'),
                   'ov04_F_0104': dict(name='load_invest', evidence='e')},
                  {'G_h01_46DA': dict(name='arc_file', evidence='e')})
        text = 'extern long F_h00_2816();\nrecovered() { F_h00_2816(G_h01_46DA); F_h04_0104(); F_h00_9999(); }\n'
        out = readable.rename(text, 'ov04_F_0104', n)
        self.assertIn('load_invest() { arc_read_index(arc_file); load_invest(); F_h00_9999(); }', out)

    def test_invalid_names_reject(self):
        bad = [
            names({'resident_F_2816': dict(name='int', evidence='e')}),
            names({'resident_F_2816': dict(name='x', evidence='')}),
            names({'resident_F_2816': dict(name='dup', evidence='e')}, {'G_h01_0001': dict(name='dup', evidence='e')}),
            names({'resident_F_2816': dict(name='F_h00_1234', evidence='e')}),
            names({'resident_F_2816': dict(name='recovered', evidence='e')}),
            names({'bogus': dict(name='ok', evidence='e')}),
        ]
        for n in bad:
            with self.subTest(n=n), self.assertRaises(FormatError):
                readable.validate(n)

    def test_repository_names_are_valid(self):
        readable.load_names(ROOT)


if __name__ == '__main__':
    unittest.main()
