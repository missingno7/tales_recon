"""Synthetic storage invariants: no progress snapshots or real-corpus replay."""
import copy
import json

import pytest

import data_model as dm
import storage_plan as sp
from common import FormatError


def facts(source='',widths=None,limit=128):
    return dict(sources={'src/a.c':source},widths=widths or {},providers=[],
        model={'structs':{},'globals':{}},
        regions=[dict(hunk=1,start=0,end=limit,kind='DATA',memory_flags=1),
                 dict(hunk=2,start=0,end=4,kind='BSS',memory_flags=0)])


def observed(width):
    return dict(widths=[width],sites=[],address_taken=0)


def curation():
    return dict(bounds=[],dependencies=[],structs={},receiver_calls=[],external_bindings=[],indexed_aliases=[])


def document(f,c=None):
    c=curation() if c is None else c
    return dict(schema_version=1,policy=sp.POLICY,curation=c,derived=sp.derive(c,f))


def object_for(d,name):
    alias=d['derived']['aliases'][name]
    return next(o for o in d['derived']['objects'] if o['id']==alias['object'])


def record_case():
    source=('struct Link { long a; long b; char flags[4]; };\n'
            'extern struct Link G_h01_0010[2];\n'
            'extern struct Link G_h01_0014[2];\n'
            'recovered() { int i; for(i=0;i<2;i++) { G_h01_0010[i].a=0; } }\n')
    f=facts(source)
    f['model']['structs']['Plan']={'size':12,'fields':[
        dict(offset=0,name='a',type='long',evidence='load/store'),
        dict(offset=4,name='b',type='long',evidence='load/store'),
        dict(offset=8,name='flags',type='char [4]',evidence='four flag cells')]}
    c=curation()
    c['bounds']=[dict(symbol='G_h01_0010',element_type='struct Plan',
        count=dict(source='src/a.c',pattern=r'for\(i=0;i<(2);i\+\+\)'),
        stride={'source':'src/a.c','struct':'Link'},name='link records',
        evidence='two iterations and independently computed 12-byte stride')]
    return f,c


def test_full_partition_includes_distinct_hunk_two():
    d=document(facts())
    assert d['derived']['summary']['bytes']['h2_BSS']==dict(total=4,bounded=0,UNBOUNDED=4,bounded_member_union=0,UNBOUNDED_gaps=4)
    for region in d['derived']['regions']:
        objects=[o for o in d['derived']['objects'] if o['hunk']==region['hunk']]
        assert objects[0]['start']==region['start']
        assert objects[-1]['end']==region['end']
        assert all(a['end']==b['start'] for a,b in zip(objects,objects[1:]))


def test_scalar_cell_needs_positive_width_evidence():
    f=facts('extern int G_h01_0004;')
    assert object_for(document(f),'G_h01_0004')['status']=='UNBOUNDED'
    f['widths'][4]=observed(2)
    o=object_for(document(f),'G_h01_0004')
    assert (o['status'],o['start'],o['extent'])==('BOUNDED',4,2)


def test_array_declaration_is_not_capacity_even_with_element_width():
    f=facts('extern int G_h01_0010[30];', {16:observed(2)})
    o=object_for(document(f),'G_h01_0010')
    assert o['extent'] is None and o['status']=='UNBOUNDED'


def test_overlapping_unknown_views_share_storage_with_offsets():
    f=facts('extern long G_h01_0010[4]; extern int G_h01_0012[3];')
    d=document(f)
    a,b=[d['derived']['aliases'][n] for n in ['G_h01_0010','G_h01_0012']]
    assert a['object']==b['object'] and b['offset']-a['offset']==2


def test_shifted_struct_tail_is_not_an_extra_allocation():
    f,c=record_case()
    d=document(f,c)
    a,b=[d['derived']['aliases'][n] for n in ['G_h01_0010','G_h01_0014']]
    o=object_for(d,'G_h01_0010')
    assert o['status']=='BOUNDED' and o['extent']==24
    assert a['object']==b['object'] and b['offset']==4
    assert d['derived']['private_view_overruns'][0]['declared_end']==44
    assert b['views'][0]['declared_extent']==24


@pytest.mark.parametrize('change',['count','stride'])
def test_source_domain_and_stride_are_rederived(change):
    f,c=record_case()
    if change=='count':
        f['sources']['src/a.c']=f['sources']['src/a.c'].replace('i<2','i<3')
    else:
        f['sources']['src/a.c']=f['sources']['src/a.c'].replace('flags[4]','flags[6]')
    with pytest.raises(FormatError):
        document(f,c)


