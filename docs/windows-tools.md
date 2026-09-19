# Windows host tools and the supplied Aztec candidate

The analysis workflow can run on Windows without an Amiga emulator. Running
the supplied historical compiler is a different requirement: `cc`, `as` and
`ln` are Amiga/m68k HUNK programs, not Windows PE binaries.

## What is available

| Tool | Run on Windows without guest emulation? | Local status and use |
| --- | --- | --- |
| Project Python census/comparison tools | Yes | Already running; original disks and HUNK metadata are parsed as data |
| Capstone | Yes | Installed project-locally; M68K decode executed successfully on Windows |
| Ghidra | Yes, on a Windows JVM | Supports 68000 analysis; JDK is present, Ghidra installation not established by the bounded scan |
| amitools `xdftool` / HUNK analysis | Python, no guest CPU required | Installed project-locally (0.8.1); upstream cautions that Windows is lightly tested; independent fixture checks pending |
| VASM and VLINK | Yes, Windows cross-tool builds exist | Not found on PATH; useful for assembly/HUNK experiments; Manx overlay reproduction unproven |
| VBCC | Yes, Windows cross-compiler builds exist | Not found on PATH; different compiler, not a substitute for historical Aztec code generation |
| Local MinGW GCC / make | Yes | GCC 12.2.0 and Windows GNU Make 4.4 execute; useful to build host utilities, not an installed Amiga cross-compiler |
| Local GNU objdump | Yes, but this build is not useful for 68k decoding | Its `-i` output exposes x86/iamcu targets, no m68k backend |
| Supplied Aztec 5.0a `cc` / `as` / `ln` | No | Amiga HUNK files; require an Amiga/m68k execution environment |
| Aztec C68K/ROM DOS cross-compiler | No on this modern 64-bit Windows host without a DOS execution layer | Separate historical product; DOS-hosted does not mean a Windows-native executable or Amiga overlay linker |
| vamos | No: still emulation | Smaller command-line CPU/AmigaOS emulation layer; may avoid full Workbench/WinUAE, but Windows support and these tools need validation |
| WinUAE | Emulator | `C:/Program Files/WinUAE/winuae64.exe` runs hidden unattended worker jobs; compile/assemble/link/run verified |

Native here means the host utility runs as a Windows process (including Python
or Java); it does not mean it executes the game's 68000 instructions directly.
No new packages were installed and none of the historical tools were executed
for this audit. Local paths, PE classification, binary hashes, command outputs
and the limited discovery scope are in `evidence/toolchain/windows-host.json`.

Capstone's upstream lists M68K and Windows support. Ghidra's upstream provides
Windows launchers and a 68000 processor module. The `kusma/amiga-dev` package
maintainer documents a Windows VBCC/VASM/VLINK distribution. These are capability
references, not pins or endorsements of those particular package versions:

- [Capstone upstream](https://github.com/capstone-engine/capstone)
- [Ghidra upstream](https://github.com/NationalSecurityAgency/ghidra) and
  [68000 processor](https://github.com/NationalSecurityAgency/ghidra/tree/master/Ghidra/Processors/68000)
- [amitools upstream](https://github.com/cnvogelg/amitools) and
  [vamos architecture](https://github.com/cnvogelg/amitools/blob/main/docs/vamos.md)
- [Windows cross-tool package](https://github.com/kusma/amiga-dev)
- [VLINK manual mirror](https://github.com/8l/vlink/blob/master/vlink.texi)
- [Aztec C68K/ROM original DOS-host manual](https://bitsavers.org/pdf/manx/Manx_C68K_ROM_3.6B_MSDOS_Jun88.pdf)

VLINK documents `amigahunk` output, but the inspected manual does not establish
support for this game's Manx flat overlay table, trampolines or private library
format. Generating ordinary HUNK output is insufficient evidence. The bundled
Manx libraries start with `63 6a` (`cj`), not HUNK_HEADER/HUNK_UNIT: their format
still needs investigation before assuming a modern linker can consume them.

## Archive import and findings

The user-supplied `toolchain/aztecc50a.zip` is pinned as:

```text
SHA-256 983d0e6db077fce59aa74f7b1c608ec400da101c8ca56fafe95e72de1e5dfeb7
Size    1,750,110 bytes
```

Its four ADFs and one ROM member are hashed in `toolchain/candidate-lock.json`.
Local delivery is recorded separately from the candidate's museum catalog URL;
the catalog does not authenticate the supplied archive. The ROM member remains
unextracted and unused. The original ZIP is unchanged and ignored by Git.

Disks 1, 2 and 4 pass strict OFS checks: 339 files are inventoried and extracted
under `toolchain/installed/aztec-5.0a/`. The usable tools and 17 libraries have
individual SHA-256 identities. Disk 3 fails on `asm/exec/exec_lib.i`: its chain
reaches block 945, whose data header is zero-filled. The complete disk is
quarantined from extraction. This is a limitation of this candidate archive,
not permission to weaken validation of the original game disks.

The compiler, assembler and linker have embedded 5.0a banners dated January 9,
1990. `Aztec1:read.me` instead carries `01/09/89`. Both observations are retained;
neither proves the game's compiler release. The release notes also say that
5.0a changed register conventions, broke object/library compatibility with
earlier versions and changed the default integer width from 16 to 32 bits.
Consequently 3.6-era tools remain worth investigating and the 5.0a default
configuration must not be accepted as a historical match without experiments.

## Reproduce and proceed

```powershell
python tools/acquire_candidate.py --from toolchain/aztecc50a.zip
python tools/inventory_candidate.py --write --extract
python tools/inventory_candidate.py --check
python tools/audit_windows.py
```

Recommended division: Python/Capstone/Ghidra for host-side archaeology;
VASM/VLINK for explicitly compatible-tool experiments; pinned Aztec tools for
historical compiler/runtime fingerprints, under a validated command-line worker
or WinUAE if required. Do not replace the historical compiler solely to remove
the last emulated build step. No historical toolchain has been selected yet.
