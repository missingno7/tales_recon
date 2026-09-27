# ov11_F_4B0C A4 data/descriptor map

Status: structural layout hypothesis strongly supported; not a recovered data-layout proof. No canonical sources, ledgers, or assets were changed.

## Address equations and evidence

The function ledger gives Amiga A4 bias `0x7FFE` (resident relocation evidence in hunk 0, source offset `30308` / `0x7664`, targeting hunk 1). Therefore a short A4 displacement `d` addresses hunk-1 offset `0x7FFE + d`. The references in `ov11_F_4B0C` map the relevant compact control block as follows:

| A4 displacement | hunk-1 target | observed width/use |
|---|---:|---|
| `0x14E0` | `0x94DE` | word; cleared/read as the dynamic table index |
| `0x14E2` | `0x94E0` | word; repeatedly assigned case/mode values |
| `0x14E4` | `0x94E2` | word; case value / other state |
| `0x14E6` | `0x94E4` | word; common tail copies descriptor `+6` here |
| `0x14E8` | `0x94E6` | word; initialized to 1 |
| `0x14EA` | `0x94E8` | long pointer; selected descriptor address |

The table base used by `lea $14EE(a4)` is hunk-1 `0x94EC`. Every statically selected descriptor address is congruent to `0x14EE mod 16`, and the dynamic selector is shifted left four bits before addition. This establishes a 16-byte stride. `$158E(a4)` resolves to `0x958C`, exactly entry 10 (`0x94EC + 10*16`) of the same address sequence, not an unrelated descriptor base.

Observed descriptor anchors (A4 displacement → hunk-1 offset / index from `0x94EC`):

```
14EE → 94EC / 0    158E → 958C / 10   162E → 962C / 20
16AE → 96AC / 28    172E → 972C / 36   175E → 975C / 39
178E → 978C / 42    17FE → 97FC / 49   186E → 986C / 56
187E → 987C / 57    18BE → 98BC / 61   194E → 994C / 70
19DE → 99DC / 79    19FE → 99FC / 81   1A1E → 9A1C / 84
1A6E → 9A6C / 89    1ABE → 9ABC / 94   1AEE → 9AEC / 97
1AFE → 9AFC / 98    1B4E → 9B4C / 105  1BBE → 9BBC / 109
```

These are referenced anchors, not proof that the original allocation ended after 110 entries or that every intervening record has the same ownership/initialization history.

## Record and state views

The common F4B0C block accesses descriptor offsets `+0` (long object pointer), `+5` (byte copied to target object byte `+0x34`), `+6` (word copied to state), `+0xC` and `+0xE` (word deltas added to two coordinate globals). Neighboring recovered source `src/recovered/ov11/ov11_F_4AA4.c` independently uses the same field positions and increments a pointer to this shape. The compact C *view* for verifier work is therefore:

```c
struct Hunk1TargetView { char unknown_00_33[52]; char field_34; };
struct Ov11DescriptorView {
    struct Hunk1TargetView *field_00; /* +0, 32-bit pointer */
    char unknown_04;                  /* +4 */
    char field_05;                    /* +5, byte */
    int field_06;                     /* +6, 16-bit Aztec int */
    char unknown_08[4];               /* +8..+11 */
    int field_0c;                     /* +12, 16-bit Aztec int */
    int field_0e;                     /* +14, 16-bit Aztec int */
}; /* size/stride 16 */
```

The state addresses are contiguous and word accesses establish the widths, but treating them as one C aggregate is only a layout view; no shared semantic object/name is asserted. Leave the word at target `0x94E2` in the view as unknown if a aggregate is useful.

Minimum table declaration to preserve the proven arithmetic for a verifier is one mechanically named base plus record indexing:

```c
extern struct Ov11DescriptorView G_h01_94EC[110]; /* probe coverage extent only */
extern struct Ov11DescriptorView *G_h01_94E8;
```

Use `&G_h01_94EC[n]` for anchors; in particular use `[10]` for the `0x158E` address. Keep word globals as the existing mechanical offsets (`G_h01_94DE`, `G_h01_94E0`, etc.) if the candidate refers to them individually. Do not declare every table anchor as a separate extern: that loses the shared-base/addend relationship. The `[110]` bound is solely the minimum probe extent covering referenced index 109; it does not claim original array bounds or source ownership.

## Isolated compiler tests

`probe-one-base.c` declares one descriptor base array and uses `[10]`. Aztec 3.6a compiled it for overlay node 9. The generated BSS symbol map placed the word globals, pointer, and base array consecutively at offsets 40, 42, …, 50, 54; the `lea` to `[10]` encoded the correct address (`target offset 54 + 10*16 = 214 = 0xD6`, after the profile's `0x7FFE` A4 bias). This discriminates one-base/addend modeling from the earlier v2 probe's erroneous separate mechanical symbols and arithmetic labels.

`probe-two-fields.c` compiled the field accesses. Its generated instructions use byte offset `+5` and word offsets `+6`, `+0xC`, `+0xE`, consistent with the observed F4B0C tail. These probes test compiler layout only; they do not compare the target function, prove BSS allocation contents, or establish DATA_LAYOUT_MATCH.

Receipts and reproducible inputs:

- `probe-one-base.c` / `probe-one-base.json` (Aztec 3.6a cache key `9536d9201231c55b8be40448386c9bd20c39aacbda548ba69758d91f84474ab3`)
- `probe-two-fields.c` / `probe-two-fields.json` (Aztec 3.6a cache key `4ad162ed261cbab8023e34d9ee54f131557b73e717864b8132610017904e9216`)

## Missing proof and next discriminating experiment

Still missing: independent ownership/bounds and complete target hunk-1 object layout/relocations for the descriptor region, plus a whole-function code/relocation match. The synthetic compiler harness naturally packs the declarations and is not evidence that this is the historical allocation.

Next experiment: perform a read-only walk of hunk-1 relocation sites and all xref-producing instructions for `0x94EC..0x9BBC`, then compare neighboring verified functions' expected target identities. The decisive outcome is whether each record's `+0` long is a relocation-bearing pointer field or runtime-populated BSS and whether any references escape this indexed table view. Do not promote the 110-entry extent unless those ownership/boundary obligations are independently closed.
