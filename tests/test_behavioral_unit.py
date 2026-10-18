"""Synthetic mixed units: behavioral claims never confer exact credit."""
import copy
from pathlib import Path
import sys
from unittest.mock import patch

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import behavioral
import check_unit
from common import FormatError, json_bytes, sha256


@pytest.fixture
def mixed(tmp_path):
    # The middle member has a branch crossing its widening. Exact members
    # on either side call it, discard the byte return, then redefine D0.
    raws = ['61081b40ffff70004e75', '6004102dfffe4e5d4e75', '4ebafff470004e75']
    starts = [0x100, 0x10a, 0x114]
    members=[]
    for start,raw in zip(starts, raws):
        members.append(dict(id='ov09_F_%04X'%start,hunk=9,start=start,end=start+len(raw)//2,
                            size=len(raw)//2,raw_bytes=raw,sha256=sha256(bytes.fromhex(raw)),
                            extent_status='CLOSED_CFG',referenced_data=[],relocations=[],direct_callees=[]))
    a,b,c=members
    a['direct_callees']=[dict(id=b['id'],hunk=9,offset=b['start'],site=a['start'],basis='PC_RELATIVE')]
    c['direct_callees']=[dict(id=b['id'],hunk=9,offset=b['start'],site=c['start'],basis='PC_RELATIVE')]
    b['callers']=[dict(id=a['id'],site=a['start']),dict(id=c['id'],site=c['start'])]
    analysis=dict(functions=members)
    source=b'char recovered() { return 1; }\n'
    source_name='src/recovered/member.c'
    (tmp_path/source_name).parent.mkdir(parents=True)
    (tmp_path/source_name).write_bytes(source)
    deletions=[dict(offset=6,raw='4880',mnemonic='ext.w',operands='d0')]
    proof=dict(id=b['id'],state=behavioral.STATE,profile='aztec36',source_sha256=sha256(source),
               original=behavioral._extent(b),deletions=deletions,candidate_length=12,
               byte_only_callers=behavioral.byte_only_callers(b,members),regression=dict(passed=True),
               reduced_comparison=dict(verdict='EQUAL',relocation_equal=True,relocation_issues=[],
                                       normalized_sha256=b['sha256'],expected_sha256=b['sha256']))
    proof_name=behavioral.PROOFS+b['id']+'.json'
    (tmp_path/proof_name).parent.mkdir(parents=True)
    (tmp_path/proof_name).write_bytes(json_bytes(proof))
    item=dict(state=behavioral.STATE,source=source_name,source_sha256=sha256(source),proof=proof_name,
              proof_sha256=sha256(json_bytes(proof)),evidence_extent=behavioral._extent(b))
    ledger=dict(functions={},behavioral_functions={b['id']:item})
    (tmp_path/'candidate.exe').write_bytes(bytes(64))
    code=a['raw_bytes']+'6006102dfffe48804e5d4e75'+'4ebafff270004e75'
    compiled=dict(status='COMPILED',identity=dict(profile='aztec36',flags=[]),cache_key='synthetic',cache_hit=True,
                  directory=str(tmp_path),prefix='candidate',contribution=dict(
                      entry_offset=0,code_hex=code,code_size=len(code)//2,code_offset=0,hunk=3,data_size=0,bss_size=0,
                      relocations=[],all_relocations=[],object_sha256='synthetic',
                      symbols=[dict(hunk=3,name=n,offset=o) for n,o in
                               [('_recovered',0),('_F_h09_010A',10),('_F_h09_0114',22)]],
                      hunks=[dict(number=0,content_offset=0),dict(number=1,initialized_size=0,allocated_size=0),
                             dict(number=2,allocated_size=0)]))
    names={a['id']:'recovered',b['id']:'F_h09_010A',c['id']:'F_h09_0114'}
    def compare(value=None):
        with patch('function_compare.ROOT',tmp_path):
            return check_unit.compare_unit(members,names,value or compiled,32766,source_text='',
                                           context=dict(root=tmp_path,ledger=ledger,analysis=analysis))
    return dict(compare=compare,compiled=compiled,members=members,ledger=ledger,root=tmp_path,proof=proof)


def test_behavioral_and_exact_members_accepted_separately(mixed):
    report=mixed['compare']()
    assert report['verdict']=='ACCEPTED_WITH_BEHAVIORAL'
    assert [m['verdict'] for m in report['members']]==['EQUAL','BEHAVIORAL_EQUAL','EQUAL']
    assert report['members'][1]['proof_level'] is None
    assert report['normalized_sha256'] is None
    assert report['unclaimed_bytes']==0
    assert report['exact_members']==[mixed['members'][i]['id'] for i in (0,2)]
    assert report['accepted_exact_members']==report['exact_members']


