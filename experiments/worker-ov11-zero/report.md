# ov11_F_3B92 byte extension and compact-unit audit

All new files for this bounded audit are under `experiments/worker-ov11-zero/`. The compiler outputs are retained in `build/compile-cache/`; canonical recovery state and ledgers were not edited by this worker.

## Result

The `BYTE_ZERO_EXTENSION_CODEGEN_MISMATCH` label does not describe the remaining mismatch in the closest retained compact-unit candidate. Its target contribution is 520 bytes and contains the expected `MOVEQ #0,D0` instructions at function-relative offsets 290 and 354. Replacing the source `+ 0` expression with explicit `(int)` or `(unsigned int)` casts leaves those target bytes unchanged. Direct assignment from the unsigned-byte field omits the clears and produces a 510-byte standalone contribution. The fingerprint note in `docs/grinder-pipeline.md` describes only its four earlier microprobes; the full retained source context changes the outcome.

The closest old compact-unit receipt is `recovery/units/ov11_F_3B92/ace3d42a0435e49b8fc46adb4c3c468f96f1ee0dec8147884952284661fb86c1/db074829201a39bf/receipt.json`: Aztec 3.6a, expected 1048 bytes, actual 1052, a 4-byte excess. Symbol starts in the separate-object replay are 0, 34, 92, 160, 680, and 802 for F25D6, F25F8, F37A0, F3B92, F40E0, and F4696. F25F8 therefore spans 58 bytes (34–92), while its expected and standalone-proven contribution is 54 bytes. F37A0 is exactly 68 bytes (92–160); my earlier message attributing the excess to F37A0 was incorrect.

The +4 has a concrete link-layout cause. In the separate-object replay, F25F8's two calls to its immediately preceding direct callee F25D6 are four-byte `JSR` instructions at function offsets 16 and 38 (`4ebaffcc`, `4ebaffb6`). Joining the adjacent F25D6/F25F8 pair as one ordinary source object lets the normal linker resolve both to two-byte `BSR.B` instructions (`61cc`, `61b8`). The F25F8 byte span then becomes exactly 54 bytes and equals the expected bytes. The complete compact link becomes 1048 bytes; F25D6, F25F8, F37A0, F40E0, and F4696 compare equal. This is ordinary object context, not a compiler flag.

F3B92 still fails after that join. Its normalized first mismatch is the 16-bit displacement at byte offset 84: the `bne.w` at offset 82 targets original internal offset `0x1f6` (`660001a2`), while the candidate targets `0xf0` (`6600009c`). The instruction mnemonics/sizes otherwise align, relocation issues are empty, and mnemonic similarity is 1.0. Joining F25D6/F25F8 moves F3B92's start from 160 to 156 but leaves this internal branch instruction and target unchanged. Thus fixing the preceding +4 does not correct F3B92's branch target.

## Bounded hypotheses

- Direct unsigned-byte assignment: no `MOVEQ #0,D0`; standalone length 510 under Aztec 3.6a and 3.6a `+X3`.
- `+ 0` in the retained source: full target is 520 bytes and has both expected `MOVEQ` instructions, but normalized branch offset 84 differs.
- Explicit `(int)` and `(unsigned int)` casts on the same extracted byte: same target bytes as `+ 0`; no change to the first normalized mismatch.
- The byte-copy/cast probes compiled under 3.6a, 3.6a `+X3`, 5.0a, and 5.0a `-ps` show that promotion can produce `MOVEQ #0,D0` in each profile. They do not point to a shared undocumented compiler switch. The full compact source supplies a normal expression path for the opcode.
- Adjacent F25D6/F25F8 object grouping: removes exactly the two four-byte external-call encodings and restores the F25F8 byte span; does not change the F3B92 branch displacement.

## Intermediate blocker

Recover the control-flow/source expression around F3B92's guard at offset 82 and prove why the false edge must skip to internal offset `0x1f6`, not `0xf0`. Keep the joined F25D6/F25F8 object context in the exact-unit verifier, then test source-level guard/loop structure candidates there. Further byte-cast variants are low value until that branch target is understood.

Machine-readable details and replay helpers are in `cause-and-context.json`, `final-cause-and-branch.json`, `f25f8-span.json`, `compact-unit-results.json`, and the adjacent Python scripts.

## Branch-control-flow follow-up

The offset-82 branch was a source-nesting difference, not a compiler-mode difference. Starting from the closest retained `+0` candidate and keeping the proven joined F25D6/F25F8 object context:

- Moving only the `count1c`/switch block under `if (event->value4 == 1)` changes the branch destination from `0xf0` to `0x1c6`, but leaves the common `work16/work1a/work14/work18` history updates outside the outer guard.
- Moving those four work-field updates under the same outer guard as well changes the branch to `0x1f6`, matching the oracle's `bne.w` bytes `660001a2` at function offset 82.

The second source form passes the strict complete-unit comparator: 1048 code bytes, `ENTIRE_OBJECT_AND_ALL_MEMBER_CONTRIBUTIONS`, with all six functions equal. The worker retained its isolated candidate at `nested_outer_guard_and_updates.c` and the machine-readable exact result at `nested-guard-and-updates-result.json` (Aztec 3.6a, cache key `71af3f34444521e9f48df3ce43d629067859ec436d2e989ee6ba7e87a4870ea1`). The supervisor then reran the canonical `check_unit.py` gate with separate objects, original gaps preserved, and the adjacent direct-callee pair joined. That gate also returned EQUAL and promoted `ov11_F_3B92`; its authoritative proof is `recovery/proofs/ov11_F_3B92.json`.

The source-supported reconstruction is that `event->value4 == 1` encloses the screen/collision work, count/switch processing, and the four history-field updates. This closes the branch discrepancy while retaining the earlier natural F25D6/F25F8 link context.
