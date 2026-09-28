# Fleet task fn-ov04_F_0536 (function)

You are an autonomous worker on a historical Amiga 68k (Aztec C) reconstruction in `D:/Prog/tales_recon`. You have no memory beyond this prompt. Recover closed function ov04_F_0536 (622 bytes)

Priority 44. Lease: worker `luna-fn-ov04_F_0536`, expires 2026-09-28T18:43:31+00:00 (renew: `python tools/fleet.py renew fn-ov04_F_0536 --worker luna-fn-ov04_F_0536`).

## Rules (binding; from AGENTS.md)
- Historical reconstruction, not a source port. `assets/` is immutable oracle evidence. Never relock fixtures and never feed original code bytes into reconstructed outputs (no byte arrays, inline asm, placement directives or copied data standing in for code).
- Keep natural object/hunk/overlay layout as the target. Numeric overlay names are containers; do not invent semantic names or source filenames. Printable runs are candidates, not string boundaries. Unknown ownership stays visible. Runtime ABI identification is not library provenance.
- Do not edit tools/, tests/, docs/, evidence/, recovery/, src/ or assets/, do not hand-edit generated ledgers, do not run `census.py --write`, `function_census.py` or `type_evidence.py --write`, and do not commit.
- Write files ONLY under `experiments/fleet/fn-ov04_F_0536/`. The tools themselves append to build/compile-cache and to the hypothesis ledger; that is expected.
- Never promote: never run check_function.py/check_unit.py without `--isolated`; use the wrappers below. Never delete lock files. If a tool reports a stale lock, stop and report BLOCKED quoting the message.
- The exact verifier alone decides EQUAL. Diagnostics and similarity scores are advisory. Other workers share this checkout; do not touch other experiments/ directories.

## Origin
`{"constraints":["PC_RELATIVE_DATA_OWNERSHIP"],"source":"ranked_frontier"}`

## Target facts
- `{"calls":["F_h00_0FDE A4_RELOCATED_JMP_STUB DISCOVERED x3","F_h00_86DC A4_RELOCATED_JMP_STUB DISCOVERED x2","F_h00_2816 A4_RELOCATED_JMP_STUB DISCOVERED x3","F_h00_291E A4_RELOCATED_JMP_STUB DISCOVERED x2","F_h00_0976 A4_RELOCATED_JMP_STUB DISCOVERED x3","F_h00_704E A4_RELOCATED_JMP_STUB DISCOVERED x2","F_h00_463E A4_RELOCATED_JMP_STUB DISCOVERED x2","F_h00_3C0E A4_RELOCATED_JMP_STUB DISCOVERED x2","F_h00_868C A4_RELOCATED_JMP_STUB DISCOVERED x2"],"confidence":"HIGH","constraints":["PC_RELATIVE_DATA_OWNERSHIP"],"data":["G_h01_0012","G_h01_001E","G_h01_002A","G_h01_0030","G_h01_0096","G_h01_00A8","G_h01_00D2","G_h01_0114","G_h01_0120","G_h01_46DA","G_h01_4D60","G_h01_4D62","G_h01_4D82","G_h01_4D84","G_h01_4D86","G_h01_4D88"],"end":"0x07A4","extent":"CLOSED_CFG","hunk":4,"id":"ov04_F_0536","indirect":0,"instructions":176,"jump_tables":0,"more_calls":0,"more_data":5,"node":"ov04","pc_relative_data":4,"size":622,"start":"0x0536","strings":4}`

## Prior hypotheses (do not repeat)
`{"summary":{"predictions":{},"shown":0,"trials":0,"verdicts":{}},"trials":[]}`

