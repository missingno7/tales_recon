# ov08_F_1D42 signed-byte trial r5

Only the declaration of `G_h01_46E1` changed relative to r4, from `unsigned char` to `char`, following the target's sign-extending byte loads and the prior `bge` versus `bcc` mismatch.

Isolated Aztec36 verdict: `DIFFER` / `CODE_OR_REFERENCE_DIFFERS`. Expected length 522 bytes; actual length 522 bytes; mnemonic similarity 0.9869; `relocation_equal=false`; `proof_level=null`.

First structural mismatch: offset 390 (`+0x186`), expected `moveq #$0,d0` (2 bytes), absent in candidate (delete). The earlier `bge` versus `bcc` difference is no longer the first structural mismatch. First normalized byte mismatch remains offset 6 in the prologue A4 displacement (`d372` expected versus `804e` actual); layout mismatch prevents A4 identity proof (`INSTRUCTION_LAYOUT_DIFFERS_FOR_SYMBOL_PROOF`).

Receipt: `verifier-rectfill-r5/ov08_F_1D42/d6d10dea9fa35bc93a960715354e649b4644c538c48eb3a6d1ea2739903f2965-aztec36-755f7d3babbf.json`.

This is the single requested r5 run. Stop here regardless of verdict; no canonical edits or promotion.
