"""Named DATA interfaces bind authored JMP payloads, original evidence and source."""
import copy
import json
import struct
import tempfile
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import resident_interfaces as interfaces
import compiler_oracle as oracle
import compile_queue
import queued_oracle
import mixed_profile_oracle
from analysis_support import game
from common import FormatError,sha256,json_bytes
from recovery_state import evidence
from recovery_evidence import unit_export_evidence


class ResidentInterfaceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.blob,cls.model,_=game()
        cls.function=next(f for f in evidence()['functions'] if f['id']=='resident_F_77A4')
        cls.source='extern int F_h00_7AF0();\nextern int F_h00_8044();\nrecovered(){return F_h00_7AF0()+F_h00_8044();}\n'
        cls.recipe=interfaces.derive([cls.function],cls.source,cls.blob,cls.model,32766)

    def test_original_decoded_calls_payloads_and_unique_relocations(self):
        self.assertEqual([(m['start'],m['data_offset']) for m in self.recipe['members']],[(0x7af0,0xf0),(0x8044,0x108)])
        self.assertEqual([m['sites'][0]['offset']-self.function['start'] for m in self.recipe['members']],[116,394])
        self.assertEqual(interfaces.original_a4_bias(self.blob,self.model),32766)
        self.assertIsNone(interfaces.derive([self.function],'recovered(){}',self.blob,self.model,32766))
        for mutation in ('opcode','missing','duplicate','target'):
            blob=bytearray(self.blob);model=copy.deepcopy(self.model)
            data=next(h for h in model['hunks'] if h['number']==1)
            rr=next(r for r in model['relocations'] if r['source_hunk']==1 and r['source_offset']==0xf2)
            if mutation=='opcode':blob[data['content_offset']+0xf0]=0
            elif mutation=='missing':model['relocations'].remove(rr)
            elif mutation=='duplicate':model['relocations'].append(copy.deepcopy(rr))
            else:rr['target_hunk']=1
            with self.subTest(mutation=mutation),self.assertRaises(FormatError):
                interfaces.derive([self.function],self.source,bytes(blob),model,32766)

    def test_no_qualifying_declaration_and_proved_embedded_table_compatibility(self):
        self.assertIsNone(interfaces.derive([dict(hunk=0)],'extern int other(); recovered(){}',b'',{},0))
        raw=bytes.fromhex('4eac0000ffffffff4e75');blob=raw+bytes.fromhex('4ef900000000')
        f=dict(id='resident_F_0000',hunk=0,start=0,end=10,sha256=sha256(raw),
               direct_callees=[dict(site=0,hunk=0,offset=0)],jump_tables=[dict(table_start=4,table_end=8)])
        model=dict(hunks=[dict(number=0,content_offset=0,initialized_size=10),dict(number=1,content_offset=10,initialized_size=6)],
                   relocations=[dict(source_hunk=1,source_offset=2,target_hunk=0,type='HUNK_RELOC32',width=4,addend_raw=0)])
        source='extern int F_h00_0000(); recovered(){return F_h00_0000();}'
        result=interfaces.derive([f],source,blob,model,0)
        self.assertEqual(result['members'][0]['start'],0)
        bad=dict(f);del bad['jump_tables']
        with self.assertRaises(FormatError):interfaces.derive([bad],source,blob,model,0)

    def test_harness_and_all_runner_identities_preserve_optional_legacy_behavior(self):
        legacy=oracle.identity(self.source,'aztec36-x3',0)
        self.assertEqual(legacy,oracle.identity(self.source,'aztec36-x3',0,resident_data_interfaces=None))
        rooted=oracle.identity(self.source,'aztec36-x3',0,resident_data_interfaces=self.recipe)
        self.assertNotEqual(legacy[0],rooted[0])
        self.assertIn('F_h00_7AF0 = { 0x4ef9, resident_body_F_h00_7AF0 };',rooted[2])
        self.assertNotIn('int F_h00_7AF0() { return 0; }',rooted[2])
        trial=dict(source=self.source,profile='aztec36-x3',target_node=0,resident_data_interfaces=self.recipe)
        self.assertEqual(queued_oracle.trial_plan(trial)[:3],rooted)
        self.assertEqual(compile_queue.trial_key(trial),rooted[0])
        trial.update(profile='aztec36',objects=[dict(source=self.source)],object_profiles=['aztec36-large-data'])
        mixed=mixed_profile_oracle.mixed_identity(trial)
        self.assertEqual(mixed[1][interfaces.FIELD],self.recipe)
        self.assertEqual(mixed[2],rooted[2]);self.assertEqual(compile_queue.trial_key(trial),mixed[0])
        for recipe in ({},dict(self.recipe,members=[]),dict(self.recipe,source_sha256='0'*64)):
            with self.assertRaises(FormatError):oracle.identity(self.source,'aztec36-x3',0,resident_data_interfaces=recipe)
        with self.assertRaises(FormatError):oracle.identity(self.source,'aztec36-x3',1,resident_data_interfaces=self.recipe)

    def test_strict_original_source_recipe_and_harness_rederivation(self):
        compiler=oracle.identity(self.source,'aztec36-x3',0,resident_data_interfaces=self.recipe)[1]
        interfaces.evidence([self.function],self.source,compiler,self.blob,self.model,32766)
        unit=dict(id=self.function['id'],ordered_members=[self.function],resident_data_interfaces=self.recipe)
        unit_export_evidence(unit,self.source,compiler,self.blob,self.model)
        for field in ('executable_sha256','source_sha256'):
            bad=copy.deepcopy(self.recipe);bad[field]='0'*64
            with self.assertRaisesRegex(FormatError,'do not re-derive'):
                interfaces.evidence([self.function],self.source,dict(compiler,resident_data_interfaces=bad),self.blob,self.model,32766)
        for field,value in [('start',0x7af2),('data_offset',0xf2),('body','resident_body_F_h00_8044'),('payload_sha256','0'*64)]:
            bad=copy.deepcopy(self.recipe);bad['members'][0][field]=value
            with self.subTest(field=field),self.assertRaisesRegex(FormatError,'do not re-derive'):
                interfaces.evidence([self.function],self.source,dict(compiler,resident_data_interfaces=bad),self.blob,self.model,32766)
        for field in ('harness_sha256','resident_interface_producer_sha256'):
            with self.assertRaises(FormatError):
                interfaces.evidence([self.function],self.source,dict(compiler,**{field:'0'*64}),self.blob,self.model,32766)
        for removed in ([interfaces.FIELD],[interfaces.FIELD,'resident_interface_producer_sha256','resident_interface_extractor_sha256']):
            bad={k:v for k,v in compiler.items() if k not in removed}
            with self.assertRaises(FormatError):interfaces.evidence([self.function],self.source,bad,self.blob,self.model,32766)
        badunit=dict(unit);del badunit[interfaces.FIELD]
        with self.assertRaises(FormatError):unit_export_evidence(badunit,self.source,compiler,self.blob,self.model)
        stripped=dict(compiler);del stripped[interfaces.FIELD]
        with self.assertRaisesRegex(FormatError,'harness hash'):unit_export_evidence(badunit,self.source,stripped,self.blob,self.model)
        genuine=oracle.identity(self.source,'aztec36-x3',0)[1]
        unit_export_evidence(badunit,self.source,genuine,self.blob,self.model)

    def specimen(self):
        blob=b'\x4e\x75'*4+b'\x4e\xf9'+(0).to_bytes(4,'big')+b'\x4e\xf9'+(4).to_bytes(4,'big')
        model=dict(hunks=[dict(number=0,content_offset=0,initialized_size=8),dict(number=1,content_offset=8,initialized_size=12)],
                   relocations=[dict(source_hunk=1,source_offset=2,target_hunk=0,type='HUNK_RELOC32',width=4,addend_raw=0),
                                dict(source_hunk=1,source_offset=8,target_hunk=0,type='HUNK_RELOC32',width=4,addend_raw=4)])
        symbols={(1,'_F_h00_7AF0'):0,(1,'_F_h00_8044'):6,
                 (0,'_resident_body_F_h00_7AF0'):0,(0,'_resident_body_F_h00_8044'):4}
        return blob,model,symbols

    def test_actual_data_payload_unique_relocation_and_exact_body_mapping(self):
        blob,model,symbols=self.specimen()
        extracted=interfaces.extract(self.recipe,blob,model,symbols)
        self.assertEqual([e['target_offset'] for e in extracted],[0,4])
        for mutation in ('wrong_opcode','zero_payload','missing','duplicate','wrong_hunk','wrong_body','code_callable','no_body','truncated'):
            raw=bytearray(blob);m=copy.deepcopy(model);s=dict(symbols)
            if mutation=='wrong_opcode':raw[8]=0
            elif mutation=='zero_payload':raw[8:14]=b'\0'*6
            elif mutation=='missing':m['relocations'].pop(0)
            elif mutation=='duplicate':m['relocations'].append(copy.deepcopy(m['relocations'][0]))
            elif mutation=='wrong_hunk':m['relocations'][0]['target_hunk']=1
            elif mutation=='wrong_body':raw[10:14]=(4).to_bytes(4,'big');m['relocations'][0]['addend_raw']=4
            elif mutation=='code_callable':del s[(1,'_F_h00_7AF0')];s[(0,'_F_h00_7AF0')]=0
            elif mutation=='no_body':del s[(0,'_resident_body_F_h00_7AF0')]
            else:m['hunks'][1]['initialized_size']=11
            with self.subTest(mutation=mutation),self.assertRaises(FormatError):interfaces.extract(self.recipe,bytes(raw),m,s)

    def test_cache_reextract_rejects_consistently_rehashed_payload_and_missing_recipe(self):
        # Real serialized root CODE/DATA/BSS, real HUNK_RELOC32 records, and
        # object-bounded extraction. Only unrelated AJ label-bound parsing is
        # stubbed here; retained resident-object fixtures exercise it separately.
        words=[1011,0,3,0,2,3,3,1,1001,3,0x4e754e75,0x4e754e75,0x4e754e75,1010,
               1002,3,0x4ef90000,0x00004ef9,4,1004,1,0,2,1,0,8,0,1010,1003,1,1010]
        executable=struct.pack('>'+str(len(words))+'I',*words)
        metadata=oracle.identity(self.source,'aztec36-x3',0,resident_data_interfaces=self.recipe)[1]
        key=sha256(json_bytes(metadata))
        with tempfile.TemporaryDirectory() as tmp:
            cache=Path(tmp);directory=cache/key;directory.mkdir()
            (directory/'candidate.exe').write_bytes(executable)
            obj=bytearray(22);obj[:2]=b'AJ';obj[10:14]=(4).to_bytes(4,'big');(directory/'candidate.o').write_bytes(obj)
            (directory/'candidate.c').write_text(self.source)
            (directory/'candidate.sym').write_text('Segment 0: Hunk 0\n  00000008 _recovered\n  00000000 _resident_body_F_h00_7AF0\n  00000004 _resident_body_F_h00_8044\nSegment 1: Hunk 1\n  00000000 _F_h00_7AF0\n  00000006 _F_h00_8044\n')
            def artifacts():return [dict(path=p.name,sha256=sha256(p.read_bytes())) for p in directory.iterdir() if p.name!='receipt.json']
            with patch('resident_object.bounds',return_value=(8,0,dict(end=12))),patch.object(oracle,'CACHE',cache):
                contribution=oracle.extract(directory,'candidate',resident=True,resident_data_interfaces=self.recipe)
                receipt=dict(cache_key=key,identity=metadata,status='COMPILED',prefix='candidate',contribution=contribution,artifacts=artifacts())
                (directory/'receipt.json').write_text(json.dumps(receipt))
                self.assertEqual(oracle.cached(key)['contribution'],contribution)
                # Rehashing the artifact and cache's DATA metadata cannot hide
                # a changed JMP opcode; extraction checks the actual payload.
                model=oracle.parse(executable);data=next(h for h in model['hunks'] if h['number']==1)
                bad=bytearray(executable);bad[data['content_offset']]=0
                (directory/'candidate.exe').write_bytes(bad);receipt['artifacts']=artifacts()
                (directory/'receipt.json').write_text(json.dumps(receipt))
                with self.assertRaisesRegex(FormatError,'complete JMP'):oracle.cached(key)
                (directory/'candidate.exe').write_bytes(executable)
                with self.assertRaisesRegex(FormatError,'require their recipe'):oracle.extract(directory,'candidate',resident=True)
                stale=dict(metadata,resident_interface_producer_sha256='0'*64)
                stale_key=sha256(json_bytes(stale));newdir=cache/stale_key;directory.rename(newdir);directory=newdir
                receipt.update(identity=stale,cache_key=stale_key,artifacts=artifacts())
                (directory/'receipt.json').write_text(json.dumps(receipt))
                with self.assertRaisesRegex(FormatError,'stale resident DATA'):oracle.cached(stale_key)


if __name__=='__main__':unittest.main()
