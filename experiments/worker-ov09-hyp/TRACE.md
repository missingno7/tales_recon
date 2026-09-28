# ov09_F_298E v15 instruction trace

Baseline source: `experiments/direct-recovery/ov09_F_298E-v15.c` (672 bytes). The cache key recorded in `evidence/experiments/source-shape-search-baseline.json` is `5d74128b28b30c647f3528921a6bca6ac9f28bab31c5128da77f1c4cb132c580`; `python tools/diag.py ov09_F_298E --cache-key 5d74128b28b30c647f3528921a6bca6ac9f28bab31c5128da77f1c4cb132c580 --json` reports 183 aligned instructions, six candidate-only instructions, and 32 paired blocks. Original function length is 660 bytes.

## First register-choice divergence

The first aligned register-role difference is at the first flag-byte test, v15 source line 36. Original code-relative offsets `+0x74` / `+0x76` are `moveq #0,d1` and `move.b (a0,d0.l),d1`; v15 aligns these with candidate offsets `+0x78` / `+0x7A`, which are `moveq #0,d0` and `move.b (a0,d1.l),d0`. Thus the original keeps the scaled row index in `d0` and places the fetched byte in `d1`, while v15 uses `d1` for the index and `d0` for the fetched byte. The candidate-only copy immediately before that aligned pair is at `+0x70` (`moveq #0,d1`) and `+0x72` (`move.w d0,d1`). This is a register-allocation/lifetime observation, not proof of original source spelling or semantic necessity.

| Candidate offset | Original offset | Instruction | v15 source line / construct |
| --- | --- | --- | --- |
| `+0x70` | none | `moveq #0,d1` | 36: `*((unsigned char *)G_h01_4272+(row-14)*6)` flag-byte address |
| `+0x72` | none | `move.w d0,d1` | 36: widening/copying that computed byte offset for indexed addressing |
| `+0x138` | none | `moveq #0,d1` | 58: same row-scaled flag-byte address in the `value+5` test |
| `+0x13A` | none | `move.w d0,d1` | 58: same widening/copy before the indexed read |
| `+0x1FC` | none | `moveq #0,d1` | 78: same row-scaled flag-byte address in the `value+9` test |
| `+0x1FE` | none | `move.w d0,d1` | 78: same widening/copy before the indexed read |

The extra pairs are generated around three repeated uses of the pointer-add expression in v15 lines 36, 58 and 78. In each case, `(row-14)*6` forms the byte offset into `G_h01_4272`; the following `G_h01_0468[value]`, `[value+5]`, or `[value+9]` lookup then uses a separate index. The observed compiler choice keeps the loaded flag byte in `d0`, so it copies the row offset into `d1.l`. The original instruction stream uses `d0.l` directly as the flag-table index and leaves the fetched byte in `d1`.

The source mapping uses the candidate's code-relative instruction offsets from the validated whole-object CODE contribution. The diagnostics are advisory and do not establish whether these C expressions, temporary types, or evaluation order were historically used.
