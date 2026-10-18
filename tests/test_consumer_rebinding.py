"""Consumer pin rebinding is conditional on an identical exact result."""
from copy import deepcopy
import json
from pathlib import Path
import sys

import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from common import FormatError, json_bytes, sha256
import consumer_rebinding as binding
import recovery_transaction as transaction


def proof():
    return dict(id='f',state='FUNCTION_CODE_MATCH',object_hash='a'*64,
        source='src/old.c',source_sha256='b'*64,evidence_extent=dict(hunk=3,start=0,end=2),
        comparison=dict(verdict='EQUAL',relocation_equal=True,relocation_issues=[],
                        expected_length=2,actual_length=2,expected_sha256='c'*64,normalized_sha256='c'*64),
        relocation_proof=[dict(kind='A4_D16_SYMBOL',expected=[1,4],offset=0)])


def put(root,name,value):
    path=root/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(json_bytes(value));return path


def test_identical_compiler_result_allows_different_source_and_provenance():
    old=proof();new=deepcopy(old)
    new.update(source='src/module.c#draw',source_sha256='d'*64,cache_key='different',regression={'passed':True})
    new['comparison']['actual_sha256']='a linked address can change'
    binding.require_identical(old,new)


@pytest.mark.parametrize('change', ['normalized','extent','bindings','relocations','length','verdict','missing_hash'])
def test_different_or_incomplete_compiled_result_refuses(change):
    old=proof();new=deepcopy(old)
    if change=='normalized':new['comparison'].update(expected_sha256='d'*64,normalized_sha256='d'*64)
    if change=='extent':new['evidence_extent']['end']=4
    if change=='bindings':new['relocation_proof'][0]['expected']=[1,6]
    if change=='relocations':new['comparison']['relocation_equal']=False
    if change=='length':new['comparison'].update(actual_length=4,expected_length=4)
    if change=='verdict':new['comparison']['verdict']='DIFFERENT'
    if change=='missing_hash':new.pop('object_hash')
    with pytest.raises(FormatError):binding.require_identical(old,new)


def test_object_metadata_alone_does_not_refuse():
    old=proof();new=deepcopy(old);new['object_hash']='d'*64
    binding.require_identical(old,new)


def test_owned_literal_tail_is_part_of_identity():
    old=proof();old['state']='FUNCTION_WITH_DATA_MATCH'
    old['comparison']['code_comparison']=deepcopy(old['comparison'])
    owned=dict(actual_tail_sha256='d'*64,expected_tail_sha256='d'*64,start=2,end=4)
    old['comparison']['owned_code_data']=old['data_ownership']=owned
    new=deepcopy(old);new['data_ownership']['actual_tail_sha256']=new['data_ownership']['expected_tail_sha256']='e'*64
    with pytest.raises(FormatError,match='compiled result differs'):binding.require_identical(old,new)


def test_pair_rebinding_follows_fact_digest_edges_and_regenerates_recipe_key(tmp_path):
    old=dict(source='src/old.c',source_sha256='a'*64,proof='recovery/proofs/f.json',proof_sha256='b'*64)
    new=dict(old,source='src/mod.c#draw',source_sha256='c'*64,proof_sha256='d'*64)
    name='evidence/data-providers/a.json'
    fact=dict(anchors={'f':dict(source=old['source'],source_sha256=old['source_sha256'],proof_sha256=old['proof_sha256'])})
    put(tmp_path,name,fact)
    recipe=dict(schema_version=1,members=[dict(fact=name,fact_sha256=sha256(json_bytes(fact)))],
                prefixes=['a'],profile='aztec36',commands=[],sources={},toolchain_inventory_sha256={},request_sha256='request')
    from data_providers import batch_key
    recipe['cache_key']=batch_key(recipe);put(tmp_path,'evidence/data-providers/producer.json',recipe)
    put(tmp_path,'evidence/other.json',dict(unrelated_hash='a'*64))
    index=binding.PinIndex(tmp_path);changed=index.changes(old,new)
    updated=changed[name]['anchors']['f']
    assert updated=={k:new[k] for k in ('source','source_sha256','proof_sha256')}
    updated_recipe=changed['evidence/data-providers/producer.json']
    assert updated_recipe['members'][0]['fact_sha256']==sha256(json_bytes(changed[name]))
    assert updated_recipe['cache_key']==batch_key(updated_recipe)!=recipe['cache_key']
    assert 'evidence/other.json' not in changed
    assert json.loads((tmp_path/name).read_bytes())==fact # staging is read-only


