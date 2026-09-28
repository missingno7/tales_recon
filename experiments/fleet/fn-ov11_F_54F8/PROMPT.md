# Fleet task fn-ov11_F_54F8 (function)

You are an autonomous worker on a historical Amiga 68k (Aztec C) reconstruction in `D:/Prog/tales_recon`. You have no memory beyond this prompt. Continue near-match ov11_F_54F8 (best mnemonic similarity 1.000 over 2 attempts)

Priority 15. Lease: worker `luna-fn-ov11_F_54F8`, expires 2026-09-28T18:43:30+00:00 (renew: `python tools/fleet.py renew fn-ov11_F_54F8 --worker luna-fn-ov11_F_54F8`).

## Rules (binding; from AGENTS.md)
- Historical reconstruction, not a source port. `assets/` is immutable oracle evidence. Never relock fixtures and never feed original code bytes into reconstructed outputs (no byte arrays, inline asm, placement directives or copied data standing in for code).
- Keep natural object/hunk/overlay layout as the target. Numeric overlay names are containers; do not invent semantic names or source filenames. Printable runs are candidates, not string boundaries. Unknown ownership stays visible. Runtime ABI identification is not library provenance.
- Do not edit tools/, tests/, docs/, evidence/, recovery/, src/ or assets/, do not hand-edit generated ledgers, do not run `census.py --write`, `function_census.py` or `type_evidence.py --write`, and do not commit.
- Write files ONLY under `experiments/fleet/fn-ov11_F_54F8/`. The tools themselves append to build/compile-cache and to the hypothesis ledger; that is expected.
- Never promote: never run check_function.py/check_unit.py without `--isolated`; use the wrappers below. Never delete lock files. If a tool reports a stale lock, stop and report BLOCKED quoting the message.
- The exact verifier alone decides EQUAL. Diagnostics and similarity scores are advisory. Other workers share this checkout; do not touch other experiments/ directories.

## Origin
`{"attempts":2,"best_similarity":1.0,"constraints":["UNRECOVERED_LOCAL_DEPENDENCY","NONCONTIGUOUS_LOCAL_UNIT"],"source":"attempt_ledger"}`

## Target facts
- `{"calls":["F_h11_4696 PC_RELATIVE FUNCTION_CODE_MATCH","F_h11_5962 PC_RELATIVE DISCOVERED x3"],"confidence":"HIGH","constraints":["UNRECOVERED_LOCAL_DEPENDENCY","NONCONTIGUOUS_LOCAL_UNIT"],"data":["G_h01_3724"],"end":"0x55B8","extent":"CLOSED_CFG","hunk":11,"id":"ov11_F_54F8","indirect":0,"instructions":52,"jump_tables":0,"more_calls":0,"more_data":0,"node":"ov11","pc_relative_data":0,"size":192,"start":"0x54F8","strings":0}`

## Prior verifier attempts ov11_F_54F8 (2 total, latest 2)
- `{"actual":192,"cache_key":"450b1d5617e7f07137422c707dff306ae6a731ebc1a4f1fc745afa5d87ffb4c9","expected":192,"first_diff":11,"profile":"aztec36","similarity":1.0,"source":"recovery/candidates/ov11_F_54F8/342304823be389939054f977493078c1b80c051524a14e4c2318b1e2e3514dd8.c","verdict":"DIFFER"}`
- `{"actual":192,"cache_key":"691b01eddda59844c04a44d950440c648dad8103552284ccd0ce14ab49d62a38","expected":192,"first_diff":97,"profile":"aztec36","similarity":1.0,"source":"recovery/candidates/ov11_F_54F8/df9ae8495f45ded7b66d35bbd3be77804507e1dc03da71d214cce3d3986fa29c.c","verdict":"DIFFER"}`

## Prior hypotheses (do not repeat)
`{"summary":{"predictions":{},"shown":0,"trials":0,"verdicts":{}},"trials":[]}`

