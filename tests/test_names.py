"""Spelling changes preserve source bytes and refuse ambiguous identities."""
import json
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import names
import rename


@pytest.fixture
def tree(tmp_path, monkeypatch):
    registry = dict(schema_version=1, functions={
        'resident_F_1234': dict(name='draw_scene', evidence='test'),
        'ov07_F_ABCD': dict(name='load_scene', evidence='test')},
        globals={'G_h01_4321': dict(name='scene_state', evidence='test')})
    (tmp_path / 'recovery').mkdir()
    (tmp_path / 'src').mkdir()
    def save():
        (tmp_path / 'recovery/names.json').write_bytes(json.dumps(registry).encode())
        names.load_registry.cache_clear()
        names._maps.cache_clear()
    save()
    monkeypatch.setattr(names, 'ROOT', tmp_path)
    yield tmp_path, registry, save
    names.load_registry.cache_clear()
    names._maps.cache_clear()


def test_round_trip_and_identity(tree):
    original = 'F_h00_1234 F_h07_ABCD G_h01_4321 F_h00_FFFF scene_state_extra 2F_h00_1234'
    readable = names.to_readable(original)
    assert readable == 'draw_scene load_scene scene_state F_h00_FFFF scene_state_extra 2F_h00_1234'
    assert names.to_mechanical(readable) == original
    assert names.to_readable(names.to_mechanical(readable)) == readable
    assert names.identity('draw_scene') == 'F_h00_1234'
    assert names.identity('unmapped') == 'unmapped'


def test_literals_and_comments(tree):
    original = r'''F_h00_1234("F_h00_1234 \" G_h01_4321", 'G_h01_4321', '\\');
/* function's "F_h00_1234" and G_h01_4321 */
// F_h07_ABCD says "G_h01_4321"
'''
    readable = names.to_readable(original)
    assert r'"F_h00_1234 \" G_h01_4321"' in readable
    assert "'G_h01_4321'" in readable
    assert """/* function's "draw_scene" and scene_state */""" in readable
    assert '// load_scene says "scene_state"' in readable
    assert names.to_mechanical(readable) == original


def test_assembly_underscores_and_bytes(tree):
    raw = b'\tpublic _F_h00_1234\r\n_F_h00_1234:\r\n move.l _G_h01_4321,d0 ; F_h07_ABCD\r\n'
    readable = names.to_readable(raw)
    assert b'_draw_scene:' in readable
    assert b'_scene_state,d0 ; load_scene' in readable
    assert names.identity('_scene_state') == '_G_h01_4321'
    assert names.to_mechanical(readable) == raw


@pytest.mark.parametrize('bad', ['int', '_Atomic', 'two words', '9invalid', 'F_h00_2222'])
def test_invalid_names_refused_before_writes(tree, bad):
    root, registry, save = tree
    path = root / 'src/a.c'; original = b'int F_h00_1234();\n'; path.write_bytes(original)
    registry['functions']['resident_F_1234']['name'] = bad; save()
    with pytest.raises(ValueError):
        rename.rename(root, apply=True)
    assert path.read_bytes() == original


@pytest.mark.parametrize('collision', ['draw_scene', '_draw_scene', '/* draw_scene */'])
def test_source_collision_refuses_entire_batch(tree, collision):
    root, registry, save = tree
    a = root / 'src/a.c'; a.write_bytes(b'int F_h00_1234();\n')
    b = root / 'src/b.h'; b.write_bytes(collision.encode())
    before = {p: p.read_bytes() for p in (a, b)}
    with pytest.raises(ValueError, match='already occur'):
        rename.rename(root, apply=True)
    assert {p: p.read_bytes() for p in before} == before


@pytest.mark.parametrize('name', ['draw_scene', '_draw_scene'])
def test_registry_collision_refused(tree, name):
    root, registry, save = tree
    registry['globals']['G_h01_4321']['name'] = name; save()
    with pytest.raises(ValueError, match='collision'):
        rename.rename(root, apply=True)


def test_dry_run_subset_and_apply_preserve_line_endings(tree):
    root, registry, save = tree
    a = root / 'src/a.c'; a.write_bytes(b'int F_h00_1234() { return G_h01_4321; }\r\n')
    b = root / 'src/b.asm'; b.write_bytes(b'\tpublic _F_h07_ABCD\n_F_h07_ABCD:\n\trts\n')
    before = {p: p.read_bytes() for p in (a, b)}
    changes = rename.rename(root, only=['ov07_F_ABCD'])
    assert set(changes) == {b}
    assert {p: p.read_bytes() for p in before} == before
    rename.rename(root, apply=True)
    # Fresh registry cache simulates a new process reading renamed source.
    names.load_registry.cache_clear(); names._maps.cache_clear()
    for p, raw in before.items():
        assert names.to_mechanical(p.read_bytes()) == raw
    assert b'\r\n' in a.read_bytes()
    assert b'\r' not in b.read_bytes()
    assert (root / 'recovery/names.json').read_bytes() == json.dumps(registry).encode()


def test_verification_failure_restores_every_changed_file(tree, monkeypatch):
    root, registry, save = tree
    paths = [root / 'src/a.c', root / 'src/b.asm']
    for path in paths:
        path.write_bytes(b'F_h00_1234 _G_h01_4321\n')
    before = {p: p.read_bytes() for p in paths}
    original = names.translate
    def broken(text, mapping):
        # Corrupt the inverse only; both changed files have already been written.
        if mapping.get('draw_scene') == 'F_h00_1234':
            return b'corrupt'
        return original(text, mapping)
    monkeypatch.setattr(names, 'translate', broken)
    with pytest.raises(ValueError, match='normalization changed'):
        rename.rename(root, apply=True)
    assert {p: p.read_bytes() for p in paths} == before


def test_write_failure_restores_files_already_written(tree, monkeypatch):
    root, registry, save = tree
    a = root / 'src/a.c'; b = root / 'src/b.c'
    for path in (a, b):
        path.write_bytes(b'F_h00_1234\n')
    original = Path.write_bytes
    failed = False
    def fail_once(path, raw):
        nonlocal failed
        if path == b and not failed:
            failed = True
            raise OSError('write failed')
        return original(path, raw)
    monkeypatch.setattr(Path, 'write_bytes', fail_once)
    with pytest.raises(OSError, match='write failed'):
        rename.rename(root, apply=True)
    assert a.read_bytes() == b.read_bytes() == b'F_h00_1234\n'


def test_excluded_identity_is_never_mapped_or_renamed(tree, monkeypatch, capsys):
    root, registry, save = tree
    monkeypatch.setattr(names, 'EXCLUDED', frozenset({'resident_F_1234'}))
    names._maps.cache_clear()
    path = root / 'src/a.c'; raw = b'int draw_scene; F_h00_1234();\n'; path.write_bytes(raw)
    assert names.to_mechanical(raw) == names.to_readable(raw) == raw
    assert not rename.rename(root, only=['resident_F_1234'], apply=True)
    assert path.read_bytes() == raw
    assert 'EXCLUDED resident_F_1234' in capsys.readouterr().out
