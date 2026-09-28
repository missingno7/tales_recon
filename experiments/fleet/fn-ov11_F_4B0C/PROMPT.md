# Fleet task fn-ov11_F_4B0C (function)

You are an autonomous worker on a historical Amiga 68k (Aztec C) reconstruction in `D:/Prog/tales_recon`. You have no memory beyond this prompt. Recover closed function ov11_F_4B0C (954 bytes)

Priority 27. Lease: worker `luna-fn-ov11_F_4B0C`, expires 2026-09-28T21:58:20+00:00 (renew: `python tools/fleet.py renew fn-ov11_F_4B0C --worker luna-fn-ov11_F_4B0C`).

## First step (host liveness)
Run `python tools/fleet.py renew fn-ov11_F_4B0C --worker luna-fn-ov11_F_4B0C` before anything else. If the shell does not return within about two minutes, or keeps failing to start commands, stop immediately and reply with one line: `TASK fn-ov11_F_4B0C BLOCKED HOST_TOOLS_UNRESPONSIVE` (no result.json needed; the supervisor releases the lease).

## Rules (binding; from AGENTS.md)
- Historical reconstruction, not a source port. `assets/` is immutable oracle evidence. Never relock fixtures and never feed original code bytes into reconstructed outputs (no byte arrays, inline asm, placement directives or copied data standing in for code).
- Keep natural object/hunk/overlay layout as the target. Numeric overlay names are containers; do not invent semantic names or source filenames. Printable runs are candidates, not string boundaries. Unknown ownership stays visible. Runtime ABI identification is not library provenance.
- Do not edit tools/, tests/, docs/, evidence/, recovery/, src/ or assets/, do not hand-edit generated ledgers, do not run `census.py --write`, `function_census.py` or `type_evidence.py --write`, and do not commit.
- Write files ONLY under `experiments/fleet/fn-ov11_F_4B0C/`. The tools themselves append to build/compile-cache and to the hypothesis ledger; that is expected.
- Never promote: never run check_function.py/check_unit.py without `--isolated`; use the wrappers below. Never delete lock files. If a tool reports a stale lock, stop and report BLOCKED quoting the message.
- The exact verifier alone decides EQUAL. Diagnostics and similarity scores are advisory. Other workers share this checkout; do not touch other experiments/ directories.

## Origin
`{"constraints":["NONCONTIGUOUS_LOCAL_UNIT"],"source":"ranked_frontier"}`

## Target facts
- `{"calls":["F_h00_57D2 A4_RELOCATED_JMP_STUB DISCOVERED x3","F_h11_6ED6 PC_RELATIVE FUNCTION_CODE_MATCH"],"confidence":"HIGH","constraints":["NONCONTIGUOUS_LOCAL_UNIT"],"data":["G_h01_00CC","G_h01_94B0","G_h01_94B2","G_h01_94B4","G_h01_94B6","G_h01_94BE","G_h01_94C0","G_h01_94D8","G_h01_94DA","G_h01_94DE","G_h01_94E0","G_h01_94E4","G_h01_94E6","G_h01_94E8","G_h01_94EC","G_h01_958C"],"end":"0x4EC6","extent":"CLOSED_CFG","hunk":11,"id":"ov11_F_4B0C","indirect":0,"instructions":256,"jump_tables":0,"more_calls":0,"more_data":21,"node":"ov11","pc_relative_data":0,"size":954,"start":"0x4B0C","strings":0}`

## Prior hypotheses (do not repeat)
`{"summary":{"predictions":{},"shown":0,"trials":0,"verdicts":{}},"trials":[]}`

## Type evidence ov11_F_4B0C (advisory)
`{"declaration_conflicts":1,"frame":["+8 w=[2] n=1"],"globals":["G_h01_00CC w=[] rw={'UNKNOWN': 208}","G_h01_94B0 w=[2] rw={'READ': 25, 'UNKNOWN': 20, 'WRITE': 3}","G_h01_94B2 w=[2] rw={'UNKNOWN': 1, 'WRITE': 1}","G_h01_94B4 w=[2] rw={'UNKNOWN': 6, 'WRITE': 5}","G_h01_94B6 w=[2] rw={'UNKNOWN': 11, 'WRITE': 9}","G_h01_94BE w=[2] rw={'READ': 34, 'READ_WRITE': 7, 'UNKNOWN': 6, 'WRITE': 1}","G_h01_94C0 w=[2] rw={'READ': 38, 'READ_WRITE': 4, 'UNKNOWN': 8, 'WRITE': 9}","G_h01_94D8 w=[2] rw={'READ': 3, 'READ_WRITE': 2, 'UNKNOWN': 2, 'WRITE': 4}"]}`

