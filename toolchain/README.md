# Toolchain candidates

No compiler, assembler, linker or runtime has been selected as the historical
toolchain. `docs/toolchain.json` records current evidence and acquisition status.
`acquire_candidate.py` downloads only the explicitly identified research ZIP,
hashes it and inventories member hashes. It neither extracts nor executes tools.
The first pin is trust-on-first-use; it proves identity, not historical selection.

Keep PROVEN_HISTORICAL, LIKELY_HISTORICAL, COMPATIBLE_TOOL and ANALYSIS_ONLY
distinct. A modern tool's useful output does not make it historical.
Eventually a Windows controller should drive a pinned Amiga-only worker under
WinUAE when necessary, retaining source, flags, tools, generated assembly,
objects, linker logs, output and first mismatches for every experiment.
