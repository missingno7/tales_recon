# Fleet task unit-ov11_F_5962-5C42 (unit)

You are an autonomous worker on a historical Amiga 68k (Aztec C) reconstruction in `D:/Prog/tales_recon`. You have no memory beyond this prompt. Same-hunk dependency cycle ov11_F_5962, ov11_F_5C42 as one natural source-unit hypothesis

Priority 10. Lease: worker `luna-unit-ov11_F_5962-5C42`, expires 2026-09-28T21:22:42+00:00 (renew: `python tools/fleet.py renew unit-ov11_F_5962-5C42 --worker luna-unit-ov11_F_5962-5C42`).

## First step (host liveness)
Run `python tools/fleet.py renew unit-ov11_F_5962-5C42 --worker luna-unit-ov11_F_5962-5C42` before anything else. If the shell does not return within about two minutes, or keeps failing to start commands, stop immediately and reply with one line: `TASK unit-ov11_F_5962-5C42 BLOCKED HOST_TOOLS_UNRESPONSIVE` (no result.json needed; the supervisor releases the lease).

## Rules (binding; from AGENTS.md)
- Historical reconstruction, not a source port. `assets/` is immutable oracle evidence. Never relock fixtures and never feed original code bytes into reconstructed outputs (no byte arrays, inline asm, placement directives or copied data standing in for code).
- Keep natural object/hunk/overlay layout as the target. Numeric overlay names are containers; do not invent semantic names or source filenames. Printable runs are candidates, not string boundaries. Unknown ownership stays visible. Runtime ABI identification is not library provenance.
- Do not edit tools/, tests/, docs/, evidence/, recovery/, src/ or assets/, do not hand-edit generated ledgers, do not run `census.py --write`, `function_census.py` or `type_evidence.py --write`, and do not commit.
- Write files ONLY under `experiments/fleet/unit-ov11_F_5962-5C42/`. The tools themselves append to build/compile-cache and to the hypothesis ledger; that is expected.
- Never promote: never run check_function.py/check_unit.py without `--isolated`; use the wrappers below. Never delete lock files. If a tool reports a stale lock, stop and report BLOCKED quoting the message.
- The exact verifier alone decides EQUAL. Diagnostics and similarity scores are advisory. Other workers share this checkout; do not touch other experiments/ directories.

## Origin
`{"metadata":{"bridge_functions":["ov11_F_5A12","ov11_F_5A62","ov11_F_5AB0","ov11_F_5BC4","ov11_F_5C1A"],"canonical_bridge_ids":["ov11_F_5A12","ov11_F_5A62","ov11_F_5AB0","ov11_F_5BC4","ov11_F_5C1A"],"external_unrecovered_dependencies":[],"hunk":11,"interval":[22882,23786],"unclassified_gaps":[[23014,23058]],"unknown_bridge_ids":[]},"package_kind":"DEPENDENCY_SCC_REVIEW","rationale":"A same-hunk call cycle exists, but its bounded interval or dependency closure is incomplete; this is a review hypothesis, not a unit-ready claim.","source":"recovery_plan"}`

## Target facts
- `{"calls":["F_h11_5C42 PC_RELATIVE DISCOVERED","F_h11_66FE PC_RELATIVE FUNCTION_CODE_MATCH"],"confidence":"HIGH","constraints":["UNRECOVERED_LOCAL_DEPENDENCY","NONCONTIGUOUS_LOCAL_UNIT"],"data":["G_h01_8BEC"],"end":"0x59E6","extent":"CLOSED_CFG","hunk":11,"id":"ov11_F_5962","indirect":0,"instructions":36,"jump_tables":0,"more_calls":0,"more_data":0,"node":"ov11","pc_relative_data":0,"size":132,"start":"0x5962","strings":0}`
- `{"calls":["F_h11_4696 PC_RELATIVE FUNCTION_CODE_MATCH","F_h11_5962 PC_RELATIVE DISCOVERED x2"],"confidence":"HIGH","constraints":["UNRECOVERED_LOCAL_DEPENDENCY","NONCONTIGUOUS_LOCAL_UNIT"],"data":["G_h01_8BEC"],"end":"0x5CEA","extent":"CLOSED_CFG","hunk":11,"id":"ov11_F_5C42","indirect":0,"instructions":46,"jump_tables":0,"more_calls":0,"more_data":0,"node":"ov11","pc_relative_data":0,"size":168,"start":"0x5C42","strings":0}`

## Recorded blocker ov11_F_5962
CYCLIC_INTER_OBJECT_PC_CALL: the compact cluster still shortens F_h11_5C42 -> F_h11_4696 to BSR.b, but an ordinary earlier-object link now proves the historical backward JSR.d16(PC) form is retained without padding or copied bytes. Its remaining differences are only A4/global placement and PC-relative displacement. Exact displacement requires the full physical 0x4790..0x5962 interval: 858 canonical bytes, seven discovered unrecovered candidates totaling 3664 bytes, and 40 unclaimed bytes. Recover that interval in physical source order before another normal layout proof; do not retry isolated members.
Next action: Recover and link the 0x4790..0x5962 physical ov11 source interval in order as a normal source-layout proof. Ordinary earlier-object linking is proven to reta...

