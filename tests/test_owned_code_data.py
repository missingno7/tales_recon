import tempfile
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from owned_code_data import alignment_padding,compare_owned_code_data,expected_string_tail
from function_compare import compare_function
from check_function import owned_code_data_boundary
from recovery_evidence import owned_tail_boundary


class OwnedCodeDataTests(unittest.TestCase):
    def setUp(self):
        # pea 4(pc); rts; "X\\0".  The string follows the closed code extent.
        self.f=dict(id='ov99_F_0064',hunk=99,start=100,end=106,size=6,raw_bytes='487a00044e75',
            extent_status='CLOSED_CFG',referenced_data=[dict(kind='PC_RELATIVE_DATA',hunk=99,instruction_offset=100,offset=106)],
            referenced_strings=[dict(hunk=99,offset=106,text='X')],relocations=[],direct_callees=[])
        self.temp=tempfile.TemporaryDirectory();base=Path(self.temp.name)
        (base/'candidate.c').write_text('int recovered() { return 0; }\n')
        (base/'candidate.exe').write_bytes(b'\0')
        self.compiled=dict(status='COMPILED',identity=dict(profile='aztec36',flags=[]),cache_key='test',cache_hit=True,
            directory=str(base),prefix='candidate',contribution=dict(entry_offset=0,code_hex='487a00044e755800',code_size=8,
            code_offset=0,hunk=3,data_size=0,bss_size=0,relocations=[],all_relocations=[],symbols=[],
            hunks=[dict(number=0,content_offset=0),dict(number=1,initialized_size=0,allocated_size=0),dict(number=2,allocated_size=0)]))

    def tearDown(self):self.temp.cleanup()

    def test_exact_tail_and_pc_target_are_proven(self):
        tail,extent=expected_string_tail(self.f)
        self.assertEqual((tail,extent['start'],extent['end']),(b'X\0',106,108))
        report=compare_owned_code_data(self.f,self.compiled,32766)
        self.assertEqual(report['verdict'],'EQUAL')
        self.assertEqual(report['proof_level'],'FUNCTION_WITH_DATA_MATCH')
        self.assertEqual(len(report['owned_code_data']['pc_relative_proof']),1)

    def test_tail_mismatch_never_promotes(self):
        self.compiled['contribution']['code_hex']='487a00044e755900'
        report=compare_owned_code_data(self.f,self.compiled,32766)
        self.assertEqual(report['verdict'],'BLOCKED')
        self.assertIn('tail differs',report['reason'])

    def test_ordinary_function_gate_still_blocks_pc_relative_data(self):
        report=compare_function(self.f,self.compiled,32766)
        self.assertNotEqual(report['verdict'],'EQUAL')
        self.assertIn('PC_RELATIVE_DATA_OWNERSHIP_UNPROVEN',
                      [x['kind'] for x in report['relocation_issues']])

    def test_noncontiguous_string_evidence_is_rejected(self):
        self.f['referenced_strings'][0]['offset']=107
        with self.assertRaisesRegex(ValueError,'exactly'):
            expected_string_tail(self.f)

    def test_odd_literal_bundle_requires_one_zero_alignment_byte(self):
        self.assertEqual(alignment_padding(b'XY\0'),b'\0')
        self.assertEqual(alignment_padding(b'X\0'),b'')

    def test_terminal_hunk_alignment_bounds_a_final_literal_tail(self):
        """A final hunk tail may leave only serialization alignment zeros."""
        report=dict(owned_code_data=dict(end=106))
        ledger=dict(functions=[self.f])
        model=dict(hunks=[dict(number=99,content_offset=0,initialized_size=108)])
        with patch('check_function.game',return_value=(b'\0'*108,model,None)):
            owned_code_data_boundary(self.f,ledger,report)

    def test_terminal_hunk_alignment_rejects_nonzero_unclaimed_bytes(self):
        report=dict(owned_code_data=dict(end=106))
        ledger=dict(functions=[self.f])
        model=dict(hunks=[dict(number=99,content_offset=0,initialized_size=108)])
        with patch('check_function.game',return_value=(b'\0'*106+b'\0X',model,None)):
            with self.assertRaisesRegex(ValueError,'immutable zero fill'):
                owned_code_data_boundary(self.f,ledger,report)

    def test_independent_promotion_loader_accepts_terminal_alignment(self):
        hunk=dict(number=99,content_offset=0,initialized_size=108)
        analysis=dict(functions=[self.f])
        self.assertTrue(owned_tail_boundary(hunk,self.f['id'],self.f['end'],106,analysis,b'\0'*108))
        self.assertFalse(owned_tail_boundary(hunk,self.f['id'],self.f['end'],106,analysis,b'\0'*106+b'\0X'))
