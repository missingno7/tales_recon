# Fleet task fn-ov08_F_1D42 (function)

You are an autonomous worker on a historical Amiga 68k (Aztec C) reconstruction in `D:/Prog/tales_recon`. You have no memory beyond this prompt. Recover closed function ov08_F_1D42 (522 bytes)

Priority 44. Lease: worker `luna-fn-ov08_F_1D42`, expires 2026-09-28T21:45:39+00:00 (renew: `python tools/fleet.py renew fn-ov08_F_1D42 --worker luna-fn-ov08_F_1D42`).

## First step (host liveness)
Run `python tools/fleet.py renew fn-ov08_F_1D42 --worker luna-fn-ov08_F_1D42` before anything else. If the shell does not return within about two minutes, or keeps failing to start commands, stop immediately and reply with one line: `TASK fn-ov08_F_1D42 BLOCKED HOST_TOOLS_UNRESPONSIVE` (no result.json needed; the supervisor releases the lease).

## Rules (binding; from AGENTS.md)
- Historical reconstruction, not a source port. `assets/` is immutable oracle evidence. Never relock fixtures and never feed original code bytes into reconstructed outputs (no byte arrays, inline asm, placement directives or copied data standing in for code).
- Keep natural object/hunk/overlay layout as the target. Numeric overlay names are containers; do not invent semantic names or source filenames. Printable runs are candidates, not string boundaries. Unknown ownership stays visible. Runtime ABI identification is not library provenance.
- Do not edit tools/, tests/, docs/, evidence/, recovery/, src/ or assets/, do not hand-edit generated ledgers, do not run `census.py --write`, `function_census.py` or `type_evidence.py --write`, and do not commit.
- Write files ONLY under `experiments/fleet/fn-ov08_F_1D42/`. The tools themselves append to build/compile-cache and to the hypothesis ledger; that is expected.
- Never promote: never run check_function.py/check_unit.py without `--isolated`; use the wrappers below. Never delete lock files. If a tool reports a stale lock, stop and report BLOCKED quoting the message.
- The exact verifier alone decides EQUAL. Diagnostics and similarity scores are advisory. Other workers share this checkout; do not touch other experiments/ directories.

## Origin
`{"constraints":[],"source":"ranked_frontier"}`

## Target facts
- `{"calls":["F_h00_8B88 A4_RELOCATED_JMP_STUB DISCOVERED x5","F_h00_8B76 A4_RELOCATED_JMP_STUB DISCOVERED","F_h00_8B4C A4_RELOCATED_JMP_STUB DISCOVERED x4","F_h00_8AA8 A4_RELOCATED_JMP_STUB DISCOVERED x4","F_h00_34E0 A4_RELOCATED_JMP_STUB DISCOVERED x3","F_h00_09C0 A4_RELOCATED_JMP_STUB DISCOVERED x3"],"confidence":"HIGH","constraints":[],"data":["G_h01_0018","G_h01_0054","G_h01_0162","G_h01_01A4","G_h01_01B6","G_h01_01BC","G_h01_33EE","G_h01_3424","G_h01_345A","G_h01_345C","G_h01_348E","G_h01_46CA","G_h01_46E1","G_h01_46E6","G_h01_5370","G_h01_6F3B"],"end":"0x1F4C","extent":"CLOSED_CFG","hunk":8,"id":"ov08_F_1D42","indirect":0,"instructions":153,"jump_tables":0,"more_calls":0,"more_data":0,"node":"ov08","pc_relative_data":0,"size":522,"start":"0x1D42","strings":0}`

## Prior hypotheses (do not repeat)
`{"summary":{"predictions":{},"shown":0,"trials":0,"verdicts":{}},"trials":[]}`

## Type evidence ov08_F_1D42 (advisory)
`{"declaration_conflicts":0,"frame":[],"globals":["G_h01_0018 w=[] rw={'UNKNOWN': 40}","G_h01_0054 w=[] rw={'UNKNOWN': 277}","G_h01_0162 w=[] rw={'UNKNOWN': 66}","G_h01_01A4 w=[] rw={'UNKNOWN': 67}","G_h01_01B6 w=[] rw={'UNKNOWN': 2}","G_h01_01BC w=[] rw={'UNKNOWN': 76}","G_h01_33EE w=[2] rw={'WRITE': 1}","G_h01_3424 w=[2] rw={'WRITE': 1}"]}`

