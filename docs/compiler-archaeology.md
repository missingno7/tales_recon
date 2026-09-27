# Compiler archaeology: measured pipeline improvement

This work improves search feedback, not the exact proof policy. The immutable
game remains a comparison oracle. No diagnostic category, score, type clue, or
dependency plan assigns source ownership.

## Baseline

The September 2026 checkout has 652 candidate functions, 252 closed CFGs,
115 canonical recovered functions and 22,242 verified function bytes. The
canonical ledger retains 482 attempts across 112 function IDs: 275 DIFFER,
115 EQUAL and 92 BLOCKED. These historical attempt counts are not a controlled
model-success experiment. There are 370 retained candidate source files.

At the default 256-byte bound, `grinder.frontier(limit=256)` finds zero eligible
functions. Its first-reason deferrals are:

| First reason | Candidates |
| --- | ---: |
| Uncertain extent | 389 |
| Resident deferred | 71 |
| Size limit | 48 |
| Unrecovered local dependency | 8 |
| Unknown call limit | 3 |

Seven explicit blockers remain: three byte-return ABI cases, two cyclic local
call cases, one persistent code-generation case and one private FFP ABI case.
First-reason counts hide overlapping constraints; they do not mean that lifting
a size threshold makes all 48 larger functions safe to recover independently.

The immediate overlay frontier is much smaller than the resident-heavy total:
82 unrecovered overlay candidates, of which 66 have closed CFGs and 16 uncertain
extents. Within those 82, overlapping constraints include 65 size-limit cases,
49 unresolved local dependencies, 55 noncontiguous-unit flags, 44 data-reference
limit cases and 22 PC-relative-data ownership cases. Context, dependency and
data proof obligations therefore dominate the practical overlay queue; the
whole-program count of uncertain resident entries must not obscure that result.

## Concrete feedback defects

`recovery_state.facts()` collected prior source text by source hash but populated
`previous_sources` with the attempt summary list instead. This deprived generic
consumers of the intended source map and made the local fact packer's dictionary
lookup fail on a revision. The fix passes the actual source map. A regression
exercises fact creation through local prompt representation. On the retained
`ov14_F_0412` case, five previous receipts resolve to three source entries and
the current 438-character candidate reaches the prompt.

The local prompt also instructed the model to use `unsigned int` externs
unconditionally. It now asks for access-based widths and explicitly preserves
signedness ambiguity. Neither change proves why all previous proposals failed;
both remove concrete obstacles to evidence-directed revision.

## Implemented search layer

`tools/diag.py` compares a closed original function with the complete independently
bounded CODE contribution in a validated compiler cache entry. It aligns decoded
instructions across insertions, pairs basic blocks, checks branch conditions,
targets and fallthrough correspondence, and exposes register-role, width, stack,
constant and reference differences. All classifications are advisory. Unsupported
unit/data boundaries are reported rather than sliced using original lengths.
The tool does not perform semantic equivalence or register-liveness proof.

`tools/type_evidence.py` generates `evidence/types.json` separately from census
metrics. It records A4 access widths/address-taking, register-linked extension
context, A5 frame accesses, and differences among supported source declarations.
Compact function queries carry program-wide observations for touched globals,
with input/source freshness checks and explicit omissions.
The current report covers 1,783 A4 offsets, 7,885 accesses and 981 A5 frame
accesses. It retains 55 declaration differences across 18 mechanical symbols:
43 require struct-view review, five concern pointer/scalar views, four concern
array shape, and three concern other views. These are not 55 proven type errors.

`tools/recovery_plan.py` exposes overlapping constraints and bounded review
packages. Exhausted grinder runs use `tools/recovery_feedback.py` to execute up
to four cached diagnoses, retain their results in the normal run/report, and
return `RECOVERY_REVIEW_REQUIRED`. This is an automatic transition into analysis,
not an automatic claim that a source unit is ready to compile. Requested scope
and eligibility limits are preserved; no blocked function is silently requeued.

`tools/shape_search.py` batches explicitly authored, budgeted variants through
the existing isolated exact verifier and ranks the diagnostic results. It uses
the existing compiler cache and can refuse cache misses. Source transformation
generation is deliberately deferred: the first experiment establishes bounded
evaluation before introducing a mutation language.

