# AJ external-fixup audit: `ov11_F_5FB2`

Read-only object audit; no parser/comparator changes or canonical edits.

## Specimen

- Cached Aztec 3.6a candidate object: `build/compile-cache/7db436d7e179481ad2d8cc553d997c224ba873da5704d5f059cb0bf0ac2e1e1a/t000.o`
- Object SHA-256: `178672e209c63e9d3e60d4c4bf09875ac7c71c135914eb39c7e72df524198920`; size 468 bytes; AJ magic, successful assembler/link return codes.
- Immutable link receipt: sibling `receipt.json`; isolated comparison receipt: `results/ov11_F_5FB2/95dc8eb042af0ee0b8ddd0d6632686be84dce595fee6e92b80dd01364f45fbe6-aztec36-7db436d7e179.json`.

## What the bytes establish

The object trailer begins at file offset `0x124` with `F5 00 00 00 02`. Its records contain the NUL-terminated private names `.Fflt`, `.Fsub`, `.Fmul`, `.Fdiv`, and `.Ffix` (name starts at `0x15B`, `0x165`, `0x16D`, `0x175`, and `0x17D`). The name records are preceded by repeated raw `07 08 00 00` sequences. Other external names, including `_G_h01_94BE`, appear in the same trailer with `07 0A 00 00` prefixes. The fixed header also contains 32-bit values `0x0D` and `0x09` at offsets `0x14` and `0x18`; without a format decoder, these are observations, not interpreted counts.

The compiler assembly (`t000.asm`) emits seven private-helper calls, corresponding to comparison offsets 28 `.Fflt`, 46 `.Fflt`, 54 `.Fsub`, 76 `.Fflt`, 84 `.Fmul`, 94 `.Fdiv`, and 98 `.Ffix`. Thus the object demonstrably names all five helper symbols, but this audit does **not** demonstrate that the external records encode all seven individual sites or their fixup widths. In particular, `.Fflt` occurs once in the named trailer while representing three calls, so its name alone is insufficient.

## First parser obstacle and proof still needed

The repository's object handling only checks `AJ`/`CJ` magic and reads size fields in `tools/compiler_oracle.py`; its HUNK parser handles the linked executable, not Aztec AJ external records. The trailer's marker/type/prefix meanings and the call-site offset lists are not currently decoded or validated. Therefore there is no byte-backed per-site width mapping to feed the seven unresolved `A4_IDENTITY` checks.

A format-aware AJ parser looks feasible as a bounded extension: records are NUL-terminated and typed-looking prefixes repeat, while the source assembly and linked symbols provide independent cross-checks. It must first establish grammar/endianness and decode reference counts, site offsets, and widths from a tiny synthetic one-call object before parsing this multi-call object; this audit did not attempt that experiment.

Even after object parsing, linked binding remains separate: prove that each final call-site operand resolves to its specifically named `.F*` definition in this link, then independently map those five distinct linked gate identities to original hunk-0 offsets `0x8D00`, `0x8D0A`, `0x8D14`, `0x8D1E`, and `0x8D28`. The existing linked symbol map and byte-identical gate study establish candidate definitions/signatures, but the current final-link comparison has no per-call actual relocation identity. Keep `DIFFER`; do not waive the seven missing identities based on symbol presence alone.
