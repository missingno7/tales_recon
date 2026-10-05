# ov07_F_0F30 larger-leaf audit

Scope: read-only evidence inspection plus one isolated Aztec 3.6 code-shape baseline. No canonical source, proof, recovery ledger, ranking, or blocker was edited. The baseline source and receipt are local to this experiment directory.

## Function shape and ownership

`validated_function('ov07_F_0F30')` passes for hunk 7 `[0x0F30,0x1424)`, 1268 bytes, HIGH-confidence `CLOSED_CFG`. There are 15 CFG edges, one RTS, no direct same-overlay callees, no indirect control flow, no undecoded gaps, no boundary stops, and no HUNK relocation records. The frame is `LINK A5,#0`; the function reads a signed word argument from `8(A5)`. It references no PC-relative data or strings, so there is no adjacent compiler-owned literal tail to claim.

The 113 recorded A4-relative reference sites resolve to five unique hunk-1 offsets:

- `0x5370`: a byte global written with `12` on entry and read before each color/helper call. A separate ov05 candidate uses a `char *` view at this same mechanical global, which supports but does not independently prove that source type here.
- `0x46CA`: passed to every helper call, consistent with the `long` global/pointer view used by the separate ov05 source hypothesis; type and semantics remain provisional.
- `0x1BC`, `0x1A4`, `0x162`: relocated resident trampoline slots for `resident_F_8B88`, `resident_F_8B4C`, and `resident_F_8AA8`, respectively; each helper is called 16 times.

No additional A4 globals, string references, or owned CODE data were found. The three resident helper identities and the two globals form the complete observed external-data/call surface.

## Dispatch and repeated blocks

The entry stores byte value 12 through the global at `0x5370`, loads the signed word argument, and branches to a dispatch ladder at function-relative `+0x4C6`. The ladder compares against `0xC0`, `0xE0`, `0x100`, and `0x120`, branching to four backward body blocks at `+0x016`, `+0x142`, `+0x26E`, and `+0x39A`; other values take the short return path. Each block contains four repeated triples: set up through `F_8B88`, followed by one `F_8B4C` and one `F_8AA8`. The latter two calls take the handle, the argument (sometimes plus 24 or 25), and a fixed coordinate pushed with `PEA`. The fixed coordinates are 0xAE/0xC2 in the first three cases and 0xAC/0xC5 in the last. This supports a compact source outline as a four-case drawing/coordinate routine, but the helper semantics and names are not established by this function alone.

## One isolated compiler baseline

I compiled [candidate.c](D:/Prog/tales_recon/experiments/worker-ov07-0f30-audit/candidate.c) once with `python tools/check_function.py --isolated --profile aztec36 --output-dir experiments/worker-ov07-0f30-audit/check ov07_F_0F30 ...`. It models the four cases and shared globals, but mistakenly gave `F_8B4C` and `F_8AA8` only two arguments. Result: `DIFFER / CODE_OR_REFERENCE_DIFFERS`; expected 1268 bytes, actual 1052, mnemonic similarity 0.1404. The first raw difference is at `+0x006` (A4 displacement); the first structural instruction difference is at `+0x02C`: expected `PEA.L #$AE`, while the candidate starts the next argument load. The absent third argument and associated 12-byte call cleanup recur throughout the four blocks, so this is a broad arity/layout mismatch, not a near-match. Relocation equality is false and the verifier cannot normalize the A4 address correspondence after that structural divergence.

The exact first-mismatch evidence is preserved in `check/ov07_F_0F30/*`. No second compile was run. The next useful experiment is one corrected candidate with three arguments to `F_8B4C` and `F_8AA8`, preserving the fixed-coordinate sequence above; only then can switch lowering and A4 identity be assessed meaningfully.

## One corrected-arity revision (parent follow-up)

Candidate [candidate-v2.c](D:/Prog/tales_recon/experiments/worker-ov07-0f30-audit/candidate-v2.c) adds the measured third coordinates to every `F_8B4C`/`F_8AA8` call and changes nothing else from the first outline. It was compiled once in isolated mode with Aztec 3.6. Verdict remains `DIFFER / CODE_OR_REFERENCE_DIFFERS`: expected 1268 bytes, actual 1256 bytes. The first structural difference is at `+0x04C`: target uses `ADD.W #$19,D0; EXT.L D0; MOVE.L D0,-(A7)`, while the candidate uses `EXT.L D0; MOVEA.L D0,A0; PEA.L $19(A0)`. The same source pattern emits address arithmetic from `(long)y + 25L`; target evidence requires 16-bit addition before sign extension. The first raw difference remains `+0x006` at the A4 global displacement. `relocation_equal=false`, no relocation proof was produced, and the verifier reports `INSTRUCTION_LAYOUT_DIFFERS_FOR_SYMBOL_PROOF`; A4 identity therefore remains unproven. No further compile was run.

## Final targeted word-width revision (parent follow-up)

Candidate [candidate-v3.c](D:/Prog/tales_recon/experiments/worker-ov07-0f30-audit/candidate-v3.c) keeps the corrected helper arity and changes each repeated `+24`/`+25` expression to `(long)(y + offset)`, so the addition occurs on the signed-word argument before widening. One isolated Aztec 3.6 run still returns `DIFFER / CODE_OR_REFERENCE_DIFFERS`: expected 1268 bytes, actual 1256; mnemonic similarity 0.7629. The `+0x04C` structural mismatch is resolved. The first remaining structural difference is a deletion at `+0x23A`: target has `ADD.W #$18,D0`; candidate has no instruction there. First raw mismatch is still `+0x006` (A4 displacement). A4 remains unproved: `relocation_equal=false`, no relocation proof, and `INSTRUCTION_LAYOUT_DIFFERS_FOR_SYMBOL_PROOF`. No further compile was run.

## Read-only audit of the proposed remaining +24 adjustments

I compared the target disassembly's `ADD.W #$18,D0` sites with candidate-v3 source and its cached Aztec assembly before deciding whether to run another compile. The target has 12 such sites at function-relative offsets `0x178,0x1C2,0x23A,0x256,0x2A4,0x2EE,0x366,0x382,0x3D0,0x41A,0x492,0x4AE`; candidate-v3 emits 10 `ADD.W #24,D0` instructions. The missing source adjustments are at target-corresponding calls `+0x23A` (case `0xE0`, fourth `F_8B4C`), `+0x2EE` (case `0x100`, second `F_8AA8`), `+0x366` (case `0x100`, fourth `F_8B4C`), and `+0x41A` (case `0x120`, second `F_8AA8`). Candidate-v3 also incorrectly adds `+24` in the third `0x100` group to both helpers, where target has neither adjustment. Thus there are four missing call-site adjustments and two wrongly added adjustments (net two fewer ADD.W instructions / eight bytes), not exactly three missing adjustments; the residual 12-byte object deficit also includes other differences. The conditional for another compile was not met, so no source was changed and no compile was run.
