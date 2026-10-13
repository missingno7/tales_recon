# Supervised fleet (Opus supervisor, Haiku workers)

Operational guide for running mechanical recovery waves. The canonical
authorities are unchanged: `recovery/ledger.json` owns accepted source,
`docs/blockers.json` owns blockers, and the exact verifier alone decides
equality. Everything under `build/fleet/` and `build/workers/` is derived,
ignored coordination state.

Roles:

- **Opus supervisor** (the interactive session): plans waves, dispatches
  workers with the Agent tool, takes in results, promotes, curates blockers
  and works on one shared structural blocker while workers run.
- **Haiku workers** (`model: haiku` subagents): one task each, autonomous,
  writing only in `build/workers/<task>/`. They compile only through the
  isolated wrappers and never promote, commit or edit canonical files.
- **Compile queue** (`tools/compile_queue.py`): cache hits return at once;
  misses are coalesced into one emulator boot per batch. Workers never start
  their own emulator.

## 1. Inspect the frontier

```powershell
python tools/fleet.py plan --max-bytes 2048
python tools/fleet.py wave 6 --dry-run
python tools/fleet.py status
```

`plan` regenerates `build/fleet/tasks.json` from the canonical ledgers. Each
task carries an advisory `route`:

| Route | Meaning | Who |
|---|---|---|
| `READY_FOR_HAIKU` | closed, independently verifiable function | Haiku |
| `READY_FOR_REGION_WORK` | unit/region whose members are proved together | Haiku with region packet, or Opus first |
| `BLOCKED_BY_SHARED_MECHANISM` | ABI/codegen/call-binding blocker shared by targets | Opus |
| `NEEDS_STRUCTURAL_EVIDENCE` | review chunks, deferred regions, uncertain extents, resident runtime tail | Opus |
| `ALREADY_EXHAUSTED` | prior intake was BLOCKED/rejected for the same task kind | nobody until new evidence |

Claim order is `priority`, then `leverage`, then id. Priority already includes
the dependency boost (a task whose recovery lets a waiting caller compile).
`leverage` is the summed `unlock_value` from `grinder.py rank`:
400 per unrecovered same-hunk PC-relative caller (a real verification
dependency) plus 100 per unrecovered A4-stub caller (interface evidence only:
stub callers already verify independently).

### Resident eligibility

Resident functions are ordinary candidates when `recovery_state.resident_deferral`
returns `None`:

- start below the first resident `RUNTIME_CANDIDATE` (0x75D8 today). Library
  objects link after the game objects, so the tail (startup, CLI/Workbench,
  exit, library leaves) keeps its specialised mixed/runtime route
  (`RESIDENT_RUNTIME_TAIL`);
- a single measured data model. `data_model` ignores A4 slots at jump-stub
  call sites (jump-table entries, not data). `ABSOLUTE` (RELOC32 into DATA)
  hints `aztec36-large-data`; `A4` hints `aztec36`. `MIXED` is deferred
  (`RESIDENT_MIXED_DATA_MODEL`);
- all ordinary limits still apply (closed CFG, no unresolved indirect flow,
  no PC-relative data, size and dependency limits).

Profile hints are advice; the verifier decides.

## 2. Dispatch a wave

```powershell
python tools/fleet.py wave 4                 # or: wave 1 --task fn-resident_F_463E
```

This leases up to N open tasks of the requested routes (default
`READY_FOR_HAIKU`), writes `build/workers/<task>/PROMPT.md` plus `task.json`,
and records `build/fleet/waves/<wave_id>.json`. It refuses a `tasks.json` that
predates the current recovery ledger. It launches nothing.

For each entry, call the Agent tool with the entry's `agent` fields verbatim
(`subagent_type`, `model`, `run_in_background`, `description`, `prompt`). The
prompt only points at `PROMPT.md`; the packet is the whole contract (rules,
facts, budget, manifests, verify commands, result schema). Supervisor-only
context (for example a measured prior probe) may be appended to the prompt;
copy any referenced file into the task directory first.

Start with 4 workers. Raise toward 6 only while `fleet.py status` shows the
compile queue draining (no long `pending_trials` backlog) and intake keeps up.

## 3. What a worker does

1. `renew` its lease, write `facts-ID.json` with the larger fact budget.
2. Record a schema v2 manifest (one controlled change per variant, measured
   parent, machine-checkable prediction), run `shape_search.py`.
3. Read the diff, change one factor, repeat. Stop at EQUAL, the trial budget,
   repeated emitted states, or three refuted predictions in one family.
4. Write `result.json`, self-check with `fleet.py intake TASK --dry-run`,
   reply `TASK <id> <STATUS> <path>`.

A first DIFFER, a large function or an ugly residual are not escalation
reasons. Escalate (status BLOCKED with `proposed_blocker`) only for a named
mechanism: compiler/ABI inconsistency, linkage that blocks a plausibly exact
shape, emitted-state collapse across serious variants, a structural
dependency, or contradictory evidence.

## 4. Intake and promotion (supervisor only)

