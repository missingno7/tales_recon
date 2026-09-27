# ov11_F_583A dependency audit

No new compile was run. The requested precondition failed because this candidate has a deeper unrecovered same-overlay dependency chain with a documented cyclic source-layout blocker.

## Target facts

The existing ranked row for `ov11_F_583A` reports `CLOSED_CFG`, 296 bytes, confidence HIGH, state `CODEGEN_SIMILAR`, one call, one unknown call, and `pending_local_dependencies: [ov11_F_5962]`. The function ledger places it at `0x583A..0x5962` (exclusive end), with its single direct call at `0x593E` / decimal 22846 targeting `ov11_F_5962` at `0x5962`. It also has one A4-relative data reference at instruction offset `0x5926` to hunk 1 offset 35612. Thus it satisfies the ≤512-byte CLOSED_CFG extent condition, but not the no-deeper-unrecovered-local-dependency condition.

## Dependency chain and first gate

`ov11_F_583A` → `ov11_F_5962` → `ov11_F_5C42` (pending, BLOCKED). `ov11_F_5962` also calls `ov11_F_66FE`, which is already present at `src/recovered/ov11/ov11_F_66FE.c`.

The curated recovery blocker for both `ov11_F_5962` and `ov11_F_5C42` is `CYCLIC_INTER_OBJECT_PC_CALL`. It says the compact cluster shortens `F_h11_5C42 → F_h11_4696` to `BSR.b`, while ordinary earlier-object linking proves the historical backward `JSR.d16(PC)` survives without padding or copied bytes. The exact displacement and A4/global placement require recovering and linking the full physical ov11 interval `0x4790..0x5962` in source order: 858 canonical bytes, seven discovered unrecovered functions totaling 3664 bytes, plus 40 unclaimed bytes. The blocker explicitly says not to retry either isolated member.

This is the first concrete gate; it is a physical interval/layout proof requirement rather than an extent or CFG failure on `F_583A`. A new isolated Aztec36 attempt on `F_583A` would not satisfy the requested dependency precondition and would repeat work without resolving the downstream blocker.

## Existing target attempts (context only)

The recovery ledger already has three Aztec36 attempts for `ov11_F_583A`; all are `DIFFER` / `CODEGEN_SIMILAR`, expected 296 bytes versus actual 298 bytes, mnemonic similarity 0.9882. Their first raw differences were at offset 23 (attempts `6deb288a…` and `fafd0408…`) and offset 209 (`528572f0…`). No new hypothesis or verifier run was made for this task.

Recommendation: do not retry isolated `ov11_F_583A`; resolve the documented `0x4790..0x5962` ordered interval/layout blocker first. This report makes no proof or promotion claim.