## Protocol
1. Inspect evidence (read-only): `python tools/grinder.py facts ID` (full disassembly/CFG/relocations), `python tools/diag.py ID --cache-key KEY` for any cached key, `python tools/type_evidence.py --function ID`, `python tools/shape_search.py --ledger-summary ID`, docs/source-shape-search.md, docs/m68k-diagnostics.md.
2. BEFORE compiling, record each hypothesis with a machine-checkable prediction. Write a schema v2 manifest `experiments/fleet/fn-ov08_F_1D42/manifest-NN.json` (docs/source-shape-search.md): every variant has parent, suspected_cause, controlled_change and predicted_effect {length_delta, removed_candidate_only, register_role_diffs, note}. Name a measured parent (an earlier variant, a compiled .c path, `ledger:N` or a 64-hex cache key); parent `none` leaves every prediction unmeasurable. Sources: `experiments/fleet/fn-ov08_F_1D42/*.c` (self-contained K&R C defining `recovered(...)`, mechanical G_hNN_XXXX/F_hNN_XXXX externs).
3. Each variant makes ONE controlled change from its parent. Do not resubmit a hypothesis listed under prior hypotheses; the ledger rejects normalized duplicates and returns the earlier record, which you must read instead.
4. Compile via: `python tools/shape_search.py experiments/fleet/fn-ov08_F_1D42/manifest-NN.json --output-dir experiments/fleet/fn-ov08_F_1D42/runs --json` (isolated; records the ledger; add `--measure-parents` to compile an unmeasured parent as a counted trial). For owned CODE data or m.lib only: `python tools/fleet.py verify-function ID SRC --profile P [--owned-code-data] [--with-m-lib] --output-dir experiments/fleet/fn-ov08_F_1D42/runs`.
   Compiles are queued and batched across workers (a cache miss may wait minutes); cache hits are instant. Never loop on a failing tool.
5. Budget: at most 24 compiler trials and 6 variants per manifest. Stop at an exact EQUAL, at budget, or after three consecutive refuted predictions in one causal family without new evidence (switch family once, then report).
6. Write `experiments/fleet/fn-ov08_F_1D42/result.json` exactly per the schema below using Python `json.dump` (UTF-8, no BOM; never an empty file), check it with `python tools/fleet.py intake fn-ov08_F_1D42 --dry-run`, fix any REJECTED reason, then reply with one line: `TASK fn-ov08_F_1D42 <STATUS> experiments/fleet/fn-ov08_F_1D42/result.json`.

## result.json (closed schema; intake re-verifies every EQUAL claim)
```json
{"schema_version":1,"task_id":"fn-ov08_F_1D42","worker":"<your -n name>",
 "status":"EQUAL_CANDIDATE|NEAR|BLOCKED|NEEDS_EVIDENCE",
 "target":"ov08_F_1D42",
 "best":null or {"source":"experiments/fleet/fn-ov08_F_1D42/<file>.c","profile":"aztec36","cache_key":"<64 hex>",
   "verdict":"EQUAL|DIFFER|BLOCKED","verifier":"check_function","entry":"<evidence id of the member compiled as recovered(), e.g. ov08_F_1D42>",
   "options":["owned_code_data","with_m_lib"],"expected_length":0,"actual_length":0},
 "hypotheses":[{"id":"h1","statement":"...","outcome":"confirmed|refuted|partial|unmeasurable|untested","evidence":"ledger line / report path"}],
 "compile_trials":0,"ledger_lines":[],
 "explanation":"what the evidence now shows (<=1200 chars)",
 "proposed_blocker":null or {"mechanism":"UPPER_SNAKE_CASE","text":"blocker text for docs/blockers.json curation"}}
```
EQUAL_CANDIDATE needs best.verdict EQUAL from an isolated run. NEAR needs best. BLOCKED needs proposed_blocker. NEEDS_EVIDENCE names the missing evidence in explanation. `entry` is required for check_unit and equals the target for check_function.
For check_unit with several new members, `best` may add `"members":{"<other member id>":"experiments/fleet/fn-ov08_F_1D42/<file>.c"}` (the `--member` sources; never the entry).
