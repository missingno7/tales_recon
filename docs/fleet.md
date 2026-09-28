# Parallel worker fleet

`tools/fleet.py` coordinates many autonomous workers that share this checkout.
The supervisor plans, launches and reviews. Workers get one self-contained
prompt each. Nothing in the fleet launches processes, promotes proofs, relocks
fixtures or writes curated/generated ledgers. It is experiment coordination,
not a game build.

```powershell
python tools/fleet.py plan                      # build/fleet/tasks.json from the current frontier
python tools/fleet.py regions                   # strongly connected regions of the frontier (writes nothing)
python tools/fleet.py status                    # task states, leases, compile queue
python tools/fleet.py launch-plan 6             # claim 6 tasks, write packets, print cx commands
python tools/fleet.py claim --worker NAME [--kind function|unit|region|review|blocker-probe] [--task ID]
python tools/fleet.py verify-region TASK --sources DIR [--print]   # isolated whole-region check_unit
python tools/fleet.py packet TASK               # experiments/fleet/TASK/PROMPT.md
python tools/fleet.py renew|release|complete|reopen TASK ...
python tools/fleet.py intake TASK [--verify-near] [--dry-run]
python tools/fleet.py intake-all [--verify-near] [--dry-run]
```

`launch-plan` prints lines like
`python ~/.codex-dashboard/cx.py run -n luna-fn-ov11_F_583A -C D:/Prog/tales_recon -m gpt-6-luna -e xhigh < experiments/fleet/fn-ov11_F_583A/PROMPT.md`,
then PowerShell equivalents. Windows PowerShell 5.1 has no `<`, pipes text to
native programs in `$OutputEncoding` (BOM or ASCII by default) and does not
expand `~` in native arguments, so the variant first sets BOM-less UTF-8 once
per session and uses `Get-Content -Raw -Encoding UTF8 PROMPT.md | python
$HOME/.codex-dashboard/cx.py run ...`. cx reads the prompt from stdin as UTF-8;
the pipe was checked byte-for-byte in a `-NoProfile` 5.1 session (PowerShell
appends one trailing CRLF). The supervisor runs the commands.

