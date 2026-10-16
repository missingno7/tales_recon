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

| CODE hunks (2026-10-16) | Bytes |
| --- | ---: |
| Exact C (FUNCTION_CODE_MATCH / WITH_DATA, unit and complete-C proofs) | 149,682 |
| Behavioral C (BEHAVIORAL_CHAR_RETURN: 411E, ov14 0412/04A8/0540) | 602 |
| Assembly (RECOVERED_ASM 48 + RECONSTRUCTED_ASM 2,682) | 2,730 |
| Typed CODE data, compiler literals, padding | 13,999 |
| Pinned Aztec runtime library (c.lib, m.lib members) | 5,444 |
| Unresolved | 1,911 |

The session that started from 7,055 unresolved bytes (exact C 145,968) on
2026-10-15 closed ov14 and the `.arc` loader and decoder path (287C, 291E,
404A, 4184, 49A0). It also closed the Paula IRQ handlers and the audio
setup and teardown (50E8, 53E6).

- Overlays ov03-ov15 are complete, apart from five 2-byte terminal gaps.
- Resident DATA has 1,044 typed bytes, 588 runtime bytes and 10,324 raw
  bytes. BSS (34,092 bytes) has no typed layout. This, and 195 conflicting
  global views, is now the largest gap (priority 3).
- Names: `recovery/names.json` names 38 game functions, 88 OS/runtime entries
  and 19 globals; `tools/readable.py` renders them. Most functions still have
  mechanical names.
- Assets: `formats/decode.py` decodes all 17 containers (LZW, RLE bitplanes,
  ADPCM) and 11 recovered palettes. The title screen renders correctly.
- Behavior: `tools/difftest.py` runs 101 functions both as original 68000 code
  and as host C; 55 agree. The rest are emulator memory-model gaps, plus real
  portability findings (byte order, pointer width).

## Remaining code, by cause

| Cause | Functions | Approx. bytes | Category |
| --- | --- | ---: | --- |
| Library glue with a register ABI, then its caller | 4692 (asm), 34E0 (C): verified, patch being rebased | 312 | RUNTIME/LIBRARY |
| One codegen residual | 463E (eor operand order) | 56 | SOURCE_SHAPE, exhausted |
| Audio residues whose entries lack proof | 57D2, 5FC8/6000/60BC/615E.., 6A8E, 701A/702E | about 100 | CFG/BOUNDARY |
| FFP gateway stubs and stdio (`putc` differs in 4 bytes), startup header | 8CD8.., 806C..83E0, 0000..0018 | about 1,000 | runtime, category C |

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
non-C), behaviorally reconstructed (`BEHAVIORAL_C`, see priority 1), and
unresolved. Never describe behavioral equivalence as a match. Never replace
an accepted source with an unverified rewrite.

## Priorities

1. **Behavioral route for the char-return group (in progress).**
   `tools/behavioral.py` verifies a candidate with the pinned compiler. It
   deletes only `ext.w d0` widenings that directly follow a byte return. The
   unchanged exact comparison must then be EQUAL, relocations included, and
   every original caller must read only D0.b. Accepted entries live in the
   `behavioral_functions` ledger map. They are accounted as `BEHAVIORAL_C` and
   are never counted as matches. ov14 0412/04A8/0540 (500 bytes) are accepted.
   Next is resident_F_411E. It is blocked by a verifier weak spot: when a
   function's only PC-relative calls go to proven library entries (411E's
   `Read` glue), check_function builds a unit that pulls in A4-slot callees
   and contradicts the resident interface derivation. Every accepted function
   in that situation was proved on the single-function path, so restore that
   path there. 404A/4184 follow; they hold the `.arc` RLE graphics decoder
   (formats/arc.md). Then 291E/287C/49A0 and ov14_F_0000.
2. **Audio driver closure (mostly done).** FRAMELESS_ENTRY is implemented
   (tools/audio_frame_calibration.py: every canonical C function and all 24
   compiler controls are framed). Batch 0004 admits the four Paula IRQ
   handlers 55D6..5726, the wrappers 5594/5868 and callback 615E as
   RECONSTRUCTED_ASM (572 bytes). Still open: 72 bytes whose entries lack
   proof, and 50E8/53E6, which need an ASM-dependency recipe for C units.
   Driver behavior (Paula channels, 44 opcodes, note packing) is what the
   port's audio backend must reproduce.
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
5. **Semantic naming (started).** `recovery/names.json` is the curated map from
   mechanical to semantic names. Every function or global entry needs an
   evidence note. `python tools/readable.py` renders `build/readable/` with
   those names applied; `--check` validates the map. Matched sources and proofs
   stay mechanical. Struct fields come next, after the data-model map
   (priority 3).
6. **Platform surface.** `behavior.py` lists the 88 runtime/OS members that
   game code calls and the 21 functions with absolute custom-chip or CIA
   access. That list is the port's platform-layer contract. Annotate its
   semantics (blitter, copper, Paula, input, timing, DOS I/O) as the driver and
   data model become clear.
7. **Differential behavior harness (prototype works).**
   build/workers/opus-difftest/difftest.py runs the original 68000 bytes of a
   function under Unicorn (Aztec stack ABI, result in D0.w). It compiles the
   matched C for the host with gcc and `int` mapped to 16 bits, then compares
   the two on random and boundary inputs. ov11_F_25D6 and ov11_F_262E agree on
   20,000 inputs each, and a one-character mutant is caught at once. To grow
   it into `tools/difftest.py`: map resident DATA at the A4 bias for globals,
   pass struct pointers, handle stubbed callees, and record per-function
   results. It gives behavioral evidence for BEHAVIORAL_C and unresolved code,
   and later checks modernized port code against the original. Host tools:
   MSYS2 `gcc` and the installed `unicorn` 2.1.4.

Future portability concerns: the 16-bit `int`, big-endian data, A4-relative
small data, overlay paging, FFP floats, and hardware timing. Record them; do
not convert any code yet.

## Worker loop

```powershell
python tools/behavior.py
python tools/readable.py      # readable view with reviewed names -> build/readable/
python tools/grinder.py facts TARGET
python tools/behavioral.py TARGET SOURCE        # byte-return widening only; isolated
python tools/behavioral.py --promote MANIFEST.json   # one regression gate for a batch
python tools/boundary_refresh.py                # after every promotion
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

Known tool-hash coupling that remains (2026-10-16). Compiler identities and
cache keys embed the source hash of `compiler_oracle.py`
(`same_overlay_export_extractor_sha256`, resident interface
producer/extractor). Editing that file therefore re-keys overlay trials and
stales the ov04 padding recipe (run `tools/padding_refresh.py`, about 1 min).
The cached-artifact gate now treats these hashes as provenance, because
exact re-extraction runs on every read. Dropping them from new identities
would re-key the whole compile cache once. Do that only together with a
planned cache rebuild.

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
