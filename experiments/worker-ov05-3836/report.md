# ov05_F_3836 bounded Aztec 3.6a probe

Scope: inspect the closed CFG and typed global operands, then test two isolated source shapes. No canonical source, recovery candidate, proof, ledger, or ranking file was edited; verifier calls used `--isolated --output-dir experiments/worker-ov05-3836/...`.

## CFG-derived candidate

`ov05_F_3836` is hunk 5 `[0x3836,0x3a9e)`, 616 bytes, `CLOSED_CFG`, one return, no pending same-node dependencies. Its initial block converts signed words `G_h01_0A84` and `G_h01_5E42` to FFP and retains them in two long locals. It draws four short edges through `F_h00_8B88/8B4C/8AA8`, calls `F_h00_34E0` on globals `0x593e` and `0x5974`, conditionally increments byte `G_h01_46E1` and adds 42 to word `G_h01_5E56`, then calls `F_h00_09C0` with a counter capped at 30 and first argument 18 or 14 based on the counter being below 10. The final flag-controlled path computes one or two `(float-left - float-right) * 208.0 / 72.0` values, truncates each with `.Ffix`, stores the results and accompanying word tags, and passes their addresses to `F_h00_34E0`.

Best candidate is [ov05_F_3836.c](/D:/Prog/tales_recon/experiments/worker-ov05-3836/ov05_F_3836.c). Variant 1 is retained at [ov05_F_3836-v1.c](/D:/Prog/tales_recon/experiments/worker-ov05-3836/ov05_F_3836-v1.c). The important typing decisions are signed word globals for conversion, a byte for the counter and flag, and separate `float` locals for the two FFP operands. The source deliberately uses regular float operators rather than explicit FFP helper calls.

## Verifier and helper lowering

Best candidate result: `BLOCKED / COMPILE_ERROR`, Aztec 3.6a, flags `[]`, expected length 616, actual length unavailable, cache key `361097e787b14b13b3c7c7478a0ba34b9368dd7cb078fd8c678b20040244d323`, source SHA-256 `ab6fef54bd4ef6f5c717c37edffc20326926189fb57db55bce7bb7260b8255be`. Compiler and assembler returned 0; the linker returned 5 solely because the harness did not link the private helpers `.Fflt`, `.Fsub`, `.Fmul`, `.Fdiv`, `.Ffix`. As in the existing `ov11_F_5FB2` probe, there is no linked contribution, so no exact byte comparison and no first mismatch are available.

The compiler assembly at `build/compile-cache/361097e787b14b13b3c7c7478a0ba34b9368dd7cb078fd8c678b20040244d323/t000.asm` does naturally lower the floating-point parts into the target’s helper sequence: `.Fflt` twice; `.Fsub`; immediate `#$d0000048`; `.Fmul`; immediate `#$90000047`; `.Fdiv`; `.Ffix`. It also materializes the two float locals at `-4(a5)` and `-8(a5)` in the expected order. The constants correspond to 208.0 and 72.0, consistent with the observed immediates. Thus the FFP helper mechanism itself is a strong natural match; it remains unverified at linked-byte/relocation level.

The two source attempts differed around the capped count call. Variant 1 used nested calls with a 16-bit counter argument and therefore did not express the observed 32-bit push. The best candidate makes the third argument long and uses a ternary cap. This fixes the argument width, emits a 14-byte caller cleanup, and keeps the exact 18/14 branch. Its cap branch is still arranged differently from the target assembly (`move.b` path first and `move.l #30` after it, versus target's `moveq #30` fallthrough then byte extension). The first candidate’s full call shape therefore is not claimed to match. This is a bounded source-shape limitation; no more variants were tried.

## Recommendation and uncertainty

Keep the function undiscovered/unpromoted until an isolated verifier path can resolve the Aztec private helpers through pinned `m.lib` and compare the linked contribution plus relocations. The next experiment should be a verifier run with that library available, then address any actual first linked mismatch. If comparison stops on the counter clamp first, a single source rewrite should invert the ternary to put constant 30 on fallthrough while preserving a long result. No exact match or promotion is claimed here.
