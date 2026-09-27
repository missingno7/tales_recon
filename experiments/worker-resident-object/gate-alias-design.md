# FFP gate-only call-target alias design audit

## Finding

A strict, opt-in alias for the five call-entry addresses is defensible as an independent call-target identity for `ov11_F_5FB2`. It would not establish ownership of the shared dispatcher or exact `m.lib` object provenance. It can support only the existing function-level obligation to resolve the five external call targets; it cannot by itself satisfy `FUNCTION_CODE_MATCH`, which still requires a complete byte comparison and independent resolution of every remaining relocation/reference.

## Independent identity evidence

The pinned Aztec 3.6a `ffp.arc` source names `.Ffix`, `.Fflt`, `.Fsub`, `.Fmul`, and `.Fdiv`, pushes their `_LVOSP*` vector immediates, then jumps to the common `amiga_ffp` dispatcher. The vector values are distinct: -30, -36, -72, -78, and -84 respectively. The linked m.lib probe's symbol map places these exact symbols at HUNK0 `0x810`, `0x82e`, `0x81a`, `0x838`, and `0x824`, with `amiga_ffp` at `0x842`.

The five 10-byte generated m.lib entry stubs are exactly equal to original HUNK0 `0x8d00..0x8d32`, by entry, after pairing symbols with the unique push immediates. Each final `jmp` displacement targets the common dispatcher: original displacements `+0x2a,+0x20,+0x16,+0x0c,+0x02` all land at `0x8d32`; the linked m.lib entries have the same bytes and land at `0x842`. A read-only whole-HUNK0 scan found each 10-byte original signature exactly once, at its corresponding entry. Thus the entry mapping has distinct names, distinct vector IDs, exact bytes, a verified common branch destination, and unique original locations.

The exact mapping is:

| Aztec symbol | Original identity | Original h00 offset | Vector |
| --- | --- | ---: | ---: |
| `.Ffix` | `resident_F_8D00` | `0x8d00` | -30 |
| `.Fsub` | `resident_F_8D0A` | `0x8d0a` | -72 |
| `.Fdiv` | `resident_F_8D14` | `0x8d14` | -84 |
| `.Fflt` | `resident_F_8D1E` | `0x8d1e` | -36 |
| `.Fmul` | `resident_F_8D28` | `0x8d28` | -78 |

F5FB2 has seven A4-relative JSR sites targeting these five entries: `.Fflt` at `0x5fce`, `0x5fe0`, and `0x5ffe`; `.Fsub` at `0x5fe8`; `.Fmul` at `0x6006`; `.Fdiv` at `0x6010`; `.Ffix` at `0x6014`. The existing evidence ledger resolves those sites to the corresponding original h00 target offsets.

## Existing comparator boundary

`function_compare.py` currently resolves A4 references using mechanical target names and only adds runtime aliases returned by `runtime_arithmetic.aliases`. That function intentionally requires an entire linked/original contribution hash, complete bounds, matching library identity, and relocation-free code. The FFP gates do not satisfy that full-contribution policy: only the ten-byte entry ranges match; dispatcher operands differ with A4/runtime link context. Reusing the current full-runtime alias path would improperly imply the 130-byte dispatcher contribution is identical.

A separate gate-only identity map can fit the proof-level policy because it resolves only the call target address through independently measured bytes and source/archive symbol correspondence. The normalization must remain at the caller's A4 call-site operand and must not extend the alias range beyond each ten-byte entry.

## Required strict checks for an opt-in rule

- Require the pinned Aztec 3.6a profile and the exact `m.lib` SHA-256; reject other profiles/libraries or missing library identity evidence.
- Require exactly one HUNK0 CODE definition for each `.F*` symbol in the linked artifact, with an in-bounds ten-byte entry; require no duplicate/ambiguous symbol mapping.
- Compare each generated ten-byte entry exactly to the single independently evidenced original HUNK0 signature. Check opcode, vector immediate, full JSR/JMP encoding, and that its computed branch target equals the linked `amiga_ffp` symbol; independently check the original branch target equals `h00+0x8d32`.
- Require the one-to-one name/vector/target table above. Confirm each original signature is unique in original HUNK0. Do not alias `amiga_ffp`, any dispatcher tail, strings, or a shared extent.
- At each candidate call site, prove the actual A4 displacement or relocation resolves exactly to the corresponding `.F*` symbol address, then map only that address to the matching mechanical original entry identity. Do not accept a pointer into the middle of a gate or a different gate with similar shape.
- Record this as a gate-entry / call-target identity proof, not runtime ownership or exact library-object provenance. Do not count these gate bytes as newly reconstructed game bytes or use them to claim dispatcher bytes.
- Continue requiring complete F5FB2 code equality, matching length/layout, and all non-gate relocation and data identities before granting `FUNCTION_CODE_MATCH`.

This design audit made no comparator, canonical-source, or ledger edits.
