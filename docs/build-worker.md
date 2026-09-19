# Historical build worker

The candidate Aztec 5.0a compiler, assembler and linker now execute unattended
using the existing Windows WinUAE installation. This is a toolchain experiment,
not yet a reconstructed game build or evidence selecting the historical release.

From the project root:

```powershell
python tools/aztec_worker.py prepare smoke-new experiments/aztec-smoke --commands experiments/aztec-smoke/commands.json
.\tools\run_worker.ps1 -Job build/worker-jobs/smoke-new
python tools/aztec_worker.py collect build/worker-jobs/smoke-new
```

Use a fresh job name. Preparation validates the pinned distribution and copies
system files into a disposable boot volume. Compiler volumes are read-only;
game disks are not mounted. The runner checks recorded input hashes, starts
WinUAE hidden, waits for the guest marker, and stops only its own process.
Collection checks every guest return code; reaching the marker alone is not
success. The 68020/AGA worker configuration is an execution host, not a claim
about the original game hardware requirements. The supplied ROM stays in ignored
local job directories. Raw compiler/runtime and ROM files are not committed.

Two runs produced an identical naturally linked 2,112-byte executable, SHA-256
`3ae8e00f3fb666edb2397f800636b88e55d50faecd96764911db1c67ba227cd9`.
The independent K&R C arithmetic probe exits zero. The linked file parses fully:
2,012 CODE bytes; 12 initialized DATA bytes in 100 allocated; 4 BSS bytes.
Receipts and logs are under `evidence/experiments/`.

Retained failures: the initial launch lacked the assembler search path; a second
attempt lacked the C library path. Explicit paths resolved these. In smoke-003,
`adump -cdrs probe.o` returned 1 (`got funny code: 434a0000 @ 0`). The object
was accepted by the same distribution's linker. Smoke-004 excludes that separate
object-dumper experiment and all five steps pass. Full local job artifacts remain
under ignored `build/`; hashes and selected textual logs are retained in evidence.

Windows-native analysis dependencies are installed in
`toolchain/installed/host-python`. Download identities are in
`toolchain/host-lock.json`. Capstone wheel version 5.0.9 reports module version
5.0.7; this discrepancy is recorded rather than normalized. The project census
continues to need only Python's standard library. Historical compiler execution
uses WinUAE; disassembly and binary parsing do not need guest execution.

Next: identify candidate runtime object contributions and compare compiler ABI
fingerprints before selecting a toolchain for the complete investment overlay.

Natural overlay linking is now verified; see [overlay experiments](overlay-linking.md).
