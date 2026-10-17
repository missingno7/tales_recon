"""Synthetic admission/memo invariants; no real-corpus replay or progress pins."""
import json
import os
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import pytest

import acceptance
import validation_memo as memo
from common import FormatError


@pytest.fixture
def cheap_closure(monkeypatch):
    monkeypatch.setattr(memo.Session, 'closure', lambda self, module: 'synthetic-validator-v1')


def call(root, loader, ident='proof', context='context'):
    return memo.validated(root, 'synthetic', ident, context, 'synthetic_validator', loader)


def test_exact_key_reuses_json_and_returns_independent_values(tmp_path, cheap_closure):
    source = tmp_path/'source'; source.write_bytes(b'old')
    calls = []
    def load():
        calls.append(True)
        return dict(raw=source.read_bytes(), nested=[dict(exact=True)], pair=(1, 2))
    row = call(tmp_path, load)
    row['nested'][0]['exact'] = False
    assert call(tmp_path, load) == dict(raw=b'old', nested=[dict(exact=True)], pair=(1, 2))
    assert len(calls) == 1
    cache = next((tmp_path/'build/validation-memo').rglob('*.json'))
    assert isinstance(json.loads(cache.read_text()), dict)


@pytest.mark.parametrize('name', ['proof', 'source', 'unit-receipt', 'facts'])
def test_each_read_content_invalidates_without_timestamp_help(tmp_path, cheap_closure, name):
    paths = [tmp_path/n for n in ('proof', 'source', 'unit-receipt', 'facts')]
    for p in paths:p.write_bytes(b'one')
    calls = []
    def load():
        calls.append(True)
        return [p.read_bytes() for p in paths]
    call(tmp_path, load)
    changed = tmp_path/name; before = changed.stat()
    changed.write_bytes(b'two'); os.utime(changed, ns=(before.st_atime_ns, before.st_mtime_ns))
    assert b'two' in call(tmp_path, load)
    assert len(calls) == 2


def test_unrelated_proof_stays_warm(tmp_path, cheap_closure):
    a = tmp_path/'a'; b = tmp_path/'b'
    a.write_bytes(b'a'); b.write_bytes(b'b')
    counts = [0, 0]
    def load(index, path):
        counts[index] += 1
        return path.read_bytes()
    for ident, index, path in [('a', 0, a), ('b', 1, b)]:
        call(tmp_path, lambda:load(index, path), ident)
    a.write_bytes(b'changed')
    for ident, index, path in [('a', 0, a), ('b', 1, b)]:
        call(tmp_path, lambda:load(index, path), ident)
    assert counts == [2, 1]


def test_context_and_class_are_key_inputs(tmp_path, cheap_closure):
    seen = []
    def load():seen.append(True); return len(seen)
    assert call(tmp_path, load, context='old') == 1
    assert call(tmp_path, load, context='new') == 2
    assert memo.validated(tmp_path, 'another', 'proof', 'new', 'synthetic_validator', load) == 3


def test_missing_path_and_directory_membership_are_dependencies(tmp_path, cheap_closure):
    missing = tmp_path/'optional'; folder = tmp_path/'facts'; folder.mkdir()
    def load():
        return missing.exists(), sorted(p.name for p in folder.iterdir())
    assert call(tmp_path, load) == (False, [])
    missing.write_bytes(b'x'); (folder/'new').write_bytes(b'x')
    assert call(tmp_path, load) == (True, ['new'])


@pytest.mark.parametrize('damage', ['json', 'value'])
def test_damaged_memo_replays(tmp_path, cheap_closure, damage):
    calls = []
    def load():calls.append(True); return 'accepted'
    call(tmp_path, load)
    cache = next((tmp_path/'build/validation-memo').rglob('*.json'))
    if damage == 'json':cache.write_text('{')
    else:
        data = json.loads(cache.read_bytes()); data['value'] = ['scalar', 'forged']; cache.write_text(json.dumps(data))
    assert call(tmp_path, load) == 'accepted'
    assert len(calls) == 2


def test_changed_input_cannot_publish_mixed_snapshot(tmp_path, cheap_closure):
    source = tmp_path/'source'; source.write_bytes(b'before')
    def load():
        result = source.read_bytes(); source.write_bytes(b'after'); return result
    with pytest.raises(FormatError, match='changed during snapshot'):
        call(tmp_path, load)
    assert not list((tmp_path/'build/validation-memo').rglob('*.json'))


def test_warm_and_shared_reads_keep_scope_end_check(tmp_path, cheap_closure):
    source = tmp_path/'source'; source.write_bytes(b'old')
    call(tmp_path, source.read_bytes)
    with pytest.raises(FormatError, match='changed during snapshot'):
        with memo.scope(tmp_path):
            assert call(tmp_path, source.read_bytes) == b'old'
            source.write_bytes(b'new')


