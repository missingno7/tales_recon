"""Slow, opt-in replay of the retained vamos equivalence corpus."""
from concurrent.futures import ThreadPoolExecutor
import json
import os
from pathlib import Path
import shutil

import pytest

import vamos_backend


ROOT = Path(os.environ.get("TALES_VAMOS_TEST_ROOT", Path(__file__).resolve().parents[1])).resolve()
WORKER = ROOT / "build/workers/luna-vamos"
LOCAL = ROOT / "build/vamos-equivalence"


@pytest.mark.vamos_equivalence
def test_retained_equivalence_corpus_and_link(monkeypatch):
    manifest_path = WORKER / "corpus-manifest.json"
    routed_path = WORKER / "routed-corpus-results.json"
    pin_path = ROOT / "docs/toolchain.json"
    if not manifest_path.is_file() or not routed_path.is_file():
        pytest.skip("requires the retained build/workers/luna-vamos corpus artifacts")
    if not pin_path.is_file():
        pytest.skip("requires the pinned vamos toolchain inventory in docs/toolchain.json")

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    routed = json.loads(routed_path.read_text(encoding="utf-8"))
    routes = {item["id"]: item for item in routed["items"]}
    job_root = LOCAL / "jobs"
    monkeypatch.setenv("TALES_VAMOS_TEST_ROOT", str(ROOT))
    monkeypatch.setenv("TALES_VAMOS_JOB_ROOT", str(job_root))
    vamos_backend.toolchain_root.cache_clear()
    vamos_backend._runtime.cache_clear()

    def check(row):
        row_id = row["id"]
        expected_route = routes[row_id]["route"]
        source_path = ROOT / row["source"]
        source = source_path.read_text(encoding="utf-8-sig")
        job = job_root / row_id
        if row["kind"] == "c":
            if vamos_backend.has_float_type(source):
                assert expected_route, f"float source was not routed: {row_id}"
                return
            try:
                result = vamos_backend.compile_source_pair(
                    source, row["profile"], job, flags=row.get("flags") or None)
            except vamos_backend.VamosFailure as exc:
                assert expected_route, f"unrouted vamos failure for {row_id}: {exc}"
                if any(reason.startswith(("trace-open:", "trace-call:"))
                       for reason in routes[row_id].get("route_reasons", [])):
                    assert "math-library-use:" in str(exc)
                return
            assert not expected_route, f"math-dependent source missed trace routing: {row_id}"
            actual_asm = result["asm"].read_bytes()
            actual_obj = result["object"].read_bytes()
        else:
            result = vamos_backend.compile_asm_source(source, job)
            actual_asm = source_path.read_bytes()
            actual_obj = result["object"].read_bytes()
        expected_asm = (ROOT / row["asm_ref"]).read_bytes()
        expected_obj = (ROOT / row["obj_ref"]).read_bytes()
        assert actual_asm == expected_asm, f"assembly mismatch: {row_id}"
        assert actual_obj == expected_obj, f"object mismatch: {row_id}"

    with ThreadPoolExecutor(max_workers=8) as pool:
        list(pool.map(check, manifest["items"]))

    stage = ROOT / "build/workers/luna-link-smoke/stage-v17/artifacts"
    link_reference = WORKER / "whole-game-link/result.json"
    if stage.is_dir() and link_reference.is_file():
        expected = json.loads(link_reference.read_text(encoding="utf-8"))["reference"]
        job = LOCAL / "whole-game-link"
        sysroot = job / "sys"
        work = sysroot / "work"
        work.mkdir(parents=True, exist_ok=True)
        shutil.copytree(stage, work, dirs_exist_ok=True)
        toolchain = vamos_backend.toolchain_root()
        vamos, _ = vamos_backend._runtime()
        vamos_backend._run_guest(
            vamos, sysroot, toolchain, work, "Old1:bin/ln",
            ["-m", "-t", "-o", "DuckTales", "-f", "link.lnk"],
            work / "vamos-link.log", timeout=300)
        for name in ("DuckTales", "DuckTales.sym"):
            assert (work / name).is_file()
            assert vamos_backend.sha256((work / name).read_bytes()) == expected[name]["sha256"]
