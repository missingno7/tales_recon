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
prove symbol identity by themselves; see reference identity below.

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

`register_trace` walks aligned pairs whose operation stem and operand-role
structure agree. It reports the first pair whose register roles differ, an
original-to-candidate register table, and the first conflict (one original
register used as two candidate registers, or the reverse). Per-register
read/write counts are approximate syntax only. The trace does not prove
allocation or liveness. For the retained `ov09_F_298E` candidate, the first
divergence is expected `moveq #0,d1` at 116 against candidate `moveq #0,d0` at
120. The table also records a `d0`/`d1` role swap.

## Reference identity and hypothesis groups

`diagnose` builds a `ReferenceResolver` that reuses identities the repository
already establishes. It never infers a binding from a displacement or name
alone. Sources, as listed in `reference_identity.sources`:

| Source | Side | Proof level |
| --- | --- | --- |
| ledger `a4.bias` backed by the startup LEA `HUNK_RELOC32` | original | observed relocation |
| ledger `referenced_data` (A4_RELATIVE) and `direct_callees` per site | original | observed function evidence |
| ledger function `relocations` | original | observed relocation |
| cached compile symbols, relocations and linked startup A4 LEA | candidate | compiler output |
| `[GF]_hNN_HEX` proxy names through `function_compare.target_identity`, with the same folded-COMMON and extern-width bounds | binding | rule used for FUNCTION_CODE_MATCH |
| runtime aliases from `runtime-arithmetic.json` | binding | runtime contribution byte proof |
| `docs/symbols.json` recovered function ids | binding | FUNCTION_CODE_MATCH extent |
| `recovery/proofs/*` `relocation_proof` | corroboration | FUNCTION_CODE_MATCH |

Each aligned A4, PC-relative, absolute-relocated or call reference is
classified as `same_identity`, `layout_only` (same identity, and only the
candidate link layout changes the displacement), `different_identity` (a real
binding problem) or `unresolved` (with the missing side and reason). If a pair
differs only in resolved displacement fields, it produces no hypothesis. Binding
categories (`a4_global_layout`, `pc_relative_layout`,
`memory_reference_or_layout`, `call_target_or_encoding`, `data_ownership_review`)
carry `identity_states` counts. `hypothesis_groups` reports them separately
from source-shape categories (register, width, frame, constants, layout,
control flow). Frame-slot displacements now count only as
`frame_or_stack_reference`. `compare_code` without a resolver leaves every
reference `unresolved`, which preserves the earlier behaviour.

Cached measurements from 2026-09-28:

- `ov14_F_03AE` control: the earlier output had 2 unresolved `a4_global_layout`
  observations. It now has 0 hypotheses and 2 `layout_only` references
  (`_G_h01_1424`, `_G_h01_3AB2`), with 0 unresolved.
- `ov09_F_298E` v15: the earlier output had `a4_global_layout` 24,
  `call_target_or_encoding` 8, `register_assignment` 17 and
  `instruction_layout` 1. It now has 0 binding/layout hypotheses and 18
  source-shape hypotheses (`register_assignment` 17, `instruction_layout` 1),
  plus 32 `layout_only` references (24 data, 8 A4 call stubs) and 0 unresolved.

The retained snapshots in `evidence/experiments/*-baseline.json` predate this
change. They are historical evidence and are not regenerated.

Complete compiler units (several members, gaps, literal tails, candidate-only
contributions) are diagnosed by `tools/unit_diag.py`; see
`docs/unit-diagnostics.md`. Absolute short operands are no longer treated as
reference operands (they carry no `HUNK_RELOC32` identity).