def test_tu_local_struct_variants_survive_identical_tag_spelling():
    f=facts('struct R { int x; }; extern struct R G_h01_0010[1];')
    f['sources']['src/b.c']='struct R { long x; }; extern struct R G_h01_0010[1];'
    d=document(f)
    v=d['derived']['aliases']['G_h01_0010']
    assert len(v['views'])==2 and v['reinterpretation'] is True
    assert len(d['derived']['private_structs'])==2


def test_compatible_short_int_spellings_are_kept_without_type_pun_claim():
    f=facts('extern short G_h01_0010;')
    f['sources']['src/b.c']='extern int G_h01_0010;'
    a=document(f)['derived']['aliases']['G_h01_0010']
    assert len(a['views'])==2 and a['reinterpretation'] is False


def test_signed_unsigned_views_are_marked():
    f=facts('extern unsigned int G_h01_0010;')
    f['sources']['src/b.c']='extern int G_h01_0010;'
    assert document(f)['derived']['aliases']['G_h01_0010']['reinterpretation'] is True


def test_float_view_uses_manx_four_bytes():
    f=facts('extern float G_h01_0010;', {16:observed(4)})
    o=object_for(document(f),'G_h01_0010')
    assert o['extent']==4 and o['members'][0]['type']=='float'


def test_unknown_assembly_view_and_unparsed_view_are_visible():
    f=facts('extern strange G_h01_0010;')
    f['sources']['src/asm.s']=' public _G_h02_0000\n move.l _G_h02_0000,d0\n'
    d=document(f)
    assert d['derived']['aliases']['G_h01_0010']['views'][0]['type'].startswith('UNPARSED:')
    assert d['derived']['aliases']['G_h02_0000']['views'][0]['type']=='UNKNOWN'


def test_dependency_evidence_and_coallocation():
    f=facts('extern int G_h01_0010; extern int G_h01_0012; /* edge */',
            {16:observed(2),18:observed(2)})
    c=curation()
    c['dependencies']=[dict(symbols=['G_h01_0010','G_h01_0012'],coallocate=True,
        constraint='shared adjacent state',evidence=[dict(source='src/a.c',text='/* edge */')])]
    d=document(f,c)
    assert d['derived']['aliases']['G_h01_0010']['object']==d['derived']['aliases']['G_h01_0012']['object']
    f['sources']['src/a.c']=f['sources']['src/a.c'].replace('/* edge */','')
    with pytest.raises(FormatError,match='stale storage dependency'):
        document(f,c)


@pytest.mark.parametrize('target',['alias','view','gap','total'])
def test_validator_rejects_mechanical_tampering(target):
    f=facts('extern int G_h01_0010;', {16:observed(2)})
    d=document(f)
    if target=='alias':
        d['derived']['aliases']['G_h01_0010']['offset']=1
    elif target=='view':
        d['derived']['aliases']['G_h01_0010']['views']=[]
    elif target=='gap':
        d['derived']['objects'][0]['extent']=16
    else:
        d['derived']['summary']['bytes']['h1_DATA']['bounded']+=1
    with pytest.raises(FormatError,match='stale/modified'):
        dm.validate_storage_plan(d,facts=f)


def test_duplicate_keys_rejected_and_no_boolean_integer_substitution():
    with pytest.raises(FormatError,match='duplicate'):
        json.loads('{"derived":1,"derived":2}',object_pairs_hook=dm._unique_object)
    f=facts('extern char G_h01_0010;', {16:observed(1)})
    d=document(f)
    object_for(d,'G_h01_0010')['extent']=True
    with pytest.raises(FormatError):
        dm.validate_storage_plan(d,facts=f)


def test_bound_must_not_cross_region_and_unknown_has_no_fabricated_type():
    f,c=record_case()
    f['regions'][0]['end']=30
    with pytest.raises(FormatError,match='crosses resident region'):
        document(f,c)
    f=facts('extern int G_h01_0010[1]; recovered(i) int i; { G_h01_0010[i]=3; }')
    o=object_for(document(f),'G_h01_0010')
    assert o['extent'] is None and o['link_gap_bytes']==128
    assert not o['members']


def test_comment_only_names_do_not_become_storage():
    d=document(facts('/* extern int G_h01_0010; */\n// G_h01_0020\n'))
    assert not d['derived']['aliases']

def test_candidate_overlap_anchors_cannot_be_disconnected_by_authoritative_tail():
    f,c=record_case()
    f['sources']['src/a.c']+='\nextern int G_h01_002A;'
    f['widths'][42]=observed(2)
    d=document(f,c)
    assert d['derived']['aliases']['G_h01_0014']['object']==d['derived']['aliases']['G_h01_002A']['object']
    assert all(p['same_object'] for p in d['derived']['declared_overlap_candidates'])


