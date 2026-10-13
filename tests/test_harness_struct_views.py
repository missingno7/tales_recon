"""Harness storage keeps each global's own struct view across separate objects."""
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))

from recovery_evidence import aztec_struct_size,compiled_unit_source_sha256,struct_view_source
from common import FormatError,sha256

SMALL='struct Record { int a; int b; int c; int d; int e; int f; int g; };\nextern struct Record G_h01_8A66[1];\n'
LARGE=('struct Record { char pad0[12]; int value12; int value14; char pad2[6]; int value22; char pad1[2];\n'
       '    int value26; int state; int value30; };\nextern struct Record G_h01_A15E[1];\n')


class StructSizeTests(unittest.TestCase):
    def test_aztec_layout(self):
        bodies={'A':'char c; int i;','B':'char c[3];','C':'struct A a; char *p; long l, m[2];','D':'int (*f)();'}
        self.assertEqual(aztec_struct_size('A',bodies),4)
        self.assertEqual(aztec_struct_size('B',bodies),4)
        self.assertEqual(aztec_struct_size('C',bodies),20)
        self.assertIsNone(aztec_struct_size('D',bodies))


class StructViewSourceTests(unittest.TestCase):
    def test_undersized_first_body_renames_the_later_view(self):
        text=SMALL+LARGE
        viewed=struct_view_source(text)
        self.assertIn('struct Record__v2 { char pad0[12];',viewed)
        self.assertIn('extern struct Record__v2 G_h01_A15E[1];',viewed)
        self.assertIn('extern struct Record G_h01_8A66[1];',viewed)

    def test_no_undersized_storage_keeps_the_text(self):
        for text in (SMALL,LARGE+SMALL,SMALL+SMALL,
                     SMALL+LARGE.replace('extern struct Record G_h01_A15E[1];','extern struct Record *G_h01_A15E;')):
            self.assertEqual(struct_view_source(text),text)

    def test_global_first_declared_through_the_first_body_keeps_it(self):
        text=SMALL+'extern struct Record G_h01_A15E[1];\n'+LARGE
        self.assertEqual(struct_view_source(text),text)

    def test_receipt_flag_rederives_only_when_recorded(self):
        text=SMALL+LARGE
        self.assertEqual(compiled_unit_source_sha256({},text,{}),sha256(text.encode('ascii')))
        self.assertEqual(compiled_unit_source_sha256(dict(harness_struct_views=True),text,{}),
                         sha256(struct_view_source(text).encode('ascii')))
        with self.assertRaises(FormatError):
            compiled_unit_source_sha256(dict(harness_struct_views=True),SMALL,{})
        with self.assertRaises(FormatError):
            compiled_unit_source_sha256(dict(harness_struct_views='yes'),text,{})


if __name__=='__main__':
    unittest.main()
