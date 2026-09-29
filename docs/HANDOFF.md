# Handoff — 2026-09-29

Session range: `739a7ff..HEAD` (51 commits). This note summarizes state, the
fleet workflow that now works, measured results, and the prioritized open
items. Canonical facts still live in the generated ledgers
(`docs/progress.json`, `recovery/ledger.json`) and curated ledgers
(`docs/blockers.json`, `docs/toolchain.json`); this file is a pointer, not a
source of truth.

## Where things stand

| Measure | Session start | Now |
| --- | ---: | ---: |
| Canonical recovered functions | 115 | 149 |
| Verified source bytes | 22,242 | 38,604 |
| Test suite | 226 | 367 (1 skip) |

Remaining candidate-function bytes (census extents; overlaps with ownership
work are not resolved by this table):

| Area | Closed CFG | Uncertain extent |
| --- | ---: | ---: |
| Overlays | 47,186 B / 32 fns | 45,870 B / 16 fns |
| Resident | 13,674 B / 71 fns | 11,020 B / 384 fns |

Resident code is untouched (deferred). ~37 KB of the executable lies outside
candidate functions (DATA hunks, runtime, unreached ranges). Matched code is
function/unit proof only; no overlay- or game-level build exists.

Hypothesis ledger (`python tools/shape_search.py --ledger-summary`): 240
recorded compiler trials, 20 exact matches recorded through the ledger
(0.083 per trial), predictions 100 confirmed / 7 partial / 35 refuted /
81 unmeasurable. Several promotions came through check_unit runs that are not
counted as ledger trials, so the true yield per compile is somewhat higher.

## What was built this session

All advisory tooling leaves exact acceptance to `check_function` /
`check_unit`. Each item has its own doc section.

- **Controlled hypotheses** — `shape_search.py` schema v2 (parent, suspected
  cause, one controlled change, scored predicted effect), append-only
  `evidence/experiments/hypothesis-ledger.jsonl` with race-safe duplicate
  rejection. See [source-shape-search.md](source-shape-search.md).
- **Diagnostics** — `diag.py`: register first-divergence trace, reference
  identity resolver that consumes only proven bindings (splits source-shape
  from binding problems), unit-member bounding inside prepared units, and
  independent code/data boundaries for jump tables and owned literal pools.
  `unit_diag.py`: whole-unit per-member diagnostics; unknown gaps stay
  unknown. See [m68k-diagnostics.md](m68k-diagnostics.md),
  [unit-diagnostics.md](unit-diagnostics.md).
- **Verifier extensions (opt-in, strict)** in `check_unit.py`:
  `--member ID=SRC` (multi-new-member and cyclic units),
  `--natural-interval START..END` (links every canonical interval member in
  address order; gap-crossing calls must be encoding-independent),
  `--object-group ID,ID` (same-object/translation-unit *hypothesis*, never
  provenance), `--per-member-profiles` (canonical members use the profile of
  their own proof; only link-compatible pairs, see `tools/profile_compat.py`).
  Proven canonical groupings are preserved; duplicate harness stand-ins are
  merged; `recovery_evidence.py` re-derives every new receipt form at
  promotion. See [proof-levels.md](proof-levels.md), [fleet.md](fleet.md).
- **Toolchain fix** — the guest AmigaDOS shell silently rejects commands with
  more than 510 characters of arguments (status 10, empty log). Long links now
  use `ln -f FILE` via `tools/link_line.py`; short commands are byte-identical.
  Evidence in `docs/toolchain.json` (`link_command_line_limit`).
- **Fleet** — `tools/fleet.py` (+ `compile_queue.py`, `file_lock.py`,
  `fleet_regions.py`, `declaration_views.py`): planner with unlock-aware
  priorities and region detection, leased claims, self-contained packets
  (rules, facts, prior hypotheses, canonical declaration views), coalescing
  compile queue, re-verifying intake that never promotes, host guard.
  `grinder.py facts` gained `--max-instructions` / `--max-bytes` for large
  targets. See [fleet.md](fleet.md).

## Supervisor loop that works

1. `python tools/fleet.py plan --max-bytes 4096`
2. Check host load: `python ~/.codex-dashboard/cx.py ps`. Other projects'
   fleets share the machine; above ~30 total Codex workers, tales workers'
   shell commands take 30–80 s and batch launches stall. Launch **staggered**
   (2 min apart), set `TALES_FLEET_HOST_MAX` deliberately.
