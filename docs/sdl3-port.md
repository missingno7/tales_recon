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
| `port/platform.h` | the contract: every OS call, custom-chip/CIA access, interrupt and file the game reaches (from `docs/platform.md`, `recovery/platform.json`) |
| `port/amiga_*.c` | the emulated Amiga: graphics/layers/intuition library calls on a planar bitmap model, Exec memory and interrupts, DOS files on `DT1:`/`DT2:`, Paula audio, joystick/CIA, beam position |
| `port/override/*.c` | C for the RECONSTRUCTED_ASM modules (audio driver, Paula IRQ handlers, VBlank server, frameless helpers) and for any function that reaches hardware through raw pointers |
| `port/replay.c` | record/replay of every nondeterministic platform read (below) |
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
* any access that views a word through a byte pointer (or the reverse) - `port_gen.py`
  reports every such cast so each is reviewed once.

A global-state dump of the port serializes the typed globals (`recovery/data_model.json`)
big-endian under their `G_h01_XXXX` names, so it compares directly with WinUAE state dumps.

## Determinism: record and replay

Everything nondeterministic reaches the game through the platform: joystick and fire
(`JOY1DAT`, CIA-A PRA), keyboard events, the beam position (`VPOSR` - the game reseeds its
RNG from it, `resident_F_4676`), the VBlank tick and DOS `Delay`. The platform records each
such read per game tick into a replay log and can replay a log exactly. A bug report is a
replay log; replay reproduces the run bit for bit on any machine.

## Finding a bug from the lowest layer

1. Replay the log to the failing tick and dump the globals.
2. Find the first wrong value (against expectation, or against a WinUAE state dump of the
   original with the same inputs and pinned RNG seed: `game_boot.py --rng-pin`,
   `game_compare.py --sequences`).
3. Check the one function that wrote it against the original 68000 code with
   `tools/difftest.py` (original CODE run in a CPU emulator vs the C, same memory and
   inputs). No game state has to be reached in play to prove a function.

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

Next: the audio driver, keyboard through the input handler, record/replay, then play.
