# Direct reconstruction pass

These candidates were authored directly from bounded function evidence and
tested with the historical worker. No local or hosted proposer was invoked.
The permanent receipt is `evidence/experiments/direct-recovery.json`.

`ov13_F_0000` adds 302 exact bytes under aztec36. Its normal C state layout
models only the A4 fields reached by the routine; the receipt proves every
field addend, five resident call identities, and the complete code extent.

`ov13_F_0190` adds another 302 bytes as a three-function natural source unit
with `ov13_F_0000` and the recovered bridge `ov13_F_012E`. Its receipt proves
all 702 bytes of that unit, including four same-overlay calls and every local
and resident reference identity.

`ov13_F_0746` adds 508 exact bytes outside that unit. It selects a measured
draw origin, then performs four normal C rendering passes through verified
resident helpers. Its receipt proves all 35 global/reference identities.

Twenty functions match completely under aztec36, adding 4,510 FUNCTION_CODE_MATCH
bytes: ov09_F_18D0 (84), ov08_F_3FC0 (88), ov08_F_4018 (96), ov10_F_2BCA
(136), ov11_F_69A4 (160), ov07_F_0EC0 (112), ov11_F_5A12 (80), ov11_F_5BC4
(86), ov09_F_1956 (126), ov07_F_0E7C (68), and ov07_F_0E06 (118). Canonical
source is in src/recovered.
Descriptive local/field names are interpretation; original identifiers and full
global allocations are not claimed. Extern bounds supply independent harness
storage, not a proof of the original objects' complete sizes.

`ov08_F_1C30` adds 274 exact bytes: a five-row digit display loop. The source
uses a normal long pointer expression to retain the historical `MULS`/address-add
sequence, and its receipt proves all thirteen A4 global and resident-call
identities.

`ov10_F_1FDE` adds 386 exact bytes: a 3x3 rendering helper with four
flag-controlled edge calls. Its normal C loop and bitfield test retain every
resident/global reference identity through the historical compiler.

`ov15_F_0A80` adds 402 exact bytes: a rectangle-outline helper. Four ordinary
C draw passes produce the matching edge endpoints and every global/resident
reference identity through aztec36.

The later direct `ov03_F_154E` distance-ranking recovery adds 498 exact bytes.
It uses the independently resolved `G_h01_4524` table, six natural resident
helper calls, and the proved compiler-emitted signed division helper. Two
unreferenced stack-frame words remain explicitly unknown rather than given
semantic names. Its canonical receipt records all eleven reference identities.

The later `ov10_F_320C` guarded dispatcher adds 124 exact bytes. Its union
layout follows the observed overlapping word and second-byte accesses; nine
resident/global reference identities are independently resolved in its receipt.

`ov11_F_727A` now supplies the first independently reconstructed initialized
DATA trial: 64 fixed-point sine samples are emitted as a normal C global and
their 128-byte linked DATA contribution matches exactly. All tested compiler
profiles still address that global through A4, while the game uses a six-byte
absolute HUNK relocation, so this remains a retained codegen blocker rather
than a function promotion.

The later `ov06_F_028C` decimal counter animation adds 414 exact bytes. It
builds two right-to-left digit buffers from signed long values, renders them
with the observed draw/present/delay sequence, and naturally emits the proved
signed modulo and division helpers. Reordering the 30-byte local frame was the
only revision needed after the initial same-length, same-mnemonic trial.

`ov11_F_20F2` is the first `FUNCTION_WITH_DATA_MATCH`: a 230-byte parser for
an `L` header and 14-byte rows, followed by two source-owned format strings
and one required Aztec word-alignment byte (32 bytes total). The literal extent
ends exactly at the next discovered function entry. Its receipt proves the
two PC-relative references, eight resident calls, the record-table A4 identity,
and the matched `.divs` runtime contribution.