@pytest.mark.parametrize('old,new',[('102dfffe','102dfffc'),('102dfffe','302dfffe'),('4880','4e71')])
def test_non_widening_difference_in_behavioral_member_rejects(mixed,old,new):
    c=copy.deepcopy(mixed['compiled'])
    c['contribution']['code_hex']=c['contribution']['code_hex'].replace(old,new)
    assert mixed['compare'](c)['verdict']=='DIFFER'


def test_exact_member_difference_rejects_whole_unit(mixed):
    c=copy.deepcopy(mixed['compiled'])
    c['contribution']['code_hex']=c['contribution']['code_hex'].replace('70004e75','70014e75',1)
    report=mixed['compare'](c)
    assert report['verdict']=='DIFFER'
    assert [m['verdict'] for m in report['members']]==['DIFFER','BEHAVIORAL_EQUAL','EQUAL']
    assert report['accepted_exact_members']==[]


def test_extra_instruction_or_wrong_partition_rejects(mixed):
    c=copy.deepcopy(mixed['compiled'])
    c['contribution']['code_hex']+='4e71'
    assert mixed['compare'](c)['reason']=='COMPLETE_UNIT_SIZE_DIFFERS'
    c=copy.deepcopy(mixed['compiled'])
    c['contribution']['symbols'][-1]['offset']-=2
    with pytest.raises(FormatError,match='ordering/extent'):
        mixed['compare'](c)


def test_behavioral_member_is_not_an_exact_promotion(mixed):
    report=mixed['compare']()
    behavioral_id=report['behavioral_members'][0]
    with patch('check_unit.promote') as promote:
        # The behavioral member itself can never be promoted as exact C.
        with pytest.raises(FormatError,match='never promoted as exact'):
            check_unit.promote_unit_members(behavioral_id,'',{},mixed['members'],report,{},{},'FUNCTION_CODE_MATCH')
        # Any differing exact member blocks the whole promotion.
        broken=copy.deepcopy(report)
        exact=next(m for m in broken['members'] if m['id']!=behavioral_id)
        exact['verdict']='DIFFER'
        with pytest.raises(FormatError,match='every exact member EQUAL'):
            check_unit.promote_unit_members(exact['id'],'',{},mixed['members'],broken,{},{},'FUNCTION_CODE_MATCH')
        promote.assert_not_called()


def test_behavioral_source_or_caller_claim_changes_reject(mixed):
    item=next(iter(mixed['ledger']['behavioral_functions'].values()))
    (mixed['root']/item['source']).write_text('changed')
    with pytest.raises(FormatError,match='source/proof binding'):
        mixed['compare']()


def test_profile_uses_hash_bound_behavioral_proof(mixed):
    fid=mixed['members'][1]['id']
    with patch('check_unit.verification_root',return_value=mixed['root']):
        profile=check_unit.canonical_member_profile(fid,mixed['ledger'])
    assert profile['profile']=='aztec36'


def test_changed_caller_use_rejects_recorded_claim(mixed):
    mixed['members'][0]['raw_bytes']='61083b40fffe70004e75'
    with pytest.raises(FormatError,match='reads widened D0 bits'):
        mixed['compare']()


def test_unrecorded_widening_is_not_accepted_as_exact(mixed):
    mixed['ledger']['behavioral_functions'].clear()
    report=mixed['compare']()
    assert report['verdict']=='DIFFER'
    assert report['reason']=='COMPLETE_UNIT_SIZE_DIFFERS'


def test_preparation_loads_canonical_behavioral_source(mixed):
    members=mixed['members']
    analysis=dict(functions=members,a4=dict(bias=32766))
    def validated(fid):
        return next(m for m in members if m['id']==fid),analysis
    with patch('check_unit.validated_function',side_effect=validated), \
         patch('check_unit.recovery',return_value=mixed['ledger']), \
         patch('check_unit.verification_root',return_value=mixed['root']), \
         patch('check_unit.proven_object_members',return_value=[]):
        prepared=check_unit.prepare_unit(members[0]['id'],'recovered() {}',True,local_calls_only=True)
        assert [m['id'] for m in prepared[0]]==[m['id'] for m in members[:2]]
        assert 'F_h09_010A()' in prepared[2][members[1]['id']]
        with pytest.raises(FormatError,match='canonical ledger sources'):
            check_unit.prepare_unit(members[0]['id'],'recovered() {}',True,
                                    member_sources={members[1]['id']:'char recovered() {}'})


