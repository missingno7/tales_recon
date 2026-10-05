# Historical reconstruction constraints

Read `docs/VISION.md`, `docs/progress.json`, `docs/blockers.json`, and
`docs/proof-levels.md` before extending the reconstruction. The current work is
historical reconstruction, not a source port. `assets/` is immutable oracle
evidence. Never relock fixtures automatically or feed original code bytes into
reconstructed outputs. Keep natural object/hunk/overlay layout as the target.

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
`python tools/census.py --check`, and `python -m unittest discover -s tests -v`.
No normal game build exists yet. Do not describe the analysis pipeline as one.

# Current worker loop

Read `docs/NEXT.md` for the current campaign and open gates. Canonical ownership
is `recovery/ledger.json`; accepted source is `src/`, backed by compact proofs
and the retained unit inputs they actually reference. Current blockers are
`docs/blockers.json`. Attempt history and generated candidates belong under
ignored `build/recovery/`; worker source belongs under `build/workers/NAME/`.

Use `python tools/grinder.py facts TARGET` for context, then write a candidate,
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