def test_transitive_validator_import_edit_invalidates(tmp_path, monkeypatch):
    tools = tmp_path/'tools'; tools.mkdir()
    (tools/'synthetic_validator.py').write_text('from dependency import helper\n')
    (tools/'dependency.py').write_text('helper = 1\n')
    monkeypatch.setattr(memo, '__file__', str(tools/'validation_memo.py'))
    calls = []
    def load():calls.append(True); return 'accepted'
    call(tmp_path, load); call(tmp_path, load)
    assert len(calls) == 1
    (tools/'dependency.py').write_text('helper = 2\n')
    call(tmp_path, load)
    assert len(calls) == 2


def test_shared_audit_dependencies_propagate_to_every_proof(tmp_path, cheap_closure):
    source = tmp_path/'producer'; source.write_bytes(b'old')
    counts = []
    @memo.shared
    def audit(root):counts.append(True); return source.read_bytes()
    with memo.scope(tmp_path):
        assert call(tmp_path, lambda:audit(tmp_path), 'a') == b'old'
        assert call(tmp_path, lambda:audit(tmp_path), 'b') == b'old'
    assert len(counts) == 1
    source.write_bytes(b'new')
    assert call(tmp_path, lambda:audit(tmp_path), 'b') == b'new'
    assert len(counts) == 2


@pytest.mark.parametrize('verdict,exact_members,member,accepted', [
    ('EQUAL', [], 'new', True),
    ('ACCEPTED_WITH_BEHAVIORAL', ['exact'], 'exact', True),
    ('ACCEPTED_WITH_BEHAVIORAL', ['exact'], 'behavioral', False),
    ('DIFFER', ['exact'], 'exact', False),
    ('BEHAVIORAL_EQUAL', [], 'exact', False),
])
def test_unit_predicate_keeps_exact_and_behavioral_separate(verdict, exact_members, member, accepted):
    report = dict(verdict=verdict, accepted_exact_members=exact_members, exact_unit=False)
    assert acceptance.accepted_unit(report, [member], require_inexact=True) is accepted


def test_registry_declares_distinct_ownership_maps_and_publishers():
    maps = [c.ledger_map for c in acceptance.REGISTRY]
    assert len(maps) == len(set(maps))
    for entry in acceptance.REGISTRY:
        assert entry.categories and entry.validator and entry.projector and entry.publisher
        assert acceptance.proof_class(entry.ledger_map) is entry
    with pytest.raises(FormatError, match='unknown proof class'):
        acceptance.proof_class('unregistered')


@pytest.mark.parametrize('name,publisher', [('functions', 'promote_batch'), ('data', 'promote_data'),
                                          ('asm', 'promote_asm'), ('code_data', 'promote_code_data')])
@pytest.mark.parametrize('verify', [False, True])
def test_publisher_dispatch_preserves_existing_modes(tmp_path, name, publisher, verify):
    import promote
    manifest = tmp_path/'manifest.json'
    with patch.object(promote.subprocess, 'run', return_value=SimpleNamespace(returncode=7)) as run:
        assert promote.dispatch(name, manifest, verify) == 7
    argv = run.call_args.args[0]
    assert Path(argv[1]).name == publisher+'.py'
    assert str(manifest) in argv
    assert ('--verify-only' in argv) is verify
    if name in ('asm', 'code_data'):assert ('--promote' in argv) is not verify


def test_complete_c_manifest_keeps_single_object_boundary(tmp_path):
    import promote
    manifest = tmp_path/'manifest.json'; manifest.write_text(json.dumps({'id':'target'}))
    with patch.object(promote.subprocess, 'run', return_value=SimpleNamespace(returncode=0)) as run:
        assert promote.dispatch('dead_code', manifest, True) == 0
    assert run.call_args.args[0][-2:] == ['target', '--isolated']
    manifest.write_text(json.dumps([{'id':'one'}, {'id':'two'}]))
    with pytest.raises(FormatError, match='exactly one id'):promote.dispatch('dead_code', manifest)


def test_one_proof_can_yield_multiple_typed_object_rows(tmp_path, cheap_closure):
    import data_providers
    ctx=SimpleNamespace(blob=b'',model={},analysis={},ledger={'data_providers':{'provider':{}}},
                        promoted=[],identity='context')
    rows=[dict(id='object-a',original={'hunk':1,'start':0,'size':1},original_relocations=[],data_hex='01'),
          dict(id='object-b',original={'hunk':1,'start':1,'size':1},original_relocations=[],data_hex='02')]
    entry=acceptance.proof_class('data')
    with patch.object(data_providers,'load_data_providers',return_value=rows) as validate:
        with memo.scope(tmp_path):
            assert entry.validate(tmp_path,ctx)==rows
        with memo.scope(tmp_path):
            assert entry.validate(tmp_path,ctx)==rows
        assert validate.call_count==2  # Runtime validator replacements always run.


def test_new_tool_during_scope_cannot_publish_old_closure(tmp_path, monkeypatch):
    tools=tmp_path/'tools';tools.mkdir()
    (tools/'synthetic_validator.py').write_text('value=1\n')
    monkeypatch.setattr(memo,'__file__',str(tools/'validation_memo.py'))
    def load():
        (tools/'added.py').write_text('value=2\n')
        return 'accepted'
    with pytest.raises(FormatError,match='changed during snapshot'):
        call(tmp_path,load)
    assert not list((tmp_path/'build/validation-memo').rglob('*.json'))


