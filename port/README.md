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
| `main.c` | SDL3: window and presentation of the loaded View, keys to the joystick, the 50 Hz VBlank, the game thread, `--shot` |
| `adf.c` | the two original disk images (OFS), mounted as DT1: and DT2: |
| `os_exec.c` | memory (including exec's Allocate/Deallocate on the game's own pool), lists, ports, input.device, interrupts, libraries |
| `os_dos.c` | Open/Read/Seek/Close/Delay and the DOS volume list the game walks |
| `os_graphics.c` | graphics and layers on planar bitmaps: blits (minterms, masks), lines, fills, text, View/copper |
| `os_misc.c` | intuition and icon as far as the game uses them |
| `runtime.c` | Aztec runtime pieces bound by name (segload/freeseg: everything is linked in) |
| `m68k.h`, `m68k.c` | what the translated 68000 assembly (`tools/asm_port.py`: audio driver, Paula interrupt handlers, VBlank server, colour cycling) runs on: registers, condition codes, memory with big-endian tables, entries from C and from interrupts |
| `paula.c` | the custom chip registers and Paula's four DMA sound channels, mixed into an SDL3 audio stream |
| `asm_ports.c` | kprintf (the one assembly routine with a hand-written port version) |
| `override/*.c` | port versions of game functions that touch hardware registers or swap bytes for the 68000 |
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
ducktales.exe [--data DIR] [--log] [--wav FILE] [--shot FILE.bmp:MS ...]
```

Arrow keys move the joystick; Space, Ctrl or Enter is fire; every key also reaches the
game's own input handler as an Amiga raw key. `--wav` records the sound output. `--log` writes OS calls and
the game's own kprintf messages to stderr (otherwise to `ducktales.log`); `--shot` saves
the exact 320x200 picture at MS milliseconds (the last shot ends the run).

## Status

Plays the title (with its music) and the office scenes with the original graphics,
sprites, palette, text and sound. Pending: record and replay, the levels and minigames in
play.
