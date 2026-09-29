# Fleet task fn-ov11_F_62B4 (function)

You are an autonomous worker on a historical Amiga 68k (Aztec C) reconstruction in `D:/Prog/tales_recon`. You have no memory beyond this prompt. Recover closed function ov11_F_62B4 (426 bytes)

Priority 43. Lease: worker `luna-fn-ov11_F_62B4`, expires 2026-09-29T12:34:00+00:00 (renew: `python tools/fleet.py renew fn-ov11_F_62B4 --worker luna-fn-ov11_F_62B4`).

## First step (host liveness)
Run `python tools/fleet.py renew fn-ov11_F_62B4 --worker luna-fn-ov11_F_62B4` before anything else. The host is shared and heavily loaded: a single command can take 1-3 minutes to start and finish. Run commands one at a time (never batch several commands in parallel), wait on slow commands instead of terminating them, and keep outputs small. Do not read whole docs/*.json ledgers or long docs; this packet already carries the binding rules and target facts, so use targeted queries. Only if this `renew` command itself has still not returned after 10 minutes, stop and reply with one line: `TASK fn-ov11_F_62B4 BLOCKED HOST_TOOLS_UNRESPONSIVE` (no result.json needed; the supervisor releases the lease).

## Rules (binding; from AGENTS.md)
- Historical reconstruction, not a source port. `assets/` is immutable oracle evidence. Never relock fixtures and never feed original code bytes into reconstructed outputs (no byte arrays, inline asm, placement directives or copied data standing in for code).
- Keep natural object/hunk/overlay layout as the target. Numeric overlay names are containers; do not invent semantic names or source filenames. Printable runs are candidates, not string boundaries. Unknown ownership stays visible. Runtime ABI identification is not library provenance.
- Do not edit tools/, tests/, docs/, evidence/, recovery/, src/ or assets/, do not hand-edit generated ledgers, do not run `census.py --write`, `function_census.py` or `type_evidence.py --write`, and do not commit.
- Write files ONLY under `experiments/fleet/fn-ov11_F_62B4/`. The tools themselves append to build/compile-cache and to the hypothesis ledger; that is expected.
- Never promote: never run check_function.py/check_unit.py without `--isolated`; use the wrappers below. Never delete lock files. If a tool reports a stale lock, stop and report BLOCKED quoting the message.
- The exact verifier alone decides EQUAL. Diagnostics and similarity scores are advisory. Other workers share this checkout; do not touch other experiments/ directories.

## Origin
`{"constraints":["NONCONTIGUOUS_LOCAL_UNIT"],"source":"ranked_frontier"}`

## Target facts
- `{"calls":["F_h11_5A62 PC_RELATIVE FUNCTION_CODE_MATCH","F_h11_5A12 PC_RELATIVE FUNCTION_CODE_MATCH","F_h11_5962 PC_RELATIVE FUNCTION_CODE_MATCH","F_h11_5C42 PC_RELATIVE FUNCTION_CODE_MATCH","F_h11_41F6 PC_RELATIVE FUNCTION_CODE_MATCH","F_h00_463E A4_RELOCATED_JMP_STUB DISCOVERED"],"confidence":"HIGH","constraints":["NONCONTIGUOUS_LOCAL_UNIT"],"data":["G_h01_00A8","G_h01_37EC","G_h01_37EE","G_h01_37F0","G_h01_37F2","G_h01_46E0","G_h01_8BEC","G_h01_8BEE","G_h01_8BF4","G_h01_8BFE","G_h01_8C18","G_h01_8C1A","G_h01_8C1C","G_h01_940C"],"end":"0x645E","extent":"CLOSED_CFG","hunk":11,"id":"ov11_F_62B4","indirect":0,"instructions":124,"jump_tables":0,"more_calls":0,"more_data":0,"node":"ov11","pc_relative_data":0,"size":426,"start":"0x62B4","strings":0}`

## Declarations already used by canonical sources (candidate views, not provenance)
Paste-ready block: `experiments/fleet/fn-ov11_F_62B4/canonical-declarations.h` (details: task.json `declaration_views`). Reuse these names, views and struct definitions unless a hypothesis needs another view; that view change is then the recorded controlled change. They compiled exactly elsewhere; they are not historical types, and access widths do not determine a type. 11 referenced symbols have canonical views (4 differ: G_h01_8BEC, G_h01_940C, F_h00_463E, F_h11_5962); 8 have none.
```c
/* Declarations already used by canonical sources: candidate views, not provenance.
   Reuse them unless a hypothesis needs a different view (then that is the controlled change). */
