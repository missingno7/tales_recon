# Fleet task blk-ov11_F_5FB2 (blocker-probe)

You are an autonomous worker on a historical Amiga 68k (Aztec C) reconstruction in `D:/Prog/tales_recon`. You have no memory beyond this prompt. Probe blocker ov11_F_5FB2 (EXTERNAL_CALL_BINDING) with a changed hypothesis

Priority 20. Lease: worker `luna-blk-ov11_F_5FB2`, expires 2026-09-28T22:11:32+00:00 (renew: `python tools/fleet.py renew blk-ov11_F_5FB2 --worker luna-blk-ov11_F_5FB2`).

## First step (host liveness)
Run `python tools/fleet.py renew blk-ov11_F_5FB2 --worker luna-blk-ov11_F_5FB2` before anything else. The host is shared and heavily loaded: a single command can take 1-3 minutes to start and finish. Run commands one at a time (never batch several commands in parallel), wait on slow commands instead of terminating them, and keep outputs small. Do not read whole docs/*.json ledgers or long docs; this packet already carries the binding rules and target facts, so use targeted queries. Only if this `renew` command itself has still not returned after 10 minutes, stop and reply with one line: `TASK blk-ov11_F_5FB2 BLOCKED HOST_TOOLS_UNRESPONSIVE` (no result.json needed; the supervisor releases the lease).

## Rules (binding; from AGENTS.md)
- Historical reconstruction, not a source port. `assets/` is immutable oracle evidence. Never relock fixtures and never feed original code bytes into reconstructed outputs (no byte arrays, inline asm, placement directives or copied data standing in for code).
- Keep natural object/hunk/overlay layout as the target. Numeric overlay names are containers; do not invent semantic names or source filenames. Printable runs are candidates, not string boundaries. Unknown ownership stays visible. Runtime ABI identification is not library provenance.
- Do not edit tools/, tests/, docs/, evidence/, recovery/, src/ or assets/, do not hand-edit generated ledgers, do not run `census.py --write`, `function_census.py` or `type_evidence.py --write`, and do not commit.
- Write files ONLY under `experiments/fleet/blk-ov11_F_5FB2/`. The tools themselves append to build/compile-cache and to the hypothesis ledger; that is expected.
- Never promote: never run check_function.py/check_unit.py without `--isolated`; use the wrappers below. Never delete lock files. If a tool reports a stale lock, stop and report BLOCKED quoting the message.
- The exact verifier alone decides EQUAL. Diagnostics and similarity scores are advisory. Other workers share this checkout; do not touch other experiments/ directories.

## Origin
`{"mechanism":"EXTERNAL_CALL_BINDING","source":"recovery_blockers"}`

## Target facts
- `{"calls":["F_h00_8D1E A4_RELOCATED_JMP_STUB DISCOVERED x3","F_h00_8D0A A4_RELOCATED_JMP_STUB DISCOVERED","F_h00_8D28 A4_RELOCATED_JMP_STUB DISCOVERED","F_h00_8D14 A4_RELOCATED_JMP_STUB DISCOVERED","F_h00_8D00 A4_RELOCATED_JMP_STUB DISCOVERED"],"confidence":"HIGH","constraints":[],"data":["G_h01_0228","G_h01_022E","G_h01_0234","G_h01_023A","G_h01_0240","G_h01_37EE","G_h01_37F0","G_h01_8BEC","G_h01_94B0","G_h01_94BE","G_h01_94C0"],"end":"0x6080","extent":"CLOSED_CFG","hunk":11,"id":"ov11_F_5FB2","indirect":0,"instructions":58,"jump_tables":0,"more_calls":0,"more_data":0,"node":"ov11","pc_relative_data":0,"size":206,"start":"0x5FB2","strings":0}`

## Recorded blocker ov11_F_5FB2
UNSUPPORTED_REGISTER_CALL_ABI: resident F_8Dxx vector wrappers require D-register arguments. Aztec 3.6a rejects #pragma regcall before compilation; ordinary stack calls cannot express the observed D0/D1 sequence. Retain three bounded trial receipts; add a historically supported 3.6a register-call mechanism before retrying.
Next action: Revise ABI/data hypothesis or use a stronger model; retry explicitly

## Prior verifier attempts ov11_F_5FB2 (3 total, latest 3)
- `{"actual":null,"cache_key":"ceefbbd3aacd7388e4f6991a1994218d67e18b348567c7780b320292688e2fe1","expected":206,"first_diff":null,"profile":"aztec36","similarity":null,"source":"recovery/candidates/ov11_F_5FB2/2555713430645dc61d3ccfa7977e4564e054b3932f3e1831c42c45aea55a198c.c","verdict":"BLOCKED"}`
- `{"actual":null,"cache_key":"e52e1ba012e5c2c73b2d3124257ea532765af3293382fd9339ec1817dbd9163c","expected":206,"first_diff":null,"profile":"aztec36","similarity":null,"source":"recovery/candidates/ov11_F_5FB2/2555713430645dc61d3ccfa7977e4564e054b3932f3e1831c42c45aea55a198c.c","verdict":"BLOCKED"}`
- `{"actual":null,"cache_key":"03cb38683161194ec58a4a26914968d407962256337bba12f8ba35bfad8bf021","expected":206,"first_diff":null,"profile":"aztec36","similarity":null,"source":"recovery/candidates/ov11_F_5FB2/092de8e0061c20c4e1f074d1c7172e0443ae434872164bb1bd5cba465bac4eec.c","verdict":"BLOCKED"}`

## Prior hypotheses (do not repeat)
`{"summary":{"predictions":{},"shown":0,"trials":0,"verdicts":{}},"trials":[]}`

## Type evidence ov11_F_5FB2 (advisory)
`{"declaration_conflicts":1,"frame":["+8 w=[2] n=1"],"globals":["G_h01_0228 w=[] rw={'UNKNOWN': 56}","G_h01_022E w=[] rw={'UNKNOWN': 11}","G_h01_0234 w=[] rw={'UNKNOWN': 4}","G_h01_023A w=[] rw={'UNKNOWN': 36}","G_h01_0240 w=[] rw={'UNKNOWN': 12}","G_h01_37EE w=[2] rw={'READ': 1, 'WRITE': 4}","G_h01_37F0 w=[2] rw={'READ': 2, 'WRITE': 4}","G_h01_8BEC w=[] rw={}"]}`

## Protocol
1. Inspect evidence (read-only): `python tools/grinder.py facts ID` (full disassembly/CFG/relocations), `python tools/diag.py ID --cache-key KEY` for any cached key, `python tools/type_evidence.py --function ID`, `python tools/shape_search.py --ledger-summary ID`, docs/source-shape-search.md, docs/m68k-diagnostics.md.
2. BEFORE compiling, record each hypothesis with a machine-checkable prediction. Write a schema v2 manifest `experiments/fleet/blk-ov11_F_5FB2/manifest-NN.json` (docs/source-shape-search.md): every variant has parent, suspected_cause, controlled_change and predicted_effect {length_delta, removed_candidate_only, register_role_diffs, note}. Name a measured parent (an earlier variant, a compiled .c path, `ledger:N` or a 64-hex cache key); parent `none` leaves every prediction unmeasurable. Sources: `experiments/fleet/blk-ov11_F_5FB2/*.c` (self-contained K&R C defining `recovered(...)`, mechanical G_hNN_XXXX/F_hNN_XXXX externs).
3. Each variant makes ONE controlled change from its parent. Do not resubmit a hypothesis listed under prior hypotheses; the ledger rejects normalized duplicates and returns the earlier record, which you must read instead.
4. Compile via: `python tools/shape_search.py experiments/fleet/blk-ov11_F_5FB2/manifest-NN.json --output-dir experiments/fleet/blk-ov11_F_5FB2/runs --json` (isolated; records the ledger; add `--measure-parents` to compile an unmeasured parent as a counted trial). For owned CODE data or m.lib only: `python tools/fleet.py verify-function ID SRC --profile P [--owned-code-data] [--with-m-lib] --output-dir experiments/fleet/blk-ov11_F_5FB2/runs`.
   Compiles are queued and batched across workers (a cache miss may wait minutes); cache hits are instant. Never loop on a failing tool.
5. Budget: at most 16 compiler trials and 4 variants per manifest. Stop at an exact EQUAL, at budget, or after three consecutive refuted predictions in one causal family without new evidence (switch family once, then report).
6. Write `experiments/fleet/blk-ov11_F_5FB2/result.json` exactly per the schema below using Python `json.dump` (UTF-8, no BOM; never an empty file), check it with `python tools/fleet.py intake blk-ov11_F_5FB2 --dry-run`, fix any REJECTED reason, then reply with one line: `TASK blk-ov11_F_5FB2 <STATUS> experiments/fleet/blk-ov11_F_5FB2/result.json`.

## result.json (closed schema; intake re-verifies every EQUAL claim)
```json
{"schema_version":1,"task_id":"blk-ov11_F_5FB2","worker":"<your -n name>",
 "status":"EQUAL_CANDIDATE|NEAR|BLOCKED|NEEDS_EVIDENCE",
 "target":"ov11_F_5FB2",
 "best":null or {"source":"experiments/fleet/blk-ov11_F_5FB2/<file>.c","profile":"aztec36","cache_key":"<64 hex>",
   "verdict":"EQUAL|DIFFER|BLOCKED","verifier":"check_function","entry":"<evidence id of the member compiled as recovered(), e.g. ov11_F_5FB2>",
   "options":["owned_code_data","with_m_lib"],"expected_length":0,"actual_length":0},
 "hypotheses":[{"id":"h1","statement":"...","outcome":"confirmed|refuted|partial|unmeasurable|untested","evidence":"ledger line / report path"}],
 "compile_trials":0,"ledger_lines":[],
 "explanation":"what the evidence now shows (<=1200 chars)",
 "proposed_blocker":null or {"mechanism":"UPPER_SNAKE_CASE","text":"blocker text for docs/blockers.json curation"}}
```
EQUAL_CANDIDATE needs best.verdict EQUAL from an isolated run. NEAR needs best. BLOCKED needs proposed_blocker. NEEDS_EVIDENCE names the missing evidence in explanation. `entry` is required for check_unit and equals the target for check_function.
For check_unit with several new members, `best` may add `"members":{"<other member id>":"experiments/fleet/blk-ov11_F_5FB2/<file>.c"}` (the `--member` sources; never the entry).
