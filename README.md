# DuckTales Amiga historical reconstruction

This independent project follows [the vision](docs/VISION.md). The current
deliverable is a mechanical source-recovery pipeline with 111 verified C
functions (20,666 bytes), a recursive function census and a historical compiler
oracle. There is no
reconstructed game executable or completed source overlay yet.

The supplied originals in `assets/` are hash-locked verification fixtures.
They are never reconstructed build inputs. All analysis runs on Windows with
Python 3.10+; the topology parser uses the standard library, and recursive 68k
analysis uses the installed native Capstone. Historical compilation uses the
unattended WinUAE worker.

Start with [the grinder interface and proof boundaries](docs/grinder-pipeline.md):

```powershell
python tools/grinder.py rank --limit 12
python tools/grinder.py facts ov14_F_03AE
python tools/check_function.py ov14_F_03AE experiments/grinder-bootstrap/ov14_F_03AE.c
```

## Reproduce the evidence

From the project directory in PowerShell:

```powershell
python tools/census.py --check
python -m unittest discover -s tests -v
```

`--check` re-reads the locked disks, extracts files in memory, parses the full
executable, and compares every generated JSON document. It does not write.
Changes to supplied inputs, extracted identities, or generated evidence fail
with a nonzero status. JSON output contains no current timestamps or absolute
workstation paths.

```powershell
# Regenerate derived evidence after an intentional analysis-tool change:
python tools/census.py --write
# Optional local oracle files, excluded from source control:
python tools/census.py --write --extract
# Compare a future independently built candidate; retain each experiment:
python tools/compare.py build/candidate/DuckTales --report build/experiments/run-001.json
```

`--init-lock` is a one-time initialization command and refuses an existing lock.
No automatic relocking occurs. Extraction preserves original file bytes and
case under `build/fixtures/DT1` and `DT2`; Amiga attributes stay in the manifests.
Comparison reports distinguish content, relocation, layout, and whole-file
equality. They **never** promote a reconstruction proof level: even comparing
an oracle copy to itself cannot prove independently recovered source.

## Measured baseline

| Item | Result |
| --- | --- |
| Volumes | DT1 and DT2, OFS, 901,120 bytes each |
| Files | 27 on DT1, 12 on DT2 |
| Executable | `DT1:DuckTales`, 193,004 bytes |
| Resident | Hunk 0 CODE, 1 DATA, 2 BSS |
| Overlays | 13 CODE hunks, numbered 3–15 |
| Manx-style dispatch | 14 table slots, one empty; 26 trampolines |
| Relocations | 1,445 HUNK_RELOC32 sites |
| Symbols / debug | Neither record type present |
| Executable bytes parsed | 193,004; zero unparsed |
| Uninitialized allocation | 34,088 bytes in DATA hunk 1, plus 4-byte BSS hunk 2 |
| Pilot | ov07, 8,352 bytes, investment/stock-market semantic candidate |

The table's empty slot, 14 BREAK records, one-based dispatch IDs, and DATA
allocation tail are preserved. See [census findings](docs/census.md) for offsets
and [format scope](docs/formats.md) for validation boundaries.

## Evidence and next work

- [Fixture identities](evidence/fixture-lock.json), [filesystem](evidence/filesystem),
  [hunks](evidence/executable/hunks.json), [overlay model](evidence/executable/overlay-tree.json).
- [Progress](docs/progress.json), [module ownership](docs/modules.json),
  [blockers and failed experiments](docs/blockers.json), [toolchain provenance](docs/toolchain.json).
- [Pilot evidence](evidence/executable/pilot.json), [proof rules](docs/proof-levels.md),
  [research sources](docs/references.md).

The supplied Aztec 5.0a archive is now pinned. Three disks validate, providing
339 files including the compiler, assembler, linker and 17 libraries; disk 3
fails strict OFS validation and remains quarantined. No historical tools have
been selected as the unique historical release. Both 3.6a and 5.0a execute
unattended; 294 fingerprint trials are retained. The recovered functions match the
tested 3.6a profile, and 470 resident runtime bytes match candidate contributions.
The shared segload code does not distinguish releases. The earlier HTTP 465
failure is retained in the ledger.
See [Windows tools and archive findings](docs/windows-tools.md) for native
analysis/build options and the distinction between native execution and vamos.

```powershell
python tools/acquire_candidate.py --from toolchain/aztecc50a.zip
python tools/inventory_candidate.py --check
```

`src/resident` and `src/overlays/ov03` through `ov15` retain container identities;
their README files are placeholders, not reconstructed sources. The census is
an analysis pipeline, not the future normal build. No original code fallback,
patching, fixed function placement, or source-port implementation is present.

The unattended historical tool worker is operational; see [build-worker instructions](docs/build-worker.md) for repeatable commands and evidence.
