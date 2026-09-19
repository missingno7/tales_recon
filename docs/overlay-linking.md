# Natural overlay linking

The Aztec Amiga 3.6a linker produces the game's measured container shape from
independent C modules. It requires no fixed addresses, copied game code or
post-link patching. This is a working historical overlay build experiment, not a
reconstructed game build or a complete linked-layout match.

`+oN` selects the node for subsequent inputs; `+o0` resumes resident input.
Omitting node 4 while using nodes 1 through 14 leaves the fourth slot empty.
The tested command is recorded exactly in `experiments/overlay-topology/commands.json`.
`-m -t` produces a symbol map alongside the executable.

The option was identified directly in the pinned 3.6a linker's option parser:
CODE hunk 3 at offset 0x19f6 dispatches plus options; case 'o' reaches 0x18e2,
parses an explicit numeric ID or finds the next free ID, checks the 0..99 range,
and calls the node selector. These observations were hypotheses until verified
by independent linking and execution. No Amiga overlay syntax was inferred from
unrelated CP/M or DOS manuals.

## Reproduced shape

| Property | Game and independent probe |
| --- | --- |
| Hunk types | Resident CODE/DATA/BSS, then 13 CODE overlays |
| Overlay slots | 14, with slot 4 empty |
| Per-slot exported entries | 2, 10, 1, 0, 1, 2, 1, 1, 1, 1, 1, 2, 2, 1 |
| Total exported entries | 26 |
| HUNK_BREAK records | 14 |
| Overlay table upper-bound field | 54 (55 longwords, 220 bytes) |

The 4,160-byte test executable calls every exported entry, checks its result,
and calls an entry in the first overlay again. It returns zero. All 31 worker
steps pass. This tests the independent program; it does not test game behavior.
The smaller sparse two-node experiment independently reproduces an empty slot
and the extra BREAK. Receipts and symbol maps are retained in evidence.

## Complete runtime contribution

The extracted 3.6a `c.lib(segload)` object declares 244 code bytes. The linker's
symbol map places `_segload` at the start, `.segload` 18 bytes later, and the next
object's `.begin` exactly 244 bytes after the start. The generated contribution
matches resident h00 offsets 0x7978 through 0x7a6b byte-for-byte. Its 226-byte
manager begins at 0x798a, agreeing with the independently parsed dispatch bridge.

Both complete relocation records also match after expressing the source offsets
relative to the contribution: RELOC32 at +40 targets h00+8; RELOC32 at +62 targets
h01+0. The comparison checks complete unmodified bytes, record types, widths,
target hunks and addends. It does not mask relocation operands.

The 5.0a counterexample is equally important: its named CJ object also has 244
code bytes, and its naturally linked output has identical bytes and relocations.
Therefore this runtime match cannot select 3.6a over 5.0a. In the 5.0a probe the
next object is `__wb_parse`, while `.begin` occurs earlier; object placement is
checked using that experiment's own symbol map. The seven previous 3.6a runtime
matches plus this contribution cover 470 distinct bytes, recorded separately
from reconstructed game-source bytes and final ownership claims.

## Reproduce

Use fresh job names and the already pinned local distributions:

```powershell
python tools/aztec_worker.py prepare topology-new experiments/overlay-topology --commands experiments/overlay-topology/commands.json --aztec36
.\tools\run_worker.ps1 -Job build/worker-jobs/topology-new
python tools/aztec_worker.py collect build/worker-jobs/topology-new
python tools/aztec_worker.py prepare overlay50-new experiments/overlay-smoke --commands experiments/overlay-smoke/commands-50.json
.\tools\run_worker.ps1 -Job build/worker-jobs/overlay50-new
python tools/aztec_worker.py collect build/worker-jobs/overlay50-new
python tools/overlay_experiment.py build/worker-jobs/topology-new --comparison-job build/worker-jobs/overlay50-new
python tools/census.py --write
python tools/census.py --check
```

The comparison report is `evidence/experiments/overlay-topology.json`.
The game is only read by the final comparison and census, never by preparation,
compilation, assembly or linking. Full game content, allocations, relocation
layout, compiler flags and the investment overlay reconstruction remain open.
