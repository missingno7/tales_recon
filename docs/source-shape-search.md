# Bounded source-shape search

`tools/shape_search.py` evaluates a short list of independently authored C
variants against one already-censused function. The manifest names the source
file, causal family, diagnostic scope, and one compiler profile for each
variant. The tool does not synthesize or rewrite C.

Example manifest:

```json
{
  "schema_version": 1,
  "function_id": "ov09_F_298E",
  "budget": {"max_variants": 3, "max_unique_compiles": 3},
  "variants": [
    {
      "id": "baseline-v15",
      "causal_family": "table-mask-register-allocation",
      "diagnostic_scope": "register_assignment",
      "source": "experiments/direct-recovery/ov09_F_298E-v15.c",
      "profile": "aztec36"
    },
    {
      "id": "row-register-hint",
      "causal_family": "table-mask-register-allocation",
      "diagnostic_scope": "register_assignment",
      "source": "experiments/worker-ov09-298e/register_row_value.c",
      "profile": "aztec36"
    }
  ]
}
```

The JSON object has a closed schema: additional or missing keys are rejected.
Variant source paths must point to existing `.c` files under `experiments/` or
`recovery/candidates/`. Each variant gets exactly one profile, avoiding a
hidden profile-by-variant product. The declared limits are bounded by hard
caps of 32 variants and 32 unique source/profile identities. The evaluator
preflights variants and then calls `check_function.check_many(...,
isolated=True, promote_equal=False)`. The verifier remains the authority for
exact `EQUAL`, `DIFFER`, or `BLOCKED` results. No exact result is promoted.

Use `--cached-only` to refuse the run unless every unique compiler identity is
already in the compiler cache. This allows examination of archived candidates
without starting a compiler worker or WinUAE job. Without that flag, cache
misses use the normal batched compiler oracle. Optional output reports can be
saved only below `experiments/` or `build/`.
Cached-only preflight rejects targets with same-overlay PC-relative callees,
because those comparisons require prepared-unit cache identities.

`diagnostic_scope` must use one of the current diagnostic categories:
`operand_width`, `register_assignment`, `frame_or_stack_reference`,
`a4_global_layout`, `pc_relative_layout`, `memory_reference_or_layout`,
`call_target_or_encoding`, `immediate_constant`, `unknown_codegen`,
`instruction_layout`, `branch_condition_or_kind`, `control_flow_target_or_edge`,
`control_flow_unresolved`, `control_flow_shape`, or
`data_ownership_review`.

The diagnostic layer is advisory and states `UNSUPPORTED` when the streams
cannot be independently bounded or decoded. A valid comparison may have no
hypotheses in the requested scope. Supported hypotheses
are evidence about generated structure, not recovered source facts. Ranking
puts exact `EQUAL` verdicts first, then keeps each causal-family and scope
group together. Within a group it uses diagnostic instruction similarity,
aligned instruction coverage, and conservative CFG target consistency,
followed by the exact comparator's mnemonic similarity and generated length.
Unsupported diagnostics sort after supported diagnostic evidence; the
evaluator does not substitute ordinary mnemonic similarity for a missing
diagnostic. Confidence labels describe diagnostic evidence and do not act as
distance scores. A single function comparison remains function-level evidence;
it does not prove object, HUNK, or overlay layout.

This schema is a deliberate bounded first step. It accepts explicit source
files only; automated text edits, generalized C mutation, and candidate
generation are outside the evaluator. Every new variant must remain a
separately reviewable hypothesis with a causal label and stated diagnostic
scope.

## Schema v2: recorded hypotheses

`schema_version: 2` keeps every v1 rule and requires four more variant keys, so
each compile trial answers one recorded, non-duplicate hypothesis:

- `parent`: an earlier variant id in the same manifest, a `.c` path under
  `experiments/` or `recovery/candidates/`, `ledger:N` (a prior trial line),
  a 64-hex compiler cache key, or `"none"` (every prediction is then
  unmeasurable).
- `suspected_cause` and `controlled_change`: text; the change should be one edit.
- `predicted_effect`: exactly `{"length_delta", "removed_candidate_only",
  "register_role_diffs", "note"}`. `length_delta` is the predicted candidate
  byte change (child minus parent), `removed_candidate_only` the predicted
  decrease in candidate-only instructions, `register_role_diffs` one of
  `fewer`/`same`/`more` for the `register_assignment` hypothesis count. Unused
  fields are `null`; at least one must be non-null.

