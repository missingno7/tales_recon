# Toolchain candidates

No compiler, assembler, linker or runtime has been selected as the historical
toolchain. `docs/toolchain.json` records current evidence and acquisition status.
The supplied 5.0a ZIP is pinned in `candidate-lock.json`; `acquisition.json`
records local delivery separately from the catalog URL. The first pin establishes
identity, not historical selection. The original and normalized ZIPs stay ignored.

`acquire_candidate.py --from toolchain/aztecc50a.zip` imports without network
access. `inventory_candidate.py --write --extract` inventories every validated
disk and extracts only those disks beneath `installed/aztec-5.0a`. Disks 1, 2
and 4 validate; disk 3 fails and is not extracted. `--check` verifies the inventory.
No program from this archive has been executed. The ROM member is only hashed.

The supplied cc/as/ln are Amiga HUNK files. They cannot run directly on Windows.
See `docs/windows-tools.md` for native alternatives and measured local tool status.

Keep PROVEN_HISTORICAL, LIKELY_HISTORICAL, COMPATIBLE_TOOL and ANALYSIS_ONLY
distinct. A modern tool's useful output does not make it historical.
Eventually a Windows controller should drive a pinned Amiga-only worker under
WinUAE when necessary, retaining source, flags, tools, generated assembly,
objects, linker logs, output and first mismatches for every experiment.
