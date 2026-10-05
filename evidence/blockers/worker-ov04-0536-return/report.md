# ov04_F_0536 return and local-layout follow-up

The earlier follow-up report conflated the stack frame size with the saved-handle slot. The oracle starts with `LINK A5,#-$92` (a 146-byte frame) and then stores `G_h01_46DA` at `-$3c(A5)`. Changing `line[93]` to `line[7]` moved the saved local to `-$3c`, but also shrank the frame to `-$3c`; it did not match the frame.

The selected declaration-order candidate keeps `1005L`, declares `F_h00_86DC` as returning `long`, and orders the locals so the compiler emits all three measured local facts: frame `-$92`, saved handle at `-$3c(A5)`, and the text buffer at `-$91(A5)`. These are confirmed in its Aztec-generated assembly. The declaration layout uses 22 bytes of upper locals, the 30-byte status table, a 4-byte local, the saved long, 8 bytes of lower locals, and a 77-byte text buffer.

A long return is supported by two independently matched ov04 callers: `ov04_F_0104` and `ov04_F_037E` both declare `extern long F_h00_86DC()` in source with `FUNCTION_WITH_DATA_MATCH` proofs. The resident address at h00+0x86DC is only a 4-byte jump veneer, so it does not expose the callee signature by itself.

The candidate compiles with aztec36. Its four final literals exactly match the independently evidenced 38-byte tail. The strict owned-code-data verdict remains `BLOCKED` because the candidate emits 652 code bytes plus 38 literal bytes; the target allows 622 plus 38. The diagnostic-only body comparison is `DIFFER`, with an inserted `move.l -4(a5),G_h01_46DA` at +42; mnemonic similarity is 0.4543. The raw first differing byte is +6 because the broad instruction-layout difference prevents A4 field normalization. This remains a broad code-shape mismatch, so the bounded experiment stops here.

The source and machine-readable receipts are adjacent to this report. No canonical source or recovery ledger was changed.
