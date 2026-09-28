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
CODE data whose candidate boundary cannot be established independently (see
below). It does not slice an
object to the original function length. A candidate payload can include
compiler-owned code data; the report says so explicitly.

Prepared units are the exception to the first three refusals. When
`check_function` bundles recovered same-node callees, the target is compiled as
`_recovered` among them (for example `ov11_F_415A` at offset 236 of 1420
bytes). `unit_member_extent` then bounds the entry member by the candidate's
own output: the unique `_recovered` symbol (it must agree with `entry_offset`)
up to the next linked symbol or object boundary. The object CODE sizes come
from the candidate `.o` files (`unit_diag.candidate_contributions`). Every
function label in the member's object listing must be a linked symbol, so an
unsymboled static function cannot sit inside the segment. The normal function
diagnostic then runs on that member, and the report carries
`bounded_by: "unit_member_symbol"`, `unit_standalone_reason` and a
`candidate_extent` with `unit_offset`, `unit_end`, `object` and `end_basis`.
If the member cannot be bounded independently, the original refusal reason is
kept and `unit_member_reason` names the missing evidence. Measured on
2026-09-28: the EQUAL keys for `ov11_F_415A` (`652f00b4…`), `ov11_F_4B0C`
(`5872c112…`) and `ov11_F_6486` (`cc5bc703…`) align fully, with 0 hypotheses
and 0 unresolved or different references. The DIFFER key `cf0c6b55…` for
`ov11_F_415A` is 158 against 156 bytes, with 3 expected-only and 4
candidate-only instructions.

An original with CODE data (a census-proved PC-relative word jump table, or
PC-relative literals) is aligned only when both sides have an independently
established code/data boundary. The original side uses existing strict proofs
only: `jump_tables` from the census and `owned_code_data.expected_string_tail`.
The candidate side uses its own compile. The function's section of its
assembler listing must declare the literal pool (a local label followed only
by `dc.b` bytes and an optional `ds 0`, and nothing that emits code after it)
and any switch tables (`dc.w .T-.B-2`). The pool must equal the final payload
bytes, so the code part ends at `payload - pool - padding`. Every in-stream
PC-relative data target must fall in the pool and match the listing's
`.N+k` references. Each listed table must be a dispatch that recursive descent
from the entry reaches, with the census's form and the same entry counts. The
candidate must carry no relocations in the data part. Original lengths are
never used.

The two code parts then go through the normal comparison. Table spans are
not decoded, and table entries are CFG targets. `blocks.jump_tables` checks
that each entry's aligned target is the candidate entry and a paired block
start. PC-relative operands at the same pool offset resolve to one
`code_data` identity. `data_boundary` reports `original_basis`,
`candidate_basis`, code lengths, the literal comparison (lengths, padding,
byte equality, first difference, PC-relative targets), and the table counts.
Differing literal bytes or targets add one `data_ownership_review`
hypothesis. `candidate_extent.bytes` stays the whole payload, and
`code_bytes`/`data_bytes` are added. If either boundary cannot be
established, the report keeps `UNSUPPORTED` with
`ORIGINAL_DATA_BOUNDARY_HAS_NO_MAPPED_CANDIDATE_BOUNDARY` and adds a specific
`data_boundary_reason`, for example `CANDIDATE_LISTING_UNAVAILABLE`,
`CANDIDATE_LISTING_POOL_BYTES_DISAGREE_WITH_PAYLOAD` or
`ORIGINAL_CODE_DATA_NOT_STRICTLY_PROVEN: ...`. None of this claims data
ownership. FUNCTION_WITH_DATA_MATCH still comes only from `check_function`.

Measured on 2026-09-28, the exact-verified controls have zero differences:
all 16 FUNCTION_WITH_DATA_MATCH proofs except `ov04_F_26F0` and
`ov04_F_27FE` (for example `ov04_F_18A6` `55be4b1e…`, a 164-byte pool, and the
unit member `ov07_F_03CC` `616b5b9b…`), and the jump-table functions
`ov08_F_3DF4` (`4d019117…`, 11 entries) and `ov11_F_41F6` (`ff6e3163…`, 8
entries). For those two exceptions the data parts are equal, but absolute-long
references remain unresolved. Their relocation identities are not yet mapped
by the resolver, which is a separate limitation. All 15 retained
`ov04_F_0536` keys in the hypothesis ledger are now measurable. The literal
pools are 38 bytes against 38 and byte-equal. The code parts are 600–682
bytes against 622.

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