def test_wrong_call_binding_in_exact_member_rejects(mixed):
    c=copy.deepcopy(mixed['compiled'])
    c['contribution']['code_hex']=c['contribution']['code_hex'].replace('4ebafff2','4ebaffe8')
    report=mixed['compare'](c)
    assert report['verdict']=='DIFFER'
    assert report['members'][2]['verdict']=='DIFFER'
    assert report['accepted_exact_members']==[]


def test_unproven_relocation_in_behavioral_member_rejects(mixed):
    c=copy.deepcopy(mixed['compiled'])
    c['contribution']['relocations']=[dict(relative_offset=12,width=4,type='HUNK_RELOC32',target_hunk=1,addend_raw=0)]
    report=mixed['compare'](c)
    assert report['verdict']=='DIFFER'
    assert report['members'][1]['reduced_comparison']['relocation_equal'] is False


def test_recorded_deletion_locations_must_replay(mixed):
    item=next(iter(mixed['ledger']['behavioral_functions'].values()))
    proof=copy.deepcopy(mixed['proof'])
    proof['deletions'][0]['offset']=4
    raw=json_bytes(proof)
    (mixed['root']/item['proof']).write_bytes(raw)
    item['proof_sha256']=sha256(raw)
    report=mixed['compare']()
    assert report['verdict']=='DIFFER'
    assert 'deletions differ from recorded claim' in report['members'][1]['reason']


def test_behavioral_dependencies_keep_mechanical_library_bindings(mixed):
    members=mixed['members']
    target=dict(members[0],node='ov09')
    names={m['id']:('recovered' if i==0 else check_unit.mechanical_name(m)) for i,m in enumerate(members)}
    parts={m['id']:'recovered() {}' for m in members}
    with patch('check_unit.validated_function',return_value=(target,{})), \
         patch('check_unit.recovery',return_value=mixed['ledger']), \
         patch('check_unit.unit_export_roots',return_value=None), \
         patch('check_unit.external_stand_in_source',return_value=('recovered() {}',{})), \
         patch('mixed_object_dependencies.derive',return_value=[]), \
         patch('runtime_member_routes.derive',return_value=[]) as routes, \
         patch('helper_exports.original_helpers',return_value=()):
        check_unit.unit_trials(target['id'],members,names,parts,'recovered() {}',
                               ['aztec36'],True,False,None)
    assert [m['id'] for m in routes.call_args.args[0]]==[members[i]['id'] for i in (0,2)]


@pytest.fixture
def accepted_object(mixed):
    """A hash-bound accepted object with exact/behavioral/exact members."""
    root=mixed['root'];members=mixed['members'];ledger=mixed['ledger']
    report=mixed['compare']();entry=members[0]['id']
    hashes={m['id']:sha256(m['id'].encode()) for m in members}
    hashes[members[1]['id']]=ledger['behavioral_functions'][members[1]['id']]['source_sha256']
    report.update(id=entry,ordered_members=members,source_sha256=hashes[entry],
                  member_sources={m['id']:hashes[m['id']] for m in (members[0],members[2])},
                  dependency_sources={members[1]['id']:hashes[members[1]['id']]})
    receipt='recovery/units/group/receipt.json'
    (root/receipt).parent.mkdir(parents=True)
    def save():
        raw=json_bytes(report);(root/receipt).write_bytes(raw)
        for m in (members[0],members[2]):
            proof='recovery/proofs/'+m['id']+'.json'
            (root/proof).parent.mkdir(parents=True,exist_ok=True)
            (root/proof).write_bytes(json_bytes(dict(comparison=dict(complete_unit_receipt=receipt,
                                                                    complete_unit_receipt_sha256=sha256(raw)))))
            ledger['functions'][m['id']]=dict(state='FUNCTION_CODE_MATCH',proof=proof,source_sha256=hashes[m['id']])
    save()
    return dict(mixed,receipt=report,save=save)


def test_accepted_behavioral_object_group_is_preserved(accepted_object):
    obj=accepted_object;members=obj['members'];ids=[m['id'] for m in members]
    with patch('check_unit.verification_root',return_value=obj['root']):
        assert check_unit.proven_object_members(ids[0],obj['ledger'])==ids[1:]
        assert check_unit.proven_unit_groups(members,set(),obj['ledger'])==([ids],[])
    # Grouping never changes the behavioral member's exactness category.
    assert obj['compare']()['verdict']=='ACCEPTED_WITH_BEHAVIORAL'
    assert obj['compare']()['behavioral_members']==[ids[1]]


