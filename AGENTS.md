# Reconstruction constraints

Goal (user decision 2026-10-15): complete, readable source of the game whose
behavior we can trust, as the base for a later native SDL3 port. Exact matching
decompilation is the preferred recovery and verification technique, not the
deliverable. Do not modernize matched source.

SDL3 port (user decision 2026-10-18): the port lives in `port/`, as in the
user's other recon projects (duke1_recon): a thin layer that runs the
reconstructed game unchanged on an emulated Amiga over SDL3. `src/` stays the
recovered program; port behaviour goes into `port/` (platform code,
`port/override/` for the RECONSTRUCTED_ASM modules and anything that touches
hardware through raw pointers) and `tools/port_gen.py`, never into `src/`. A
port bug is traced from the lowest layer: replay the recorded platform inputs,
find the first wrong global, then check that one function against the original
68000 code (`tools/difftest.py`). Design: `docs/sdl3-port.md`.

Read `docs/NEXT.md`, `docs/VISION.md`, `docs/blockers.json` and
`docs/proof-levels.md` before extending the reconstruction. `assets/` is
immutable oracle evidence. Never relock fixtures automatically or feed original
code bytes into reconstructed outputs. Keep every proven natural
object/hunk/overlay result, but historical executable reproduction (link order,
padding, startup/runtime objects, whole-file identity) never blocks behavior
recovery.

Proof categories stay separate in every report: exact C, recovered ASM,
reconstructed ASM, behaviorally reconstructed (requires explicit evidence and
stated limits), unresolved. Never present behavioral equivalence as a match, and
never replace accepted source with an unverified rewrite.

DATA initializer policy (user decision 2026-10-14): measured initializer values
from the original DATA may be curated into reconstructed C as recovered-source
facts only under strict typing. Types and extents must come from recovered code's
accesses or other independent evidence. Pointer initializers must bind to
independently named targets. Each provider object is compiled and verified exactly,
relocations included. Never use opaque char/byte arrays, padding fillers or guessed
extents. Untyped spans stay RAW_ORACLE_DEBT. This never permits original CODE bytes.

Reconstructed assembly policy (user decision 2026-10-14): a span may be
reconstructed as Manx assembly source only with machine-checked non-C evidence,
re-derived per span: instruction, ABI or register use the pinned compilers
cannot emit, such as register/CCR calling conventions or A4 reused as a general
pointer. Use mnemonics, symbolic labels and named relocation targets only.
Never use dc.w/dc.l instruction encodings or opaque byte carriers for code; an
encoding the pinned `as` cannot select is a blocker. Assemble with the pinned
`as` and verify CODE, relocations and object structure exactly. Account it as
RECONSTRUCTED_ASM, separate from C and from provenance-backed RECOVERED_ASM;
it never claims original-source provenance. Tables inside such modules follow
the DATA initializer policy (typed, independently bounded). Code that is
compatible with C stays on the C route.

Numeric overlay directories reflect historical containers; source filenames
and semantic labels require explicit provenance. Printable runs are candidates,
not established string boundaries. Unknown ownership/classification must remain
visible. Runtime ABI identification is not exact library provenance.

`tools/census.py --write` regenerates measured baseline ledgers, including
`docs/modules.json`, `symbols.json`, `data-layout.json`, and `progress.json`.
When introducing recovered-source facts, extend the evidence model with separate
curated inputs first; do not hand-edit generated metrics or let generation erase
future reconstruction work. `docs/blockers.json` and `docs/toolchain.json` are
curated ledgers; retain failed experiments there.

For parser/evidence changes run `python tools/census.py --write`,
`python tools/census.py --check`, and the full two-phase regression suite:
`python -m pytest -n 16 --dist=loadscope -m "not regression_serial" tests`, then
`python -m pytest -m regression_serial tests`. The promotion gate
(`check_function.regression_receipt`) is tiered: it runs that full suite only
when `tools/` or `tests/` differ from the last full pass on this host
(`build/regression/full-pass.json`); otherwise it re-proves canonical state
(census, hybrid and type-evidence checks, a few minutes). `TALES_FULL_GATE=1`
forces the full suite. Every commit follows a full pass. Tool file hashes are
provenance only: generated evidence does not record them. No normal game
build exists yet. Do not describe the analysis pipeline as one.

# Current worker loop

Read `docs/NEXT.md` for the current priorities; `python tools/behavior.py`
reports behavior coverage from the ledgers. Canonical ownership
is `recovery/ledger.json`; accepted source is `src/`, backed by compact proofs
and the retained unit inputs they actually reference. Current blockers are
`docs/blockers.json`. Attempt history and generated candidates belong under
ignored `build/recovery/`; worker source belongs under `build/workers/NAME/`.