`ov11_F_3926` is a second `FUNCTION_WITH_DATA_MATCH`: a 230-byte parser for
an `F` header and 32-byte indexed records. Its three contiguous format strings
add 24 exact CODE bytes. The exact source declares the observed field offsets,
including the intentionally non-source-order scan arguments needed to match the
historical ABI.

`ov11_F_506A` and `ov11_F_67B0` extend the same strict proof to 40-byte `P`
and `S` record parsers. They contribute respectively 266 code bytes plus a
40-byte literal tail, and 228 code bytes plus a 28-byte literal/padding tail.
Both tails end exactly at the next discovered entry; each receipt proves all
PC-relative literal and A4 reference identities.

`ov11_F_2C96` adds a 260-byte `M` record parser and 32-byte literal tail. Its
second literal is the short `"%d "` format. The function census now records a
short literal only when an explicit PC-relative reference reaches an
ASCII/NUL-terminated payload; the unchanged tail verifier still requires every
reference, every tail byte, and the next entry boundary to match exactly.

`ov11_F_7194` adds a 210-byte `X` record parser and a 20-byte three-literal
tail. Its ten-byte indexed records show the same historical scan/error/advance
shape in a smaller form, and the tail reaches the next discovered entry exactly.

`ov11_F_6A44` is the first larger multi-section match in this family: its
448-byte function body parses `V` 34-byte records and `J` word records, then
owns all six contiguous literals (54 bytes) before the next entry. The normal
source contribution resolves all 18 resident/global identities exactly.

The ov07 percentage lookup uses 31-byte rows. A struct containing 31 chars is
rounded to 32 bytes by Aztec; an ordinary two-dimensional unsigned-char array
produces the observed multiply by 31. The harness now accepts positive constant
array dimensions without placement or changes to comparison normalization.

`ov07_F_03CC` proves the complementary PC-relative string-tail path. Its normal
aztec36 output has the exact 182-byte instruction body, all external A4
identities, and the exact adjacent 42-byte string contribution. Its two local
calls target recovered `ov07_F_0E06` and `ov07_F_0E7C`, but the intervening
overlay bytes are not yet owned by a complete source unit. The checker therefore
retains it as an inter-object-call blocker instead of replacing the direct calls
with synthetic A4 harness stubs.

The two ov14 selector hypotheses remain unpromoted. The measured return matrix
in `evidence/fingerprints/index.json` shows that installed Aztec 3.6a emits
`EXT.W` for signed and integer byte returns, clears `D0` for an unsigned-byte
return, and adds `EXT.L` for a long return; none reproduces the bare byte return
in the game. The linked caller consumes only `D0.b`. This is retained as the
`BYTE_RETURN_ABI_MISMATCH` toolchain blocker. No expression-fallthrough trick
was substituted for explicit return semantics, and no source ownership changed.

`ov11_F_6F78` adds 134 exact bytes through the normal `aztec36` compiler. The
fingerprint-derived `return index>0 && scale>distance(...)` form gives the
observed short-circuit branches and final Boolean return layout. Its direct
same-overlay call is proved by a normal two-object link with recovered
`ov11_F_2562`: every one of the compact 250 source-owned bytes matches and the
linker resolves the PC-relative target identity. The unrelated original gap
between those functions remains unclaimed.

`ov11_F_3F90` adds 202 exact bytes through a normal two-object `aztec36` link
with recovered `ov11_F_25D6`. Its 32-byte event layout, local-frame declaration
order, right-to-left call argument order, and variable shift are all derived
from the complete function extent. The compact proof matches all 236 source-owned
bytes and every A4/call identity; the original gap between the two objects remains
unclaimed.

`ov11_F_70DC` adds 158 exact bytes through two normal source objects: the
contiguous `ov11_F_25D6`/`ov11_F_25F8` helper pair and the contiguous
`ov11_F_70DC`/`ov11_F_717A` update pair. This preserves the historical short
local branches while keeping the 19 KiB original gap between those pairs
unclaimed. The 272-byte compact proof matches every member, all six A4 globals,
and all three direct-call identities.

These are function matches only, not module or overlay layout matches.
