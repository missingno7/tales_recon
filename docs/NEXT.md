# Current state and next work - 2026-10-18

The end goal (user decision 2026-10-18) is fully human-readable, extendable
source for DuckTales and a deep, documented understanding of the game, like a
modern decompilation project (model: duke1_recon). Exact matching is the
recovery and verification technique, not the deliverable. The work runs in
parallel streams, with no freeze of matching:

1. Exact matching of what remains (code, audio tables, raw DATA).
2. Readability in src/ itself: semantic names under the naming rule
   (AGENTS.md), applied with `tools/rename.py`. `recovery/names.json` is the one
   map between a mechanical identity and its readable name; tools read sources
   through `tools/names.py`, so a pure rename changes no proof. Then per-function
   summaries, shared structure headers instead of per-file views, files per
   original object, the data model (BSS and raw DATA typed), and a game book under
   docs/game/. Subsystem by subsystem, in the order the port reaches them.
3. The SDL3 port in port/ (docs/sdl3-port.md): a thin layer that runs src/
   unchanged; record/replay as its behaviour regression.

When everything matches, the per-function proof era is archived under a tag and
the whole-build comparison remains the gate. Git history holds the earlier
handoff narratives (waves 12-18, Sol campaigns 1-18).

## Verification and the route to a native game (user direction 2026-10-18)

The long-term goal is a clean, native DuckTales that behaves like the original:
behavioral fidelity kept, implementation fidelity (Amiga OS, chips, overlays, memory
layout, 68000 code) removed step by step. `src/` stays the matched reference; native
rewrites happen in the port, one bounded subsystem at a time, each proven against the
original by replay before the compatibility code it replaces is deleted.

Verification (2026-10-18, numbers in docs/sdl3-port.md, "Verification"): one replay log,
timed in **poll frames** (the steps of the game's input reading), drives the original in
WinUAE, the reconstructed Amiga build and the SDL3 port. The original replays its own log
exactly across fresh sessions; the port replays byte-identically. Original vs port: the same
23 sound commands at the same poll frames, and 1,009 of 1,018 typed globals identical at every
one of 1,082 logical checkpoints - the rest is the audio driver's frame-timed progress. A
deliberate rule mutation is located to the two tables it writes, at the poll frame it acts.
Emulator survey: WinUAE with a fixed emulated start is sufficient (BizHawk's UAE core lacks
register access and needs a window; vAmiga has no prebuilt Windows headless build; FS-UAE's
scripting is unreleased).

Next, in order:

1. **Widen the scenarios** with the same tools: locations, travel, the four minigames; then
   the user's own playthrough, recorded in the original (`game_boot.py`) and replayed on the
   build and the port. Keep a dump at every poll frame for the first divergence.
2. **Audio as events**: the sound commands match; compare what the driver plays (Paula
   register writes or the mixed output per sound command) to retire the frame-timed driver
   state from the comparison, and look for loops that animate while a sound plays.
3. **The build's pointers by identity** (`game_compare.py`: map a build DATA address to the
   original offset through the link map), so build-vs-original compares pointers too.
