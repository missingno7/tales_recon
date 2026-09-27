# DOS as a secondary source-shape oracle

The Amiga executable remains the reconstruction target and the future SDL3
presentation reference. This bounded DOS pilot tests whether an independent
x86 compiler output can clarify common gameplay C. It neither promotes Amiga
bytes nor starts a matching DOS build.

## Measured container

`assets/dos/DUCKTALE.EXE` (SHA-256
`f5454d4e3b760aede974f6e08f0b441ba5ebae556205ca86e99816da088381a9`)
is 165,218 bytes. Its MZ header declares a 61,787-byte root. The root uses an
observed 16-byte `RB` EXEPACK variant. Strict backward decompression yields an
87,664-byte load image (SHA-256
`47e622175ccf124edab2ed1b5ccb725045d5e54b5766428f8309303fcdf5564d`)
and 659 root relocation sites. Ten sequential, 512-byte-aligned MZ overlay
records, numbered 1–10, occupy the remaining file; their tables contain 1,453
relocations. All file bytes are parsed. The overlay relocation coordinates use
a shared `0x0C17` segment base; the parser retains raw segment:offset pairs and
bounds-checks normalized sites. DOS overlay 1 is a 14-byte stub, not a game
source module identified by name. See [measured structure](../evidence/dos/structure.json).

The unpacked root contains a 1988 Microsoft runtime notice and overlay-manager
diagnostics. Far returns and calls with near global-data operands are consistent
with medium-model C. These are ABI/toolchain clues, not an exact compiler
identification. The [candidate census](../evidence/dos/function-census.json)
uses Capstone x86/16 recursive traversal from overlay entry zero and BP-frame
patterns: 165 candidate entries, 146 closed CFGs. A frame pattern may be data
or an interior sequence; candidate extents claim no source ownership. The root
has not been assigned a complete function map, and no C/ASM/runtime byte
percentage is claimed.

## Controlled compiler evidence

The [paired source hypothesis](../experiments/dos/ov10_shared_pair.c) contains
the two expressions already exactly matched on Amiga as `ov10_F_2B8A` and
`ov10_F_2BAC`. MSC 5.10 with `/AM /Os` emits one 66-byte CODE object with
publics at offsets 0 and 33. That full 66-byte span matches DOS overlay 6
at `0x2390..0x23D2` at every byte outside its six OMF-declared external fields.
Both references to each DOS global resolve to the same observed word, and both
pointer32 stack-check calls predict exactly the MZ relocation sites in the
span. MSC 5.00 emits 68 bytes and differs in the `AND` encoding; MSC 6.00a
emits 60 bytes and chooses byte loads. The comparison and all tool hashes are
in the [pair receipt](../evidence/dos/pair-receipt.json). This strongly favors
MSC 5.10 code generation for these game functions, but it does not uniquely
prove the historical release or the complete original DOS translation unit.

Two Amiga `ov09` functions independently correlate with adjacent DOS overlay 7
functions. Under the same MSC 5.10 profile, `ov09_F_1924` emits the complete
44-byte DOS body after its declared stack-check binding, including a matching
MZ relocation. `ov09_F_18D0` emits all 61 DOS body bytes after declared
external bindings; its standalone object then adds one `90` alignment byte,
which is **not** claimed as part of the DOS function. Loop bound 6, row stride
10, and subtraction 16 agree. See the [specimen receipts](../evidence/dos/specimen-receipts.json).
The [correspondence map](../evidence/dos/correspondence.json) keeps stronger,
weaker, and divergent links separate. The broader eight-source search also
records non-matches and low-specificity mnemonic rankings in
[cross-probe results](../evidence/dos/cross-probe.json).

One useful limit is visible immediately: the next DOS overlay 6 function calls
an absolute-value helper twice for row/column distance, while exact Amiga
`ov10_F_2BCA` uses an inline conditional macro. Equivalent gameplay does not
make source spelling or compiler behavior identical. DOS may suggest a C
hypothesis, but Aztec must still reproduce the Amiga function independently.

## Reproduction and scope

The existing local MSC 5.00, 5.10 and 6.00a candidates and MS-DOS Player were
used without downloading another compiler. The analysis-only Capstone 5.0.3
package was copied from the existing `D:/Prog/pre2_recon/tools/vendor/capstone`
to `C:/tools/capstone-5.0.3/capstone`; its entire 58-file tree is checked by
SHA-256 before import. Paths, provenance references, roles and hashes are in
[DOS toolchain evidence](../evidence/dos/toolchain.json). A local override of
the Capstone path may be supplied through `TALES_CAPSTONE_ROOT`, but its tree
hash must match.

```powershell
python tools/dos_structure.py --summary --write evidence/dos/structure.json --write-root-image build/dos/root-image.bin
python tools/dos_functions.py --write evidence/dos/function-census.json
python tools/dos_pair_receipt.py --write evidence/dos/pair-receipt.json
python tools/dos_specimen_receipts.py --write evidence/dos/specimen-receipts.json
```

The derived root image stays under ignored `build/` and is never a game build
input. The DOS census is for quick lookup when an Amiga routine has a specific
source-shape or semantic ambiguity. Whole DOS overlay closure, Microsoft
runtime reconstruction, EGA, and DOS audio are outside this work. The next
useful cross-version test should start with a concrete blocked Amiga function,
locate its DOS counterpart, and return the hypothesis to the Aztec oracle.
