"""Per-member compiler profiles for separate-object units (opt-in)."""
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
sys.path.insert(0,str(ROOT/'tests'))

import check_unit
import profile_compat
from common import FormatError
from test_natural_interval import fn,linked

NOP='4e71'*3+'4e75'


def toolchain_present():
    from compiler_oracle import PROFILES
    base=ROOT/PROFILES['aztec36']['base']
    return all((base/'bin'/n).is_file() for n in ('cc','as','ln')) and (base/'lib/c.lib').is_file()


class LinkCompatibilityTests(unittest.TestCase):
    def test_policy_flags_match_the_oracle_profiles(self):
        from compiler_oracle import PROFILES
        for name,flags in profile_compat.PROFILE_FLAGS.items():
            self.assertEqual(PROFILES[name]['flags'],flags)
            self.assertEqual((PROFILES[name]['version'],PROFILES[name]['base']),('3.6a','toolchain/installed/aztec-3.6a/SYS1'))

    def test_only_established_classes_mix(self):
        self.assertEqual(profile_compat.link_class(['aztec36','aztec36-large-data']),'aztec-3.6a-c.lib')
        self.assertEqual(profile_compat.link_class(['aztec36']),'aztec-3.6a-c.lib')
        for other in ('aztec50-short','aztec50','aztec36-long','aztec36-x3'):
            with self.subTest(other=other),self.assertRaisesRegex(FormatError,'PROFILES_NOT_LINK_COMPATIBLE'):
                profile_compat.link_class(['aztec36',other])

    def test_proof_profile_prefers_the_recorded_member_profile(self):
        proof=dict(compiler=dict(profile='aztec36',flags=[],member_profiles={'x':'aztec36-large-data'}))
        self.assertEqual(profile_compat.proof_profile(proof,'x'),'aztec36-large-data')
        self.assertEqual(profile_compat.proof_profile(proof,'y'),'aztec36')
        with self.assertRaisesRegex(FormatError,'flags disagree'):
            profile_compat.proof_profile(dict(compiler=dict(profile='aztec36-large-data',flags=[])),'z')


class ObjectProfileTests(unittest.TestCase):
    def plan(self,**profiles):
        return {k:dict(profile=v,basis='REQUESTED_PROFILE') for k,v in profiles.items()}

    def test_uniform_profiles_keep_the_ordinary_trial(self):
        trial=dict(source='s',profile='aztec36',objects=[dict(source='a',members=['a']),dict(source='b',members=['b'])])
        before=json.dumps(trial,sort_keys=True)
        record=check_unit.apply_member_profiles(trial,self.plan(a='aztec36',b='aztec36'),'aztec-3.6a-c.lib')
        self.assertEqual(json.dumps(trial,sort_keys=True),before)
        self.assertFalse(record['mixed_object_profiles'])
        self.assertEqual(record['object_profile_partition'],[['a'],['b']])

    def test_mixed_objects_gain_object_profiles(self):
        trial=dict(source='s',profile='aztec36',objects=[dict(source='a',members=['a']),dict(source='b',members=['b'])])
        record=check_unit.apply_member_profiles(trial,self.plan(a='aztec36',b='aztec36-large-data'),'aztec-3.6a-c.lib')
        self.assertEqual(trial['object_profiles'],['aztec36','aztec36-large-data'])
        self.assertTrue(record['mixed_object_profiles'])

    def test_one_object_cannot_mix_profiles(self):
        trial=dict(source='s',profile='aztec36',objects=[dict(source='ab',members=['a','b'])])
        with self.assertRaisesRegex(FormatError,'OBJECT_MIXES_MEMBER_PROFILES'):
            check_unit.apply_member_profiles(trial,self.plan(a='aztec36',b='aztec36-large-data'),'aztec-3.6a-c.lib')
        with self.assertRaisesRegex(FormatError,'need separate ordinary objects'):
            check_unit.apply_member_profiles(dict(source='s',profile='aztec36'),self.plan(a='aztec36',b='aztec36-large-data'),
                                             'aztec-3.6a-c.lib',single_object=['a','b'])

    def test_member_objects_do_not_change_ordinary_partitions(self):
        a=fn(0x100,NOP);b=fn(0x108,NOP)
        names={a['id']:'recovered',b['id']:'F_h09_0108'};parts={a['id']:'recovered() {}',b['id']:'F_h09_0108() {}'}
        plain=check_unit.grouped_objects([a,b],names,parts,False,[])
        tagged=check_unit.grouped_objects([a,b],names,parts,False,[],with_members=True)
        self.assertEqual(plain,[dict(source=parts[a['id']]),dict(source=parts[b['id']])])
        self.assertEqual([o['source'] for o in tagged],[o['source'] for o in plain])
        self.assertEqual([o['members'] for o in tagged],[[a['id']],[b['id']]])

    @unittest.skipUnless(toolchain_present(),'pinned toolchain absent')
    def test_mixed_identity_is_a_distinct_cache_family(self):
        from compiler_oracle import identity,object_specs
        import mixed_profile_oracle
        objects=[dict(source='recovered() { return 1; }\n'),dict(source='F_h09_0108() { return 2; }\n')]
        trial=dict(source='recovered() { return 1; }\nF_h09_0108() { return 2; }\n',profile='aztec36',objects=objects,
                   local_functions=['F_h09_0108'])
        plain=identity(trial['source'],'aztec36',1,object_specs(trial),trial['local_functions'])[0]
        mixed=dict(trial,object_profiles=['aztec36','aztec36-large-data'])
        key,meta,_,_=mixed_profile_oracle.mixed_identity(mixed)
        self.assertNotEqual(key,plain)
        self.assertEqual([o['flags'] for o in meta['object_profiles']],[[],['+D']])
        self.assertEqual(check_unit.trial_cache_key(mixed)[0],key)
        self.assertEqual(check_unit.trial_cache_key(trial)[0],plain)
        with self.assertRaisesRegex(FormatError,'PROFILES_NOT_LINK_COMPATIBLE'):
            mixed_profile_oracle.mixed_identity(dict(trial,object_profiles=['aztec36','aztec50-short']))