## Cached diagnostic of best attempt ov11_F_54F8 (advisory)
key `450b1d5617e7f07137422c707dff306ae6a731ebc1a4f1fc745afa5d87ffb4c9`
`{"alignment_counts":{"actual_only":0,"expected_only":0,"paired":52},"extents":{"candidate":192,"expected":192},"first_nonreference_divergence":{"actual":{"mnemonic":"jsr","offset":96,"operands":"-$7ffe(a4)"},"confidence":"low","expected":{"mnemonic":"jsr","offset":96,"operands":"$fffff19e(pc)"},"note":"First coarse-aligned instruction-shape difference; operand reference identity is not evaluated."},"hypotheses":[{"category":"call_target_or_encoding","count":4,"evidence":[]},{"category":"immediate_constant","count":1,"evidence":[]},{"category":"memory_reference_or_layout","count":6,"evidence":[]},{"category":"register_assignment","count":4,"evidence":[]}],"instruction_similarity":0.9231,"recommended_search_scope":["register roles or temporary lifetime"],"register_trace":{"first_conflict":null,"remapped":[]},"status":"DIAGNOSTIC_ONLY"}`

## Type evidence ov11_F_54F8 (advisory)
`{"declaration_conflicts":1,"frame":["+8 w=[2] n=1","+10 w=[2] n=3"],"globals":["G_h01_3724 w=[] rw={}"]}`

## Protocol
1. Inspect evidence (read-only): `python tools/grinder.py facts ID` (full disassembly/CFG/relocations), `python tools/diag.py ID --cache-key KEY` for any cached key, `python tools/type_evidence.py --function ID`, `python tools/shape_search.py --ledger-summary ID`, docs/source-shape-search.md, docs/m68k-diagnostics.md.
2. BEFORE compiling, record each hypothesis with a machine-checkable prediction. Write a schema v2 manifest `experiments/fleet/fn-ov11_F_54F8/manifest-NN.json` (docs/source-shape-search.md): every variant has parent, suspected_cause, controlled_change and predicted_effect {length_delta, removed_candidate_only, register_role_diffs, note}. Sources: `experiments/fleet/fn-ov11_F_54F8/*.c` (self-contained K&R C defining `recovered(...)`, mechanical G_hNN_XXXX/F_hNN_XXXX externs).
3. Each variant makes ONE controlled change from its parent. Do not resubmit a hypothesis listed under prior hypotheses; the ledger rejects normalized duplicates and returns the earlier record, which you must read instead.
4. Compile via: `python tools/shape_search.py experiments/fleet/fn-ov11_F_54F8/manifest-NN.json --output-dir experiments/fleet/fn-ov11_F_54F8/runs --json` (isolated; records the ledger). For owned CODE data or m.lib only: `python tools/fleet.py verify-function ID SRC --profile P [--owned-code-data] [--with-m-lib] --output-dir experiments/fleet/fn-ov11_F_54F8/runs`.
   Compiles are queued and batched across workers (a cache miss may wait minutes); cache hits are instant. Never loop on a failing tool.
5. Budget: at most 24 compiler trials and 6 variants per manifest. Stop at an exact EQUAL, at budget, or after three consecutive refuted predictions in one causal family without new evidence (switch family once, then report).
6. Write `experiments/fleet/fn-ov11_F_54F8/result.json` exactly per the schema below, then reply with one line: `TASK fn-ov11_F_54F8 <STATUS> experiments/fleet/fn-ov11_F_54F8/result.json`.

## result.json (closed schema; intake re-verifies every EQUAL claim)
```json
{"schema_version":1,"task_id":"fn-ov11_F_54F8","worker":"<your -n name>",
 "status":"EQUAL_CANDIDATE|NEAR|BLOCKED|NEEDS_EVIDENCE",
 "target":"ov11_F_54F8",
 "best":null or {"source":"experiments/fleet/fn-ov11_F_54F8/<file>.c","profile":"aztec36","cache_key":"<64 hex>",
   "verdict":"EQUAL|DIFFER|BLOCKED","verifier":"check_function","entry":"<member compiled as recovered>",
   "options":["owned_code_data","with_m_lib"],"expected_length":0,"actual_length":0},
 "hypotheses":[{"id":"h1","statement":"...","outcome":"confirmed|refuted|partial|unmeasurable|untested","evidence":"ledger line / report path"}],
 "compile_trials":0,"ledger_lines":[],
 "explanation":"what the evidence now shows (<=1200 chars)",
 "proposed_blocker":null or {"mechanism":"UPPER_SNAKE_CASE","text":"blocker text for docs/blockers.json curation"}}
```
EQUAL_CANDIDATE needs best.verdict EQUAL from an isolated run. NEAR needs best. BLOCKED needs proposed_blocker. NEEDS_EVIDENCE names the missing evidence in explanation. `entry` is required for check_unit and equals the target for check_function.
