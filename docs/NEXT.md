# Current state and next work - 2026-10-15

The end goal is complete, readable source for DuckTales whose behavior we can
trust, as the base for a later native SDL3 port. Exact matching decompilation
is the preferred recovery and verification technique, not the deliverable.
The stages are:

1. Exact matching recovery.
2. Behavioral completeness for whatever cannot be matched.
3. A dedicated cleanup and modernization pass.
4. The SDL3 port.

We are in stages 1-2. Do not modernize matched sources, and do not add SDL3
code or dependencies to this repository yet. Git history holds the earlier
handoff narratives (waves 12-18, Sol campaigns 1-18).

## Where we are

Run `python tools/behavior.py` (read-only, under a second) for the current
numbers. It derives everything from the accounting, function, ownership and
blocker ledgers. At this checkpoint:

| CODE hunks | Bytes |
| --- | ---: |
| Exact C (FUNCTION_CODE_MATCH / WITH_DATA, unit and complete-C proofs) | 145,968 |
| Assembly (RECOVERED_ASM 48 + RECONSTRUCTED_ASM 2,110) | 2,158 |
| Typed CODE data, compiler literals, padding | 13,743 |
| Pinned Aztec runtime library (c.lib, m.lib members) | 5,444 |
| Unresolved | 7,055 |

- Overlays ov03-ov13 and ov15 are completely exact C, apart from four 2-byte
  terminal gaps. ov14 (the bootstrap overlay) has 1,444 unresolved bytes.
- The resident CODE hunk has 5,603 unresolved bytes. They are listed in the
  next section.
- Resident DATA has 1,044 typed bytes, 588 runtime bytes and 10,324 raw
  bytes. BSS (34,092 bytes) has no typed layout.
- No source has a semantic name. Of the 287 accepted C files, 274 define the
  mechanical entry `recovered`. They reference 1,620 mechanical globals
  (194 with conflicting per-file views) and 350 mechanical callees. There is
  no shared header.
- No asset format is decoded (FORMAT-001), and nothing reconstructed has
  been executed. Matching proves code equivalence one function at a time.
  Data initialization, the link and runtime behavior are not exercised.

## Remaining code, by cause

| Cause | Functions | Approx. bytes | Category |
| --- | --- | ---: | --- |
| Char-return widening: every pinned compiler adds `ext.w`; needs Aztec 3.3x/3.4x | 411E, ov14 0412/04A8/0540, then 404A, 4184, 287C, 291E, 49A0, ov14 0000 | 3,600 | TOOLCHAIN |
| Audio driver, frameless IRQ and register-ABI entries | 55D6..5796, 5594, 57D2, 5868, 615E, and small residues in 5E7C..704E | 1,100 | needs a FRAMELESS_ENTRY non-C predicate |
| Game callers of the audio driver | 50E8 (exact against the 6200 provider, needs a harness recipe), 53E6 | 680 | CALL_BINDING |
| Unpinned amiga.lib glue (BltMaskBitMapRastPort) | 4692, which gates 34E0 | 312 | RUNTIME/LIBRARY |
| One codegen residual | 463E (eor operand order) | 56 | SOURCE_SHAPE, exhausted |
| FFP gateway stubs and stdio (`putc` differs in 4 bytes), startup header | 8CD8.., 806C..83E0, 0000..0018 | 1,000 | runtime, category C |

## Requirement categories

Every effort is one of three kinds. Prefer A, use B where it unlocks code, and
never let C block A or B.

- **A. Game behavior:** logic, control flow, data structures, state, resource
  loading, timing, rendering, audio, input. Essential.
- **B. Recovery enablers:** compiler profiles and ABI, symbol and relocation
  binding, function boundaries, object groups, overlay call routing,
  runtime-library identification (it removes library bytes from the game
  denominator). Valuable while they unlock or verify game code.
- **C. Historical executable reproduction:** natural link order, the ov04
  node link, root JMP-slot prefix and linker-generated data, padding, CRT0
  and startup objects, exact stdio/malloc/amiga_ffp members, dead-code
  objects, and the hunt for a 3.4x compiler. Keep what is proven. These are
  not prerequisites for the port, so open no new C campaigns before the A
  items below.

Proof categories stay separate and are never merged in reporting:
exact C, recovered ASM (provenance-backed), reconstructed ASM (machine-proven
non-C), behaviorally reconstructed (not yet implemented; see priority 1), and
unresolved. Never describe behavioral equivalence as a match. Never replace
an accepted source with an unverified rewrite.

## Priorities

1. **Behavioral route for the char-return group.** The code is understood,
   and the 3.6a candidates differ only by the widening. Add one explicit
   category: compile with the pinned 3.6a, and machine-check that every
   difference is an `ext.w`/`andi` after a byte return. Account it separately,
   and keep it upgradeable to exact if a 3.4x compiler ever appears. This
   unblocks about 3.6 KB without pretending to match.