def test_receiver_subobject_needs_allocation_size_and_direct_global_argument():
    f,c=record_case()
    c['bounds']=[]
    f['sources']['src/a.c']+='\nrecovered2() { draw(&G_h01_0010); alloc(12L); }'
    c['receiver_calls']=[dict(callee='draw',element_type='struct Plan',
        allocation=dict(source='src/a.c',pattern=r'alloc\((\d+)L\)'),
        consumer=dict(source='src/a.c',struct='Link'),
        evidence='direct typed receiver and independent allocation control')]
    assert object_for(document(f,c),'G_h01_0010')['members'][0]['basis']=='BOUNDED_RECEIVER_SUBOBJECT'
    f['sources']['src/a.c']=f['sources']['src/a.c'].replace('alloc(12L)','alloc(14L)')
    with pytest.raises(FormatError,match='allocation size'):
        document(f,c)

def test_quoted_names_and_comment_markers_are_not_data_references():
    f=facts('recovered() { char *s="http://G_h01_0010"; char c=\'x\'; }')
    assert not document(f)['derived']['aliases']


def test_receiver_consumer_layout_is_rederived():
    f,c=record_case()
    c['bounds']=[]
    f['sources']['src/a.c']+='\nrecovered2() { draw(&G_h01_0010); alloc(12L); }'
    c['receiver_calls']=[dict(callee='draw',element_type='struct Plan',
        allocation=dict(source='src/a.c',pattern=r'alloc\((\d+)L\)'),
        consumer=dict(source='src/a.c',struct='Link'),evidence='typed receiver')]
    f['sources']['src/a.c']=f['sources']['src/a.c'].replace('flags[4]','flags[6]')
    with pytest.raises(FormatError,match='consumer layout'):
        document(f,c)

def test_native_abi_names_share_mechanical_storage_without_a_second_allocation():
    f=facts('extern long G_h01_0010;', {16:observed(4)})
    c=curation()
    c['external_bindings']=[dict(native='_Base',mechanical='G_h01_0010',
        artifact='evidence/runtime.json',kind='RUNTIME_OPERAND_IDENTITY')]
    f['external_evidence']={'evidence/runtime.json':json.dumps(dict(
        symbol='_Base',kind='A4',original=[1,16],addend=0,width=2))}
    d=document(f,c)
    binding=d['derived']['external_bindings'][0]
    alias=d['derived']['aliases']['G_h01_0010']
    assert (binding['object'],binding['offset'])==(alias['object'],alias['offset'])
    assert object_for(d,'G_h01_0010')['extent']==4  # A4 operand width2 is not storage width.
    f['external_evidence']['evidence/runtime.json']=json.dumps([
        dict(symbol='_Base',kind='A4',original=[1,16],addend=0),
        dict(symbol='_Base',kind='A4',original=[1,20],addend=0)])
    with pytest.raises(FormatError,match='conflicting runtime slot'):
        document(f,c)


def test_startup_recipe_literal_is_read_without_executing_python():
    f=facts()
    c=curation()
    c['external_bindings']=[dict(native='__saved',mechanical='G_h01_0010',
        artifact='evidence/recipe.py',kind='STARTUP_RECIPE_SLOT')]
    f['external_evidence']={'evidence/recipe.py':
        'global_views=[("long","_saved","0010")]\nraise RuntimeError("must not execute")'}
    d=document(f,c)
    assert d['derived']['external_bindings'][0]['view_type']=='long'
    assert d['derived']['aliases']['G_h01_0010']['origin']=='IMPORTED_BINDING_ANCHOR'


def test_source_a4_equate_is_an_address_alias_and_bias_is_rederived():
    f=facts()
    f['sources']['src/a.asm']='_G_h01_0010_A4 equ -14\nlea _G_h01_0010_A4(a4),a0\n'
    f['a4_bias']=30
    d=document(f)
    assert d['derived']['address_equates'][0]['displacement']==-14
    assert object_for(d,'G_h01_0010')['extent'] is None
    f['a4_bias']=32
    with pytest.raises(FormatError,match='A4 source equate'):
        document(f)


def test_declared_only_names_are_retained_but_not_called_live_consumers():
    f=facts('extern int G_h01_0010; extern int G_h01_0020; recovered(){G_h01_0010=1;}')
    d=document(f)
    assert d['derived']['aliases']['G_h01_0010']['active_sources']==['src/a.c']
    assert d['derived']['aliases']['G_h01_0020']['active_sources']==[]