The sibling tools were inspected locally. Stunts' `blockdiff`/`diagnostics` and
`typeinfer` motivated shift-tolerant advisory evidence and shared constraints;
Icy Tower's `diag` motivated separating source structure from compiler context;
Empires' `probe_tu`/`audit_tu_flags` motivated explicit whole-unit hypotheses and
source/flag provenance. Their x86-specific register, relocation and compiler-dump
logic was not transplanted into the M68k verifier.

## Measured outcome

| Measurement | Before | After this pass |
| --- | ---: | ---: |
| Default automatically eligible functions | 0 | 0 |
| Canonical recovered functions | 115 | 115 |
| Verified function bytes | 22,242 | 22,242 |
| Bounded review packages on exhaustion | none in the run | 13 available; default preview 8 |
| New compiler-worker invocations in the variant experiment | — | 0 |
| New promotions in the variant experiment | — | 0 |

The expanded frontier observes 124 unresolved-local-dependency cases, 127
noncontiguous-unit flags and 49 PC-relative-data ownership cases. These overlap
with extent, size and other constraints. The counts describe current ranking
rules, not proven minimal translation units.

The retained `ov09_F_298E` v15 candidate is 672 bytes versus the original 660.
Diagnostics align 183 instructions, isolate six candidate-only instructions,
pair 32 blocks, and find 25 consistent branch-target checks. Repeated index and
result register roles differ. A4/call binding observations remain separate and
unproved. This narrows an experiment toward temporary lifetime/expression shape;
it does not establish source semantics or prescribe the historical declaration.

The bounded cache-only experiment ranks three independent ov09 variants 98,
96 and 89 while the authoritative verifier returns DIFFER for every one.
The reproducible manifest, hashes, cache keys and results are retained in
`evidence/experiments/source-shape-search-baseline.json`.

The scoped exhaustion review delivers the ov09 type evidence in 4,889 JSON bytes
and its compiler diagnostic in 4,655 bytes, without dropping either optional
section or invoking a compiler/model. The exact `ov14_F_03AE` control aligns all
five instructions without insertions; two A4 displacement observations remain
unresolved because diagnostics do not normalize reference identities. The
integrated review and control are retained in
`evidence/experiments/recovery-feedback-baseline.json`.

The ov11 cycle is now a concrete review package with a 44-byte unclassified
gap, missing retained member source, and canonical callees outside its interval.
It remains unready for a complete source-unit proof. The snapshot is in
`evidence/experiments/recovery-plan.json`.

These measurements establish improved feedback and routing, not a higher exact
match rate. No new model proposal trial was run, and no declaration was silently
replaced. The next controlled experiment should author a small set of ov09
temporary/index-width variants using the new feedback, then compare exact
matches per compiler trial. A subsequent unit diagnostic must map member/literal
boundaries independently before extending this alignment to compact linked units.
That independently bounded unit diagnostic is the next highest-leverage general
mechanism: the measured overlay dependency frontier is broader than the isolated
near-match set. SCCs are useful review seeds, not evidence of original translation
unit boundaries or of the smallest compiler-coupled component.

## Boundaries and deferred work

Diagnostics must compare complete independently bounded contributions, tolerate
instruction shifts for alignment, and retain unresolved reference identities.
They must not mask a changed branch target or label graph similarity semantic
equivalence. Exact acceptance stays in the existing function/unit verifiers.

Shared declarations are candidate source views, not historical type provenance.
Memory access widths do not uniquely determine scalar type, array extent,
signedness, or object boundaries. Unit planning must keep unrecovered members
and unclaimed gaps explicit; normal compiler/linker output must supply every
claimed byte.

See [the AJ/FFP and DOS assessment](fixup-and-dos-assessment.md) for why a new
fixup parser and automatic cross-architecture matcher were deferred. The AJ
experiments do not yet establish a grammar, and DOS matches cannot prove Amiga
call binding. A controlled AJ reference matrix is a separate bounded follow-up.

## Validation

`python tools/census.py --write` and `--check` regenerate and verify all 18
baseline evidence documents. `python tools/type_evidence.py --check` verifies the
separate curated-evidence-derived report. The full analysis test suite passes
226 tests, including independent diagnostic edge-case tests, existing exact
function/unit proof tests, feedback-budget tests and bounded search tests.
No game build exists yet. Assets, canonical recovered sources, fixture locks,
recovery receipts and the exact comparison implementation are unchanged.