## Protocol
1. Inspect evidence (read-only): `python tools/grinder.py facts ID` (full disassembly/CFG/relocations), `python tools/diag.py ID --cache-key KEY` for any cached key, `python tools/type_evidence.py --function ID`, `python tools/shape_search.py --ledger-summary ID`, docs/source-shape-search.md, docs/m68k-diagnostics.md.
2. BEFORE compiling, record each hypothesis with a machine-checkable prediction. Write a schema v2 manifest `experiments/fleet/fn-ov11_F_4B0C/manifest-NN.json` (docs/source-shape-search.md): every variant has parent, suspected_cause, controlled_change and predicted_effect {length_delta, removed_candidate_only, register_role_diffs, note}. Name a measured parent (an earlier variant, a compiled .c path, `ledger:N` or a 64-hex cache key); parent `none` leaves every prediction unmeasurable. Sources: `experiments/fleet/fn-ov11_F_4B0C/*.c` (self-contained K&R C defining `recovered(...)`, mechanical G_hNN_XXXX/F_hNN_XXXX externs).
3. Each variant makes ONE controlled change from its parent. Do not resubmit a hypothesis listed under prior hypotheses; the ledger rejects normalized duplicates and returns the earlier record, which you must read instead.
4. Compile via: `python tools/shape_search.py experiments/fleet/fn-ov11_F_4B0C/manifest-NN.json --output-dir experiments/fleet/fn-ov11_F_4B0C/runs --json` (isolated; records the ledger; add `--measure-parents` to compile an unmeasured parent as a counted trial). For owned CODE data or m.lib only: `python tools/fleet.py verify-function ID SRC --profile P [--owned-code-data] [--with-m-lib] --output-dir experiments/fleet/fn-ov11_F_4B0C/runs`.
   Compiles are queued and batched across workers (a cache miss may wait minutes); cache hits are instant. Never loop on a failing tool.
5. Budget: at most 24 compiler trials and 6 variants per manifest. Stop at an exact EQUAL, at budget, or after three consecutive refuted predictions in one causal family without new evidence (switch family once, then report).
6. Write `experiments/fleet/fn-ov11_F_4B0C/result.json` exactly per the schema below using Python `json.dump` (UTF-8, no BOM; never an empty file), check it with `python tools/fleet.py intake fn-ov11_F_4B0C --dry-run`, fix any REJECTED reason, then reply with one line: `TASK fn-ov11_F_4B0C <STATUS> experiments/fleet/fn-ov11_F_4B0C/result.json`.

## result.json (closed schema; intake re-verifies every EQUAL claim)
```json
{"schema_version":1,"task_id":"fn-ov11_F_4B0C","worker":"<your -n name>",
 "status":"EQUAL_CANDIDATE|NEAR|BLOCKED|NEEDS_EVIDENCE",
 "target":"ov11_F_4B0C",
 "best":null or {"source":"experiments/fleet/fn-ov11_F_4B0C/<file>.c","profile":"aztec36","cache_key":"<64 hex>",
   "verdict":"EQUAL|DIFFER|BLOCKED","verifier":"check_function","entry":"<evidence id of the member compiled as recovered(), e.g. ov11_F_4B0C>",
   "options":["owned_code_data","with_m_lib"],"expected_length":0,"actual_length":0},
 "hypotheses":[{"id":"h1","statement":"...","outcome":"confirmed|refuted|partial|unmeasurable|untested","evidence":"ledger line / report path"}],
 "compile_trials":0,"ledger_lines":[],
 "explanation":"what the evidence now shows (<=1200 chars)",
 "proposed_blocker":null or {"mechanism":"UPPER_SNAKE_CASE","text":"blocker text for docs/blockers.json curation"}}
```
EQUAL_CANDIDATE needs best.verdict EQUAL from an isolated run. NEAR needs best. BLOCKED needs proposed_blocker. NEEDS_EVIDENCE names the missing evidence in explanation. `entry` is required for check_unit and equals the target for check_function.
For check_unit with several new members, `best` may add `"members":{"<other member id>":"experiments/fleet/fn-ov11_F_4B0C/<file>.c"}` (the `--member` sources; never the entry).