4. **First native replacements** (docs/sdl3-port.md, "From compatibility port to native
   game"), each proven by replay before the old code goes.

Readable modules (2026-10-18): the map overlay is one module, `src/map/map.c` (five functions,
each proven EQUAL from `src/map/map.c#name`; the executable rebuilt from it is byte-identical).
Evidence no longer pins source layout: the DATA audio-field validator re-checks the data-model
facts it uses instead of the file's hash, mechanical data-model evidence is refreshed with
`tools/data_model.py --refresh-scalar-evidence` (refuses any type or extent change), and
`tools/hybrid_image.py --refresh` re-captures only the specimens whose proof changed. Next
module candidate: ov12 (one function, measured EQUAL from a module reference in 200 s).
`hybrid_image.py --refresh-all` is blocked by a pre-existing recipe drift in
`resident_F_291E` (its retained unit predates today's ASM-dependency closure).

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
- Names (2026-10-18): `recovery/names.json` names 264 game functions, 85
  OS/runtime entries and 216 globals, proposed per subsystem by Codex workers and
  reviewed; `tools/rename.py` has applied them to src/ (two batches, the Amiga
  executable rebuilt byte-identical each time) and `port_gen.py` spells the port
  with them. docs/game/ is the game book that grew out of the review. Next: each
  per-function file still defines its function as `recovered()`, so a function's
  own name appears only at call sites - fixed when files are consolidated per
  original object; field names (proposed in build/workers/names-*/) wait for the
  struct-header step; 40 of 288 C function files and most BSS globals stay mechanical
  until the code shows what they are.
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
| Audio envelope/bytecode candidates 5FC8, 6000, 60BC, 6A8E | 14 | A, DATA_OWNERSHIP | unrooted records; need a general audio-data provider (evidence/blockers/resident_audio_residues.json) |
| Audio score/envelope tables in CODE: RAW_ORACLE_DEBT spans the build leaves out (largest: 26 bytes in `score_1836` at 0x19F8, also `r400`, `audio3_e_6028`, `audio4_c_6579`, `audio3_08`) and differing typed bytes (`build/game/diff.json`) | about 200 raw, 420 differing | A | the SDL3 port plays these tables (`tools/asm_port.py`); until recovered, some tunes can differ from the original |
| 463E (one `eor` operand-order residual) | 56 | A | kept unresolved by decision, agrees on 4,000 executed inputs |
| Startup header, FFP gateway stubs, stdio (`putc` differs in 4 bytes) | about 1,470 | C | identify roles and names only; no exact campaign |
| Root JMP-slot table 0000..0320 in DATA | 800 | C | linker-generated; stays raw |
| BSS layout | 34,092 | A | types come from the data model; no initializers to recover |

**Milestone (2026-10-17): the from-source build reaches the title screen.**
`python tools/game_build.py --build` compiles every accepted source with the
pinned Aztec 3.6a tools (vamos, parallel; float TUs batched into one headless
WinUAE job), links with `ln` and matches the original topology (16 hunks, 13
overlays, CHIP flags, root JMP slots). `python tools/game_boot.py run` boots it
deterministically (emulated frames from power-on) and records CPU faults from
WinUAE's console; `--original` gives the baseline. The build shows the title
screen at the same point as the original and runs the same functions per frame
range (loading: 46CE/404A/50E8/559E/411E; title loop: 4376/4F62, Paula IRQs).
It is not stub-free yet (`game_build.py --report`): BSS is zero-filled
reservations per storage-plan object, raw DATA gaps are zero placeholders that
keep the original layout, 463E uses its best candidate, and 2B4A/2BFE are zero
cells. Faults found and fixed on the way, all layout dependencies: MemHeader
fields allocated apart (pool empty), callback tables still raw (NULL jumps), a
byte alias of an int provider stubbed, one numeric A4 displacement in 617C,
and the sample-pointer array split around raw cells (a write into audio code).
Next: play-through traces (input scripts past the title) against the original,
then replace the remaining stand-ins.

**Plan (user decision 2026-10-18, replaces 2026-10-17):** start the SDL3 port
now, in `port/`, as a thin layer that runs the reconstructed game unchanged on an
emulated Amiga (`docs/sdl3-port.md`). Exhaustive play-testing of every game state
does not gate it: the port records and replays every nondeterministic platform
read, and a port bug is traced from the lowest layer (replay, first wrong global,
then `tools/difftest.py` on the one function against the original 68000 code).
The readability pass and the remaining raw bytes continue alongside, driven by
what the port and its replays expose. (The earlier note that WinUAE runs were not
reproducible across sessions traced back to the harness entering the debugger after a
wall-clock pause; with a fixed emulated start they are, see "Verification" above.)

**Completeness rule (user decision 2026-10-17):** play-through traces define
done. Everything the trace scripts exercise must be recovered and match the
original; widen the scripts to real gameplay (locations, segments, money,
endings), and they double as the SDL3 port's acceptance suite. Raw DATA that no
trace ever reads may stay unrecovered: the port loads it at start-up from the
user's original executable (like the disk assets), from an explicit list, never
embedded in source. Amiga-only reproduction details (JMP slots, link padding,
c.lib data) get no further effort unless a trace shows they change behavior.

Method (user direction 2026-10-17): find behavior differences at their source,
not by replaying. `python tools/game_diff.py` (about 1 s, no emulator) compares the
linked build with the original byte for byte: every original hunk offset maps to
the build through offset-encoding link-map names, runtime aliases and CODE-data
provider parts; relocations, small-data (A4) references, jump-slot calls and
PC-relative branches count as consistent when they reach corresponding targets,
and each remaining DIFFERENT byte is attributed to its accounting category. At
119654f: 3,930 bytes differ - 2,156 raw unrecovered bytes (sound record pointers,
pointer and callback tables, audio values, small code fragments: the behavior
source), 1,054 c.lib version differences, 380 in the superseded compact selector,
308 in runtime-alias boundaries. `build/workers/sol-raw-data/targets.json` lists
the 97 raw ranges whose original bytes are nonzero.

Behavior finding (2026-10-18, title-to-money-bin script, turbo floppy): the build's
state sequence equals the original's (same resource loads in the same order, same
RNG states) until the game reseeds its LFSR (G_h01_3AB8) from VPOSR + tick
(resident_F_4676, around the difficulty choice). The build is not cycle-identical, so
the beam position - and every random outcome after it - differs (seed 0x8AA0 vs
0x8AA7). With the reseed pinned to the original's value (`--rng-record` on the
original, `--rng-pin RUN` on the build) all companies, locations, treasures and map
links (pointers by target) equal the original at frames 4000/6000/8000; the remaining
listed differences are fast-changing state sampled at another phase (animation
frames, audio interrupt countdowns) and absolute pointers. Seeding the remaining
raw DATA from the original (a harness-only experiment) changed nothing on this
script, so it is not read there. Use `game_compare.py ORIG BUILD --sequences` for
the timing-free comparison.

