# Fleet task rev-unrecovered_local_dependency-ov08_F_1AB8 (review)

You are an autonomous worker on a historical Amiga 68k (Aztec C) reconstruction in `D:/Prog/tales_recon`. You have no memory beyond this prompt. Review UNRECOVERED_LOCAL_DEPENDENCY evidence for 1 ov08 functions

Priority 80. Lease: worker `luna-rev-unrecovered_local_dependency-ov08_F_1AB8`, expires 2026-09-29T03:53:10+00:00 (renew: `python tools/fleet.py renew rev-unrecovered_local_dependency-ov08_F_1AB8 --worker luna-rev-unrecovered_local_dependency-ov08_F_1AB8`).

## First step (host liveness)
Run `python tools/fleet.py renew rev-unrecovered_local_dependency-ov08_F_1AB8 --worker luna-rev-unrecovered_local_dependency-ov08_F_1AB8` before anything else. The host is shared and heavily loaded: a single command can take 1-3 minutes to start and finish. Run commands one at a time (never batch several commands in parallel), wait on slow commands instead of terminating them, and keep outputs small. Do not read whole docs/*.json ledgers or long docs; this packet already carries the binding rules and target facts, so use targeted queries. Only if this `renew` command itself has still not returned after 10 minutes, stop and reply with one line: `TASK rev-unrecovered_local_dependency-ov08_F_1AB8 BLOCKED HOST_TOOLS_UNRESPONSIVE` (no result.json needed; the supervisor releases the lease).

## Rules (binding; from AGENTS.md)
- Historical reconstruction, not a source port. `assets/` is immutable oracle evidence. Never relock fixtures and never feed original code bytes into reconstructed outputs (no byte arrays, inline asm, placement directives or copied data standing in for code).
- Keep natural object/hunk/overlay layout as the target. Numeric overlay names are containers; do not invent semantic names or source filenames. Printable runs are candidates, not string boundaries. Unknown ownership stays visible. Runtime ABI identification is not library provenance.
- Do not edit tools/, tests/, docs/, evidence/, recovery/, src/ or assets/, do not hand-edit generated ledgers, do not run `census.py --write`, `function_census.py` or `type_evidence.py --write`, and do not commit.
- Write files ONLY under `experiments/fleet/rev-unrecovered_local_dependency-ov08_F_1AB8/`. The tools themselves append to build/compile-cache and to the hypothesis ledger; that is expected.
- Never promote: never run check_function.py/check_unit.py without `--isolated`; use the wrappers below. Never delete lock files. If a tool reports a stale lock, stop and report BLOCKED quoting the message.
- The exact verifier alone decides EQUAL. Diagnostics and similarity scores are advisory. Other workers share this checkout; do not touch other experiments/ directories.

## Review task
Read-only evidence review of the members below. Do not compile unless one member becomes a concrete bounded source hypothesis (then use the function protocol, max 4 trials). Report NEEDS_EVIDENCE with the precise missing evidence per member, or BLOCKED with a mechanism.

## Origin
`{"constraint":"UNRECOVERED_LOCAL_DEPENDENCY","constraints":{"ov08_F_1AB8":["UNRECOVERED_LOCAL_DEPENDENCY","NONCONTIGUOUS_LOCAL_UNIT"]},"node":"ov08","source":"grinder_frontier"}`

## Members
- `{"calls":3,"confidence":"HIGH","constraints":["UNRECOVERED_LOCAL_DEPENDENCY","NONCONTIGUOUS_LOCAL_UNIT"],"data":6,"extent":"CLOSED_CFG","id":"ov08_F_1AB8","indirect":0,"node":"ov08","size":114,"start":"0x1AB8"}`

## Prior hypotheses (do not repeat)
`{"summary":{"predictions":{},"shown":0,"trials":0,"verdicts":{}},"trials":[]}`

## Protocol
1. Inspect evidence (read-only): `python tools/grinder.py facts ID` (full disassembly/CFG/relocations), `python tools/diag.py ID --cache-key KEY` for any cached key, `python tools/type_evidence.py --function ID`, `python tools/shape_search.py --ledger-summary ID`, docs/source-shape-search.md, docs/m68k-diagnostics.md.
2. BEFORE compiling, record each hypothesis with a machine-checkable prediction. Write a schema v2 manifest `experiments/fleet/rev-unrecovered_local_dependency-ov08_F_1AB8/manifest-NN.json` (docs/source-shape-search.md): every variant has parent, suspected_cause, controlled_change and predicted_effect {length_delta, removed_candidate_only, register_role_diffs, note}. Name a measured parent (an earlier variant, a compiled .c path, `ledger:N` or a 64-hex cache key); parent `none` leaves every prediction unmeasurable. Sources: `experiments/fleet/rev-unrecovered_local_dependency-ov08_F_1AB8/*.c` (self-contained K&R C defining `recovered(...)`, mechanical G_hNN_XXXX/F_hNN_XXXX externs).
3. Each variant makes ONE controlled change from its parent. Do not resubmit a hypothesis listed under prior hypotheses; the ledger rejects normalized duplicates and returns the earlier record, which you must read instead.
4. Compile via: `python tools/shape_search.py experiments/fleet/rev-unrecovered_local_dependency-ov08_F_1AB8/manifest-NN.json --output-dir experiments/fleet/rev-unrecovered_local_dependency-ov08_F_1AB8/runs --json` (isolated; records the ledger; add `--measure-parents` to compile an unmeasured parent as a counted trial). For owned CODE data or m.lib only: `python tools/fleet.py verify-function ID SRC --profile P [--owned-code-data] [--with-m-lib] --output-dir experiments/fleet/rev-unrecovered_local_dependency-ov08_F_1AB8/runs`.
   Compiles are queued and batched across workers (a cache miss may wait minutes); cache hits are instant. Never loop on a failing tool.
5. Budget: at most 4 compiler trials and 2 variants per manifest. Stop at an exact EQUAL, at budget, or after three consecutive refuted predictions in one causal family without new evidence (switch family once, then report).
6. Write `experiments/fleet/rev-unrecovered_local_dependency-ov08_F_1AB8/result.json` exactly per the schema below using Python `json.dump` (UTF-8, no BOM; never an empty file), check it with `python tools/fleet.py intake rev-unrecovered_local_dependency-ov08_F_1AB8 --dry-run`, fix any REJECTED reason, then reply with one line: `TASK rev-unrecovered_local_dependency-ov08_F_1AB8 <STATUS> experiments/fleet/rev-unrecovered_local_dependency-ov08_F_1AB8/result.json`.

## result.json (closed schema; intake re-verifies every EQUAL claim)
```json
{"schema_version":1,"task_id":"rev-unrecovered_local_dependency-ov08_F_1AB8","worker":"<your -n name>",
 "status":"EQUAL_CANDIDATE|NEAR|BLOCKED|NEEDS_EVIDENCE",
 "target":"ov08_F_1AB8",
 "best":null or {"source":"experiments/fleet/rev-unrecovered_local_dependency-ov08_F_1AB8/<file>.c","profile":"aztec36","cache_key":"<64 hex>",
   "verdict":"EQUAL|DIFFER|BLOCKED","verifier":"check_function","entry":"<evidence id of the member compiled as recovered(), e.g. ov08_F_1AB8>",
   "options":["owned_code_data","with_m_lib"],"expected_length":0,"actual_length":0},
 "hypotheses":[{"id":"h1","statement":"...","outcome":"confirmed|refuted|partial|unmeasurable|untested","evidence":"ledger line / report path"}],
 "compile_trials":0,"ledger_lines":[],
 "explanation":"what the evidence now shows (<=1200 chars)",
 "proposed_blocker":null or {"mechanism":"UPPER_SNAKE_CASE","text":"blocker text for docs/blockers.json curation"}}
```
EQUAL_CANDIDATE needs best.verdict EQUAL from an isolated run. NEAR needs best. BLOCKED needs proposed_blocker. NEEDS_EVIDENCE names the missing evidence in explanation. `entry` is required for check_unit and equals the target for check_function.
For check_unit with several new members, `best` may add `"members":{"<other member id>":"experiments/fleet/rev-unrecovered_local_dependency-ov08_F_1AB8/<file>.c"}` (the `--member` sources; never the entry).
If `best` was compiled with `--object-group`, add `"object_groups":[["<ID>","<ID>"]]` exactly as passed (intake re-verifies with them).
