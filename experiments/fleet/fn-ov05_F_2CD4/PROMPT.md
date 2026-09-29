# Fleet task fn-ov05_F_2CD4 (function)

You are an autonomous worker on a historical Amiga 68k (Aztec C) reconstruction in `D:/Prog/tales_recon`. You have no memory beyond this prompt. Recover closed function ov05_F_2CD4 (1050 bytes)

Priority 38. Lease: worker `luna-fn-ov05_F_2CD4`, expires 2026-09-29T17:01:47+00:00 (renew: `python tools/fleet.py renew fn-ov05_F_2CD4 --worker luna-fn-ov05_F_2CD4`).

## First step (host liveness)
Run `python tools/fleet.py renew fn-ov05_F_2CD4 --worker luna-fn-ov05_F_2CD4` before anything else. The host is shared and heavily loaded: a single command can take 1-3 minutes to start and finish. Run commands one at a time (never batch several commands in parallel), wait on slow commands instead of terminating them, and keep outputs small. Do not read whole docs/*.json ledgers or long docs; this packet already carries the binding rules and target facts, so use targeted queries. Only if this `renew` command itself has still not returned after 10 minutes, stop and reply with one line: `TASK fn-ov05_F_2CD4 BLOCKED HOST_TOOLS_UNRESPONSIVE` (no result.json needed; the supervisor releases the lease).

## Rules (binding; from AGENTS.md)
- Historical reconstruction, not a source port. `assets/` is immutable oracle evidence. Never relock fixtures and never feed original code bytes into reconstructed outputs (no byte arrays, inline asm, placement directives or copied data standing in for code).
- Keep natural object/hunk/overlay layout as the target. Numeric overlay names are containers; do not invent semantic names or source filenames. Printable runs are candidates, not string boundaries. Unknown ownership stays visible. Runtime ABI identification is not library provenance.
- Do not edit tools/, tests/, docs/, evidence/, recovery/, src/ or assets/, do not hand-edit generated ledgers, do not run `census.py --write`, `function_census.py` or `type_evidence.py --write`, and do not commit.
- Write files ONLY under `experiments/fleet/fn-ov05_F_2CD4/`. The tools themselves append to build/compile-cache and to the hypothesis ledger; that is expected.
- Never promote: never run check_function.py/check_unit.py without `--isolated`; use the wrappers below. Never delete lock files. If a tool reports a stale lock, stop and report BLOCKED quoting the message.
- The exact verifier alone decides EQUAL. Diagnostics and similarity scores are advisory. Other workers share this checkout; do not touch other experiments/ directories.

## Origin
`{"constraints":[],"source":"ranked_frontier"}`

## Target facts
- `{"calls":["F_h00_463E A4_RELOCATED_JMP_STUB DISCOVERED x2","F_h00_34E0 A4_RELOCATED_JMP_STUB DISCOVERED x9","F_h00_8D1E A4_RELOCATED_JMP_STUB DISCOVERED","F_h00_8D0A A4_RELOCATED_JMP_STUB DISCOVERED","F_h00_8D00 A4_RELOCATED_JMP_STUB DISCOVERED","F_h00_57D2 A4_RELOCATED_JMP_STUB DISCOVERED","F_h00_7B00 A4_RELOCATED_JMP_STUB DISCOVERED x6"],"confidence":"HIGH","constraints":["SIZE_LIMIT"],"data":["G_h01_0054","G_h01_00A8","G_h01_00CC","G_h01_00F6","G_h01_0228","G_h01_022E","G_h01_023A","G_h01_0A7A","G_h01_0A7C","G_h01_2F10","G_h01_2F14","G_h01_2F16","G_h01_2F18","G_h01_2F1A","G_h01_2F1C","G_h01_54C8"],"end":"0x30EE","extent":"CLOSED_CFG","hunk":5,"id":"ov05_F_2CD4","indirect":0,"instructions":289,"jump_tables":0,"more_calls":0,"more_data":19,"node":"ov05","pc_relative_data":0,"size":1050,"start":"0x2CD4","strings":0}`

## Declarations already used by canonical sources (candidate views, not provenance)
Paste-ready block: `experiments/fleet/fn-ov05_F_2CD4/canonical-declarations.h` (details: task.json `declaration_views`). Reuse these names, views and struct definitions unless a hypothesis needs another view; that view change is then the recorded controlled change. They compiled exactly elsewhere; they are not historical types, and access widths do not determine a type. 7 referenced symbols have canonical views (2 differ: F_h00_34E0, F_h00_463E); 28 have none.
```c
/* Declarations already used by canonical sources: candidate views, not provenance.
   Reuse them unless a hypothesis needs a different view (then that is the controlled change). */
