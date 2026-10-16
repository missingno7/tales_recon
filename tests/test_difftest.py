from pathlib import Path
import sys

import pytest
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import difftest

_DEPENDENCIES = difftest.dependencies()
_NEEDS_RUNTIME = pytest.mark.skipif(
    not _DEPENDENCIES["ok"],
    reason="difftest runtime dependency missing: " + "; ".join(_DEPENDENCIES["reasons"]),
)


@_NEEDS_RUNTIME
def test_known_good_ov11_25d6_agrees():
    result = difftest.compare_function("ov11_F_25D6", trials=128)
    assert result["status"] == "agree", result
    assert result["trials"] == 128


@_NEEDS_RUNTIME
def test_known_good_ov11_262e_agrees():
    result = difftest.compare_function("ov11_F_262E", trials=128)
    assert result["status"] == "agree", result
    assert result["trials"] == 128


@_NEEDS_RUNTIME
def test_one_character_mutant_is_detected():
    plan = difftest.prepare("ov11_F_25D6")
    mutant, count = plan["source"].replace("b>=a", "b>a", 1), plan["source"].count("b>=a")
    assert count == 1
    result = difftest.compare_function("ov11_F_25D6", trials=64, source_override=mutant)
    assert result["status"] == "mismatch", result
    assert any(item.get("area") == "D0" and item.get("args") == [0, 0, 0] for item in result["mismatches"])


def test_model_backed_struct_global_uses_measured_stride():
    plan = difftest.prepare("ov11_F_5EC0")
    global_view = plan["globals"]["G_h01_8BEC"]
    assert global_view["struct_model"] == "GameJungleCluster"
    assert global_view["struct_size"] == 52
    assert global_view["model_count"] == 40
    source = difftest.make_host_source(plan, difftest.image())
    assert "#pragma pack(push,2)" in source
    assert "G_h01_8BEC[40]" in source


def test_unmodeled_struct_view_is_reported_unsupported():
    entries, _ = difftest.catalog()
    candidate = next((fid for fid in entries if "no compatible typed data_model layout" in
                      difftest.classify_function(fid).get("reason", "")), None)
    if candidate is None:
        pytest.skip("no unmodeled struct views remain")
    result = difftest.compare_function(candidate, trials=1)
    assert result["status"] == "unsupported", result
    assert result["eligible"] is False
    assert result["reason"]


@pytest.mark.skipif(not difftest.gcc_path(), reason="MSYS2 gcc unavailable")
def test_model_backed_struct_host_harness_compiles():
    plan = difftest.prepare("ov11_F_5EC0")
    im = difftest.image()
    difftest.BUILD.mkdir(parents=True, exist_ok=True)
    host = None
    with tempfile.TemporaryDirectory(prefix="difftest_test_", dir=str(difftest.BUILD.resolve()),
                                     ignore_cleanup_errors=True) as directory:
        try:
            host = difftest.compile_host(plan, im, Path(directory))
        finally:
            if host and host.get("lib"):
                import _ctypes
                _ctypes.FreeLibrary(host["lib"]._handle)
                host["lib"]._handle = 0
                host.clear()


def test_pointer_long_view_normalizes_to_target_identity():
    plan = difftest.prepare("ov04_F_1302")
    view = plan["globals"]["G_h01_46D6"]
    assert view["pointer_valued"] is True
    assert view["pointer_store_target"] == "G_h01_1426"
    source = difftest.make_host_source(plan, difftest.image())
    assert "normptr32((uint32_t)G_h01_46D6)" in source


def test_typed_long_buffer_reports_endianness_as_portability():
    param = {"kind": "pointer", "base": "long", "unsigned": False}
    original = bytes.fromhex("0000000100000002")
    host = bytes.fromhex("0100000002000000")
    mismatches, portability = difftest.compare_pointer_buffer(param, original, host, 0)
    assert not mismatches
    assert portability[0]["cause"] == "host_endianness"
    assert portability[0]["logical_value"] == 1


def test_measured_jump_table_and_overlay_code_are_mapped():
    entries, evs = difftest.catalog()
    jump = next(evs[fid] for fid in entries if evs[fid].get("jump_tables"))
    calls, stubs = difftest.calls_of(jump)
    assert jump["jump_tables"]
    assert len(calls) == len(stubs)
    overlay = next(evs[fid] for fid in entries if evs[fid].get("hunk", 0) >= 3)
    im = difftest.image()
    code = difftest.patch_code({"evidence": overlay}, im)
    assert code["base"] == difftest.hunk_base(overlay["hunk"])
    assert code["bytes"][overlay["start"]:overlay["end"]] == bytes.fromhex(overlay["raw_bytes"])
    for rel in im["model"]["relocations"]:
        if rel["source_hunk"] == 1 and rel["type"] == "HUNK_RELOC32":
            target = int.from_bytes(im["data"][rel["source_offset"]:rel["source_offset"] + 4], "big")
            assert difftest.segment_for_address(im, target) is not None


@_NEEDS_RUNTIME
def test_runtime_state_dependency_is_diagnosed_not_guessed():
    # 411E reads through G_h01_3AB4, a buffer pointer that is zero in the initial
    # DATA image and only valid after a file is opened. The harness must name
    # the first unmapped access instead of inventing a state.
    result = difftest.compare_function("resident_F_411E", trials=8)
    assert result["status"] == "mismatch", result
    first = result["mismatches"][0]
    assert first["cause"] == "READ_UNMAPPED" and first.get("first_unmapped"), result