Workers are Codex sessions (gpt-6-luna xhigh for mechanical work, gpt-6.1-sol
for hard blockers), one target each, briefed directly by the supervisor. Read
`docs/COMPILER_LEARNINGS.md` (Aztec rules, patterns and dead ends) before writing
C. Use `python tools/grinder.py facts TARGET` and `python tools/declaration_views.py
--function TARGET --block` for context, then write a candidate,
run lightweight diagnostics, and use `check_function.py TARGET SOURCE --isolated
--no-promote --profile aztec36` for exact verification. Promote the unchanged
candidate with `check_function.py TARGET SOURCE --profile aztec36` only after
reviewing the exact result. Every proof class publishes through one CLI,
`python tools/promote.py CLASS MANIFEST [--verify-only]` (registry:
`tools/acceptance.py`); independent contributions share one batch manifest.

Compile dependencies as separate historical objects by default. An explicit
`--object-group` requires independent evidence of same-object membership; do
not infer it merely to silence declarations. Shared headers require positive
evidence; compatible declarations in unrelated TUs need not be identical.

Use `repo_paths.active_files` / `is_active_repo_path` for discovery and reject
quarantine in canonical inputs. `.ignore` excludes `to_delete/` and `build/`
from ordinary rg searches. Never override these exclusions for worker context.
Retire historical files by moving them to `to_delete/` with a manifest entry.
The user may manually delete reviewed quarantine contents.

Milestone self-check (before each commit): run `python tools/behavior.py` and
note what moved; keep the full regression suite near 7 minutes (profile it
with `--durations` before adding real-repo tests); tests assert invariants,
never progress snapshots (no pinned function ids or corpus counts that grow as
recovery advances); justify any new infrastructure
by the bytes or behavior it unlocks; say which requirement category (A/B/C,
docs/VISION.md) the work served; never run a gated promotion while a worker
can write under `tests/` or `tools/`. `docs/REUSE.md` records what transfers
to the next project.

Cost discipline (2026-10-17, after a DATA wave whose publication took 12 hours):
time a new validator, proof route or publisher once, cold, on the real
repository before scaling it; per-item cost that grows with the corpus is a
bug. Bound long commands with a timeout, and profile anything that exceeds
about 10 minutes instead of waiting on it. Read the code for repeated work
before re-running. A worker wave delivers one manifest list, published with one
`promote.py CLASS M1 M2 ...` call (resumable; already-published manifests are
skipped). Land tool changes in their own commit with one full gate so that
publications stay on the canonical tier. Prefer one typed provider per
storage-plan aggregate over one provider per cell. Tool hashes are provenance:
never make generated evidence fail because a tool's bytes changed; re-derive
instead (`function_census.py --check` runs in the full gate when an analysis
tool changed).

Emulator use (2026-10-17, after an NVIDIA driver crash while WinUAE ran with the
screens off): WinUAE runs headless (`headless=true`, `gfx_api=directdraw`, no GPU
rendering) for traces, boots and compile jobs, one instance at a time. Prefer
vamos for compiles (`tools/vamos_backend.py`; WinUAE only for float/math code).
Batch emulator work: one session answers a whole question (`game_boot.py` records
registers, symbolized stack and messages at the end of the same run); never
relaunch the emulator for a one-second probe.

Exact acceptance remains absolute. Diagnostics run per hypothesis; census,
canonical proof checks, hybrid accounting and regression tests run at promotion
or tooling boundaries. RAW_ORACLE_DEBT is accounting only and grants no proof.
Do not retry an unchanged failed hypothesis without a smallest next experiment
and a blocker category: SOURCE_SHAPE, DECLARATION_VIEW, OBJECT/TU_LAYOUT,
DATA_OWNERSHIP, CALL_BINDING, CFG/BOUNDARY, RUNTIME/LIBRARY or TOOLCHAIN.

Bounded waves assign one target per grinding worker from one canonical HEAD.
Keep a worker-local task card with HEAD, canonical ledger hash, extent, profile,
blocker category, trial budget and stagnation limit. The supervisor owns all
canonical writes and revalidates unchanged submissions against current inputs;
an old wave cannot publish a cached PASS after canonical dependencies change.
Use a worker-local `shape_search.py --ledger` for recorded hypotheses, or keep
compact trials using `shape_search.emitted_identity(report)`. Equal CODE hashes
do not establish equal objects or bindings. Stop at exactness, the assigned
budget, repeated emitted states, or a structural dependency. Escalation needs
a concrete question and smallest changed experiment, never an unchanged retry.