Host guard: before claiming, `launch-plan` counts running workers with
`cx.py ps` (one line per worker, project column) and launches at most
`min(N, TALES_FLEET_HOST_MAX - running host-wide, TALES_FLEET_MAX - running here)`
(defaults 20 and 6), printing each cap as a `# host guard:` line. With ~25
workers from other projects, extra workers only stalled ("exec_command never
returned"). If cx is missing, the host-wide count is skipped and live leases
stand in for the repository count. If `cx ps` fails or times out, nothing is
launched; `--no-host-guard` skips the check.

## Tasks

`plan` reads the function census, `recovery/ledger.json`, the ranked frontier,
`recovery_plan` packages and the hypothesis ledger. Task ids are stable per
target: `fn-<id>`, `blk-<id>`, `reg-<node>_<start>-<end>`, `unit-<first>-<hex>...`,
`rev-<constraint>-<first>`. Outside regions, a function target appears in at
most one task. Canonical exact recoveries never become targets, and a task
whose targets become canonical later is `obsolete`.

| Kind | Source | Priority |
| --- | --- | --- |
| region | strongly connected regions (below); all new members of one physical interval | 10 / 70 (deferred) |
| unit | complete same-hunk dependency SCC packages not covered by a region | 10 (hypothesis) / 30 (review) |
| function | retained attempts or ledger trials, not blocked | 15 (similarity >= 0.75) / 25 |
| blocker-probe | recovery blockers; ABI-profile blockers only with `--include-abi-blockers` | 20 |
| function | closed, high-confidence, non-resident, direct-flow leaves <= `--max-bytes` (1024) | 40 + size/128 |
| function | callers whose unrecovered local callees are all tasks (dependencies) | 55 + size/128 |
| review | remaining frontier by first constraint and node, chunks of 8, capped by `--max-review-tasks` | 80+ |

A dependency is satisfied only when the dependency task's targets are canonical
(`check_function` then builds the caller unit itself).

Unlocks: `plan` builds a blocking graph from the frontier's pending local
dependencies and from NEEDS_EVIDENCE/BLOCKED intake records that name a
function (evidence id or `F_hNN_XXXX`). Each task records `unlocks` (other
non-review task targets its recovery would unblock, including tasks waiting on
it) and `blocked_by`. An unblocked task gains `5 x min(unlocks, 4)` priority
points (`base_priority` keeps the original). A task that itself waits on an
unrecovered function is not boosted. Closed leaves that block others but have
no task (an excluded ABI-profile blocker) are listed under
`omitted.untasked_blocking_leaves`, not turned into tasks. A leaf in a
same-hunk cycle, like ov11_F_5962 (calls ov11_F_5C42, which calls it back),
has an unresolved callee of its own, so `check_function` cannot build it alone.
It belongs to a region task (below).

## Regions

Single-function tasks were sent to impossible targets: in ov11, 5C42's call to
4696 must stay a 4-byte `JSR d16(PC)`, which the recorded
CYCLIC_INTER_OBJECT_PC_CALL blocker ties to the whole physical interval
`0x4790..0x5962`. `tools/fleet_regions.py` (pure, read-only) computes strongly
connected components of the unrecovered same-hunk graph. Its edges are:

- `call`: a same-hunk PC-relative direct call between unrecovered functions;
- `pending_dependency`: the ranked frontier's pending local dependency;
- `layout_interval`: a DEPENDENCY_LAYOUT recovery blocker that names
  `0xAAAA..0xBBBB`. The blocked function needs every unrecovered candidate
  inside that interval;
- `short_form_if_compacted`: a long call form (`JSR d16(PC)`/`BSR.W`) whose
  original displacement is outside the BSR.B range but would fall inside it
  without the unrecovered bytes in between.

Intake explanations that only mention a function are not region edges. Each
component is widened to its physical interval. The interval grows to whole
function extents and to overlapping curated intervals, including the
`cycle_layout_gap_audit` report. Overlapping regions in one hunk are merged.
Every unrecovered function in the interval is a new member and every canonical
one is reused. Bytes covered by no function and no proven literal tail are
listed as `UNKNOWN_NOT_ASSIGNED` gaps and stay unclaimed.

A `region` task targets all new members. It records the ordered members, the
SCC and independent members, gaps, edges and external prerequisites. It also
records the up to three best candidate sources per new member (fleet intakes,
then retained recovery attempts, with verdicts and cache keys), prior task
directories, and the check_unit options. The options are
`--separate-objects --natural-interval START..END` with the region interval. A
new member's own function or blocker-probe task is kept, but it
is marked `blocked_by_region` and is never claimable. The exception is an
*independent* member: it lies inside the interval but has no unrecovered
prerequisite, so its task stays open. A region waits on the tasks of
prerequisites outside it and counts `member_tasks_blocked`. A region is
deferred to priority 70 if it is oversized (more than 12 new members), resident,
or has a member of uncertain extent.

The region packet (at most 12 KB) references `task.json` for full facts. Its
protocol is staged. Each variant is a directory `vNN/` with one `<ID>.c` per
new member. Stage the best candidates first, then compile the whole region
with `fleet.py verify-region TASK --sources DIR`. That command runs an isolated
check_unit: the first unrecovered member is the entry and the rest are passed
as `--member`. `verify-region --prepare-only` prints the planned member order,
object offsets, spans, gap crossings and trial cache keys without compiling.
Next, run `unit_diag.py --receipt` for per-member states. Then
change one member per variant, and record a hypothesis naming that member
before each compile. The budget is 40 trials.

### Natural-interval verification

`--allow-original-gaps` links only the new members and their canonical call
closure. It leaves out canonical bridges that nothing calls, so the object is
compact, not the natural layout. Regions therefore use the opt-in
`check_unit.py --natural-interval START..END` mode:

- Every discovered function of the interval is linked in original address
  order. Canonical functions use their exact canonical sources, and new
  members use their candidate sources. Proven literal tails of canonical
  members are included as before. A function straddling a bound, a new member
  outside the interval, or an unrecovered interval function without a
  `--member` source is refused. Canonical callees outside the interval are
  linked in address order, as before.
- Acceptance is unchanged. Every linked byte comes from normal compiler and
  linker output of these sources, and every member must be EQUAL. Canonical
  members are regression checks and are listed in `canonical_regressions`.
- The receipt's `natural_interval` block lists each member's role, original
  extent and linked object offset. It also lists every *compaction span*:
  original bytes absent between two consecutive linked members. A span is an
  `UNKNOWN_GAP` (inside the interval, `UNKNOWN_NOT_ASSIGNED`) or
  `UNLINKED_OUTSIDE_INTERVAL`. No span byte is claimed, filled or copied.
- Each original PC-relative call or data reference that crosses a span is
  listed with its original displacement, compact displacement and distance
  delta. The rule is conservative. A crossing is `GAP_INDEPENDENT_ENCODING`
  only if both displacements fall in the same class: a nonzero 8-bit
  displacement (`BSR.B`), or a 16-bit one (`JSR d16(PC)`, `BSR.W`, `d16(PC)`
  data). Whatever rule chose the original form then sees the same class in
  both links, so the member comparison proves the reference by target
  identity. If the class changes, the crossing is `GAP_DEPENDENT_ENCODING`.
  A target inside a span is `TARGET_IN_UNLINKED_SPAN`. Either result makes
  the unit `BLOCKED` with that reason, even when every member compares EQUAL
  (the member verdict is kept as `member_verdict`).
- Across spans the mode requires `--separate-objects`. It cannot be combined
  with `--allow-original-gaps`. Without spans, one combined object is
  accepted: this is the ordinary contiguous unit, with the same cache key.
  Other option sets keep their exact trials and cache keys.
- With `--separate-objects`, canonical members that their own proof's
  complete-unit receipt shows in one ordinary source object stay in one
  object here (`natural_interval.proven_object_groups`). The partition comes
  from the receipt: no object partition means one object; otherwise the
  hash-checked compile-cache assembler output names each object's functions.
  A group applies only when every member is canonical, has its proved source
  hash, and is consecutive in this unit. Otherwise it is listed in
  `proven_object_groups_not_applied`. Example: ov11_F_25D6+25F8 or
  ov11_F_407C+40E0 keep their proved short local calls.
- Member objects keep their own `extern` declarations. The one link harness
  defines each external stand-in once. When objects declare one external
  differently (`void`/`int F_h00_3674()`), the first declaration defines the
  stand-in, and the receipt lists `merged_external_declarations`. Stand-ins
  are harness code, never claimed bytes. The prepare-only plan reports
  `duplicate_stand_in_definitions` for each trial. The oracle then compiled
  this stand-in text, not `unit.c`. The promotion evidence check
  (`recovery_evidence.compiled_unit_source_sha256`) re-derives it from the
  retained `unit.c`, plus the local functions and overlay proxies of the
  compile identity. It requires the receipt's merge list and the proof's
  compiler source hash to match.
- `--object-group ID,ID,...` (repeatable; `--separate-objects` only, not with
  `--join-direct-callees`) compiles the named members as one ordinary object.
  This is a translation-unit hypothesis tested like any variant. It is not
  source-file provenance. The members are taken in address order and must be
  consecutive linked members. No original byte may lie between them: a
  compaction span or an unknown gap cannot sit inside one object, and only a
  proven literal tail may. A group is all new members. A canonical member may
  join only if its whole proven object group lies inside the group. The object
  source is the address-ordered concatenation of the member parts
  (`recovery_evidence.group_object_source`). Externs of the group's own
  definitions are removed. Differing views of one external keep the first
  declaration, and the object lists them in `object_group_merged_declarations`.
  The receipt adds `object_groups`, `object_partition` and a `parts/`
  directory. The promotion evidence check
  (`recovery_evidence.object_partition_sources`) re-derives `unit.c` from the
  parts, and every object source hash from them. Without the option, trials and
  cache keys are unchanged. `fleet.py verify-region --object-group` passes
  the option through. A result's `best.object_groups` is re-verified and
  promoted with the same groups.

For intake, `natural_interval` is a region-only option. `reverify` and the
promote command take the interval from the region task.

On 2026-09-28 the frontier had 4 regions:

| Region | New members | New / canonical / gap bytes | Unlocks | Member tasks blocked | State |
| --- | --- | --- | --- | --- | --- |
| `reg-ov11_4790-5CEA` | 487E, 4EC6, 51C0, 54F8, 55B8, 583A, 5962, 5C42 | 3010 / 2372 / 44 | 7 | 8 | open, priority 1 |
| `reg-ov05_131C-1EFC` | 131C, 1860 | 3040 / 0 / 0 | 0 | 0 | deferred, waits on fn-ov05_F_3836 |
| `reg-resident_287C-2D00` | 287C, 291E | 1156 / 0 / 0 | 0 | 0 | deferred (resident) |
| `reg-resident_7BF4-7F9C` | 7BF4, 7C82 | 936 / 0 / 0 | 0 | 0 | deferred (resident) |

In ov11 region v10, 583A's only difference was its call to 5962. The original
has `BSR.B`; the separate-object candidate had `JSR d16(PC)`. With
`--object-group ov11_F_583A,ov11_F_5962` (build/object-group-reg-ov11, key
`f0d0039d…`), 583A emits `BSR.B` and both members are
`same_after_reference_identity`. The unit is still DIFFER, 7260 vs 7198 bytes,
from 487E, 4EC6, 51C0 and 55B8. A group reaching 5C42 is refused: the unknown
gap `0x59E6..0x5A12` follows 5962, and the canonical `5A12`..`5C1A` have no
proven object grouping.

The ov11 region's edges are 8 call, 8 pending-dependency, 12 layout-interval
and 2 short-form. Its gap is `0x59E6..0x5A12`. Under `--allow-original-gaps`
it linked 20 functions and left out 13 of its 14 canonical bridges. The
`--natural-interval 0x4790..0x5CEA` prepare-only dry run (stub sources, no
compile) links 33 objects. These are the 22 interval functions in address
order (8 new, 14 canonical, including `506A`'s 40-byte proven tail) and 11
canonical callees outside the interval (`2562`..`4696`, `645E`, `66FE`,
`6ED6`). The spans are the 44-byte unknown gap and four unlinked outside
spans (`0x262E..0x41F6`, `0x5CEA..0x645E`, `0x6486..0x66FE`,
`0x673E..0x6ED6`). `0x41F6..0x59E6` is linked at its natural spacing. All 12
crossing calls are 16-bit `JSR d16(PC)` and stay 16-bit when compacted, so all
are `GAP_INDEPENDENT_ENCODING`. Five cross only the unknown gap (distance change 44 bytes):
`5962`->`5C42`, `5C1A`->`4610`, `5C42`->`4696`, and `5C42`->`5962` twice.
`5C42`->`4696` is at -5650 in the original and -5606 when compacted. The other
seven also cross outside spans: from `487E`, `4B0C`, `51C0` (three),
`5962` and `645E`. Nothing is `GAP_DEPENDENT_ENCODING`.
The 7 tasks it unlocks are 13DC, 2E26, 3532, 5D14, 5EC0, 62B4 and 6CFE. A
`plan` then yields 56 tasks: 4 region, 25 function, 3 blocker-probe and 24
review. Six member tasks are `blocked_by_region`; the other two are already
completed.

## Leases and outcomes

`claim` runs under `build/fleet/state.lock` (owner-annotated `O_EXCL` file) and
leases the lowest-priority-number open task. A worker that already has a
live lease gets the same one back. Leases expire (default 6 h, `renew` extends)
and an expired task can be claimed again. Leases, tasks and history live in
ignored `build/fleet/`: they are per-checkout, regenerable coordination state
and would only add commit noise. Outcomes are durable. `intake` appends a
`fleet_intake` record to `evidence/experiments/hypothesis-ledger.jsonl`, which
makes the task `completed` even after `build/` is wiped. `reopen` allows the
task to be claimed again.

## Packets

`packet` writes `PROMPT.md` (target 10 KB, hard limit 12 KB) and `task.json`.
The prompt starts with a liveness step: run `fleet.py renew TASK --worker W`.
Commands can take minutes under shared host load, so packets tell workers to
run one command at a time and avoid reading whole ledgers. Only if `renew`
has not returned after 10 minutes does a worker stop and reply `TASK T BLOCKED
HOST_TOOLS_UNRESPONSIVE` without a result.json. The supervisor then runs
`fleet.py release T --force --note ...`, and the task is claimable again. The
prompt then holds the AGENTS.md rules and the target. It adds compact facts:
extent, calls, data, constraints, blocker text, the last verifier attempts with
cache keys and retained source paths, the cached `diag` or `unit_diag` summary
of the best attempt, a type-evidence slice, and prior ledger hypotheses and
fleet outcomes that must not be repeated. It also sets the protocol: record
hypotheses with predictions before compiling (schema v2 manifests for
functions, `hypotheses.jsonl` for units), one controlled change per variant,
budgets, and writing only under `experiments/fleet/<task>/`. It ends with the
closed `result.json` schema. Advisory sections are dropped first when the size
target is exceeded.

Workers compile only through isolated paths that use the compile queue:
`shape_search.py` and `fleet.py verify-function|verify-unit ARGS` (wrappers
that always add `--isolated`). A unit task names every unrecovered member. The
entry source is compiled as `recovered()`. Each other new member is passed as
`--member ID=SRC`; its file also defines `recovered()` and is renamed to
`F_hNN_XXXX`. Calls between members, including calls back to the entry, use
mechanical names. Remaining same-node callees must already be canonical.
The unit is EQUAL only when the complete object and every member are EQUAL,
so a mutual-call SCC can now reach EQUAL as a whole
(`fleet.py verify-unit ov11_F_5962 T/a.c --member ov11_F_5C42=T/b.c
--separate-objects --allow-original-gaps ...`). `unit_diag.py --new-members`
labels the authored members in per-member diagnostics.

## Intake

`intake` validates `result.json` against a closed schema. `best.source` must be
a `.c` file inside the task directory. `status` is one of `EQUAL_CANDIDATE`,
`NEAR`, `BLOCKED` or `NEEDS_EVIDENCE`. Intake never trusts a worker's verdict.
An EQUAL claim is re-run through the isolated verifier (`check_many` or
`check_unit.check`, `isolated=True`) and becomes `CONFIRMED_EQUAL` or
`EQUAL_CLAIM_REJECTED`. `--verify-near` also re-runs NEAR results. For a
confirmed result, intake prints the normal promoting command, for example
`python tools/check_function.py ID experiments/fleet/T/x.c --profile aztec36`.
A multi-member unit result adds `best.members` (`{id: source}` for the
non-entry members, task targets only). Intake re-verifies with those sources,
and the printed `check_unit` command repeats them as `--member` flags.
It does not run that command. BLOCKED and NEEDS_EVIDENCE results are printed
as a `blocker_curation` summary for manual editing of `docs/blockers.json`.
Intake never writes them there.

`intake-all` intakes every task directory with a `result.json` that has no
intake record yet. It groups the outcomes: `confirmed_equal` and
`unclaimed_equal` (with promote commands, never run), `near`, `needs_evidence`,
`blocked`, `rejected` (schema reason or failed re-verification),
`already_intaken`, and `changed_after_intake` (to intake one again, reopen it
first). Worker type-evidence reads (`type_evidence.py --function`, packets)
serve the last generated report with `stale: true` and the reasons after a
promotion changes its inputs. The Python API and `--check` stay strict.

## Compile concurrency

`compiler_oracle.compile_many` still fails fast when `build/compiler-oracle.lock`
exists. `tools/compile_queue.py` wraps it without changing that file. The
file's hash is part of proxy and named-entry cache identities. Behavior:

- Cache hits return at once and never touch any lock.
- Each cache-miss request is spooled in `build/compile-queue/requests/`. One
  process holds `build/compile-queue/leader.lock` and compiles its own misses
  plus every live spooled miss (up to 48 trials) in one oracle batch, so one
  WinUAE boot serves many workers. Waiters return when their keys are cached.
  `cache_hit` is false for keys compiled on their behalf.
- Waits are bounded by `TALES_COMPILE_WAIT_SECONDS` (default 1800). If a
  lock's owner pid is not running, or an unannotated lock is more than an hour
  old, the error reports it and names the file. The lock is never removed or
  taken over.

`install()` routes `check_function`/`check_unit` in the current process through
the queue. Direct `check_function.py`/`check_unit.py` runs keep the old
fail-fast behavior, which is fine for a supervisor's promoting run of an
already-cached candidate. Measured guest time from retained worker jobs:
a one-trial batch takes about 2.2-3.1 s (median about 2.5 s). A 36-step batch
(about 5 trials) takes 3.3 s, and a 480-step batch (about 80 trials) takes
11 s. The fixed boot cost dominates, so coalescing is the main gain.

`shape_search` now repeats its duplicate check under the ledger lock just
before compiling. It reserves each hypothesis in `build/hypothesis-inflight/`.
A process that meets an identical in-flight hypothesis waits, then records a
`duplicate_rejected` pointer instead of compiling it again.

## Limitations

- Pid liveness cannot detect pid reuse. Locks from another host report only by age.
- If one poisoned batch fails in the emulator, every request swept into it
  fails. Survivors retry as leaders, and each retry drops the failed leader's
  own request.
- Review tasks are evidence reviews and only rarely yield compiler work.
- The frontier is thin: most remaining functions have uncertain extents or
  unrecovered local dependencies.
