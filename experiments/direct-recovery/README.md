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

The ov07 percentage lookup uses 31-byte rows. A struct containing 31 chars is
rounded to 32 bytes by Aztec; an ordinary two-dimensional unsigned-char array
produces the observed multiply by 31. The harness now accepts positive constant
array dimensions without placement or changes to comparison normalization.

The two ov14 selector hypotheses remain unpromoted. Aztec 3.6a generates the
expected bodies plus a two-byte EXT.W on explicit char return. Tested 5.0a-short
also differs. No expression-fallthrough trick was substituted for explicit return
semantics. Their compiler outputs and failed comparisons remain in the ledger.

These are function matches only, not module or overlay layout matches.
