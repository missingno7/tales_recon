# ov11 small-unit frontier

Read-only trace from the current function/ranking evidence. No compiler was run and no canonical files were changed.

## `ov11_F_2430` (76 bytes)

Its pending local dependency is `ov11_F_247C` (230 bytes), called at site `0x2472`. The callee starts exactly at the caller’s end (`0x247C`), so this pair is naturally adjacent and totals 306 bytes. In isolation, this looks like a small two-function unit.

It is not a self-contained unit: `F_247C` also has pending calls to `ov11_F_2E26` (196 bytes), `ov11_F_54F8` (192 bytes), and `ov11_F_5C42` (168 bytes). `F_2E26` and `F_54F8` both call `ov11_F_5962` (132 bytes), and `F_5962` and `F_5C42` call each other. The pending call graph from `F_2430` therefore reaches six functions totaling 994 code bytes, with a two-function cycle. `F_2430` also calls the recovered `ov11_F_4696` at `0x4696`; that far same-node edge makes its measured local interval `0x2430..0x4696` (8,806 bytes), containing 29 discovered function entries and 466 unassigned bytes. This is the large/cyclic option despite the adjacent first edge.

## `ov11_F_5EC0` (106 bytes)

Its one pending local dependency is `ov11_F_5C42` (168 bytes), called at site `0x5EF8`. The closure is `F_5EC0 → F_5C42 → F_5962 → F_5C42`, a three-function cycle path totaling 406 code bytes. `F_5EC0` also calls recovered `ov11_F_41F6` (638 bytes). The intervening `ov11_F_5D14` (428 bytes) is a natural bridge: it calls `F_5C42` three times and calls recovered `F_41F6`, `F_37A0`, `F_25F8`, and `F_4474`.

The compact physical interval `0x5962..0x5F2A` is 1,480 bytes across nine functions. Its unresolved source bodies are `ov11_F_5962` (132), `ov11_F_5C42` (168), `ov11_F_5D14` (428), and `ov11_F_5EC0` (106), totaling 834 bytes. Existing source bridges in that interval are `ov11_F_5A12` (80), `ov11_F_5A62` (78), `ov11_F_5AB0` (276), `ov11_F_5BC4` (86), and `ov11_F_5C1A` (40). Two uncovered spans remain: 44 bytes between `F_5962` and `F_5A12`, and 42 bytes between `F_5C42` and `F_5D14`.

The current `same_node_unit_ready` gate still sees the `F_41F6` call, so the measured interval expands to `0x41F6..0x5F2A` (7,476 bytes): 29 function entries, 7,350 decoded bytes, and 126 unassigned bytes. Eleven functions in that interval lack recovered source: `F_487E` (336), `F_4B0C` (954), `F_4EC6` (420), `F_51C0` (824), `F_54F8` (192), `F_55B8` (642), `F_583A` (296), `F_5962` (132), `F_5C42` (168), `F_5D14` (428), and `F_5EC0` (106), totaling 4,498 bytes. This interval-closure requirement, plus the 126 unassigned bytes, is the proof gate that must be cleared before the small dependency cycle can admit `F_5EC0`.

## Recommended future worker unit

Choose the `ov11_F_5EC0` interval/cycle. Its pending call closure is only three functions and 406 bytes, and the surrounding 1,480-byte region has five already recovered bridge functions. This is a tighter, more bounded reconstruction target than `F_2430`’s six-function, two-cycle call closure and 8.8 KB direct unit span. Include `ov11_F_5D14` because its three calls to `F_5C42` lie in the natural interval.

Required proof gate: close `same_node_unit_ready` over `0x41F6..0x5F2A` while accounting for the 126 unassigned bytes and naturally preserving the PC-relative edges `F_5EC0 → F_5C42`, `F_5EC0 → F_41F6`, `F_5D14 → F_5C42`, `F_5C42 → F_5962`, and `F_5962 → F_5C42`. If the worker only closes `0x5962..0x5F2A`, that recovers the dependency cluster but does not by itself satisfy the current admission metric for `F_5EC0`.
