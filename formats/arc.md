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

formats/decode.py --dump DIR uses the Amiga planar bit order (plane 0 as the
low color-index bit, high bit first within each byte). It applies resident DATA
palettes where a matched scene path establishes them and expands each 4-bit
RGB channel by 17. Unmapped records use a grey ramp; dynamic exp-scene color
indices 27 and 30 alone stay grey in otherwise color previews.

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
the host decoder reads these bounded big-endian WORD arrays from resident DATA
hunk 1 of DT1:DuckTales at runtime (offset/count/type: +0x1e32/8/WORD and
+0x1e42/49/WORD), using the strict HUNK parser; it does not embed their values.
A missing executable is an error. In the supplied disks, kind 5
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

## Palettes: DATA targets and scene use

`python tools/behavior.py --json` reports one `runtime_glue_getcolor` caller,
`ov04_F_1E36`; it reports no callers for `runtime_glue_loadrgb4` or
`runtime_glue_setrgb4`. The readable view `build/readable/ov04/initialize_av.c`
identifies `F_h00_8AEA` as `GetColorMap`. Exact-matched `ov04_F_1E36` requests
32 entries and sets `G_h01_5392` to the returned map's field at +4. The palette
is then handled by exact-matched resident routines: `resident_F_3178` copies 32
words into that field, `resident_F_31AA` moves each 0x0RGB nibble toward a
32-word target for 16 steps, and `resident_F_30F0` copies the 32 words into
both Copper lists starting at color register 0x180. Thus the RGB source is
resident DATA, even though the matched code does not call LoadRGB4 or SetRGB4.

The 32-word targets below are measured big-endian UWORD arrays in resident
DATA hunk 1. `resident_F_31AA` reads target[0..31], and `resident_F_3178`
copies the same count; the measured ranges are 64 bytes and contain no
relocations. The word format is 0x0RGB; the PNG decoder expands each nibble by
17. formats/decode.py reads each named 32-entry UWORD range from the DT1
executable at runtime (resident DATA hunk 1); the descriptors retain the
symbol, offset, count, and type rather than copying DATA values. In `ov04_F_1302`, the game loads `DT1:main.arc` entry 2 and later copies
`G_h01_1426` directly into the ColorMap. This establishes its exact palette:
`G_h01_1426` =
`000 DFF BEF 7BF 47F 00F 00A 006 B70 DB3 FE7 FB5 F73 E00 A10 710 410 830 B41 E52 E85 E96 FB9 FDB 333 555 777 999 CCC EEE FFF FFB`.

| Asset entry / scene | DATA palette | Code evidence |
| --- | --- | --- |
| `DT1:main.arc` entry 0 | `G_h01_14A6` | `ov04_F_1D32`: load entry 0, then fade to this table. |
| `DT1:main.arc` entry 1 | `G_h01_1826` | `ov04_F_1D32`: load entry 1, then fade to this table. |
| `DT1:main.arc` entry 2 (title) | `G_h01_1426` | `ov04_F_1302`: loads entry 2, fades and directly copies this table. |
| `DT1:main.arc` entry 3 | `G_h01_1466` | `ov04_F_0E44` calls `ov04_F_07CA` (which loads entry 3), then fades to this table. |
| `DT1:plane.arc` scene | `G_h01_15A6` | `ov05_F_0000` opens this archive and uses this target during the scene. |
| `DT1:invart.arc`, `DT1:invest.arc` scenes | `G_h01_1466` | `ov07_F_0000` and `ov07_F_1424` open each archive and use this target. |
| `DT1:mbin.arc` scene | `G_h01_18E6` | `ov12_F_0000` loads entry 0, draws it, then fades to this target. |
| `DT2:mac.arc` scene | `G_h01_1566` | `ov06_F_0000` loads entry 5; `ov06_F_063A` draws and fades to this target. |
| `DT2:mt.arc` scene | `G_h01_15E6` | `ov08_F_0000` opens the archive and uses this target for the scene bitmap. |
| `DT2:ps.arc` scene | `G_h01_1626` | `ov09_F_0000` opens the archive, loads entry 0, and fades to this target. |
| `DT2:exp.arc` scene | `G_h01_16A6` | `ov10_F_0000` opens the archive, loads entry 0, and fades to this target. |
| `DT2:jg.arc` scene | `G_h01_16E6` | `ov11_F_0000` calls `ov11_F_15C8(1)` (loads entry 4) and uses this target in the same scene. |

For `main.arc`, the entry-to-palette association is explicit in the load and
transition order. Inference from those paths: for the other listed archives, the matched overlay
sets one scene-wide 32-color map, so `decode.py --dump` applies that established
scene map to image records from that archive. Their individual record roles are
UNKNOWN where the call path does not identify an entry.

`ov10_F_2634` is an exact code source for two dynamic colors: it writes
ColorMap word 27 at `G_h01_5392 + 0x36` and word 30 at `+0x3c`, then calls
`resident_F_30F0` to update the Copper list. A switch on `G_h01_79A2` chooses
`(0x832,0xb20)`, `(0x842,0xb30)`, `(0x943,0xa30)`, or `(0x843,0xa20)`.
The selected pair is runtime state, not recorded in the archive. For
`DT2:exp.arc`, the decoder therefore uses measured `G_h01_16A6` colors for the
other 30 indices and greys only indices 27 and 30.

Other referenced DATA tables
(e.g. `G_h01_1766`, `G_h01_17A6`, `G_h01_17E6`, `G_h01_1866`, and
`G_h01_18A6`) are also 32-word fade targets, but their exact archive-record
associations are UNKNOWN. Kind-1/2 metadata still has no palette field; the
RGB tables live separately in executable DATA. Unlisted archive palettes remain
UNKNOWN and their PNGs stay grayscale.
