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
