# Fleet task fn-ov10_F_2634 (function)

You are an autonomous worker on a historical Amiga 68k (Aztec C) reconstruction in `D:/Prog/tales_recon`. You have no memory beyond this prompt. Recover closed function ov10_F_2634 (1366 bytes)

Priority 40. Lease: worker `luna-fn-ov10_F_2634`, expires 2026-09-29T17:01:48+00:00 (renew: `python tools/fleet.py renew fn-ov10_F_2634 --worker luna-fn-ov10_F_2634`).

## First step (host liveness)
Run `python tools/fleet.py renew fn-ov10_F_2634 --worker luna-fn-ov10_F_2634` before anything else. The host is shared and heavily loaded: a single command can take 1-3 minutes to start and finish. Run commands one at a time (never batch several commands in parallel), wait on slow commands instead of terminating them, and keep outputs small. Do not read whole docs/*.json ledgers or long docs; this packet already carries the binding rules and target facts, so use targeted queries. Only if this `renew` command itself has still not returned after 10 minutes, stop and reply with one line: `TASK fn-ov10_F_2634 BLOCKED HOST_TOOLS_UNRESPONSIVE` (no result.json needed; the supervisor releases the lease).

## Rules (binding; from AGENTS.md)
- Historical reconstruction, not a source port. `assets/` is immutable oracle evidence. Never relock fixtures and never feed original code bytes into reconstructed outputs (no byte arrays, inline asm, placement directives or copied data standing in for code).
- Keep natural object/hunk/overlay layout as the target. Numeric overlay names are containers; do not invent semantic names or source filenames. Printable runs are candidates, not string boundaries. Unknown ownership stays visible. Runtime ABI identification is not library provenance.
- Do not edit tools/, tests/, docs/, evidence/, recovery/, src/ or assets/, do not hand-edit generated ledgers, do not run `census.py --write`, `function_census.py` or `type_evidence.py --write`, and do not commit.
- Write files ONLY under `experiments/fleet/fn-ov10_F_2634/`. The tools themselves append to build/compile-cache and to the hypothesis ledger; that is expected.
- Never promote: never run check_function.py/check_unit.py without `--isolated`; use the wrappers below. Never delete lock files. If a tool reports a stale lock, stop and report BLOCKED quoting the message.
- The exact verifier alone decides EQUAL. Diagnostics and similarity scores are advisory. Other workers share this checkout; do not touch other experiments/ directories.

## Origin
`{"constraints":[],"source":"ranked_frontier"}`

## Target facts
- `{"calls":["F_h00_8A46 A4_RELOCATED_JMP_STUB DISCOVERED","F_h00_8A68 A4_RELOCATED_JMP_STUB DISCOVERED","F_h00_30F0 A4_RELOCATED_JMP_STUB DISCOVERED","F_h00_34E0 A4_RELOCATED_JMP_STUB DISCOVERED x8","F_h10_22E6 PC_RELATIVE FUNCTION_CODE_MATCH","F_h00_463E A4_RELOCATED_JMP_STUB DISCOVERED"],"confidence":"HIGH","constraints":["SIZE_LIMIT"],"data":["G_h01_003C","G_h01_0054","G_h01_00A8","G_h01_014A","G_h01_0150","G_h01_060A","G_h01_0626","G_h01_0636","G_h01_0646","G_h01_0656","G_h01_4356","G_h01_46CA","G_h01_46CE","G_h01_46D2","G_h01_5392","G_h01_726C"],"end":"0x2B8A","extent":"CLOSED_CFG","hunk":10,"id":"ov10_F_2634","indirect":1,"instructions":376,"jump_tables":1,"more_calls":0,"more_data":19,"node":"ov10","pc_relative_data":0,"size":1366,"start":"0x2634","strings":0}`

## Declarations already used by canonical sources (candidate views, not provenance)
Paste-ready block: `experiments/fleet/fn-ov10_F_2634/canonical-declarations.h` (details: task.json `declaration_views`). Reuse these names, views and struct definitions unless a hypothesis needs another view; that view change is then the recorded controlled change. They compiled exactly elsewhere; they are not historical types, and access widths do not determine a type. 7 referenced symbols have canonical views (2 differ: F_h00_34E0, F_h00_463E); 29 have none.
```c
/* Declarations already used by canonical sources: candidate views, not provenance.
   Reuse them unless a hypothesis needs a different view (then that is the controlled change). */
