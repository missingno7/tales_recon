# Fleet task fn-ov04_F_149C (function)

You are an autonomous worker on a historical Amiga 68k (Aztec C) reconstruction in `D:/Prog/tales_recon`. You have no memory beyond this prompt. Recover closed function ov04_F_149C (688 bytes)

Priority 45. Lease: worker `luna-fn-ov04_F_149C`, expires 2026-09-29T03:52:45+00:00 (renew: `python tools/fleet.py renew fn-ov04_F_149C --worker luna-fn-ov04_F_149C`).

## First step (host liveness)
Run `python tools/fleet.py renew fn-ov04_F_149C --worker luna-fn-ov04_F_149C` before anything else. The host is shared and heavily loaded: a single command can take 1-3 minutes to start and finish. Run commands one at a time (never batch several commands in parallel), wait on slow commands instead of terminating them, and keep outputs small. Do not read whole docs/*.json ledgers or long docs; this packet already carries the binding rules and target facts, so use targeted queries. Only if this `renew` command itself has still not returned after 10 minutes, stop and reply with one line: `TASK fn-ov04_F_149C BLOCKED HOST_TOOLS_UNRESPONSIVE` (no result.json needed; the supervisor releases the lease).

## Rules (binding; from AGENTS.md)
- Historical reconstruction, not a source port. `assets/` is immutable oracle evidence. Never relock fixtures and never feed original code bytes into reconstructed outputs (no byte arrays, inline asm, placement directives or copied data standing in for code).
- Keep natural object/hunk/overlay layout as the target. Numeric overlay names are containers; do not invent semantic names or source filenames. Printable runs are candidates, not string boundaries. Unknown ownership stays visible. Runtime ABI identification is not library provenance.
- Do not edit tools/, tests/, docs/, evidence/, recovery/, src/ or assets/, do not hand-edit generated ledgers, do not run `census.py --write`, `function_census.py` or `type_evidence.py --write`, and do not commit.
- Write files ONLY under `experiments/fleet/fn-ov04_F_149C/`. The tools themselves append to build/compile-cache and to the hypothesis ledger; that is expected.
- Never promote: never run check_function.py/check_unit.py without `--isolated`; use the wrappers below. Never delete lock files. If a tool reports a stale lock, stop and report BLOCKED quoting the message.
- The exact verifier alone decides EQUAL. Diagnostics and similarity scores are advisory. Other workers share this checkout; do not touch other experiments/ directories.

## Origin
`{"constraints":["PC_RELATIVE_DATA_OWNERSHIP"],"source":"ranked_frontier"}`

## Target facts
- `{"calls":["F_h00_8BC8 A4_RELOCATED_JMP_STUB DISCOVERED x3","F_h00_307C A4_RELOCATED_JMP_STUB DISCOVERED x3","F_h00_0640 A4_RELOCATED_JMP_STUB DISCOVERED","F_h00_35DC A4_RELOCATED_JMP_STUB DISCOVERED x14","F_h00_31AA A4_RELOCATED_JMP_STUB DISCOVERED","F_h00_435E A4_RELOCATED_JMP_STUB DISCOVERED","F_h00_8A46 A4_RELOCATED_JMP_STUB DISCOVERED","F_h00_57D2 A4_RELOCATED_JMP_STUB DISCOVERED x3","F_h00_86A8 A4_RELOCATED_JMP_STUB DISCOVERED","F_h00_4376 A4_RELOCATED_JMP_STUB DISCOVERED","F_h00_4676 A4_RELOCATED_JMP_STUB DISCOVERED","F_h00_330E A4_RELOCATED_JMP_STUB DISCOVERED"],"confidence":"HIGH","constraints":["PC_RELATIVE_DATA_OWNERSHIP"],"data":["G_h01_0006","G_h01_0036","G_h01_0048","G_h01_004E","G_h01_005A","G_h01_009C","G_h01_00A2","G_h01_00AE","G_h01_00CC","G_h01_011A","G_h01_014A","G_h01_01CE","G_h01_1766","G_h01_46CA","G_h01_46CE","G_h01_46D2"],"end":"0x174C","extent":"CLOSED_CFG","hunk":4,"id":"ov04_F_149C","indirect":0,"instructions":194,"jump_tables":0,"more_calls":0,"more_data":16,"node":"ov04","pc_relative_data":14,"size":688,"start":"0x149C","strings":14}`

## Declarations already used by canonical sources (candidate views, not provenance)
Paste-ready block: `experiments/fleet/fn-ov04_F_149C/canonical-declarations.h` (details: task.json `declaration_views`). Reuse these names, views and struct definitions unless a hypothesis needs another view; that view change is then the recorded controlled change. They compiled exactly elsewhere; they are not historical types, and access widths do not determine a type. 17 referenced symbols have canonical views (1 differ: F_h00_4376); 1 have none.
```c
/* Declarations already used by canonical sources: candidate views, not provenance.
   Reuse them unless a hypothesis needs a different view (then that is the controlled change). */