2. **Audio driver closure.** Implement the calibrated FRAMELESS_ENTRY
   predicate (all 272 canonical C functions start with LINK) for the IRQ and
   wrapper entries, then admit 50E8/53E6. Driver behavior (Paula channels,
   44 opcodes, note packing) is what the port's audio backend must reproduce.
3. **Data model.** Turn the 194 conflicting global views into one evidence
   map: address -> extent, type and consumers, from `declaration_views.py`
   conflict clusters and the type evidence. Type the remaining resident DATA
   (10.3 KB raw) under the DATA initializer policy, and map BSS. Keep this as
   a separate reconstructed interpretation. Matched sources stay unchanged.
4. **Asset formats.** The file loaders and decoders (resident readers
   2D66/2DBA/3C4C/3E9C, `.arc` users in ov03-ov15) are now exact C.
   3C4C sets up 9-bit codes with the first free code 0x102 and 0x200 table
   growth, which looks like an LZW decoder (a hypothesis). Derive the
   container, compression and record formats from this code. Validate host
   decoders against the original disks. The port needs this directly.
5. **Semantic naming.** Add a reviewed mechanical-to-semantic name map
   (functions, globals, struct fields) with evidence notes. Apply it only when
   generating a readable view; matched sources and proofs stay mechanical.
6. **Platform surface.** `behavior.py` lists the 88 runtime/OS members that
   game code calls and the 21 functions with absolute custom-chip or CIA
   access. That list is the port's platform-layer contract. Annotate its
   semantics (blitter, copper, Paula, input, timing, DOS I/O) as the driver and
   data model become clear.

Future portability concerns: the 16-bit `int`, big-endian data, A4-relative
small data, overlay paging, FFP floats, and hardware timing. Record them; do
not convert any code yet.

## Worker loop

```powershell
python tools/behavior.py
python tools/grinder.py facts TARGET
python tools/declaration_views.py --function TARGET --block
# Write build/workers/NAME/candidate.c, then verify without promoting:
python tools/check_function.py TARGET build/workers/NAME/candidate.c --profile aztec36 --isolated --no-promote
# Promote the unchanged candidate after reviewing the exact result:
python tools/check_function.py TARGET build/workers/NAME/candidate.c --profile aztec36
python tools/promote_batch.py MANIFEST --verify-only
```

Workers are Codex sessions (`build/workers/NAME`) or Agent subagents. Each
gets one target and a task card, as AGENTS.md describes. The supervisor owns
all canonical writes. Read `docs/COMPILER_LEARNINGS.md` before writing C.

Validation at tooling and promotion boundaries:

```powershell
python tools/census.py --write
python tools/census.py --check
python tools/hybrid_image.py --check
python -m pytest tests -n 16 --dist=loadscope -m "not regression_serial" -q
python -m pytest tests -m regression_serial -q
```

Canonical re-derivation reads ignored `build/compile-cache` and
`build/worker-jobs` (producer jobs found by receipt hash). Prune neither.
A cold cache means re-running the WinUAE worker.

Gate cost is a first-class concern. A strict derivation re-validates every
accepted proof from scratch, and many tests run one against the real
repository. Profile with `--durations` before adding another real-repo test.
Prefer synthetic fixtures for mechanism tests. Keep real-repo replays to the
few that guard canonical results.

Measured on 2026-10-15: a strict `hybrid_image.build()` takes about 70 s,
and it is now mostly file I/O. The audio, code-data and data provider
verifications run 2-5 times per build: once inside the census derivation and
again for accounting. The structural fix is to compute each provider's rows
once per derivation and pass them on. A content-keyed memo outside the census
stage was tried and is slower, because each lookup rehashes the whole input
closure. Do not retry that.

## Retired 2026-10-15

These moved to `to_delete/` (see its manifest). Git history keeps them too.

- Supervised Haiku fleet: `fleet.py`, `fleet_regions.py`, `docs/fleet.md`.
  The function frontier is drained, and every remaining target is blocked
  above. Its compile-queue, file-lock and resident-recovery tests live on in
  `test_compile_queue.py` and `test_resident_recovery.py`. Its worker
  lessons are now an appendix of `COMPILER_LEARNINGS.md`.
- Local-LLM proposer stack (`local_*`, `model_proposer`, GPU telemetry).
  It produced zero promotions (LOCAL-GRINDER-QUALITY-001).
- DOS secondary-oracle pilot (`dos_*`, `evidence/dos`, its docs). The
  executable stays in `assets/dos` as a possible behavior cross-reference
  for the port.
- ov11 cycle-gap and frontier audits. ov11 is now exact.
- Stale docs: the consolidation checkpoint, the grinder narrative, the
  recovery-planning note, and the placeholder overlay READMEs.
