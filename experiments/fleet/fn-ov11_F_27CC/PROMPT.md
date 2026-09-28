# Fleet task fn-ov11_F_27CC (function)

You are an autonomous worker on a historical Amiga 68k (Aztec C) reconstruction in `D:/Prog/tales_recon`. You have no memory beyond this prompt. Recover closed function ov11_F_27CC (622 bytes)

Priority 44. Lease: worker `luna-fn-ov11_F_27CC`, expires 2026-09-29T04:11:17+00:00 (renew: `python tools/fleet.py renew fn-ov11_F_27CC --worker luna-fn-ov11_F_27CC`).

## First step (host liveness)
Run `python tools/fleet.py renew fn-ov11_F_27CC --worker luna-fn-ov11_F_27CC` before anything else. The host is shared and heavily loaded: a single command can take 1-3 minutes to start and finish. Run commands one at a time (never batch several commands in parallel), wait on slow commands instead of terminating them, and keep outputs small. Do not read whole docs/*.json ledgers or long docs; this packet already carries the binding rules and target facts, so use targeted queries. Only if this `renew` command itself has still not returned after 10 minutes, stop and reply with one line: `TASK fn-ov11_F_27CC BLOCKED HOST_TOOLS_UNRESPONSIVE` (no result.json needed; the supervisor releases the lease).

## Rules (binding; from AGENTS.md)
- Historical reconstruction, not a source port. `assets/` is immutable oracle evidence. Never relock fixtures and never feed original code bytes into reconstructed outputs (no byte arrays, inline asm, placement directives or copied data standing in for code).
- Keep natural object/hunk/overlay layout as the target. Numeric overlay names are containers; do not invent semantic names or source filenames. Printable runs are candidates, not string boundaries. Unknown ownership stays visible. Runtime ABI identification is not library provenance.
- Do not edit tools/, tests/, docs/, evidence/, recovery/, src/ or assets/, do not hand-edit generated ledgers, do not run `census.py --write`, `function_census.py` or `type_evidence.py --write`, and do not commit.
- Write files ONLY under `experiments/fleet/fn-ov11_F_27CC/`. The tools themselves append to build/compile-cache and to the hypothesis ledger; that is expected.
- Never promote: never run check_function.py/check_unit.py without `--isolated`; use the wrappers below. Never delete lock files. If a tool reports a stale lock, stop and report BLOCKED quoting the message.
- The exact verifier alone decides EQUAL. Diagnostics and similarity scores are advisory. Other workers share this checkout; do not touch other experiments/ directories.

## Origin
`{"constraints":["NONCONTIGUOUS_LOCAL_UNIT"],"source":"ranked_frontier"}`

## Target facts
- `{"calls":["F_h11_25D6 PC_RELATIVE FUNCTION_CODE_MATCH","F_h00_8B88 A4_RELOCATED_JMP_STUB DISCOVERED x5","F_h00_8B76 A4_RELOCATED_JMP_STUB DISCOVERED","F_h00_8B4C A4_RELOCATED_JMP_STUB DISCOVERED x4","F_h00_8AA8 A4_RELOCATED_JMP_STUB DISCOVERED x4","F_h00_34E0 A4_RELOCATED_JMP_STUB DISCOVERED x3","F_h00_09C0 A4_RELOCATED_JMP_STUB DISCOVERED x3"],"confidence":"HIGH","constraints":["NONCONTIGUOUS_LOCAL_UNIT"],"data":["G_h01_0018","G_h01_0054","G_h01_0162","G_h01_01A4","G_h01_01B6","G_h01_01BC","G_h01_46CA","G_h01_46E1","G_h01_46E6","G_h01_5370","G_h01_8A3C","G_h01_94AC","G_h01_94AE","G_h01_94C0","G_h01_9F92","G_h01_9F96"],"end":"0x2A3A","extent":"CLOSED_CFG","hunk":11,"id":"ov11_F_27CC","indirect":0,"instructions":188,"jump_tables":0,"more_calls":0,"more_data":1,"node":"ov11","pc_relative_data":0,"size":622,"start":"0x27CC","strings":0}`

## Declarations already used by canonical sources (candidate views, not provenance)
Paste-ready block: `experiments/fleet/fn-ov11_F_27CC/canonical-declarations.h` (details: task.json `declaration_views`). Reuse these names, views and struct definitions unless a hypothesis needs another view; that view change is then the recorded controlled change. They compiled exactly elsewhere; they are not historical types, and access widths do not determine a type. 18 referenced symbols have canonical views (8 differ: G_h01_8A3C, G_h01_94AE, G_h01_94C0, F_h00_09C0, F_h00_34E0, F_h00_8AA8 ...); 0 have none.
```c
/* Declarations already used by canonical sources: candidate views, not provenance.
   Reuse them unless a hypothesis needs a different view (then that is the controlled change). */