@pytest.mark.parametrize('mutation',['changed_source','missing_behavioral','differ','changed_receipt','missing_member'])
def test_accepted_behavioral_object_group_rejects_changed_inputs(accepted_object,mutation):
    obj=accepted_object;members=obj['members'];ids=[m['id'] for m in members]
    if mutation=='changed_source':obj['ledger']['behavioral_functions'][ids[1]]['source_sha256']='0'*64
    elif mutation=='missing_behavioral':obj['ledger']['behavioral_functions'].clear()
    elif mutation=='differ':obj['receipt']['verdict']='DIFFER';obj['save']()
    elif mutation=='changed_receipt':obj['receipt']['extra']='changed';(obj['root']/'recovery/units/group/receipt.json').write_bytes(json_bytes(obj['receipt']))
    else:members=members[:2]
    with patch('check_unit.verification_root',return_value=obj['root']):
        assert check_unit.proven_unit_groups(members,set(),obj['ledger'])[0]==[]
        if mutation!='missing_member':assert check_unit.proven_object_members(ids[0],obj['ledger'])==[]


def test_root_slot_export_pc_jsr_proves_whole_contiguous_object():
    a=dict(id='resident_F_0100',hunk=0,start=0x100,end=0x104,direct_callees=[],instructions=[])
    middle=dict(id='resident_F_0104',hunk=0,start=0x104,end=0x108,direct_callees=[],instructions=[])
    b=dict(id='resident_F_0108',hunk=0,start=0x108,end=0x10c,
           direct_callees=[dict(id=a['id'],hunk=0,offset=0x100,site=0x108,basis='PC_RELATIVE')],
           instructions=[dict(offset=0x108,mnemonic='jsr')])
    caller=dict(id='resident_F_0200',hunk=0,start=0x200,end=0x204,
                direct_callees=[dict(id=a['id'],hunk=0,offset=0x100,site=0x200,basis='A4_RELOCATED_JMP_STUB')],instructions=[])
    members=[a,middle,b,caller];ids=[m['id'] for m in members]
    ledger=dict(functions={i:dict(source_sha256=sha256(i.encode())) for i in ids})
    assert check_unit.resident_slot_pairs(members)==[(b,a)]
    with patch('check_unit.proven_tail',return_value=(b'',None)):
        assert check_unit.proven_unit_groups(members,{caller['id']},ledger)==([ids[:3]],[])
        with pytest.raises(FormatError,match='unowned gaps'):
            check_unit.proven_unit_groups([a,b,caller],{caller['id']},ledger)
    caller['direct_callees'].clear()
    assert check_unit.resident_slot_pairs(members)==[]


def test_root_slot_pc_jsr_closure_keeps_intervening_canonical_members():
    # Even when original-gap compaction is otherwise permitted, the local
    # object's intervening member cannot be omitted from its source object.
    def f(start):
        return dict(id='resident_F_%04X'%start,hunk=0,node='resident',start=start,end=start+2,
                    direct_callees=[],instructions=[])
    a,mid,b,entry=[f(x) for x in (0x100,0x102,0x104,0x200)]
    b.update(direct_callees=[dict(id=a['id'],hunk=0,offset=a['start'],site=b['start'],basis='PC_RELATIVE')],
             instructions=[dict(offset=b['start'],mnemonic='jsr')])
    entry['direct_callees']=[dict(id=b['id'],hunk=0,offset=b['start'],site=entry['start'],basis='PC_RELATIVE'),
                              dict(id=a['id'],hunk=0,offset=a['start'],site=entry['start']+4,basis='A4_RELOCATED_JMP_STUB')]
    members=[a,mid,b,entry];text='recovered() {}\n'
    ledger=dict(functions={m['id']:dict(source='synthetic.c',source_sha256=sha256(text.encode())) for m in members[:-1]})
    analysis=dict(functions=members,a4=dict(bias=32766))
    def validated(fid):return next(m for m in members if m['id']==fid),analysis
    with patch('check_unit.validated_function',side_effect=validated),patch('check_unit.recovery',return_value=ledger), \
         patch('check_unit.read_source_text',return_value=text), \
         patch('check_unit.proven_object_members',return_value=[]):
        prepared=check_unit.prepare_unit(entry['id'],text,True,allow_gaps=True)
    assert [m['id'] for m in prepared[0]]==[m['id'] for m in members]
