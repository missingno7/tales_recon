# Parallel worker fleet

`tools/fleet.py` coordinates many autonomous workers that share this checkout.
The supervisor plans, launches and reviews. Workers get one self-contained
prompt each. Nothing in the fleet launches processes, promotes proofs, relocks
fixtures or writes curated/generated ledgers. It is experiment coordination,
not a game build.

```powershell
python tools/fleet.py plan                      # build/fleet/tasks.json from the current frontier
python tools/fleet.py status                    # task states, leases, compile queue
python tools/fleet.py launch-plan 6             # claim 6 tasks, write packets, print cx commands
python tools/fleet.py claim --worker NAME [--kind function|unit|review|blocker-probe] [--task ID]
python tools/fleet.py packet TASK               # experiments/fleet/TASK/PROMPT.md
python tools/fleet.py renew|release|complete|reopen TASK ...
python tools/fleet.py intake TASK [--verify-near] [--dry-run]
```

`launch-plan` prints lines like
`python ~/.codex-dashboard/cx.py run -n luna-fn-ov11_F_583A -C D:/Prog/tales_recon -m gpt-6-luna -e xhigh < experiments/fleet/fn-ov11_F_583A/PROMPT.md`.
The supervisor runs them.

## Tasks

`plan` reads the function census, `recovery/ledger.json`, the ranked frontier,
`recovery_plan` packages and the hypothesis ledger. Task ids are stable per
target: `fn-<id>`, `blk-<id>`, `unit-<first>-<hex>...`, `rev-<constraint>-<first>`.
A function target appears in at most one task. Canonical exact recoveries never
become targets, and a task whose targets become canonical later is `obsolete`.

| Kind | Source | Priority |
| --- | --- | --- |
| unit | complete same-hunk dependency SCC packages | 10 (hypothesis) / 30 (review) |
| function | retained attempts or ledger trials, not blocked | 15 (similarity >= 0.75) / 25 |
| blocker-probe | recovery blockers; ABI-profile blockers only with `--include-abi-blockers` | 20 |
| function | closed, high-confidence, non-resident, direct-flow leaves <= `--max-bytes` (1024) | 40 + size/128 |
| function | callers whose unrecovered local callees are all tasks (dependencies) | 55 + size/128 |
| review | remaining frontier by first constraint and node, chunks of 8, capped by `--max-review-tasks` | 80+ |

A dependency is satisfied only when the dependency task's targets are canonical
(`check_function` then builds the caller unit itself). On 2026-09-28, `plan`
produced 53 tasks: 26 function (10 open, 16 waiting), 2 blocker-probe, 1 unit
and 24 review; 60 further review chunks were omitted by the cap.

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
The prompt holds the AGENTS.md rules and the target. It adds compact facts:
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
that always add `--isolated`). `check_unit` accepts one candidate whose other
same-node callees are canonical. Therefore a mutual-call SCC unit task can
report layout evidence, but it cannot reach EQUAL on its own.

## Intake

`intake` validates `result.json` against a closed schema. `best.source` must be
a `.c` file inside the task directory. `status` is one of `EQUAL_CANDIDATE`,
`NEAR`, `BLOCKED` or `NEEDS_EVIDENCE`. Intake never trusts a worker's verdict.
An EQUAL claim is re-run through the isolated verifier (`check_many` or
`check_unit.check`, `isolated=True`) and becomes `CONFIRMED_EQUAL` or
`EQUAL_CLAIM_REJECTED`. `--verify-near` also re-runs NEAR results. For a
confirmed result, intake prints the normal promoting command, for example
`python tools/check_function.py ID experiments/fleet/T/x.c --profile aztec36`.
It does not run that command. BLOCKED and NEEDS_EVIDENCE results are printed
as a `blocker_curation` summary for manual editing of `docs/blockers.json`.
Intake never writes them there.

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
