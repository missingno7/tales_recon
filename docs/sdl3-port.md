# SDL3 port: design

Goal (user decision 2026-10-18): one executable that plays DuckTales: The Quest for Gold
on a modern system, built from the recovered source. The port is a thin layer: the
reconstructed game runs unchanged on an emulated Amiga, and the platform below turns what
the game asks of the Amiga into an SDL3 window, input, audio and files. `src/` stays the
recovered program (and keeps building the Amiga executable through `tools/game_build.py`);
port behaviour lives in `port/` and `tools/port_gen.py`, never in `src/`. Same shape as
duke1_recon's port.

## Shape

```
src/ (recovered C, typed DATA providers, CODE-data and reconstructed assembly)
   |  tools/game_build.py materializes the accepted sources into translation units
   |  (entry names, runtime-name bindings, DATA providers, BSS reservations) - the same
   |  input the Amiga oracle build compiles
   |  tools/port_gen.py translates them -> build/port-gen/ (never committed)
   v
ducktales.exe = game (generated) + port/override/ + emulated Amiga (port/*.c) + SDL3
```

| Part | What it is |
|---|---|
| `port/amiga.h`, `port/os.h` | the contract: the OS structures as the game sees them and the platform functions the OS emulation calls |
| `port/os_*.c`, `port/adf.c` | the emulated Amiga: graphics/layers/intuition calls on a planar bitmap model, exec memory, lists and interrupts, DOS files on `DT1:`/`DT2:` |
| `port/main.c` | the game's clock, record/replay, state dumps, presentation and input (below) |
| `port/override/*.c` | port versions of game functions that reach hardware through raw pointers or swap bytes for the 68000 |
| `tools/asm_port.py`, `port/m68k.*`, `port/paula.c` | the RECONSTRUCTED_ASM modules (audio driver, Paula IRQ handlers, VBlank server) translated instruction by instruction, and the Paula they drive (below) |
| `tools/port_gen.py` | mechanical translation of the staged translation units (below) |

## Same source, mechanical translation

`port_gen.py` translates the staged C units of `game_build.py` (the exact code the
verified Amiga build compiles) so the C stays Aztec C 3.6:

* the data model stays explicit: `int` -> `int16_t`, `unsigned` -> `uint16_t`, `short` ->
  `int16_t`, `long` -> `int32_t`; `char` stays as Aztec has it (signed);
* the port is a **32-bit (i686) build**, so pointers stay 4 bytes and records that hold
  pointers keep the Amiga layout; structures use the Amiga's 2-byte alignment;
* absolute hardware accesses (`*(unsigned short *)0xdff004`, `0xbfe0fe` ...) become
  `amiga_read16/amiga_write16(address)` calls into the emulated chips;
* OS glue calls (`F_h00_8A46` = BltBitMap ...) bind to the platform functions of the same
  OS names; c.lib runtime members (`strcpy`, `sprintf` ...) bind to host libc or to
  `port/` equivalents where Aztec semantics differ (16-bit `int` in `printf` formats);
* typed CODE-data assembly (audio scores, envelopes, selectors) becomes C byte arrays with
  the same big-endian bytes and a relocation list for its pointers.

## Byte order

The 68000 is big-endian, the host little-endian. Values the game computes and stores in C
variables are host order and need nothing. Byte order matters only where bytes enter or
leave the game as data:

* binary records read from `DT1:`/`DT2:` files into typed structures (the archive loader's
  binary record kind, `.as` sample headers) - converted where they are loaded, per record
  type, in the platform/override layer;
* CODE-data tables read by the audio driver - kept big-endian and read through `be16/be32`
  in the driver override;
* any access that views a word through a byte pointer (or the reverse). The audit of
  2026-10-18 went through every such view in the generated code once; `port_gen.py`
  handles each kind and lists what it did under `byte_order` in
  `build/port-gen/port-gen-report.json`:

