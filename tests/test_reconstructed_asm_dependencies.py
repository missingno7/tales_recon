"""Synthetic dependency contracts; no corpus sizes or growing target lists."""
import copy,json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import reconstructed_asm_dependencies as asm
import canonical_code_data_dependencies as typed
from common import FormatError,sha256,json_bytes


class ClosureTests(unittest.TestCase):
    def records(self):
        def record(ident,start,end,exports,calls=(),edges=()):
            return dict(id=ident,item={},symbol=exports[0]['name'],fact=dict(original=dict(hunk=0,start=start,end=end),exports=exports,external_code=list(calls),boundary_edges=list(edges)))
        a=record('a',0x100,0x110,[dict(name='_a',offset=0,original=0x100),dict(name='_inside',offset=4,original=0x104)],
                 [dict(hunk=0,target=0x200,name='_b'),dict(hunk=0,target=0x80,name='_c')],
                 [dict(kind='CALL',target=0x110)])
        b=record('b',0x200,0x210,[dict(name='_b',offset=0,original=0x200)])
        n=record('neighbor',0x110,0x118,[dict(name='_neighbor',offset=0,original=0x110)])
        return {(0,0x100):a,(0,0x104):dict(a,symbol='_inside'),(0,0x110):n,(0,0x200):b}
    def member(self,target,basis='PC_RELATIVE'):
        return dict(direct_callees=[dict(hunk=0,offset=target,basis=basis)])
    def test_interior_export_selects_whole_object_and_closes_named_calls(self):
        with patch.object(asm,'inventory',return_value=self.records()):
            rows,c=asm.closure([self.member(0x104)])
        self.assertEqual([r['id'] for r in rows],['a','neighbor','b'])
        self.assertEqual(c,[(0,0x80)])
    def test_a4_calls_do_not_pull_asm_objects(self):
        with patch.object(asm,'inventory',return_value=self.records()):
            self.assertEqual(asm.closure([self.member(0x100,'A4_RELOCATED_JMP_STUB')]),([],[]))
    def test_missing_one_past_owner_rejects(self):
        by=self.records();del by[(0,0x110)]
        with patch.object(asm,'inventory',return_value=by),self.assertRaisesRegex(FormatError,'one-past'):
            asm.closure([self.member(0x100)])
    def test_ownership_requires_exact_export(self):
        with patch.object(asm,'inventory',return_value=self.records()):
            self.assertTrue(asm.owns('resident_F_0104',entries=self.records()))
            self.assertFalse(asm.owns('resident_F_0106',entries=self.records()))
    def test_unrelated_members_have_no_recipe(self):
        with patch.object(asm,'inventory',return_value=self.records()):
            self.assertIsNone(asm.derive([self.member(0x300)]))
    def test_source_adaptation_changes_only_bound_symbol(self):
        recipe=dict(aliases={'F_h00_0104':'inside'},external_data=['G_h01_0002'])
        original='extern int F_h00_0104();\nextern int F_h00_0106();\nrecovered() { F_h00_0104(); }\n'
        text=asm.source(original,recipe)
        self.assertIn('F_h00_0106',text);self.assertIn('inside()',text)
        self.assertNotIn('extern long',text)
        self.assertEqual(asm.harness_source(original,recipe).count('extern long G_h01_0002;'),1)
    def test_single_c_object_mode_cannot_absorb_asm(self):
        with self.assertRaisesRegex(FormatError,'separate'):
            asm.configure(dict(target_node=0,profile='aztec36',source='recovered() {}'),{})
    def test_typed_selector_has_no_harness_allocation(self):
        recipe=dict(omit_harness_objects=['G_h00_0200'])
        text=typed.harness_source('extern long G_h00_0200;\nextern long G_h01_0002;\n',recipe)
        self.assertNotIn('G_h00_0200',text);self.assertIn('G_h01_0002',text)
        with self.assertRaises(FormatError):typed.harness_source('extern char G_h00_0200;',recipe)
    def test_no_selector_reference_means_no_typed_recipe(self):
        self.assertIsNone(typed.derive([dict(relocations=[])],Path('.'),{}))


class LinkedTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name)
        (self.root/'work').mkdir();(self.root/'evidence').mkdir()
        self.raw=b'canonical assembled object';self.objhash=sha256(self.raw)
        self.fact=dict(original=dict(hunk=0,start=0x100,end=0x108),exports=[dict(name='_entry',offset=0,original=0x100),dict(name='_end',offset=8,original=None)],boundary_edges=[])
        (self.root/'evidence/fact.json').write_text(json.dumps(self.fact))
        self.item=dict(source='source.asm',source_sha256='source hash',proof='proof.json',proof_sha256='proof hash',fact='evidence/fact.json')
        self.object=dict(self.item,id='owner',category='RECONSTRUCTED_ASM',fact_sha256=sha256(json_bytes(self.fact)),object_sha256=self.objhash,label='asm000',original=self.fact['original'])
        self.recipe=dict(objects=[self.object],aliases={'F_h00_0100':'entry'},external_data=['G_h01_0020'],c_bytes=0,data_credit=0)
        self.directory=self.root/'work';(self.directory/'t000_asm000.o').write_bytes(self.raw)
        (self.directory/'t000.exe').write_bytes(b'link');(self.directory/'t000.sym').write_text('symbol map')
        self.compiled=dict(status='COMPILED',directory=str(self.directory),prefix='t000',identity={asm.FIELD:self.recipe},contribution=dict(resident_bounds=dict(end=10),symbols=[]))
        self.code=bytes.fromhex('2079000000004e75')
        self.ref=dict(offset=2,width=4,type='HUNK_RELOC32',symbol='_G_h01_0020',addend=0)
        self.payload=bytes(10)+bytes.fromhex('2079000000204e75')
        self.reloc=dict(source_hunk=0,source_offset=12,target_hunk=1,addend_raw=32,type='HUNK_RELOC32',width=4)
        self.model=dict(hunks=[dict(number=0,type='CODE',allocated_size=20,initialized_size=20),dict(number=1,type='DATA',allocated_size=40,initialized_size=0),dict(number=2,type='BSS',allocated_size=4,initialized_size=0)],relocations=[self.reloc])
        self.sm={(0,'_entry'):10,(0,'_end'):18,(2,'__H2_org'):0,(2,'_G_h01_0020'):32}
        self.context=dict(blob=b'oracle',model={},analysis={},ledger=dict(reconstructed_asm={'owner':self.item}))
        self.accepted=dict(id='owner',object_structure=dict(object_sha256=self.objhash))
    def validate(self):
        with patch('reconstructed_asm.rows',return_value=[self.accepted]),patch('hunk.parse',return_value=self.model),patch('overlay_experiment.symbols',return_value=self.sm),patch('audio_sequence_data.payload',return_value=self.payload),patch.object(asm,'object_code',return_value=(self.code,[self.ref],{})):
            return asm.validate_linked(self.compiled,self.root,self.context)
    def test_complete_object_rebinds_common_and_has_zero_c_credit(self):
        out=self.validate();self.assertEqual(out[asm.FIELD][0]['c_bytes'],0)
        self.assertEqual(out[asm.FIELD][0]['category'],'RECONSTRUCTED_ASM')
        self.assertIn(dict(name='_F_h00_0100',hunk=0,offset=10),out['contribution']['symbols'])
        self.assertEqual(self.compiled['contribution']['symbols'],[])
    def test_changed_object_rejects(self):
        (self.directory/'t000_asm000.o').write_bytes(b'mutant')
        with self.assertRaisesRegex(FormatError,'complete canonical'):self.validate()
    def test_changed_ordinary_byte_rejects(self):
        self.payload=bytes(10)+bytes.fromhex('2279000000204e75')
        with self.assertRaisesRegex(FormatError,'CODE/named'):self.validate()
    def test_changed_named_field_rejects(self):
        self.payload=bytes(10)+bytes.fromhex('2079000000244e75')
        with self.assertRaisesRegex(FormatError,'CODE/named'):self.validate()
    def test_missing_relocation_rejects(self):
        self.model['relocations']=[]
        with self.assertRaisesRegex(FormatError,'relocation inventory'):self.validate()
    def test_extra_relocation_rejects(self):
        self.model['relocations'].append(dict(self.reloc,source_offset=16))
        with self.assertRaisesRegex(FormatError,'relocation inventory'):self.validate()
    def test_common_folding_needs_actual_link_convention(self):
        self.sm[(2,'__H2_org')]=4
        with self.assertRaisesRegex(FormatError,'relocation inventory'):self.validate()
    def test_wrong_export_partition_rejects(self):
        self.sm[(0,'_entry')]=12
        with self.assertRaisesRegex(FormatError,'order/export'):self.validate()
    def test_lost_canonical_ownership_rejects(self):
        self.accepted['id']='other'
        with self.assertRaisesRegex(FormatError,'canonical ownership'):self.validate()
    def test_changed_canonical_proof_rejects(self):
        self.context['ledger']['reconstructed_asm']['owner']=dict(self.item,proof_sha256='changed')
        with self.assertRaisesRegex(FormatError,'canonical identity'):self.validate()


