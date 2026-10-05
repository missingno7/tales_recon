# DuckTales Amiga historical reconstruction

This workspace reconstructs the historical Amiga project using independently
compiled C/ASM and a strict, immutable executable oracle. It is not a source
port. No independent game build or complete reconstructed overlay exists yet.

Start with [AGENTS.md](AGENTS.md) and [the current handoff](docs/NEXT.md).
[The vision](docs/VISION.md) and [proof policy](docs/proof-levels.md) define
historical fidelity and natural linking requirements.

The active authorities are `src/` for reconstructed source,
`recovery/ledger.json` and its referenced proofs/unit inputs for ownership and
acceptance, `evidence/fixture-lock.json` for original input identity,
`docs/blockers.json` for current blockers, and `docs/toolchain.json` plus
`toolchain/` for pinned compiler assumptions. Generated measurements are in
`docs/progress.json`; [whole-image accounting](docs/ACCOUNTING.md) keeps every
unreconstructed byte explicitly visible as RAW_ORACLE_DEBT.

Use `tools/` and `tests/` for the active recovery mechanisms. Compact compiler
controls and open blocker observations live in `evidence/rules/` and
`evidence/blockers/`. Scratch, compiler caches and worker packets belong under
ignored `build/`. Retired material goes to `to_delete/`, outside all normal
search and validation; the user can delete it after review.

```powershell
python tools/grinder.py facts ov04_F_0536
python tools/census.py --check
python tools/hybrid_image.py --check
python -m unittest discover -s tests -v
```

The local immutable disks in `assets/` and installed historical tools are not
tracked. Analysis needs Python and native Capstone; historical compilation uses
the existing unattended WinUAE worker. See [worker setup](docs/build-worker.md).

[Consolidation status](docs/CONSOLIDATION.md) records the cleanup checkpoint,
its validation and remaining infrastructure gates.
