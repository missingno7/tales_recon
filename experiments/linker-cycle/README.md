# Reciprocal external-call linker probe

This isolated Aztec 3.6a experiment measures a reciprocal pair of ordinary
candidate C objects. It does not read or mount the game.

The worker compiles the same pair and links it four ways: one `+o9` selector,
a repeated `+o9` selector, a library, and the same library listed twice. Every
guest command succeeds. Every resulting executable has the same hash and call
encodings:

- the forward `F_h11_5962 -> F_h11_5C42` call is PC-relative (`4eba002c`);
- the backward `F_h11_5C42 -> F_h11_5962` calls are A4-relative
  (`4eac8016`), whereas the original has PC-relative JSRs.

The machine-readable receipt is
[`evidence/experiments/linker-cycle.json`](../../evidence/experiments/linker-cycle.json).
It is evidence for the cyclic inter-object-call blocker, not a reconstruction
or a substitute for a normal whole-module link.

`tools/cycle_gap_audit.py` separately records the two unclaimed windows between
the pair and their surrounding recovered functions. Both decode as `LINK...RTS`
code, but have no allowed discovery seed, so the audit retains them as latent
layout evidence and never counts them as recovered functions.

`tools/cycle_prefix_experiment.py` compiles the `F_5962` prefix plus the first
latent loop as one normal source object. It records the exact-length mnemonic
match and the remaining A4/external-call binding differences in
`evidence/experiments/linker-cycle-prefix.json`; this also remains non-promotable
until a complete natural module layout explains those references.