## Type evidence ov04_F_0536 (advisory)
`{"declaration_conflicts":0,"frame":[],"globals":["G_h01_0012 w=[] rw={'UNKNOWN': 24}","G_h01_001E w=[] rw={'UNKNOWN': 101}","G_h01_002A w=[] rw={'UNKNOWN': 58}","G_h01_0030 w=[] rw={'UNKNOWN': 285}","G_h01_0096 w=[] rw={'UNKNOWN': 12}","G_h01_00A8 w=[] rw={'UNKNOWN': 97}","G_h01_00D2 w=[] rw={'UNKNOWN': 33}","G_h01_0114 w=[] rw={'UNKNOWN': 20}"]}`

## Protocol
1. Inspect evidence (read-only): `python tools/grinder.py facts ID` (full disassembly/CFG/relocations), `python tools/diag.py ID --cache-key KEY` for any cached key, `python tools/type_evidence.py --function ID`, `python tools/shape_search.py --ledger-summary ID`, docs/source-shape-search.md, docs/m68k-diagnostics.md.
2. BEFORE compiling, record each hypothesis with a machine-checkable prediction. Write a schema v2 manifest `experiments/fleet/fn-ov04_F_0536/manifest-NN.json` (docs/source-shape-search.md): every variant has parent, suspected_cause, controlled_change and predicted_effect {length_delta, removed_candidate_only, register_role_diffs, note}. Sources: `experiments/fleet/fn-ov04_F_0536/*.c` (self-contained K&R C defining `recovered(...)`, mechanical G_hNN_XXXX/F_hNN_XXXX externs).
3. Each variant makes ONE controlled change from its parent. Do not resubmit a hypothesis listed under prior hypotheses; the ledger rejects normalized duplicates and returns the earlier record, which you must read instead.
4. Compile via: `python tools/shape_search.py experiments/fleet/fn-ov04_F_0536/manifest-NN.json --output-dir experiments/fleet/fn-ov04_F_0536/runs --json` (isolated; records the ledger). For owned CODE data or m.lib only: `python tools/fleet.py verify-function ID SRC --profile P [--owned-code-data] [--with-m-lib] --output-dir experiments/fleet/fn-ov04_F_0536/runs`.
   Compiles are queued and batched across workers (a cache miss may wait minutes); cache hits are instant. Never loop on a failing tool.
5. Budget: at most 24 compiler trials and 6 variants per manifest. Stop at an exact EQUAL, at budget, or after three consecutive refuted predictions in one causal family without new evidence (switch family once, then report).
6. Write `experiments/fleet/fn-ov04_F_0536/result.json` exactly per the schema below, then reply with one line: `TASK fn-ov04_F_0536 <STATUS> experiments/fleet/fn-ov04_F_0536/result.json`.

## result.json (closed schema; intake re-verifies every EQUAL claim)
```json
{"schema_version":1,"task_id":"fn-ov04_F_0536","worker":"<your -n name>",
 "status":"EQUAL_CANDIDATE|NEAR|BLOCKED|NEEDS_EVIDENCE",
 "target":"ov04_F_0536",
 "best":null or {"source":"experiments/fleet/fn-ov04_F_0536/<file>.c","profile":"aztec36","cache_key":"<64 hex>",
   "verdict":"EQUAL|DIFFER|BLOCKED","verifier":"check_function","entry":"<member compiled as recovered>",
   "options":["owned_code_data","with_m_lib"],"expected_length":0,"actual_length":0},
 "hypotheses":[{"id":"h1","statement":"...","outcome":"confirmed|refuted|partial|unmeasurable|untested","evidence":"ledger line / report path"}],
 "compile_trials":0,"ledger_lines":[],
 "explanation":"what the evidence now shows (<=1200 chars)",
 "proposed_blocker":null or {"mechanism":"UPPER_SNAKE_CASE","text":"blocker text for docs/blockers.json curation"}}
```
EQUAL_CANDIDATE needs best.verdict EQUAL from an isolated run. NEAR needs best. BLOCKED needs proposed_blocker. NEEDS_EVIDENCE names the missing evidence in explanation. `entry` is required for check_unit and equals the target for check_function.
