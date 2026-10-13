"""Complete library members proved with exact relocations, and their unit routes."""
import copy
import sys
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))

from common import FormatError, sha256
from runtime_arithmetic import aliases
from runtime_members import relocation_identity, SEGLOAD_RELOCATIONS, object_code_size
import compiler_oracle
import runtime_member_routes as routes
import check_unit


class RelocatedMemberTests(unittest.TestCase):
    def setUp(self):
        raw=bytearray(244);raw[40:44]=(8).to_bytes(4,'big');self.raw=bytes(raw)
        self.hunks=[dict(number=0,node='resident',type='CODE',content_offset=0,initialized_size=244),
                    dict(number=1,node='resident',type='DATA',content_offset=244,initialized_size=0)]
        self.relocs=[dict(source_hunk=0,source_offset=r['offset'],width=r['width'],type=r['type'],
                         target_hunk=r['target']['hunk'],addend_raw=r['target']['addend']) for r in SEGLOAD_RELOCATIONS]
        self.model=dict(hunks=self.hunks,relocations=self.relocs)
        self.item=dict(member='segload',library_sha256='lib',size=244,original=dict(hunk=0,offset=0,size=244),
                       code_sha256=sha256(self.raw),owned_data_size=0,owned_bss_size=0,
                       relocation_identity=copy.deepcopy(SEGLOAD_RELOCATIONS),
                       entries=[dict(name='_segload',offset=0),dict(name='.segload',offset=18)])
        self.evidence=dict(game_sha256=sha256(self.raw),contributions=[self.item])
        self.compiled=dict(identity=dict(library_sha256='lib'),contribution=dict(hunks=copy.deepcopy(self.hunks),
                           all_relocations=copy.deepcopy(self.relocs),symbols=[dict(name=e['name'],hunk=0,offset=e['offset']) for e in self.item['entries']]))

    def resolve(self, raw=None):
        return aliases(self.compiled,self.raw if raw is None else raw,self.raw,self.model,self.evidence)

    def test_complete_relocation_identity_match(self):
        syms,proof=self.resolve()
        self.assertEqual([s['name'] for s in syms],['F_h00_0000','F_h00_0012'])
        self.assertEqual(proof[0]['relocation_identity'],SEGLOAD_RELOCATIONS)

    def test_missing_relocation(self):
        self.compiled['contribution']['all_relocations'].pop()
        self.assertEqual(self.resolve()[0],[])

    def test_extra_relocation(self):
        self.compiled['contribution']['all_relocations'].append(dict(self.relocs[0],source_offset=72))
        self.assertEqual(self.resolve()[0],[])

    def test_wrong_site_type_width_target_addend(self):
        for field,value in [('source_offset',42),('type','HUNK_DREL32'),('width',2),('target_hunk',1),('addend_raw',10)]:
            with self.subTest(field=field):
                self.compiled['contribution']['all_relocations']=copy.deepcopy(self.relocs)
                self.compiled['contribution']['all_relocations'][0][field]=value
                self.assertEqual(self.resolve()[0],[])

    def test_shortened_rehashed_contribution_is_not_a_whole_member(self):
        self.item['size']=self.item['original']['size']=240
        self.item['code_sha256']=sha256(self.raw[:240])
        with self.assertRaises(FormatError):self.resolve()

    def test_original_relocation_tamper(self):
        self.relocs[0]['addend_raw']=10
        with self.assertRaises(FormatError):self.resolve()

    def test_duplicate_and_straddling_relocations_reject(self):
        for r in [dict(self.relocs[0]),dict(self.relocs[0],source_offset=242)]:
            model=dict(hunks=self.hunks,relocations=self.relocs+[r])
            with self.assertRaises(FormatError):relocation_identity(model,self.item['original'])

    def test_export_offsets_and_whole_bytes_required(self):
        self.compiled['contribution']['symbols'][1]['offset']=20
        self.assertEqual(self.resolve()[0],[])
        self.compiled['contribution']['symbols'][1]['offset']=18
        self.assertEqual(self.resolve(self.raw[:-1]+b'1')[0],[])

    def test_wrong_library_rejects(self):
        self.compiled['identity']['library_sha256']='wrong'
        self.assertEqual(self.resolve()[0],[])

    def test_nonzero_owned_data_bss_never_clipped(self):
        for at in (14,18):
            obj=bytearray(22);obj[:2]=b'AJ';obj[10:14]=(244).to_bytes(4,'big');obj[at:at+4]=(4).to_bytes(4,'big')
            with self.assertRaises(FormatError):object_code_size(obj)

    def test_wrong_root_hunk_type(self):
        self.compiled['contribution']['hunks'][1]['type']='BSS'
        with self.assertRaises(FormatError):self.resolve()


