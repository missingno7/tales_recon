import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from common import FormatError
from recovery_state import runtime_dependencies, facts, ranked


class RuntimeGuidanceTests(unittest.TestCase):
    def test_real_helper_guidance_preserves_ambiguity(self):
        package=facts('ov14_F_0412')
        calls=[c for c in package['calls'] if c['offset']==0x7b00]
        self.assertEqual(len(calls),3)
        for call in calls:
            self.assertEqual(call['current_state'],'MATCHED_RUNTIME_CONTRIBUTION')
            self.assertEqual(call['runtime']['symbol'],'.mulu')
            self.assertEqual(set(call['runtime']['profiles']),{'aztec36','aztec50-short'})
            self.assertIn('Do not declare a C function',call['runtime']['source_contract'])
        self.assertEqual(package['abi']['historical_selection'],'AMBIGUOUS')

    def test_wrong_executable_rejected(self):
        with self.assertRaises(FormatError):runtime_dependencies(dict(game_sha256='wrong'))

    def test_hunk_reference_has_exact_mechanical_name(self):
        package=facts('ov11_F_729C')
        self.assertTrue(any(d['name']=='G_h01_13A2' for d in package['data']))
        self.assertEqual(package['relocations'][0]['target_name'],'G_h01_13A2')

    def test_absent_optional_runtime_evidence(self):
        with tempfile.TemporaryDirectory() as temp,patch('recovery_state.ROOT',Path(temp)):
            self.assertEqual(runtime_dependencies(dict(game_sha256='unused')), {})

    def test_ranking_guidance_does_not_promote_runtime(self):
        with patch('recovery_state.runtime_dependencies',return_value={}):
            before=next(x for x in ranked() if x['id']=='ov14_F_0412')
        after=next(x for x in ranked() if x['id']=='ov14_F_0412')
        self.assertEqual(before['score']-after['score'],90)
        self.assertEqual(after['state'],'BLOCKED')


if __name__=='__main__':unittest.main()
