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
