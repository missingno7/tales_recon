# ov07_F_0000 prerequisite and ownership audit

Scope: read-only analysis of the 900-byte `ov07_F_0000` candidate. No reconstruction candidate was compiled, no canonical source/proof/ledger was changed, and no original bytes were copied into a source output.

## Extent and direct-call map

`evidence/functions/ledger.json` validates `ov07_F_0000` as a 900-byte (`0x0000..0x0384`) HIGH-confidence `CLOSED_CFG` function in hunk 7 / ov07. It has a 20-byte A5 frame, 32 CFG edges, no indirect control flow, no boundary stops, and no undecoded gaps. It has 46 direct call sites across 21 unique targets: 36 calls through 17 resident A4 stubs and 10 PC-relative same-overlay calls.

| Direct target | Call sites | Evidence state / consequence |
|---|---|---|
| `resident_F_435E` | `+0x00C` | Resident A4 trampoline |
| `resident_F_57D2` | `+0x012,+0x112,+0x182,+0x1D8,+0x226,+0x334` | Resident A4 trampoline |
| `resident_F_0FDE` | `+0x01C,+0x09A` | Resident A4 trampoline |
| `resident_F_291E` | `+0x02A,+0x07E,+0x0E2` | Resident A4 trampoline |
| `resident_F_8A46` | `+0x052` | Resident A4 trampoline |
| `resident_F_86DC` | `+0x0A8` | Resident A4 trampoline |
| `resident_F_2816` | `+0x0B6,+0x108` | Resident A4 trampoline |
| `resident_F_868C` | `+0x0F8` | Resident A4 trampoline |
| `ov07_F_1424` | `+0x120` | Direct local call; unresolved target extent/control flow |
| `ov07_F_03CC` | `+0x136,+0x1AA,+0x200,+0x252` | CLOSED_CFG, existing `FUNCTION_WITH_DATA_MATCH` |
| `ov07_F_04AC` | `+0x142,+0x1B6,+0x20C,+0x25E` | CLOSED_CFG, existing `FUNCTION_WITH_DATA_MATCH` |
| `resident_F_307C` | `+0x148,+0x1BC,+0x212,+0x264,+0x30C` | Resident A4 trampoline |
| `resident_F_31AA` | `+0x158,+0x31C` | Resident A4 trampoline |
| `resident_F_4376` | `+0x16A` | Resident A4 trampoline |
| `ov07_F_0612` | `+0x1A0` | Direct local call; unresolved target extent/control flow |
| `resident_F_86A8` | `+0x21A,+0x26C` | Resident A4 trampoline |
| `resident_F_330E` | `+0x28A,+0x308` | Resident A4 trampoline |
| `resident_F_0640` | `+0x29A` | Resident A4 trampoline |
| `resident_F_35DC` | `+0x2B2,+0x2CC,+0x2E6,+0x300` | Resident A4 trampoline |
| `resident_F_134C` | `+0x326` | Resident A4 trampoline |
| `resident_F_3AE4` | `+0x36E` | Resident A4 trampoline |

The immediate unresolved same-overlay closure is `F_1424` and `F_0612`. `F_1424` is 1090 bytes and `UNCERTAIN`/LOW: one unresolved indexed PC-relative jump (`$1824(pc,d0.w)`) and undecoded gaps. It has no local direct callees in its discovered call list. `F_0612` is 1684 bytes and `UNCERTAIN`/LOW: two unresolved indexed PC-relative jumps (`$818(pc,d0.w)` and `$c36(pc,d0.w)`) plus undecoded gaps; its local calls include recovered `F_0E06`, `F_0E7C`, `F_0EC0`, and `F_18F8`, plus unrecovered `F_0F30`. `F_0F30` itself is a 1268-byte HIGH-confidence `CLOSED_CFG` candidate with no local calls or indirect jumps, but remains `DISCOVERED` (not a source match). Therefore `F_0612` needs its own closed body/table ownership proof and a separate complete `F_0F30` match; the recovered callees do not close those gates.

## PC-relative literals and relocation references

`tools/owned_code_data.py::expected_string_tail` succeeds for the five same-hunk PC-relative data targets. It proves one contiguous 72-byte tail at `0x384..0x3CC`: 71 bytes of five NUL-terminated ASCII literals followed by one immutable zero byte of word-alignment padding. The next discovered function entry is exactly `ov07_F_03CC` at `0x3CC`, so the tail has an exact ownership boundary. Reference sites and targets are:

| Instruction | Target / literal |
|---|---|
| `+0x0A4` | `0x384`: `DT1:invart.arc` |
| `+0x2A6` | `0x393`: `I'll put that` |
| `+0x2C0` | `0x3A1`: `order through` |
| `+0x2DA` | `0x3AF`: ` right away,  ` |
| `+0x2F4` | `0x3BE`: ` Mr. McDuck!` |

The extent excludes this tail from the 900-byte code body; candidate source could claim it only as separately proven compiler-owned CODE data. The asset name and dialogue are evidence, but do not by themselves establish a source filename or semantic label.

There are zero HUNK relocation records inside `F_0000`. Its recorded A4-relative data references are in hunk 1: 63 references to 30 unique offsets. Seventeen offsets map to resident relocated-JMP stubs (the direct-call groups above); the other 13 remain untyped A4 data/table addresses: `0x0A92`, `0x1466`, `0x1766`, `0x3232`, `0x323A`, `0x323C`, `0x3242`, `0x329E`, `0x33E2`, `0x46CE`, `0x46D2`, `0x46D6`, `0x46DA`. These are unresolved source-level globals/table shapes, not demonstrated ownership of bytes adjacent to the function. No A4 target is part of `F_0000`'s owned tail.

## Likely source-shape blocks and first gate

The decoded body is structurally closed but not a small leaf: it has 32 explicit CFG edges, multiple conditional branches and joins, a backward edge, and repeated helper/callee sequences. Four separate paths pair calls to `F_03CC` and `F_04AC` (at `0x136/0x142`, `0x1AA/0x1B6`, `0x200/0x20C`, `0x252/0x25E`), with nearby repeated resident calls to `F_307C`. The most defensible source-shape hypothesis is a branch-heavy overlay operation with repeated draw/format or item-processing blocks, a setup/auxiliary call to `F_1424`, and a later `F_0612` path; exact names and user-visible semantics are not proven. The string tail suggests an investment/order message path, but does not prove that all 900 code bytes implement only that dialogue.

**First concrete gate to a complete unit:** close the called `F_1424` and `F_0612` extents, especially resolving their indexed jump tables and the undecoded regions; then prove/compare their local closure including `F_0F30`. Only after that is it meaningful to attempt a full-unit candidate for `F_0000`. Its external-call and owned-string evidence are already bounded; its A4 data targets still need types/layout before a faithful C shape can be composed.

## Verification

Read-only checks: `validated_function('ov07_F_0000')` passed; `expected_string_tail` passed with `start=900`, `end=972`, `alignment_padding=1`; next hunk-7 entry is `ov07_F_03CC` at `0x3CC`. No compiler or verifier candidate run was performed. This report and the scratch audit scripts are confined to `experiments/worker-ov07-0000-audit/`.
