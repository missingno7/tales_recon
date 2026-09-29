# Fleet task fn-ov13_F_02BE (function)

You are an autonomous worker on a historical Amiga 68k (Aztec C) reconstruction in `D:/Prog/tales_recon`. You have no memory beyond this prompt. Recover closed function ov13_F_02BE (1086 bytes)

Priority 48. Lease: worker `luna-fn-ov13_F_02BE`, expires 2026-09-29T17:01:50+00:00 (renew: `python tools/fleet.py renew fn-ov13_F_02BE --worker luna-fn-ov13_F_02BE`).

## First step (host liveness)
Run `python tools/fleet.py renew fn-ov13_F_02BE --worker luna-fn-ov13_F_02BE` before anything else. The host is shared and heavily loaded: a single command can take 1-3 minutes to start and finish. Run commands one at a time (never batch several commands in parallel), wait on slow commands instead of terminating them, and keep outputs small. Do not read whole docs/*.json ledgers or long docs; this packet already carries the binding rules and target facts, so use targeted queries. Only if this `renew` command itself has still not returned after 10 minutes, stop and reply with one line: `TASK fn-ov13_F_02BE BLOCKED HOST_TOOLS_UNRESPONSIVE` (no result.json needed; the supervisor releases the lease).

## Rules (binding; from AGENTS.md)
- Historical reconstruction, not a source port. `assets/` is immutable oracle evidence. Never relock fixtures and never feed original code bytes into reconstructed outputs (no byte arrays, inline asm, placement directives or copied data standing in for code).
- Keep natural object/hunk/overlay layout as the target. Numeric overlay names are containers; do not invent semantic names or source filenames. Printable runs are candidates, not string boundaries. Unknown ownership stays visible. Runtime ABI identification is not library provenance.
- Do not edit tools/, tests/, docs/, evidence/, recovery/, src/ or assets/, do not hand-edit generated ledgers, do not run `census.py --write`, `function_census.py` or `type_evidence.py --write`, and do not commit.
- Write files ONLY under `experiments/fleet/fn-ov13_F_02BE/`. The tools themselves append to build/compile-cache and to the hypothesis ledger; that is expected.
- Never promote: never run check_function.py/check_unit.py without `--isolated`; use the wrappers below. Never delete lock files. If a tool reports a stale lock, stop and report BLOCKED quoting the message.
- The exact verifier alone decides EQUAL. Diagnostics and similarity scores are advisory. Other workers share this checkout; do not touch other experiments/ directories.

## Origin
`{"constraints":["PC_RELATIVE_DATA_OWNERSHIP"],"source":"ranked_frontier"}`

## Target facts
- `{"calls":["F_h00_57D2 A4_RELOCATED_JMP_STUB DISCOVERED x8","F_h00_8BC8 A4_RELOCATED_JMP_STUB DISCOVERED","F_h13_0000 PC_RELATIVE FUNCTION_CODE_MATCH x5","F_h00_4EC6 A4_RELOCATED_JMP_STUB DISCOVERED","F_h00_0FDE A4_RELOCATED_JMP_STUB DISCOVERED x4","F_h00_4D04 A4_RELOCATED_JMP_STUB DISCOVERED","F_h00_2816 A4_RELOCATED_JMP_STUB DISCOVERED","F_h00_330E A4_RELOCATED_JMP_STUB DISCOVERED","F_h00_307C A4_RELOCATED_JMP_STUB DISCOVERED x10","F_h00_31AA A4_RELOCATED_JMP_STUB DISCOVERED","F_h00_8A46 A4_RELOCATED_JMP_STUB DISCOVERED","F_h00_34E0 A4_RELOCATED_JMP_STUB DISCOVERED x16"],"confidence":"HIGH","constraints":["SIZE_LIMIT","PC_RELATIVE_DATA_OWNERSHIP"],"data":["G_h01_001E","G_h01_002A","G_h01_0030","G_h01_0036","G_h01_0048","G_h01_004E","G_h01_0054","G_h01_005A","G_h01_007E","G_h01_009C","G_h01_00A2","G_h01_00B4","G_h01_00BA","G_h01_00CC","G_h01_011A","G_h01_014A"],"end":"0x06FC","extent":"CLOSED_CFG","hunk":13,"id":"ov13_F_02BE","indirect":0,"instructions":312,"jump_tables":0,"more_calls":8,"more_data":38,"node":"ov13","pc_relative_data":6,"size":1086,"start":"0x02BE","strings":6}`

## Declarations already used by canonical sources (candidate views, not provenance)
Paste-ready block: `experiments/fleet/fn-ov13_F_02BE/canonical-declarations.h` (details: task.json `declaration_views`). Reuse these names, views and struct definitions unless a hypothesis needs another view; that view change is then the recorded controlled change. They compiled exactly elsewhere; they are not historical types, and access widths do not determine a type. 31 referenced symbols have canonical views (4 differ: G_h01_50E6, F_h00_291E, F_h00_34E0, F_h00_4376); 20 have none.
```c
/* Declarations already used by canonical sources: candidate views, not provenance.
   Reuse them unless a hypothesis needs a different view (then that is the controlled change). */
