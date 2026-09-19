# Direct reconstruction pass

These candidates were authored directly from bounded function evidence and
tested with the historical worker. No local or hosted proposer was invoked.
The permanent receipt is `evidence/experiments/direct-recovery.json`.

Eleven functions match completely under aztec36, adding 1,154 FUNCTION_CODE_MATCH
bytes: ov09_F_18D0 (84), ov08_F_3FC0 (88), ov08_F_4018 (96), ov10_F_2BCA
(136), ov11_F_69A4 (160), ov07_F_0EC0 (112), ov11_F_5A12 (80), ov11_F_5BC4
(86), ov09_F_1956 (126), ov07_F_0E7C (68), and ov07_F_0E06 (118). Canonical
source is in src/recovered.
Descriptive local/field names are interpretation; original identifiers and full
global allocations are not claimed. Extern bounds supply independent harness
storage, not a proof of the original objects' complete sizes.

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

The two ov14 selector hypotheses remain unpromoted. Aztec 3.6a generates the
expected bodies plus a two-byte EXT.W on explicit char return. Tested 5.0a-short
also differs. No expression-fallthrough trick was substituted for explicit return
semantics. Their compiler outputs and failed comparisons remain in the ledger.

These are function matches only, not module or overlay layout matches.
