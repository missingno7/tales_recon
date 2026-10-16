from pathlib import Path
import sys

import pytest

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


def test_struct_layout_function_is_reported_unsupported():
    result = difftest.compare_function("ov14_F_0412", trials=1)
    assert result["status"] == "unsupported", result
    assert result["eligible"] is False
    assert "struct layout" in result["reason"]

@_NEEDS_RUNTIME
@pytest.mark.xfail(reason="411E reads through G_h01_3AB4 into a buffer the emulator does not map yet", strict=True)
def test_behavioral_char_return_compares_low_byte_and_memory():
    result = difftest.compare_function("resident_F_411E", trials=32)
    assert result["status"] == "agree", result
    assert result["return_comparison"] == "D0.b"
    assert result["stubs"]