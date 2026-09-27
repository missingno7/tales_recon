# ov08_F_1D42 RectFill call revision r1

Starting from `ov08_F_1D42.c`, this single isolated revision replaces the incomplete first `F_h00_8B76` call with the independently supported five-argument call:

```c
F_h00_8B76(G_h01_46CA, 0L, 168L, 319L, 199L);
```

The required mechanical extern `G_h01_46CA` was added. No other source hypothesis was changed. The candidate is `ov08_F_1D42_rectfill_r1.c`.

Command:

```powershell
python tools\check_function.py ov08_F_1D42 experiments\worker-ov08-1d42\ov08_F_1D42_rectfill_r1.c --profile aztec36 --isolated --output-dir experiments\worker-ov08-1d42\verifier-rectfill-r1 --json
```

Final Aztec 3.6a verdict: **DIFFER**. Expected code size 522 bytes; candidate 540 bytes. `relocation_equal=false`, with issue `INSTRUCTION_LAYOUT_DIFFERS_FOR_SYMBOL_PROOF`; no relocation proof. Mnemonic similarity is 0.9484. Receipt: `verifier-rectfill-r1/ov08_F_1D42/b6218fd5ca4b74a26251e2cc9bfae3033e451bfad62bc2b2168363c5f9cbcd52-aztec36-f2e4ef70f8ee.json`.

First raw/normalized mismatch: offset `0x6`, expected `d372`, actual `804e` (historical A4 displacement `-$2c8e`, candidate-natural displacement `-$7fb2`). Because layouts diverge, the comparator cannot normalize this A4 symbol reference in this trial. First structural mismatch: `insert` at candidate offset `0x56` (decimal 86); expected no instruction, candidate emits `move.l -$7fae(a4),-(a7)`, `jsr -$7ffe(a4)`, `addq.w #$8,a7`. This is the still-present second short `F_h00_8B76(G_h01_01B6,0L)` statement. The edit fixed the first RectFill call’s arity/order but did not fix that later spurious call or the other broad code/reference differences. Stop here; the remaining mismatch is broad enough to require a fresh full instruction-to-source pass before another compile.

`--isolated` kept outputs under this experiment directory. No canonical source, ledger, ranking, attempts, or proof was written.
