# Current state and next work - 2026-10-16

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
| Exact C (FUNCTION_CODE_MATCH / WITH_DATA, unit and complete-C proofs) | 149,934 |
| Behavioral C (BEHAVIORAL_CHAR_RETURN: 411E, ov14 0412/04A8/0540) | 602 |
| Assembly (RECOVERED_ASM 48 + RECONSTRUCTED_ASM 2,742) | 2,790 |
| Typed CODE data, compiler literals, padding | 13,999 |
| Pinned Aztec runtime library (c.lib, m.lib members) | 5,444 |
| Unresolved | 1,599 |

Between 2026-10-15 and 2026-10-16, unresolved code fell from 7,055 to 1,599
bytes. ov14, the `.arc` loader and decoders, the Paula IRQ handlers, audio
setup and teardown, and the graphics glue with the sprite draw (4692, 34E0)
are now recovered.

- Overlays ov03-ov15 are complete, apart from five 2-byte terminal gaps.
- Resident DATA has 1,044 typed bytes, 588 runtime bytes and 10,324 raw
  bytes. BSS (34,092 bytes) has no typed layout. `recovery/data_model.json`
  gives evidence-backed types and extents for 1,037 of 1,652 globals.
- Names: `recovery/names.json` names 38 game functions, 88 OS/runtime entries
  and 19 globals; `tools/readable.py` renders them. Most functions still have
  mechanical names.
- Assets: `formats/decode.py` decodes all 17 containers (LZW, RLE bitplanes,
  ADPCM) and 11 recovered palettes. The title screen renders correctly.
- Behavior: `tools/difftest.py --all` runs 144 functions both as original
  68000 code and as host C. 75 agree, 66 differ and 3 time out waiting on
  hardware. The differences are runtime-state dependencies the harness names
  (unmapped reads), plus real portability findings (byte order, pointer width).

## Remaining work for a complete oracle

| Item | Bytes | Category | State |
| --- | ---: | --- | --- |
| Raw resident DATA: palettes 1422..1EA4, audio periods and pointers 29DE..2C64, coordinates 0468..0A3A, map/tile rows 0AC2..12B4, index tables 1F34..292E | about 9,500 | A | typed providers in review (53 exact candidates) |
| Audio residues 57D2, 5FC8, 6000, 60BC, 6A8E, 701A, 702E | 66 | A, CFG/BOUNDARY | worker in progress |
| 463E (one `eor` operand-order residual) | 56 | A | kept unresolved by decision, agrees on 4,000 executed inputs |
| Startup header, FFP gateway stubs, stdio (`putc` differs in 4 bytes) | about 1,470 | C | identify roles and names only; no exact campaign |
| Root JMP-slot table 0000..0320 in DATA | 800 | C | linker-generated; stays raw |
| BSS layout | 34,092 | A | types come from the data model; no initializers to recover |

**Completeness test (user decision 2026-10-16): link and run.** The oracle is
complete when everything under `src/` compiles with the pinned Aztec `cc`/`as`,
links with its `ln` (Manx overlay tree, original c.lib/m.lib) into a program,
and that program runs in WinUAE and behaves like the original: boot, title
screen and recorded-input gameplay. Byte-identical layout is not required
(link order and padding are category C). No original CODE/DATA bytes, no
patching, no ORG or placement. Temporary link-only stubs may be used in a
smoke test, are clearly labelled, and never count as recovery. The link
inventory (undefined, duplicate and conflicting symbols, overlay `ln`
specification, layout-dependence risks) is the first step.

**Porting foundation (2026-10-16).** The port is mostly mechanical once all of
these hold:

1. Complete: every game byte exists as source; no oracle bytes fill gaps.
2. Self-consistent: link-and-run, as above.
3. Verified as a whole: the same recorded input gives the same per-frame
   game-state trace in the original (WinUAE), in our build and later in the
   port. This trace is the port's acceptance test. Rendering and audio get
   per-frame screenshot and audio-buffer references.