extern int G_h01_1422; /* 1x; w2 */
extern long G_h01_46CA; /* 13x; w4 */
extern long G_h01_46CE; /* 15x; w4 */
extern long G_h01_46D2; /* 16x; w4 */
extern char *G_h01_46D6; /* 3x; w4 */
extern long G_h01_46DA; /* 5x; w4 */
extern int G_h01_50E6; /* 2x; alt struct UiState x1 */
extern int G_h01_511C; /* 2x */
extern int G_h01_5152; /* 2x */
extern int G_h01_5188; /* 2x */
extern int G_h01_5338; /* 1x; w2 */
extern int G_h01_533A; /* 1x; w2 */
extern char G_h01_536C; /* 1x; w1 */
extern int F_h00_0FDE(); /* 10x */
extern int F_h00_2816(); /* 4x */
extern int F_h00_291E(); /* 5x; alt long () x2 */
extern int F_h00_307C(); /* 13x */
extern int F_h00_31AA(); /* 3x */
extern int F_h00_330E(); /* 4x */
extern int F_h00_34E0(); /* 20x; alt void () x2 */
extern int F_h00_35DC(); /* 9x */
extern int F_h00_3AE4(); /* 6x */
extern int F_h00_435E(); /* 4x */
extern int F_h00_4376(); /* 4x; alt char () x1 */
extern int F_h00_4D04(); /* 3x */
extern int F_h00_4EC6(); /* 5x */
extern int F_h00_57D2(); /* 19x */
extern int F_h00_86A8(); /* 8x */
extern int F_h00_8A46(); /* 16x */
extern int F_h00_8BC8(); /* 5x */
extern int F_h13_0000(); /* 1x */
/* G_h01_1466: no canonical view */
/* G_h01_2A16: no canonical view; w4 */
/* G_h01_5E5E: no canonical view; w1 */
```
(17 more lines in the sidecar)

## Prior hypotheses (do not repeat)
`{"summary":{"predictions":{},"shown":0,"trials":0,"verdicts":{}},"trials":[]}`

## Type evidence ov13_F_02BE (advisory)
`{"declaration_conflicts":2,"frame":[],"globals":["G_h01_001E w=[] rw={'UNKNOWN': 101}","G_h01_002A w=[] rw={'UNKNOWN': 58}","G_h01_0030 w=[] rw={'UNKNOWN': 285}","G_h01_0036 w=[] rw={'UNKNOWN': 180}","G_h01_0048 w=[] rw={'UNKNOWN': 34}","G_h01_004E w=[] rw={'UNKNOWN': 55}","G_h01_0054 w=[] rw={'UNKNOWN': 277}","G_h01_005A w=[] rw={'UNKNOWN': 176}"]}`

## Protocol
1. Inspect evidence (read-only): `python tools/grinder.py facts ID --max-instructions 2000 --max-bytes 2000000 > experiments/fleet/fn-ov13_F_02BE/facts-ID.json` then query that file (full disassembly/CFG/relocations), `python tools/diag.py ID --cache-key KEY` for any cached key, `python tools/type_evidence.py --function ID`, `python tools/shape_search.py --ledger-summary ID`, docs/source-shape-search.md, docs/m68k-diagnostics.md.
2. BEFORE compiling, record each hypothesis with a machine-checkable prediction. Write a schema v2 manifest `experiments/fleet/fn-ov13_F_02BE/manifest-NN.json` (docs/source-shape-search.md): every variant has parent, suspected_cause, controlled_change and predicted_effect {length_delta, removed_candidate_only, register_role_diffs, note}. Name a measured parent (an earlier variant, a compiled .c path, `ledger:N` or a 64-hex cache key); parent `none` leaves every prediction unmeasurable. Sources: `experiments/fleet/fn-ov13_F_02BE/*.c` (self-contained K&R C defining `recovered(...)`, mechanical G_hNN_XXXX/F_hNN_XXXX externs).
3. Each variant makes ONE controlled change from its parent. Do not resubmit a hypothesis listed under prior hypotheses; the ledger rejects normalized duplicates and returns the earlier record, which you must read instead.
4. Compile via: `python tools/shape_search.py experiments/fleet/fn-ov13_F_02BE/manifest-NN.json --output-dir experiments/fleet/fn-ov13_F_02BE/runs --json` (isolated; records the ledger; add `--measure-parents` to compile an unmeasured parent as a counted trial). For owned CODE data or m.lib only: `python tools/fleet.py verify-function ID SRC --profile P [--owned-code-data] [--with-m-lib] --output-dir experiments/fleet/fn-ov13_F_02BE/runs`.
   Compiles are queued and batched across workers (a cache miss may wait minutes); cache hits are instant. Never loop on a failing tool.
5. Budget: at most 24 compiler trials and 6 variants per manifest. Stop at an exact EQUAL, at budget, or after three consecutive refuted predictions in one causal family without new evidence (switch family once, then report).
6. Write `experiments/fleet/fn-ov13_F_02BE/result.json` exactly per the schema below using Python `json.dump` (UTF-8, no BOM; never an empty file), check it with `python tools/fleet.py intake fn-ov13_F_02BE --dry-run`, fix any REJECTED reason, then reply with one line: `TASK fn-ov13_F_02BE <STATUS> experiments/fleet/fn-ov13_F_02BE/result.json`.

## result.json (closed schema; intake re-verifies every EQUAL claim)
```json
{"schema_version":1,"task_id":"fn-ov13_F_02BE","worker":"<your -n name>",
 "status":"EQUAL_CANDIDATE|NEAR|BLOCKED|NEEDS_EVIDENCE",
 "target":"ov13_F_02BE",
 "best":null or {"source":"experiments/fleet/fn-ov13_F_02BE/<file>.c","profile":"aztec36","cache_key":"<64 hex>",
   "verdict":"EQUAL|DIFFER|BLOCKED","verifier":"check_function","entry":"<evidence id of the member compiled as recovered(), e.g. ov13_F_02BE>",
   "options":["owned_code_data","with_m_lib"],"expected_length":0,"actual_length":0},
 "hypotheses":[{"id":"h1","statement":"...","outcome":"confirmed|refuted|partial|unmeasurable|untested","evidence":"ledger line / report path"}],
 "compile_trials":0,"ledger_lines":[],
 "explanation":"what the evidence now shows (<=1200 chars)",
 "proposed_blocker":null or {"mechanism":"UPPER_SNAKE_CASE","text":"blocker text for docs/blockers.json curation"}}
```
EQUAL_CANDIDATE needs best.verdict EQUAL from an isolated run. NEAR needs best. BLOCKED needs proposed_blocker. NEEDS_EVIDENCE names the missing evidence in explanation. `entry` is required for check_unit and equals the target for check_function.
For check_unit with several new members, `best` may add `"members":{"<other member id>":"experiments/fleet/fn-ov13_F_02BE/<file>.c"}` (the `--member` sources; never the entry).
If `best` was compiled with `--object-group`, add `"object_groups":[["<ID>","<ID>"]]` exactly as passed (intake re-verifies with them).
