# DuckTales — the SDL3 port

One executable, `ducktales`, that plays DuckTales: The Quest for Gold on a modern
system. It runs the reconstructed game - the code `tools/game_build.py` builds for the
Amiga, unchanged - on an emulated Amiga: the game still builds its own View and
bitplanes, installs its VBlank server and input handler, and calls graphics, layers,
intuition, exec and dos; the platform below turns that into an SDL3 window, input and
files. Design: [../docs/sdl3-port.md](../docs/sdl3-port.md).

## How it is put together

```
src/ (recovered sources)
   |  tools/game_build.py stages the Amiga build's translation units (build/game/)
   |  tools/port_gen.py translates them -> build/port-gen/ (never committed),
   |  tools/asm_port.py the reconstructed 68000 assembly and its tables:
   |    16-bit types kept (int -> int16_t ...), the DATA hunk at its original layout
   |    (data_hunk.c), port/override/ units swapped in
   v
ducktales.exe = game + emulated Amiga (port/*.c) + SDL3
```

| File | Part |
|---|---|
| `amiga.h` | Amiga OS structure layouts as the game sees them (2-byte alignment, 4-byte pointers) and the platform interface |
| `main.c` | the game's clock (one tick per PAL frame, run on the game thread: Paula, VBlank servers, inputs), record/replay, state dumps, SDL3 window, presentation and keys |
| `adf.c` | the two original disk images (OFS), mounted as DT1: and DT2: |
| `os_exec.c` | memory (AllocMem and the OS structures from one fixed arena with exec's Allocate/Deallocate, so addresses are the same every run), lists, ports, input.device, interrupts, libraries |
| `os_dos.c` | Open/Read/Seek/Close/Delay and the DOS volume list the game walks |
| `os_graphics.c` | graphics and layers on planar bitmaps: blits (minterms, masks), lines, fills, text, View/copper |
| `os_misc.c` | intuition and icon as far as the game uses them |
| `runtime.c` | Aztec runtime pieces bound by name (segload/freeseg: everything is linked in) |
| `m68k.h`, `m68k.c` | what the translated 68000 assembly (`tools/asm_port.py`: audio driver, Paula interrupt handlers, VBlank server, colour cycling) runs on: registers, condition codes, the registered guest memory (big-endian tables; an access outside it is a verification fault), entries from C and from interrupts |
| `paula.c` | the custom chip registers and Paula's four DMA sound channels, one frame at a time on the game's clock, pushed to an SDL3 audio stream |
| `asm_ports.c` | kprintf (the one assembly routine with a hand-written port version) |
| `override/*.c` | port versions of the few game functions the port cannot run as recovered: the Aztec startup and exit (inline assembly), the blitter plane union, two little-endian file-field readers. Hardware register reads are translated (`port_gen.py hardware_reads`), not overridden |
| `include/aztec.h` | the Aztec C data model for the generated game code |

## Build

MinGW-w64 **i686** gcc and CMake (`C:/msys64/mingw32`), SDL3 3.4.16 MinGW package
(`SDL3_ROOT` in `CMakeLists.txt`). The Amiga build must have been staged first:

```
python tools/game_build.py --build
cmake -S port -B build/port -G Ninja
cmake --build build/port
```

## Run

Put `ducktales.exe` and `SDL3.dll` next to the two original disk images (`*.adf`), or:

```
ducktales.exe [--data DIR] [--log] [--wav FILE] [--headless] [--strict] [--ticks N]
              [--record FILE] [--replay FILE] [--dump DIR:FROM:EVERY] [--shot FILE.bmp:TICK ...]
```

Arrow keys move the joystick; Space, Ctrl or Enter is fire; every key also reaches the
game's own input handler as an Amiga raw key. `--wav` records the sound output. `--log` writes
OS calls and the game's own kprintf messages to stderr (otherwise to `ducktales.log`).

A run is a function of its inputs (docs/sdl3-port.md, "Determinism"): `--record FILE` writes
every external input (joystick, fire, keys, RNG seeds) and the sound commands, timed in poll
frames (the steps of the game's input reading); `--replay FILE` plays such a log - also one
`tools/game_boot.py` recorded from the original in WinUAE. `--headless` runs without window,
sound device or real-time pacing, `--ticks N` ends after N frames, `--dump DIR:FROM:EVERY`
dumps the DATA/BSS hunk at poll frames for `tools/game_compare.py --port`, `--shot
FILE.bmp:TICK` saves the picture at a tick. A guest memory access outside the game's memory
is a fault: logged, exit status 3, and `--strict` stops the run at the first.

## Status

Plays the title (with its music) and the office scenes with the original graphics,
sprites, palette, text and sound; record and replay are exact (2026-10-18). Pending: the
levels and minigames in play.
