"""Module references select exact compile units without duplicating sources."""
import json
from pathlib import Path
import pytest
import names
from common import FormatError, sha256


@pytest.fixture
def module_tree(tmp_path):
    (tmp_path/'src').mkdir()
    (tmp_path/'recovery').mkdir()
    (tmp_path/'recovery/names.json').write_text(json.dumps(dict(schema_version=1,
        functions={'ov07_F_0100':dict(name='draw_scene'), 'ov07_F_0200':dict(name='load_scene')},
        globals={'G_h01_0010':dict(name='scene_state')})))
    yield tmp_path
    names.load_registry.cache_clear(); names._maps.cache_clear()


def test_extracts_shared_prefix_definition_and_comment(module_tree):
    root=module_tree
    shared='/* Readability module, not a historical TU. */\nstruct View { int n; };\nextern int scene_state;\nextern int draw_scene();\nextern int load_scene();\n\n'
    first='/* Draw the scene. */\ndraw_scene(n)\nint n;\n{\n    char *s="} draw_scene"; /* { */\n    if(n) { return draw_scene(n-1); }\n    return load_scene(scene_state);\n}\n'
    second='/* Load the scene. */\nint load_scene(void) { return scene_state; }\n'
    (root/'src/scenes.c').write_bytes((shared+first+'\n'+second).encode())
    raw=names.read_source(root,'src/scenes.c#draw_scene')
    expected=names.translate(names.to_mechanical(shared+first,root),{'F_h07_0100':'recovered'}).encode()
    assert raw==expected
    assert b'"} draw_scene"' in raw
    assert b'return recovered(n-1)' in raw
    assert b'F_h07_0200(G_h01_0010)' in raw
    assert b'Load the scene' not in raw
    assert names.read_source(root,'src/scenes.c#load_scene') == names.translate(
        names.to_mechanical(shared+second,root),{'F_h07_0200':'recovered'}).encode()


def test_plain_paths_preserve_bytes_and_translation(module_tree):
    raw=b'/* draw_scene */\r\nint recovered() { return scene_state; }\r\n'
    path=module_tree/'src/one.c';path.write_bytes(raw)
    assert names.read_source(module_tree,'src/one.c')==names.to_mechanical(raw,module_tree)
    assert names.read_source(module_tree,path)==names.to_mechanical(raw,module_tree)


def test_unknown_name_refused(module_tree):
    (module_tree/'src/a.c').write_text('int draw_scene() { return 0; }\n')
    with pytest.raises(ValueError,match='unknown module function'):
        names.read_source(module_tree,'src/a.c#missing')


@pytest.mark.parametrize('source,reason',[
    ('int f() {}\nint f() {}\n','duplicate'),
    ('int f() {}\nextern int x;\nint g() {}\n','between'),
    ('int f() {}\nint x;\n','after'),
    ('int f() {','unbalanced'),
    ('#if FLAG\nint f() {}\n#endif\n','conditionals'),
])
def test_ambiguous_module_shapes_refused(source,reason):
    with pytest.raises(ValueError,match=reason):names.module_parts(source)


@pytest.mark.parametrize('ref',['src/a.c#','src/a.c#two#names','src/a.c#9bad','#f'])
def test_invalid_reference_refused(ref):
    with pytest.raises(ValueError,match='invalid source reference'):names.split_source_ref(ref)


def test_module_path_checks_preserve_canonical_and_scratch_boundary(module_tree):
    root=module_tree
    for directory in ('build','to_delete'):
        (root/directory).mkdir()
        (root/directory/'a.c').write_text('int draw_scene() { return 0; }\n')
    with pytest.raises(FormatError):names.read_source(root,'build/a.c#draw_scene')
    assert b'recovered()' in names.read_source(root,'build/a.c#draw_scene',scratch=True)
    with pytest.raises(FormatError):names.read_source(root,'to_delete/a.c#draw_scene',scratch=True)
    with pytest.raises(FormatError):names.source_path(root,'../outside.c#draw_scene',scratch=True)


