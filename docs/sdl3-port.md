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

## Determinism: one clock, inputs at the game's input reads

The port runs everything on the game thread: no timer thread, no audio callback into the
driver, no lock. The game's clock is one tick per PAL frame (71051 colour clocks, 20.0318 ms)
and advances only when the game waits for time (`Delay`, `WaitBOVP`, and busy-waits on
interrupt state). A tick runs, in order, Paula for one frame (its block interrupts run the
driver) and the VBlank servers. Live play paces ticks to real time; `--headless` does not.

What reaches the game from outside (measured from the code, 2026-10-18):

| Input | Where | In the replay log |
|---|---|---|
| joystick and fire | `poll_controller_and_keyboard_input` reads JOY1DAT and CIA-A PRA | `joy`, `fire` |
| keys | the input handler (`input.device`), drained by the same poll | `key` (raw code, bit 7 = release) |
| RNG seed | `seed_random` stores VPOSR + `game_frame_tick` | `seed` (the stored value) |
| time | `Delay`, `WaitBOVP`; busy-waits on the audio driver's channel-0 state `G_h01_2A16` ("until the sound ends") and on `game_frame_tick` | the clock itself |

Nothing else in the game reads interrupt-driven state. VPOSR holds LOF (bit 15) and V8 (bit
0), not the line number, so the seed is 0x8000 + `game_frame_tick` (+1): the frames spent
before the difficulty choice.

**The time base: poll frames.** The 68000 spends frames drawing, decompressing and loading;
the port spends none. Inputs timed in frames therefore reach the two machines in different
states. Inputs, checkpoints and the end of a replay are instead timed in *poll frames*, the
steps of the game's own input reading: a poll starts a new poll frame when the game has waited
for time (`Delay`, `WaitBOVP`) since the current one began, or when it also polled in the frame
just before (a loop polling every frame while a sound plays). Work that spans frames does not,
on either machine. The port counts them in `platform_poll` (called by the first input register
the poll reads - it reads the fire bit before JOY1DAT); `tools/game_boot.py` counts them on
the original with breakpoints at the poll, `Delay`/`WaitBOVP` glue and the VBlank server (below).
Busy-waits get one frame per pass from `port_gen.py` (`spin_waits`; a loop whose body already
waits keeps its own pace) through `platform_spin_frame`, which is not a game wait.

The port runs the recovered input poll and `seed_random` unchanged: `port_gen.py` turns their
16-bit dereferences of custom chip and CIA addresses into `amiga_read16`, so JOY1DAT, CIA-A PRA
and VPOSR are register reads of the emulated chips (`hardware_reads`). Replay hands VPOSR the
recorded seed minus the game clock, so `seed_random` computes the recorded seed itself.

Addresses are run-independent: AllocMem and the OS structures the game sees come from one
fixed arena with exec's algorithm, the executable has a fixed base, and the DATA hunk owns every
cell the runtime knows by name (`_numdev`, `GfxBase`, `DOSBase`, `_argc` ...: `RUNTIME_CELLS`)
and every link-only stub cell. Guest memory is registered (`m68k_memory`); an access outside it
is a verification fault (`platform_fault`): logged, exit status 3, and `--strict` stops the run.

`ducktales --record FILE` / `--replay FILE` (text, poll frames):

```
# from tools/game_boot.py: WinUAE inputs at the poll frame that read them
1015 fire 0001
1016 fire 0000
0 seed 8000
0 seed 8aa6
1 sound 0001
1015 sound 0000
1082 end
```

`sound` lines (the sound commands the game issued) are events for comparison; replay ignores
them. `--dump DIR:FROM:EVERY` dumps the DATA/BSS hunk at the first poll of every EVERY-th poll
frame, with the guest regions in `state-layout.json`; `--shot FILE.bmp:TICK`; `--ticks N`.