def test_unknown_consumer_proof_class_refuses(tmp_path):
    old=dict(source='src/a.c',source_sha256='a'*64,proof_sha256='b'*64,proof='recovery/proofs/f.json')
    put(tmp_path,'recovery/proofs/other.json',dict(anchor={k:old[k] for k in ('source_sha256','proof_sha256')}))
    index=binding.PinIndex(tmp_path)
    with pytest.raises(FormatError,match='no consumer-proof producer'):index.changes(old,dict(old,proof_sha256='c'*64))


def test_failed_replacement_restores_facts_proofs_source_and_ledger(tmp_path):
    ledger=put(tmp_path,'recovery/ledger.json',dict(functions={}))
    paths=[put(tmp_path,'evidence/fact.json',dict(pin='old')),
           put(tmp_path,'recovery/proofs/data/a.json',dict(pin='old'))]
    source=tmp_path/'src/module.c';source.parent.mkdir();source.write_bytes(b'old')
    paths.append(source);paths.append(ledger);before={p:p.read_bytes() for p in paths}
    def refuse():raise FormatError('strict final replay failed')
    with pytest.raises(FormatError,match='strict final replay'):
        with transaction.replacement_scope(tmp_path,ledger,refuse):
            transaction.publish(tmp_path,ledger,{p:b'new' for p in paths[:-1]},dict(functions={'f':{}}),sha256(ledger.read_bytes()))
            transaction.publish(tmp_path,ledger,{paths[0]:b'newer'},dict(functions={'f':{'next':True}}),sha256(ledger.read_bytes()))
    assert {p:p.read_bytes() for p in paths}==before
    assert not transaction.pending(ledger)


def test_interrupted_replacement_restores_even_after_intermediate_ledger_commit(tmp_path):
    ledger=put(tmp_path,'recovery/ledger.json',dict(functions={}))
    fact=put(tmp_path,'evidence/fact.json',dict(pin='old'));before={p:p.read_bytes() for p in (ledger,fact)}
    with transaction.ledger_lock(ledger):
        job=transaction.ReplacementTransaction(tmp_path,ledger)
        job.publish({fact:b'changed'},dict(functions={'f':{}}),sha256(ledger.read_bytes()))
    assert transaction.recover(ledger,job.id)=='ROLLED_BACK'
    assert {p:p.read_bytes() for p in (ledger,fact)}==before


def test_refused_identity_changes_no_canonical_files(tmp_path):
    ledger_path=put(tmp_path,'recovery/ledger.json',dict(functions={}))
    old=proof();p=put(tmp_path,'recovery/proofs/f.json',old)
    prior=dict(source=old['source'],source_sha256=old['source_sha256'],proof='recovery/proofs/f.json',proof_sha256=sha256(p.read_bytes()))
    new=deepcopy(old);new['comparison'].update(expected_sha256='d'*64,normalized_sha256='d'*64)
    before={x:x.read_bytes() for x in (ledger_path,p)}
    with pytest.raises(FormatError,match='compiled result differs'):
        binding.publish(tmp_path,ledger_path,{p:json_bytes(new)},dict(functions={'f':prior}),prior,new)
    assert {x:x.read_bytes() for x in before}==before
    assert not (tmp_path/'build/promotion-transactions').exists()


def test_module_snapshot_does_not_write_source(tmp_path,monkeypatch):
    ledger=put(tmp_path,'recovery/ledger.json',dict(functions={}))
    source=tmp_path/'src/a.c';source.parent.mkdir();source.write_bytes(b'int draw(){return 0;}')
    real=transaction.replace_bytes;written=[]
    def record(path,data):
        written.append(Path(path));return real(path,data)
    monkeypatch.setattr(transaction,'replace_bytes',record)
    with transaction.replacement_scope(tmp_path,ledger,lambda:None) as job:
        job.snapshot([source])
        transaction.publish(tmp_path,ledger,{},dict(functions={'f':{}}),sha256(ledger.read_bytes()))
    assert source not in written
    journal=json.loads((job.directory/'journal.json').read_bytes())
    assert any(e['path']=='src/a.c' for e in journal['files'])


