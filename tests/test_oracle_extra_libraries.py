import hashlib
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))

import check_function
from common import FormatError
from compiler_oracle import identity,link_command


class ExtraLibraryIdentityTests(unittest.TestCase):
    source='recovered() { return 7; }\n'

    def test_default_recipe_and_identity_remain_c_lib_only(self):
        key,meta,_=identity(self.source,'aztec36')
        self.assertEqual(meta['link_recipe'],'harness.o +o1 candidate.o +o0 c.lib; -m -t')
        self.assertNotIn('additional_libraries',meta)
        default_again,_,_=identity(self.source,'aztec36',extra_libraries=())
        self.assertEqual(key,default_again,'empty opt-in must preserve the legacy c.lib-only cache identity')
        command=link_command('Old1:','t000','h000',1,['t000'],[],meta)
        self.assertTrue(command.endswith('+o0 Old1:lib/c.lib'))

    def test_pinned_m_lib_is_ordered_and_cache_keyed_by_hash_and_recipe(self):
        default_key,_,_=identity(self.source,'aztec36')
        key,meta,_=identity(self.source,'aztec36',extra_libraries=['m.lib'])
        lib=ROOT/'toolchain/installed/aztec-3.6a/SYS1/lib/m.lib'
        digest=hashlib.sha256(lib.read_bytes()).hexdigest()
        self.assertEqual(meta['link_recipe'],'harness.o +o1 candidate.o +o0 c.lib m.lib; -m -t')
        self.assertEqual(meta['additional_libraries'],[dict(library='m.lib',library_guest='Old1:',library_sha256=digest)])
        self.assertNotEqual(key,default_key)
        command=link_command('Old1:','t000','h000',1,['t000'],[],meta)
        self.assertTrue(command.endswith('+o0 Old1:lib/c.lib Old1:lib/m.lib'))

    def test_m_lib_is_rejected_for_5a_and_unknown_libraries(self):
        with self.assertRaises(FormatError):identity(self.source,'aztec50-short',extra_libraries=['m.lib'])
        with self.assertRaises(FormatError):identity(self.source,'aztec36-long',extra_libraries=['m.lib'])
        with self.assertRaises(FormatError):identity(self.source,'aztec36',extra_libraries=['unknown.lib'])

    def test_cli_flag_selects_aztec36_and_forwards_opt_in_library(self):
        with patch.object(sys,'argv',['check_function.py','ov11_F_5FB2','candidate.c','--with-m-lib','--isolated']), \
             patch.object(check_function,'check_many',return_value=[]) as run:
            status=check_function.main()
        self.assertEqual(status,1)
        requests,promote,isolated,output=run.call_args.args
        self.assertEqual(requests[0]['profiles'],['aztec36'])
        self.assertEqual(requests[0]['extra_libraries'],['m.lib'])
        self.assertTrue(promote);self.assertTrue(isolated);self.assertIsNone(output)


if __name__=='__main__':
    unittest.main()
