import copy
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))

import check_function
import check_unit
from common import write_json
from compiler_oracle import cached,identity
from function_compare import compare_function
from recovery_state import evidence


class IsolatedFunctionVerifierTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source_path=ROOT/'experiments/grinder-bootstrap/ov14_F_03AE.c'
        if not cls.source_path.exists():raise unittest.SkipTest('bootstrap source unavailable')
        cls.source=cls.source_path.read_text()
        key=identity(cls.source,'aztec36')[0]
        cls.compiled=cached(key)
        if cls.compiled is None:raise unittest.SkipTest('bootstrap compiler cache unavailable')
        cls.ledger=evidence()
        cls.function=next(f for f in cls.ledger['functions'] if f['id']=='ov14_F_03AE')

    def run_isolated(self,compiled,output_dir=None):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);ledger=root/'recovery/ledger.json';ranking=root/'evidence/functions/ranking.json'
            initial=dict(schema_version=1,functions={'keep':{'state':'FUNCTION_CODE_MATCH'}},
                         attempts={'keep':[{'verdict':'DIFFER'}]},blockers={})
            write_json(ledger,initial);ranking.parent.mkdir(parents=True,exist_ok=True)
            ranking.write_text('{"untouched": true}\n')
            before=(ledger.read_bytes(),ranking.read_bytes())
            selected_output=root/'experiments/isolated' if output_dir else None
            with patch.object(check_function,'ROOT',root),patch.object(check_function,'LEDGER',ledger), \
                 patch.object(check_function,'recovery',lambda:json.loads(ledger.read_text())), \
                 patch.object(check_function,'validated_function',return_value=(self.function,self.ledger)), \
                 patch.object(check_function,'compile_many',return_value=[copy.deepcopy(compiled)]), \
                 patch.object(check_function,'save_rank') as save_rank:
                reports=check_function.check_many(
                    [dict(id=self.function['id'],source=str(self.source_path),profiles=['aztec36'])],
                    isolated=True,output_dir=selected_output)
                save_rank.assert_not_called()
            self.assertEqual((ledger.read_bytes(),ranking.read_bytes()),before)
            for name in ('candidates','attempts','proofs','units'):
                self.assertFalse((root/'recovery'/name).exists(),name+' was written')
            self.assertFalse((root/'src/recovered').exists())
            if selected_output is not None:
                report=reports[0];stem=report['source_sha256']+'-aztec36-'+report['cache_key'][:12]
                trial_dir=selected_output/'ov14_F_03AE'
                self.assertEqual((trial_dir/(stem+'.c')).read_text(),self.source)
                saved=json.loads((trial_dir/(stem+'.json')).read_text())
                self.assertEqual(saved['verdict'],report['verdict'])
            return reports[0]

    def test_isolated_equal_verdict_writes_only_selected_experiment_output(self):
        report=self.run_isolated(self.compiled,True)
        self.assertEqual(report['verdict'],'EQUAL')
        self.assertEqual(report['proof_level'],'FUNCTION_CODE_MATCH')

    def test_isolated_mismatch_uses_the_same_exact_comparator(self):
        changed=copy.deepcopy(self.compiled)
        code=changed['contribution']['code_hex']
        changed['contribution']['code_hex']='4e71'+code[4:]
        expected=compare_function(self.function,changed,self.ledger['a4']['bias'])
        actual=self.run_isolated(changed)
        self.assertEqual(actual['verdict'],expected['verdict'])
        self.assertEqual(actual['raw_first_difference'],expected['raw_first_difference'])


class IsolatedUnitReceiptTests(unittest.TestCase):
    def test_isolated_unit_check_saves_only_to_selected_output_and_skips_promotion(self):
        f=dict(id='ov03_F_0000',hunk=3,start=0,end=4,size=4,sha256='0'*64,node='ov03')
        source='recovered() { return 0; }\n'
        compiled=dict(identity={'profile':'aztec36'},cache_key='b'*64,cache_hit=False)
        ledger={'a4':{'bias':0}}
        unit_report=dict(verdict='EQUAL',reason='EXACT',members=[])
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);source_path=root/'candidate.c';source_path.write_text(source)
            output=root/'experiments/isolated'
            prepared=([f],{f['id']:'recovered'},{f['id']:source},source,ledger)
            with patch.object(check_unit,'ROOT',root),patch.object(check_function,'ROOT',root), \
                 patch.object(check_unit,'prepare_unit',return_value=prepared), \
                 patch.object(check_unit,'validated_function',return_value=(f,ledger)), \
                 patch.object(check_unit,'compile_many',return_value=[compiled]), \
                 patch.object(check_unit,'retain_unit',return_value=(unit_report,dict(verdict='EQUAL'))) as retain, \
                 patch.object(check_unit,'promote') as promote,patch.object(check_unit,'save_rank') as save_rank:
                reports=check_unit.check(f['id'],source_path,['aztec36'],isolated=True,output_dir=output)
            self.assertEqual(reports[0]['verdict'],'EQUAL')
            retain.assert_called_once()
            self.assertTrue(retain.call_args.args[-1])
            promote.assert_not_called();save_rank.assert_not_called()
            output_report=next(output.glob(f['id']+'/*/receipt.json'))
            self.assertEqual(json.loads(output_report.read_text())['verdict'],'EQUAL')
            self.assertFalse((root/'recovery/units').exists())

    def test_isolated_unit_retention_does_not_write_recovery_units(self):
        f=dict(id='ov03_F_0000',hunk=3,start=0,end=4,size=4,sha256='0'*64)
        compiled=dict(identity={'profile':'aztec36'},cache_key='a'*64,cache_hit=False)
        source='recovered() { return 0; }\n'
        report=dict(verdict='EQUAL',reason='EXACT',members=[])
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            tools=root/'tools';tools.mkdir()
            for name in ('check_unit.py','function_compare.py','compiler_oracle.py','runtime_arithmetic.py'):
                shutil.copy2(ROOT/'tools'/name,tools/name)
            with patch.object(check_unit,'ROOT',root),patch.object(check_unit,'recovery',return_value={'functions':{}}), \
                 patch.object(check_unit,'compare_unit',return_value=report), \
                 patch.object(check_unit,'compare_function',return_value={'verdict':'EQUAL'}):
                unit,comparison=check_unit.retain_unit(
                    f['id'],source,[f],{f['id']:'recovered'},source,compiled,0,isolated=True)
            self.assertEqual(unit['verdict'],'EQUAL')
            self.assertEqual(comparison['verdict'],'EQUAL')
            self.assertFalse((root/'recovery/units').exists())


if __name__=='__main__':
    unittest.main()
