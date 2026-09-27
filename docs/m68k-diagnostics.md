# M68K comparison diagnostics

`tools/diag.py` provides shift-tolerant alignment and local mismatch guidance
for a closed original function and a validated, cached standalone compiler
artifact. It never establishes semantic, source, or machine-code equality and
is not used by `check_function.py` or the exact comparison path.

```powershell
python tools/diag.py ov09_F_298E --cache-key 5d74128b28b30c647f3528921a6bca6ac9f28bab31c5128da77f1c4cb132c580 --json
```

The API is `diagnose(function_id, cache_key)`. It validates original function
evidence through `check_function.validated_function` and loads compiler output
through the integrity-checked `compiler_oracle.cached`. `compact_summary(report)`
returns bounded feedback for research records. The report includes coarse
instruction pairs, insertions/deletions, paired basic blocks, conservative
branch target and fallthrough checks, and uncertain width/register/frame/
reference hypotheses. Calls are not CFG edges. A4 reference changes do not
prove symbol identity.

The candidate extent is the complete standalone object CODE payload. The tool
returns `UNSUPPORTED` for multi-object units, a nonzero entry offset, additional
CODE symbols, DATA/BSS contributions, non-closed original extents, or original
data boundaries without mapped candidate boundaries. It does not slice an
object to the original function length. A candidate payload can include
compiler-owned code data; the report says so explicitly.

Cached examples used by the regression tests are a 20-byte `ov14_F_03AE`
exact-verifier control (`f25f68d19e2811fa7533a18a206ec128d932d9de16c8f6cf7e6c96009b0e9456`)
and the retained 672-byte `ov09_F_298E` near-match (`5d74128b28b30c647f3528921a6bca6ac9f28bab31c5128da77f1c4cb132c580`).
The latter aligns 183 instructions, leaves six candidate instructions unpaired,
and produces 32 coarse paired blocks. These measurements are search guidance;
the underlying attempt remains `DIFFER`.
