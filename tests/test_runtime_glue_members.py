"""Complete glue admission and exact-entry routing regression controls."""
import copy,json,sys,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from analysis_support import ROOT,game
from census import advisory_image
from common import FormatError,sha256
from repo_paths import canonical_path
import runtime_glue_members as g
import runtime_entry_routes as routes

class GlueTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc=json.loads(canonical_path(ROOT,g.RECIPE).read_text())
        with advisory_image():cls.original=game()[:2]
        cls.contexts,cls.bounds=g.producer(ROOT,cls.doc)
        cls.bases=g.bases(ROOT,cls.doc,cls.original)
        cls.result=g.verify(ROOT,document=cls.doc,original=cls.original)

    def prove(self,specs=None,candidate=None,bases=None,original=None):
        return g.prove_context(candidate or self.contexts['one-lib'],original or self.original,
                               specs if specs is not None else self.doc['specs'],self.bounds,bases or self.bases)

    def spec(self,name):return next(r for r in self.doc['specs'] if r['member']==name)

    def changed(self,name,field,*,original=False):
        b,m,sm=self.contexts['one-lib'];offset=self.bounds[name][0]
        if original:b,m=self.original;offset=self.spec(name)['original']
        out=bytearray(b);h=m['hunks'][0];out[h['content_offset']+offset+field]^=1
        return (bytes(out),m) if original else (bytes(out),m,sm)

    def test_all_complete_members_and_independent_contexts(self):
        self.assertEqual(len(self.result['contributions']),91)
        self.assertEqual(sum(r['size'] for r in self.result['contributions']),1234)
        self.assertEqual(sum(r['size'] for r in self.result['contributions'] if r['accounting']),1076)
        self.assertEqual(self.contexts['one-lib'],self.contexts['one-source'])
        self.assertEqual(self.contexts['two-lib'],self.contexts['two-source'])
        self.assertTrue(all(not r['relocation_identity'] for r in self.result['contributions']))

    def test_each_base_wrong_coordinate_rejects(self):
        for name in self.bases:
            bad=copy.deepcopy(self.bases);bad[name]['original']=(1,bad[name]['original'][1]+4)
            with self.subTest(base=name),self.assertRaises(FormatError):self.prove(bases=bad)

    def test_candidate_and_original_a4_operand_changes_reject(self):
        for name in ('_read','delay','draw','autorequ','createup','findtool'):
            field=next(int(k) for k in self.spec(name)['fields'])
            with self.subTest(member=name),self.assertRaises(FormatError):self.prove(candidate=self.changed(name,field))
            with self.assertRaises(FormatError):self.prove(original=self.changed(name,field,original=True))

    def test_masked_or_omitted_operand_rejects(self):
        bad=copy.deepcopy(self.doc['specs']);next(r for r in bad if r['member']=='_read')['fields']={}
        with self.assertRaisesRegex(FormatError,'unbound'):self.prove(specs=bad)
        bad=copy.deepcopy(self.doc['specs']);next(r for r in bad if r['member']=='read')['fields'][0]=dict(kind='PC',symbol='__Read')
        with self.assertRaises(FormatError):self.prove(specs=bad)

    def test_partial_member_and_interior_export_reject(self):
        for name in ('_read','draw','read'):
            bad=copy.deepcopy(self.doc['specs']);next(r for r in bad if r['member']==name)['size']-=2
            with self.assertRaisesRegex(FormatError,'partial member'):self.prove(specs=bad)
        bad=copy.deepcopy(self.doc['specs']);next(r for r in bad if r['member']=='read')['entries'][0][1]=2
        with self.assertRaises(FormatError):self.prove(specs=bad)

    def test_forwarder_without_proved_target_rejects(self):
        for name,private in [('read','_read'),('seek','_seek'),('close','_close'),('open','_open')]:
            bad=[r for r in self.doc['specs'] if r['member']!=private]
            with self.subTest(member=name),self.assertRaisesRegex(FormatError,'forwarder lacks proved target'):self.prove(specs=bad)
            with self.assertRaises(FormatError):self.prove(candidate=self.changed(name,2))

    def test_ordinary_bytes_and_relocations_reject(self):
        for name in ('read','_read','newlist','bltbitma','text','createup'):
            with self.assertRaises(FormatError):self.prove(candidate=self.changed(name,0))
        b,m,sm=self.contexts['one-lib'];bad=copy.deepcopy(m)
        bad['relocations'].append(dict(source_hunk=0,source_offset=self.bounds['_read'][0]+2,width=4,type='HUNK_RELOC32',target_hunk=1,addend_raw=0))
        with self.assertRaises(FormatError):self.prove(candidate=(b,bad,sm))

    def test_rehashed_recipe_and_failed_producer_reject(self):
        bad=copy.deepcopy(self.doc);bad['specs'][0]['size']=2
        with self.assertRaisesRegex(FormatError,'curated recipe'):g.verify(ROOT,document=bad,original=self.original)
        checked=g.checked
        def failed(root,record):
            raw=checked(root,record)
            if record==self.doc['receipt']:
                obj=json.loads(raw);obj['steps'][0]['returncode']=10;return json.dumps(obj).encode()
            return raw
        with patch.object(g,'checked',side_effect=failed),self.assertRaisesRegex(FormatError,'producing commands'):g.producer(ROOT,self.doc)

class RouteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with advisory_image():cls.original=game()[:2]
        cls.sha=sha256(cls.original[0]);cls.rows=routes.load(ROOT,cls.sha,original=cls.original,audit=True)

    def test_proven_natural_tail_and_forwarder_entries(self):
        for offset,name in [(0x7bd8,'_printf'),(0x86f6,'_Read'),(0x8708,'_Seek'),(0x86ee,'__Output'),(0x8a1e,'_SetIntVector')]:
            self.assertEqual(self.rows[(0,offset)]['symbol'],name)
        self.assertNotIn((0,0x86f8),self.rows)
        self.assertTrue(all(r['kind']=='LIBRARY_MEMBER' and not r['symbol'].startswith('.') for r in self.rows.values()))

    def test_dot_entries_and_wrong_extents_reject_or_stay_unroutable(self):
        proof=dict(status='COMPLETE_RUNTIME_CODE_MATCH',contributions=[dict(original=dict(hunk=0,offset=0,size=4),size=4,member='p',profile='aztec36',entries=[dict(name='.Fadd',offset=0)])])
        self.assertEqual(routes.export(proof,'x','y'),{})
        proof['contributions'][0]['entries'][0]=dict(name='_Private',offset=4)
        with self.assertRaises(FormatError):routes.export(proof,'x','y')
        proof['contributions'][0]['entries'][0]['offset']=0;proof['contributions'][0]['size']=2
        with self.assertRaises(FormatError):routes.export(proof,'x','y')

    def test_wrong_game_and_curated_provider_change_reject(self):
        with self.assertRaises(FormatError):routes.load(ROOT,'0'*64,original=self.original)
        doc=json.loads(canonical_path(ROOT,routes.INPUT).read_text());doc['providers'].pop()
        with self.assertRaises(FormatError):routes.load(ROOT,self.sha,document=doc,original=self.original)

    def test_route_derivation_keeps_mechanical_c_view(self):
        import runtime_member_routes as r
        source='extern long F_h00_86F6();\nrecovered() { return F_h00_86F6(); }\n'
        member=dict(hunk=0,start=0x291e,direct_callees=[dict(hunk=0,offset=0x86f6,basis='PC_RELATIVE')])
        with patch('recovery_state.runtime_dependencies',return_value=self.rows):out=r.derive([member],source,game_sha256=self.sha)
        self.assertEqual(out[0]['symbol'],'_Read')
        self.assertIn('#define F_h00_86F6 Read',r.object_source(source,out))
        member['direct_callees'][0]['offset']=0x86f8
        with patch('recovery_state.runtime_dependencies',return_value=self.rows):self.assertEqual(r.derive([member],source,game_sha256=self.sha),[])

    def test_unit_pc_and_a4_exact_entries_remain_external_but_interiors_reject(self):
        import check_unit
        functions=[dict(id='resident_F_0100',hunk=0,node='resident',start=0x100,end=0x104,size=4,
                        direct_callees=[],referenced_data=[]),
                   dict(id='resident_F_0200',hunk=0,node='resident',start=0x200,end=0x204,size=4,
                        direct_callees=[],referenced_data=[])]
        ledger=dict(game_sha256=self.sha,functions=functions)
        def validated(fid):return next(f for f in functions if f['id']==fid),ledger
        for basis in ('PC_RELATIVE','A4_RELOCATED_JMP_STUB'):
            for interior in (False,True):
                functions[0]['direct_callees']=[dict(id='resident_F_876E' if interior else 'resident_F_876C',
                    hunk=0,offset=0x876e if interior else 0x876c,basis=basis)]
                with patch.object(check_unit,'validated_function',side_effect=validated), \
                     patch.object(check_unit,'recovery',return_value=dict(functions={})), \
                     patch('recovery_state.runtime_dependencies',return_value=self.rows):
                    # Resident A4-slot callees stay external stand-ins (their slot
                    # identity is proved by the resident interface route); only a
                    # PC-relative call into a library interior is a missing member.
                    if interior and basis=='PC_RELATIVE':
                        with self.assertRaisesRegex(FormatError,'unrecovered same-node dependency'):
                            check_unit.prepare_unit('resident_F_0100','recovered() { return 0; }',
                                member_sources={'resident_F_0200':'recovered() { return 0; }'},natural_interval=(0x100,0x204))
                    else:
                        members,*_=check_unit.prepare_unit('resident_F_0100','recovered() { return 0; }',
                            member_sources={'resident_F_0200':'recovered() { return 0; }'},natural_interval=(0x100,0x204))
                        self.assertEqual({m['id'] for m in members},{f['id'] for f in functions})

if __name__=='__main__':unittest.main(verbosity=2)
