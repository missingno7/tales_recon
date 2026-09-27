# ov08_F_1D42 isolated Aztec trial

Target evidence: `ov08_F_1D42`, overlay ov08 / HUNK 8, 522 bytes, `CLOSED_CFG`, 20 direct calls all identified as relocated resident stubs, no relocations or PC-relative data. The candidate follows the CFG’s save/clear/set/restore operations, straight-line graphics calls, A4-relative object initialization, bounded counter loop, and final counter display. All source names are mechanical hunk/offset identities; no semantic labels or binary bytes were used.

Command:

```powershell
python tools\check_function.py ov08_F_1D42 experiments\worker-ov08-1d42\ov08_F_1D42.c --profile aztec36 --isolated --output-dir experiments\worker-ov08-1d42\verifier --json
```

The first invocation was `BLOCKED / COMPILE_ERROR` because two referenced mechanical globals lacked declarations. My first declaration-edit command inserted literal newline markers and produced a second `BLOCKED / COMPILE_ERROR`; I corrected the file and reran the same source hypothesis without changing its control-flow interpretation. Final verdict: **DIFFER**, expected 522 bytes, actual 526, mnemonic similarity 0.9316; no relocation proof. Final isolated receipt: `verifier/ov08_F_1D42/f8d71e03338c5ad4ceee27ed7d1ac3e8505636871a18f70945e6639640287829-aztec36-753a5bdd8288.json`.

First raw / normalized mismatch is offset `0x6` (expected `d372`, actual `804e`), in the A4 displacement for the first access through `G_h01_5370`; emitted operand is `-$7fb2(a4)` while the original instruction is `-$2c8e(a4)`. The first structural instruction difference is offset `0x28`: the original pushes five call arguments (`$c7`, `$13f`, `$a8`, zero, and the A4 value) before the call at 7548; this candidate emitted no corresponding immediate-argument sequence there. The candidate therefore misidentified the arity/argument shape of the `resident_F_8B76` call. That, plus the unresolved A4 address encoding difference, is the concrete blocker: current evidence does not support the call contract and global binding strongly enough to justify another source adjustment.

Recommendation: keep `ov08_F_1D42` discovered and unpromoted; resolve the A4 address mapping and identify the five-argument `resident_F_8B76` call contract from independent evidence before spending another compile. `--isolated` kept verifier artifacts in this experiment directory; no canonical ledger, ranking, attempts, proofs, or promoted source was written.
