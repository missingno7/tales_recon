# DuckTales Amiga reconstruction

This workspace recovers the original Amiga DuckTales game as readable source
whose behavior we can trust, as the foundation for a later native SDL3 port.
Exact matching decompilation, verified against the immutable original
executable with the pinned Aztec C toolchain, is the preferred recovery and
verification technique. No independent game build exists yet.

Start with [AGENTS.md](AGENTS.md) and [the current state and priorities](docs/NEXT.md).
[The vision](docs/VISION.md) and [proof policy](docs/proof-levels.md) define the
goal and what each proof category claims.

The active authorities are:

- `src/` for reconstructed source;
- `recovery/ledger.json`, with its referenced proofs and unit inputs, for
  ownership and acceptance;
- `evidence/fixture-lock.json` for original input identity;
- `docs/blockers.json` for current blockers;
- `docs/toolchain.json` and `toolchain/` for pinned compiler assumptions.

Generated measurements are in `docs/progress.json`. [Whole-image
accounting](docs/ACCOUNTING.md) keeps every unreconstructed byte visible as
RAW_ORACLE_DEBT, and `tools/behavior.py` reports the same evidence by behavior:
what is exact, what is assembly or runtime library, what is unresolved, and
which platform services game code uses.

```powershell
python tools/behavior.py
python tools/readable.py      # readable view with reviewed names -> build/readable/
python tools/grinder.py facts ov04_F_0536
python tools/census.py --check
python tools/hybrid_image.py --check
python -m pytest -n 16 --dist=loadscope -m "not regression_serial" tests
python -m pytest -m regression_serial tests
```

The local immutable disks in `assets/` and installed historical tools are not
tracked. Analysis needs Python and native Capstone. Historical compilation uses
the existing unattended WinUAE worker (see [worker setup](docs/build-worker.md)).
Scratch, compiler caches and worker directories belong under ignored `build/`.
Canonical re-derivation reads `build/compile-cache` and `build/worker-jobs`, so do
not prune them. Retired material goes to `to_delete/` with a manifest entry.
