# Fleet task fn-ov11_F_415A (function)

You are an autonomous worker on a historical Amiga 68k (Aztec C) reconstruction in `D:/Prog/tales_recon`. You have no memory beyond this prompt. Recover closed function ov11_F_415A (156 bytes)

Priority 36. Lease: worker `luna-fn-ov11_F_415A`, expires 2026-09-28T22:58:51+00:00 (renew: `python tools/fleet.py renew fn-ov11_F_415A --worker luna-fn-ov11_F_415A`).

## First step (host liveness)
Run `python tools/fleet.py renew fn-ov11_F_415A --worker luna-fn-ov11_F_415A` before anything else. The host is shared and heavily loaded: a single command can take 1-3 minutes to start and finish. Run commands one at a time (never batch several commands in parallel), wait on slow commands instead of terminating them, and keep outputs small. Do not read whole docs/*.json ledgers or long docs; this packet already carries the binding rules and target facts, so use targeted queries. Only if this `renew` command itself has still not returned after 10 minutes, stop and reply with one line: `TASK fn-ov11_F_415A BLOCKED HOST_TOOLS_UNRESPONSIVE` (no result.json needed; the supervisor releases the lease).

## Rules (binding; from AGENTS.md)
- Historical reconstruction, not a source port. `assets/` is immutable oracle evidence. Never relock fixtures and never feed original code bytes into reconstructed outputs (no byte arrays, inline asm, placement directives or copied data standing in for code).
- Keep natural object/hunk/overlay layout as the target. Numeric overlay names are containers; do not invent semantic names or source filenames. Printable runs are candidates, not string boundaries. Unknown ownership stays visible. Runtime ABI identification is not library provenance.
- Do not edit tools/, tests/, docs/, evidence/, recovery/, src/ or assets/, do not hand-edit generated ledgers, do not run `census.py --write`, `function_census.py` or `type_evidence.py --write`, and do not commit.
- Write files ONLY under `experiments/fleet/fn-ov11_F_415A/`. The tools themselves append to build/compile-cache and to the hypothesis ledger; that is expected.
- Never promote: never run check_function.py/check_unit.py without `--isolated`; use the wrappers below. Never delete lock files. If a tool reports a stale lock, stop and report BLOCKED quoting the message.
- The exact verifier alone decides EQUAL. Diagnostics and similarity scores are advisory. Other workers share this checkout; do not touch other experiments/ directories.

## Origin
`{"constraints":["NONCONTIGUOUS_LOCAL_UNIT"],"source":"ranked_frontier"}`

## Target facts
- `{"calls":["F_h11_3F90 PC_RELATIVE FUNCTION_CODE_MATCH","F_h11_4B0C PC_RELATIVE FUNCTION_CODE_MATCH"],"confidence":"HIGH","constraints":["NONCONTIGUOUS_LOCAL_UNIT"],"data":["G_h01_94AE","G_h01_94B6","G_h01_94C0","G_h01_94D4","G_h01_A156","G_h01_A15A","G_h01_A15E"],"end":"0x41F6","extent":"CLOSED_CFG","hunk":11,"id":"ov11_F_415A","indirect":0,"instructions":46,"jump_tables":0,"more_calls":0,"more_data":0,"node":"ov11","pc_relative_data":0,"size":156,"start":"0x415A","strings":0}`

## Prior hypotheses (do not repeat)
`{"summary":{"predictions":{},"shown":0,"trials":0,"verdicts":{}},"trials":[]}`

## Type evidence ov11_F_415A (advisory)
`{"declaration_conflicts":12,"frame":["+8 w=[2] n=1","+10 w=[4] n=2","+14 w=[4] n=1"],"globals":["G_h01_94AE w=[2] rw={'READ': 10, 'UNKNOWN': 28, 'WRITE': 34}","G_h01_94B6 w=[2] rw={'UNKNOWN': 11, 'WRITE': 9}","G_h01_94C0 w=[2] rw={'READ': 38, 'READ_WRITE': 4, 'UNKNOWN': 8, 'WRITE': 9}","G_h01_94D4 w=[2] rw={'READ': 5, 'WRITE': 3}","G_h01_A156 w=[2] rw={'READ': 1, 'UNKNOWN': 1, 'WRITE': 2}","G_h01_A15A w=[2] rw={'READ_WRITE': 1, 'UNKNOWN': 4, 'WRITE': 3}","G_h01_A15E w=[] rw={}"]}`

## Protocol
1. Inspect evidence (read-only): `python tools/grinder.py facts ID` (full disassembly/CFG/relocations), `python tools/diag.py ID --cache-key KEY` for any cached key, `python tools/type_evidence.py --function ID`, `python tools/shape_search.py --ledger-summary ID`, docs/source-shape-search.md, docs/m68k-diagnostics.md.
2. BEFORE compiling, record each hypothesis with a machine-checkable prediction. Write a schema v2 manifest `experiments/fleet/fn-ov11_F_415A/manifest-NN.json` (docs/source-shape-search.md): every variant has parent, suspected_cause, controlled_change and predicted_effect {length_delta, removed_candidate_only, register_role_diffs, note}. Name a measured parent (an earlier variant, a compiled .c path, `ledger:N` or a 64-hex cache key); parent `none` leaves every prediction unmeasurable. Sources: `experiments/fleet/fn-ov11_F_415A/*.c` (self-contained K&R C defining `recovered(...)`, mechanical G_hNN_XXXX/F_hNN_XXXX externs).
3. Each variant makes ONE controlled change from its parent. Do not resubmit a hypothesis listed under prior hypotheses; the ledger rejects normalized duplicates and returns the earlier record, which you must read instead.
4. Compile via: `python tools/shape_search.py experiments/fleet/fn-ov11_F_415A/manifest-NN.json --output-dir experiments/fleet/fn-ov11_F_415A/runs --json` (isolated; records the ledger; add `--measure-parents` to compile an unmeasured parent as a counted trial). For owned CODE data or m.lib only: `python tools/fleet.py verify-function ID SRC --profile P [--owned-code-data] [--with-m-lib] --output-dir experiments/fleet/fn-ov11_F_415A/runs`.
   Compiles are queued and batched across workers (a cache miss may wait minutes); cache hits are instant. Never loop on a failing tool.
5. Budget: at most 24 compiler trials and 6 variants per manifest. Stop at an exact EQUAL, at budget, or after three consecutive refuted predictions in one causal family without new evidence (switch family once, then report).
6. Write `experiments/fleet/fn-ov11_F_415A/result.json` exactly per the schema below using Python `json.dump` (UTF-8, no BOM; never an empty file), check it with `python tools/fleet.py intake fn-ov11_F_415A --dry-run`, fix any REJECTED reason, then reply with one line: `TASK fn-ov11_F_415A <STATUS> experiments/fleet/fn-ov11_F_415A/result.json`.

## result.json (closed schema; intake re-verifies every EQUAL claim)
```json
{"schema_version":1,"task_id":"fn-ov11_F_415A","worker":"<your -n name>",
 "status":"EQUAL_CANDIDATE|NEAR|BLOCKED|NEEDS_EVIDENCE",
 "target":"ov11_F_415A",
 "best":null or {"source":"experiments/fleet/fn-ov11_F_415A/<file>.c","profile":"aztec36","cache_key":"<64 hex>",
   "verdict":"EQUAL|DIFFER|BLOCKED","verifier":"check_function","entry":"<evidence id of the member compiled as recovered(), e.g. ov11_F_415A>",
   "options":["owned_code_data","with_m_lib"],"expected_length":0,"actual_length":0},
 "hypotheses":[{"id":"h1","statement":"...","outcome":"confirmed|refuted|partial|unmeasurable|untested","evidence":"ledger line / report path"}],
 "compile_trials":0,"ledger_lines":[],
 "explanation":"what the evidence now shows (<=1200 chars)",
 "proposed_blocker":null or {"mechanism":"UPPER_SNAKE_CASE","text":"blocker text for docs/blockers.json curation"}}
```
EQUAL_CANDIDATE needs best.verdict EQUAL from an isolated run. NEAR needs best. BLOCKED needs proposed_blocker. NEEDS_EVIDENCE names the missing evidence in explanation. `entry` is required for check_unit and equals the target for check_function.
For check_unit with several new members, `best` may add `"members":{"<other member id>":"experiments/fleet/fn-ov11_F_415A/<file>.c"}` (the `--member` sources; never the entry).
