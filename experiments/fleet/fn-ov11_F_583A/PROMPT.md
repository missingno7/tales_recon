# Fleet task fn-ov11_F_583A (function)

You are an autonomous worker on a historical Amiga 68k (Aztec C) reconstruction in `D:/Prog/tales_recon`. You have no memory beyond this prompt. Continue near-match ov11_F_583A (best mnemonic similarity 0.988 over 3 attempts)

Priority 15. Lease: worker `luna-fn-ov11_F_583A`, expires 2026-09-28T18:43:30+00:00 (renew: `python tools/fleet.py renew fn-ov11_F_583A --worker luna-fn-ov11_F_583A`).

## Rules (binding; from AGENTS.md)
- Historical reconstruction, not a source port. `assets/` is immutable oracle evidence. Never relock fixtures and never feed original code bytes into reconstructed outputs (no byte arrays, inline asm, placement directives or copied data standing in for code).
- Keep natural object/hunk/overlay layout as the target. Numeric overlay names are containers; do not invent semantic names or source filenames. Printable runs are candidates, not string boundaries. Unknown ownership stays visible. Runtime ABI identification is not library provenance.
- Do not edit tools/, tests/, docs/, evidence/, recovery/, src/ or assets/, do not hand-edit generated ledgers, do not run `census.py --write`, `function_census.py` or `type_evidence.py --write`, and do not commit.
- Write files ONLY under `experiments/fleet/fn-ov11_F_583A/`. The tools themselves append to build/compile-cache and to the hypothesis ledger; that is expected.
- Never promote: never run check_function.py/check_unit.py without `--isolated`; use the wrappers below. Never delete lock files. If a tool reports a stale lock, stop and report BLOCKED quoting the message.
- The exact verifier alone decides EQUAL. Diagnostics and similarity scores are advisory. Other workers share this checkout; do not touch other experiments/ directories.

## Origin
`{"attempts":3,"best_similarity":0.9882,"constraints":["UNRECOVERED_LOCAL_DEPENDENCY"],"source":"attempt_ledger"}`

## Target facts
- `{"calls":["F_h11_5962 PC_RELATIVE DISCOVERED"],"confidence":"HIGH","constraints":["UNRECOVERED_LOCAL_DEPENDENCY"],"data":["G_h01_8B1C"],"end":"0x5962","extent":"CLOSED_CFG","hunk":11,"id":"ov11_F_583A","indirect":0,"instructions":85,"jump_tables":0,"more_calls":0,"more_data":0,"node":"ov11","pc_relative_data":0,"size":296,"start":"0x583A","strings":0}`

## Prior verifier attempts ov11_F_583A (3 total, latest 3)
- `{"actual":298,"cache_key":"87ff5c50b04be95481a62d0a4f33a3d89c29ed065de9499b7c8464a8f4c28e26","expected":296,"first_diff":23,"profile":"aztec36","similarity":0.9882,"source":"recovery/candidates/ov11_F_583A/6deb288a087599485acb41063b8d54f77ef332212b1dad36d8ed49a8a9e06ef3.c","verdict":"DIFFER"}`
- `{"actual":298,"cache_key":"c2fa57acbb5b0ad40929c511574d8d8df9f75f168a59d3e693b1a83aeb3aedcb","expected":296,"first_diff":23,"profile":"aztec36","similarity":0.9882,"source":"recovery/candidates/ov11_F_583A/fafd040863a9460b145b3e8743da57ebb53c2be7dd8d1185db02f510d80206d1.c","verdict":"DIFFER"}`
- `{"actual":298,"cache_key":"1976729719a4d8c305631b23dc4e9a4fdbff121f14b7eb8be172b752c58cb0fc","expected":296,"first_diff":209,"profile":"aztec36","similarity":0.9882,"source":"recovery/candidates/ov11_F_583A/528572f0a0a9bac9eb036fb522030ee983185a015aaaab3e14a73722e2716a8b.c","verdict":"DIFFER"}`

## Prior hypotheses (do not repeat)
`{"summary":{"predictions":{},"shown":0,"trials":0,"verdicts":{}},"trials":[]}`