**The original and the build, driven the same way.** `tools/game_boot.py run --poll-dumps N`
drives WinUAE by events instead of frame steps: it runs to the next watched entry - the input
poll, `seed_random`, `play_sound`, the `Delay`/`WaitBOVP` glue, the VBlank server - and acts
there: at a poll that starts a poll frame it injects the inputs due (the poll reads them at
once - measured: fire injected at the entry is in the poll's result), counts it and dumps every
N-th; at `seed_random` it takes (or pins) the seed exactly; at `play_sound` it records the
command. Frames without polls run at emulation speed. (A frame step cannot do this: with a
breakpoint armed, WinUAE's frame steps run past their target line, and its memory watches do
not fire during frame steps; debugger stops do not change the emulation.) With `--input` (a
frame-stamped script) a run writes `port-replay.log`; with `--replay LOG` it is driven by a log,
so one log drives the original, a build and the port.

## Verification: what is proven, and how to find the first divergence

Measured 2026-10-18 with `evidence/trace/title-to-money-bin.json` (title, office, Money Bin,
difficulty choice, company/location setup, contest screen; 6,000 emulated frames = 1,082 poll
frames, turbo floppy). One log, `title-to-money-bin.poll.log`, recorded from the original,
drives all three machines.

| Claim | Evidence | Result |
|---|---|---|
| The original replays identically across fresh WinUAE sessions | fixed emulated start (`START_CCK`), frame-stepped and poll-driven runs | identical: CPU and beam on every frame, every dump, the same seeds; three poll-driven sessions wrote the same log |
| The log replays the original exactly | the original driven by its own poll-keyed log (`--replay`) | the round trip reproduces the log: same inputs, poll frames, seeds, sound commands |
| The port replays exactly | the log replayed twice; a live run recorded and replayed | byte-identical: 1,082 dumps (one per poll frame) and screenshots |
| Original vs SDL3 port | the log, a dump at every poll frame (`game_compare.py --port --events`) | **sound commands 23/23 identical (same commands, same poll frames); 1,009 of 1,018 typed globals identical at all 1,082 checkpoints.** The other nine are the audio driver's state (below) |
| Original vs reconstructed Amiga build | the log (`--replay`), every 25th poll frame | sound commands 23/23 identical; 964 of 978 globals identical at all 42 checkpoints; the rest are pointers (compared by value - the build's link layout differs) and the same audio-driver state |
| A wrong rule is caught and located | mutation `% 37` to `% 36` in the treasure assignment (port) | against the original: exactly `location_records` and `location_treasure_slots` differ, from poll frame 1,054 (the first poll after the reseed that shuffles them) to the end; everything else as before |
| A replay proves only what it runs | mutation `>= 35` to `> 35` in `wrap_location_index` | not exercised by this script: no difference |

How the comparison reads state (`tools/game_compare.py`): every typed global of
`recovery/data_model.json` through its type - numbers by value (the port's in host order),
pointers by what they point at (an offset in the DATA hunk, the one region both machines lay
out alike), two addresses elsewhere as *incomparable* (listed, never counted as a match),
a number never as an address; the three dos.library file handles as open/closed; the Aztec CLI
startup's argument cells and device table (`_argc`, `_argv` ...) listed as launch environment,
since the port starts without a CLI. Every category is printed in the report.

What still differs, and why:

* **The audio driver's own state** (block countdowns, sample cursors, the channel-0 stream
  pointer): audio advances with real frames, and at the same poll frame the original has spent
  more frames (its work between polls), so its sounds are further along. The sound commands the
  game issues are identical; what the game reads back - "has the sound ended", in busy-waits - did
  not change any game state in this script. A test that waits on a sound with work in the loop
  body would show it.
* **Load-time and work-time are not modelled**, by design: the port does instantly what takes
  the 68000 frames. Gameplay that counts loop passes *until a sound ends* (an animation that
  runs while a tune plays) can make more passes in the port; this script has none that change
  state.

Finding the first divergence: replay the log on both, `game_compare.py ORIG PORT --port` with a
dump at every poll frame (`--poll-dumps 1`, `--dump .:1:1`), take the earliest global that
differs at every lag, then the function that writes it - against the original 68000 code with
`tools/difftest.py` where it is a single function. Found this way so far: the envelope table
bound to an older compact copy in the build (sound 6 read data as a pointer), Paula raising its
start interrupt too early (the driver lost one block count), the fire bit read before the poll
frame started (a press seen one poll late), a busy-wait rule stretching loops that already
wait, and runtime cells (`_numdev`, the library bases) living outside the DATA hunk.

Recording a human playthrough: play the original in WinUAE with `game_boot.py` or the port
with `--record`; the poll-keyed log replays on the original, the build and the port. Recording
in the original is the reference: its log is the input the other two must reproduce.

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
| `runtime.c` (`segload` no-op), overrides | C | overlays, Aztec startup/exit, the blitter plane union, little-endian file fields | the input poll and `seed_random` overrides are gone (2026-10-18: the recovered functions run unchanged, their hardware reads go to the emulated chips); the rest go when their callers are rewritten |
| record/replay, dumps, guest-memory checks | D | nothing | stays as the verification harness, outside the game proper |

Removed so far: the timer thread, the audio-callback interrupts and the driver lock (one
thread, a fixed order: the port became reproducible); the hand-written copies of the input poll
and `seed_random` (91 + 15 lines: the recovered functions run unchanged, with hardware reads
translated by `port_gen.py`); the port's separate definitions of runtime cells (the DATA hunk
owns them).

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
