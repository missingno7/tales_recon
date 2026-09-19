import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from common import FormatError
from overlay_experiment import relocation_profile, symbols, contribution

class OverlayExperimentTests(unittest.TestCase):
    def model(self,offset=106,target=1,addend=0):
        return {'relocations':[{'source_hunk':0,'source_offset':offset,'width':4,
                                'type':'HUNK_RELOC32','target_hunk':target,'addend_raw':addend}]}

    def test_relocations_normalize_only_source_position(self):
        a=relocation_profile(self.model(),0,100,20)
        self.assertEqual(a,relocation_profile(self.model(offset=206),0,200,20))
        self.assertNotEqual(a,relocation_profile(self.model(target=0),0,100,20))
        self.assertNotEqual(a,relocation_profile(self.model(addend=8),0,100,20))

    def test_partial_relocation_rejected(self):
        with self.assertRaises(FormatError):
            relocation_profile(self.model(offset=98),0,100,20)
        with self.assertRaises(FormatError):
            relocation_profile(self.model(offset=118),0,100,20)

    def test_symbol_map_keeps_hunk_identity(self):
        result=symbols('Segment 00:  Hunk 000\n\t00000070 .segload\nSegment 01: Hunk 003\n\t00000000 _one\n')
        self.assertEqual(result,{(0,'.segload'):112,(3,'_one'):0})
        with self.assertRaises(FormatError):
            symbols('Segment 00: Hunk 000\n\t00000000 duplicate\n\t00000002 duplicate\n')

    def test_contribution_must_be_initialized_code(self):
        model={'hunks':[{'number':0,'type':'CODE','content_offset':2,'initialized_size':4}]}
        self.assertEqual(contribution(b'xxcode',model,0,0,4),b'code')
        with self.assertRaises(FormatError):
            contribution(b'xxcode',model,0,0,6)
