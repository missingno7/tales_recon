"""Measured same-node export recipes must survive every strict boundary."""
import copy
import json
from pathlib import Path
import shutil
import struct
import sys
import tempfile
import unittest
from contextlib import ExitStack
from types import SimpleNamespace
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import compiler_oracle as oracle
import check_function
import check_unit
import mixed_profile_oracle as mixed
import queued_oracle as queued
import compile_queue
from analysis_support import game,ROOT
from common import FormatError,sha256,json_bytes
from recovery_evidence import same_overlay_exports,unit_export_evidence


class ExportRecipeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.blob,cls.model,_=game()
        cls.members=[dict(id='ov04_F_1E36',hunk=4,start=0x1e36),
                     dict(id='ov04_F_26F0',hunk=4,start=0x26f0),
                     dict(id='ov04_F_27FE',hunk=4,start=0x27fe)]
        cls.names={m['id']:'recovered' if i==0 else 'F_h04_%04X'%m['start'] for i,m in enumerate(cls.members)}
        cls.roots=same_overlay_exports(cls.members,cls.names,cls.members[0]['id'],cls.blob,cls.model)
        cls.source='extern int F_h04_27FE(); recovered() { return F_h04_27FE(); }\nF_h04_27FE() { return 7; }\n'
        cls.local=('F_h04_26F0','F_h04_27FE')
        cls.objects=[dict(label='candidate',source='extern int F_h04_27FE(); recovered(){return F_h04_27FE();}'),
                     dict(label='part001',source='F_h04_27FE(){return 7;}')]

    def test_roots_derive_only_exported_actual_nonentry_members(self):
        self.assertEqual(self.roots['members'],[dict(id='ov04_F_27FE',hunk=4,start=0x27fe,name='F_h04_27FE')])
        self.assertEqual(self.roots['executable_sha256'],sha256(self.blob))
        self.assertIsNone(same_overlay_exports(self.members[:2],self.names,self.members[0]['id'],self.blob,self.model))

    def test_optional_default_and_runner_identity_propagation(self):
        args=(self.source,'aztec36-large-data',2,self.objects,self.local)
        old=oracle.identity(*args)
        self.assertEqual(old,oracle.identity(*args,same_overlay_exports=None))
        rooted=oracle.identity(*args,same_overlay_exports=self.roots)
        self.assertNotEqual(old[0],rooted[0]);self.assertNotIn('same_overlay_exports',old[1])
        self.assertIn('int (*same_overlay_reference_0)() = F_h04_27FE;',rooted[2])
        self.assertNotIn('F_h04_27FE() { return 0; }',rooted[2])
        trial=dict(source=self.source,profile='aztec36-large-data',target_node=2,
                   objects=self.objects,local_functions=self.local,same_overlay_exports=self.roots)
        self.assertEqual(queued.trial_plan(trial)[:3],rooted)
        self.assertEqual(compile_queue.trial_key(trial),rooted[0])
        self.assertEqual(compile_queue.trial_key({k:v for k,v in trial.items() if k!='same_overlay_exports'}),old[0])
        trial.update(object_profiles=['aztec36','aztec36-large-data'])
        meta=mixed.mixed_identity(trial)
        self.assertEqual(meta[1]['same_overlay_exports'],self.roots)
        self.assertEqual(meta[2],rooted[2])
        self.assertEqual(queued.trial_plan(trial),meta)
        self.assertEqual(compile_queue.trial_key(trial),meta[0])

    def test_strict_inventory_members_and_harness_rederivation(self):
        meta=oracle.identity(self.source,'aztec36-large-data',2,self.objects,self.local,same_overlay_exports=self.roots)[1]
        unit=dict(id=self.members[0]['id'],ordered_members=self.members,same_overlay_exports=self.roots)
        unit_export_evidence(unit,self.source,meta,self.blob,self.model)
        corruptions=[]
        for which in ('inventory_sha256','executable_sha256'):
            bad=copy.deepcopy(self.roots);bad[which]='0'*64;corruptions.append(bad)
        bad=copy.deepcopy(self.roots);bad['members']=[];corruptions.append(bad)
        for member in [dict(id='ov04_F_26F0',hunk=4,start=0x26f0,name='F_h04_26F0'),
                       dict(id='ov04_F_0000',hunk=4,start=0,name='F_h04_0000'),
                       dict(id='ov05_F_27FE',hunk=5,start=0x27fe,name='F_h05_27FE')]:
            bad=copy.deepcopy(self.roots);bad['members']=[member];corruptions.append(bad)
        for recipe in corruptions:
            with self.subTest(recipe=recipe):
                badunit=dict(unit,same_overlay_exports=recipe);badmeta=dict(meta,same_overlay_exports=recipe)
                with self.assertRaisesRegex(FormatError,'do not re-derive'):
                    unit_export_evidence(badunit,self.source,badmeta,self.blob,self.model)
        with self.assertRaisesRegex(FormatError,'harness hash'):
            unit_export_evidence(unit,self.source,dict(meta,harness_sha256='0'*64),self.blob,self.model)
        # Removing both semantic fields must not turn the retained rooted
        # harness into a legacy recipe, even with matching source hashes.
        legacyunit=dict(unit);del legacyunit['same_overlay_exports']
        stripped=dict(meta);del stripped['same_overlay_exports']
        with self.assertRaisesRegex(FormatError,'harness hash'):
            unit_export_evidence(legacyunit,self.source,stripped,self.blob,self.model)
        genuine=oracle.identity(self.source,'aztec36-large-data',2,self.objects,self.local)[1]
        unit_export_evidence(legacyunit,self.source,genuine,self.blob,self.model)

    def test_all_three_runner_build_paths_pass_roots_to_extraction(self):
        trial=dict(source=self.source,profile='aztec36-large-data',target_node=2,
                   objects=self.objects,local_functions=self.local,same_overlay_exports=self.roots)
        plain=oracle.identity(self.source,trial['profile'],2,self.objects,self.local,same_overlay_exports=self.roots)
        mixed_trial=dict(trial,object_profiles=['aztec36','aztec36-large-data'])
        mixed_plan=mixed.mixed_identity(mixed_trial)
        for runner,request,plan in [(oracle,trial,(*plain,self.objects)),
                                    (queued,trial,(*plain,self.objects)),(mixed,mixed_trial,mixed_plan)]:
            with self.subTest(runner=runner.__name__),tempfile.TemporaryDirectory() as tmp,ExitStack() as stack:
                root=Path(tmp);(root/'build').mkdir();cache=root/'build/cache';key,meta,h,objects=plan
                command_count=[]
                def prepare(name,source_dir,commands,*args,**kwargs):
                    job=root/'job';work=job/'sys/work';work.mkdir(parents=True)
                    for p in source_dir.iterdir():shutil.copyfile(p,work/p.name)
                    (job/'result.json').write_text('{}')
                    command_count.append(len(commands))
                    self.assertIn('same_overlay_reference_0',next(p for p in work.glob('h*.c')).read_text())
                    return job
                def cache_read(k):
                    p=cache/k/'receipt.json'
                    return dict(json.loads(p.read_text()),cache_hit=True) if p.exists() else None
                for module in {runner,oracle}:
                    stack.enter_context(patch.object(module,'ROOT',root))
                    stack.enter_context(patch.object(module,'cached',side_effect=cache_read))
                    if hasattr(module,'CACHE'):stack.enter_context(patch.object(module,'CACHE',cache))
                if runner is oracle:stack.enter_context(patch.object(oracle,'identity',return_value=plain))
                elif runner is queued:stack.enter_context(patch.object(queued,'trial_plan',return_value=plan))
                else:
                    stack.enter_context(patch.object(mixed,'mixed_identity',return_value=plan))
                    stack.enter_context(patch.object(mixed,'LOCK',root/'build/compiler-oracle.lock'))
                stack.enter_context(patch.object(runner,'prepare',side_effect=prepare))
                stack.enter_context(patch.object(runner,'collect',side_effect=lambda job:dict(steps=[dict(returncode=0)]*command_count[0])))
                stack.enter_context(patch.object(runner.subprocess,'run',return_value=SimpleNamespace(returncode=0,stdout='',stderr='')))
                extraction=stack.enter_context(patch.object(runner,'extract',return_value={'overlay_trampolines':['parsed']}))
                result=runner.compile_many([request])[0]
                self.assertEqual(extraction.call_args.args[-1],self.roots)
                self.assertEqual(result['identity']['same_overlay_exports'],self.roots)
                self.assertEqual(result['contribution'],{'overlay_trampolines':['parsed']})


