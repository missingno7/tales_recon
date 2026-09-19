import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from runtime_match import find_matches

class RuntimeMatchTests(unittest.TestCase):
    def model(self, relocs=None, kind='CODE'):
        return {'hunks':[{'number':0,'type':kind,'content_offset':0,'initialized_size':8}],
                'relocations':relocs or []}

    def test_aligned_complete_match(self):
        self.assertEqual(find_matches(b'xxabcdef',self.model(),b'abcdef'),
                         [{'hunk':0,'offset':2,'size':6}])

    def test_relocation_overlapping_start_rejects_match(self):
        relocs=[{'source_hunk':0,'source_offset':0}]
        self.assertEqual(find_matches(b'xxabcdef',self.model(relocs),b'abcdef'),[])

    def test_odd_offset_and_data_not_code(self):
        self.assertEqual(find_matches(b'xabcdefx',self.model(),b'abcdef'),[])
        self.assertEqual(find_matches(b'xxabcdef',self.model(kind='DATA'),b'abcdef'),[])

    def test_partial_match_rejected(self):
        self.assertEqual(find_matches(b'xxabcdex',self.model(),b'abcdef'),[])