4. Understood: semantic names, every global typed with fields, and the core
   systems documented (loop, entities, collision, levels, timing).
5. Explicit platform boundary: every OS and custom-chip touch listed with its
   meaning. The port replaces exactly this layer.
6. Portability hazards catalogued: 16-bit `int`, byte order, pointer width,
   FFP floats, A4 data, overlays, layout tricks.
7. Assets understood (done).

After that come the readability pass (stage 3: names, struct fields, readable
view) and then the SDL3 port (stage 4).

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

1. **Typed DATA (A).** Admit the raw game tables above under the DATA
   initializer policy through `promote.py data`. Keep untyped spans raw.
2. **Audio closure (A).** Only the 66 residue bytes remain. Driver behavior
   (Paula channels, 44 opcodes, note packing) is what the port's audio
   backend must reproduce.
3. **Platform surface (A).** `behavior.py` lists the 88 runtime/OS members
   that game code calls and the functions with absolute custom-chip or CIA
   access. Annotate their semantics (blitter, copper, Paula, input, timing,
   DOS I/O) and name the startup, FFP and stdio residue. That list is the
   port's platform-layer contract.
4. **Readability pass (stage 3, next).** Extend `recovery/names.json` (every
   entry needs an evidence note), add struct fields from the data model, and
   render with `tools/readable.py`. Matched sources and proofs stay
   mechanical.
5. **Differential harness.** Use `tools/difftest.py` as behavior evidence for
   BEHAVIORAL_C and unresolved code (`--candidate`), and later to check port
   code against the original 68000 bytes.

Done and closed: the behavioral char-return route, the `.arc` asset path,
the frameless/register/glue ASM predicates, the C-unit ASM-dependency recipe,
and the asset decoders.

Future portability concerns: the 16-bit `int`, big-endian data, A4-relative
small data, overlay paging, FFP floats, and hardware timing. Record them; do
not convert any code yet.

## Worker loop

```powershell
python tools/behavior.py
python tools/readable.py      # readable view with reviewed names -> build/readable/
python tools/grinder.py facts TARGET
python tools/behavioral.py TARGET SOURCE        # byte-return widening only; isolated
python tools/boundary_refresh.py                # after every promotion
python tools/declaration_views.py --function TARGET --block
# Write build/workers/NAME/candidate.c, then verify without promoting:
python tools/check_function.py TARGET build/workers/NAME/candidate.c --profile aztec36 --isolated --no-promote
# Promote the unchanged candidate after reviewing the exact result:
python tools/check_function.py TARGET build/workers/NAME/candidate.c --profile aztec36
# Every proof class publishes through one CLI (registry: tools/acceptance.py):
python tools/promote.py CLASS MANIFEST --verify-only   # functions, asm, data, code_data, behavioral, dead_code, mixed
python tools/promote.py CLASS MANIFEST                 # publish: tiered gate, then census and accounting refresh
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

Each accepted proof's validation is memoized under ignored
`build/validation-memo/` (`tools/validation_memo.py`). A row is reused only
when every file its validator read, its explicit context and the validator's
tools import closure hash identically; any change re-validates. With a warm
memo `census --check` takes about 14 s (148 s cold) and `hybrid_image.py
--check` about 34 s (147 s cold). The memo is JSON only and is safe to delete.

Known tool-hash coupling that remains (2026-10-16). Compiler identities and
cache keys embed the source hash of `compiler_oracle.py`
(`same_overlay_export_extractor_sha256`, resident interface
producer/extractor). Editing that file therefore re-keys overlay trials and
stales the ov04 padding recipe (run `tools/padding_refresh.py`, about 1 min).
The cached-artifact gate now treats these hashes as provenance, because
exact re-extraction runs on every read. Dropping them from new identities
would re-key the whole compile cache once. Do that only together with a
planned cache rebuild.

## Retired 2026-10-16

- The per-batch ASM promoters `promote_driver_asm.py`,
  `promote_callback_asm.py` and `promote_frameless_asm.py`. They are replaced
  by `promote.py asm`.

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
