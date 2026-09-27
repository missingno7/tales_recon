# ov08_F_1D42 RectFill follow-up r3

## Targeted argument trace

At target-relative `+0x12c` (decimal 300), the original pushes `199` at `+0x128`, clears a longword at `+0x12c`, pushes the A4-relative pointer at `+0x12e`, then calls `resident_F_8AA8` at `+0x132`. In the observed three-argument call shape used elsewhere in this candidate, the stack is pushed right-to-left, so the `clr.l -(a7)` is the second C argument (the x-coordinate in the `(pointer, x, y)` model), not the y value. The y value at this site is 199. This conclusion is based on code and call order; no semantic library name is claimed for `resident_F_8AA8`.

## One isolated variant

Candidate: `ov08_F_1D42_rectfill_r3.c`. Relative to r2, only the final matching `F_h00_8AA8(G_h01_0162, 319L, 199L)` was changed to `F_h00_8AA8(G_h01_0162, 0L, 199L)`.

Command: `python tools/check_function.py ov08_F_1D42 experiments/worker-ov08-1d42/ov08_F_1D42_rectfill_r3.c --profile aztec36 --isolated --output-dir experiments/worker-ov08-1d42/verifier-rectfill-r3 --json`.

Aztec36 verdict: `DIFFER` / `CODE_OR_REFERENCE_DIFFERS`, expected 522 bytes, actual 526 bytes, mnemonic similarity 0.9673, `relocation_equal=false`, `proof_level=null`. The targeted call correction removes the r2 structural replacement at `+0x12c`; the first structural mismatch moves later to `+0x194` (decimal 404), where the candidate inserts `cmpi.b #$a, -$7f92(a4)` and `bcc.b`, with no corresponding expected instructions at that aligned point. Epilogue is consequently four bytes later in the candidate. A4 layout remains unnormalized (`INSTRUCTION_LAYOUT_DIFFERS_FOR_SYMBOL_PROOF`); first raw mismatch is still the prologue's A4 displacement at offset 6.

Receipt: under `verifier-rectfill-r3/ov08_F_1D42/` (source SHA `3d3790c277f745c9b6c812beb16e948705e592dd53d88860e5c0d8f1a92d922c`).

## Stop point

One targeted historical-C variant was attempted. It corrected the specific call-argument instruction but exposed a separate control-flow/layout divergence at `+0x194`, rather than another argument-passing issue. I did not spend the second allowed variant on a blind rewrite. Keep this candidate unpromoted; the next work should map the loop/text-condition control flow and exact global identities before further compilation.
