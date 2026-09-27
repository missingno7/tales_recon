# `ov11_F_4B0C` shared-descriptor layout probe

Tested two declarations/access spellings derived from `worker-ov11-4b0c-data/findings.md`: the 16-byte record at hunk-1 `0x94EC`, field offsets `+0/+5/+6/+0xC/+0xE`, and the 16-byte-stride anchor relation. Both were run with `python tools/check_function.py --batch ... --isolated --output-dir ... --json` using Aztec 3.6a. The call to `F_h11_6ED6` was retained; isolated unit preparation included the recovered dependency as a separate object. No canonical file or promotion state was changed.

## Variants and results

- `probe-array-layout.c` declares one `struct Descriptor G_h01_94EC[110]` and expresses each static anchor as `&G_h01_94EC[index]`; the dynamic second base uses index `11 + G_h01_94DE`.
- `probe-byte-stride.c` uses a 1760-byte base at `G_h01_94EC` and explicit typed casts from `base + 16*index` (including the dynamic selector). This tests a byte-storage/pointer-arithmetic source spelling against the record-array spelling.

Both compiled and both returned `DIFFER`. Unit size is **1052 bytes** for each against **1028 bytes** expected (`ov11_F_4B0C` 954 + retained `ov11_F_6ED6` 74). The linked candidate's `_F_h11_6ED6` symbol is at offset `0x3d2` (978), confirming the dependency remains present after the candidate function. Shared-array spelling reduced the older probe-v2 unit from 1054 to 1052 bytes; byte-stride spelling had the same 1052-byte size.

Both reports give raw/normalized first byte difference at `+6`, where candidate A4 displacements reflect the naturally packed synthetic harness. The first structural mismatch is an expected instruction at function `+84`. The target trace around the site is `move.w #$8e,$14c2(a4)` at `+78`, then `move.w #5,$14e2(a4)` at `+84`. With A4 bias `0x7FFE`, these operands resolve to hunk-1 offsets `0x94C0` and `0x94E0`, respectively. The candidate emits a `move.w #5` at `+78` to its separately named `G_h01_94E2` (hunk identity `0x94E2`), then proceeds to the descriptor LEA; it lacks the `#$8e` write and the target's `#$5` destination identity. The structural shape is therefore off, and the superficially matching `#5` value is not a target-symbol match.

## A4 identity assessment

The shared-base source spelling now encodes descriptor identities as base `G_h01_94EC` plus evidence-derived multiples of 16; for example entry 10 is `0x94EC + 10*16 = 0x958C`, corresponding to A4 displacement `0x158E`. The compiler listing uses `_G_h01_94EC+constant` for descriptor anchors. The initial scalar references (`G_h01_94DE`, `G_h01_94E4`, `G_h01_94E6`, `G_h01_94E8`) retain the expected mechanical identities; their raw A4 displacements differ because the harness packs BSS differently. Later stores require the same bias discipline: target A4 displacement `0x14E2` names hunk offset `0x94E0`, while the candidate's `G_h01_94E2` names offset `0x94E2` and is therefore wrong for that store.

The exact function/unit comparator cannot certify A4 operands because the unit has a different instruction layout and reports `INSTRUCTION_LAYOUT_DIFFERS_FOR_SYMBOL_PROOF`; `relocation_equal` remains false. The current evidence supports the corrected descriptor identity model and the initial scalar identities, but not an exact A4 relocation proof or whole-function match.

## One case-6 assignment follow-up

The target trace shows a plausible omitted case-6 C assignment: after `F_h00_57D2(0x58)`, store `0x8e` to the global whose hunk identity is `0x94C0`. The correct mechanical C name is `G_h01_94C0` because `0x7FFE + 0x14C2 = 0x94C0`. A preliminary draft used `G_h01_94C2` (the wrong hunk identity); that output is retained in `case6.stdout.jsonl` but discarded as a symbol-mapping error. The single corrected test is `case6-coordinate-assignment-hunkid.c`, checked once with isolated Aztec 3.6a and the same F6ED6 dependency.

The corrected candidate emits `move.w #$8e` to its symbol `_G_h01_94C0` at `+78`, resolving the target address identity; it then emits `move.w #5` at `+84`, but to `_G_h01_94E2`. The target operand `$14E2(a4)` resolves to hunk offset `0x94E0`, so the case-value assignment still has the wrong source symbol identity. The report's first raw/normalized difference remains `+6`; structural alignment now first differs at `+136` rather than `+84`, showing that the added store fixed the earlier structural gap. The linked unit is **1058 bytes** versus **1028 expected** (`F_h11_6ED6` remains linked at offset `0x3D8`); the verifier returns `DIFFER / COMPLETE_UNIT_SIZE_DIFFERS`, and relocation proof is blocked by instruction-layout differences. Stop here: no further variants were compiled.

Full outputs are in `isolated.stdout.jsonl` and `case6-hunkid.stdout.jsonl`; exact source variants and batch requests are adjacent.