struct ClusterRecord { char pad0[8]; int value8; int value10; char pad12[2]; int value14; int value16; char pad18[12]; int state30; int value32; char pad34[6]; int state40; int value42; int value2c; int value2e; char tail[4]; };
extern int G_h01_37EC; /* 1x; w2 */
extern int G_h01_37F2; /* 1x; w2 */
extern char G_h01_46E0; /* 8x; w1 */
extern struct ClusterRecord G_h01_8BEC[1]; /* 2x; alt int [1] x1, struct MotionRecord [1] x1, struct BRecord [1] x1 */
extern short G_h01_940C[1]; /* 1x; alt int [1] x1; tie */
extern unsigned int F_h00_463E(); /* 3x; alt int () x3, long () x3; tie */
extern int F_h11_41F6(); /* 6x */
extern int F_h11_5962(); /* 3x; alt void () x1 */
extern int F_h11_5A12(); /* 1x */
extern int F_h11_5A62(); /* 1x */
extern int F_h11_5C42(); /* 1x */
/* G_h01_37EE: no canonical view; w2 */
/* G_h01_37F0: no canonical view; w2 */
/* G_h01_8BEE: inside G_h01_8BEC+2 (struct ClusterRecord [1]) */
/* G_h01_8BF4: inside G_h01_8BEC+8 (struct ClusterRecord [1]) */
/* G_h01_8BFE: inside G_h01_8BEC+18 (struct ClusterRecord [1]) */
/* G_h01_8C18: inside G_h01_8BEC+44 (struct ClusterRecord [1]) */
/* G_h01_8C1A: inside G_h01_8BEC+46 (struct ClusterRecord [1]) */
/* G_h01_8C1C: inside G_h01_8BEC+48 (struct ClusterRecord [1]) */
```

## Prior hypotheses (do not repeat)
`{"summary":{"predictions":{},"shown":0,"trials":0,"verdicts":{}},"trials":[]}`

## Type evidence ov11_F_62B4 (advisory)
`{"declaration_conflicts":10,"frame":["+8 w=[2] n=2"],"globals":["G_h01_00A8 w=[] rw={'UNKNOWN': 97}","G_h01_37EC w=[2] rw={'UNKNOWN': 2, 'WRITE': 1}","G_h01_37EE w=[2] rw={'READ': 1, 'WRITE': 4}","G_h01_37F0 w=[2] rw={'READ': 2, 'WRITE': 4}","G_h01_37F2 w=[2] rw={'UNKNOWN': 1, 'WRITE': 2}","G_h01_46E0 w=[1] rw={'READ': 18, 'READ_WRITE': 2, 'UNKNOWN': 19, 'WRITE': 3}","G_h01_8BEC w=[] rw={}","G_h01_8BEE w=[] rw={}"]}`

## Protocol
1. Inspect evidence (read-only): `python tools/grinder.py facts ID --max-instructions 2000 --max-bytes 2000000 > experiments/fleet/fn-ov11_F_62B4/facts-ID.json` then query that file (full disassembly/CFG/relocations), `python tools/diag.py ID --cache-key KEY` for any cached key, `python tools/type_evidence.py --function ID`, `python tools/shape_search.py --ledger-summary ID`, docs/source-shape-search.md, docs/m68k-diagnostics.md.
2. BEFORE compiling, record each hypothesis with a machine-checkable prediction. Write a schema v2 manifest `experiments/fleet/fn-ov11_F_62B4/manifest-NN.json` (docs/source-shape-search.md): every variant has parent, suspected_cause, controlled_change and predicted_effect {length_delta, removed_candidate_only, register_role_diffs, note}. Name a measured parent (an earlier variant, a compiled .c path, `ledger:N` or a 64-hex cache key); parent `none` leaves every prediction unmeasurable. Sources: `experiments/fleet/fn-ov11_F_62B4/*.c` (self-contained K&R C defining `recovered(...)`, mechanical G_hNN_XXXX/F_hNN_XXXX externs).
3. Each variant makes ONE controlled change from its parent. Do not resubmit a hypothesis listed under prior hypotheses; the ledger rejects normalized duplicates and returns the earlier record, which you must read instead.
4. Compile via: `python tools/shape_search.py experiments/fleet/fn-ov11_F_62B4/manifest-NN.json --output-dir experiments/fleet/fn-ov11_F_62B4/runs --json` (isolated; records the ledger; add `--measure-parents` to compile an unmeasured parent as a counted trial). For owned CODE data or m.lib only: `python tools/fleet.py verify-function ID SRC --profile P [--owned-code-data] [--with-m-lib] --output-dir experiments/fleet/fn-ov11_F_62B4/runs`.
   Compiles are queued and batched across workers (a cache miss may wait minutes); cache hits are instant. Never loop on a failing tool.
5. Budget: at most 24 compiler trials and 6 variants per manifest. Stop at an exact EQUAL, at budget, or after three consecutive refuted predictions in one causal family without new evidence (switch family once, then report).
6. Write `experiments/fleet/fn-ov11_F_62B4/result.json` exactly per the schema below using Python `json.dump` (UTF-8, no BOM; never an empty file), check it with `python tools/fleet.py intake fn-ov11_F_62B4 --dry-run`, fix any REJECTED reason, then reply with one line: `TASK fn-ov11_F_62B4 <STATUS> experiments/fleet/fn-ov11_F_62B4/result.json`.

## result.json (closed schema; intake re-verifies every EQUAL claim)
```json
{"schema_version":1,"task_id":"fn-ov11_F_62B4","worker":"<your -n name>",
 "status":"EQUAL_CANDIDATE|NEAR|BLOCKED|NEEDS_EVIDENCE",
 "target":"ov11_F_62B4",
 "best":null or {"source":"experiments/fleet/fn-ov11_F_62B4/<file>.c","profile":"aztec36","cache_key":"<64 hex>",
   "verdict":"EQUAL|DIFFER|BLOCKED","verifier":"check_function","entry":"<evidence id of the member compiled as recovered(), e.g. ov11_F_62B4>",
   "options":["owned_code_data","with_m_lib"],"expected_length":0,"actual_length":0},
 "hypotheses":[{"id":"h1","statement":"...","outcome":"confirmed|refuted|partial|unmeasurable|untested","evidence":"ledger line / report path"}],
 "compile_trials":0,"ledger_lines":[],
 "explanation":"what the evidence now shows (<=1200 chars)",
 "proposed_blocker":null or {"mechanism":"UPPER_SNAKE_CASE","text":"blocker text for docs/blockers.json curation"}}
```
EQUAL_CANDIDATE needs best.verdict EQUAL from an isolated run. NEAR needs best. BLOCKED needs proposed_blocker. NEEDS_EVIDENCE names the missing evidence in explanation. `entry` is required for check_unit and equals the target for check_function.
For check_unit with several new members, `best` may add `"members":{"<other member id>":"experiments/fleet/fn-ov11_F_62B4/<file>.c"}` (the `--member` sources; never the entry).
If `best` was compiled with `--object-group`, add `"object_groups":[["<ID>","<ID>"]]` exactly as passed (intake re-verifies with them).