## Recorded blocker ov11_F_5C42
CYCLIC_INTER_OBJECT_PC_CALL: the compact cluster still shortens F_h11_5C42 -> F_h11_4696 to BSR.b, but an ordinary earlier-object link now proves the historical backward JSR.d16(PC) form is retained without padding or copied bytes. Its remaining differences are only A4/global placement and PC-relative displacement. Exact displacement requires the full physical 0x4790..0x5962 interval: 858 canonical bytes, seven discovered unrecovered candidates totaling 3664 bytes, and 40 unclaimed bytes. Recover that interval in physical source order before another normal layout proof; do not retry isolated members.
Next action: Recover and link the 0x4790..0x5962 physical ov11 source interval in order as a normal source-layout proof. Ordinary earlier-object linking is proven to reta...

## Prior hypotheses (do not repeat)
`{"summary":{"predictions":{},"shown":0,"trials":0,"verdicts":{}},"trials":[]}`

Note: Unit acceptance is complete-object check_unit; original gaps stay unclaimed.

Note: Author every unrecovered member: the ENTRY source is compiled as recovered(), each other new member is passed as `--member ID=SRC` (its source also defines recovered(); calls use mechanical F_hNN_XXXX names, including calls back to the entry). The unit is EQUAL only if every member is EQUAL; report the non-entry sources in best.members.

## Type evidence ov11_F_5962 (advisory)
`{"declaration_conflicts":1,"frame":["+8 w=[2] n=2","+10 w=[2] n=4"],"globals":["G_h01_8BEC w=[] rw={}"]}`

## Type evidence ov11_F_5C42 (advisory)
`{"declaration_conflicts":1,"frame":["+8 w=[2] n=1","+10 w=[2] n=3"],"globals":["G_h01_8BEC w=[] rw={}"]}`

## Protocol
1. Inspect evidence (read-only): `python tools/grinder.py facts ID` (full disassembly/CFG/relocations), `python tools/diag.py ID --cache-key KEY` for any cached key, `python tools/type_evidence.py --function ID`, `python tools/shape_search.py --ledger-summary ID`, docs/source-shape-search.md, docs/m68k-diagnostics.md, docs/unit-diagnostics.md.
2. BEFORE compiling, record each hypothesis with a machine-checkable prediction. Append one JSON line per hypothesis to `experiments/fleet/unit-ov11_F_5962-5C42/hypotheses.jsonl`: {"id","parent","suspected_cause","controlled_change","prediction"} with a concrete length/diff prediction. Unit member sources: copy candidates into `experiments/fleet/unit-ov11_F_5962-5C42/` and edit there.
3. Each variant makes ONE controlled change from its parent. Do not resubmit a hypothesis listed under prior hypotheses; the ledger rejects normalized duplicates and returns the earlier record, which you must read instead.
4. Compile via: `python tools/fleet.py verify-unit ENTRY experiments/fleet/unit-ov11_F_5962-5C42/<entry>.c [--member ID=experiments/fleet/unit-ov11_F_5962-5C42/<member>.c ...] --profile aztec36 [--separate-objects] [--allow-original-gaps] [--join-direct-callees] --output-dir experiments/fleet/unit-ov11_F_5962-5C42/runs` (always isolated; one --member per other unrecovered member); diagnose with `python tools/unit_diag.py --members A,B --entry ENTRY --new-members A,B --cache-key KEY`.
   Compiles are queued and batched across workers (a cache miss may wait minutes); cache hits are instant. Never loop on a failing tool.
5. Budget: at most 12 compiler trials and 4 variants per manifest. Stop at an exact EQUAL, at budget, or after three consecutive refuted predictions in one causal family without new evidence (switch family once, then report).
6. Write `experiments/fleet/unit-ov11_F_5962-5C42/result.json` exactly per the schema below using Python `json.dump` (UTF-8, no BOM; never an empty file), check it with `python tools/fleet.py intake unit-ov11_F_5962-5C42 --dry-run`, fix any REJECTED reason, then reply with one line: `TASK unit-ov11_F_5962-5C42 <STATUS> experiments/fleet/unit-ov11_F_5962-5C42/result.json`.

## result.json (closed schema; intake re-verifies every EQUAL claim)
```json
{"schema_version":1,"task_id":"unit-ov11_F_5962-5C42","worker":"<your -n name>",
 "status":"EQUAL_CANDIDATE|NEAR|BLOCKED|NEEDS_EVIDENCE",
 "target":"ov11_F_5962,ov11_F_5C42",
 "best":null or {"source":"experiments/fleet/unit-ov11_F_5962-5C42/<file>.c","profile":"aztec36","cache_key":"<64 hex>",
   "verdict":"EQUAL|DIFFER|BLOCKED","verifier":"check_unit","entry":"<evidence id of the member compiled as recovered(), e.g. ov11_F_5962,ov11_F_5C42>",
   "options":["separate_objects","allow_original_gaps","join_direct_callees","owned_code_data"],"expected_length":0,"actual_length":0},
 "hypotheses":[{"id":"h1","statement":"...","outcome":"confirmed|refuted|partial|unmeasurable|untested","evidence":"ledger line / report path"}],
 "compile_trials":0,"ledger_lines":[],
 "explanation":"what the evidence now shows (<=1200 chars)",
 "proposed_blocker":null or {"mechanism":"UPPER_SNAKE_CASE","text":"blocker text for docs/blockers.json curation"}}
```
EQUAL_CANDIDATE needs best.verdict EQUAL from an isolated run. NEAR needs best. BLOCKED needs proposed_blocker. NEEDS_EVIDENCE names the missing evidence in explanation. `entry` is required for check_unit and equals the target for check_function.
For check_unit with several new members, `best` may add `"members":{"<other member id>":"experiments/fleet/unit-ov11_F_5962-5C42/<file>.c"}` (the `--member` sources; never the entry).
