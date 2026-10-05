# Current handoff - 2026-10-05

This is a validated consolidation checkpoint. The original requested pass is
not complete: AJ/FFP private-helper binding, live runtime-trace ingestion, and
the remaining legacy workflow/documentation audit still have open gates.

Canonical coverage remains 149 functions / 38,604 C bytes. The generated
`progress.json` is the measurement authority. Whole-file accounting has 982
compiler-owned data bytes, 430 pinned runtime bytes and 152,988 file bytes of
RAW_ORACLE_DEBT (including 6,680 structural bytes). Allocation-only zero fill
is separate. Accounting grants no new reconstruction proof.

## First closure campaign: ov04

There are 24 known closed-CFG functions, 21 canonical functions / 6,942 C bytes,
520 compiler-owned data bytes and 3,306 initialized debt bytes.
`../evidence/closure/ov04.json` lists canonical and remaining function identities;
`../evidence/hybrid/accounting.json` contains the complete ownership partition.

| Remaining function | Extent | Size | First blocker experiment |
| --- | --- | ---: | --- |
| ov04_F_0536 | 0536..07A4 | 622 | SOURCE_SHAPE / return-width control |
| ov04_F_1302 | 1302..149C | 410 | SOURCE_SHAPE, then independently bind callers |
| ov04_F_1E36 | 1E36..252E | 1784 | SOURCE_SHAPE / DATA_OWNERSHIP, bounded literal proof |

Unowned initialized ranges are 0536..07CA, 1302..149C, 1E36..26F0 and
2A0E..2A10. Besides the 2,816 known function bytes, 490 bytes still require
independent data/padding/boundary ownership. The accounting partition does not
classify these gaps by guessing. No ov04 pinned runtime contribution is proved.
Resolve relocations against independently established target identities, and
review separately compiled source/object ordering. Existing accepted grouping
receipts constrain historical hypotheses without establishing original TUs.

Exit gate: every initialized byte independently explained; all game-owned
C/ASM reconstructed; compiler literals/data proved; runtime contributions
identified or independently separated; all relocations/layout reproduced by
the ordinary historical overlay link; zero ov04 RAW_ORACLE_DEBT. An accounting
image assembled with oracle debt cannot satisfy this gate.

## Top five blockers by leverage

1. ov04 remaining closed functions: recover the three extents above.
2. ov04 data ownership and object order: account for the additional 490 bytes,
   then test a natural overlay link. Categories DATA_OWNERSHIP / OBJECT/TU_LAYOUT.
3. AJ/FFP external identities: controlled AJ specimens now establish a bounded
   external-word grammar and natural PC binding. The real FFP object still uses
   unsupported records. Extend only with positive/negative specimens, consume
   the proved identities in the strict verifier, and leave ov11_F_5FB2 blocked
   until private helpers resolve independently. Category CALL_BINDING.
4. Indirect control flow: the small WinUAE pipe history collector and bounded
   event validator exist, but no live-game trace/overlay-load adapter has been
   validated. Establish a load epoch and a genuine single-step edge, then
   return to static table/extent proof. History adjacency is only a candidate
   edge, and an observed target never proves completeness. Category CFG/BOUNDARY.
5. Declaration/object isolation: verify actual dependency units with distinct
   compatible partial views and explicit same-object conflict controls.
   Compiler-identity changes leave several old cache controls skipped until
   rerun. Categories DECLARATION_VIEW / OBJECT/TU_LAYOUT.

## Normal worker commands

```powershell
python tools/grinder.py rank --node ov04 --limit 5
python tools/grinder.py facts ov04_F_0536 --max-instructions 1000 --max-bytes 150000
# Write candidate to build/workers/NAME/candidate.c, then diagnose locally.
python tools/check_function.py TARGET build/workers/NAME/candidate.c --profile aztec36 --isolated --no-promote
# After an exact result, promote the unchanged candidate.
python tools/check_function.py TARGET build/workers/NAME/candidate.c --profile aztec36
# Existing batch alternative for independent promotions:
python tools/promote_batch.py build/workers/wave.json --verify-only
python tools/promote_batch.py build/workers/wave.json
```

Dependencies compile as separate objects by default. `--object-group` is an
evidence-backed hypothesis; arbitrary canonical concatenation is not a default.
Only expose declarations needed by the candidate TU. No universal struct
merger or inferred shared header is an authority. Ranking favors closure and
caller unlocks; report a blocker category and smallest changed experiment on
failure rather than repeatedly spawning the same hypothesis.

## Validation and assumptions

```powershell
python tools/type_evidence.py --write
python tools/census.py --write
python tools/census.py --check
python tools/hybrid_image.py --check
python -m unittest discover -s tests -v
# Re-derive produced specimens only with the validated historical caches/tools:
python tools/hybrid_image.py --refresh --write
```

Latest check: 373 tests passed, 9 skipped (local compilation-cache controls and
an already-canonical promotion control). Census validates all 149 canonical
proofs. Canonical source hashes and ownership are unchanged. Hybrid accounting
has zero overlap and zero unaccounted file bytes. The prior refresh replayed
all 149 proofs through their exact compiled artifacts. Queue/batch regression
tests remain active; fresh compilation of the skipped controls is still due.

Pinned Aztec 3.6a is the primary profile; compatible 5.0a/short-int and existing
member-specific profiles remain available where receipts justify them. Exact
historical release attribution is unproved. Do not relock original fixtures,
force addresses, patch linked outputs or normalize unproved helper identities.

Proof levels are defined in `proof-levels.md`: semantic/similarity is advisory;
FUNCTION_CODE_MATCH requires complete bytes and independently resolved fixups;
FUNCTION_WITH_DATA_MATCH adds a proved compiler-owned tail; overlay/executable
levels additionally require independent content, relocation and natural layout.
RAW_ORACLE_DEBT is validation/accounting only, never reconstructed source.

Scratch and new attempts go under ignored `build/`; retirements go under
`to_delete/`. The user manually deleted the historical quarantine before this
push. No deleted archive is reintroduced in the active project or pushed.

Recommended next wave: one ov04 source task, one ov04 data/object-order task,
one bounded AJ/FFP grammar task, and one targeted runtime CFG acquisition task.
No fleet was launched. Exact compiler-release archaeology, broad asset-format
recovery and unrelated easy-function grinding are intentionally deferred.
