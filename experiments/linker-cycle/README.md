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

`tools/cycle_gap_codegen_experiment.py` records the two standalone latent
candidate results. Both have exact lengths and mnemonic sequences under aztec36,
but their A4/global and external binding fields still require the complete source
layout, so neither changes recovery ownership.

`tools/cycle_cluster_experiment.py` compiles the 1,080-byte cluster spanning
the recovered bridge, reciprocal pair, five recovered intervening functions,
and both latent windows. Its receipt classifies every remaining difference as
A4 placement, forward external binding, or a PC-relative displacement caused by
the omitted physical layout. It is still strictly non-promoting evidence.

`tools/cycle_cluster_extended_experiment.py` adds the two forward callees to
that same normal source unit. The previously external call from `F_5962` is now
PC-relative. `F_5C42` reaches its nearby forward callee with a two-byte `BSR`
where the original physical layout used a four-byte PC-relative `JSR`, making
the unit two bytes shorter. The result retains only A4 and source-layout call
encoding/displacement differences. Its 1,394-versus-1,392-byte receipt is
strictly non-promoting and records the compact-layout effect rather than hiding
it with padding or placement directives.

`tools/cycle_layout_gap_audit.py` makes the remaining physical interval
explicit. Between `0x4790` and `0x5962`, 858 bytes already have canonical
function receipts, seven discovered candidates account for 3,664 unrecovered
bytes, and a 40-byte interval at `0x5174` remains unclaimed. The retained
frontier receipt does not classify that interval or add any layout filler; it
only supplies the source-order plan required before the cluster can be tested
as a complete natural unit.