class UnitTrampolineMappingTests(unittest.TestCase):
    def specimen(self,root):
        # A4 call to other member, PC helper call, then a PC cycle to entry.
        first=dict(id='ov09_F_0064',hunk=9,start=100,end=110,size=10,raw_bytes='4eac80124eba00044e75',
                   extent_status='CLOSED_CFG',referenced_data=[],relocations=[],
                   direct_callees=[dict(id='ov09_F_006E',hunk=9,offset=110,site=100),
                                   dict(id='ov09_F_006E',hunk=9,offset=110,site=104)])
        second=dict(id='ov09_F_006E',hunk=9,start=110,end=116,size=6,raw_bytes='4ebafff44e75',
                    extent_status='CLOSED_CFG',referenced_data=[],relocations=[],
                    direct_callees=[dict(id='ov09_F_0064',hunk=9,offset=100,site=110)])
        (root/'candidate.exe').write_bytes(bytes.fromhex('49f900007ffe4e75'))
        c=dict(status='COMPILED',identity=dict(profile='aztec36',flags=[]),cache_key='map',cache_hit=True,
            directory=str(root),prefix='candidate',contribution=dict(code_hex=first['raw_bytes']+second['raw_bytes'],
            code_size=16,hunk=3,data_size=0,bss_size=0,relocations=[],object_sha256='test',
            all_relocations=[dict(source_hunk=0,source_offset=2,target_hunk=1,addend_raw=32766)],
            symbols=[dict(hunk=3,name='_recovered',offset=0),dict(hunk=3,name='_F_h09_006E',offset=10)],
            overlay_trampolines=[dict(target_hunk=3,target_offset=10,trampoline_hunk=1,trampoline_offset=16),
                                 dict(target_hunk=5,target_offset=12,trampoline_hunk=1,trampoline_offset=24)],
            hunks=[dict(number=0,content_offset=0),dict(number=1,initialized_size=0,allocated_size=0),dict(number=2,allocated_size=0)]))
        return [first,second],{first['id']:'recovered',second['id']:'F_h09_006E'},c

    def test_both_coordinate_modes_preserve_export_helper_cycle_and_other_hunks(self):
        with tempfile.TemporaryDirectory() as tmp:
            members,names,c=self.specimen(Path(tmp))
            for compact in (False,True):
                result=check_unit.compare_unit(members,names,c,32766,allow_gaps=compact,source_text='recovered(){}')
                self.assertEqual(result['verdict'],'EQUAL')
                self.assertEqual(c['contribution']['overlay_trampolines'][1]['target_hunk'],5)
                self.assertEqual(c['contribution']['overlay_trampolines'][1]['target_offset'],12)
                self.assertEqual(result['members'][0]['relocation_proof'][0]['identity']['offset'],110)
                for key,value in [('target_offset',11),('target_offset',0),('target_hunk',5)]:
                    bad=copy.deepcopy(c);bad['contribution']['overlay_trampolines'][0][key]=value
                    self.assertEqual(check_unit.compare_unit(members,names,bad,32766,allow_gaps=compact,
                                     source_text='recovered(){}')['verdict'],'DIFFER')