```powershell
python tools/fleet.py intake-all             # re-verifies every EQUAL claim in isolation
```

Intake never trusts a worker verdict. `CONFIRMED_EQUAL` records carry a
`promote_command`. Review the source for historical plausibility (no invented
semantics, ownership or filler), then promote the unchanged candidate:

```powershell
python tools/check_function.py ID build/workers/<task>/<file>.c --profile P   # single
python tools/promote_batch.py MANIFEST --verify-only; python tools/promote_batch.py MANIFEST
```

Immediately after every published batch (or non-isolated check_unit /
check_function promotion), and before the next one, run
`python tools/boundary_refresh.py`. It performs, in order and stopping at the
first failure:

```powershell
python tools/type_evidence.py --write
python tools/hybrid_image.py --refresh --write
python tools/census.py --write
python tools/census.py --check
python tools/hybrid_image.py --check
```

After a CFG/parser change, start with `python tools/function_census.py`,
confirm no canonical extent changed, then run the same sequence (rerun
`type_evidence.py --write` if a test still reports a stale instruction index).

The promotion gate's regression suite requires current type evidence and
hybrid specimens that name exactly the canonical sources, so a batch on
stale derived evidence is refused (transactionally, nothing is written).
Run these as separate commands and confirm both `--check` results; a
refresh chained inside one long background command once silently did not
run. Do not edit tools/, tests/, evidence/, src/, recovery/ or docs/blockers.json
while a gate runs; its input snapshot must not change. Then `fleet.py plan` again:
newly canonical callees release waiting callers.

Same-object evidence: an original `bsr` between a new function and a
canonical one proved standalone admits them into one `--object-group`
(check_unit, `--separate-objects`; the census consumer re-derives the `bsr`
from function evidence). Members of a recorded multi-member object still
never join a different group, and every member must stay EQUAL. This closed
ov07_F_1F6E, ov05_F_467E and ov08_F_1AB8; promote such units with the same
non-isolated check_unit command.

Replacing a canonical source (for example a goto-free rewrite) uses
`check_function`/`check_unit ... --replace-canonical` with the same unit
options. It is one transaction (`tools/canonical_replacement.py`): every
canonical receipt that pinned the old source hash is re-proved from its own
unchanged source against the replacement, or nothing changes. Dependents
proved in grouped or multi-member units refuse; re-prove them explicitly.
`promote_batch` refuses replacements that would stale a receipt.

Supervisor review before promotion (the verifier proves bytes, not history):

- No filler locals or arrays (`pad`, `filler`, `unused[N]`) placed only to
  move frame or data offsets. An unused local is acceptable when a historical
  explanation exists (for example a copied sibling's leftover variables) and
  it has a neutral name; re-verify the renamed source and promote that file.
- Prefer structured C. A `goto` stays only when the structured form was
  measured to emit different bytes (record that measurement).
- Struct tags are candidate views; field names must not invent semantics the
  evidence does not show.
- Historical expressions that are undefined in modern C (for example
  `r = (r < t) ? ++r : --r`) are kept exactly; note them for the port.

`BLOCKED`/`NEEDS_EVIDENCE` intakes are curation inputs for
`docs/blockers.json`; the next plan routes those targets `ALREADY_EXHAUSTED`
until a changed hypothesis or new evidence reopens them (`fleet.py reopen`).

## 5. Shared blockers

When two or more independent workers report the same mechanism, stop
dispatching that family. Opus designs the smallest discriminating
experiment, records it in `docs/blockers.json` (category and next experiment),
encodes any confirmed rule in tools/tests, then re-plans so the mechanical
remainder returns to Haiku.

Before parking a near-miss as a shared blocker, re-measure its best source
against today's verifier. On 2026-10-12 the Luna-era report for
`ov11_F_2EEA` ("A4 layout, nine unresolved references") was stale: the
current relocation proof showed one wrong global name and two if/else join
shapes, and the function became exact in two trials. Luna-era task results
and sources survive in git (`git show 53e747b^:experiments/fleet/<task>/...`);
their hypothesis-ledger records were retired at consolidation, but
`build/fleet/state.json` keeps their outcomes, and the planner routes those
tasks from them.

## 6. Resume an interrupted wave

`fleet.py status` lists live leases and orphan leases. A worker that died
leaves its lease to expire (6 h) or `fleet.py release TASK --force`. Its
directory, manifests and the shared hypothesis ledger
(`build/recovery/hypotheses.jsonl`) persist, so a new worker on the same task
sees prior trials as "do not repeat". Run `intake-all` first to collect any
result already written.

## 7. Measure

Per wave, record in the wave summary: new canonical functions and C bytes
(`docs/progress.json` after `census --write`), unique compiler trials
(`shape_search.py --ledger-summary ID`), cache hits, intakes by status, and
accepted bytes per 100 unique trials. A candidate count, similarity score or
cached exploratory EQUAL is not progress until promotion passes.

Legacy: `fleet.py launch-plan` still prints `cx` commands for the retired
Codex/Luna workers; it is not used by the Claude loop.