class RouteTests(unittest.TestCase):
    def tearDown(self):routes._routes.clear()

    def test_registration_changes_only_routed_trial(self):
        source='extern int F_h00_7978();\nrecovered() { return F_h00_7978(); }\n'
        other='recovered() { return 4; }\n'
        before=compiler_oracle.harness(other,0)
        rows=[dict(name='F_h00_7978',symbol='_segload',evidence='proof',evidence_sha256='hash')]
        routes.register(source,rows)
        self.assertEqual(compiler_oracle.harness(other,0),before)
        harness=compiler_oracle.harness(source,0)
        self.assertNotIn('F_h00_7978() {',harness)
        self.assertIn('Library routes',harness)
        objects=compiler_oracle.object_specs(dict(source=source,objects=[dict(source=source)],profile='aztec36'))
        self.assertTrue(objects[0]['source'].startswith('#define F_h00_7978 segload\n'))
        self.assertEqual(compiler_oracle.object_specs(dict(source=other,profile='aztec36'))[0]['source'],other)

    def test_only_exact_public_entry_is_routable(self):
        runtime={(0,0x7978):dict(kind='LIBRARY_MEMBER',symbol='_segload',evidence='proof',evidence_sha256='hash')}
        member=dict(hunk=0,start=0,direct_callees=[dict(basis='PC_RELATIVE',hunk=0,offset=0x7978)])
        source='extern int F_h00_7978();\nrecovered() { return F_h00_7978(); }\n'
        with patch('analysis_support.game',return_value=(b'',{},{})),patch('recovery_state.runtime_dependencies',return_value=runtime):
            self.assertEqual(len(routes.derive([member],source)),1)
            member['direct_callees'][0]['offset']+=2
            self.assertEqual(routes.derive([member],source),[])

    def test_replay_uses_supplied_oracle_identity_without_recursive_census(self):
        source='extern int F_h00_7978(); recovered() { return F_h00_7978(); }'
        member=dict(id='entry',hunk=0,start=0,direct_callees=[dict(basis='PC_RELATIVE',hunk=0,offset=0x7978)])
        runtime={(0,0x7978):dict(kind='LIBRARY_MEMBER',symbol='_segload',evidence='proof',evidence_sha256='hash')}
        with patch('analysis_support.game',side_effect=AssertionError('recursive game read')),patch('recovery_state.runtime_dependencies',return_value=runtime):
            rows=routes.derive([member],source,game_sha256='game')
            unit=dict(runtime_library_routes=rows,ordered_members=[dict(id='entry')])
            routes.replay(unit,source,[member],game_sha256='game')

    def test_register_abi_helpers_keep_compiler_routing(self):
        member=dict(hunk=0,start=0,direct_callees=[dict(basis='PC_RELATIVE',hunk=0,offset=32)])
        with patch('recovery_state.runtime_dependencies',return_value={(0,32):dict(kind='LIBRARY_MEMBER',symbol='.Fadd')}):
            self.assertEqual(routes.derive([member],'recovered() { return 0; }',game_sha256='game'),[])

    def test_stale_route_receipt_rejects(self):
        unit=dict(runtime_library_routes=[dict(name='wrong')],ordered_members=[dict(id='entry')])
        with patch.object(routes,'derive',return_value=[dict(name='right')]):
            with self.assertRaises(FormatError):routes.replay(unit,'source',[dict(id='entry',direct_callees=[])])

    def test_preparation_skips_library_but_keeps_game_callee(self):
        source='recovered() { return 0; }\n'; dep_source='recovered() { return 2; }\n'
        entry=dict(id='entry',hunk=0,start=0,end=4,direct_callees=[dict(id='lib',hunk=0,offset=40,basis='PC_RELATIVE'),
                                                              dict(id='dep',hunk=0,offset=4,basis='PC_RELATIVE')])
        dep=dict(id='dep',hunk=0,start=4,end=8,direct_callees=[])
        with tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parent) as td:
            root=Path(td);(root/'dep.c').write_text(dep_source)
            rec=dict(functions=dict(dep=dict(source='dep.c',source_sha256=sha256(dep_source.encode()))))
            ledger=dict(game_sha256='game',functions=[entry,dep])
            with patch.object(check_unit,'ROOT',root),patch.object(check_unit,'recovery',return_value=rec),\
                 patch.object(check_unit,'validated_function',side_effect=lambda fid:({'entry':entry,'dep':dep}[fid],ledger)),\
                 patch.object(check_unit,'proven_object_members',return_value=[]),patch.object(check_unit,'proven_tail',return_value=(b'',None)),\
                 patch('recovery_state.runtime_dependencies',return_value={(0,40):dict(kind='LIBRARY_MEMBER')}):
                members,_,_,_=check_unit.prepare_unit('entry',source,allow_gaps=True,local_calls_only=True)
                self.assertEqual([m['id'] for m in members],['entry','dep'])
                entry['direct_callees'][0]['offset']=42
                with self.assertRaisesRegex(FormatError,'unrecovered same-node dependency: lib'):
                    check_unit.prepare_unit('entry',source,allow_gaps=True,local_calls_only=True)


if __name__=='__main__':unittest.main()
