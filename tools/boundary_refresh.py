"""Run the promotion-boundary refresh in its required order; stop at the first failure.

After every published promotion (promote_batch.py or a non-isolated
check_function/check_unit run) the derived evidence must be regenerated
before the next promotion gate, whose regression suite requires current type
evidence and hybrid specimens naming exactly the canonical sources.
"""
import subprocess
import sys

from analysis_support import ROOT

STEPS = (
    ("type evidence", ["tools/type_evidence.py", "--write"]),
    ("hybrid refresh", ["tools/hybrid_image.py", "--refresh", "--write"]),
    ("census write", ["tools/census.py", "--write"]),
    ("census check", ["tools/census.py", "--check"]),
    ("hybrid check", ["tools/hybrid_image.py", "--check"]),
)


def main():
    for label, argv in STEPS:
        proc = subprocess.run([sys.executable] + argv, cwd=ROOT, capture_output=True, text=True)
        lines = [line for line in (proc.stdout + proc.stderr).splitlines() if line.strip()]
        print("%-14s exit %d  %s" % (label, proc.returncode, lines[-1] if lines else ""))
        if proc.returncode != 0:
            print("\n".join(lines[-20:]), file=sys.stderr)
            return proc.returncode
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