def test_module_changes_invalidate_selected_unit_hash(module_tree):
    path=module_tree/'src/a.c'
    path.write_text('extern int scene_state;\n\n/* Draw. */\nint draw_scene() {return scene_state;}\n\n/* Load. */\nint load_scene() {return 1;}\n')
    ref='src/a.c#draw_scene';before=names.read_source(module_tree,ref)
    path.write_text(path.read_text().replace('return 1','return 2'))
    assert names.read_source(module_tree,ref)==before
    path.write_text(path.read_text().replace('extern int','extern long'))
    assert sha256(names.read_source(module_tree,ref))!=sha256(before)


@pytest.fixture
def publisher(module_tree,monkeypatch):
    import check_function as check
    from contextlib import nullcontext
    root=module_tree
    monkeypatch.setattr(check,'ROOT',root)
    monkeypatch.setattr(check,'LEDGER',root/'recovery/ledger.json')
    state=dict(functions={},blockers={})
    monkeypatch.setattr(check,'recovery',lambda: state)
    monkeypatch.setattr(check,'write_recovery',lambda value,path: path.write_text(json.dumps(value)))
    monkeypatch.setattr(check,'ledger_lock',lambda path:nullcontext())
    monkeypatch.setattr(check,'durable_unit',lambda report:report)
    path=root/'src/scenes.c';path.write_bytes(b'/* Draw. */\nint draw_scene() { return scene_state; }\n')
    ref='src/scenes.c#draw_scene'
    function=dict(id='ov07_F_0100',node='ov07',hunk=7,start=256,end=260,size=4,
        sha256='original',extent_status='CLOSED_CFG',direct_callees=[])
    compiled=dict(identity=dict(profile='aztec36'),contribution=dict(object_sha256='object'),artifacts={},cache_key='cache')
    # promotion_proof hashes the tools as provenance; fake only that metadata
    # constructor so these publisher tests do not depend on a real repo clone.
    def proof(fid,source,report,compiled,f,state,gate,canonical_ref=None):
        return dict(id=fid,state=state,source=canonical_ref or 'src/one.c',source_sha256=sha256(source.encode()),
            evidence_extent={k:f[k] for k in ('hunk','start','end','size','sha256','extent_status')},
            compiler_selection='test',regression=gate)
    monkeypatch.setattr(check,'promotion_proof',proof)
    return check,root,path,ref,function,compiled


def test_publisher_binds_module_ref_without_writing_source(publisher):
    check,root,path,ref,function,compiled=publisher
    before=path.read_bytes();unit=names.read_source(root,ref).decode()
    item=check.promote(function['id'],unit,{},compiled,function,
        regression=dict(passed=True),canonical_ref=ref)
    assert path.read_bytes()==before
    assert item['source']==ref
    assert item['source_sha256']==sha256(unit.encode())
    assert not (root/'src/recovered').exists()


def test_publisher_refuses_unverified_module_text_before_writes(publisher):
    check,root,path,ref,function,compiled=publisher
    before=path.read_bytes()
    with pytest.raises(FormatError,match='differs from verified candidate'):
        check.promote(function['id'],'int recovered(){return 9;}\n',{},compiled,function,
            regression=dict(passed=True),canonical_ref=ref)
    assert path.read_bytes()==before
    assert not (root/'recovery/proofs').exists()
    assert not (root/'recovery/ledger.json').exists()


def test_publisher_refuses_another_function_name(publisher):
    check,root,path,ref,function,compiled=publisher
    path.write_bytes(path.read_bytes()+b'\nint load_scene() { return 0; }\n')
    ref='src/scenes.c#load_scene'
    with pytest.raises(FormatError,match='does not identify'):
        check.promote(function['id'],names.read_source(root,ref).decode(),{},compiled,function,
            regression=dict(passed=True),canonical_ref=ref)


