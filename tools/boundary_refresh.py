"""Run the promotion-boundary refresh in its required order; stop at the first failure.

After every published promotion (promote_batch.py or a non-isolated
check_function/check_unit run) the derived evidence must be regenerated
before the next promotion gate, whose regression suite requires current type
evidence and hybrid specimens naming exactly the canonical sources.
"""
from contextlib import redirect_stderr, redirect_stdout
import io
import runpy
import sys
import traceback

from analysis_support import ROOT
from evidence_snapshot import snapshot, validated_stage

STEPS = (
    # Census first: a census change regenerates the instruction index that
    # type evidence is keyed to, so type evidence must follow it.
    ("census write", "tools/census.py", ["--write"]),
    ("type evidence", "tools/type_evidence.py", ["--write"]),
    ("hybrid refresh", "tools/hybrid_image.py", ["--refresh", "--write"]),
    ("census write", "tools/census.py", ["--write"]),
    ("census check", "tools/census.py", ["--check"]),
    ("hybrid check", "tools/hybrid_image.py", ["--check"]),
    ("type check", "tools/type_evidence.py", ["--check"]),
)


def run_step(script, argv):
    stdout, stderr = io.StringIO(), io.StringIO()
    previous = sys.argv
    sys.argv = [str(ROOT / script), *argv]
    code = 0
    try:
        with redirect_stdout(stdout), redirect_stderr(stderr):
            try:
                runpy.run_path(str(ROOT / script), run_name="__main__")
            except SystemExit as exc:
                code = 0 if exc.code is None else (exc.code if isinstance(exc.code, int) else 1)
    except Exception:
        traceback.print_exc(file=stderr)
        code = 1
    finally:
        sys.argv = previous
    return code, stdout.getvalue() + stderr.getvalue()


def main():
    with snapshot():
        for label, script, argv in STEPS:
            with validated_stage(ROOT, strict=True):
                code, output = run_step(script, argv)
            lines = [line for line in output.splitlines() if line.strip()]
            print("%-14s exit %d  %s" % (label, code, lines[-1] if lines else ""))
            if code != 0:
                print("\n".join(lines[-20:]), file=sys.stderr)
                return code
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
