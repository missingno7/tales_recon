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
        for field in ('harness_sha256',):
            with self.assertRaises(FormatError):
                interfaces.evidence([self.function],self.source,dict(compiler,**{field:'0'*64}),self.blob,self.model,32766)
        for field in ('resident_interface_producer_sha256','resident_interface_extractor_sha256'):
            interfaces.evidence([self.function],self.source,dict(compiler,**{field:'0'*64}),self.blob,self.model,32766)
            with self.assertRaisesRegex(FormatError,'provenance'):
                interfaces.evidence([self.function],self.source,dict(compiler,**{field:'bad'}),self.blob,self.model,32766)
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
                self.assertEqual(oracle.cached(stale_key)['contribution'],contribution)
                # A stale tool hash grants no exemption from exact extraction.
                (directory/'candidate.exe').write_bytes(bad);receipt['artifacts']=artifacts()
                (directory/'receipt.json').write_text(json.dumps(receipt))
                with self.assertRaisesRegex(FormatError,'complete JMP'):oracle.cached(stale_key)


class LinkedResidentInterfaceTests(unittest.TestCase):
    """Synthetic PC/A4 calls to one real member, without canonical corpus reads."""
    def setUp(self):
        raw=bytes.fromhex('4eac000061024e754e75')
        self.blob=raw+bytes.fromhex('4ef900000008')
        def function(start,end,calls):
            return dict(id='resident_F_%04X'%start,hunk=0,node='resident',start=start,end=end,size=end-start,
                        raw_bytes=raw[start:end].hex(),sha256=sha256(raw[start:end]),extent_status='CLOSED_CFG',
                        referenced_data=[],relocations=[],direct_callees=calls)
        self.caller=function(0,8,[dict(id='resident_F_0008',hunk=0,offset=8,site=0,basis='A4_RELOCATED_JMP_STUB'),
                                  dict(id='resident_F_0008',hunk=0,offset=8,site=4,basis='PC_RELATIVE')])
        self.member=function(8,10,[])
        self.members=[self.caller,self.member]
        self.model=dict(hunks=[dict(number=0,content_offset=0,initialized_size=10),
                               dict(number=1,content_offset=10,initialized_size=6)],
                        relocations=[dict(source_hunk=1,source_offset=2,target_hunk=0,type='HUNK_RELOC32',width=4,addend_raw=8)])
        self.source='extern int F_h00_0008();\nrecovered() { F_h00_0008(); F_h00_0008(); }\nF_h00_0008() {}\n'
        self.recipe=interfaces.derive(self.members,self.source,self.blob,self.model,0)

    def specimen(self):
        raw=bytearray(224)
        raw[:8]=bytes.fromhex('49f900007ffe4e75')
        raw[100:110]=bytes.fromhex('4eac800e61024e754e75')
        raw[212:218]=bytes.fromhex('4ef90000006c')
        model=dict(hunks=[dict(number=0,content_offset=0,initialized_size=200),
                          dict(number=1,content_offset=200,initialized_size=24,allocated_size=24),
                          dict(number=2,content_offset=224,allocated_size=0)],
                   relocations=[dict(source_hunk=0,source_offset=2,target_hunk=1,type='HUNK_RELOC32',width=4,addend_raw=32766),
                                dict(source_hunk=1,source_offset=14,target_hunk=0,type='HUNK_RELOC32',width=4,addend_raw=108)])
        symbols={(0,'_recovered'):100,(0,'_F_h00_0008'):108,(0,'_F_h00_0010'):110}
        return raw,model,symbols

    def test_real_member_export_control_and_all_runner_identities(self):
        self.assertEqual(self.recipe['members'][0]['binding'],'LINKED_MEMBER')
        self.assertEqual(self.recipe['members'][0]['body'],'F_h00_0008')
        trial=dict(source=self.source,profile='aztec36',target_node=0,local_functions=['F_h00_0008'],
                   objects=[dict(source=self.source)],resident_data_interfaces=self.recipe)
        key,meta,harness=oracle.identity(self.source,'aztec36',0,oracle.object_specs(trial),trial['local_functions'],
                                        resident_data_interfaces=self.recipe)
        self.assertNotIn('resident_body_F_h00_0008',harness)
        self.assertNotIn('F_h00_0008() { return 0; }',harness)
        self.assertIn('resident_slot_export_reference',harness)
        proxy=next(p for p in oracle.overlay_proxies(self.source,0) if p['name']==interfaces.CONTROL)
        self.assertIn('F_h00_0008();',proxy['source'])
        self.assertEqual(oracle.object_specs(trial)[0]['source'],self.source)
        self.assertEqual(queued_oracle.trial_plan(trial)[:3],(key,meta,harness))
        self.assertEqual(compile_queue.trial_key(trial),key)
        trial.update(object_profiles=['aztec36-large-data'])
        self.assertEqual(mixed_profile_oracle.mixed_identity(trial)[2],harness)
        for local in ([],['F_h00_0010']):
            with self.assertRaisesRegex(FormatError,'local functions'):
                oracle.identity(self.source,'aztec36',0,local_functions=local,resident_data_interfaces=self.recipe)
        # Re-derivation and harness proof survive a fresh process registration.
        interfaces._routes.pop(self.source)
        interfaces.evidence(self.members,self.source,meta,self.blob,self.model,0)
        self.assertIn(self.source,interfaces._routes)
        bad={k:v for k,v in meta.items() if k not in (interfaces.FIELD,'resident_interface_producer_sha256','resident_interface_extractor_sha256')}
        with self.assertRaisesRegex(FormatError,'harness hash'):
            interfaces.evidence(self.members,self.source,bad,self.blob,self.model,0)

    def test_extern_or_comment_does_not_establish_a_linked_definition(self):
        for text in ('extern int F_h00_0008(); recovered() {}',
                     '/* F_h00_0008() {} */ extern int F_h00_0008(); recovered() {}'):
            recipe=interfaces.derive(self.members,text,self.blob,self.model,0)
            self.assertNotIn('binding',recipe['members'][0])
        self.assertTrue(interfaces.defines('long F_h00_0008(a,c) long a; long c; {}','F_h00_0008'))

    def test_slot_is_unique_complete_and_targets_exact_linked_member(self):
        raw,model,symbols=self.specimen()
        extracted=interfaces.extract(self.recipe,bytes(raw),model,symbols)
        self.assertEqual((extracted[0]['offset'],extracted[0]['target_offset']),(12,108))
        for mutation in ('different_member','non_member','missing_slot','missing_relocation','duplicate',
                         'wrong_opcode','wrong_hunk','missing_member_symbol','wrong_body','bad_slot_offset'):
            blob=bytearray(raw);m=copy.deepcopy(model);s=dict(symbols)
            if mutation in ('different_member','non_member'):
                target=110 if mutation=='different_member' else 150
                blob[214:218]=target.to_bytes(4,'big');m['relocations'][1]['addend_raw']=target
            elif mutation=='missing_slot':m['hunks'][1]['initialized_size']=12
            elif mutation=='missing_relocation':m['relocations'].pop()
            elif mutation=='duplicate':m['relocations'].append(copy.deepcopy(m['relocations'][1]))
            elif mutation=='wrong_opcode':blob[212]=0
            elif mutation=='wrong_hunk':m['relocations'][1]['target_hunk']=1
            elif mutation=='missing_member_symbol':del s[(0,'_F_h00_0008')]
            elif mutation=='wrong_body':blob[214:218]=(110).to_bytes(4,'big')
            else:m['relocations'][1]['source_offset']=16
            with self.subTest(mutation=mutation),self.assertRaises(FormatError):
                interfaces.extract(self.recipe,bytes(blob),m,s)
        bad=copy.deepcopy(self.recipe);bad['members'][0]['body']='F_h00_0010'
        with self.assertRaises(FormatError):interfaces.extract(bad,bytes(raw),model,symbols)

    def test_complete_unit_proves_both_call_routes_and_rejects_redirected_slot(self):
        from check_unit import compare_unit
        raw,model,symbols=self.specimen()
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);(root/'candidate.exe').write_bytes(raw)
            compiled=dict(status='COMPILED',identity=dict(profile='aztec36',flags=[],resident_data_interfaces=self.recipe),cache_key='synthetic',cache_hit=True,
                          directory=str(root),prefix='candidate',contribution=dict(hunk=0,code_offset=100,entry_offset=0,
                          resident_bounds=dict(start=100,end=110),code_hex=raw[100:110].hex(),code_size=10,
                          data_size=0,bss_size=0,object_sha256='synthetic',relocations=[],all_relocations=model['relocations'],
                          hunks=model['hunks'],symbols=[dict(hunk=h,name=n,offset=v) for (h,n),v in symbols.items()],
                          resident_data_interfaces=interfaces.extract(self.recipe,bytes(raw),model,symbols)))
            context=dict(root=root,ledger=dict(functions={},behavioral_functions={}),analysis=dict(functions=self.members),
                         blob=self.blob,model=self.model)
            names={self.caller['id']:'recovered',self.member['id']:'F_h00_0008'}
            report=compare_unit(self.members,names,compiled,0,allow_gaps=True,source_text=self.source,context=context)
            self.assertEqual(report['verdict'],'EQUAL')
            kinds=[p['kind'] for p in report['members'][0]['relocation_proof']]
            self.assertIn('A4_D16_SYMBOL',kinds)
            self.assertIn('PC_RELATIVE_CALL_SYMBOL',kinds)
            # Keep a valid slot at DATA+12, but redirect the A4 call to a
            # non-JMP pointer at +18 with the same member relocation. Ordinary
            # CODE identity alone must not accept that alternate call route.
            bad=copy.deepcopy(compiled);c=bad['contribution']
            raw[102:104]=bytes.fromhex('8014');raw[220:224]=(108).to_bytes(4,'big')
            c['code_hex']=raw[100:110].hex()
            c['all_relocations'].append(dict(source_hunk=1,source_offset=20,target_hunk=0,
                                             type='HUNK_RELOC32',width=4,addend_raw=108))
            (root/'candidate.exe').write_bytes(raw)
            report=compare_unit(self.members,names,bad,0,allow_gaps=True,source_text=self.source,context=context)
            self.assertEqual(report['verdict'],'DIFFER')
            self.assertIn('LINKED_MEMBER_SLOT',[i['kind'] for i in report['members'][0]['relocation_issues']])


if __name__=='__main__':unittest.main()
