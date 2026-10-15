# Reconstruction constraints

Goal (user decision 2026-10-15): complete, readable source of the game whose
behavior we can trust, as the base for a later native SDL3 port. Exact matching
decompilation is the preferred recovery and verification technique, not the
deliverable. We are in the recovery stages: do not modernize matched source and
do not add SDL3 code or dependencies here.

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
`python tools/census.py --check`, and the two-phase regression gate that
promotions use (`check_function.regression_receipt`): `python -m pytest -n 16
--dist=loadscope -m "not regression_serial" tests`, then `python -m pytest -m
regression_serial tests`. No normal game build exists yet. Do not describe the
analysis pipeline as one.

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
reviewing the exact result. Independent contributions can share the existing
`promote_batch.py MANIFEST --verify-only` / `promote_batch.py MANIFEST` boundary.

Compile dependencies as separate historical objects by default. An explicit
`--object-group` requires independent evidence of same-object membership; do
not infer it merely to silence declarations. Shared headers require positive
evidence; compatible declarations in unrelated TUs need not be identical.

Use `repo_paths.active_files` / `is_active_repo_path` for discovery and reject
quarantine in canonical inputs. `.ignore` excludes `to_delete/` and `build/`
from ordinary rg searches. Never override these exclusions for worker context.
Retire historical files by moving them to `to_delete/` with a manifest entry.
The user may manually delete reviewed quarantine contents.

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
