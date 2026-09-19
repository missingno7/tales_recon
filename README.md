# DuckTales Amiga historical reconstruction

This independent project follows [the vision](docs/VISION.md). The current
deliverable is a reproducible disk/HUNK/overlay evidence model. There is no
reconstructed game executable or completed source overlay yet.

The supplied originals in `assets/` are hash-locked verification fixtures.
They are never reconstructed build inputs. All analysis runs on Windows with
Python 3.10+ and the standard library; no emulator or third-party package is
needed for the census.

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

The next dependency is a pinned candidate Manx compiler/assembler/linker and
runtime distribution, followed by object-level runtime matching and compiler
fingerprinting. The museum's 5.0a download was identified but retrieval failed
with HTTP 465; no historical tools have been acquired or executed. The command
`python tools/acquire_candidate.py` can retry this explicit research acquisition
and pins any successful archive and every ZIP member by SHA-256.

`src/resident` and `src/overlays/ov03` through `ov15` retain container identities;
their README files are placeholders, not reconstructed sources. The census is
an analysis pipeline, not the future normal build. No original code fallback,
patching, fixed function placement, or source-port implementation is present.