def test_cache_replace_race_does_not_block_fresh_validation(tmp_path,cheap_closure):
    source=tmp_path/'source';source.write_bytes(b'old');calls=[]
    def load():calls.append(True);return source.read_bytes()
    assert call(tmp_path,load)==b'old'
    source.write_bytes(b'new')
    with patch.object(memo.os,'replace',side_effect=PermissionError('concurrent reader')):
        assert call(tmp_path,load)==b'new'
    assert call(tmp_path,load)==b'new'
    assert len(calls)==3
    assert not list((tmp_path/'build/validation-memo').rglob('.memo-*.json'))


def test_function_override_without_tool_source_cannot_publish_memo(tmp_path,cheap_closure):
    import data_providers
    ctx=SimpleNamespace(blob=b'',model={},analysis={},ledger={'data_providers':{'provider':{}}},
                        promoted=[],identity='context')
    calls=[]
    def replaced(*args,**kwargs):calls.append(True);return []
    with patch.object(data_providers,'load_data_providers',replaced):
        with memo.scope(tmp_path):acceptance.proof_class('data').validate(tmp_path,ctx)
        with memo.scope(tmp_path):acceptance.proof_class('data').validate(tmp_path,ctx)
    assert len(calls)==2
    assert not list((tmp_path/'build/validation-memo').rglob('*.json'))


@pytest.mark.parametrize('fail',[False,True])
def test_specimen_capture_uses_checked_read_only_stage(tmp_path,fail):
    import hybrid_image,evidence_snapshot
    from contextlib import contextmanager
    events=[]
    @contextmanager
    def checked(root):
        assert root==tmp_path
        events.append('enter')
        try:yield
        finally:events.append('exit')
    def replay(root):
        assert memo._SESSION.get().root==tmp_path.resolve()
        if fail:raise ValueError('replay failed')
        return {'compiler_produced':True}
    with patch.object(evidence_snapshot,'isolated_verification',checked),patch.object(hybrid_image,'_capture',replay):
        if fail:
            with pytest.raises(ValueError,match='replay failed'):hybrid_image.capture(tmp_path)
        else:assert hybrid_image.capture(tmp_path)=={'compiler_produced':True}
    assert events==['enter','exit']
    assert memo._SESSION.get() is None


def test_publish_refreshes_generated_evidence_and_verify_only_does_not(tmp_path):
    import promote
    manifest = tmp_path / 'm.json'; manifest.write_text('[]')
    calls = []
    def run(argv, *a, **k):
        calls.append([Path(x).name for x in argv[1:3]])
        return SimpleNamespace(returncode=0)
    with patch.object(promote.subprocess, 'run', side_effect=run):
        assert promote.main(['data', str(manifest)]) == 0
        assert calls[1:] == [['type_evidence.py', '--write'], ['census.py', '--write'], ['hybrid_image.py', '--write']]
        calls.clear()
        assert promote.main(['data', str(manifest), '--verify-only']) == 0
        assert len(calls) == 1


def test_publish_skips_a_manifest_already_in_the_ledger_and_rejects_partial(tmp_path, monkeypatch):
    import promote
    (tmp_path / 'recovery').mkdir()
    for ident in ('a', 'b'):
        (tmp_path / (ident + '.json')).write_text(json.dumps({'id': ident}))
    manifest = tmp_path / 'm.json'; manifest.write_text(json.dumps({'facts': ['a.json', 'b.json']}))
    ledger = tmp_path / 'recovery/ledger.json'
    monkeypatch.setattr(promote, 'ROOT', tmp_path)
    entry = acceptance.proof_class('data')
    ledger.write_text(json.dumps({'data_providers': {}}))
    assert promote.published(entry, manifest) is False
    ledger.write_text(json.dumps({'data_providers': {'a': {}, 'b': {}}}))
    assert promote.published(entry, manifest) is True
    with patch.object(promote, 'dispatch') as dispatch:
        assert promote.main(['data', str(manifest)]) == 0
        dispatch.assert_not_called()
    ledger.write_text(json.dumps({'data_providers': {'a': {}}}))
    with pytest.raises(FormatError, match='partially published'):
        promote.published(entry, manifest)


def test_several_data_manifests_share_one_publisher_run_and_one_refresh(tmp_path):
    import promote
    manifests = [tmp_path / ('m%d.json' % i) for i in range(3)]
    for m in manifests: m.write_text('[]')
    calls = []
    def run(argv, *a, **k):
        calls.append(argv)
        return SimpleNamespace(returncode=0)
    with patch.object(promote.subprocess, 'run', side_effect=run):
        assert promote.main(['data'] + [str(m) for m in manifests]) == 0
    publisher, refreshes = calls[0], calls[1:]
    assert Path(publisher[1]).name == 'promote_data.py'
    assert [a for a in publisher if a.endswith('.json')] == [str(m) for m in manifests]
    assert publisher.count('--manifest') == 3
    assert [Path(c[1]).name for c in refreshes] == ['type_evidence.py', 'census.py', 'hybrid_image.py']
