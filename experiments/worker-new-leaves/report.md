# New leaves experiment

The ranked queue had one eligible target outside ov03, ov07, ov11, ov14, and resident: `ov08_F_1AB8` (114 bytes, `CLOSED_CFG`, `DISCOVERED`, score 594, no indirect control flow, one unknown call, pending same-node dependency `ov08_F_354E`).

Candidate: `ov08_F_1AB8_v1.c`.

`python tools/check_function.py ov08_F_1AB8 experiments/worker-new-leaves/ov08_F_1AB8_v1.c --profile aztec36 --no-promote --json` returned `BLOCKED` / `SOURCE_REJECTED`, expected length 114, actual length null, cache key `9446e05ae49e919dfc99b66c87ddc61d245a62e6449c22e2c7eb6abd503a9c5f`. No first byte mismatch exists because validation stopped before compilation. The concrete proof blocker is the unrecovered same-node dependency `ov08_F_354E`; validation also rejected the unbounded extern array declaration. No source was promoted.

The original transient receipt was `recovery/attempts/ov08_F_1AB8/1965c550966739beb080fc3935ed5066b5d90abe15ebae71596ade89b72623c7-aztec36-9446e05ae49e-c989caac244f.json`; it was removed with the verifier scratch state after recording its exact verdict here.
