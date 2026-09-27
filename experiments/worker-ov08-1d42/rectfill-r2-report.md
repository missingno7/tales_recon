# ov08_F_1D42 RectFill call revision r2

This one-change follow-up removes the candidate’s second short `F_h00_8B76(G_h01_01B6,0L)` call and keeps the corrected five-argument call in `ov08_F_1D42_rectfill_r1.c`. Candidate: `ov08_F_1D42_rectfill_r2.c`.

Command:

```powershell
python tools\check_function.py ov08_F_1D42 experiments\worker-ov08-1d42\ov08_F_1D42_rectfill_r2.c --profile aztec36 --isolated --output-dir experiments\worker-ov08-1d42\verifier-rectfill-r2 --json
```

Final Aztec 3.6a verdict: **DIFFER**. Expected 522 bytes; actual 528 bytes. `relocation_equal=false`, with `INSTRUCTION_LAYOUT_DIFFERS_FOR_SYMBOL_PROOF`; no relocation proof. Mnemonic similarity: 0.9608. Receipt: `verifier-rectfill-r2/ov08_F_1D42/1791d92988fb94a9170af32db80bb8a685795ac4315f23c964792bdaf08d0a2c-aztec36-93aa1507cd3b.json`.

First raw/normalized mismatch remains offset `0x6` (expected `d372`, actual `804e`), the historical A4 displacement versus candidate-natural placement for `G_h01_5370`; code-layout divergence prevents normalization. First structural mismatch is a `replace` at offset `0x12c` (decimal 300): expected `clr.l -(a7)` (2 bytes), candidate emitted `pea.l $13f.w` (4 bytes). Further code/reference differences remain after the two call corrections. Stop this target; no more candidate iterations are warranted without a fresh whole-function source mapping.

`--isolated` kept the verifier output under this experiment directory. No canonical source, ledger, ranking, attempts, or proof was written.