extern long G_h01_46CA; /* 13x; w4 */
extern long G_h01_46CE; /* 15x; w4 */
extern long G_h01_46D2; /* 16x; w4 */
extern int F_h00_30F0(); /* 1x */
extern int F_h00_34E0(); /* 20x; alt void () x2 */
extern unsigned int F_h00_463E(); /* 4x; alt int () x3, long () x3 */
extern int F_h00_8A46(); /* 16x */
/* G_h01_060A: no canonical view */
/* G_h01_0626: no canonical view */
/* G_h01_0636: no canonical view */
/* G_h01_0646: no canonical view */
/* G_h01_0656: no canonical view */
/* G_h01_4356: inside G_h01_4274+226 (struct Table [64]) */
/* G_h01_5392: no canonical view; w4 */
/* G_h01_726C: no canonical view; w2 */
/* G_h01_726E: no canonical view; w2 */
/* G_h01_72A0: no canonical view; w1 */
/* G_h01_72A2: no canonical view; w2 */
/* G_h01_72A4: no canonical view; w2 */
/* G_h01_72D6: no canonical view; w1 */
/* G_h01_72D8: no canonical view; w2 */
/* G_h01_72DA: no canonical view; w2 */
/* G_h01_730C: no canonical view; w1 */
/* G_h01_741C: no canonical view */
/* G_h01_7452: no canonical view */
/* G_h01_74F4: no canonical view */
/* G_h01_7998: no canonical view; w4 */
/* G_h01_79A2: no canonical view; w1 */
/* G_h01_79A3: no canonical view; w1 */
/* G_h01_79A4: no canonical view; w1 */
/* G_h01_79A6: no canonical view; w1 */
/* G_h01_79AE: no canonical view; w2 */
/* G_h01_79B0: no canonical view; w2 */
/* G_h01_79B2: no canonical view; w2 */
/* F_h00_8A68: no canonical view */
/* F_h10_22E6: no canonical view */
```

## Prior hypotheses (do not repeat)
`{"summary":{"predictions":{},"shown":0,"trials":0,"verdicts":{}},"trials":[]}`

## Type evidence ov10_F_2634 (advisory)
`{"declaration_conflicts":0,"frame":["+8 w=[4] n=26","+12 w=[2] n=10","+14 w=[2] n=2"],"globals":["G_h01_003C w=[] rw={'UNKNOWN': 6}","G_h01_0054 w=[] rw={'UNKNOWN': 277}","G_h01_00A8 w=[] rw={'UNKNOWN': 97}","G_h01_014A w=[] rw={'UNKNOWN': 129}","G_h01_0150 w=[] rw={'UNKNOWN': 1}","G_h01_060A w=[] rw={}","G_h01_0626 w=[] rw={}","G_h01_0636 w=[] rw={}"]}`

## Protocol
1. Inspect evidence (read-only): `python tools/grinder.py facts ID --max-instructions 2000 --max-bytes 2000000 > experiments/fleet/fn-ov10_F_2634/facts-ID.json` then query that file (full disassembly/CFG/relocations), `python tools/diag.py ID --cache-key KEY` for any cached key, `python tools/type_evidence.py --function ID`, `python tools/shape_search.py --ledger-summary ID`, docs/source-shape-search.md, docs/m68k-diagnostics.md.
2. BEFORE compiling, record each hypothesis with a machine-checkable prediction. Write a schema v2 manifest `experiments/fleet/fn-ov10_F_2634/manifest-NN.json` (docs/source-shape-search.md): every variant has parent, suspected_cause, controlled_change and predicted_effect {length_delta, removed_candidate_only, register_role_diffs, note}. Name a measured parent (an earlier variant, a compiled .c path, `ledger:N` or a 64-hex cache key); parent `none` leaves every prediction unmeasurable. Sources: `experiments/fleet/fn-ov10_F_2634/*.c` (self-contained K&R C defining `recovered(...)`, mechanical G_hNN_XXXX/F_hNN_XXXX externs).
3. Each variant makes ONE controlled change from its parent. Do not resubmit a hypothesis listed under prior hypotheses; the ledger rejects normalized duplicates and returns the earlier record, which you must read instead.
4. Compile via: `python tools/shape_search.py experiments/fleet/fn-ov10_F_2634/manifest-NN.json --output-dir experiments/fleet/fn-ov10_F_2634/runs --json` (isolated; records the ledger; add `--measure-parents` to compile an unmeasured parent as a counted trial). For owned CODE data or m.lib only: `python tools/fleet.py verify-function ID SRC --profile P [--owned-code-data] [--with-m-lib] --output-dir experiments/fleet/fn-ov10_F_2634/runs`.
   Compiles are queued and batched across workers (a cache miss may wait minutes); cache hits are instant. Never loop on a failing tool.
5. Budget: at most 24 compiler trials and 6 variants per manifest. Stop at an exact EQUAL, at budget, or after three consecutive refuted predictions in one causal family without new evidence (switch family once, then report).
6. Write `experiments/fleet/fn-ov10_F_2634/result.json` exactly per the schema below using Python `json.dump` (UTF-8, no BOM; never an empty file), check it with `python tools/fleet.py intake fn-ov10_F_2634 --dry-run`, fix any REJECTED reason, then reply with one line: `TASK fn-ov10_F_2634 <STATUS> experiments/fleet/fn-ov10_F_2634/result.json`.

## result.json (closed schema; intake re-verifies every EQUAL claim)
```json
{"schema_version":1,"task_id":"fn-ov10_F_2634","worker":"<your -n name>",
 "status":"EQUAL_CANDIDATE|NEAR|BLOCKED|NEEDS_EVIDENCE",
 "target":"ov10_F_2634",
 "best":null or {"source":"experiments/fleet/fn-ov10_F_2634/<file>.c","profile":"aztec36","cache_key":"<64 hex>",
   "verdict":"EQUAL|DIFFER|BLOCKED","verifier":"check_function","entry":"<evidence id of the member compiled as recovered(), e.g. ov10_F_2634>",
   "options":["owned_code_data","with_m_lib"],"expected_length":0,"actual_length":0},
 "hypotheses":[{"id":"h1","statement":"...","outcome":"confirmed|refuted|partial|unmeasurable|untested","evidence":"ledger line / report path"}],
 "compile_trials":0,"ledger_lines":[],
 "explanation":"what the evidence now shows (<=1200 chars)",
 "proposed_blocker":null or {"mechanism":"UPPER_SNAKE_CASE","text":"blocker text for docs/blockers.json curation"}}
```
EQUAL_CANDIDATE needs best.verdict EQUAL from an isolated run. NEAR needs best. BLOCKED needs proposed_blocker. NEEDS_EVIDENCE names the missing evidence in explanation. `entry` is required for check_unit and equals the target for check_function.
For check_unit with several new members, `best` may add `"members":{"<other member id>":"experiments/fleet/fn-ov10_F_2634/<file>.c"}` (the `--member` sources; never the entry).
If `best` was compiled with `--object-group`, add `"object_groups":[["<ID>","<ID>"]]` exactly as passed (intake re-verifies with them).