| Kind | Example | Port rule |
|---|---|---|
| `#define` alias inside a scalar | `G_h01_0971` = low byte of the int `G_h01_0970` | `byte_order_aliases`: the offset moves to the host byte |
| separate name inside a scalar | the LZW decoder stores a 16-bit code in `G_h01_A9C2` and reads `G_h01_A9C3`; `A7D8` = low word of the long `A7D6` (7 names) | `access_widths` + `interior_aliases`: every unit's extern declarations give each name's access width; a name inside a wider scalar is placed at the host position of its bits in `data_hunk.c` |
| cast of a scalar's address | `((char *)&i)[1]`, `((int16_t *)&b)[0]` | `scalar_views` -> `BE_VIEW(T, x, k)` (`aztec.h`): `_Generic` flips the index only when `x` is an integer scalar wider than `T` |
| structure naming one byte of a word | ov10 cave cells `{char pad; char bits;}` over an int; ov11 animation descriptors read byte +5 of the int `word4` | `WORD_BYTE_PAIRS` (reviewed list): the two byte members are swapped |

  Reviewed and left alone: byte arrays used only by address (`motion`, `prefix`, `pad18`
  passed to functions), record tables viewed through different structures with the same
  field widths, `sscanf("%d")` into `Slot.text` (an int written and read as an int),
  `Rec.kind` (bytes everywhere), OS structures (Node, BitMap, Preferences). The game's
  input handler reads byte 7 of an InputEvent (the low byte of `ie_Code`): the platform
  must write the event in that view.

A state dump of the port is the DATA/BSS hunk as the port holds it: original offsets, host
byte order. `tools/game_compare.py --port` reads each typed global of
`recovery/data_model.json` through its type (numbers by value, pointers never), so it
compares directly with WinUAE state dumps.

## Determinism: one clock, record and replay