@pytest.mark.parametrize('foreign_edit',[False,True])
def test_replacement_rolls_back_physical_module_file(module_tree,monkeypatch,foreign_edit):
    import check_function as check
    import canonical_replacement as replacement
    root=module_tree;path=root/'src/scenes.c';path.write_bytes(b'int draw_scene(){return 0;}\n')
    proof=root/'recovery/proofs/a.json';proof.parent.mkdir();proof.write_text('{}')
    ledger=root/'recovery/ledger.json';ledger.write_text('{}')
    state=dict(functions={'f':dict(source='src/scenes.c#draw_scene',proof='recovery/proofs/a.json')})
    monkeypatch.setattr(replacement,'ROOT',root)
    monkeypatch.setattr(check,'LEDGER',ledger)
    monkeypatch.setattr(check,'recovery',lambda:state)
    monkeypatch.setattr(replacement,'closure',lambda fid,state:{})
    before={p:p.read_bytes() for p in (path,proof,ledger)}
    def failed(gate):
        from recovery_transaction import publish,digest
        publish(root,ledger,{path:b'changed',proof:b'changed'},dict(functions={}),digest(ledger))
        if foreign_edit:path.write_bytes(b'foreign edit')
        raise ValueError('publication failed')
    error=FormatError if foreign_edit else ValueError
    message='conflicts with a later edit' if foreign_edit else 'publication failed'
    with pytest.raises(error,match=message):
        replacement.replace('f',failed,regression=dict(passed=True))
    if foreign_edit:
        from recovery_transaction import pending,recover
        assert path.read_bytes()==b'foreign edit'
        # Resolve the simulated external edit before explicit recovery.
        path.write_bytes(b'changed')
        recover(ledger,pending(ledger)[0])
    assert {p:p.read_bytes() for p in before}==before



def test_text_adapter_preserves_plain_read_text_semantics(module_tree):
    path=module_tree/'src/one.c';path.write_bytes(b'int recovered() {return scene_state;}\r\n')
    assert names.read_source_text(module_tree,path)=='int recovered() {return G_h01_0010;}\n'


def test_comments_inside_strings_do_not_steal_next_summary():
    source='int first() {char *s="/*";}\n\n/* Second. */\nint second() {return 2;}\n'
    shared,parts=names.module_parts(source)
    assert not shared
    assert parts['second']=='/* Second. */\nint second() {return 2;}\n'


def test_module_inventory_keeps_object_boundaries_and_rejects_stale_proofs(module_tree):
    import copy
    import game_build
    root=module_tree
    ref='src/scenes.c#draw_scene'
    (root/'src/scenes.c').write_bytes(b'int draw_scene() {return 0;}\n')
    extent=dict(hunk=7,start=256,end=260)
    proof=dict(id='ov07_F_0100',source=ref,source_sha256=sha256(names.read_source(root,ref)),
        state='FUNCTION_CODE_MATCH',evidence_extent=extent,compiler=dict(profile='aztec36'),
        comparison=dict(verdict='EQUAL'),regression=dict(passed=True))
    proof_path=root/'recovery/proof.json';proof_path.write_bytes(json.dumps(proof).encode())
    accepted={k:proof[k] for k in ('source','source_sha256','state','evidence_extent')}
    accepted.update(proof='recovery/proof.json',proof_sha256=sha256(proof_path.read_bytes()))
    inv=dict(sources=[dict(id=proof['id'],ledger_map='functions',source='src/old.c',
        hunk=7,original_start=256,original_end=260,profile='aztec36',source_sha256='old',selected=True)],
        objects=[dict(object='original.o',members=[proof['id']],sources=['src/old.c'])])
    before=copy.deepcopy(inv);ledger=dict(functions={proof['id']:accepted})
    current=game_build.module_inventory(inv,ledger,root)
    assert inv==before
    assert current['sources'][0]['source']==ref
    assert current['objects'][0]==dict(before['objects'][0],sources=[ref])
    for field,value in [('profile','different'),('original_start',258)]:
        bad=copy.deepcopy(inv);bad['sources'][0][field]=value
        with pytest.raises(ValueError,match='identity/extent/profile/proof'):
            game_build.module_inventory(bad,ledger,root)
    proof_path.write_bytes(proof_path.read_bytes()+b' ')
    with pytest.raises(ValueError,match='proof hash'):
        game_build.module_inventory(inv,ledger,root)



