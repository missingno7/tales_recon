# ov08_F_1D42 guard-removal follow-up r4

The r3 source and target CFG around `+0x194` show one identifiable extra guard. Target control flow executes the first `F_h00_09C0(168,174,...)` text call, then compares the byte against 10 at `+0x1b4` to choose a second call. R3 instead put both calls under an outer `if (G_h01_46E1 < 10)`, adding a comparison before the first call. R4 removes only that outer guard and keeps the nested choice.

Candidate: `ov08_F_1D42_rectfill_r4.c`.

Verifier: `python tools/check_function.py ov08_F_1D42 experiments/worker-ov08-1d42/ov08_F_1D42_rectfill_r4.c --profile aztec36 --isolated --output-dir experiments/worker-ov08-1d42/verifier-rectfill-r4 --json`.

Exact result: `DIFFER` / `CODE_OR_REFERENCE_DIFFERS`; expected 522 bytes, actual 518; mnemonic similarity 0.9737; `relocation_equal=false`; `proof_level=null`. The added pre-call compare/branch is gone. First structural mismatch is at byte offset 442 (`+0x1ba`): expected `bge.b $1e2`, candidate `bcc.b $1e0`. The candidate's epilogue is four bytes earlier. The first raw mismatch remains the unnormalized A4 displacement at offset 6 (`INSTRUCTION_LAYOUT_DIFFERS_FOR_SYMBOL_PROOF`).

Receipt: `verifier-rectfill-r4/ov08_F_1D42/3bba49712c9b3fec0580b60293b1379df51c21eb78b2c7d3085f92947c06a3a2-aztec36-6fda143b2dd0.json`.

The branch-condition difference is consistent with the candidate declaring `G_h01_46E1` as `unsigned char`, while the target uses sign-extending byte loads and a signed `bge`. This is a concrete next source-level hypothesis, not a proven type identity. Per the one-variant limit, no second compile was run. No canonical edits or promotion.