Play-through traces confirm a fix: `game_boot.py run --turbo-floppy --input
evidence/trace/title-to-money-bin.json --input-offset 2100 --dump-from 500
--dump-every 25` (add `--original` for the baseline), then `game_compare.py ORIG
BUILD --shift N`, N aligning the game tick G_h01_B1EC. WinUAE replays are
deterministic across fresh sessions (fixed emulated start, 2026-10-18); turbo floppy removes load
times that depend on where files sit on the disk, which otherwise shift the build
by hundreds of frames when a short scripted press is missed. The build now plays
the whole script (office, Money Bin, contest screen); earlier hangs and crashes
came from the compacted CODE-data selector and from one-byte DATA cells padded
apart by ln, both fixed in the build materialization.

**Completeness test (user decision 2026-10-16): link and run.** The oracle is
complete when everything under `src/` compiles with the pinned Aztec `cc`/`as`,
links with its `ln` (Manx overlay tree, original c.lib/m.lib) into a program,
and that program runs in WinUAE and behaves like the original: boot, title
screen and recorded-input gameplay. Byte-identical layout is not required
(link order and padding are category C). No original CODE/DATA bytes, no
patching, no ORG or placement. Known adjacency dependencies for the link:
57D2's not-taken branch targets its object end and must fall into 57E4
(link it directly before that object or merge them); 615E calls 617C at its
end boundary; audio dispatch index 44 at H1+292E reads the period table at
29DE. Temporary link-only stubs may be used in a
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

Validation cost fixes (2026-10-17, measured on 600 DATA providers): each
producer job is audited once per validation scope, not once per provider
(DATA class cold: about 2 h to 7.4 s); `game_image.game()` returns the
fixture-locked image without a census derivation; publishers hash the input
closure once per validated stage instead of around every read; the DATA
snapshot identity handles each batch once (20.3 s to 3.8 s per call). A DATA
verification pass went from 1 h 41 min to 84 s and `check_function --isolated`
from about 60 s to 18 s. Compiles go through `tools/vamos_backend.py`
(TALES_COMPILE_BACKEND=auto): byte-identical to WinUAE on 58 float-free corpus
items and the whole-game link, about 4x faster per compile and parallel;
float/double sources and any compile that opens a math library use WinUAE.

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