def test_indexed_cross_member_alias_is_rederived_and_coallocated():
    f=facts('extern char G_h01_0010[1]; extern char G_h01_0015; recovered(){G_h01_0010[5]=0;}')
    c=curation()
    c['indexed_aliases']=[dict(base='G_h01_0010',target='G_h01_0015',element_type='char',
        index=dict(source='src/a.c',pattern=r'G_h01_0010\[(\d+)\]=0'),
        evidence='five-byte interior alias')]
    d=document(f,c)
    edge=d['derived']['indexed_aliases'][0]
    assert edge['byte_offset']==5 and edge['width']==1
    assert d['derived']['aliases']['G_h01_0010']['object']==d['derived']['aliases']['G_h01_0015']['object']
    f['sources']['src/a.c']=f['sources']['src/a.c'].replace('[5]=0','[6]=0')
    with pytest.raises(FormatError,match='indexed alias address'):
        document(f,c)


def test_hex_index_capture_and_nonzero_runtime_addend_are_not_storage_extents():
    f=facts('recovered(){/* note */}',limit=256)
    f['sources']['src/a.asm']='cmp.b #$2c,d0\n'
    assert sp.capture(dict(source='src/a.asm',pattern=r'cmp.b #\$(2c),d0',radix=16),f)==44
    c=curation()
    c['external_bindings']=[dict(native='_Base',mechanical='G_h01_0010',
        artifact='evidence/runtime.json',kind='RUNTIME_OPERAND_IDENTITY')]
    f['external_evidence']={'evidence/runtime.json':json.dumps([
        dict(symbol='_Base',kind='A4',original=[1,16],addend=0),
        dict(symbol='_Base',kind='A4',original=[1,18],addend=2)])}
    assert document(f,c)['derived']['external_bindings'][0]['mechanical']=='G_h01_0010'


def test_storage_cli_runs_the_rederivation_entrypoint(monkeypatch,capsys):
    d=document(facts())
    monkeypatch.setattr(dm,'load_storage_plan',lambda:d)
    assert dm.main(['--check-storage-plan'])==0
    assert json.loads(capsys.readouterr().out)==d['derived']['summary']

def test_local_function_pointer_typedef_spelling_is_not_a_storage_dependency():
    f=facts('typedef void (*OtherName)(); OtherName G_h01_0010[3] = { 0,0,0 };')
    a=document(f)['derived']['aliases']['G_h01_0010']
    assert a['views'][0]['type']=='void (*)() [3]'
    assert a['views'][0]['declared_extent']==12
    assert object_for(document(f),'G_h01_0010')['extent'] is None


def test_assembly_comment_names_do_not_become_storage():
    f=facts()
    f['sources']['src/a.asm']='* _G_h01_0010\n; _G_h01_0020\n'
    assert not document(f)['derived']['aliases']

def test_read_only_proposal_rederives_stale_measurements_without_changing_curation():
    f=facts('extern int G_h01_0010;', {16:observed(2)})
    c=curation()
    before=copy.deepcopy(c)
    d=dm.derive_storage_plan(c,facts=f)
    dm.validate_storage_plan(d,facts=f)
    assert c==before
    f['sources']['src/a.c']+=' extern char G_h01_0020;'
    regenerated=dm.derive_storage_plan(c,facts=f)
    assert 'G_h01_0020' in regenerated['derived']['aliases']
    assert regenerated['curation']==before

def test_curated_scalar_interpretation_wins_without_erasing_private_views():
    f=facts('extern long G_h01_0010;', {16:observed(4)})
    f['model']['globals']['G_h01_0010']=dict(type='struct Entity *',extent=4,basis='CURATED',evidence='pointer consumers')
    d=document(f)
    assert object_for(d,'G_h01_0010')['members'][0]['type']=='struct Entity *'
    assert d['derived']['aliases']['G_h01_0010']['views'][0]['type']=='long'
    assert d['derived']['aliases']['G_h01_0010']['observed_access_widths']==[4]

def test_unknown_aggregate_has_explicit_gaps_between_retained_bounded_members():
    f=facts('extern long G_h01_0010[8]; extern int G_h01_0020;', {32:observed(2)})
    d=document(f)
    o=object_for(d,'G_h01_0010')
    assert o['status']=='UNBOUNDED' and o['extent'] is None
    assert o['known_member_bytes']==2 and o['unbounded_gap_bytes']==126
    assert [(g['start'],g['end'],g['limit']) for g in o['unbounded_gaps']]==[
        (0,32,'NEXT_BOUNDED_MEMBER'),(34,128,'NEXT_BOUNDED_OBJECT_OR_MEASURED_REGION_END')]
    assert o['known_member_bytes']+sum(g['bytes'] for g in o['unbounded_gaps'])==o['end']-o['start']
    total=d['derived']['summary']['bytes']['h1_DATA']
    assert total['bounded_member_union']+total['UNBOUNDED_gaps']==total['total']