The port runs everything on the game thread: there is no timer thread, no audio callback
into the driver and no lock. The game's clock is one tick per PAL frame (71051 colour
clocks, 20.0318 ms) and advances only when the game waits for time (`Delay`, `WaitBOVP`,
and busy-waits on interrupt state, below). Each tick runs, in order, what the Amiga did
around a frame: Paula plays one frame of sound (its block interrupts run the driver), the
VBlank servers run (`game_frame_tick`, colour cycling, the driver's channel update), the
inputs of the new frame are taken. Live play paces the ticks to real time; `--headless`
runs them as fast as the host allows. A run is therefore a function of its inputs.

What reaches the game from outside, measured from the code (2026-10-18):

| Input | Where | Recorded as |
|---|---|---|
| joystick and fire | `poll_controller_and_keyboard_input` (JOY1DAT, CIA-A PRA) | `joy`, `fire` |
| keys | the input handler (`input.device`) | `key` (raw code, bit 7 = release) |
| RNG seed | `seed_random` reads VPOSR + `game_frame_tick` | `seed` (the resulting state) |
| time | `Delay`, `WaitBOVP`, busy-waits on the audio driver's channel-0 state `G_h01_2A16` (title, map, travel: "wait until the sound ends") and on `game_frame_tick` | the clock itself |
| audio driver progress | the driver's state words, read by those busy-waits | follows from the clock |

Nothing else in the game reads interrupt-driven state (cross-reference of every global the
reconstructed assembly writes against the C sources). VPOSR holds LOF (bit 15, set for PAL
non-interlaced frames) and V8 (bit 0, beam on line 256-312), not the line number, so the
seed is 0x8000 + `game_frame_tick` (+1): the RNG is seeded from how many frames the player
spent before the difficulty choice, plus one bit of beam position. The original's recorded
seeds fit this (0x8000 at tick 0, 0x8AA6 at tick 2726).

Busy-waits: `port_gen.py` gives each `while` loop whose condition reads `G_h01_2A16` or
`game_frame_tick` a one-frame wait per pass (`spin_waits`, 19 loops). On the Amiga such a
loop spins while interrupts move the state; here every external change lands on a frame
boundary, so the loop leaves at the same boundary a finer spin would.

Addresses are run-independent too: exec's `AllocMem` and the OS structures the game sees
(RastPort, Layer, ColorMap, copper list, ports) are carved from one fixed arena with exec's
own algorithm, and the executable is linked without address randomization. Guest memory is
registered (`m68k_memory`); a translated-assembly access outside it reads 0 and is logged,
as the Amiga reads bus noise there instead of faulting.

`ducktales --record FILE` writes the log, `--replay FILE` plays it, `--dump DIR:FROM:EVERY`
appends the DATA/BSS hunk (host order, original offsets) to `DIR/state.bin` with
`state-index.jsonl`, `--shot FILE.bmp:TICK` saves the picture at a tick, `--ticks N` ends the
run. The log is text, timed in the game's own clock (`game_frame_tick`), so the same log
drives the port and the original:

```
# ducktales replay log (game clock): CLOCK joy|fire|key|seed HEX, CLOCK end
0 seed 8000
1652 fire 0001
2172 joy 0003
2725 seed 8aa6
5522 end
```

`tools/game_boot.py run ... --dump-every N` writes `port-replay.log` next to every WinUAE run:
its frame-stamped inputs at the game clock they reached the game, and its recorded seeds.

## Verification: what is proven, and how to find the first divergence

Measured 2026-10-18 with `evidence/trace/title-to-money-bin.json` (title, office, Money Bin,
difficulty choice, company/location setup, contest screen; 6,000 frames, turbo floppy):

| Claim | Evidence | Result |
|---|---|---|
| 1-2. The original replays identically, also after restarting WinUAE | fresh sessions, `game_boot.py` starting at a fixed emulated cycle (`START_CCK`) | identical: PC and beam on 6,000/6,000 frames, 220/220 DATA/BSS dumps, the same RNG reseed (three fresh sessions, the third after the tool changes). Before the fix one of three fresh sessions started 47,000 colour clocks earlier |
| 3. Original vs reconstructed Amiga build | same script, the original's seeds pinned (`--rng-pin`), compared per emulated frame | of 940 typed globals: 871 equal at all 220 checkpoints, 50 the same values shifted, 3 never (two pointers typed as numbers, the `GameGraphic` at `G_h01_50E6`). The build is not cycle-identical: it reaches the reseed 13 frames earlier, and from frame ~4550 it catches a fire press the original misses while busy, then runs ~300 frames ahead |
| 4a. The port replays identically | a recorded run replayed twice | byte-identical: 241/241 dumps, screenshot |
| 4b. Original vs SDL3 port | the original's inputs and seeds in the game clock (`port-replay.log`), compared at equal game clock (`game_compare.py --port`) | of 978 typed globals: 863 equal at all 220 checkpoints, 88 take the same values in the same order but later in the original (lag growing from ~150 to ~950 frames: companies, locations, treasures, money, market, sprites), 12 partly (decoder scratch, animation), 15 never: Aztec startup values the port's `_main` does not set (argc, command-line length, `_numdev` bound outside the hunk), pointers and file handles typed as numbers, decoder scratch, and the four audio block countdowns (0 in the original, 1 in the port: a lead into the port's Paula timing) |
| Detection | mutation `% 37` to `% 36` in the treasure assignment (port only) | port vs port: first divergence at tick 2806 in exactly `location_records` and `location_treasure_slots`; original vs port: their agreement falls from 94-98% to 52-54% |
| Detection is not coverage | mutation `>= 35` to `> 35` in `wrap_location_index` | not exercised by the script: identical dumps. A replay proves only what it runs |

What remains nondeterministic or unequal, and why:

* **Time spent working.** The 68000 needs frames to decompress (LZW), draw and read the
  disk; the port needs none. Inputs timed in frames (or in the game clock) therefore reach
  the original later in its state, and a press can land while one machine is busy and the
  other is waiting. Equal-clock comparison then shows the same values shifted ("lag"), and
  a press caught by one and missed by the other changes the path. Exact cross-machine
  replay needs inputs tied to what the game consumes, not to frames (next step below).
* **Interrupt-side state** (audio countdowns, the channel stream pointer `G_h01_2A16`) is
  sampled at different phases relative to the frame; compared, but judged by lag.
* **Typed as numbers but not numbers:** `active_screen_bitmap`, file handles (`arc_file`,
  `G_h01_A7CE`) and `G_h01_2A16` are pointers/handles typed `long` in
  `recovery/data_model.json`; they differ by design between machines.
* **Load-time scratch** (`arc_*` decoder state) differs while one machine is mid-load.

First divergence, in practice: replay the same log in both, compare at equal game clock
(`game_compare.py ORIG PORT --port`), take the earliest global that disagrees at every lag,
then check the function that writes it against the original 68000 code (`tools/difftest.py`).
The first real divergence found this way: sound 6 (played at the difficulty choice) made the
translated driver read through `08 FF 80 00`. Cause: `game_build.py` bound the envelope
pointer table `_G_h00_5E6C` to an older 58-entry compact table instead of the accepted
80-entry table in `r600.asm`; the Amiga build had the same defect (reading garbage), the port
faulted. Fixed in the build materialization; both now play the accepted table.

Recording a human playthrough later: play the original in WinUAE with
`game_boot.py` (frame-stamped events; claim 2 makes it exact on the original) or play the port
with `--record`. Either log replays exactly on the machine it was recorded on. Across machines
it currently holds where inputs arrive while both wait (menus, as in this canary); the planned
input-consumption timing (inputs keyed to the game's input polls) removes the remaining gap.

## From compatibility port to native game

What each part of the port is for (A game logic and state, B a platform interaction the game
needs, C compatibility with a historical implementation detail, D reconstruction and
verification only), and how it leaves:

| Part | Kind | What the game gets from it | Route out |
|---|---|---|---|
| generated game C (`src/` through `port_gen.py`) | A | the game | becomes the native source module by module: a readable rewrite of one subsystem, proven equal by replay, replaces its generated units |
| the game clock in `main.c` (this change) | A | the fixed 50 Hz update the game is paced by | stays: it is the native game loop; rendering and audio can run at their own rates around it |
| `data_hunk.c` (DATA/BSS at original offsets) | C | the game indexes across separately declared globals and keeps addresses in state | typed state structures once `recovery/data_model.json` covers the indexed tables |
| `os_graphics.c` (planar bitmaps, minterm blits, copper View) | B | drawing into bitplanes, palette through copper lists | semantic draw calls (sprite with mask, rectangle copy, text, palette set) where the game's call sites show the meaning; checked by per-tick screenshot equality under replay |
| `paula.c`, translated driver (`asm_port.py`, `m68k.*`) | B + C | music and effects through a 68000 driver on emulated Paula | a native C driver once its behaviour is pinned by WAV equality per replay; the driver's state feeds back into the game only through the "sound finished" busy-waits |
| `os_exec.c` (arena, lists, ports, interrupts) | C | exec semantics the game relies on (its own MemHeader pool, interrupt servers) | goes with the code that calls it |
| `os_dos.c`, `adf.c` | B | files from the two disks | host files (the extracted assets) |
| `runtime.c` (`segload` no-op), overrides | C | overlays and Aztec startup/exit | already reduced to stubs; the overrides go when their callers are rewritten |
| record/replay, dumps, guest-memory checks | D | nothing | stays as the verification harness, outside the game proper |

This change removed one layer: the timer thread, the audio-callback interrupts and the
driver lock are gone; the game, its interrupts and its inputs run on one thread in a fixed
order, which is what made the port reproducible.

## Build

CMake + SDL3 3.4.16, Windows first: MinGW-w64 **i686** gcc (`C:/msys64/mingw32`) and the
SDL3 MinGW package (`C:/tools/sdl3-3.4.16-mingw/SDL3-3.4.16/i686-w64-mingw32`).
`port_gen.py` runs as a build step after `game_build.py --stage`.

## Status

2026-10-18: `tools/port_gen.py` translates all 653 C units of the Amiga build's compile
plan; 651 compile with i686 gcc without errors (two need port versions: the Aztec `_main`
startup and `_exit`, both with inline 68000 assembly; four more reach custom chips or the
CIA through raw addresses). The materialization assembly (1,450 measured BSS reservations,
symbol aliases) becomes `materialization.s`, and every DATA/BSS symbol then resolves. A
trial link leaves 133 undefined names - the platform surface:

* about 70 OS calls (exec, dos, graphics, layers, intuition, icon) and the library bases;
* the Aztec runtime pieces the game binds by name (`segload`/`freeseg` overlay loading -
  a no-op here, everything is linked - `movmem`, `index`, `argc`/`argv`, `devtab`, `errno`);
* about 50 entry points of the reconstructed assembly (audio driver, Paula interrupt
  handlers, VBlank server and callbacks) and the CODE-data tables they read;
* one unrecovered code fragment (`F_h00_4692`) and the startup/exit versions.

Later on 2026-10-18 the port links and runs (port/README.md): it boots through the
office scene with the original graphics, copper palette and text. Found the hard way:

| Amiga behaviour | What went wrong | Where it is reproduced |
|---|---|---|
| the game indexes across DATA providers (`G_h01_27E4[n]` runs into `27E8`...) | separate C globals: wrong cells, crash | `data_hunk.c`: the whole DATA/BSS hunk as one structure at original offsets |
| the game carves blocks from its own MemHeader pool and checks them on free | host-heap blocks: BAD POINTER, shutdown | exec `Allocate`/`Deallocate` on the MemHeader |
| `request_disk` walks DOSBase->dl_Root->rn_Info->di_DevInfo | NULL DOSBase: crash | `dos_init`: DosLibrary, RootNode, DosInfo, volume nodes |
| little-endian file fields are swapped in memory for the 68000 | `LoadIT() - Unknown block type` | `override/resident_F_2D66.c`, `2DBA.c`: assemble the value from bytes |
| VBlank colour cycling writes into the copper list | (would freeze the palette) | `MrgCop` builds the colour MOVEs at the layout it expects |
| a byte alias names the low byte of a big-endian `int` (`G_h01_0971` = low byte of `G_h01_0970`, the bitplane depth) | every sprite BitMap got Depth 0: no sprites, no speech bubbles | `port_gen.byte_order_aliases`: narrower views inside scalars move to the host byte |
| BltMaskBitMapRastPort indexes its minterm as source, mask, destination (0xE2 = cookie-cut) | (sprites would have been OR'd onto the background) | `F_h00_4692` in `os_graphics.c` |
| byte views of words elsewhere: 7 interior names, 4 address casts, cave cells, animation descriptors (byte-order audit above) | (would have broken the LZW decoder, the ov10 cave and the ov11 animations) | `port_gen` byte-order rules |

## The reconstructed assembly, translated

`tools/asm_port.py` (run by `port_gen.py`) translates the RECONSTRUCTED_ASM modules - the
audio driver, the four Paula interrupt handlers, the VBlank server and its colour
callbacks - and the TYPED_CODE_DATA tables (scores, envelopes, selectors) mechanically, so
the port plays the reconstructed driver itself rather than a rewrite of it:

* every instruction becomes one labelled C statement on the register file of
  `port/m68k.h`, with the condition codes the following branch reads;
* original addresses come from instruction sizes and the assembler's span-dependent
  branch sizes, plus two Manx rules found in the build's bytes: a `public` declared
  outside `dseg` is addressed `d16(a4)`, and `jsr label` assembles PC-relative. Every
  address-named label and every label in `build/game/DuckTales.sym` (700) is checked
  against the computed layout;
* a code address is `M68K_CODE_BASE` + its original offset. The DATA hunk's jump tables
  (`recon_h00_544C + 200`) and the Interrupt structures hold these keys and
  `m68k_run()` dispatches them; the five entries the C code calls get C wrappers that
  push their arguments as Aztec C does;
* memory is host-order (the DATA hunk and heap hold what the C code wrote), except the
  tables, which keep their big-endian bytes (32-bit references patched in at start), and
  0xDFF000-0xDFF1FF, the custom chips (`port/paula.c`);
* one lock serializes the driver's entries from the game thread, the VBlank timer, the
  audio callback (Paula's block interrupts) and the input handler, as one CPU did.

Paula starts with DMA and interrupts master-enabled, as the OS leaves them; the driver
never sets those bits itself. With the driver running, the title screen stays until its
tune ends (about 66 seconds) before the office scene, as on the Amiga; the silent stub
had skipped that wait.

Known difference: the build's audio tables still miss about 200 bytes of RAW_ORACLE_DEBT
inside typed scores and envelopes (for example 26 bytes in `score_1836` at original
0x19F8, which the build leaves out, shifting what follows) and about 420 typed-table bytes
differ from the original (`build/game/diff.json`). Some tunes or effects can play
differently from the original until those spans are recovered as typed data.

Record/replay and the verification canary: above (2026-10-18). Next: inputs timed by consumption, then wider scripts (docs/NEXT.md).