class RootedExtractionTests(unittest.TestCase):
    def test_extract_and_cached_reextract_keep_only_explicit_new_table_semantics(self):
        # Actual HUNK parser/object-boundary extraction, with a bounded parsed
        # table stand-in. Live diagnostics separately exercise real Manx parsing.
        words=[1011,0,1,3,3,1,1001,1,0x4e754e75,1010]
        blob=struct.pack('>'+str(len(words))+'I',*words)
        with tempfile.TemporaryDirectory() as tmp:
            cache=Path(tmp);meta=dict(profile='aztec36',flags=[],same_overlay_exports={'members':[]})
            key=sha256(json_bytes(meta));dest=cache/key;dest.mkdir()
            (dest/'candidate.exe').write_bytes(blob)
            obj=bytearray(22);obj[:2]=b'AJ';obj[10:14]=(4).to_bytes(4,'big');(dest/'candidate.o').write_bytes(obj)
            (dest/'candidate.sym').write_text('Segment 0: Hunk 3\n  00000000 _recovered\n')
            table=dict(slots=[dict(symbols=[dict(target_hunk=3,target_offset=0,trampoline_hunk=1,trampoline_offset=8)])])
            # Mark the otherwise real parsed model as an overlay load file.
            original_parse=oracle.parse
            def parsed(raw):
                m=original_parse(raw);m['overlay']={};m['hunks'][0]['node']='ov03';return m
            with patch.object(oracle,'parse',side_effect=parsed),patch.object(oracle,'manx_overlay',return_value=table):
                legacy=oracle.extract(dest,'candidate')
                self.assertNotIn('overlay_trampolines',legacy)
                rooted=oracle.extract(dest,'candidate',same_overlay_exports=meta['same_overlay_exports'])
                self.assertEqual(rooted['overlay_trampolines'],table['slots'][0]['symbols'])
                receipt=dict(cache_key=key,identity=meta,prefix='candidate',status='COMPILED',contribution=rooted,
                    artifacts=[dict(path=p.name,sha256=sha256(p.read_bytes())) for p in dest.iterdir()])
                (dest/'receipt.json').write_text(json.dumps(receipt))
                with patch.object(oracle,'CACHE',cache):
                    self.assertEqual(oracle.cached(key)['contribution'],rooted)
                    receipt['contribution']=legacy;(dest/'receipt.json').write_text(json.dumps(receipt))
                    with self.assertRaisesRegex(FormatError,'contribution metadata changed'):oracle.cached(key)


if __name__=='__main__':unittest.main()