3. `python tools/fleet.py launch-plan N [--kind function|region|review]`
   prints cx commands; or `fleet.py claim --task T` + `fleet.py packet T` for
   hand-picked tasks. Run each cx as its own background job.
4. When a worker finishes: `python tools/fleet.py intake T`. For
   `CONFIRMED_EQUAL`, **read the source** (no asm, byte arrays, placement
   tricks; mechanical names only), then run the printed promote command,
   `python tools/type_evidence.py --write`, `python tools/census.py --write`,
   `--check`, and the unittest suite — check the real result line, not a
   piped `tail` exit status.
5. Near misses: resume the same Codex session (`cx run --resume <session>`)
   with a follow-up naming the new budget and the concrete next hypothesis.
   Split stubborn multi-member regions into per-member workers that each
   change only their member against a frozen variant, then merge.

Pinned tests that encode frontier counts (e.g.
`tests/test_cycle_layout_gap_audit.py`) legitimately change when a
promotion covers their interval; update them with the promotion.

## Recurring technical lessons

- A short `BSR.B` in the original where the candidate emits `JSR d16(PC)`
  means the callee must be in the same object: try `--object-group`
  (583A/5962) or the natural interval (407C in the 37E4 proof).
- A unit size delta with a shape-exact target usually means a canonical
  member was linked differently: proven grouping (25D6/25F8), or a helper
  proven under another profile (`--per-member-profiles`, 6CFE).
- Workers stall on missing facts, not on source: raise facts budgets before
  concluding NEEDS_EVIDENCE.
- Two partial variants (one with correct structure, one with correct
  references) merged cleanly for ov11_F_51C0.

## Open items, prioritized

1. **ov11_F_2EEA** (1,608 B, `experiments/fleet/fn-ov11_F_2EEA`, best v14):
   every instruction aligned; 10 A4 references remain (1 different identity,
   9 unresolved). Binding/extern-view work, not source shape. Unblocks
   ov11_F_2272.
2. **ov11_F_2272** (386 B, NEAR, `experiments/fleet/fn-ov11_F_2272`): only difference is the late call to 2430
   (original BSR.B). Test `--object-group ov11_F_2272,ov11_F_23F4,ov11_F_2430`
   once 2EEA is canonical (check_unit refuses the unit while 2EEA is
   unrecovered).
3. **Conflicting declarations in prepared units** — ov10_F_2634 failed to
   compile because two canonical dependency sources declare different
   `struct Flags` bodies and check_function concatenates them. Either compile
   dependencies as separate objects in that path or consolidate views.
   Declaration conflicts grew from 55 to 250
   (`python tools/declaration_views.py --clusters`).
4. **ov05_F_2CD4** (1,050 B, NEAR): exact length; A4 displacement of
   G_h01_5E66 and 7–8 instructions around a register geometry call differ —
   needs natural hunk-1 DATA placement evidence and a register-call view.
5. **FFP helper binding** (GRINDER-PROOF-001): ov11_F_5FB2 (206 B) and
   ov05_F_3836 (616 B) are shape-exact; only private Aztec FFP helper call
   identities are unbound. An AJ per-site fixup grammar / linked binding proof
   would unlock 822 B.
6. **Readability debt** (spawned as a separate suggested task): goto-shaped
   sources (ov11_F_3532, 0BB6, 063A, ov04_F_0B50), byte-offset casts
   (ov11_F_2E26 — a named-field variant compiles identically), the first-word
   long-argument read in ov11_F_247C. Rewrite only when re-verification stays
   EQUAL.
7. **Measurement gap**: region/unit variants are mostly "unmeasurable" in the
   ledger scorer; score per member from unit_diag.
8. **Frontier widening**: remaining function tasks are mostly waiting on
   dependencies; 16 uncertain-extent overlay functions (45 KB) need boundary
   work; resident code has not been started.

## Housekeeping

- `experiments/fleet/fn-ov11_F_2272/` retains both worker rounds, including
  the refused object-group attempts.
- Fleet leases and tasks live in ignored `build/fleet/`; durable outcomes are
  `fleet_intake` records in the hypothesis ledger.
- Memory note for future sessions: host contention guidance in the Claude
  project memory (`fleet-host-contention`).
