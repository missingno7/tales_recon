# `ov04_F_0536` frame and immediate-push follow-up

This bounded Aztec 3.6a comparison tested two source edits to candidate3. It changed only files under this follow-up directory; no canonical source, ledger, promotion state, or fixtures were edited.

## Evidence from candidate3 and target

The target function is 622 bytes, and the independently owned contiguous literal tail is 38 bytes. Candidate3 compiles to a 656-byte function body plus that exact 38-byte tail (694 bytes total). At `+0`, both the target and candidate3 use `link.w a5,#-$92`. At `+4`, however, the target saves the A4 value to `-$3c(a5)`, while candidate3 saves it to `-$92(a5)`. These are distinct facts: the target frame is 0x92 bytes, and this saved local is at displacement -0x3c.

Candidate3 declares `char line[93]`. Reducing it to 7 bytes changes the compiler's frame to `-$3c`, which breaks the target LINK size, while moving the save destination to `-$3c(a5)`. Thus `line[7]` is not a valid target frame match; it only matches the saved-local displacement. The observed target instead calls for preserving the -0x92 frame while placing this saved local at -0x3c through some other source/local-layout explanation.

At `+24`, candidate3 emits `move.w #$3ed,-(a7)` from the unsuffixed `1005` int argument. The target emits `pea.l $3ed.w` (`48 78 03 ed`), the compiler's long-constant push form. The target call's long-sized argument is naturally represented as `1005L`.

## Two variants

| Variant | Edit | LINK at `+0` / save destination at `+4` | Push at `+24` | Function body | Exact outcome |
|---|---|---|---|---:|---|
| `long_open_mode.c` | Change both `1005` arguments to `1005L`. | `LINK -$92` matches; save destination `-$92(a5)` differs from target `-$3c(a5)`. | Now exact `pea.l $3ed.w`. | 656 bytes | `DIFFER` |
| `seven_byte_line_and_long_mode.c` | Also change `line[93]` to `line[7]`. | `LINK -$3c` differs from target `-$92`; save destination `-$3c(a5)` matches. | Exact `pea.l $3ed.w`. | 656 bytes | `DIFFER` |

Both compile. In both, the 38-byte literal suffix equals the independently evidenced tail byte-for-byte. However, the strict owned-code-data check remains blocked: the body is still 656 rather than 622 bytes, leaving 34 code bytes unclaimed. The stripped-body pure comparison also differs. The combined seven-byte variant does not have a correct prologue because its LINK operand is wrong. Its next structural difference after the save and push sites is an extra `ext.l d0` at `+38`; candidate3 declares `F_h00_86DC` as returning `int`, then assigns it to a `long`. The target does not sign-extend the return before saving it, which points to a long return declaration as a high-value ABI hypothesis. Other call return declarations should be reviewed similarly before expecting a full match.

Full compiler receipts and comparator outputs are in `results.json`; both exact C inputs are beside this report. The `1005L` push match is a useful local source-shape result. The line[7] change is specifically a negative result for frame size: it happens to align the save displacement while changing the LINK allocation away from the target. Neither variant proves the complete 622-byte function, and no promotion was attempted.