class QueueTests(unittest.TestCase):
    def test_dependency_trials_use_dependency_key(self):
        import compile_queue,queued_oracle
        trial={asm.FIELD:dict(objects=[])}
        with patch.object(queued_oracle,'trial_plan',return_value=('dependency-key',{},'',[])):
            self.assertEqual(compile_queue.trial_key(trial),'dependency-key')
    def test_dependency_trials_use_capable_runner(self):
        import compile_queue,queued_oracle
        trials=[{asm.FIELD:{'objects':[]}}]
        with patch.object(queued_oracle,'compile_many',return_value=['compiled']) as runner:
            self.assertEqual(compile_queue._compile_batch(trials),['compiled']);runner.assert_called_once_with(trials)


class UnitBoundaryTests(unittest.TestCase):
    def test_missing_asm_recipe_cannot_pass_as_a_c_stub(self):
        import check_unit
        with patch.object(check_unit,'recovery',return_value={}),patch.object(asm,'derive',return_value={'objects':['canonical']}),self.assertRaisesRegex(FormatError,'complete object recipe'):
            check_unit.compare_unit([],{},dict(status='COMPILED',identity={}),32766)
    def test_plain_units_keep_the_existing_comparison(self):
        import check_unit
        result=dict(verdict='EQUAL',members=[dict(id='c',verdict='EQUAL')])
        with patch.object(check_unit,'recovery',return_value={}),patch.object(asm,'derive',return_value=None),patch.object(check_unit,'_compare_unit',return_value=result):
            self.assertEqual(check_unit.compare_unit([],{},dict(status='COMPILED',identity={}),32766),result)
    def test_complete_asm_dependencies_stay_outside_c_members(self):
        import check_unit
        recipe=dict(objects=['canonical']);reports=[dict(id='asm',category='RECONSTRUCTED_ASM',c_bytes=0)]
        compiled=dict(status='COMPILED',identity={asm.FIELD:recipe})
        linked=dict(compiled,**{asm.FIELD:reports});result=dict(verdict='EQUAL',members=[dict(id='c',verdict='EQUAL')])
        with patch.object(check_unit,'recovery',return_value={}),patch.object(asm,'derive',return_value=recipe),patch.object(asm,'validate_linked',return_value=linked),patch.object(check_unit,'_compare_unit',return_value=result):
            out=check_unit.compare_unit([],{},compiled,32766)
        self.assertEqual(out['members'],[dict(id='c',verdict='EQUAL')])
        self.assertEqual(out['reconstructed_asm_member_comparisons'],reports)
        self.assertTrue(out['c_contribution_only'])
    def test_missing_one_past_neighbor_rejects_physical_link(self):
        # Reuse a complete synthetic link, adding only the outward short edge.
        fixture=LinkedTests('test_complete_object_rebinds_common_and_has_zero_c_credit');fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        fixture.fact['boundary_edges']=[dict(kind='CALL',target=0x108)]
        (fixture.root/'evidence/fact.json').write_text(json.dumps(fixture.fact))
        fixture.object['fact_sha256']=sha256(json_bytes(fixture.fact))
        with self.assertRaisesRegex(FormatError,'one-past dependency missing'):fixture.validate()
    def test_support_only_typed_object_is_still_verified(self):
        import audio_stateful_provider as stateful,audio_score_measured as score
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);work=root/'work';work.mkdir();raw=b'complete support';digest=sha256(raw)
            (work/'t000_typed000.o').write_bytes(raw);(work/'t000.exe').write_bytes(b'link');(work/'t000.sym').write_text('map')
            row=dict(prefix='support',object_sha256=digest,typed_bytes=0)
            (root/'one.json').write_text(json.dumps(dict(comparison=dict(objects=[row]))))
            (root/'two.json').write_text(json.dumps(dict(comparison=dict(objects=[]))))
            inputs={'one':dict(proof='one.json'),'two':dict(proof='two.json')}
            recipe=dict(inputs=inputs,objects=[dict(prefix='support',object_sha256=digest,label='typed000')])
            compiled=dict(directory=str(work),prefix='t000')
            aj=dict(code=b'xy',definitions=[dict(name='_G_h00_6200',offset=0,external=False)],fixups=[])
            ctx=dict(blob=b'oracle',model={},analysis={},ledger=dict(code_data_providers=inputs))
            with patch.object(stateful,'IDENT','one'),patch.object(score,'IDENT','two'),patch.object(stateful,'rows',return_value=[]) as first,patch.object(score,'rows',return_value=[]) as second,patch.object(typed,'object_code',return_value=aj),patch('hunk.parse',return_value=dict(relocations=[])),patch('overlay_experiment.symbols',return_value={(0,'_G_h00_6200'):10}),patch('audio_sequence_data.payload',return_value=bytes(10)+b'xy'):
                reports=typed.validate_linked(compiled,recipe,10,root,ctx)
            self.assertEqual(reports[0]['category'],'TYPED_CODE_DATA');self.assertEqual(reports[0]['c_bytes'],0)
            first.assert_called_once();second.assert_called_once()