extern char G_h01_1766[1]; /* 1x */
extern long G_h01_46CA; /* 11x; w4 */
extern long G_h01_46CE; /* 13x; w4 */
extern long G_h01_46D2; /* 14x; w4 */
extern char *G_h01_46D6; /* 2x; w4 */
extern char G_h01_46E0; /* 6x; w1 */
extern int F_h00_0640(); /* 2x */
extern int F_h00_307C(); /* 12x */
extern int F_h00_31AA(); /* 2x */
extern int F_h00_330E(); /* 3x */
extern int F_h00_35DC(); /* 8x */
extern int F_h00_435E(); /* 3x */
extern int F_h00_4376(); /* 3x; alt char () x1 */
extern int F_h00_57D2(); /* 16x */
extern int F_h00_86A8(); /* 7x */
extern int F_h00_8A46(); /* 14x */
extern int F_h00_8BC8(); /* 4x */
/* F_h00_4676: no canonical view */
```

## Prior hypotheses (do not repeat)
`{"summary":{"predictions":{},"shown":0,"trials":0,"verdicts":{}},"trials":[]}`

## Type evidence ov04_F_149C (advisory)
`{"declaration_conflicts":0,"frame":[],"globals":["G_h01_0006 w=[] rw={'UNKNOWN': 16}","G_h01_0036 w=[] rw={'UNKNOWN': 180}","G_h01_0048 w=[] rw={'UNKNOWN': 34}","G_h01_004E w=[] rw={'UNKNOWN': 55}","G_h01_005A w=[] rw={'UNKNOWN': 176}","G_h01_009C w=[] rw={'UNKNOWN': 47}","G_h01_00A2 w=[] rw={'UNKNOWN': 47}","G_h01_00AE w=[] rw={'UNKNOWN': 2}"]}`

## Protocol
1. Inspect evidence (read-only): `python tools/grinder.py facts ID` (full disassembly/CFG/relocations), `python tools/diag.py ID --cache-key KEY` for any cached key, `python tools/type_evidence.py --function ID`, `python tools/shape_search.py --ledger-summary ID`, docs/source-shape-search.md, docs/m68k-diagnostics.md.
2. BEFORE compiling, record each hypothesis with a machine-checkable prediction. Write a schema v2 manifest `experiments/fleet/fn-ov04_F_149C/manifest-NN.json` (docs/source-shape-search.md): every variant has parent, suspected_cause, controlled_change and predicted_effect {length_delta, removed_candidate_only, register_role_diffs, note}. Name a measured parent (an earlier variant, a compiled .c path, `ledger:N` or a 64-hex cache key); parent `none` leaves every prediction unmeasurable. Sources: `experiments/fleet/fn-ov04_F_149C/*.c` (self-contained K&R C defining `recovered(...)`, mechanical G_hNN_XXXX/F_hNN_XXXX externs).
3. Each variant makes ONE controlled change from its parent. Do not resubmit a hypothesis listed under prior hypotheses; the ledger rejects normalized duplicates and returns the earlier record, which you must read instead.
4. Compile via: `python tools/shape_search.py experiments/fleet/fn-ov04_F_149C/manifest-NN.json --output-dir experiments/fleet/fn-ov04_F_149C/runs --json` (isolated; records the ledger; add `--measure-parents` to compile an unmeasured parent as a counted trial). For owned CODE data or m.lib only: `python tools/fleet.py verify-function ID SRC --profile P [--owned-code-data] [--with-m-lib] --output-dir experiments/fleet/fn-ov04_F_149C/runs`.
   Compiles are queued and batched across workers (a cache miss may wait minutes); cache hits are instant. Never loop on a failing tool.
5. Budget: at most 24 compiler trials and 6 variants per manifest. Stop at an exact EQUAL, at budget, or after three consecutive refuted predictions in one causal family without new evidence (switch family once, then report).
6. Write `experiments/fleet/fn-ov04_F_149C/result.json` exactly per the schema below using Python `json.dump` (UTF-8, no BOM; never an empty file), check it with `python tools/fleet.py intake fn-ov04_F_149C --dry-run`, fix any REJECTED reason, then reply with one line: `TASK fn-ov04_F_149C <STATUS> experiments/fleet/fn-ov04_F_149C/result.json`.

## result.json (closed schema; intake re-verifies every EQUAL claim)
```json
{"schema_version":1,"task_id":"fn-ov04_F_149C","worker":"<your -n name>",
 "status":"EQUAL_CANDIDATE|NEAR|BLOCKED|NEEDS_EVIDENCE",
 "target":"ov04_F_149C",
 "best":null or {"source":"experiments/fleet/fn-ov04_F_149C/<file>.c","profile":"aztec36","cache_key":"<64 hex>",
   "verdict":"EQUAL|DIFFER|BLOCKED","verifier":"check_function","entry":"<evidence id of the member compiled as recovered(), e.g. ov04_F_149C>",
   "options":["owned_code_data","with_m_lib"],"expected_length":0,"actual_length":0},
 "hypotheses":[{"id":"h1","statement":"...","outcome":"confirmed|refuted|partial|unmeasurable|untested","evidence":"ledger line / report path"}],
 "compile_trials":0,"ledger_lines":[],
 "explanation":"what the evidence now shows (<=1200 chars)",
 "proposed_blocker":null or {"mechanism":"UPPER_SNAKE_CASE","text":"blocker text for docs/blockers.json curation"}}
```
EQUAL_CANDIDATE needs best.verdict EQUAL from an isolated run. NEAR needs best. BLOCKED needs proposed_blocker. NEEDS_EVIDENCE names the missing evidence in explanation. `entry` is required for check_unit and equals the target for check_function.
For check_unit with several new members, `best` may add `"members":{"<other member id>":"experiments/fleet/fn-ov04_F_149C/<file>.c"}` (the `--member` sources; never the entry).
If `best` was compiled with `--object-group`, add `"object_groups":[["<ID>","<ID>"]]` exactly as passed (intake re-verifies with them).
