# `.arc` indexed resources

## Container and header

`resident_F_2816` seeks to byte zero, reads a little-endian `u16` count with
`resident_F_2D66`, then that many little-endian `u32` offsets with
`resident_F_2DBA` into `G_h01_A7EE[104]`. It rejects counts over 104. The
reader `resident_F_287C` indexes that table, seeks to the record offset, reads
the `u32` at `+0` into `G_h01_A7D6`, then six `u16` words at `+4..+15` into
`G_h01_A7DA..G_h01_A7E4`. This establishes the 16-byte header:

| Offset | Field | Evidence |
| --- | --- | --- |
| `+0` | `u32` stored-data byte count | `resident_F_287C` / `G_h01_A7D6`; supplied spans equal `16 + count`. |
| `+4` | `u16` kind | `resident_F_287C` / `G_h01_A7DA`; dispatch in `resident_F_291E`. |
| `+6..+15` | five `u16` metadata words | `resident_F_287C` / `G_h01_A7DC..G_h01_A7E4`; meanings depend on kind. |

`ov04_F_07CA` loads `main.arc` record 3 into the preconfigured `G_h01_46CE`
bitmap and calls `F_h00_8A46` for a 320×200 blit. `ov05_F_0000`,
`ov06_F_0000`, `ov08_F_0000`, `ov09_F_0000`, `ov10_F_0000`, and
`ov12_F_0000` also request indexed records before graphics drawing; their
`runtime_glue_bltbitma` caller status is listed by `python tools/behavior.py
--json`.

## Kind 1 and kind 2: bitmap RLE

Both kinds reach `resident_F_404A` from the kind switch in the
`resident_F_291E` disassembly (kind 1 at function offset `+0x7c`, kind 2 at
`+0x172`). The byte reader `resident_F_411E` refills a `0x400`-byte buffer
through AmigaDOS `Read`. `resident_F_404A` consumes controls whose low seven
bits are the output count: with bit 7 set it copies that many following
literal bytes; with bit 7 clear it repeats the following byte that many
times. It writes a `BitMap` plane buffer using the fields at `+0` (`BytesPerRow`),
`+2` (`Rows`), `+5` (`Depth`), and the plane pointers from `+8`; the inner
stride is the low byte of `BytesPerRow`. The loop visits byte-column offsets,
then planes, then rows, writing each byte at `column + row * BytesPerRow`.
This token grammar and destination layout come from `resident_F_404A` disassembly, not an accepted C body.

For kind 1, `resident_F_291E` passes the caller-supplied destination to
`resident_F_404A`. Its `+6` and `+8` words are used only in the null-destination
allocation path. Calling them image width and height is a **hypothesis**:
`main.arc` record 3 has `(320, 200, 1, 65535, 0)`, matching the 320×200
bitmap/blit in `ov04_F_07CA`; kind 1’s `+10..+15` meanings are **UNKNOWN**.

For kind 2, `resident_F_291E` allocates an outer descriptor, writes `+6 >> 3`
to its width-bytes field and `+8` to its row fields, then sets the embedded
bitmap’s `BytesPerRow` to `(+6 >> 3) * +10`, `Rows` to `+8`, and `Depth` to
the global `G_h01_0971`. It allocates the plane pointers through
`resident_F_3A6E` and calls `resident_F_404A` on that embedded bitmap. Thus
`+6` is a pixel-width value, `+8` is row count, and `+10` is a row-stride
multiplier; the code does **not** establish `+10` as color depth. The global
plane count is `G_h01_0970`, initialized to 5 at resident DATA offset `0x970`
and used as bitmap depth by `ov04_F_1E36` and by `resident_F_3A6E`.
Kind 2 words `+12` and `+14` are not consumed by this path and remain
**UNKNOWN**.

Neither the kind 1/2 loader path nor the matched graphics callers bind the
remaining metadata to a palette. No matched `LoadRGB4`/`SetRGB4` caller was
found, so palette values and the color-index mapping are **UNKNOWN**. The host
decoder currently extracts kind 1/2 compressed payloads byte-for-byte; it does
not claim pixel-plane output. No PNG dump is provided without the palette and
complete per-kind display mapping.

## Kind 4: LZW

`resident_F_3C4C` and `resident_F_3E9C` establish a clear/end-code LZW stream:
CLEAR `0x100`, END `0x101`, first dictionary code `0x102`, 9-bit initial
codes growing to 12 bits, and low-bit-first packing. `resident_F_4032`
appends output. For supplied kind-4 records, metadata `+6` equals the decoded
byte count; `formats/decode.py` checks it. Kinds other than 1, 2, and 4 were
not observed in `.arc` files.

## Limits

The record table and kind-4 codec are host-decoded. Kind-1/2 records are
identified as RLE bitmaps from loader disassembly, but the host tool retains
their stored streams because kind 1 relies on caller bitmap setup and a supplied
kind-2 stream (`DT2:jg.arc`, index 16) does not reach the expected five-plane
output length under the recovered stride model. Palette and kind-1 metadata
semantics remain **UNKNOWN**.

## Graphics call evidence and palette limits

`ov04_F_07CA` sends the kind-1 destination bitmap `G_h01_46CE` to
`F_h00_8A46` with source/destination origins `(0,0)`, size `320×200`, minterm
`192`, mask `255`, and flags `0`; the call is the `runtime_glue_bltbitma` service.
`ov12_F_0000` likewise loads `mbin.arc` record 0 into `G_h01_46CE` and blits
`320×200`. `ov08_F_0000` loads `mt.arc` records and later blits its record-0
bitmap through the same service. These calls establish draw rectangles and
buffer identity, not color palette values.

`runtime_glue_setrast` callers include resource-consuming overlays such as
`ov05_F_0000`, `ov06_F_0000`, `ov09_F_0000`, `ov10_F_0000`, and
`ov12_F_0000`; they operate on raster-port state and do not consume the header
palette words. `runtime_glue_writepix` callers are `ov10_F_1FDE` and
`ov15_F_08B0`; those pass a raster port, current pen, and pixel coordinates.
No `LoadRGB4`/`SetRGB4` caller appears in matched C or the behavior service
ledger. Palette contents, palette index mapping, and any implicit palette
resource are **UNKNOWN**.
