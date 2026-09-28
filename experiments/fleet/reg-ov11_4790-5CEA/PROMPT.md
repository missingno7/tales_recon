# Fleet task reg-ov11_4790-5CEA (region)

You are an autonomous worker on a historical Amiga 68k (Aztec C) reconstruction in `D:/Prog/tales_recon`. You have no memory beyond this prompt. Recover strongly connected region ov11 0x4790..0x5CEA (8 new members, 3010 bytes) as one natural unit

Priority 1. Lease: worker `luna-reg-ov11_4790-5CEA`, expires 2026-09-28T23:37:47+00:00 (renew: `python tools/fleet.py renew reg-ov11_4790-5CEA --worker luna-reg-ov11_4790-5CEA`).

## First step (host liveness)
Run `python tools/fleet.py renew reg-ov11_4790-5CEA --worker luna-reg-ov11_4790-5CEA` before anything else. The host is shared and heavily loaded: a single command can take 1-3 minutes to start and finish. Run commands one at a time (never batch several commands in parallel), wait on slow commands instead of terminating them, and keep outputs small. Do not read whole docs/*.json ledgers or long docs; this packet already carries the binding rules and target facts, so use targeted queries. Only if this `renew` command itself has still not returned after 10 minutes, stop and reply with one line: `TASK reg-ov11_4790-5CEA BLOCKED HOST_TOOLS_UNRESPONSIVE` (no result.json needed; the supervisor releases the lease).

## Rules (binding; from AGENTS.md)
- Historical reconstruction, not a source port. `assets/` is immutable oracle evidence. Never relock fixtures and never feed original code bytes into reconstructed outputs (no byte arrays, inline asm, placement directives or copied data standing in for code).
- Keep natural object/hunk/overlay layout as the target. Numeric overlay names are containers; do not invent semantic names or source filenames. Printable runs are candidates, not string boundaries. Unknown ownership stays visible. Runtime ABI identification is not library provenance.
- Do not edit tools/, tests/, docs/, evidence/, recovery/, src/ or assets/, do not hand-edit generated ledgers, do not run `census.py --write`, `function_census.py` or `type_evidence.py --write`, and do not commit.
- Write files ONLY under `experiments/fleet/reg-ov11_4790-5CEA/`. The tools themselves append to build/compile-cache and to the hypothesis ledger; that is expected.
- Never promote: never run check_function.py/check_unit.py without `--isolated`; use the wrappers below. Never delete lock files. If a tool reports a stale lock, stop and report BLOCKED quoting the message.
- The exact verifier alone decides EQUAL. Diagnostics and similarity scores are advisory. Other workers share this checkout; do not touch other experiments/ directories.

## Region protocol (staged; the whole region is the only acceptance unit)
Full member facts, candidates and edges are in `experiments/fleet/reg-ov11_4790-5CEA/task.json` (`task.origin.region`); read that file and `python tools/grinder.py facts ID` per member instead of asking for more context.
A. Stage sources: each variant is one directory `experiments/fleet/reg-ov11_4790-5CEA/vNN/` holding `<ID>.c` for EVERY new member (copy the best candidate listed below, else author it; later variants copy their parent directory and change one member). Each file is self-contained K&R C defining `recovered(...)`; calls to other members, including back to the entry, use mechanical `F_hNN_XXXX` names. The entry file is compiled as recovered(); every other new member is one `--member ID=SRC`. Canonical members are reused automatically; never copy their bytes or source into your files.
B. Baseline: compile the complete region once with the verify command below and run the diagnostics command on its receipt and cache key. It reports per-member states (`same_after_reference_identity`, `differs`, ...), unknown gaps and candidate-only bytes.
C. Improve members one at a time: pick the worst `differs` member, record a hypothesis for THAT member (`"member"` field, `"parent"` = parent variant directory), change only that member's file in a new variant directory, recompile the whole region, rerun unit_diag. A member already `same_after_reference_identity` is frozen unless a hypothesis names it.
D. Unknown gaps stay unknown: never fill them with bytes, padding, data or asm. With `--natural-interval` every canonical function of the interval is linked as well and must stay EQUAL. A BLOCKED verdict `GAP_DEPENDENT_ENCODING` or `TARGET_IN_UNLINKED_SPAN` (receipt `natural_interval.gap_crossings`) means the gap itself blocks equality: report NEEDS_EVIDENCE or BLOCKED naming the gap.
E. The region is EQUAL only if the complete object and every member are EQUAL. Report every non-entry source in best.members.

## Region
`{"bridges_not_linked":0,"canonical_bytes":2372,"edge_kinds":{"call":8,"layout_interval":12,"pending_dependency":8,"short_form_if_compacted":2},"entry":"ov11_F_487E","gap_bytes":44,"layout_intervals":[{"dependents":["ov11_F_5962","ov11_F_5C42"],"interval":"0x4790..0x5962","sources":["ov11_cycle_physical_layout_frontier","recovery_blocker:ov11_F_5962","recovery_blocker:ov11_F_5C42"]}],"linked_outside_interval":11,"new_bytes":3010,"options":["separate_objects","natural_interval"],"size":5466}`
(internal edges: `task.origin.region.internal_edges`)

## Members in address order (region interval 0x4790..0x5CEA)
- 0x4790 +238 canonical (reused): ov11_F_4790, ov11_F_4848
- 0x487E +336 NEW ov11_F_487E scc
- 0x49CE +1272 canonical (reused): ov11_F_49CE, ov11_F_49EA, ov11_F_4A92, ov11_F_4AA4, ov11_F_4B0C
- 0x4EC6 +420 NEW ov11_F_4EC6 scc
- 0x506A +302 canonical (reused): ov11_F_506A, ov11_F_519C
- 0x51C0 +824 NEW ov11_F_51C0 scc
- 0x54F8 +192 NEW ov11_F_54F8 scc; cand `experiments/fleet/fn-ov11_F_54F8/fieldgap-after-y.c` DIFFER 192/192 key 0dbb63338233; cand `recovery/candidates/ov11_F_54F8/342304823be389939054f977493078c1b80c051524a14e4c2318b1e2e3514dd8.c` DIFFER 192/192 key 450b1d5617e7; dirs experiments/fleet/fn-ov11_F_54F8
- 0x55B8 +642 NEW ov11_F_55B8 scc
- 0x583A +296 NEW ov11_F_583A scc; cand `experiments/fleet/fn-ov11_F_583A/near.c` DIFFER 298/296 key 1976729719a4; cand `recovery/candidates/ov11_F_583A/6deb288a087599485acb41063b8d54f77ef332212b1dad36d8ed49a8a9e06ef3.c` DIFFER 298/296 key 87ff5c50b04b; dirs experiments/fleet/fn-ov11_F_583A
- 0x5962 +132 NEW ov11_F_5962 scc; dirs experiments/fleet/unit-ov11_F_5962-5C42
- 0x59E6 +44 GAP UNKNOWN_NOT_ASSIGNED (stays unclaimed)
- 0x5A12 +560 canonical (reused): ov11_F_5A12, ov11_F_5A62, ov11_F_5AB0, ov11_F_5BC4, ov11_F_5C1A
- 0x5C42 +168 NEW ov11_F_5C42 scc; dirs experiments/fleet/unit-ov11_F_5962-5C42

## Commands
- verify (isolated, queued): `python tools/fleet.py verify-region reg-ov11_4790-5CEA --sources experiments/fleet/reg-ov11_4790-5CEA/vNN` compiles `vNN/<ID>.c` for every new member: entry `ov11_F_487E` as recovered(), the others as `--member`, flags `--separate-objects --natural-interval 0x4790..0x5CEA`, output under `experiments/fleet/reg-ov11_4790-5CEA/runs` (explicit form: `commands.verify` in task.json). Add `--prepare-only` to see member order, spacing and gap crossings without compiling.
- per-member diagnostics: `python tools/unit_diag.py --receipt experiments/fleet/reg-ov11_4790-5CEA/runs/ov11_F_487E/aztec36-<KEY12>/receipt.json --cache-key KEY` (explicit `--members` form: `commands.diag`).
Promotion is the supervisor's `check_unit.py` with the same arguments; never run it yourself.

## Prior hypotheses (do not repeat)
`{"summary":{"predictions":{"confirmed":1},"shown":1,"trials":1,"verdicts":{"DIFFER":1}},"trials":[{"change":"Move the existing four-byte padding member from after the third field to between the second and third field...","fn":"ov11_F_54F8","line":1,"observed_len_delta":0,"prediction":"confirmed","profile":"aztec36","source":"experiments/fleet/fn-ov11_F_54F8/fieldgap-after-y.c","variant":"field-gap-after-y","verdict":"DIFFER"}]}`
Prior fleet outcomes: `[{"explanation":"The isolated aztec36 trial kept the 192-byte extent and 52-instruction shape. Moving the four-byte gap between y and first confirmed the predicted layout correction: the three conditional fields now address +34, +36, ...","line":2,"status":"NEEDS_EVIDENCE_FOR_CURATION","task":"fn-ov11_F_54F8"},{"explanation":"The retained best candidate is 298 bytes versus the 296-byte target. Its only remaining generated-call shape difference is at offset 0x104: candidate JSR through the A4 cal`

Note: check_unit --natural-interval 0x4790..0x5CEA links every function of the interval in address order (canonical members from their canonical sources, as regression checks that must stay EQUAL) plus 11 canonical callees outside it. Unknown gaps stay unclaimed; a PC-relative reference crossing a gap or unlinked span whose displacement class could change BLOCKS the unit (GAP_DEPENDENT_ENCODING). `verify-region --prepare-only` shows the layout without compiling.

## Protocol
1. Inspect evidence (read-only): `python tools/grinder.py facts ID` (full disassembly/CFG/relocations), `python tools/diag.py ID --cache-key KEY` for any cached key, `python tools/type_evidence.py --function ID`, `python tools/shape_search.py --ledger-summary ID`, docs/source-shape-search.md, docs/m68k-diagnostics.md, docs/unit-diagnostics.md, docs/fleet.md (Regions).
2. BEFORE compiling, record each hypothesis with a machine-checkable prediction. Append one JSON line per hypothesis to `experiments/fleet/reg-ov11_4790-5CEA/hypotheses.jsonl`: {"id","parent","member","suspected_cause","controlled_change","prediction"} with a concrete per-member length/state prediction (for example `member ov11_F_54F8 becomes same_after_reference_identity`).
3. Each variant makes ONE controlled change from its parent. Do not resubmit a hypothesis listed under prior hypotheses; the ledger rejects normalized duplicates and returns the earlier record, which you must read instead.
4. Compile via: the verify command in the Commands section (always isolated; one --member per other new member, exactly the listed flags), then the per-member diagnostics command with the new cache key.
   Compiles are queued and batched across workers (a cache miss may wait minutes); cache hits are instant. Never loop on a failing tool.
5. Budget: at most 40 compiler trials and 4 variants per manifest. Stop at an exact EQUAL, at budget, or after three consecutive refuted predictions in one causal family without new evidence (switch family once, then report).
6. Write `experiments/fleet/reg-ov11_4790-5CEA/result.json` exactly per the schema below using Python `json.dump` (UTF-8, no BOM; never an empty file), check it with `python tools/fleet.py intake reg-ov11_4790-5CEA --dry-run`, fix any REJECTED reason, then reply with one line: `TASK reg-ov11_4790-5CEA <STATUS> experiments/fleet/reg-ov11_4790-5CEA/result.json`.

## result.json (closed schema; intake re-verifies every EQUAL claim)
```json
{"schema_version":1,"task_id":"reg-ov11_4790-5CEA","worker":"<your -n name>",
 "status":"EQUAL_CANDIDATE|NEAR|BLOCKED|NEEDS_EVIDENCE",
 "target":"ov11_F_487E,ov11_F_4EC6,ov11_F_51C0,ov11_F_54F8,ov11_F_55B8,ov11_F_583A,ov11_F_5962,ov11_F_5C42",
 "best":null or {"source":"experiments/fleet/reg-ov11_4790-5CEA/<file>.c","profile":"aztec36","cache_key":"<64 hex>",
   "verdict":"EQUAL|DIFFER|BLOCKED","verifier":"check_unit","entry":"<evidence id of the member compiled as recovered(), e.g. ov11_F_487E>",
   "options":["separate_objects","natural_interval","join_direct_callees","owned_code_data"],"expected_length":0,"actual_length":0},
 "hypotheses":[{"id":"h1","statement":"...","outcome":"confirmed|refuted|partial|unmeasurable|untested","evidence":"ledger line / report path"}],
 "compile_trials":0,"ledger_lines":[],
 "explanation":"what the evidence now shows (<=1200 chars)",
 "proposed_blocker":null or {"mechanism":"UPPER_SNAKE_CASE","text":"blocker text for docs/blockers.json curation"}}
```
EQUAL_CANDIDATE needs best.verdict EQUAL from an isolated run. NEAR needs best. BLOCKED needs proposed_blocker. NEEDS_EVIDENCE names the missing evidence in explanation. `entry` is required for check_unit and equals the target for check_function.
For check_unit with several new members, `best` may add `"members":{"<other member id>":"experiments/fleet/reg-ov11_4790-5CEA/<file>.c"}` (the `--member` sources; never the entry).