@unittest.skipUnless(toolchain_present(),'pinned toolchain absent')
class MemberProfilePromotionEvidenceTests(unittest.TestCase):
    """A synthetic mixed-profile unit promoted in a temporary root re-derives its profiles."""

    def test_canonical_member_keeps_its_proven_profile_through_promotion(self):
        import check_function
        import mixed_profile_oracle
        import recovery_state
        from recovery_evidence import member_profile_evidence
        a=fn(0x100,NOP);b=fn(0x108,NOP);c=fn(0x110,NOP)
        for f in (a,b,c):f.update(sha256=check_unit.sha256(bytes.fromhex(f['raw_bytes'])),extent_status='CLOSED_CFG')
        functions={f['id']:f for f in (a,b,c)}
        def validated(fid):
            if fid not in functions:raise FormatError('unknown function '+fid)
            return functions[fid],dict(functions=list(functions.values()),a4=dict(bias=32766))
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            for d in ('recovery/proofs','tools','src/recovered/ov09'):(root/d).mkdir(parents=True)
            for name in ('check_unit.py','check_function.py','function_compare.py','compiler_oracle.py','runtime_arithmetic.py',
                         'profile_compat.py','mixed_profile_oracle.py'):
                shutil.copyfile(ROOT/'tools'/name,root/'tools'/name)
            canonical_source='F_h09_0110() {}\n'.replace('F_h09_0110','recovered')
            (root/'src/recovered/ov09'/(c['id']+'.c')).write_text(canonical_source,newline='\n')
            source_hash=check_unit.sha256(canonical_source.encode())
            proof=dict(schema_version=1,id=c['id'],state='FUNCTION_CODE_MATCH',source='src/recovered/ov09/%s.c'%c['id'],
                       source_sha256=source_hash,compiler=dict(profile='aztec36-large-data',flags=['+D']),comparison={},
                       cache_key='c'*64)
            proof_path=root/'recovery/proofs'/(c['id']+'.json');check_unit.write_json(proof_path,proof)
            extent={k:c[k] for k in ('hunk','start','end','size','sha256','extent_status')}
            ledger=root/'recovery/ledger.json'
            check_unit.write_json(ledger,dict(schema_version=1,attempts={},blockers={},functions={c['id']:dict(
                state='FUNCTION_CODE_MATCH',source=proof['source'],source_sha256=source_hash,evidence_extent=extent,
                compiler_selection='test',proof='recovery/proofs/%s.json'%c['id'],proof_sha256=check_unit.sha256(proof_path.read_bytes()))}))
            paths={a['id']:root/'a.c',b['id']:root/'b.c'}
            paths[a['id']].write_text('extern int F_h09_0110();\nrecovered() { F_h09_0110(); }\n',newline='\n')
            paths[b['id']].write_text('recovered() {}\n',newline='\n')
            compiled_trials=[]
            def compile_mixed(trials):
                (trial,)=trials;compiled_trials.append(trial)
                key,meta,_,_=mixed_profile_oracle.mixed_identity(trial)
                result=linked(root,NOP*3,(('_recovered',0),('_F_h09_0108',8),('_F_h09_0110',16)))
                result.update(identity=meta,cache_key=key,artifacts=[])
                return [result]
            def ordinary(trials):raise AssertionError('a mixed unit must not reach the ordinary oracle')
            with patch.object(check_unit,'ROOT',root),patch.object(check_function,'ROOT',root), \
                 patch.object(check_function,'LEDGER',ledger),patch.object(recovery_state,'LEDGER',ledger), \
                 patch.object(check_unit,'validated_function',side_effect=validated), \
                 patch.object(check_unit,'compile_many',side_effect=ordinary), \
                 patch.object(mixed_profile_oracle,'_compile_mixed',side_effect=compile_mixed), \
                 patch.object(check_function,'regression_receipt',return_value=dict(command='test',passed=True,output_sha256='0'*64)), \
                 patch.object(check_unit,'save_rank'):
                with self.assertRaisesRegex(FormatError,'requires --separate-objects'):
                    check_unit.check(a['id'],paths[a['id']],['aztec36'],per_member_profiles=True,
                                     member_sources={b['id']:paths[b['id']]})
                with self.assertRaisesRegex(FormatError,'PROFILES_NOT_LINK_COMPATIBLE'):
                    check_unit.check(a['id'],paths[a['id']],['aztec50-short'],separate_objects=True,isolated=True,
                                     natural_interval='0x100..0x118',member_sources={b['id']:paths[b['id']]},
                                     per_member_profiles=True)
                report=check_unit.check(a['id'],paths[a['id']],['aztec36'],separate_objects=True,natural_interval='0x100..0x118',
                                        member_sources={b['id']:paths[b['id']]},per_member_profiles=True)[0]
            self.assertEqual(report['verdict'],'EQUAL')
            self.assertEqual(compiled_trials[0]['object_profiles'],['aztec36','aztec36','aztec36-large-data'])
            self.assertEqual(report['member_profiles'],{a['id']:'aztec36',b['id']:'aztec36',c['id']:'aztec36-large-data'})
            self.assertEqual(report['member_profile_basis'][c['id']]['basis'],'CANONICAL_PROOF')
            items=json.loads(ledger.read_text())['functions']
            self.assertEqual(sorted(items),sorted(functions))
            promoted=json.loads((root/items[b['id']]['proof']).read_text())
            self.assertEqual(profile_compat.proof_profile(promoted,b['id']),'aztec36')
            unit_path=root/promoted['comparison']['complete_unit_receipt'];unit=json.loads(unit_path.read_text())
            ledger_data=json.loads(ledger.read_text())
            self.assertEqual(member_profile_evidence(root,ledger_data,unit,promoted['compiler'])[c['id']],'aztec36-large-data')
            # A canonical member whose own proof names another profile no longer re-derives.
            forged=dict(unit,member_profiles=dict(unit['member_profiles'],**{c['id']:'aztec36'}),object_profiles=['aztec36']*3)
            with self.assertRaisesRegex(FormatError,'compiled member profiles differ'):
                member_profile_evidence(root,ledger_data,forged,promoted['compiler'])
            compiler=dict(promoted['compiler'],member_profiles=forged['member_profiles'],
                          object_profiles=[dict(o,profile='aztec36',flags=[]) for o in promoted['compiler']['object_profiles']])
            with self.assertRaisesRegex(FormatError,'differs from its own proof'):
                member_profile_evidence(root,ledger_data,forged,compiler)
            # A new member may not silently take another profile.
            forged=dict(unit,member_profiles=dict(unit['member_profiles'],**{b['id']:'aztec36-large-data'}))
            with self.assertRaisesRegex(FormatError,'mixes member profiles|compiled member profiles differ'):
                member_profile_evidence(root,ledger_data,forged,promoted['compiler'])
            with self.assertRaisesRegex(FormatError,'flags disagree'):
                member_profile_evidence(root,ledger_data,unit,dict(promoted['compiler'],object_profiles=[
                    dict(o,flags=[]) for o in promoted['compiler']['object_profiles']]))


if __name__=='__main__':
    unittest.main()
