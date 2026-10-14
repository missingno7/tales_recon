"""Complete natural library tail CODE; private allocation stays UNKNOWN."""
import copy,json,sys,unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from common import FormatError
from analysis_support import game
import runtime_natural_members as n
import runtime_accounting as a
RECIPE_FILE=ROOT/n.RECIPE

class NaturalTailTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.recipe=json.loads(RECIPE_FILE.read_bytes());cls.original=game()[:2]
        cls.contexts=n.producer(ROOT,cls.recipe)
        cls.report=n.verify(ROOT,recipe=cls.recipe,original=cls.original)
        cls.tail=[r for r in cls.report['contributions'] if r['member'] in n.TAIL_MEMBERS]
        cls.rows=a.capture_runtime_members(ROOT,*cls.original)

    def context(self,candidate=None,original=None,recipe=None):
        return n.prove_tail_context(ROOT,recipe or self.recipe,candidate or self.contexts['tail_natural'],
                                    original or self.original,self.contexts['crt'])

    def changed(self,member,field,value):
        b,m,sm=self.contexts['tail_natural'];start=n.symbol(sm,n.SPECS[member]['export'])[1]
        h=next(h for h in m['hunks'] if h['number']==0);out=bytearray(b)
        at=h['content_offset']+start+field;out[at:at+len(value)]=value
        return bytes(out),m,sm

    def test_six_complete_CODE_members_and_unknown_private_allocation(self):
        self.assertEqual([(r['member'],r['size']) for r in self.tail],
                         [('sscanf',112),('scan',1124),('abort',42),('createpo',210),('createst',40),('createex',128)])
        self.assertEqual(sum(r['size'] for r in self.tail),1656)
        for member in ('sscanf','scan'):
            r=next(r for r in self.tail if r['member']==member)
            self.assertIsNone(r['owned_bss_size']);self.assertEqual(r['candidate_owned_bss_size'],6)
            self.assertEqual(r['storage_ownership'],'UNKNOWN');self.assertEqual(r['accepted_storage_size'],0)
        for proof in self.report['tail_contexts']:
            for name in self.recipe['tail']['private_accesses']:
                identity=proof['identities'][name]
                self.assertEqual(identity['ownership'],'UNKNOWN');self.assertIsNone(identity['allocation_identity'])
        ids={r['id'] for r in self.rows}
        self.assertNotIn('runtime_data_scan',ids)
        self.assertTrue(all(r['hunk']==0 for r in self.rows if r['id'] in {'runtime_member_'+m for m in n.TAIL_MEMBERS}))

    def test_every_external_operand_is_bound_and_wrong_word_rejects(self):
        candidate=self.contexts['tail_natural'];b,m,sm=candidate
        identities=self.report['tail_contexts'][0]['identities'];tested=0
        for row in self.tail:
            member=row['member'];spec=n.SPECS[member];start=n.symbol(sm,spec['export'])[1]
            fields={int(k):v for k,v in self.recipe['tail']['contracts'][member].items()}
            self.assertEqual(set(fields),{r['field'] for r in row['operand_identity'] if 'field' in r})
            for field in fields:
                raw=n.extent(b,m,0,start+field,2);bad=((int.from_bytes(raw,'big')+2)&65535).to_bytes(2,'big')
                with self.subTest(member=member,field=field),self.assertRaises(FormatError):
                    n.compare_member(self.changed(member,field,bad),self.original,spec['original'],start,spec['size'],spec['code_size'],fields,identities)
                tested+=1
        self.assertEqual(tested,58)

    def test_opcode_normalization_and_unbound_operand_reject(self):
        with self.assertRaises(FormatError):self.context(self.changed('scan',504,bytes.fromhex('4eba0002')))
        with self.assertRaises(FormatError):self.context(self.changed('createex',30,bytes.fromhex('4eba0002')))
        bad=copy.deepcopy(self.recipe);del bad['tail']['contracts']['scan']['86']
        with self.assertRaises(FormatError):self.context(recipe=bad)

    def test_original_private_access_and_initializer_templates_reject(self):
        ob,om=self.original;h=next(h for h in om['hunks'] if h['number']==0)
        for access in self.recipe['tail']['private_accesses'].values():
            spec=n.SPECS[access['member']];at=h['content_offset']+spec['original']+access['field']
            for delta in (1,-2):
                out=bytearray(ob);out[at+delta]^=2
                with self.subTest(member=access['member'],field=access['field'],delta=delta),self.assertRaises(FormatError):
                    self.context(original=(bytes(out),om))

    def test_private_storage_claim_never_follows_from_access_spacing(self):
        bad=copy.deepcopy(self.recipe);bad['tail']['original_bss_claim']={'size':12,'start':0x3aba}
        with self.assertRaises(FormatError):n.producer_tail(ROOT,bad['tail'])
        bad=copy.deepcopy(self.recipe);bad['tail']['private_accesses']['SSCANF_SCNSTR']['ownership']='PROVEN'
        with self.assertRaises(FormatError):n.producer_tail(ROOT,bad['tail'])

    def test_public_private_wrong_entry_and_slot_relocation_reject(self):
        b,m,sm=self.contexts['tail_natural'];row=next(r for r in self.tail if r['member']=='createex')
        slot=next(r for r in row['operand_identity'] if r.get('symbol')=='_AllocMem')['candidate_slot']['slot_offset']
        h=next(h for h in m['hunks'] if h['number']==1);out=bytearray(b)
        target=n.symbol(sm,'__AllocMem')[1]
        out[h['content_offset']+slot+2:h['content_offset']+slot+6]=target.to_bytes(4,'big')
        bad=copy.deepcopy(m);rel=next(r for r in bad['relocations'] if r['source_hunk']==1 and r['source_offset']==slot+2);rel['addend_raw']=target
        with self.assertRaises(FormatError):self.context((bytes(out),bad,sm))
        bad=copy.deepcopy(m);bad['relocations']=[r for r in bad['relocations'] if not(r['source_hunk']==1 and r['source_offset']==slot+2)]
        with self.assertRaises(FormatError):self.context((b,bad,sm))

    def test_complete_callback_helpers_and_literal_tail_are_not_clipped(self):
        for member,field in [('sscanf',38),('sscanf',110),('scan',824),('scan',882),('scan',1122),('abort',38),('abort',41)]:
            b,m,sm=self.contexts['tail_natural'];start=n.symbol(sm,n.SPECS[member]['export'])[1]
            raw=n.extent(b,m,0,start+field,1)
            with self.subTest(member=member,field=field),self.assertRaises(FormatError):self.context(self.changed(member,field,bytes([raw[0]^1])))

    def test_rehashed_recipe_and_whole_producer_outputs_reject(self):
        for key in ('contracts','private_accesses','artifacts','options','commands'):
            bad=copy.deepcopy(self.recipe);bad['tail'][key]={} if key!='commands' else []
            with self.subTest(key=key),self.assertRaises(FormatError):n.producer(ROOT,bad)
        read=n.read
        for suffix in ('/source','/scan.asm','/sscanf-source.o','/consumer.o','/reverse.sym'):
            def changed(root,path):return read(root,path)+b'X' if path.endswith(suffix) else read(root,path)
            with patch.object(n,'read',side_effect=changed),self.subTest(suffix=suffix),self.assertRaises(FormatError):n.producer(ROOT,self.recipe)

    def test_original_and_candidate_unchecked_CODE_relocations_reject(self):
        for original in (False,True):
            b,m,sm=self.contexts['tail_natural'];blob,model=self.original if original else (b,m);bad=copy.deepcopy(model)
            at=n.SPECS['sscanf']['original'] if original else n.symbol(sm,'_sscanf')[1]
            bad['relocations'].append(dict(source_hunk=0,source_offset=at+8,type='HUNK_RELOC32',width=4,target_hunk=1,addend_raw=0))
            with self.assertRaises(FormatError):
                self.context(original=(blob,bad)) if original else self.context(candidate=(blob,bad,sm))

    def test_snapshot_closure_tracks_new_producer_sources_and_access_anchors(self):
        paths=a.input_identity(ROOT)
        for suffix in ('/sol-lib-tail-routes-04/request.json','/sol-lib-tail-routes-04/sys/work/scan.c',
                       '/sol-lib-tail-routes-04/sys/work/consumer.asm','/ov04_F_037E.c','/runtime-tail-leaves.json'):
            self.assertTrue(any(p.replace('\\','/').endswith(suffix) for p in paths),suffix)

if __name__=='__main__':unittest.main()
