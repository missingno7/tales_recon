# Complete-unit diagnostics

`tools/unit_diag.py` gives advisory guidance for a complete compiler-unit
hypothesis. `check_unit.py` remains the only acceptance path, and the complete
unit remains the acceptance boundary. This tool does not compile, write
recovery state, promote, relock, or claim equality or ownership.

Inputs:

- Unit hypothesis: ordered original member ids (all in one CODE hunk), an
  optional interval, and an optional entry member. The entry member is the one
  `check_unit` compiles as `recovered`. Literal tails are included only when
  `check_unit.proven_tail` already proves them from the recovery ledger
  (`FUNCTION_WITH_DATA_MATCH`). No other owned range is accepted.
- Candidate: a validated compile-cache entry (`compiler_oracle.cached`).

The candidate payload is split at its own linked symbols and at object-file
CODE sizes. Original lengths are never used to slice it. When the compiler
listing has public labels with no linked symbol (for example, a definition
that Manx drops from the map after an earlier `extern`), the report lists them
under `unsymboled_asm_labels`. Their bytes stay in the preceding segment.

Members are paired with segments by identity only. The accepted bases are
`[F]_hNN_HEX` proxy names (`function_compare.mechanical`), `docs/symbols.json`
recovered ids, and the explicit `_recovered` entry convention. Each pair goes
through `diag.compare_code` with a per-member `diag.ReferenceResolver`
subclass. The member reports length delta, alignment, source-shape versus
binding hypothesis groups, and reference states (`same_identity`,
`layout_only`, `different_identity`, `unresolved`). For a member with a proven
literal tail, the candidate's own literal bundle begins at its lowest
in-segment PC-relative data target. A PC-relative operand into the original
proven tail and into the candidate bundle at the same offset resolves to one
literal identity. The two bundles are then compared byte for byte.

Member states: `same_bytes`, `same_after_reference_identity` (no hypotheses,
no unresolved or different references), `no_shape_difference_references_unresolved`,
`differs`, `missing_in_candidate`, `comparison_unsupported`, and
`literal_boundary_unmapped`.

Original bytes inside the interval that are not covered by a member or a
proven tail are listed as `unknown` gaps (`ownership: UNKNOWN_NOT_ASSIGNED`),
with offset and length. Discovered function starts inside a gap are listed as
evidence only. Candidate segments without a paired member are reported as
`CANDIDATE_ONLY_NOT_ASSIGNED`, with their identity note. A proxy name that
points into an unknown gap is recorded as `proxy_location_in_unknown_gap`, and
the gap stays unknown. The report also covers order inversions,
candidate-only segments between members, and overlapping claims.
`exact_verdict` only echoes existing `recovery/units/*/<cache_key>/*/receipt.json`
verdicts, or reports `NOT_RUN_FOR_THIS_CACHE_KEY`.

```powershell
python tools/unit_diag.py --receipt recovery/units/ov10_F_2160/af14c548.../43c0a61592f51d1c/receipt.json --cache-key af14c548...
python tools/unit_diag.py --members ov10_F_1FDE,ov10_F_2160 --entry ov10_F_2160 --cache-key <key>
python tools/unit_diag.py --package RP01 --cache-key 0b66dd65e9063d0c60d599e670250cee907ac9134fdd7e157359d4e7206fcaeb
```

For a multi-member candidate (`check_unit --member`), pass `--new-members
A,B` (or `--receipt`, which reads the receipt's `member_sources`). Each new
member's row is then marked `new`, and canonical bridges are marked as not new.
Calls back to the entry bind through `_recovered`. The labels are advisory and
do not change pairing, states or gaps.

For a `check_unit --natural-interval` receipt, `--receipt` uses the receipt's
interval for unknown gaps. Linked callees outside the interval are listed as
`members_outside_interval`. The summary gains a `natural_interval` block, which
echoes the receipt verdict, the member verdict, the compaction spans, the
unknown gaps, the gap-crossing counts, every crossing that is not
gap-independent, and every canonical member that is not EQUAL. This is an echo
of the receipt; the classification comes only from check_unit.

`diagnose_unit` runs under `census.advisory_image`. The fixture lock, the
function evidence, and the compile cache are still hash-checked. The census does
not re-validate every canonical promotion receipt here, and the report records
`canonical_promotion_evidence: NOT_REVALIDATED_BY_ADVISORY_DIAGNOSTIC`. A
receipt written by another tool version therefore cannot make an advisory
diagnostic unreadable. For example, on 2026-09-28 a canonical receipt with
merged stand-ins raised "combined source hash differs" in every region
`--receipt` run. Census and promotion stay strict.

By default, the CLI prints `compact_summary` (at most 5 KB, for fleet-worker
prompts). `--json` prints the full report. The API consists of
`analyze_unit(...)` (pure, used by the synthetic fixtures), `diagnose_unit(ids,
cache_key, entry_member=, interval=)` and `compact_summary(report)`.

Cached measurements from 2026-09-28:

- Positive control `ov10_F_1FDE`+`ov10_F_2160` (`af14c548…`, check_unit
  `EQUAL`): both members are `same_after_reference_identity`, with 0 unresolved
  references, 0 gaps and 0 candidate-only bytes. Same-length `a797c4d6…`
  (`DIFFER`): `ov10_F_2160` has 5 `different_identity` A4 references.
  `b67e0134…` (`DIFFER`): `ov10_F_2160` is 36 bytes longer, with
  branch/control-flow source-shape hypotheses.
- Seven-object control `ov04_F_0000` (`108846b1…`, `EQUAL`): 4 members are
  `same_bytes` and 3 are `same_after_reference_identity`. This includes two
  proven literal tails whose bytes are equal.
- ov11 `RP01` (members `5962`, `5C42` plus canonical bridges; interval
  `0x5962..0x5CEA`) against the retained layout experiment `0b66dd65…`: all 7
  members pair, and the order matches. Five bridges are
  `same_after_reference_identity`. `5962` has 1 unresolved call, which targets
  `4696` inside the unsymboled `_recovered` segment. `5C42` is 2 bytes shorter
  (`JSR d16(PC)` becomes `BSR.B`). The 44-byte gap `0x59E6..0x5A12` stays
  `unknown`. `_F_h11_59E6` (44 bytes), `_F_h11_4610` and `_recovered` (356
  bytes) are candidate-only. `exact_verdict` is `NOT_RUN_FOR_THIS_CACHE_KEY`.
  This experiment is not a check_unit candidate. It needs retained sources for
  `5962` and `5C42`, and independent evidence for the gap before any member
  can own it.

The original tool accepted absolute short operands as reference operands.
`diag.py` now excludes them. They cannot carry `HUNK_RELOC32`, so they remain
ordinary operand bytes.
