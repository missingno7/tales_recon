# Synthetic AJ external-reference grammar probe

Bounded experiment using only generated assembler input and the pinned Aztec 3.6a assembler. No production parser/verifier or canonical files were changed. Both assembler commands returned 0.

## Inputs and receipts

- Job: `build/worker-jobs/aj-fixup-grammar-001/` (`request.json`, `result.json`; both preserve pinned tool identities and per-file hashes).
- One call input: `experiments/worker-aj-fixup-grammar/src/one.asm`, SHA-256 `5d8c9a7f405c6aa6d30862ab5c81a6627b96c8b3bcee35cd6585ddb9ec9ad2c3`:
  ```asm
          public  _one
  _one:
          jsr     .Fflt#
          rts
  ```
- Two-call input: `experiments/worker-aj-fixup-grammar/src/two.asm`, SHA-256 `575957cf512e836c0f5171b31cf9d0124b209f312892e3931a681d3225f7ff39`; same shape, with two `jsr .Fflt#` lines before `rts`.
- `one.o`: 68 bytes, SHA-256 `1563fb915eea2ce9de9562371d2cbaf2171c0f51ff9daca6b1408352ea6988fc`.
- `two.o`: 72 bytes, SHA-256 `d85bd0a63419bf40c9aad765d141afcee4cbf0f86790a9d440fec25233d3ed3f`.

## Byte comparison

Both objects have `AJ` at bytes `00..01`. The 32-bit field at `0x0C` is `00000006` for one call and `0000000A` for two calls. The assembler output contains `4E BA FA 71` at file offset `0x25` in both; the two-call object has another at `0x2B`. Each is followed by bytes `00 11` (`one.o: 0x29..2A`; `two.o: 0x29..2A` and `0x2F..30`), then the return opcode `4E 75` (`0x2B` and `0x31`, respectively). The opcode `4E BA` is JSR with a 16-bit PC-relative extension word, so the instruction operand itself is 16 bits.

The trailer in each object names `_one`/`_two` and then contains a single `.Fflt` name record. In `one.o`, `.Fflt` starts at `0x3D`, preceded by bytes `07 08 00 00` at `0x39..3C`; in `two.o`, it starts at `0x41`, preceded by the same bytes at `0x3D..40`. Thus the name is interned once even when the source has two calls. There is no obvious multiplicity list adjacent to the symbol name.

Bytes `0x1C..0x24` differ as `00 0C 00 11 00 11 C0 00 11` vs `00 0D 00 12 00 12 C0 00 11`: three nearby words each increase by one, while the trailing bytes remain. The one-vs-two probe does not establish which field encodes site count, offsets, or width. The repeated `00 11` after each opcode may be linker metadata, but this interpretation is unproven.

## Verdict

The experiment confirms named external symbol presence and demonstrates where each call instruction and repeated adjacent marker appear. It does **not** decode a strict per-reference table: `.Fflt` remains one symbol record for both calls, and the changed header words are ambiguous. A strict parser should not infer all sites or fixup widths from these bytes yet. The 16-bit instruction extension is visible from the JSR encoding, but binding that word to `.Fflt` as a linker fixup still lacks a parsed record proof.

The controlled one-NOP follow-up below tests whether a site-like field tracks a known call shift; it is not a production parser or verifier change.

## Controlled one-NOP discriminator

The follow-up used the exact same `_one` public label and the same assembler command, adding only `nop` before the single call. The input is `experiments/worker-aj-fixup-grammar/shifted-same-src/shifted-same.asm` (SHA-256 `0359ed0aa8340aee444dba94d894bf33cbbd07214240c2b7d2cbf7c530b4c55c`). Its isolated job is `build/worker-jobs/aj-fixup-grammar-003/` (`result.json` SHA-256 `d8bd82a4c95cbfe093652d52911eb9a12d3c992c0e4b82b462eb0f8f194e7a26`).

`shifted-same.o` is 68 bytes, SHA-256 `55d3addb10827047be5062095f5da6b0de698a4ed2f2b823fd0467532ecedd84`. Against the original `one.o`, the code-size field at `0x0C` rises `6→8`; the three words at `0x1C`, `0x1E`, and `0x20` remain `000C`, `0011`, and `0011`; byte `0x24` alone changes `11→13`. The call moves exactly two bytes (`4E BA FA 71` starts at `0x25` originally and `0x27` after `NOP`), while the `.Fflt` name-record trailer remains byte-identical at `0x39..0x43`.

This gives positive evidence that byte `0x24` tracks a code location shifted by two bytes; it is a plausible one-byte site-offset field. It does not establish the field's base/encoding or tie it to the 16-bit extension word as a named `.Fflt` fixup. The single-reference pair also cannot determine whether additional call sites are represented as repeated fields or an offset list. Therefore the grammar remains ambiguous for a strict parser and this audit stops here. The first blocker is now specifically the undocumented AJ header/site-field coordinate and its link to the named external record; do not parse by heuristic or promote call identities from this correlation alone.