def test_port_override_keeps_function_identity_for_module_refs(module_tree):
    import port_gen
    overrides=module_tree/'overrides';overrides.mkdir()
    expected=overrides/'ov07_F_0100.c';expected.write_text('override')
    (overrides/'scenes.c').write_text('wrong module-wide override')
    text='/* staged from accepted source: src/scenes.c#draw_scene; source/proof class: exact C */'
    assert port_gen.unit_override(text,overrides,root=module_tree)==expected
    expected.unlink()
    assert port_gen.unit_override(text,overrides,root=module_tree) is None


def test_registry_scope_is_independent_of_source_location(module_tree):
    copied=module_tree/'copy';copied.mkdir()
    path=copied/'unit.c';raw=b'int recovered() { return scene_state; }\r\n';path.write_bytes(raw)
    assert names.read_source(copied,path)==raw
    assert names.read_source(copied,path,names_root=module_tree)==names.to_mechanical(raw,module_tree)
    # None retains the exact default registry of the old to_mechanical call.
    assert names.read_source(copied,path,names_root=None)==names.to_mechanical(raw)
    assert names.read_source_text(copied,path,names_root=module_tree)==names.to_mechanical(path.read_text(),module_tree)


def test_text_reader_preserves_default_encoding_and_universal_newlines(module_tree):
    path=module_tree/'src/text.c'
    path.write_bytes(b'/* caf\xc3\xa9 */\r\nint recovered(){ return scene_state; }\r\n')
    assert names.read_source_text(module_tree,path)==names.to_mechanical(path.read_text(),module_tree)
    assert names.read_source(module_tree,path)==names.to_mechanical(path.read_bytes(),module_tree)


def test_text_decoding_precedes_normalization_for_multibyte_encoding(module_tree):
    path=module_tree/'src/wide.c';path.write_bytes('int recovered(){return scene_state;}\r\n'.encode('utf-16'))
    expected=names.to_mechanical(path.read_text(encoding='utf-16'),module_tree)
    assert 'G_h01_0010' in expected
    assert names.read_source_text(module_tree,path,encoding='utf-16')==expected
    assert names.read_source(module_tree,path)==names.to_mechanical(path.read_bytes(),module_tree)


def test_external_candidate_requires_explicit_scratch_opt_in(module_tree):
    root=module_tree/'repo';root.mkdir()
    path=module_tree/'candidate.c';path.write_bytes(b'int recovered(){return scene_state;}\r\n')
    with pytest.raises(FormatError):names.read_source(root,path)
    with pytest.raises(FormatError):names.read_source(root,path,scratch=True)
    with pytest.raises(FormatError):names.read_source(root,path,external=True)
    assert names.read_source(root,path,scratch=True,external=True,names_root=module_tree)==names.to_mechanical(path.read_bytes(),module_tree)
    assert names.read_source_text(root,path,scratch=True,external=True,names_root=module_tree)==names.to_mechanical(path.read_text(),module_tree)
    with pytest.raises(FormatError,match='absolute'):names.read_source(root,'../candidate.c',scratch=True,external=True)
    quarantine=module_tree/'to_delete';quarantine.mkdir();retired=quarantine/'candidate.c';retired.write_bytes(path.read_bytes())
    with pytest.raises(FormatError,match='quarantined'):names.read_source(root,retired,scratch=True,external=True)


def test_difftest_diagnostic_accepts_explicit_external_candidate(module_tree,monkeypatch):
    import difftest
    root=module_tree/'repo';root.mkdir()
    candidate=module_tree/'candidate.c';candidate.write_bytes(b'/* candidate */\r\nint recovered(){return 1;}\r\n')
    fid='ov07_F_0300'
    evidence=dict(id=fid,hunk=7,start=0,end=2,extent_status='CLOSED_CFG',confidence='HIGH',undecoded_gaps=[])
    monkeypatch.setattr(difftest,'ROOT',root)
    monkeypatch.setattr(difftest,'catalog',lambda:({}, {fid:evidence}))
    monkeypatch.setattr(difftest,'data_model',lambda:{})
    plan=difftest.prepare(fid,candidate=candidate)
    assert plan['source']==names.to_mechanical(candidate.read_bytes()).decode('latin-1')
    assert plan['source_path']==candidate.resolve()
    assert plan['proof_category']=='UNRESOLVED_CANDIDATE'