## Cached diagnostic of best attempt ov11_F_583A (advisory)
key `87ff5c50b04be95481a62d0a4f33a3d89c29ed065de9499b7c8464a8f4c28e26`
`{"alignment_counts":{"actual_only":0,"expected_only":0,"paired":85},"extents":{"candidate":298,"expected":296},"first_nonreference_divergence":{"actual":{"mnemonic":"jsr","offset":260,"operands":"-$7ffe(a4)"},"confidence":"low","expected":{"mnemonic":"bsr.b","offset":260,"operands":"$128"},"note":"First coarse-aligned instruction-shape difference; operand reference identity is not evaluated."},"hypotheses":[{"category":"call_target_or_encoding","count":1,"evidence":[]},{"category":"frame_or_stack_reference","count":30,"evidence":[]}],"instruction_similarity":0.9882,"recommended_search_scope":["reference identity and data-boundary evidence"],"register_trace":{"first_conflict":null,"remapped":[]},"status":"DIAGNOSTIC_ONLY"}`

## Type evidence ov11_F_583A (advisory)
`{"declaration_conflicts":0,"frame":["+8 w=[2] n=9","+10 w=[2] n=9","+12 w=[2] n=2","+14 w=[2] n=2","+16 w=[2] n=2"],"globals":["G_h01_8B1C w=[] rw={}"]}`

## Protocol
1. Inspect evidence (read-only): `python tools/grinder.py facts ID` (full disassembly/CFG/relocations), `python tools/diag.py ID --cache-key KEY` for any cached key, `python tools/type_evidence.py --function ID`, `python tools/shape_search.py --ledger-summary ID`, docs/source-shape-search.md, docs/m68k-diagnostics.md.
2. BEFORE compiling, record each hypothesis with a machine-checkable prediction. Write a schema v2 manifest `experiments/fleet/fn-ov11_F_583A/manifest-NN.json` (docs/source-shape-search.md): every variant has parent, suspected_cause, controlled_change and predicted_effect {length_delta, removed_candidate_only, register_role_diffs, note}. Sources: `experiments/fleet/fn-ov11_F_583A/*.c` (self-contained K&R C defining `recovered(...)`, mechanical G_hNN_XXXX/F_hNN_XXXX externs).
3. Each variant makes ONE controlled change from its parent. Do not resubmit a hypothesis listed under prior hypotheses; the ledger rejects normalized duplicates and returns the earlier record, which you must read instead.
4. Compile via: `python tools/shape_search.py experiments/fleet/fn-ov11_F_583A/manifest-NN.json --output-dir experiments/fleet/fn-ov11_F_583A/runs --json` (isolated; records the ledger). For owned CODE data or m.lib only: `python tools/fleet.py verify-function ID SRC --profile P [--owned-code-data] [--with-m-lib] --output-dir experiments/fleet/fn-ov11_F_583A/runs`.
   Compiles are queued and batched across workers (a cache miss may wait minutes); cache hits are instant. Never loop on a failing tool.
5. Budget: at most 24 compiler trials and 6 variants per manifest. Stop at an exact EQUAL, at budget, or after three consecutive refuted predictions in one causal family without new evidence (switch family once, then report).
6. Write `experiments/fleet/fn-ov11_F_583A/result.json` exactly per the schema below, then reply with one line: `TASK fn-ov11_F_583A <STATUS> experiments/fleet/fn-ov11_F_583A/result.json`.

## result.json (closed schema; intake re-verifies every EQUAL claim)
```json
{"schema_version":1,"task_id":"fn-ov11_F_583A","worker":"<your -n name>",
 "status":"EQUAL_CANDIDATE|NEAR|BLOCKED|NEEDS_EVIDENCE",
 "target":"ov11_F_583A",
 "best":null or {"source":"experiments/fleet/fn-ov11_F_583A/<file>.c","profile":"aztec36","cache_key":"<64 hex>",
   "verdict":"EQUAL|DIFFER|BLOCKED","verifier":"check_function","entry":"<member compiled as recovered>",
   "options":["owned_code_data","with_m_lib"],"expected_length":0,"actual_length":0},
 "hypotheses":[{"id":"h1","statement":"...","outcome":"confirmed|refuted|partial|unmeasurable|untested","evidence":"ledger line / report path"}],
 "compile_trials":0,"ledger_lines":[],
 "explanation":"what the evidence now shows (<=1200 chars)",
 "proposed_blocker":null or {"mechanism":"UPPER_SNAKE_CASE","text":"blocker text for docs/blockers.json curation"}}
```
EQUAL_CANDIDATE needs best.verdict EQUAL from an isolated run. NEAR needs best. BLOCKED needs proposed_blocker. NEEDS_EVIDENCE names the missing evidence in explanation. `entry` is required for check_unit and equals the target for check_function.
