# Initial disk and executable findings

All measurements here derive from the SHA-256-locked supplied disks. The parser
does not mount or modify either filesystem. It checks block checksums, parent
links, directory hash buckets, extension chains, sequence numbers, exact sizes,
bitmap allocation, and agreement between both OFS file traversal methods.

DT1 contains 27 files; DT2 contains 12. Neither has allocated blocks left
unaccounted for by the census. The raw bitmap-validity fields are retained,
including DT2's value 1. The boot checksum passes for DT1. DT2's boot area has
an invalid checksum and a raw root pointer of `0x444f5302`; filesystem traversal
uses the DD geometry's root block 880. This does not establish DT2 as bootable.
No repair is made or needed for extraction.

DT1's `s/startup-sequence` contains exactly:

```text
DuckTales
endcli >nil:
```

The executable consists of 65 records occupying all 193,004 bytes. Its root
header declares a 16-entry hunk table and resident hunks 0–2. The later headers
retain their raw table-size fields; those must not be rewritten using generic
assumptions about non-overlay executables.

| Hunk | Container | Initialized bytes | Allocated bytes |
| --- | --- | ---: | ---: |
| 0 | resident CODE | 36,260 | 36,260 |
| 1 | resident DATA | 11,956 | 46,044 |
| 2 | resident BSS | 0 | 4 |
| 3 | overlay CODE | 5,952 | 5,952 |
| 4 | overlay CODE | 10,768 | 10,768 |
| 5 | overlay CODE | 23,648 | 23,648 |
| 6 | overlay CODE | 4,352 | 4,352 |
| 7 | overlay CODE | 8,352 | 8,352 |
| 8 | overlay CODE | 16,504 | 16,504 |
| 9 | overlay CODE | 11,384 | 11,384 |
| 10 | overlay CODE | 13,516 | 13,516 |
| 11 | overlay CODE | 29,376 | 29,376 |
| 12 | overlay CODE | 3,012 | 3,012 |
| 13 | overlay CODE | 3,968 | 3,968 |
| 14 | overlay CODE | 1,544 | 1,544 |
| 15 | overlay CODE | 5,732 | 5,732 |

The sum of allocations is 220,416 bytes, not a measured simultaneous RAM
requirement. CODE/DATA allocations request CHIP memory (`0x40000000` flags);
BSS has no memory flag. Root DATA contains executable dispatch stubs, so a
HUNK_DATA label alone cannot justify classifying all its initialized bytes as data.
The DATA tail is uninitialized storage; its original C/common ownership is unknown.

There are 916 relocations from hunk 0, 342 from hunk 1, 185 from hunk 4, and 2
from hunk 11. All are RELOC32. Their target hunk identifiers and source bounds
validate. This does not mean a reconstructed source has resolved any relocation.
HUNK_EXT, HUNK_SYMBOL and HUNK_DEBUG are absent, as are the other unencountered
record types listed in `hunks.json`.

The overlay table begins at file offset `0xd074`. Its length field is 54,
meaning 55 payload longwords. It has 14 descriptors; descriptor index 3 is
zero-filled. Thirteen descriptors resolve exactly to the thirteen subsequent
HUNK_HEADER records. The additional BREAK at `0x17274` between ov05 and ov06
is preserved as its own record. Association with the empty descriptor is a
plausible linker interpretation, not an observed runtime event.

The 26 trampolines span hunk 1 offsets `0x248..0x318`. Each begins with BSR.W;
the next four bytes contain a node ID and a 24-bit target offset. Their branch
targets converge on the JMP bridge at `h01+0x318`, whose RELOC32 points to
`h00+0x798a`. Every exported target lies inside its assigned overlay hunk.
The node IDs are 1–14 with 4 absent. These are table-slot IDs and must not be
confused with logical hunk numbers.

The bytes `MANX` occur at `h00+0x76d6` (file `0x76fe`). Together with the table
and trampoline structure they establish strong Manx overlay ABI evidence.
They do not select a compiler release, optimization flags, library objects,
source filenames, or a particular source language for every routine.

ov07 has exported offsets 0 and `0x1a02`, investment asset anchors, and portfolio
text. The semantic label is reconstructed. Its complete function boundaries,
data layout, external-call ownership and original compilation-unit structure
remain unresolved. No matching-source proof has been assigned.

The byte map partitions every allocated hunk without gaps or overlaps. Only
the structurally validated overlay glue, exact asset-name strings, and
uninitialized storage receive classifications at this stage. Printable byte
runs remain candidates: some include instruction bytes that happen to be ASCII.
The instruction database covers the 26 BSR.W instructions and one JMP bridge;
it deliberately does not disassemble all CODE payloads linearly.