extern long G_h01_46CA; /* 11x; w4 */
extern char G_h01_46E1; /* 4x; w1 */
extern long G_h01_46E6; /* 4x; w4 */
extern char *G_h01_5370; /* 8x; w4 */
extern int G_h01_8A3C; /* 5x; alt short x1; w2 */
extern int G_h01_94AC; /* 1x; w2 */
extern int G_h01_94AE; /* 6x; alt short x2; w2 */
extern int G_h01_94C0; /* 8x; alt short x2; w2 */
extern long G_h01_9F92; /* 1x; w4 */
extern long G_h01_9F96; /* 1x; w4 */
extern long G_h01_9F9A; /* 1x; w4 */
extern int F_h00_09C0(); /* 4x; alt void () x1 */
extern int F_h00_34E0(); /* 18x; alt void () x2 */
extern int F_h00_8AA8(); /* 5x; alt void () x1 */
extern int F_h00_8B4C(); /* 5x; alt void () x1 */
extern void F_h00_8B76(); /* 1x */
extern int F_h00_8B88(); /* 6x; alt void () x1 */
extern int F_h11_25D6(); /* 4x */
```

## Prior hypotheses (do not repeat)
`{"summary":{"predictions":{},"shown":0,"trials":0,"verdicts":{}},"trials":[]}`
Prior fleet outcomes: `[{"explanation":"The required full disassembly/CFG/relocation package is unavailable: grinder facts ov11_F_27CC returned BLOCKED because the function exceeds the bounded grinder budget. The task packet supplies only call/global summar...","line":96,"status":"NEEDS_EVIDENCE_FOR_CURATION","task":"fn-ov11_F_27CC"}]`

## Type evidence ov11_F_27CC (advisory)
`{"declaration_conflicts":31,"frame":[],"globals":["G_h01_0018 w=[] rw={'UNKNOWN': 40}","G_h01_0054 w=[] rw={'UNKNOWN': 277}","G_h01_0162 w=[] rw={'UNKNOWN': 66}","G_h01_01A4 w=[] rw={'UNKNOWN': 67}","G_h01_01B6 w=[] rw={'UNKNOWN': 2}","G_h01_01BC w=[] rw={'UNKNOWN': 76}","G_h01_46CA w=[4] rw={'READ': 244}","G_h01_46E1 w=[1] rw={'READ': 21, 'READ_WRITE': 8, 'UNKNOWN': 21, 'WRITE': 4}"]}`

## Protocol
1. Inspect evidence (read-only): `python tools/grinder.py facts ID --max-instructions 2000` (full disassembly/CFG/relocations), `python tools/diag.py ID --cache-key KEY` for any cached key, `python tools/type_evidence.py --function ID`, `python tools/shape_search.py --ledger-summary ID`, docs/source-shape-search.md, docs/m68k-diagnostics.md.
2. BEFORE compiling, record each hypothesis with a machine-checkable prediction. Write a schema v2 manifest `experiments/fleet/fn-ov11_F_27CC/manifest-NN.json` (docs/source-shape-search.md): every variant has parent, suspected_cause, controlled_change and predicted_effect {length_delta, removed_candidate_only, register_role_diffs, note}. Name a measured parent (an earlier variant, a compiled .c path, `ledger:N` or a 64-hex cache key); parent `none` leaves every prediction unmeasurable. Sources: `experiments/fleet/fn-ov11_F_27CC/*.c` (self-contained K&R C defining `recovered(...)`, mechanical G_hNN_XXXX/F_hNN_XXXX externs).
3. Each variant makes ONE controlled change from its parent. Do not resubmit a hypothesis listed under prior hypotheses; the ledger rejects normalized duplicates and returns the earlier record, which you must read instead.
4. Compile via: `python tools/shape_search.py experiments/fleet/fn-ov11_F_27CC/manifest-NN.json --output-dir experiments/fleet/fn-ov11_F_27CC/runs --json` (isolated; records the ledger; add `--measure-parents` to compile an unmeasured parent as a counted trial). For owned CODE data or m.lib only: `python tools/fleet.py verify-function ID SRC --profile P [--owned-code-data] [--with-m-lib] --output-dir experiments/fleet/fn-ov11_F_27CC/runs`.
   Compiles are queued and batched across workers (a cache miss may wait minutes); cache hits are instant. Never loop on a failing tool.
5. Budget: at most 24 compiler trials and 6 variants per manifest. Stop at an exact EQUAL, at budget, or after three consecutive refuted predictions in one causal family without new evidence (switch family once, then report).
6. Write `experiments/fleet/fn-ov11_F_27CC/result.json` exactly per the schema below using Python `json.dump` (UTF-8, no BOM; never an empty file), check it with `python tools/fleet.py intake fn-ov11_F_27CC --dry-run`, fix any REJECTED reason, then reply with one line: `TASK fn-ov11_F_27CC <STATUS> experiments/fleet/fn-ov11_F_27CC/result.json`.

## result.json (closed schema; intake re-verifies every EQUAL claim)
```json
{"schema_version":1,"task_id":"fn-ov11_F_27CC","worker":"<your -n name>",
 "status":"EQUAL_CANDIDATE|NEAR|BLOCKED|NEEDS_EVIDENCE",
 "target":"ov11_F_27CC",
 "best":null or {"source":"experiments/fleet/fn-ov11_F_27CC/<file>.c","profile":"aztec36","cache_key":"<64 hex>",
   "verdict":"EQUAL|DIFFER|BLOCKED","verifier":"check_function","entry":"<evidence id of the member compiled as recovered(), e.g. ov11_F_27CC>",
   "options":["owned_code_data","with_m_lib"],"expected_length":0,"actual_length":0},
 "hypotheses":[{"id":"h1","statement":"...","outcome":"confirmed|refuted|partial|unmeasurable|untested","evidence":"ledger line / report path"}],
 "compile_trials":0,"ledger_lines":[],
 "explanation":"what the evidence now shows (<=1200 chars)",
 "proposed_blocker":null or {"mechanism":"UPPER_SNAKE_CASE","text":"blocker text for docs/blockers.json curation"}}
```
EQUAL_CANDIDATE needs best.verdict EQUAL from an isolated run. NEAR needs best. BLOCKED needs proposed_blocker. NEEDS_EVIDENCE names the missing evidence in explanation. `entry` is required for check_unit and equals the target for check_function.
For check_unit with several new members, `best` may add `"members":{"<other member id>":"experiments/fleet/fn-ov11_F_27CC/<file>.c"}` (the `--member` sources; never the entry).
If `best` was compiled with `--object-group`, add `"object_groups":[["<ID>","<ID>"]]` exactly as passed (intake re-verifies with them).
