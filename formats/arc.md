# Indexed DuckTales resource containers and record codecs

## Container

resident_F_2816 seeks to byte zero, reads the little-endian u16 count via
resident_F_2D66, then that many little-endian u32 record offsets via
resident_F_2DBA into G_h01_A7EE[104]. Counts above 104 are rejected.
resident_F_287C seeks to an indexed offset and reads a 16-byte header using
read_le32 / read_le16:

| Offset | Meaning | Evidence |
| --- | --- | --- |
| +0 | u32 stored/read byte count | resident_F_287C -> G_h01_A7D6; kind-specific uses in resident_F_291E. For kinds 1/2, 404A is not passed this count. |
| +4 | u16 record kind | resident_F_287C -> G_h01_A7DA; switch in resident_F_291E. |
| +6 | kind-specific u16 | resident_F_287C -> G_h01_A7DC; meanings below. |
| +8 | kind-specific u16 | resident_F_287C -> G_h01_A7DE; meanings below. |
| +10 | kind-specific u16 | resident_F_287C -> G_h01_A7E0; kind 2 stride multiplier. |
| +12 | u16, meaning UNKNOWN for kinds 1/2/5/6 | resident_F_287C -> G_h01_A7E2; not consumed in those resident_F_291E branches. |
| +14 | kind-specific u16 | resident_F_287C -> G_h01_A7E4; kind 6 allocation length. Other meanings UNKNOWN here. |

In the supplied files, each distinct offset bounds a record whose physical
span is 16 bytes plus the header +0 count; repeated offsets are table references
to the same body. This measured span does not bound kind-1/2 reads, as described
below.

The on-disk header and index words are little-endian because resident_F_287C
uses read_le16 and read_le32. The C bitmap and ADPCM tables reside in big-endian
Amiga DATA.

The 291E-v1.c candidate in build/workers/sol-arc-loader has a function-level
exact comparison; its worker report does not claim complete-unit promotion.
resident_F_404A and resident_F_4184 are accepted FUNCTION_CODE_MATCH
functions. The byte reader resident_F_411E remains separately
BEHAVIORAL_CHAR_RETURN, not exact C. python tools/readable.py renders their
named views under build/readable/resident/.

## Kinds 1 and 2: five-plane RLE bitmaps

resident_F_291E sends kinds 1 and 2 to resident_F_404A. The latter's exact C
body establishes this token grammar: token & 0x7f is the number of output
bytes; if bit 7 is set, that many following bytes are literals; otherwise the
next byte is repeated that many times. remaining is an unsigned 16-bit C
counter. Output traversal is byte-column, plane, then row, and each byte is
written at column + row * BytesPerRow (resident_F_404A).

The global G_h01_0970 is the 16-bit word 5 in resident DATA at +0x970;
G_h01_0971 is its low byte. resident_F_3A6E allocates and fills five plane
pointers, while resident_F_291E / resident_F_3B16 set bitmap depth from
G_h01_0971. Thus the supplied bitmaps use five planes.

| Header field | Kind 1 | Kind 2 | Evidence |
| --- | --- | --- | --- |
| +6 | pixel width | pixel width | resident_F_291E; kind 1 passes it to resident_F_3B16 only when destination is null. |
| +8 | row count | row count | resident_F_291E; kind 1 passes it to resident_F_3B16 only when destination is null. |
| +10 | UNKNOWN / unused by this branch | row-stride multiplier | kind 2 sets BytesPerRow = (+6 >> 3) * +10 in resident_F_291E. |
| +12, +14 | UNKNOWN | UNKNOWN | Not read by these branches in resident_F_291E. |

For a standalone kind-1 decode, resident_F_3B16 constructs BytesPerRow =
+6 >> 3, Rows = +8, and depth 5. If the caller supplies an existing bitmap,
its actual fields control resident_F_404A; those caller fields are not
serialized in the record and are UNKNOWN to this decoder. For kind 2,
resident_F_291E constructs an embedded bitmap with BytesPerRow =
(+6 >> 3) * +10, Rows = +8, and depth 5, then calls resident_F_3A6E for the
planes.

For supplied records, the decoded plane-buffer size is BytesPerRow * Rows * 5:
kind 1 uses (+6 >> 3) * +8 * 5; kind 2 uses ((+6 >> 3) * +10) * +8 * 5.
The host decoder preserves all five planes in plane-major order. Its image
preview uses +6 by +8 as the visible rectangle; extra row bytes implied by
kind-2 +10 remain in the decoded buffer and are not shown in the preview.

The RLE routine receives no stored-length argument. resident_F_404A sets
G_h01_B1E8 to 0x400; behaviorally reconstructed resident_F_411E refills its
byte buffer with Read(arc_file, ..., 1024) and does not cap reads at header +0.
The host decoder therefore starts at the payload and models the contiguous
archive byte stream. DT2:jg.arc entry 16 has +0 = 1468, but the bitmap loop
consumes 1543 bytes (75 bytes beyond that indexed span) to fill its metadata-
described output. This cross-boundary read follows the matched 404A loop and
the 411E readable view; whether the record's declared count is intended to
bound that stream is UNKNOWN. This behavior is retained in record_output and
reported by --verbose.

formats/decode.py --dump DIR writes kind-1/2 PNG previews using a 32-level
grey ramp. It uses the Amiga planar bit order (plane 0 as the low color-index
bit, high bit first within each byte) to construct the visualization. The game
palette and color-index-to-RGB mapping are UNKNOWN; the grey ramp is only for
inspection, not recovered palette data.

## Kind 4: LZW

resident_F_3C4C / resident_F_3E9C establish CLEAR 0x100, END 0x101, first
dictionary code 0x102, 9-to-12-bit codes, and low-bit-first packing.
resident_F_4032 appends decoded bytes. resident_F_291E passes header +6 as
the output allocation/count; the host decoder verifies that it equals the
expanded output length.

## Kind 5: packed adaptive delta samples

resident_F_291E allocates the output length from header +6 and calls
resident_F_4184 with the stored byte count from +0. For each input byte,
resident_F_4184 decodes the high nibble then low nibble, updates a signed
16-bit sample and step index, and writes one output byte per nibble
(sample >> 4, narrowed to char). Thus output size is exactly twice the stored
input size, and +6 is the decoded byte count. The signed 16-bit table values
are resident DATA G_h01_1E32[8] at +0x1e32 and G_h01_1E42[49] at +0x1e42;
the host decoder uses those measured words. In the supplied disks, kind 5
occurs in dt1.as and dt2.as, not in an .arc file. All supplied kind-5 records
have +6 == 2 * +0.

## Kinds 3 and 6

Kind 3 reads +0 stored bytes and uses its low 16-bit word as the
TextBlock.length (resident_F_291E); the rest of its metadata meaning is
UNKNOWN here. Kind 6 allocates +14 bytes, then reads +0 stored bytes.
Therefore +14 is an allocation length, not necessarily the number of valid
bytes read. If +14 exceeds +0, the trailing allocated bytes are not
initialized by the loader and are UNKNOWN. The host decoder exposes only
the bytes actually read and checks +0 <= +14.

## Remaining semantic unknowns

ov04_F_07CA and ov12_F_0000 blit kind-1 screen bitmaps at 320 by 200;
other overlay callers use loaded records with graphics routines. Those calls
establish draw sizes and destination identity, not palette contents. No matched
LoadRGB4 / SetRGB4 call was found. Kind-1 +10..+14, kind-2 +12/+14,
kind-3 auxiliary fields, the palette, and kind-5 +12 remain UNKNOWN unless
stated above.
