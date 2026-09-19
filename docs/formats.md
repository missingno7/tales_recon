# Supported evidence formats

`tools/ofs.py` supports these supplied DD, 512-byte-sector, non-international
DOS0 OFS disks. It rejects other geometries, FFS, links, directory cache variants,
invalid/cyclic/shared block chains, invalid directory hash buckets, malformed
metadata, bad block checksums and inconsistent file sizes. It validates the
single DD bitmap and reports boot checksum/bitmap-validity observations.
Dates retain their raw Amiga fields and an unspecified-timezone interpretation.
Text metadata uses Latin-1; file content is never decoded/re-encoded in extraction.

`tools/hunk.py` reads HEADER, CODE, DATA, BSS, END, OVERLAY and BREAK, the classic
relocation forms, NAME/UNIT, SYMBOL, DEBUG and the implemented EXT variants.
Only HEADER/CODE/DATA/BSS/END/OVERLAY/BREAK/RELOC32 are exercised by these fixtures.
Other record variants are provisional support, not established historical facts
about DuckTales. Unsupported record flags/types/EXT forms fail at their offset;
LIB and INDEX containers are intentionally unsupported. DREL32 is interpreted
in load-file context as the short-relocation compatibility form, not an object
file DREL32. This parser is not yet an archive/object-module parser.

The Manx overlay decoder is deliberately specific to the measured dialect:
length is an upper bound; descriptor count includes an empty slot; trampoline
node IDs are one-based. The reference manual's illustrative count/index wording
differs here. File offsets, symbol descriptors, trampoline encodings, bridge
relocation and overlay target bounds are checked against one another. No runtime
load/unload behavior has yet been traced.

File offsets, hunk-relative offsets, disk block indices, slot indices and node
IDs are separate quantities. JSON offsets are decimal; prose may use hexadecimal.
All byte ranges are start-inclusive, end-exclusive. Hunk allocations include
zero-fill tails; executable file-size accounting excludes those virtual bytes.

The asset inventory hashes `.arc`/`.as` content, records leading signatures and
links exact embedded filenames. It does not identify a compression algorithm or
infer a container format merely from an extension.
