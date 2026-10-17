from pathlib import Path

import pytest

from common import FormatError
import compile_queue
import vamos_backend


def test_float_screen_ignores_non_code():
    assert not vamos_backend.has_float_type('/* double */ int recovered(void) { return 1; }')
    assert not vamos_backend.has_float_type('char *s = "float double"; int recovered(void) { return 1; }')
    assert vamos_backend.has_float_type('int recovered(void) { double value; return 0; }')
    assert vamos_backend.has_float_type('int recovered(void) { float value; return 0; }')


def test_math_trace_detects_open_and_call_names():
    trace = "OpenLibrary: 'mathieeedoubbas.library' version 0\n{ CALL: (mathieeedoubbas.library) 12 IEEEDPAdd(\n"
    assert vamos_backend.trace_math_libraries(trace) == ['mathieeedoubbas.library']
    assert vamos_backend.trace_math_libraries('OpenLibrary: graphics.library') == []


def test_volume_args_are_private_and_include_required_volumes(tmp_path):
    sysroot = tmp_path / 'job' / 'sys'
    work = sysroot / 'work'
    tools = tmp_path / 'toolchain'
    args = vamos_backend.build_vamos_args(
        tmp_path / 'vamos.exe', sysroot, tools, work, 'Old1:bin/cc', ['-a', 'unit.c'])
    volumes = [args[index + 1] for index, token in enumerate(args) if token == '-V']
    names = [entry.split(':', 1)[0] for entry in volumes]
    include_path = (tools / 'SYS1/include').resolve().as_posix()
    assert names == ['root', 'System', 'Old1', 'Old2', 'Work', 'INCLUDE']
    assert volumes[0] == f'root:{sysroot.resolve().as_posix()}'
    assert volumes[4] == f'Work:{work.resolve().as_posix()}'
    assert volumes[5] == f'INCLUDE:{include_path}'
    assert '--cwd' in args and args[args.index('--cwd') + 1] == 'Work:'


def test_compatibility_shim_is_pinned(tmp_path, monkeypatch):
    shim_dir = tmp_path / "shim"
    shim_dir.mkdir()
    shim = shim_dir / "sitecustomize.py"
    shim.write_text("compat", encoding="utf-8")
    digest = vamos_backend.sha256(shim.read_bytes())
    monkeypatch.setattr(vamos_backend, "_backend_spec", lambda: {
        "compatibility_shim": "tools/vamos_compat/sitecustomize.py",
        "compatibility_shim_sha256": digest,
    })
    monkeypatch.setenv("TALES_VAMOS_COMPAT_PATH", str(shim_dir))
    assert vamos_backend.compatibility_shim() == shim_dir
    shim.write_text("changed", encoding="utf-8")
    with pytest.raises(FormatError, match="compatibility shim"):
        vamos_backend.compatibility_shim()


def test_inventory_hash_binds_file_names_and_contents(tmp_path):
    for system in ('SYS1', 'SYS2'):
        for subdir in ('bin', 'include', 'lib'):
            (tmp_path / system / subdir).mkdir(parents=True)
    first = tmp_path / 'SYS1' / 'bin' / 'cc'
    first.write_bytes(b'cc')
    expected = vamos_backend.inventory_sha256(tmp_path)
    spec = {'tree_inventory': {'directories': list(vamos_backend.TREE_DIRECTORIES), 'file_count': 1, 'sha256': expected}}
    vamos_backend.validate_inventory(tmp_path, spec)
    first.write_bytes(b'changed')
    with pytest.raises(FormatError, match='inventory SHA-256 differs'):
        vamos_backend.validate_inventory(tmp_path, spec)


def test_math_use_retries_the_trial_on_winuae(monkeypatch):
    trial = {'source': 'int recovered(void) { return 1; }', 'profile': 'aztec36'}
    monkeypatch.setattr(compile_queue, 'trial_key', lambda _: 'synthetic-key')
    monkeypatch.setattr(vamos_backend.compiler_oracle, 'cached', lambda _: None)
    monkeypatch.setattr(vamos_backend, '_compile_vamos_trial',
                        lambda *_: (None, 'math-library-use:mathieeedoubbas.library', {'job': 'vamos-1'}))
    events = []
    monkeypatch.setattr(compile_queue, 'write_backend_receipt',
                        lambda key, backend, attempts: events.append((key, backend, attempts)))
    result = vamos_backend.compile_many(
        [trial], legacy_compile_many=lambda trials: [{'status': 'COMPILED'}])
    assert result == [{'status': 'COMPILED'}]
    assert events[0][0:2] == ('synthetic-key', 'winuae')
    assert events[0][2][0]['reason'] == 'math-library-use:mathieeedoubbas.library'


@pytest.mark.parametrize('value', ['auto', 'vamos', 'winuae'])
def test_backend_switch_accepts_supported_values(monkeypatch, value):
    monkeypatch.setenv('TALES_COMPILE_BACKEND', value)
    assert compile_queue.compile_backend() == value


def test_backend_switch_rejects_unknown_value(monkeypatch):
    monkeypatch.setenv('TALES_COMPILE_BACKEND', 'native')
    with pytest.raises(FormatError, match='TALES_COMPILE_BACKEND'):
        compile_queue.compile_backend()


def test_vamos_pool_defaults_to_eight_and_is_bounded(monkeypatch):
    monkeypatch.delenv('TALES_VAMOS_JOBS', raising=False)
    assert vamos_backend.worker_count() == 8
    monkeypatch.setenv('TALES_VAMOS_JOBS', '9')
    with pytest.raises(FormatError, match='between 1 and 8'):
        vamos_backend.worker_count()


def test_link_command_keeps_arguments_after_shell_redirections():
    guest, args = vamos_backend.link_guest_command(
        'Old1:bin/ln <compiler-input.txt >t000-ln.log -m -t -o t000.exe h000.o c.lib')
    assert guest == 'Old1:bin/ln'
    assert args == ['-m', '-t', '-o', 't000.exe', 'h000.o', 'c.lib']