After the exact comparison, the observed child-minus-parent delta is computed
from both diagnostics. Each predicted field is `confirmed` (exact equality),
`refuted`, `unmeasurable` or `not_predicted`. `removed_candidate_only` and
`register_role_diffs` need supported diagnostics on both sides. `length_delta`
needs only both compiled code-payload lengths. `diag` still reports that length
when it refuses alignment, for example for an original with PC-relative data
(`ORIGINAL_DATA_BOUNDARY_HAS_NO_MAPPED_CANDIDATE_BOUNDARY`). A failed compile
or a missing parent stays unmeasurable. The record's `prediction.measurement` is
`FULL_DIAGNOSTIC` or `PAYLOAD_LENGTH_ONLY`. The overall outcome is `confirmed`,
`partial`, `refuted` or `unmeasurable`. A parent variant uses its measurement
from the same run or its prior ledger record. A parent path, `ledger:N` or
cache key is re-measured from its cached compile. For a path, the lookup order
is the latest ledger record, the current compiler identity, then a retained
`recovery/ledger.json` attempt with byte-identical source. Parents are compiled
only with `--measure-parents`. That flag compiles an unmeasured path parent in
the same batch, inside `budget.max_unique_compiles`. The child record marks it
`parent_basis: PARENT_COMPILED_COUNTED_TRIAL` with `parent_compile`, and the
summary counts it as a compiler trial. Over budget or with `--cached-only`, the
parent stays unmeasurable with the reason. None of this affects
`EQUAL`/`DIFFER`/`BLOCKED`.

Duplicate detection hashes a shallow normalization: comments become one
space, literals are kept verbatim, whitespace runs outside literals collapse to
one space, and preprocessor directives stay on their own lines. There is no
token or semantic normalization. A duplicate (normalized source, profile)
within a manifest, or a variant identical to its parent path, rejects the
manifest. A (function, normalized source, profile) already present as a trial
in the ledger is not re-run; the output reports a pointer to the prior record.

The ledger defaults to ignored `build/recovery/hypotheses.jsonl`
(override with `--ledger` under `evidence/experiments/`, `experiments/` or
`build/`). It is a curated experiment record, not a generated census ledger:
refuted and duplicate hypotheses are retained, and `build/` is not tracked.
Records are appended under a lock file and never rewritten; a malformed or
truncated line refuses the ledger. Each `trial` record holds the timestamp,
function, manifest, variant, normalized and exact source hashes, profile,
cache key and hit flag, parent, hypothesis fields, exact verdict, observed
metrics and deltas, and prediction outcomes. Rejected duplicates are recorded
as `duplicate_rejected` records with the prior pointer. The duplicate check is
repeated under the ledger lock immediately before compiling. Each remaining
variant then receives an in-flight reservation under `build/hypothesis-inflight/`.
A concurrent identical hypothesis waits for that reservation and is then
rejected as a duplicate instead of compiling again. A reservation left by a
dead process is replaced and reported as `stale_reservations_replaced`. Cache
misses go through the coalescing compile queue (see [fleet](fleet.md)). The
ledger also accepts `fleet_intake` records from `tools/fleet.py`. They never
count as compiler trials. v1 manifests do not use the ledger.

For bounded workers, set `--ledger build/workers/NAME/hypotheses.jsonl`.
New trials also retain `emitted_identity`: separate profile, complete linked
CODE, all emitted object, and binding metadata hashes. Raw object hashes retain
fixup records even where their grammar is unsupported. The summary counts
distinct complete states and distinct CODE states separately. Syntactically
different sources with identical output constitute one emitted state; equal
CODE with different symbols, relocations, data allocation or object records
remains distinct. Failed compiles have no emitted identity. These hashes guide
stagnation handling only; promotion always performs the normal exact check.

```powershell
python tools/shape_search.py manifest-v2.json --cached-only
python tools/shape_search.py --ledger-summary ov09_F_298E
python tools/shape_search.py --ledger-summary --rescore   # read-only re-measurement
```

`--rescore` re-measures every recorded trial from cached compiles with the
current scorer and reports `predictions_rescored` plus the reasons for the
remaining unmeasurable trials. The ledger is not rewritten. On 2026-09-28 the
25 recorded trials showed 7 measurable predictions (6 confirmed, 1 refuted) and
18 unmeasurable. Fifteen of the unmeasurable trials were ov04_F_0536, whose
original has PC-relative data. `diag` refused the alignment there, and the
scorer discarded the payload length that `diag` had measured. Rescored, 17
are measurable: 6 confirmed, 6 partial and 5 refuted. The 8 still unmeasurable
are 4 with parent `none`, 3 failed compiles and 1 alignment-only prediction.

The summary reports compiler trials (distinct cache keys actually compiled),
cache hits, exact matches, exact matches from compiled trials per compiler
trial, prediction outcomes and rejected duplicates. Convergence is measured by
those counts, not by diagnostic similarity.