@pytest.mark.parametrize('different_data',[False,True])
def test_data_proof_is_rederived_and_changed_data_rolls_back(tmp_path,monkeypatch,different_data):
    import data_providers, census, game_image
    old=proof();old_path=put(tmp_path,'recovery/proofs/f.json',old)
    prior={k:old[k] for k in ('source','source_sha256','state','evidence_extent')}
    prior.update(proof='recovery/proofs/f.json',proof_sha256=sha256(old_path.read_bytes()))
    fact_name='evidence/data-providers/cell.json'
    fact=dict(id='cell',source='src/data.c',anchors={'f':{k:prior[k] for k in ('source_sha256','proof_sha256')}},
              producer=dict(batch='evidence/data-providers/producer.json',prefix='cell'))
    put(tmp_path,fact_name,fact)
    recipe=dict(schema_version=1,members=[dict(fact=fact_name,fact_sha256=sha256(json_bytes(fact)))],
                prefixes=['cell'],profile='aztec36',commands=[],sources={},toolchain_inventory_sha256={},request_sha256='request')
    recipe['cache_key']=data_providers.batch_key(recipe)
    put(tmp_path,'evidence/data-providers/producer.json',recipe)
    previous=dict(object_sha256='e'*64,actual_sha256='e'*64,source_sha256='e'*64,typed_evidence=[fact['anchors']])
    dp=put(tmp_path,'recovery/proofs/data/cell.json',dict(fact=fact,comparison=previous,regression=dict(passed=True)))
    put(tmp_path,'evidence/functions/ledger.json',dict(functions=[]))
    data_source=tmp_path/'src/data.c';data_source.parent.mkdir();data_source.write_bytes(b'int cell=0;')
    module=tmp_path/'src/module.c';module.write_bytes(b'int draw(){return 0;}')
    entry=dict(fact=fact_name,source='src/data.c',source_sha256=sha256(data_source.read_bytes()),
               proof='recovery/proofs/data/cell.json',proof_sha256=sha256(dp.read_bytes()))
    ledger_path=put(tmp_path,'recovery/ledger.json',dict(functions={'f':prior},data_providers={'cell':entry}))
    new=deepcopy(old);new.update(source='src/module.c#draw',source_sha256='d'*64)
    accepted=dict(prior,source=new['source'],source_sha256=new['source_sha256'],proof_sha256=sha256(json_bytes(new)))
    ledger=dict(functions={'f':accepted},data_providers={'cell':deepcopy(entry)})
    before={x:x.read_bytes() for x in tmp_path.rglob('*') if x.is_file()}
    calls=[]
    def verify(root,blob,model,analysis,current,promotions,current_fact,src,retained):
        assert current_fact['anchors']['f']=={k:accepted[k] for k in ('source_sha256','proof_sha256')}
        assert json.loads((root/fact_name).read_bytes())==current_fact
        assert src==b'int cell=0;' and promotions==[{'id':'f'}]
        calls.append(current_fact)
        result=dict(previous,typed_evidence=[current_fact['anchors']])
        if different_data:result['actual_sha256']='f'*64
        return result
    monkeypatch.setattr(data_providers,'verify',verify)
    monkeypatch.setattr(game_image,'game',lambda:(b'',{},None))
    strict=[]
    def replay(root,promotion_evidence):
        assert promotion_evidence is True
        proof_now=json.loads(dp.read_bytes());ledger_now=json.loads(ledger_path.read_bytes())
        assert proof_now['fact']==calls[0] and proof_now['comparison']['typed_evidence']==[calls[0]['anchors']]
        assert ledger_now['data_providers']['cell']['proof_sha256']==sha256(dp.read_bytes())
        strict.append(True)
    monkeypatch.setattr(census,'derive',replay)
    if different_data:
        with pytest.raises(FormatError,match='DATA compiled result changed'):
            binding.publish(tmp_path,ledger_path,{old_path:json_bytes(new)},ledger,prior,new)
        assert {x:x.read_bytes() for x in before}==before
        assert strict==[]
    else:
        binding.publish(tmp_path,ledger_path,{old_path:json_bytes(new)},ledger,prior,new)
        assert strict==[True]
    assert len(calls)==1
