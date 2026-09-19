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