struct Lookup { int index; int pad; };
struct Record { char pad[4]; int value; char pad2[8]; };
extern char G_h01_54FE; /* 1x; w2 */
extern int G_h01_5500; /* 1x; w2 */
extern struct Lookup G_h01_5E66[16]; /* 1x */
extern struct Record G_h01_606C[16]; /* 1x */
extern int F_h00_34E0(); /* 20x; alt void () x2 */
extern unsigned int F_h00_463E(); /* 4x; alt int () x3, long () x3 */
extern int F_h00_57D2(); /* 19x */
/* G_h01_0A7A: no canonical view; w2 */
/* G_h01_0A7C: no canonical view; w2 */
/* G_h01_2F10: no canonical view; w2 */
/* G_h01_2F14: no canonical view; w2 */
/* G_h01_2F16: no canonical view; w2 */
/* G_h01_2F18: no canonical view; w2 */
/* G_h01_2F1A: no canonical view; w2 */
/* G_h01_2F1C: no canonical view; w2 */
/* G_h01_54C8: no canonical view; w2 */
/* G_h01_54CA: no canonical view; w2 */
/* G_h01_5534: no canonical view */
/* G_h01_5536: no canonical view */
/* G_h01_57C0: no canonical view */
/* G_h01_57C2: no canonical view */
/* G_h01_582C: no canonical view; w2 */
/* G_h01_582E: no canonical view; w2 */
/* G_h01_5862: no canonical view; w2 */
/* G_h01_5864: no canonical view; w2 */
/* G_h01_5AEE: no canonical view; w2 */
/* G_h01_5AF0: no canonical view; w2 */
/* G_h01_5D40: no canonical view; w2 */
/* G_h01_5D42: no canonical view; w2 */
/* G_h01_5D74: no canonical view; w1 */
/* G_h01_5E34: no canonical view; w4 */
/* F_h00_7B00: no canonical view */
/* F_h00_8D00: no canonical view */
/* F_h00_8D0A: no canonical view */
/* F_h00_8D1E: no canonical view */
```

## Prior hypotheses (do not repeat)
`{"summary":{"predictions":{},"shown":0,"trials":0,"verdicts":{}},"trials":[]}`

## Type evidence ov05_F_2CD4 (advisory)
`{"declaration_conflicts":0,"frame":["+8 w=[2] n=4"],"globals":["G_h01_0054 w=[] rw={'UNKNOWN': 277}","G_h01_00A8 w=[] rw={'UNKNOWN': 97}","G_h01_00CC w=[] rw={'UNKNOWN': 208}","G_h01_00F6 w=[] rw={'UNKNOWN': 42}","G_h01_0228 w=[] rw={'UNKNOWN': 56}","G_h01_022E w=[] rw={'UNKNOWN': 11}","G_h01_023A w=[] rw={'UNKNOWN': 36}","G_h01_0A7A w=[2] rw={'UNKNOWN': 1, 'WRITE': 3}"]}`

## Protocol
1. Inspect evidence (read-only): `python tools/grinder.py facts ID --max-instructions 2000 --max-bytes 2000000 > experiments/fleet/fn-ov05_F_2CD4/facts-ID.json` then query that file (full disassembly/CFG/relocations), `python tools/diag.py ID --cache-key KEY` for any cached key, `python tools/type_evidence.py --function ID`, `python tools/shape_search.py --ledger-summary ID`, docs/source-shape-search.md, docs/m68k-diagnostics.md.
2. BEFORE compiling, record each hypothesis with a machine-checkable prediction. Write a schema v2 manifest `experiments/fleet/fn-ov05_F_2CD4/manifest-NN.json` (docs/source-shape-search.md): every variant has parent, suspected_cause, controlled_change and predicted_effect {length_delta, removed_candidate_only, register_role_diffs, note}. Name a measured parent (an earlier variant, a compiled .c path, `ledger:N` or a 64-hex cache key); parent `none` leaves every prediction unmeasurable. Sources: `experiments/fleet/fn-ov05_F_2CD4/*.c` (self-contained K&R C defining `recovered(...)`, mechanical G_hNN_XXXX/F_hNN_XXXX externs).
3. Each variant makes ONE controlled change from its parent. Do not resubmit a hypothesis listed under prior hypotheses; the ledger rejects normalized duplicates and returns the earlier record, which you must read instead.
4. Compile via: `python tools/shape_search.py experiments/fleet/fn-ov05_F_2CD4/manifest-NN.json --output-dir experiments/fleet/fn-ov05_F_2CD4/runs --json` (isolated; records the ledger; add `--measure-parents` to compile an unmeasured parent as a counted trial). For owned CODE data or m.lib only: `python tools/fleet.py verify-function ID SRC --profile P [--owned-code-data] [--with-m-lib] --output-dir experiments/fleet/fn-ov05_F_2CD4/runs`.
   Compiles are queued and batched across workers (a cache miss may wait minutes); cache hits are instant. Never loop on a failing tool.
5. Budget: at most 24 compiler trials and 6 variants per manifest. Stop at an exact EQUAL, at budget, or after three consecutive refuted predictions in one causal family without new evidence (switch family once, then report).
6. Write `experiments/fleet/fn-ov05_F_2CD4/result.json` exactly per the schema below using Python `json.dump` (UTF-8, no BOM; never an empty file), check it with `python tools/fleet.py intake fn-ov05_F_2CD4 --dry-run`, fix any REJECTED reason, then reply with one line: `TASK fn-ov05_F_2CD4 <STATUS> experiments/fleet/fn-ov05_F_2CD4/result.json`.

## result.json (closed schema; intake re-verifies every EQUAL claim)
```json
{"schema_version":1,"task_id":"fn-ov05_F_2CD4","worker":"<your -n name>",
 "status":"EQUAL_CANDIDATE|NEAR|BLOCKED|NEEDS_EVIDENCE",
 "target":"ov05_F_2CD4",
 "best":null or {"source":"experiments/fleet/fn-ov05_F_2CD4/<file>.c","profile":"aztec36","cache_key":"<64 hex>",
   "verdict":"EQUAL|DIFFER|BLOCKED","verifier":"check_function","entry":"<evidence id of the member compiled as recovered(), e.g. ov05_F_2CD4>",
   "options":["owned_code_data","with_m_lib"],"expected_length":0,"actual_length":0},
 "hypotheses":[{"id":"h1","statement":"...","outcome":"confirmed|refuted|partial|unmeasurable|untested","evidence":"ledger line / report path"}],
 "compile_trials":0,"ledger_lines":[],
 "explanation":"what the evidence now shows (<=1200 chars)",
 "proposed_blocker":null or {"mechanism":"UPPER_SNAKE_CASE","text":"blocker text for docs/blockers.json curation"}}
```
EQUAL_CANDIDATE needs best.verdict EQUAL from an isolated run. NEAR needs best. BLOCKED needs proposed_blocker. NEEDS_EVIDENCE names the missing evidence in explanation. `entry` is required for check_unit and equals the target for check_function.
For check_unit with several new members, `best` may add `"members":{"<other member id>":"experiments/fleet/fn-ov05_F_2CD4/<file>.c"}` (the `--member` sources; never the entry).
If `best` was compiled with `--object-group`, add `"object_groups":[["<ID>","<ID>"]]` exactly as passed (intake re-verifies with them).
