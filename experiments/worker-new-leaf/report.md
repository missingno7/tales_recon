# ov11_F_13DC isolated recovery trial

## Selection and gate

Selected `ov11_F_13DC` from the existing ranked queue: 222 bytes, `DISCOVERED`, `CLOSED_CFG`, outside excluded overlays, and not previously attempted/promoted. It is a small leaf-like control-flow shape with no indirect control or PC-relative data, but has six direct same-overlay calls: three to `ov11_F_4696` and three to `ov11_F_583A`. `ov11_F_4696` is recovered; `ov11_F_583A` is not. The strict unit gate reports `unrecovered same-node dependency: ov11_F_583A`.

## Best candidate and exact result

Best candidate: [ov11_F_13DC_r4.c](ov11_F_13DC_r4.c)

Verifier: `python tools/check_function.py ov11_F_13DC experiments/worker-new-leaf/ov11_F_13DC_r4.c --profile aztec36 --isolated --output-dir experiments/worker-new-leaf/verifier-r4 --json`

Receipt: [verifier receipt](verifier-r4/ov11_F_13DC/f4753f53de08cb12548a63694d4848c719f716d558203f16abb99e9506f0cd31-aztec36-e5e8b06eb3e0.json)

Exact verdict is `DIFFER` / `CODE_OR_REFERENCE_DIFFERS`: 222 expected bytes, 222 actual bytes, Aztec 3.6a (`aztec36`), mnemonic similarity 1.0, no structural instruction difference, `relocation_equal=false`, `proof_level=null`. All 20 A4 D16 symbol references normalize to their historical identities. First normalized mismatch is offset 45, at the first direct call: expected `jsr $32ba(pc)` to `ov11_F_4696`; actual `jsr -$7ffe(a4)`. The six PC-relative direct-call bindings remain unproven at offsets 44, 72, 114, 142, 182, and 210. The separate unit-gate blocker is the unrecovered `ov11_F_583A` dependency.

## Bounded hypotheses tried

1. Initial shape had a spurious `slot == 12` guard and G_9FB6 assignment, plus guessed globals. It compiled to 238 bytes and diverged at offset 4.
2. Removed the unrelated guard/store and modeled the observed pointer comparison; 222 bytes, but scalar `long` globals generated `move.l/cmp.l` instead of required address-register operations.
3. Changed compared globals to pointer types; instruction shape matched (222 bytes, similarity 1.0), but call argument references still used offsets borrowed from a different function.
4. Corrected the two call arguments to target references G_h01_94C4 and G_h01_94C2. Instruction shape and all A4 identities matched, but direct-call relocation identity remained unproven as detailed above.

No fifth variant was attempted: the remaining mismatch is a proof/identity gate, not a C shape issue. Recommend recovering/proving `ov11_F_583A` and its call binding before retrying this target; do not promote this candidate or claim fixture-proposer success.