class LazyLookupTests(unittest.TestCase):
    def test_unrelated_unit_reads_no_asm_facts(self):
        specs=asm.specifications();ident=next(iter(specs));outside=min(s['start'] for s in specs.values())-2
        ledger=dict(reconstructed_asm={ident:{}})
        members=[dict(direct_callees=[dict(hunk=0,offset=outside,basis='PC_RELATIVE')])]
        with patch.object(asm,'inventory',side_effect=AssertionError('unrelated fact read')):
            self.assertIsNone(asm.derive(members,Path('.'),ledger))
            self.assertFalse(asm.owns('resident_F_%04X'%outside,Path('.'),ledger))
    def test_overlay_references_do_not_select_resident_asm(self):
        specs=asm.specifications();ident,spec=next(iter(specs.items()))
        ledger=dict(reconstructed_asm={ident:{}})
        with patch.object(asm,'inventory',side_effect=AssertionError('unrelated fact read')):
            self.assertIsNone(asm.derive([dict(direct_callees=[dict(hunk=3,offset=spec['start'],basis='PC_RELATIVE')])],Path('.'),ledger))


class PhysicalAliasTests(unittest.TestCase):
    def test_lowercase_hex_and_mechanical_widths_bind_the_canonical_name(self):
        recipe=dict(aliases={'F_h00_010A':'entry'})
        self.assertEqual(asm.source('extern int F_h0_10a();',recipe),'extern int entry();')
    def test_function_stand_in_cannot_shadow_a_proved_entry(self):
        fixture=LinkedTests('test_complete_object_rebinds_common_and_has_zero_c_credit');fixture.setUp()
        self.addCleanup(fixture.doCleanups);fixture.sm[(0,'_F_h00_0100')]=2
        with self.assertRaisesRegex(FormatError,'stand-in shadows'):fixture.validate()
    def test_data_spelling_cannot_shadow_a_proved_code_entry(self):
        fixture=LinkedTests('test_complete_object_rebinds_common_and_has_zero_c_credit');fixture.setUp()
        self.addCleanup(fixture.doCleanups);fixture.sm[(0,'_G_h00_0100')]=2
        with self.assertRaisesRegex(FormatError,'stand-in shadows'):fixture.validate()
